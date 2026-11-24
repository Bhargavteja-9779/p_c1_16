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
    return out
