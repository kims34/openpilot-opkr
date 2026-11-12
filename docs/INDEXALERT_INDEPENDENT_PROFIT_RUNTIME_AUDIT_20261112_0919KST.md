# IndexAlert independent audit — 2026-11-12 09:19 KST

## Read-only provenance
GitHub PR metadata, GitHub Actions jobs, PR #414 gate file, prior isolated audit, Railway production environment status and deploy logs read at 2026-11-12 00:19 UTC. No market backtest, trading, deployment or merge. Prior isolated audit branch commit: `d93e4277f01311bd89a5e93cb6380902ce73a03c`. Research/development refs last independently reported `df474df348f22aa38b1dedaa59fcff66e548b406` / `1e6367d2863a86c3470da13d81a955d277eba485`; branch tip equality was NOT independently queried in this run.

## Exact PR HEADs (fresh)
- #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- #414 `18c5418d9684d1717df58261ea27f28e514385b2`; gate document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`
- #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`
All OPEN/DRAFT, unmerged. No edits to specialist branches.

## CI evidence
- Actions 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success; 38419649711: 1/1 success; 38419439742: 2/2 success (fresh jobs API).
- 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: historical assertion, independent recomputation NOT VERIFIED. 13 adversarial and 28 synthetic checks: previously reported, not rerun. Serial 2.9656 s vs concurrent 2.6209 s = 1.1315x only regression phase historical, whole CI/official PIT backtest acceleration NOT VERIFIED.
- Frozen policy, fail-closed evidence-keyed cache and read-only independent postprocessing only. No dependent model retraining/capital transitions parallelized.

## Railway production
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild and runtime each running 1/1; KRX historical worker 0/1 running (online label insufficient); Kiwoom real readonly 0/1 running, 1/1 crashed: FAIL. Backend, push, db-query-readonly offline; db-query-readonly 1 critical.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` has empty changes array. Not applied.
- 2026-11-11 23:00–2026-11-12 00:20 UTC deploy-log query: PIT/KRX/Kiwoom 0 entries. Runtime logs show Investing USD/KRW HTTP error followed by Yahoo fallback, and Naver KOSPI quote retrieval; neither is official historical KRX PIT validation.

## Source and economic admission gates
| Gate | Verdict | Evidence / blocker |
|---|---|---|
| 2017–2022 KRX 1565/1565 weekday raw-pair storage | PASS (historical limited scope) | Prior private storage integrity; no fresh raw SHA recomputation |
| Official KRX calendar, halts, delistings, corporate actions, mapping, fillability, costs/taxes | NOT VERIFIED / FAIL-CLOSED | Official time-aware market-state proof absent |
| OpenDART original SGML candidate rows and numerical adjacency | Historical narrow CI PASS | Action 38419439742 jobs successful; exact 2021/2022 original CFS three-month operating profit, corrections and public available-at NOT VERIFIED |
| PIT original filing, 2021/2022 lineage, security historical mapping | NOT VERIFIED | Missing complete independently reconciled source and timing |
| H5 / consumed holdout / Dynamic | NO-GO | Do not retune or reuse as independent holdout |
| M20 horizon20/purge20 WF504/126/126 and after-cost/tax NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness | NOT VERIFIED / NO-GO | Source and market PIT unapproved; no economic run |
| Offline runner parity | CI jobs PASS; bytewise SHA NOT VERIFIED | No fresh independent 34-case digest |
| Official end-to-end speed | NOT VERIFIED | No approved source PIT or official performance run |

## Next allowed actions
Obtain independent source-file SHA and timestamp lineage for original OpenDART CFS 3-month periods; independently reconcile official KRX session/halts/corporate actions and fillability; verify frozen policy and complete evidence key; independently recompute offline 34-case digest without economic data. Until all gates pass, only synthetic offline safety tests; maintain ORDERING=false, M20 NO-GO, no orders/funds/credentials/champion promotions, no deployment/merges, no workflow writes.
