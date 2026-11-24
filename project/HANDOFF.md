# HANDOFF — read this first

_Last updated: 2026-11-24 (cycle 1, Phase 2/3)_

## Where we are
- **Cycle:** 1 **Phase:** PHASE2_LITERATURE → PHASE3_TOPIC
- **NEXT ACTION:** (1) finish `literature/journal_papers_matrix.csv` + `reported_results.md` (if missing, rerun the extraction: see `literature/README` notes in decisions D7); (2) build `data/processed/physionet2019.parquet` via `python -c "from src.data_physionet2019 import load; load()"`; (3) choose the topic (≥10 candidates in `topic/candidates.md`) and write `topic/selected_topic.md`; (4) write `experiments/plan_v1.yaml`.
- **Selected journal:** Critical Care (BMC/Springer Nature, ISSN 1364-8535) — verified median Accepted−Received 66 d (full articles, n=318), JIF 11.4 (2025). JCR quartile UNVERIFIED.
- **Topic:** not yet selected. First idea (missingness patterns = hospital shortcut on PhysioNet 2019) is a DEAD END: already published Oct 2026 (see journal entry 004).
- **Hypothesis:** —

## Running right now
- Background data download (`scripts/download_physionet2019.sh`), idempotent; re-run if files missing (expect 20336 A + 20000 B files).
- No compute jobs yet.

## Compute
- Machine: cloud container, 4 CPU cores, 15 GB RAM, **no GPU**. Budget hours = machine-occupied hours (D1, D6).
- Used: 0.00 h of 15 h (cycle 1); 0.00 h of 120 h (global).

## Gate status
| Gate | Status | Evidence |
|---|---|---|
| G1 Journal | PASS on ≤72 d + publisher; **JCR Q1 UNVERIFIED** | journal_selection/selected_journal.md |
| G2 Prior art | in progress (queries logged) | state/novelty_ledger.json |
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
D1 CPU-only; D2 persistence via git branch; D3 Crossref-assertion turnaround; D4 Critical Care selected; D5 no browser scraping of ScienceDirect; D6 budget = machine-occupied hours.

## Last failures
- PhysioNet 2019 zip URL 404 → switched to parallel per-file download.
- Elsevier metrics pages 403 → Elsevier journals unverifiable.
- Topic idea 1 already published (dead end, not a code failure).

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
- **This container has no crontab and no systemd user bus** → boot autostart and the watchdog cron cannot be installed here. The container is ephemeral anyway. Persistence = git commits pushed to branch `claude/serene-newton-bylqpn`.
- **Layer B auto-restart is not active.** The `claude` CLI exists here, but running a nested agent inside this live session would create two agents editing the same repo. On your own machine, run `scripts/supervisor.sh` (it detects the CLI). Otherwise: open a new session on this repo/branch and paste `BOOTSTRAP_PROMPT.txt`.
- Raw data (`data/`) is git-ignored; re-download with `scripts/download_physionet2019.sh` (2019 sepsis, CC BY 4.0); 2012 challenge and eICU demo download commands are in decisions/journal (PhysioNet open files).

## Moving to a new account
1. Make sure the latest work is pushed (`git push`).
2. In the new session, check out branch `claude/serene-newton-bylqpn` of `p_c1_16`.
3. Paste the contents of `project/BOOTSTRAP_PROMPT.txt`.

## Where things are
- Journal choice: `journal_selection/` (raw per-article evidence in `raw/`, page text in `evidence/`)
- Literature: `literature/` ; prior-art ledger: `state/novelty_ledger.json`
- Research diary: `journal/ENTRIES/`
- Decisions: `state/decisions.md` ; variants: `state/variants_tried.csv`
- Code: `src/`, `run_all.py`, `scripts/` ; results: `results/`, `tables/`, `figures/` ; paper: `paper/`
