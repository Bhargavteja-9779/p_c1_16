"""Build the job list for run_all.py from the current plan. Job ids are deterministic (idempotent queue)."""
CELLS = ["A_MICU", "A_SICU", "B_MICU", "B_SICU"]


def _job(exp, cell, model, seed, split, fixes, quick=False):
    jid = f"{exp}__{model}__{fixes}__{cell}__s{seed}__{split}"
    cmd = ["python3", "-m", "src.train_eval", "--job-id", jid, "--train-cell", cell, "--model", model, "--seed", str(seed),
           "--eval-split", split, "--fixes", fixes, "--experiment", exp] + (["--quick"] if quick else [])
    return dict(id=jid, experiment=exp, cmd=cmd, threads=2)


def build_jobs(plan, mode):
    if mode == "quick":
        return [_job("QUICK", "A_MICU", "lgbm", 0, "val", "none", True), _job("QUICK", "B_SICU", "lr", 0, "val", "none", True)]
    E = plan["experiments"]; out = []
    se, sc = plan["seeds_explore"], plan["seeds_confirm"]
    for exp in ("E1_explore", "E2_fixes", "E6_confirm"):
        e = E[exp]
        seeds = se if e["seeds"] == "explore" else sc
        for fixes in e["fixes"]:
            for model in e["models"]:
                if fixes != "none" and model == "lr" and exp == "E6_confirm":
                    continue  # fixes are confirmed with the primary model class only (as in E2)
                for s in seeds:
                    for c in CELLS:
                        out.append(_job(exp, c, model, s, e["eval_split"], fixes))
    out += build_jobs_v3(plan)
    out += build_jobs_v6(plan)
    return out


def _job_v3(exp, factor, cell, model, seed, split, featset="all", size="full"):
    tag = cell.replace("+", "-")
    jid = f"{exp}__{factor}__{model}__{featset}__{size}__{tag}__s{seed}__{split}"
    cmd = ["python3", "-m", "src.train_eval_v3", "--job-id", jid, "--factor", factor, "--train-cell", cell, "--model", model,
           "--seed", str(seed), "--eval-split", split, "--featset", featset, "--size", size, "--experiment", exp]
    return dict(id=jid, experiment=exp, cmd=cmd, threads=2, result=f"results/v3/{jid}.json")


def build_jobs_v3(plan):
    """plan_v3 experiments (factor / featset / size / pooled). Empty for plans without 'v3'."""
    V = plan.get("v3")
    if not V:
        return []
    from src.train_eval_v3 import cells_of
    other_h = {"A": "B", "B": "A"}
    out = []
    for phase, split, seeds in (("explore", "val", plan["seeds_explore"]), ("confirm", "test", plan["seeds_confirm"])):
        if phase not in V["phases"]:
            continue
        sfx = "x" if phase == "explore" else "c"
        for e in V["experiments"]:
            if phase not in e.get("phases", V["phases"]):  # per-experiment phase override (plan_v5)
                continue
            exp = f"{e['id']}{sfx}"
            for model in e["models"]:
                for s in seeds:
                    if e.get("pooled"):
                        f = e["factors"][0]
                        lv = {c.split("_")[1] for c in cells_of(f)}
                        for t in cells_of(f):
                            h, l = t.split("_"); lo = (lv - {l}).pop()
                            out.append(_job_v3(exp, f, f"{h}_{lo}+{other_h[h]}_{l}", model, s, split))
                        continue
                    for f in e["factors"]:
                        for fs in e.get("featsets", ["all"]):
                            for c in cells_of(f):
                                out.append(_job_v3(exp, f, c, model, s, split, fs, e.get("size", "full")))
    return out


def _job_v6(exp, cell, model, featset, seed, split):
    jid = f"{exp}__{model}__{featset}__{cell}__s{seed}__{split}"
    cmd = ["python3", "-m", "src.train_eval_v6", "--job-id", jid, "--train-cell", cell, "--model", model,
           "--featset", featset, "--seed", str(seed), "--eval-split", split, "--experiment", exp]
    return dict(id=jid, experiment=exp, cmd=cmd, threads=2, result=f"results/v6/{jid}.json")


def build_jobs_v6(plan):
    """plan_v6: task T2 on 3 databases x 2 units (E13 main, E14 mechanism featsets). Empty without 'v6'."""
    V = plan.get("v6")
    if not V:
        return []
    from src.train_eval_v6 import CELLS6
    out = []
    for phase, split, seeds in (("explore", "val", plan["seeds_explore"]), ("confirm", "test", plan["seeds_confirm"])):
        if phase not in V["phases"]:
            continue
        sfx = "x" if phase == "explore" else "c"
        for eid, e in V["experiments"].items():
            for model in e["models"]:
                for fs in e["featsets"]:
                    for s in seeds:
                        for c in CELLS6:
                            out.append(_job_v6(f"{eid}{sfx}", c, model, fs, s, split))
    return out
