# IndexAlert independent read-only profitability gate — 2026-10-30 09:44 KST

## Scope and authority
Documentation-only independent audit; no protected source-volume access, new KRX/DART request, financial backtest, Holdout opening, broker connection, or production mutation. This note does not admit any source, performance, strategy, or order. No changes to other specialist tasks.

## Fresh GitHub repository state
- Direct REST branch reads: research `index-alert-research-v1` = `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` = `1e6367d2863a86c3470da13d81a955d277eba485`; KRX specialist `indexalert-krx-pit-source-audit-20261013` = `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Direct PR reads: #414 head before this note `8a8f42137046fac36b45cd87ad5c7bf5eed6346e`; #412 `bf3d95114a87c53b1775e22ec9ba7711f6cecc49f`; #416, #418, #420, #422, #423 and #413 remain open/Draft/unmerged. No PR merge or Champion promotion.
- GitHub Actions REST run list total 4,621. Latest [watchdog #40960712047](https://github.com/kims34/openpilot-opkr/actions/runs/40960712047), started 2026-10-29T21:47:26Z (2026-10-30 06:47:26 KST), SUCCESS; actual job logs show 4 watchdog and 31 governance tests passed, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Success is not source or profitability approval.
- [Chronology Anchor #40914179246](https://github.com/kims34/openpilot-opkr/actions/runs/40914179246) failed HTTP 404 fetching `/anchor/latest`, after retry; no chronology record was appended by that run.

## Independent SHA/PIT and market-tradability evidence
- [2022 first-filed OpenDART source-only run #38381866190](https://github.com/kims34/openpilot-opkr/actions/runs/38381866190) records original document ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 15 operating-profit row-shape candidates and zero proven strict Q3 three-month CFS facts. [2021 source-only run #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) records `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` and 13 row-shape candidates, not an admitted first-2022-filed comparative 2021 quarter fact. These hashes were checked against documented official-run evidence only: original ZIP bytes were NOT independently obtained and rehashed in this audit.
- Still missing first-publication exact 2022 and 2021 CFS Q3 operating profit, strict three-month period/unit/sign, first-publication availability time, complete correction lineage, issuer-to-security historical PIT and original source admission. Date-only filing evidence cannot prove intraday availability.
- KRX 2017–2022 original private archive reports 1,565 weekday-pair SHA checks but 90 calendar/source-gap sessions remain unresolved. Separate prospective 2026-09-28 source reports 27 common-stock nonpositive OHLC rows (803 common-stock rows). These are distinct horizons and must not be conflated. #420/#422/#423 offline synthetic CI and proposed exact-set comparators do not establish authenticated historical exchange calendar, actual private-volume exact-day reconciliation, or security-level tradability.
- Prior PR #418 runtime manifest blob SHA mismatch remains unapproved; no runtime source/hash promotion.

## Railway production (read-only)
- Direct environment status: `indexalert-pit-rebuild` 1 running / 0 crashed replica. Latest returned deploy log `2026-10-29T14:46:21.992Z` = **2026-10-29 23:46:21 KST**, `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `ordering=DISABLED`, independent source/chronology/model admissions false, real orders/funds/permissions false. No newer deploy logs returned from queried range; observation gap, not independently proven outage.
- `indexalert-kiwoom-real-readonly` latest deployment SUCCESS but environment replica status 0 running / 1 crashed. Its 2026-10-29T06:22:02Z runtime record reports `STAGE=TOKEN`, `DETAIL_CODE=8050`, `TOKEN_OK=false`, `WS_CONNECTED=false`, `TYPE00_EVENT_COUNT=0`, `ORDERING=DISABLED`; a deployment success is not authenticated broker connectivity.
- `indexalert-krx-historical-worker` returned no recent deploy logs in checked period; no protected `/data` access, rerun, source mutation, or deployment attempted.

## Independent economics decision
- Genuine executable historical stock/day availability, orderbook liquidity, fill model, slippage, brokerage commissions, market charges and realized taxes are not independently approved. No authorized frozen M20 return series; therefore after-tax NetEV, PF, CAGR, MDD, ES95 and ES99 are **NOT EVALUABLE**, not zero and not successful.
- **M20 PERFORMANCE NO-GO** until original source SHA/PIT/tradability/cost-tax gates are independently attested. Preserve Frozen, sealed Holdout, Champion, Top3, WF/preregistration and `ORDERING=false`. No trading, funds, rights, deployment, merge, Champion promotion or test replay.
