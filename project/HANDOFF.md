# HANDOFF — read this first

_Last updated: 2026-11-24 23:20 UTC (cycle 1, E6 confirmation running — resumed in session 3)_

## Where we are
- **Cycle:** 1 **Phase:** E6 confirmation running (Phases 1–4 done; E1/E2 exploration done)
- **NEXT ACTION:**
  0. Fresh container? `pip install lightgbm==4.7.0 pandas==3.0.5 scikit-learn==1.9.1 statsmodels pyarrow scipy`, `bash scripts/download_physionet2019.sh` (repeat until `bad=0`), then `python3 scripts/prepare_data.py` (~4 min; must print md5 0883ae5b4726bdc6fbe0c41bbc4f7d6d — the split is pinned in configs/, D19).
  1. `python3 scripts/status.py`. If E6 is not finished: `nohup setsid python3 run_all.py --mode full --resume --workers 2 --only E6_confirm > logs/run_all_E6.out 2>&1 < /dev/null &` (idempotent).
  2. When 100/100 E6 jobs are done, run the FROZEN analysis (commit 641c403):
     `python3 scripts/analyze_transport.py --experiment E6_confirm --split test --fix-exp E6_confirm --nboot 2000`
     and `python3 scripts/e5_estimators.py --experiment E6_confirm --split test`.
  3. Write a RESULT journal entry, update gates G5–G8, the novelty score and variants_tried.
  4. Then: G4 (compare reproduced numbers with published A/B results), the G7 breadth decision (eICU demo, plan_v3), scripts/final_report.py, scripts/audit_numbers.py, and prior art to ≥30 opened papers.
- **Selected journal:** Critical Care (BMC/Springer Nature, ISSN 1364-8535). Verified median Accepted−Received 66 d; JIF 11.4; JCR quartile UNVERIFIED.
- **Topic (v2):** factorial ICU-unit × hospital transport analysis of sepsis early warning on PhysioNet 2019 (topic/selected_topic.md).
- **Hypotheses (plan_v2):**
  - H1: site gap > unit gap.
  - H2: estimate the share of the site component removed by unlabelled fixes.
  - H3: label-free AUROC estimates err > 0.03 in ≥ 50% of transfers.
- **Validation results (exploration):**
  - H1: D = 0.043 [0.021, 0.066] for LightGBM; 0.066 for LR.
  - H2: about 0.61 of the site component is removable.
  - H3: label-free estimates miss in 64–92% of transfers.
  - See journal 010.

## Running right now
- `run_all.py --only E6_confirm` (detached, setsid; 2 workers × 2 threads). Logs: logs/run_all.log, logs/jobs/E6_confirm__*.log.

## Compute
- Machine: cloud container, 4 CPU cores, 15 GB RAM, **no GPU**. Budget hours = machine-occupied hours (D1, D6).
- Used: ~0.75 h of 15 h (cycle 1); ~0.75 h of 120 h (global); E6 adds ~0.5 h — see state/budget.json.

## Gate status
| Gate | Status | Evidence |
|---|---|---|
| G1 Journal | PASS on ≤72 d + publisher; **JCR Q1 UNVERIFIED** | journal_selection/selected_journal.md |
| G2 Prior art | in progress: 40 queries, 5 papers opened (abstracts) + 17 journal papers (Phase 2); need ≥30 opened for the claim | state/novelty_ledger.json |
| G3 Novelty | unknown | — |
| G4 Baselines | unknown | — |
| G5 Main result | unknown | — |
| G6 Ablation | unknown | — |
| G7 Generalization | unknown | — |
| G8 Leakage | unknown | — |
| G9 Reproducibility | unknown | — |
| G10 Review | unknown | — |
| G11 Integrity audit | unknown | — |

## Last decisions (full log: state/decisions.md)
D1 CPU-only; D2 persistence via git branch; D3 Crossref-assertion turnaround; D4 Critical Care selected; D5 no browser scraping of ScienceDirect; D6 budget = machine-occupied hours; D7 literature via sub-agent, spot-checked; D8 Frontiers fallback; D9 diagnose first; D10–D11 account switch; D12–D16 diagnosis → topic v2 (factorial unit × hospital); D17 plan_v2, analysis frozen 641c403; D18 resumed (session 3); **D19 split pinned in git after B-split drift on re-download (journal 011)**.

