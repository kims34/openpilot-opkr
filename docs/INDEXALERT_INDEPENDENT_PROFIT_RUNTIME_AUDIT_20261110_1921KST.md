# IndexAlert independent profitability/runtime audit — 2026-11-10 19:21 KST

Scope: independent read-only evidence verification and documentation only. No code, workflow, deployment, trade, model, or economic test changes.

## Immutable refs
- Research HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406`; development HEAD: `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branches API, checked this run).
- PRs open/draft/unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate file blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (read from its PR branch; not present on research base).
- Actions: 38381997417, 38382214223, 38419111311 each 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS (jobs checked this run). Fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` from previous attestation, NOT freshly recomputed. Synthetic-only pass, not economics.
- Prior regression-only serial 2.9656s vs parallel 2.6209s (1.1315x); overall CI/official backtest speed NOT VERIFIED. Later archived speed comparison 1.7650s vs 2.7079s (0.652x), so no general speed PASS.

## Railway production live evidence — NEW this run
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS, replica 1/1. Deploy log query from 2026-11-10T00:00Z returned **4 entries**, including `2026-11-10T10:00:43.414426477Z` and `2026-11-10T10:15:50.615515459Z`. Both explicitly report `session=2026-11-10`, `status=FAIL_CLOSED`, `ordering=DISABLED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `source_failure_session=2026-09-28`, `private_rejected_source_receipt_saved=true`, `session_manifest_sha256=null`, and all independent source/chronology/model admission and live-order/funds permissions false. This is runtime-log evidence of ORDERING disabled at logged instants, **not** direct verification of the environment variable or persistent state. PIT admission FAIL-CLOSED; source/chronology/model approval NOT VERIFIED.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS, replica 0/1 (0 crashed); 0 deploy log entries in requested window; live job execution NOT VERIFIED. Prior 1,565/1,565 weekday private raw-pair integrity PASS limited to storage; official trading calendar/status/fills NOT VERIFIED.
- Kiwoom real read-only deployment `a77fb922-b679-4d88-92c4-03054ec579cd`: SUCCESS but replica running 0, crashed 1/1: runtime health FAIL. 0 deploy log entries in requested window.
- Runtime and PIT rebuild each running 1/1. Backend/push/db-query-readonly offline; db-query-readonly critical 1. Staged environment patch `e113dacb-6705-4416-9997-dc694539d382` has zero changes; not applied.

## Independent gates
| Gate | Verdict | Boundary |
|---|---|---|
| OpenDART original SGML candidate signature / official source bytes | PASS only for earlier byte/signature attestations | 2021/2022 first-original CFS 3-month operating-profit cell meaning, correction lineage, exact public available-at/PIT NOT VERIFIED |
| Historical issuer-to-security mapping | NOT VERIFIED | as-of identifiers absent |
| KRX private weekday raw pair storage | PASS, prior attestation only | official calendar, halt/delist, actions, tradeability, execution, costs/taxes NOT VERIFIED |
| Prospective PIT runtime 2026-11-10 | FAIL-CLOSED | 27/803 nonpositive OHLC, missing independent admission; no alpha allowed |
| Kiwoom read-only runtime health | FAIL | 0 running, 1 crashed |
| Offline optimization CI | PASS software jobs only | full end-to-end acceleration, immutable transitive source archive and real official backtest NOT VERIFIED |
| Fees/tax-adjusted NetEV, PF, CAGR, MDD, ES95/99, profit concentration, temporal robustness, annual risk-adjusted net profitability | NOT VERIFIED | no admitted PIT, corporate-action/fill source or approved M20 economics run |

## Frozen safety and next steps
M20 NO-GO; H5 failed/consumed Holdout cannot be reused or post-hoc tuned. Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/sealed Holdout/Champion/Top3/NO_TRADE and costs/tax/risk rules unchanged. ORDERING=false requirement retained. Only synthetic offline software/safety tests before source PIT approval. Cache must fail closed unless independently approved source/data/code/Frozen policy/runtime/approval SHA-256 all match; parallelize only read-only independent postprocessing. Never parallelize dependent retraining or capital transitions. OpenDART owner must establish original CFS period/value and available-at lineage; KRX owner must reconcile official 90-day calendar/status and 27 OHLC failures; runtime owner must diagnose Kiwoom crash read-only. Do not edit other rooms' code, workflow, or production. No merge, promotion, orders, funds, permission changes or deployments.
