# IndexAlert independent profitability gate — 2026-10-30 08:43 KST

Read-only evidence check. This document does not approve any data, strategy, trading, or deployment. M20 execution is forbidden until independently attested source/PIT gates.

## GitHub pinned state
- Research branch `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development branch `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist branch `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #414 (head before this audit `1405b1cf5d435d01cc4af617d7bbf8336fda3495`), #412, #413, #416, #418, #420, #422, #423: all checked Draft, open, unmerged.
- Actions list count 4,621. Latest watchdog run [#40960712047](https://github.com/kims34/openpilot-opkr/actions/runs/40960712047) completed SUCCESS at 2026-10-29 21:47 UTC. Its actual job log states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; 31 governance tests in one logged suite passed. Success is a safety test result, not M20 source admission.
- Chronology anchor [#40914179246](https://github.com/kims34/openpilot-opkr/actions/runs/40914179246) failed HTTP 404; its validation job skipped. No independent historical publication-time proof.

## Source SHA and PIT
- [OpenDART 2022 first original official job](https://github.com/kims34/openpilot-opkr/actions/runs/38381866190) log recorded original ZIP SHA256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 15 operating-label candidate tables, no strict bound 2021/2022 three-month CFS profit fact. The raw original ZIP bytes were NOT independently obtained and rehashed in this audit.
- [OpenDART 2021 first original official job](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) log asserted ZIP SHA256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; 13 operating-label candidates, zero exact same-table Q3/three-month binding. This is a separate first-2021 document, NOT the first-2022 filing's 2021 comparator accounting fact. Raw bytes not independently rehashed here.
- Still missing independently attested first-vintage original CFS 2022 and 2021 exact three-month operating-profit amounts, accounting period/unit/sign, complete correction lineage, first availability timestamps, issuer-to-security historical mapping, historical tradability, and transaction-level cost/tax model.
- KRX specialist's historical 1,565 weekday-pair integrity evidence does NOT resolve 90 uncertain sessions or 27 nonpositive common-stock OHLC records. Draft #422/#423 private exact-day candidate comparators have not been executed on the original private Railway volume. Neither synthetic CI nor matching counts confer PIT/tradability authority.
- Previous runtime-manifest SHA mismatch remains an unapproved gate; this run did not independently recompute the specific base/head manifest blob comparison.

## Railway production (read-only)
- `indexalert-pit-rebuild`: one running replica; latest returned runtime record `2026-10-29T14:46:21.992Z` (`2026-10-29 23:46:21 KST`), `status=FAIL_CLOSED`, `ordering=DISABLED`, `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive common-stock OHLC rows among 803, source/chronology/model approvals false, orders/funds/permissions false. No later runtime log returned in the queried window; this is an observation gap, not proof of an outage.
- `indexalert-kiwoom-real-readonly`: deployment SUCCESS, but environment health reports 0 running and 1 crashed replica; only startup and empty log records returned for latest date window. Do not infer broker connectivity or permission from deployment SUCCESS.
- `indexalert-krx-historical-worker`: no recent deploy logs returned. No private-volume access or source execution attempted.
- Railway service configuration, environment, and deployment health were read only. No staging, redeploy, variable, access, fund, or order changes.

## Independent economics admission
- NetEV (net expected value), PF, CAGR, MDD, ES95, ES99: **NOT EVALUABLE** until original SHA/PIT/source and historical tradability, fill/slippage/fees/taxes are independently accepted and the frozen M20 execution gate is authorized.
- **NO-GO**: no M20 profitability execution, no holdout unseal, no Champion promotion, no Top3 change. Preserve Frozen/Holdout/Champion/Top3 and `ORDERING=false`.
- Other specialist source/runtime/ETF tasks are not modified. This audit adds documentation only, without running a backtest or touching production.
