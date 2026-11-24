# Decisions log (append-only)

| # | Date | Decision | Reason |
|---|------|----------|--------|
| D1 | 2026-11-24 | Run on this cloud container: CPU only (4 cores, 15 GB RAM, no CUDA/MPS). "GPU hours" budget in Section 0 is interpreted as CPU compute hours, tracked identically. | nvidia-smi absent; torch.cuda unavailable. Topic must therefore be CPU-tractable. |
| D2 | 2026-11-24 | Project lives in `project/` inside git repo `p_c1_16`, branch `claude/serene-newton-bylqpn`; persistence across accounts = git push to that branch. | Container is ephemeral; boot autostart does not survive container reclamation. |
| D3 | 2026-11-24 | Journal turnaround verified from Crossref `assertion` metadata (received/accepted dates), which Springer Nature deposits; Elsevier deposits no dates and ScienceDirect returns HTTP 403 here, so Elsevier journals cannot be verified for G1 and are treated as UNVERIFIED on turnaround. | Rule 2/3: only verifiable numbers. |
