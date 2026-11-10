# IndexAlert independent profitability and runtime audit — 2026-11-10 15:21 KST

Read-only evidence inspection; isolated documentation only. No M20 economic run, live trading, deployment, merge, workflow modification, model search or sealed Holdout reuse.

## GitHub immutable evidence
- Research branch PR base reference: `3b8b7830612a6284d7c7a60628cb527cb741627a`; **current research branch HEAD not independently resolved** in this pass. Development PR #420 base `1e6367d2863a86c3470da13d81a955d277eba485`; current development branch HEAD likewise not independently resolved. These are PR base refs, not an asserted fresh branch HEAD.
- All OPEN/Draft/unmerged: PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, #414 `18c5418d9684d1717df58261ea27f28e514385b2`, #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): each 6/6 job SUCCESS; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 SUCCESS. Fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is a prior recorded value, not freshly recomputed. Historical regression-phase 1.1315x is not end-to-end acceleration; newer PR #414 evidence notes sampled #413 0.652x speed ratio and #418 archive drift failure.
- Gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` is on PR #414 head, not research base (base-path fetch returned 404). Prior blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; not recomputed this pass.

## Railway production — native read-only API, 2026-11-10
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`. Latest PIT deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (commit `1e6367d2863a86c3470da13d81a955d277eba485`); real readonly `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`); backend and push FAILED. Replica counts returned null for all services; **runtime liveness NOT VERIFIED**, regardless of deployment status. PIT, KRX and real readonly service deploy-log queries from 2026-11-10 00:00 UTC returned 0 rows each, not proof of health. Staged patch null. No deployed change.

## Gate decisions
| Evidence domain | Decision | Limitation |
|---|---|---|
| Historical KRX 1565/1565 stored weekday SHA pairs | PASS (prior storage integrity only) | Official market calendar, 90 uncertain sessions, 27 OHLC anomalies, halts/corporate actions/fills NOT VERIFIED |
| OpenDART original/correction SGML 15 candidate row signatures | PASS (prior signature check only) | 2021/2022 first 3-month consolidated operating-profit semantic cell, corrected-vintage lineage, exact public available-at/PIT NOT VERIFIED |
| Issuer/security historical mapping | NOT VERIFIED | As-of identity and tradability absent |
| Optimization offline CI | PASS (software jobs only) | No current original-data PIT or complete production acceleration proof |
| Chronology/production anchor | FAIL (previous HTTP 404 evidence) | No new successful authoritative anchor attestation |
| After-tax NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness and annual risk-adjusted net profit | NOT VERIFIED | Source PIT and executable trade receipts not admitted |
| M20 profitability admission | NO-GO | No new independent source approval |

Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE, costs/taxes/risk/promotion criteria unchanged; ORDERING=false required (live setting NOT VERIFIED). Cache fail-closed unless source/data/code/Frozen policy/runtime/approval SHA-256 all match. Only independent read-only postprocessing may parallelize; never dependent retraining or capital transition. H5 consumed Holdout and Dynamic results cannot be tuned/reused.

Next: OpenDART owner establishes exact first-original consolidated 3-month cell/publication timestamp and correction lineage; KRX owner proves official as-of trading calendar/status, 90/27 exceptions and executable fills; runtime owner independently closes transitive source/manifest drift and evaluates full CI speed offline. Keep specialist PRs Draft. Do not modify other owners' code, workflow, accounts, credentials, orders, funds, deployment or Champion.