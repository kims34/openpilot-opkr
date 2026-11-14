# IndexAlert independent evidence audit — 2026-11-14 09:24 KST

Scope: read-only source and CI checks; no performance run, trading, deployment, PR merge, policy adjustment, or workflow edit. Prior isolated audit branch HEAD before this note: `829ac0ca4fb0ded73041aa52b2b3a38aeca97d56` (compare identical). Evidence statuses below describe the specific proof, not economic approval.

## Immutable refs checked
- Research `index-alert-research-v1` = `df474df348f22aa38b1dedaa59fcff66e548b406`, compare identical (0 ahead/behind).
- Development `index-alert-position-regen-fix-v1` = `1e6367d2863a86c3470da13d81a955d277eba485`, compare identical.
- Draft open, unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 frozen gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob Git SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (not SHA-256).
- GitHub Actions jobs direct re-read: [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) each 6/6 success; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 success; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 success; [38486028854](https://github.com/kims34/openpilot-opkr/actions/runs/38486028854) 1/1 failure (archived manifest mismatch previously reported; failure cause not re-read from step log in this run).
- Historical reported fixed 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` NOT VERIFIED by fresh independent recomputation. Synthetic software CI PASS for listed jobs; total CI speed and official PIT backtest acceleration NOT VERIFIED. Historical single-runner regression phase serial 2.9656 s vs concurrent 2.6209 s = 1.1315x slowdown, not acceleration.

## Railway production direct read
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest deployment SUCCESS: PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` 1/1 running, Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` 1/1 running, KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` 0/1 running. Kiwoom real-readonly-run SUCCESS deployment but 0/1 running; indexalert-kiwoom-real-readonly offline. Backend/push/db-query-readonly offline. Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29 remains, not deployed.
Log query 2026-11-13 23:00 through 2026-11-14 00:25 UTC: PIT 0 entries; KRX 0 entries; Runtime returned 201 entries (limit 200; connector over-returned), including repeated Investing USD/KRW HTTPError -> Yahoo fallback at 00:23:43 UTC. Absence of PIT/KRX logs is not remediation proof. Prior 27/803 OHLC abnormalities and 12,003 zero-activity quarantines remain unresolved without new official evidence.

## Independent decision gate
- OpenDART original-filing ZIP/SGML candidate extraction and CI: limited software/source evidence PASS; exact 2021/2022 initial three-month consolidated operating-profit period/values, correction lineage, original public available-at, issuer/security PIT mapping: NOT VERIFIED / FAIL-CLOSED.
- KRX private weekday pair persistence 1565/1565: historical storage integrity PASS only; official sessions, security status, corporate actions, executions, liquidity, fee/tax PIT: NOT VERIFIED / FAIL-CLOSED.
- Post-fee/post-tax annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, regime/date robustness: NOT VERIFIED, M20 performance RUN not authorized.
- H5 consumed holdout/Dynamic result cannot be recycled. Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, Top3/NO_TRADE and costs/risk/advancement rules unchanged. ORDERING=false; no live orders, money movement, permission changes, Champion promotion.
- Optimization cache requires all approved source/data/code/Frozen/runtime/evidence SHA-256 identities, fail closed; parallelize only independent read-only postprocessing. No dependent retraining or capital transition parallelization.

Next: source teams independently resolve original-filing PIT and official KRX tradability, CI owner resolve archived manifest mismatch without touching shared Work/workflows, and separately reproduce 34-case SHA-256 in an isolated offline-safe setting. No official economic run or optimization claim before gates pass.
