# IndexAlert independent profitability admission audit — 2026-11-02 01:49 KST

**Decision: M20 NO-GO / FAIL-CLOSED.** This is a single isolated evidence-only audit note. No original market-data acquisition, M20 profitability execution, Holdout access, strategy alteration, PR merge, deployment, broker order, funds or permission change. No source-owner or optimization workstream duplicated.

## Direct GitHub reads
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #414 pre-write HEAD `1d66132c363cc32e6fde23c9bc28bf6eb14f1eaf`; #412 HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; KRX #420/#422/#423 all open, Draft, unmerged.
- New latest [Watchdog Actions #41323960188](https://github.com/kims34/openpilot-opkr/actions/runs/41323960188) (2026-11-01 15:59 UTC): job `124899883924` succeeded. Actual log: 4/4 fail-closed watchdog tests and 31/31 offline governance tests pass; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is not data admission.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): fetch of public `/anchor/latest` failed with HTTP 404; chronology record/validation steps skipped.

## Independent source-evidence boundary
- Prior official [2022 original OpenDART Actions #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), job `115241142185`, was independently re-read. Its original-source flag record: ZIP received, CRC verified, one legacy SGML/HTML entry, 1,570 tables, 15 operating-profit candidate row shapes, zero strict first-twelve-row or nearby-text Q3 exact-window matches, and `original_q3_cfs_three_month_profit_bound=false`.
- Recorded 2022 first-edition ZIP SHA-256: `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; recorded corrected-edition SHA-256: `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`. These are earlier official Action attestations; **no raw original ZIP bytes were independently reacquired/rehashed in this run**. Git blob SHA-1 is not a raw source SHA-256.
- Exact first-available publication instant, 2022/2021 standalone three-month CFS operating-income facts, full amendment lineage, historic issuer/security mapping remain unapproved. A corrected filing must not fill earlier PIT gaps.
- Prior KRX 2017–2022 1,565/1,565 weekday raw daily/master pairs storage SHA integrity PASS is **not** trading PIT PASS. Unresolved 90 market calendar/source-gap sessions and separately 27 common-stock nonpositive-OHLC cases remain quarantined. Other broader-period counts are distinct populations. Historical official listing/trading status, halts, corporate actions, market cap, lot/quote liquidity and feasible fills remain unverified.

## Direct Railway production reads
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT service `indexalert-pit-rebuild`: latest returned deploy log 2026-11-01 14:46:22 UTC (23:46:22 KST), `COMMON_OHLC_NONPOSITIVE`, `fresh_alpha_observation_admitted=false`, independent chronology/model admission false. Prior runtime logs consistently `FAIL_CLOSED`, `ordering=DISABLED`.
- Kiwoom REAL read-only service `indexalert-kiwoom-real-readonly`: deployment marked SUCCESS, but environment health shows 0 running / 1 crashed replica; no new authenticated read-only feed success proven.
- Railway `describe_environment` and `get_staged_changes` returned `staged=null`; `environment_status` separately returned pending staged patch `e113dacb-6705-4416-9997-dc694539d382` with no listed changes. **Read API discrepancy**, not approval or permission to accept/deploy. No staging mutation performed.

## Independent economics decision
- Pre-registered M20: 20-session horizon, 504/126/126 train/cal/test, purge20, Top3/no rank-4 backfill, NO_TRADE, fixed costs and 2x-cost stress. Keep Frozen/Champion/Holdout untouched.
- Trading feasibility requires point-in-time official market and security state, corporate actions, prices/volumes, quotes/lot sizing and realistic fill assumptions; fees, spread, impact, slippage, turnover, tax timing/rates and FX must be specified without hindsight.
- **After-tax NetEV, Profit Factor, CAGR, MDD, ES95/ES99, date-cluster LCB, concentration and capacity are NOT COMPUTABLE/NOT VERIFIED** on admitted evidence. No placeholder profitability number or synthetic result is accepted as a historical result.
- M20 execution forbidden pending independent source SHA/PIT and tradability/cost/tax admission. `ORDERING=false`, no real orders, funds/permissions/deploy/merge/Champion promotion. Keep PR #414 Draft and isolated documentation-only.
