#!/usr/bin/env python3
"""Layer A compute runner: persistent job queue with budget ledger, lock, heartbeat.

Usage:
    python run_all.py --mode quick            # smoke test (<10 min), separate queue
    python run_all.py --mode full --resume    # run/continue the current plan's jobs
    python run_all.py --mode full --resume --workers 4

Behaviour (idempotent, safe to run twice):
  * A lock file (state/run_all.lock) prevents two copies from running.
  * Jobs come from the current plan (experiments/CURRENT_PLAN -> plan_vN.yaml) via
    src/jobs.py:build_jobs(plan, mode). New jobs are appended; existing jobs keep their state.
  * Each job is a subprocess command. Jobs are responsible for writing their own
    results (results/<job_id>.json + row in results/raw_results.csv) and checkpoints.
    A job whose result file already exists is marked done without re-running.
  * 'running' jobs found at startup (crash/reboot) are reset to 'pending' and resume
    from their own checkpoints. Failed jobs are retried up to MAX_ATTEMPTS total.
  * Compute ledger (state/budget.json) counts machine-occupied wall seconds (any job running),
    persisted every 60 s, summed across restarts; downtime is excluded automatically.
    When the cycle budget is reached, running jobs finish, remaining are 'skipped_budget'.
  * state/heartbeat is touched every <=30 s while the runner is alive.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state"
LOGS = ROOT / "logs"
RESULTS = ROOT / "results"
MAX_ATTEMPTS = 3  # first try + 2 retries


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_write_json(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def log(msg):
    LOGS.mkdir(exist_ok=True)
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    with open(LOGS / "run_all.log", "a") as f:
        f.write(line + "\n")


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except (OSError, TypeError):
        return False


def acquire_lock(lock):
    if lock.exists():
        try:
            pid = int(lock.read_text().strip() or 0)
        except ValueError:
            pid = 0
        if pid and pid_alive(pid) and pid != os.getpid():
            log(f"another run_all is active (pid {pid}); exiting (no-op)")
            sys.exit(0)
        log(f"stale lock from pid {pid}; taking over")
    lock.write_text(str(os.getpid()))


def touch_heartbeat():
    (STATE / "heartbeat").write_text(now() + "\n")


def current_cycle():
    return int(read_json(STATE / "agent_state.json", {}).get("cycle", 1))


def load_plan():
    import yaml  # noqa
    cur = (ROOT / "experiments" / "CURRENT_PLAN").read_text().strip()
    with open(ROOT / "experiments" / cur) as f:
        return cur, yaml.safe_load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["quick", "full"], default="full")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--only", default=None, help="comma-separated experiment ids (e.g. E1,E2)")
    args = ap.parse_args()

    STATE.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    lock = STATE / ("run_all_quick.lock" if args.mode == "quick" else "run_all.lock")
    acquire_lock(lock)
    try:
        run(args)
    finally:
        if lock.exists() and lock.read_text().strip() == str(os.getpid()):
            lock.unlink()


def run(args):
    sys.path.insert(0, str(ROOT))
    from src.jobs import build_jobs  # project-specific job builder

    plan_name, plan = load_plan()
    qpath = STATE / ("queue_quick.json" if args.mode == "quick" else "queue.json")
    queue = read_json(qpath, {"jobs": []})
    known = {j["id"]: j for j in queue["jobs"]}
    only = set(args.only.split(",")) if args.only else None
    added = 0
    for j in build_jobs(plan, args.mode):
        if only and j["experiment"] not in only:
            continue
        if j["id"] not in known:
            j.update(status="pending", attempts=0, plan=plan_name, added=now())
            queue["jobs"].append(j)
            known[j["id"]] = j
            added += 1
    # crash recovery
    for j in queue["jobs"]:
        if j["status"] == "running":
            j["status"] = "pending"
            log(f"recovered interrupted job {j['id']} -> pending (resumes from checkpoint)")
    atomic_write_json(qpath, queue)
    log(f"mode={args.mode} plan={plan_name} jobs_total={len(queue['jobs'])} added={added}")

    budget_path = STATE / "budget.json"
    budget = read_json(budget_path, {"per_cycle": {}, "global_seconds": 0})
    cyc = str(current_cycle())
    cycle_ceiling = float(budget.get("cycle_ceiling_h", 15)) * 3600
    global_ceiling = float(budget.get("global_ceiling_h", 120)) * 3600
    workers = args.workers or int(plan.get("workers", max(1, (os.cpu_count() or 2))))

    running = {}  # job_id -> (Popen, logfile handle)
    last_tick = time.time()
    last_persist = time.time()

    def persist_budget(force=False):
        nonlocal last_persist
        if force or time.time() - last_persist >= 60:
            atomic_write_json(budget_path, budget)
            last_persist = time.time()

    def over_budget():
        if args.mode == "quick":
            return False
        return (budget["per_cycle"].get(cyc, 0) >= cycle_ceiling
                or budget.get("global_seconds", 0) >= global_ceiling)

    while True:
        touch_heartbeat()
        t = time.time()
        if running and args.mode == "full":
            dt = t - last_tick
            budget["per_cycle"][cyc] = budget["per_cycle"].get(cyc, 0) + dt
            budget["global_seconds"] = budget.get("global_seconds", 0) + dt
        last_tick = t
        persist_budget()

        # reap finished jobs
        for jid in list(running):
            p, fh = running[jid]
            rc = p.poll()
            if rc is None:
                continue
            fh.close()
            job = known[jid]
            res_file = ROOT / job["result"] if job.get("result") else RESULTS / f"{jid}.json"
            if args.mode == "quick":
                res_file = RESULTS / "quick" / f"{jid}.json"
            if rc == 0 and res_file.exists():
                job["status"] = "done"
                job["finished"] = now()
                log(f"done {jid}")
            else:
                job["last_rc"] = rc
                if job["attempts"] >= MAX_ATTEMPTS:
                    job["status"] = "failed"
                    log(f"FAILED permanently {jid} rc={rc} (see logs/jobs/{jid}.log)")
                else:
                    job["status"] = "pending"
                    log(f"failed {jid} rc={rc}; will retry (attempt {job['attempts']}/{MAX_ATTEMPTS})")
            del running[jid]
            atomic_write_json(qpath, queue)

        pending = [j for j in queue["jobs"] if j["status"] == "pending"]
        if over_budget() and pending:
            for j in pending:
                j["status"] = "skipped_budget"
            atomic_write_json(qpath, queue)
            log(f"cycle/global budget reached; skipped {len(pending)} pending jobs")
            pending = []

        # launch new jobs
        while pending and len(running) < workers:
            job = pending.pop(0)
            res_file = RESULTS / ("quick" if args.mode == "quick" else "") / f"{job['id']}.json"
            if res_file.exists():
                job["status"] = "done"
                job["finished"] = job.get("finished", now())
                atomic_write_json(qpath, queue)
                continue
            job["status"] = "running"
            job["attempts"] += 1
            job["started"] = now()
            (LOGS / "jobs").mkdir(parents=True, exist_ok=True)
            fh = open(LOGS / "jobs" / f"{job['id']}.log", "a")
            fh.write(f"\n=== attempt {job['attempts']} at {now()} ===\n")
            fh.flush()
            env = dict(os.environ, OMP_NUM_THREADS=str(job.get("threads", 1)),
                       MKL_NUM_THREADS=str(job.get("threads", 1)),
                       OPENBLAS_NUM_THREADS=str(job.get("threads", 1)),
                       RUN_MODE=args.mode, PYTHONHASHSEED="0")
            p = subprocess.Popen(job["cmd"], cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                                 env=env, shell=isinstance(job["cmd"], str))
            running[job["id"]] = (p, fh)
            log(f"started {job['id']} (pid {p.pid}, attempt {job['attempts']})")
            atomic_write_json(qpath, queue)

        if not running and not pending:
            persist_budget(force=True)
            counts = {}
            for j in queue["jobs"]:
                counts[j["status"]] = counts.get(j["status"], 0) + 1
            log(f"queue drained: {counts}")
            break
        time.sleep(5)

    if args.mode == "full":
        # automatic report (Section 12), never fatal
        try:
            subprocess.run([sys.executable, "scripts/final_report.py"], cwd=ROOT, timeout=3600)
        except Exception as e:  # noqa
            log(f"final_report failed: {e}")


if __name__ == "__main__":
    main()
