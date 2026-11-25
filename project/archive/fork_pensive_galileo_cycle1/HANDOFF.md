# HANDOFF — read this first

_Last updated: 2026-11-24 (cycle 1, Phase 3 — per-variable diagnostic running)_

## Where we are
- **Cycle:** 1 **Phase:** PHASE3_TOPIC (Phase 1 journal ✔, Phase 2 literature ✔, D9 diagnosis ✔)
- **Branch for persistence:** `claude/pensive-galileo-vgrn1b` (D11).
- **NEXT ACTION (in order):**
  1. If `results/diagnosis/pervar_{A,B}_s0.csv` are missing, run `python3 -m src.diagnose_pervar --seed 0` (≈20 min; validation only). Data must exist first (see Data).
  2. Analyse per-variable results: does the label-free policy-shift score (rate_logratio, policy_auc_src−policy_auc_tgt) predict which variables' process features help vs hurt on the target (d_tgt)? Write a DIAGNOSIS journal entry (008). If yes → write `topic/selected_topic.md` for candidate 3 with a label-free selection method; if no → candidate 4 (local updating) as backup.
  3. Then `experiments/plan_v1.yaml`, `src/jobs.py`, `scripts/final_report.py`, `scripts/audit_numbers.py`; quick run; launch.
  4. Second dataset for G7: PhysioNet 2012 (ICU type as site) and/or eICU demo (hospital as site).
- **Selected journal:** Critical Care (BMC/Springer Nature, ISSN 1364-8535) — verified median Accepted−Received 66 d (n=318), JIF 11.4 (2025). JCR quartile UNVERIFIED.
- **Topic (tentative, D14):** which measurement-process signals transport across hospitals, and can a label-free per-variable policy-shift criterion choose them (topic/candidates.md #3).
- **Hypothesis (draft):** the transfer effect of a variable's process features is predicted by how much its measurement policy shifts between sites, measurable without target labels.
- **Key findings so far:** journal 006 (diagnosis), 007 (septic records truncated at onset+3 h → ICULOS excluded, D13; process-feature effect flips sign with transfer direction in 3/3 seeds *when ICULOS is included*; without ICULOS process features help both directions at seed 0 — the asymmetry is entangled with ICULOS, to be resolved).

## Running right now
- `python3 -m src.diagnose_pervar --seed 0` (nohup; log `logs/pervar_s0.log`). If the session died, just re-run (idempotent, skips finished CSVs).

## Compute
- Machine: cloud container, 4 CPU cores, 15 GB RAM, **no GPU**. Budget hours = machine-occupied hours (D1, D6).
- Used: ≈0.3 h of 15 h (cycle 1); ≈0.3 h of 120 h (global) (state/budget.json; diagnostics only).

## Gate status
| Gate | Status | Evidence |
|---|---|---|
| G1 Journal | PASS on ≤72 d + publisher; **JCR Q1 UNVERIFIED** | journal_selection/selected_journal.md |
| G2 Prior art | in progress: 38 queries logged (LANDSCAPE, C1–C3); ~10 abstracts read; claim table not yet written | state/novelty_ledger.json |
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
D1 CPU-only; D2 persistence via git branch; D3 Crossref-assertion turnaround; D4 Critical Care selected; D5 no browser scraping of ScienceDirect; D6 budget = machine-occupied hours; D7 literature via sub-agent, spot-checked; D8 Frontiers allowed by user — Frontiers in Medicine 69.5 d (n=40) is fallback #2; D9 diagnose before choosing a method; D10 paused for account switch; D11 new persistence branch; D12 fixed diagnostic hyperparameters; D13 ICULOS excluded (truncation); D14 tentative topic = candidate 3.

## Last failures
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
- **This container has no crontab and no systemd user bus** → boot autostart and the watchdog cron cannot be installed here. The container is ephemeral anyway. Persistence = git commits pushed to branch `claude/pensive-galileo-vgrn1b`.
- **Layer B auto-restart is not active.** The `claude` CLI exists here, but running a nested agent inside this live session would create two agents editing the same repo. On your own machine, run `scripts/supervisor.sh` (it detects the CLI). Otherwise: open a new session on this repo/branch and paste `BOOTSTRAP_PROMPT.txt`.
- Raw data (`data/`) is git-ignored; re-download with `scripts/download_physionet2019.sh` (2019 sepsis, CC BY 4.0); 2012 challenge and eICU demo download commands are in decisions/journal (PhysioNet open files).

## Moving to a new account
1. Make sure the latest work is pushed (`git push`).
2. In the new session, check out branch `claude/pensive-galileo-vgrn1b` of `p_c1_16`.
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