## Last failures
- Session 3: E6 relaunch crashed (processed caches missing) → `scripts/prepare_data.py`. Rule-based split drifted for hospital B after re-download → reconstructed old split from committed predictions, pinned in configs/ (D19).
- PhysioNet 2019 zip URL 404 → switched to parallel per-file download.
- Elsevier metrics pages 403 → Elsevier journals unverifiable.
- Topic idea 1 already published (dead end, not a code failure).
- First per-file 2019 download produced ~27k empty files (PhysioNet redirected to S3) → script now uses the official S3 open-data mirror and validates headers.
- Frontiers in Public Health scan interrupted (not needed).

## Commands (run from `project/`)
- Status: `python3 scripts/status.py`
- Logs: `tail -f logs/run_all.log` ; per job `logs/jobs/<job_id>.log`
- Launch / resume compute (detached, idempotent): `bash scripts/launch.sh`
- Stop compute: `bash scripts/stop.sh`
- Quick smoke test: `python3 run_all.py --mode quick`
- Autostart install (only on a machine with cron): `bash scripts/install_autostart.sh [--with-supervisor]`
- Remove autostart (both layers): `bash scripts/uninstall_autostart.sh`
- Agent supervisor (Layer B): `nohup setsid bash scripts/supervisor.sh >/dev/null 2>&1 &` ; stop: `touch state/STOP_SUPERVISOR`

## Known problems
- **This container has no crontab and no systemd user bus** → boot autostart and the watchdog cron cannot be installed here. The container is ephemeral anyway. Persistence = git commits pushed to branch `claude/lucid-bell-7mlvge` (D18; earlier: dazzling-albattani-8k4faw).
- **Layer B auto-restart is not active.** The `claude` CLI exists here, but running a nested agent inside this live session would create two agents editing the same repo. On your own machine, run `scripts/supervisor.sh` (it detects the CLI). Otherwise: open a new session on this repo/branch and paste `BOOTSTRAP_PROMPT.txt`.
- Raw data (`data/`) is git-ignored; after re-download ALWAYS run `python3 scripts/prepare_data.py`. Re-download with `scripts/download_physionet2019.sh` (2019 sepsis, CC BY 4.0); 2012 challenge and eICU demo download commands are in decisions/journal (PhysioNet open files).

## Moving to a new account
1. Make sure the latest work is pushed (`git push`).
2. In the new session, check out the most recent `claude/*` branch of `p_c1_16` (currently `claude/lucid-bell-7mlvge`) and fast-forward the session branch onto it.
3. Paste the contents of `project/BOOTSTRAP_PROMPT.txt`.

## Where things are
- Journal choice: `journal_selection/` (raw per-article evidence in `raw/`, page text in `evidence/`)
- Literature: `literature/` ; prior-art ledger: `state/novelty_ledger.json`
- Research diary: `journal/ENTRIES/`
- Decisions: `state/decisions.md` ; variants: `state/variants_tried.csv`
- Code: `src/`, `run_all.py`, `scripts/` ; results: `results/`, `tables/`, `figures/` ; paper: `paper/`

## Data (all open, git-ignored under data/raw)
- PhysioNet/CinC 2019 sepsis (CC BY 4.0): `bash scripts/download_physionet2019.sh`
- PhysioNet 2012 challenge: `cd data/raw/physionet2012 && for f in set-a.tar.gz set-b.tar.gz set-c.tar.gz Outcomes-a.txt Outcomes-b.txt Outcomes-c.txt; do curl -sL -O https://physionet.org/files/challenge-2012/1.0.0/$f; done && for s in a b c; do tar xzf set-$s.tar.gz; done` (license: check page, recorded as UNVERIFIED)
- eICU-CRD demo 2.0.1 (ODbL): `cd data/raw/eicu_demo && for f in patient lab vitalPeriodic vitalAperiodic apachePatientResult hospital; do curl -s -O https://physionet.org/files/eicu-crd-demo/2.0.1/$f.csv.gz; done`

## Key evidence so far
- Literature: `literature/journal_papers_matrix.csv` (15 papers), `literature/reported_results.md` (internal→external drops, missingness handling, calibration, seeds).
- Closest prior work for cross-hospital PhysioNet 2019: doi:10.20944/preprints202610.1449.v1 (XGBoost 0.725→0.608 A→B), arXiv 2609.33279 (PRISM), arXiv 2609.30781, Applied Sciences doi:10.3390/app16062735.
