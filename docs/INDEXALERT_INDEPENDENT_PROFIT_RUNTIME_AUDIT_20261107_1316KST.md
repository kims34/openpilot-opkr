# IndexAlert independent audit — 2026-11-07 13:16 KST

Read-only evidence audit. No market backtest, deployment, merge, ordering, promotion or credential action.

## Confirmed heads
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub fetch_commit by ref)
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- PR #414 integration document fetched at prior PR HEAD `18c5418d9684d1717df58261ea27f28e514385b2`, blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; **current PR HEAD/state not independently verified this run**.

## Actions checked by job (existing evidence only)
- OpenDART #38419439742: 2/2 SUCCESS, original/correction candidate row comparison is **not** original filing meaning/available-at approval.
- Independent runner #38419649711: 1/1 SUCCESS, synthetic offline comparison only; previously reported regression-phase 1.1315x does not establish end-to-end speedup.
- Optimization #38498552499: 6/6 SUCCESS, offline synthetic fail-closed tests only.
- Chronology anchor #41515392296: auto-anchor FAILURE at 'Fetch today's public hash-only prospective payload'; validation SKIPPED. Historical HTTP 404 explanation remains unconfirmed as root cause.

## Railway production
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild, KRX historical worker, runtime and real-readonly latest deployments report SUCCESS; that is **not** proof of runtime health.
- environment_status: `indexalert-kiwoom-real-readonly` replica running=0, crashed=1, total=1 despite display state online: **FAIL** runtime availability; no restart performed.
- `db-query-readonly`: one critical notification, state offline, detail NOT VERIFIED.
- `indexalert-pit-rebuild` running 1/1; `indexalert-runtime` running 1/1; KRX historical worker running 0/1 (cron/idle not proof of failure).
- describe_environment staged=null, while environment_status reports pending empty-change patch `e113dacb-6705-4416-9997-dc694539d382`; inconsistent views, application NOT VERIFIED. No acceptance.
- PIT, KRX, real-readonly deploy logs from 2026-11-07 11:00 KST: no entries returned; absence is not remediation.
- Runtime 2026-11-07 13:15 KST: Investing.com USDKRW HTTPError -> Yahoo fallback; market closed/extended session unavailable. Does not establish economic PIT.

## Gates
- KRX 1565/1565 weekday pair storage integrity: historical PASS only. Official trading calendar, 90-day classification, 12003 zero-activity exclusions, 27 suspect OHLC remediation, corporate actions, historical instrument mapping and executable fills: NOT VERIFIED / fail closed.
- OpenDART 2021/2022 original 3-month consolidated operating-profit period/correction lineage, original filing public available-at/PIT: NOT VERIFIED / fail closed.
- Independent after-tax, after-cost NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness: NOT VERIFIED; no new profitability run.
- Frozen H5; M20 horizon20/purge20, WF504/126/126; consumed holdout never reused. M20 NO-GO; ORDERING=false; NO_TRADE.

## Next safe actions
Read-only compare deployed runtime SHA/routes with chronology anchor payload contract; examine real-readonly crashed replica logs and DB critical alert without restarting; obtain original filing/public timestamps and KRX official state lineage with independent SHA evidence. Optimization remains isolated synthetic-only; caching requires all independent approval evidence SHA-256 matches, otherwise fail closed. No workflows or shared Work code touched.
