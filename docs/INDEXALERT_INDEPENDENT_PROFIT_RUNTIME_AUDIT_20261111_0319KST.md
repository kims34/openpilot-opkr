# IndexAlert independent audit — 2026-11-11 03:19 KST

Scope: read-only GitHub and Railway checks, no official economic replay, no workflow changes. This isolated document is not an admission or strategy modification.

## Exact refs
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Branch comparison: diverged, development ahead 1148 / behind 281 relative to research.
- OPEN/DRAFT/UNMERGED PR heads: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate path `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` on PR branch `indexalert-profitability-integration-evidence-20261013`: blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. A 404 on the research base is expected; it does NOT indicate deletion.
- GitHub Actions job conclusions checked: 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS. Individual fixed-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, adversarial mock counts, and synthetic counts were not independently recalculated this run.
- Offline runner 2.9656s serial vs 2.6209s concurrent (1.1315x regression-phase only) is prior evidence, not a newly measured total-CI or market backtest acceleration.

## Railway production
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest deployment: PIT rebuild SUCCESS `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`; runtime SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`; KRX worker SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c`; Kiwoom real readonly SUCCESS `a77fb922-b679-4d88-92c4-03054ec579cd`; backend FAILED `cce12a43-592a-4910-9b75-89c6b7cdd159`; push FAILED `3ad3102d-ced6-416b-a6da-85c390c9a606`. Replica counts returned null for every service: runtime health NOT VERIFIED, not a running/failed inference. Since 2026-11-10 16:00 UTC, PIT/KRX/Kiwoom deploy log queries each returned zero entries: absence of logs is not a PASS. Environment stagedChanges null, but pendingWork includes an old empty staged patch (zero changes); not applied.

## Gate verdicts
| Area | Verdict | Reason |
| --- | --- | --- |
| KRX 2017-2022 private 1565/1565 weekday pairs storage SHA | PASS (historical pinned evidence only) | Storage integrity does not establish market calendar or execution. |
| OpenDART 2022 original/correction 15 operating candidate rows and numeric-neighbor signature | PASS (prior candidate matching scope only) | Original consolidated 3-month meaning/available-at NOT VERIFIED. |
| OpenDART 2021 initial 3-month consolidated operating profit | NOT VERIFIED | PR #414 source notes 13 label candidates but zero explicit matching 3-month table; original ZIP byte SHA prior evidence is not a financial-cell semantic proof. |
| 2021/2022 first original, correction lineage, public available-at, historical corp/security mapping | NOT VERIFIED | Missing exact source-cell/time semantics. |
| KRX official historical trading status, corporate actions, fillability, costs and taxes | NOT VERIFIED | 90-day uncertainty, 12003 zero-activity observations and 27 OHLC veto remain quarantined. |
| Offline optimization CI jobs | PASS (job completion only) | No new SHA recomputation or official workload performance. |
| NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after costs/taxes | NOT VERIFIED | Official PIT admission absent; M20 economics not run. |
| Backend and push latest deployments | FAIL (deployment status) | Both Railway latest deployments FAILED; service health not independently proven. |
| Runtime ORDERING environment value | NOT VERIFIED | Do not infer configuration from historic logs. |

## Binding constraints and next safe actions
Maintain M20 NO-GO; frozen H5, horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all cost/tax/risk/upgrade rules unchanged. Consumed H5 holdout and Dynamic results cannot be retuned or reused as independent. ORDERING=false is required; never enable orders. No trading, funds, credential changes, Champion promotion, merge or production deploy. Do not run economic M20 or new official market performance experiments until independent PIT approval. Cache only when independent source/data/code/frozen-policy/runtime/approval SHA-256 all match fail-closed; parallelize read-only independent postprocessing, not dependent training or capital transitions.

Next: owner-specific independent source-cell and available-at attestation for 2021/2022; KRX official trading-status/corporate-action evidence; exact SHA and CI artifact parity checks in offline synthetic isolation; confirm Railway runtime replica and ORDERING state without changing production. Avoid modifying other Work-owned code or workflows.
