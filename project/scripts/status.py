#!/usr/bin/env python3
"""Print a compact status of the research loop (state, queue, budget, heartbeat, gates)."""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "state"

def rj(p, d):
    try:
        return json.load(open(p))
    except Exception:
        return d

st = rj(S / "agent_state.json", {})
print("== agent_state:", json.dumps(st))
for qn in ("queue.json", "queue_quick.json"):
    q = rj(S / qn, {"jobs": []})
    c = {}
    for j in q["jobs"]:
        c[j["status"]] = c.get(j["status"], 0) + 1
    if q["jobs"]:
        print(f"== {qn}: {len(q['jobs'])} jobs {c}")
        fails = [j["id"] for j in q["jobs"] if j["status"] == "failed"]
        if fails:
            print("   failed:", ", ".join(fails[:20]))
        runs = [j["id"] for j in q["jobs"] if j["status"] == "running"]
        if runs:
            print("   running:", ", ".join(runs[:20]))
b = rj(S / "budget.json", {})
g = b.get("global_seconds", 0) / 3600
print(f"== compute: global {g:.2f} h / {b.get('global_ceiling_h')} h; per cycle (h): " +
      ", ".join(f"c{k}={v/3600:.2f}" for k, v in b.get("per_cycle", {}).items()) +
      f" (cycle ceiling {b.get('cycle_ceiling_h')} h)")
hb = S / "heartbeat"
if hb.exists():
    age = datetime.now(timezone.utc).timestamp() - hb.stat().st_mtime
    print(f"== heartbeat: {hb.read_text().strip()} (age {age/60:.1f} min)")
for lk in ("run_all.lock", "run_all_quick.lock"):
    p = S / lk
    if p.exists():
        pid = p.read_text().strip()
        alive = False
        try:
            os.kill(int(pid), 0); alive = True
        except Exception:
            pass
        print(f"== lock {lk}: pid {pid} alive={alive}")
gates = rj(S / "gates.json", {})
if gates:
    print("== gates:", ", ".join(f"{k}={v.get('status') if isinstance(v, dict) else v}" for k, v in gates.items()))
rr = ROOT / "results" / "raw_results.csv"
if rr.exists():
    n = sum(1 for _ in open(rr)) - 1
    print(f"== results/raw_results.csv rows: {n}")
