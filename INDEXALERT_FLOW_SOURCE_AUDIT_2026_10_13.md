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

## Executed verification checkpoint — 2026-10-13 KST

- [Isolated offline CI #38382575489](https://github.com/kims34/openpilot-opkr/actions/runs/38382575489): **SUCCESS**, **15/15 synthetic fail-closed tests passed**. This is not a live-data test.
- [Bounded Kiwoom metadata workflow #38382700355](https://github.com/kims34/openpilot-opkr/actions/runs/38382700355): workflow **SUCCESS**, real data probe status **`AUTH_NOT_CONFIGURED`**. This means the **GitHub Actions context for this branch** did not receive `KIWOOM_APP_KEY` and `KIWOOM_APP_SECRET`. No authenticated ka10059 response and **zero** validated investor-flow market-data rows resulted. Workflow success is not data-source success.
- Read-only Railway configuration inspection found variable **names** `KIWOOM_APP_KEY`, `KIWOOM_APP_SECRET`, `KIWOOM_BASE_URL`, `KIWOOM_ENV`, and `KIWOOM_ORDERING_ENABLED` on existing `indexalert-kiwoom-real-readonly` and `indexalert-kiwoom-real-readonly-run` services. Railway OAuth redacts values. Presence of names does not attest key validity or broker availability; no credential was exported, copied or changed, and neither service was redeployed.
- No source-vintage claim, acquisition contract admission, experimental preregistration, profitability claim, holdout read, live order, secret modification, or Railway mutation occurred.

**Next authorized operation:** where an isolated existing-key **read-only** runner can be invoked without mutating concurrent services, execute the existing bounded ka10059 probe with `ORDERING=false`, save only non-secret response metadata, then separately validate historical publication/vintage/coverage/rights. Do not force moving Railway secrets to GitHub or ask the user to paste keys into chat. Until that operation is feasible, `SOURCE_NOT_ADMITTED` is the definitive research state.

## 2026-10-13 23:27 KST — continuation / independent negative tests

The hourly continuation state and GitHub were rechecked. The isolated branch and draft PR #416 remained unmerged; the primary research branch remained at `3b8b7830612a6284d7c7a60628cb527cb741627a`, so no conflicting research-base edit was required. The research continuation automation was enabled and had run on 2026-10-13 22:25 KST (automation scheduling is separate from a successful GitHub data collection).

**Concrete new code changes in the isolated branch only:**

1. Existing `research_v1_kiwoom_investor_flow_probe.py` now requires both cumulative trading value `acc_trde_prica` **and cumulative trading quantity `acc_trde_qty`**, rather than silently accepting a source row that cannot support the requested activity analysis. Signed negative foreign/institution net buying remains permissible; negative cumulative trading value or trading volume fails closed. Zero activity is not auto-filled or rejected as missing. Within-page reverse-date anomalies are recorded and block acceptance of metadata.
2. New `test_research_v1_kiwoom_investor_flow_probe.py` tests the existing *original* probe using an injected in-memory transport, without any external networking or broker credentials. Tests cover an absent key, unsafe ORDERING, wrong host, token rejected, missing quantity, signed flow, inactive row, future day, reversed dates, missing next-key, duplicate cross-page days, broker data error and no credential/token leakage into serialized evidence.
3. The isolated source metadata gate now verifies new zero-anomaly counters and corresponding negative regressions. The CI workflow was extended to execute both test modules.

**Exact executed CI evidence:** [run #38413548428](https://github.com/kims34/openpilot-opkr/actions/runs/38413548428), commit `89990927a412cbc69df08b4602d615a34f30a64d`, conclusion **SUCCESS**, `Ran 31 tests` / `OK` (31 synthetic/offline tests, *not* 31 historical trials).

**Admission remains unchanged:** no real authenticated `ka10059` data acquisition, no complete historical security-level/venue-specific official panel, no release-time/vintage record-level PIT, no new strategy preregistration or financial backtest. The previous GitHub bounded source check was `AUTH_NOT_CONFIGURED` in that Actions environment, while separately held Railway credentials were not migrated or modified. `ORDERING=false`; no live account actions; existing H5/M20, Champion and Holdout unchanged.

**Next work item:** obtain authorized primary-source original-response *metadata* on the previously configured read-only environment without copying credentials, then verify broker vs KRX venue/unit/individual-investor category parity and the acquisition licence. Keep sampled-route reachability separate from retrospective source-admission and complete 2015–2026 PIT universe coverage.

## 2026-10-13 23:33 KST — independent broker-source structural PIT guard

An additional `research_v1_kiwoom_flow_pit_structural.py` module and `test_research_v1_kiwoom_flow_pit_structural.py` module were added to the **isolated branch only**, with no network, orders or real numerical market data.

- Require explicit `published_at`, `available_at`, `ingested_at` and `decision_at` with timezone offsets; reject naive clocks, negative chronology, cross-day look-ahead and duplicated `(ISIN, venue, event_date)`.
- Distinguish KRX, NXT and SOR instead of implicitly aggregating inconsistent venue totals; require a response digest only as *structural metadata*, never as proof of an authentic timestamped historical original.
- **Do not copy the KRX final-investor 20:00 KST publication rule to Kiwoom**. Even a structurally legal Kiwoom timestamp before 20:00 must remain `broker_publication_time_contract_verified=false` until independently validated. No assertion from the input can enable `source_admitted`, `performance_testing_authorized`, Holdout or live trading.
- Preserve required original historical issuer mapping/identity, complete source vintages, signed original publication proof, valid licences and actual whole-market PIT panel as **missing evidence**; never infer them from an API response.

**Executed CI:** [GitHub Actions #38414194380](https://github.com/kims34/openpilot-opkr/actions/runs/38414194380), commit `a17de7dddc456bbb0724d1a9b6978c5a57c84cbb`: `SUCCESS`, `Ran 46 tests`, `OK`. These were entirely offline negative/synthetic tests, NOT profitability experiments or actual-data admissions. Follow-up malformed-venue guard has been added with regression coverage and is subject to the latest branch CI.

**Research state unchanged**: `NEW_OFFICIAL_SOURCE_EVIDENCE_REQUIRED`. No authentic broker event publication vintages or full historical coverage exist in this isolated evidence. Do not preregister/execute flow-alpha performance study or promote a candidate.
