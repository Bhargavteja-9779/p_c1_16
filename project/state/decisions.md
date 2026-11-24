# Decisions log (append-only)

| # | Date | Decision | Reason |
|---|------|----------|--------|
| D1 | 2026-11-24 | Run on this cloud container: CPU only (4 cores, 15 GB RAM, no CUDA/MPS). "GPU hours" budget in Section 0 is interpreted as CPU compute hours, tracked identically. | nvidia-smi absent; torch.cuda unavailable. Topic must therefore be CPU-tractable. |
| D2 | 2026-11-24 | Project lives in `project/` inside git repo `p_c1_16`, branch `claude/serene-newton-bylqpn`; persistence across accounts = git push to that branch. | Container is ephemeral; boot autostart does not survive container reclamation. |
| D3 | 2026-11-24 | Journal turnaround verified from Crossref `assertion` metadata (received/accepted dates), which Springer Nature deposits; Elsevier deposits no dates and ScienceDirect returns HTTP 403 here, so Elsevier journals cannot be verified for G1 and are treated as UNVERIFIED on turnaround. | Rule 2/3: only verifiable numbers. |
| D4 | 2026-11-24 | Selected journal: **Critical Care** (BMC/Springer Nature, ISSN 1364-8535). | Verified median Accepted−Received 66 d for full research articles (n=318, Crossref assertions); JIF 11.4 (2025) on official page; best fit for open ICU data + CPU ML. JCR quartile UNVERIFIED (paywall). Fallback: Journal of Intensive Care (69 d, JIF 7.5). |
| D5 | 2026-11-24 | Not using headless browser on ScienceDirect (tool policy denied it as unauthorized access); Elsevier remains unverifiable. Springer journal pages rendered normally in a browser for public metrics. | Respect site access controls. |
| D6 | 2026-11-24 | Compute ledger counts machine-occupied wall seconds (any job running), regardless of how many CPU workers run in parallel. 1 machine-hour = 1 budget hour. | Closest analogue of "GPU hours" on a single machine. |
