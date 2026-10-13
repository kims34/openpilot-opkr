# IndexAlert isolated foreign/institutional flow source-verification checkpoint

**Date:** 2026-10-13 KST
**Base (read-only snapshot):** `index-alert-research-v1` @ `3b8b7830612a6284d7c7a60628cb527cb741627a`
**Isolated working branch:** `indexalert-investor-flow-validation-v1`
**Decision:** `SOURCE_NOT_ADMITTED / NO_PROFITABILITY_EXPERIMENT`

## Duplicate-research audit

- `INDEXALERT_MULTI_FACTOR_VALIDATION_2026_10_09.md` has already inventoried the competing factor families. Existing `log_adv20` and `adv20_rank` are liquidity measures; they are not evidence that a *surprise in volume/turnover* adds alpha.
- Existing KRX investor-flow `MDCSTAT02303` probe, evidence `INDEXALERT_KRX_INVESTOR_FLOW_TINY_PROBE_EVIDENCE.json`, covers only ticker 005930 on 2026-09-21..23 (three observed rows, metadata only). It does **not** admit bulk history, publication-time PIT or performance testing.
- `research_v1_krx_investor_flow_{lineage,coverage}.py` already enforce strict KRX data-family PIT and coverage checks. They must not be mistaken for evidence that **Kiwoom** has the same schema, timestamp or legal rights.
- `research_v1_kiwoom_investor_flow_probe.py` already exists for a bounded `ka10059` metadata-only read. Do not duplicate it or turn on authenticated access just because earlier KRX permissions exist.
- `INDEXALERT_MEDIUM_SWING_M20_PREREG.*` remains wholly untouched; H5 Frozen and Champion remain wholly untouched.

## Official route and schema inventory (documentation, **not** observed authenticated traffic)

Kiwoom's **official** REST client sample `Kiwoom-Securities/Kiwoom-REST-API`, file
`examples/국내주식/종목정보/get_domestic_stock_investor_by_institution.py`
(reviewed against public head `953e5dbff123f437ab4d11a78a95191a685eb51f`),
identifies `ka10059`: `POST /api/dostk/stkinfo`.

- Request: `dt` (YYYYMMDD), exchange-coded `stk_cd` (e.g. KRX, NXT, SOR variants), `amt_qty_tp` (1 money / 2 quantity), `trde_tp` (0 net / 1 buy / 2 sell), `unit_tp` (1 or 1000; precise effective monetary scaling remains to be empirically reconciled).
- Response list: `stk_invsr_orgn` with `dt`, `acc_trde_qty`, `acc_trde_prica`, `frgnr_invsr`, `orgn`, and detailed institutional categories (e.g. `fnnc_invt`, `insrnc`, `invtrt`, `penfnd_etc`). **Never sum `orgn` with its constituent categories.**
- Continuation: `cont-yn` and `next-key`. The official sample caps itself at 10 pages, which does not establish server-side retention, historical depth, full universe or PIT vintages.
- `ka10008` supplies foreign ownership/holdings and should **not** be treated as equivalent to historical foreign net purchase *value*. `ka10066` is after-close investor flow but has a market/exchange distinction and is not a substitute for historical per-ticker PIT.
- Official documentation: https://openapi.kiwoom.com/m/guide/apiguide?dummyVal=0 ; https://github.com/Kiwoom-Securities/Kiwoom-REST-API .
- KRX official public OpenAPI lists per-security daily stock market trading information but no verified `ka10059`-equivalent **per-security investor flow** endpoint in its current public service list: https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd . This is not a claim that licensed products cannot provide it.

## Evidence and authority boundary

| Requirement | What is established | Gate |
|---|---|---|
| Broker endpoint | Official client sample identifies `ka10059` request/response names | PARTIAL |
| Broker authenticated response | No authenticated Kiwoom response was obtained in **this task** | BLOCKED |
| Number units and market segmentation | Documented parameter names only; not cross-checked against raw dated issuer-level source | BLOCKED |
| 2015-2026 universe and history | No attested full-universe Kiwoom history, halted/delisted identity or zero-flow completeness | BLOCKED |
| Historical vintages | No proof that currently queried history equals the values actually known on each historical decision date | BLOCKED |
| Date-D availability | KRX official **final investor figures after 20:00 KST** are not a generic timestamp attestation for Kiwoom's historical data; Kiwoom exact timestamps still unverified | BLOCKED |
| Full PIT lineage | No verified historical `event_time/published_at/available_at/ingested_at` for broker observations | BLOCKED |
| Source rights | Broker-data storage, re-use and bulk history rights not independently verified for this specific route | BLOCKED |
| Trade-ready outcome | No new backtest, holdout use, Alpha or live trade authorized | BLOCKED |

## Implemented in this isolated branch

- `research_v1_kiwoom_flow_source_gate.py` checks the **non-secret** output metadata of the existing bounded `ka10059` probe, including read-only authority, exact query, response SHA256 format, paging, duplicate/overlap dates and missing numeric rows. It fails closed.
- `test_research_v1_kiwoom_flow_source_gate.py` uses **synthetic metadata only** to show neither a successful read nor hand-added `published_at`/success booleans can authorize PIT or feature-performance testing. No market data is fabricated or marketed as real.
- `.github/workflows/indexalert-investor-flow-source-boundary.yml` provides a five-minute offline job. No credentials, APIs, Railway services, orders or capital access are needed.

## Research decision and conditional future design (not registered yet)

The previously proposed isolated comparisons `V` (turnover surprise), `F` (5-session foreign net buy / turnover), `I` (5-session institution aggregate net buy / turnover) and baseline-addition variants are **candidate questions**, not an approved experiment or a newly registered strategy. Until the complete official source, numeric monetary scaling, full-universe historical coverage, revision/PIT availability, as-of trading status, cost and intended-use evidence are admitted, do **not** freeze a profitability experiment, generate any return series, or inspect a consumed sealed holdout.

After source admission, preregister a *single*, non-retuned independent evaluation including baseline-on-matched-scope vs complete baseline, next-executable-entry, frozen WF504/126/126, purge/embargo, tax/fees/slippage/capacity, net EV, CAGR, PF, MDD, ES95/ES99, clustering, missingness, concentration, 2x costs and strongest-date sensitivity; reject failure rather than repeating feature/horizon/threshold sweeps.

**Unchanged authorisations:** `ORDERING=false`, actual orders/transfer/account permissions forbidden, `Champion` frozen, `M20` frozen, consumed Holdout not reopened.

**User action at this checkpoint:** none. Any future access/configuration blocker must be demonstrated by a real limited test before requesting manual intervention.
