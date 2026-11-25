# HANDOFF — read this first

_Last updated: 2026-11-25 ~01:30 UTC (cycle 2, plan_v3b confirmation running)_

## Where we are
- **Cycle:** 2 **Phase:** plan_v3b CONFIRMATION running (E7–E10 on test, seeds 100–104; 220 jobs). Exploration done (journal 014). analyze_v3.py frozen at 9e2e93b.
- **NEXT ACTION:**
  0. Fresh container? `pip install lightgbm==4.7.0 pandas==3.0.5 scikit-learn==1.9.1 statsmodels pyarrow scipy`, `bash scripts/download_physionet2019.sh` (repeat until `bad=0`), then `python3 scripts/prepare_data.py` (~4 min; must print md5 0883ae5b4726bdc6fbe0c41bbc4f7d6d — the split is pinned in configs/, D19).
  1. `python3 scripts/status.py`; if v3 confirm jobs not done: `nohup setsid python3 run_all.py --mode full --resume --workers 2 --only E7_factorsc,E8_mechc,E9_sizec,E10_poolc > logs/run_all_v3c.out 2>&1 < /dev/null &`
  2. When done: `python3 scripts/analyze_v3.py --phase confirm --nboot 2000` (FROZEN, do not edit), then RESULT journal entry, gates G6/G7, novelty re-score, `python3 scripts/final_report.py`.
  3. Then: blind novelty re-score by a fresh-context agent; scripts/audit_numbers.py; paper draft (Section 9) once G1–G9 pass; review panel (Section 10).
  Done this session: G8 PASS (D22); G4 PASS via published-protocol reproduction (D25); prior art 48 opened (D20).
- **Selected journal:** Critical Care (BMC/Springer Nature, ISSN 1364-8535). Verified median Accepted−Received 66 d; JIF 11.4; JCR quartile UNVERIFIED.
- **Topic (v2):** factorial ICU-unit × hospital transport analysis of sepsis early warning on PhysioNet 2019 (topic/selected_topic.md).
- **Hypotheses (plan_v2):**
  - H1: site gap > unit gap.
  - H2: estimate the share of the site component removed by unlabelled fixes.
  - H3: label-free AUROC estimates err > 0.03 in ≥ 50% of transfers.
- **CONFIRMATION (E6, test, seeds 100–104):** H1 supported — LightGBM D 0.026 [0.005, 0.049], Holm p 0.018; LR D 0.063 [0.031, 0.098], Holm p 0.0015. H2: pre-specified share 0.85 [0.26, 3.13] BUT site-src AUROC unchanged (0.763→0.762); D shrinks because unit-src/local degrade → fixes do not recover site loss. H3 supported: 77–100% of transfers err > 0.03. See journal 012.
- **Validation results (exploration):**
  - H1: D = 0.043 [0.021, 0.066] for LightGBM; 0.066 for LR.
  - H2: about 0.61 of the site component is removable.
  - H3: label-free estimates miss in 64–92% of transfers.
  - See journal 010.

## Running right now
- run_all.py --only E7_factorsc,E8_mechc,E9_sizec,E10_poolc (detached; started 01:03 UTC). Log: logs/run_all_v3c.out.

## Compute
- Machine: cloud container, 4 CPU cores, 15 GB RAM, **no GPU**. Budget hours = machine-occupied hours (D1, D6).
- Used: ~1.11 h of 15 h (cycle 1); ~1.11 h of 120 h (global) — state/budget.json (+0.15 h analysis CPU not in ledger).

## Gate status
| Gate | Status | Evidence |
|---|---|---|
| G1 Journal | PASS on ≤72 d + publisher; **JCR Q1 UNVERIFIED** | journal_selection/selected_journal.md |
| G2 Prior art | **count met**: 82 queries, 48 papers opened (≥8 queries/claim for P1–P3); claim table done; P1 design appears novel, P2/P3 partly done (D20). Re-check before writing. | state/novelty_ledger.json, literature/claim_table_v2.md |
| G3 Novelty | FAIL (self-score 12/25: diff 3, mech 2, evid 3, breadth 1, signif 3; blind reviewer not run) | state/novelty_ledger.json scores |
| G4 Baselines | PASS: published protocol reproduced — cohort 30,629/1,837 vs 30,646/1,843; A→B drop −0.115 vs −0.117 (D25) | results/g4_reproduce.json |
| G5 Main result | PASS for H1 (D16 definition): both models Holm p < 0.05, CI excludes 0, effect 0.026 / 0.063 AUROC (ratio 1.6 / 2.2) | results/analysis/E6_confirm_test.json, journal 012 |
| G6 Ablation | partial: fixes ablated (harm / noproc / norm), model class and metric level varied | tables/E6_confirm_test_transport.md |
| G7 Generalization | FAIL so far: 1 dataset (4 cells, 2 directions, 2 models); eICU demo pending | — |
| G8 Leakage | PASS: 0 patients in >1 split/cell, 0 duplicate series, 0/200 look-ahead mismatches, no forbidden features, fit scope asserted | results/leakage_check.json, scripts/leakage_check.py |
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
