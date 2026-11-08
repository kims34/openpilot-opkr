# IndexAlert independent profit/runtime audit — 2026-11-08 22:24 KST

Read-only evidence inspection; no trading, deployment, merge, workflow modification or economic replay.

## GitHub current PR evidence (GitHub connector read at this run)
- #412 OPEN Draft head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 OPEN Draft head f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 OPEN Draft head 18c5418d9684d1717df58261ea27f28e514385b2; gate document blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be
- #418 OPEN Draft head 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #420 OPEN Draft head fab3cbbd63a951a4e081f9e7f08c1391ca308581
- #422 OPEN Draft head c14857620973531013799e44625d43080904fd5f
- #423 OPEN Draft head 0e38004363cac9fc4475556b3a1c445de9af407f
- Research index-alert-research-v1 and development index-alert-position-regen-fix-v1 branches: existence confirmed, exact current HEAD NOT VERIFIED in this run. Historical reported reference heads df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 are not reasserted as current.

## CI job evidence
- Actions 38381997417, 38382214223, 38419111311: each 6/6 completed success.
- Action 38419649711: 1/1 completed success. OpenDART 38419439742: 2/2 completed success.
- Chronology Anchor 41515392296: auto-anchor FAILURE, validation SKIPPED.
- Historical 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic, and 2.9656/2.6209 seconds are previous evidence, not recalculated this run. Whole CI or official backtest acceleration NOT VERIFIED.

## Railway production read-only evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild replica running 1/1; runtime running 1/1.
- Kiwoom real-readonly service marked online / deployment SUCCESS, but replicas running 0, crashed 1: operational mismatch, FAIL for live-readiness.
- db-query-readonly offline with one critical; backend offline four warnings; push offline one warning.
- KRX historical worker marked online with 0 running, 0 crashed of 1 replica: no positive evidence of active execution.
- Pending empty staged patch e113dacb-6705-4416-9997-dc694539d382; do not apply.
- PIT deployment logs at 21:00, 21:15, 21:30, 21:45, 22:00, 22:15 KST repeat KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE. No new alpha admitted. KRX and real-readonly deploy logs in 21:00–22:24 KST query: zero entries. Runtime logs are market display, not PIT evidence.

## Gate verdict
- KRX 2017–2022 private 1565/1565 weekday original-pair storage integrity: historical PASS only; official exchange calendar/status, corporate actions, execution eligibility NOT VERIFIED.
- Original OpenDART filing public available-at, first 3-month consolidated operating-profit period and amendment lineage (2021/2022), historical entity/security mapping: NOT VERIFIED.
- Chronology Anchor action: FAIL.
- Cost/tax-inclusive NetEV, PF, CAGR, MDD, ES95/99, return concentration, time robustness: NOT VERIFIED. M20 economics RUN NOT AUTHORIZED; NO-GO.
- Optimization: offline synthetic CI PASS for listed jobs; official backtest acceleration NOT VERIFIED.
- ORDERING=false; Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout restrictions and fail-closed SHA-256 cache matching unchanged.
- Next: independently reconcile original filing timestamps/period lineage and official KRX status with source hashes; diagnose chronology 404 and Railway read-only crash in separate approved workspaces; synthetic-only software validation until PIT approval.
