# IndexAlert independent profitability/runtime audit — 2026-11-05 05:23 KST

Scope: read-only GitHub/Railway evidence, offline-only optimization policy. This isolated document does not approve source PIT, trading, M20, merging, deployment or model selection.

## GitHub refs observed
- Research integration base SHA (PR #414): `3b8b7830612a6284d7c7a60628cb527cb741627a` (NOT VERIFIED as current research branch HEAD).
- Development integration base SHA (PR #420): `1e6367d2863a86c3470da13d81a955d277eba485` (NOT VERIFIED as current development branch HEAD).
- Draft OPEN unmerged PR heads: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 integration gate file Git blob SHA-1: `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Actions: 38381997417, 38382214223, 38419111311 each 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. Chronology anchor 41515392296: auto-anchor failure, validation skipped.
- Prior 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic checks and 2.9656s/2.6209s = 1.1315x are HISTORICAL REPORTED, not independently recalculated in this run. Full CI or official market backtest speed NOT VERIFIED.

## Railway production (read-only)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, running 1/1; KRX historical worker SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c`, currently no running replica (cron/worker state cannot establish PIT).
- Runtime SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, running 1/1. Since 2026-11-04 19:00 UTC: PIT rebuild 0 deploy log entries, KRX worker 0; runtime has live FX index lookup with Yahoo fallback, NOT an official historical PIT admission.
- Kiwoom real-readonly displays online but replica running=0, crashed=1, deployment `a77fb922-b679-4d88-92c4-03054ec579cd`. Push/backend offline warnings; db-query-readonly offline critical. These were already observed earlier, not independently new incidents.
- Staged Railway patch `e113dacb-6705-4416-9997-dc694539d382` remains uncommitted; do not apply.

## Admission gates
PASS (limited, prior evidence): 1565/1565 KRX private weekday raw pairs storage integrity; historical synthetic CI job success only.
FAIL: chronology auto-anchor action; observed earlier OHLC fail-closed (not retested this interval).
NOT VERIFIED: official original-filing public available-at/PIT, 2021/2022 original consolidated three-month operating profit period/restatement lineage, historical entity-security mapping, official KRX calendar/trading states/corporate actions/fillability, tax/cost admissibility, NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness, full runtime acceleration.
Decision: M20 NOT EVALUABLE / NO-GO. H5 consumed holdout and Dynamic results must not be recycled. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all economics/risk/promotion thresholds remain unchanged. ORDERING=false. No market performance experiments.

## Next safe steps
1. Obtain original DART filing-time and amendment lineage provenance independently before any PIT admission.
2. Verify official KRX historical session/market-state and corporate-action/fillability evidence against immutable source SHA; exclude zero activity and unapproved classifications.
3. In separate optimization isolation, verify SHA-256 provenance of source/data/code/Frozen/runtime/approval evidence, fail-closed cache invalidation, and read-only independent postprocessing parity using synthetic offline fixtures only. Do not parallelize dependent retraining or capital transitions.
4. Inspect Kiwoom replica crash and offline alerts read-only; do not modify deployment or permissions.
5. No M20 run, PR merge, workflow edit, live trading or Champion promotion without explicit separate authorization.
