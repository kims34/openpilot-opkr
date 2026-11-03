# IndexAlert independent profitability / isolated runtime audit — 2026-11-03 20:16 KST

Scope: read-only GitHub/Railway evidence; no market/economic execution, no promotion, no deployment, no merges, no orders. This is a documentation-only isolated audit and **not** PIT admission.

## Verified refs (this execution)
- GitHub research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406` via fetch_commit(ref); development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`. Branch presence independently checked. HEADs are snapshots, not guaranteed stable.
- PR #412, #413, #414, #418, KRX #420/#422/#423: fetch_issue returned OPEN; draft claims appear in PR descriptions, but draft boolean and exact PR HEADs were **not independently obtained** this run. PR #414 gate file read directly at `refs/pull/414/head`; its storage-integrity PASS and PIT NO-GO claims are historical, not newly certified.
- Actions 38419111311: six job success records inspected; 38419649711: one job success record inspected. Existing 34-case identity SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 mocks and 28 synthetic controls are **historical reported evidence**, not independently rehashed in this run. 38381997417/38382214223 were not re-fetched this run.
- Action 41515392296: `auto-anchor` job FAIL at `Fetch today's public hash-only prospective payload`; subsequent chronology append SKIPPED; validation SKIPPED. Specific HTTP response not proven by job metadata alone.
- Railway IndexAlert production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`: KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS at commit `1e6367d2863a86c3470da13d81a955d277eba485`; PIT deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS at `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`. Deployment SUCCESS is not data approval.
- PIT read-only logs, 2026-11-02 UTC: `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, `session_manifest_sha256=null`, `FAIL_CLOSED`, `ORDERING=DISABLED`; no independent source/model/chronology admission. Railway KRX worker log sample empty; absence of entries does not prove health or failure.
- Runtime service logs observed 2026-11-03 11:16 UTC; market quotes/alerts are **not** official KRX PIT evidence or M20 return measurements.

## Independent verdict
| Gate | Verdict | Why |
|---|---|---|
| KRX historical raw pair byte storage 1565/1565 | historical PASS only | 2026-10-14 provenance; not rehashed this execution |
| KRX official historical calendar, 90 uncertain sessions, stock/day trading state, corporate actions, fills, tax | NOT VERIFIED / FAIL-CLOSED | No independently authenticated exchange PIT/tradability admission |
| OpenDART original-filing exact 2021/2022 first 3-month consolidated operating profit, correction lineage, public available-at, historical corp/security mapping | NOT VERIFIED / FAIL-CLOSED | SGML 15 candidate shapes and adjacent-number signatures do not prove semantic quarter or publication instant |
| Chronology anchor Action 41515392296 | FAIL | payload fetch job failed; downstream skipped |
| PR #413 offline regression engineering | LIMITED PASS | six successful synthetic/offline CI jobs; not market/economic authority |
| PR #418 one-runner synthetic CI | LIMITED PASS | one successful job; reported serial 2.9656s vs concurrent 2.6209s = 1.1315x regression phase only; no full-CI/backtest speedup proven; archived manifest mismatch not independently resolved |
| NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after costs/tax | NOT EVALUABLE / NO-GO | M20 economic run not approved, no admissible PIT source |
| M20 run, Champion, live orders | NO-GO | no separate approval and upstream blockers remain |

## Frozen policy and next evidence
Keep H5 consumed Holdout and Dynamic results isolated; M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, original risk/cost/tax gates unchanged. Cache only with complete independent source/data/code/Frozen/runtime/approval SHA256 equality, otherwise fail-closed; parallelise only read-only independent postprocessing. ORDERING=false. No GitHub workflow modifications, source acquisition expansion, strategy trials, economic runs, broker actions, deployment or merges.

Next: independently attest original filing's period/consolidation/available-at and correction lineage; authenticate KRX calendar and stock/day tradability plus corporate actions and costs; resolve chronology payload failure and prospective OHLC anomaly without bypass; verify immutable manifest SHA and exact CI artifacts before claiming any optimisation. Keep M20 NO-GO until all independent evidence gates PASS.
