# IndexAlert independent audit — 2026-11-15 20:22 KST

Read-only verification of GitHub and Railway; isolated audit-only documentation. No workflow change, official market backtest, M20 economics, deployment, merge, order, promotion or credentials operation.

## GitHub PR heads (direct read, 2026-11-15)
| PR | Head SHA | State |
|---|---|---|
| #412 OpenDART | bf3d9514a87c53b1775e22ec9ba7711f6cecc49f | open draft |
| #413 offline optimisation | f003ef6247e16fcc71bd3b1b20cd4904c4d984c0 | open draft |
| #414 profitability gate | 18c5418d9684d1717df58261ea27f28e514385b2 | open draft |
| #418 single runner | 2f98401cc50a6c6a25808a98516efd5bf0c944ee | open draft |
| #420 KRX | fab3cbbd63a951a4e081f9e7f08c1391ca308581 | open draft |
| #422 KRX | c14857620973531013799e44625d43080904fd5f | open draft |
| #423 KRX | 0e38004363cac9fc4475556b3a1c445de9af407f | open draft |

Research index-alert-research-v1 and development index-alert-position-regen-fix-v1 live HEAD: NOT VERIFIED (no exact ref-to-commit resolution in this run). PR #414 integration gate file Git blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be; read at PR branch. This is a blob hash, not a file SHA-256 or evidence approval.

## CI direct job verification
- Actions 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success.
- OpenDART 38419439742: 2/2 success, candidate row evidence only, not public PIT/period proof.
- Runner 38419649711: 1/1 success synthetic-only.
- PR #418 integration 38486028854: 1/1 failure. Previously observed manifest Git blob SHA-1 mismatch research_v1_runtime_manifest.py expected 108f66714602a1bd3ae42c34dcca7c16e38f460b, observed e428789e2e97ca7be3a4482e0df23b483a1ad69d; exact failure reason not freshly retrieved from job log this run.
- Historical 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 not independently recomputed this run. Regression-only serial 2.9656 s versus concurrent 2.6209 s (1.1315x) is historical, not full CI/official backtest speedup.

## Railway production direct read
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. Environment describe returned staged=null (not proof historical staged patch resolved; cross-check pending status separately). Latest deployments: PIT rebuild 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; KRX historical worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS. Deployment success does not prove service health or source admission.

2026-11-15 10:10–11:25 UTC read-only logs: PIT 5 entries at 10:15, 10:30, 10:45, 11:00, 11:15 UTC all contain KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE, 803 common-stock rows, independent source/model/chronology admissions false, fresh alpha false, live orders false, funds movement false. Historical KRX worker: 0 log entries in queried interval (not evidence of no past processing). Runtime: Investing USD/KRW HTTPError, Yahoo fallback at 11:22 UTC. The 27 nonpositive OHLC rows and 2026-09-28 earliest failure session were observed in preceding run; not independently extracted from full raw JSON this run.

## Gate verdict
- Prospective KRX source quality: FAIL; fail-closed admission behaviour observed PASS in five consecutive log entries.
- 2017–2022 historical 1565/1565 weekday original-pair storage integrity: historical PASS only, not independently rehashed today.
- 2021/2022 original-filing three-month consolidated operating income period/correction lineage, public available-at, corp/security historical mapping: NOT VERIFIED.
- Official KRX calendar, trading states, corporate actions, fillability, cost/tax: NOT VERIFIED.
- Post-cost/tax annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, return concentration and temporal robustness: NOT VERIFIED; M20 economics NO-GO.
- Offline isolated regression suites: historical CI PASS for five specified runs; #418 integration FAIL; actual official backtest speedup NOT VERIFIED.

## Next independent steps / non-overlap
1. KRX owner to independently resolve 27 nonpositive OHLC records and source meaning, not silently drop rows or relax fail-closed veto.
2. OpenDART owner to establish original-filing exact period/lineage and public available-at evidence.
3. PR #418 owner to diagnose immutable archived blob mismatch in isolation without updating baseline to hide drift; independently verify 34-case SHA.
4. Reconcile Railway staged=null against pendingWork status without applying any patch.
5. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout restrictions, ORDERING=false, fail-closed cache SHA-256 identity and read-only post-processing parallelism. No official market performance runs until source PIT approved.
