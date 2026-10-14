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

## 2026-10-13 — pagination-vs-history ambiguity removed (checkpoint)

**Issue detected from actual code review:** `research_v1_kiwoom_investor_flow_probe.py` previously labelled a completed *response pagination* sequence as `history_exhausted=true`. This could be mistaken for complete retrospective history even though a broker can stop at a server-side undocumented retention boundary. The earlier metadata gate also used a self-reported successful probe status to set `bounded_route_reachability=true`, which a caller could forge.

**Fail-closed fixes on isolated branch only:**

- `pagination_exhausted` now reflects only whether the received `cont-yn` pages terminated; `history_exhausted=false` and `historical_retention_verified=false` remain deliberately false without independently attested first/last eligible dates, official whole-universe coverage and original vintages.
- `research_v1_kiwoom_flow_source_gate.py` rejects `history_exhausted=true` or `historical_retention_verified=true` and requires a terminated page sequence. It distinguishes a *self-reported shape-compatible response* from independently verified authentication/reachability: `reported_bounded_response_shape_compatible` may be true for synthetic metadata, but `bounded_route_reachability=false` and `authenticated_route_evidence_verified=false` remain fixed.
- Recursive key inspection rejects accidentally embedded sensitive credential/token keys within page metadata. This does not claim to detect every secret embedded in an arbitrary value; source output stays allowlisted by construction.
- The isolated regression tests now assert these guards, not the old ambiguity. No experimental strategy, price/volume rows, credentials, account operations, Railway configuration or original Frozen protocol was changed.

**Executed offline CI:** [GitHub Actions #38415716578](https://github.com/kims34/openpilot-opkr/actions/runs/38415716578) at exact commit `30f503f811a369bd2024afdc5eff13aac10f07f5`: **SUCCESS; 50 tests passed** (`Ran 50 tests`, `OK`). All inputs are mock transport and synthetic metadata, not an authenticated Kiwoom source sample. Source admission, historical PIT coverage, performance-testing authority and Holdout remain false.

**Official documentation reference pinned for review:** `Kiwoom-Securities/Kiwoom-REST-API` at commit `953e5dbff123f437ab4d11a78a95191a685eb51f`, file `examples/국내주식/종목정보/get_domestic_stock_investor_by_institution.py`, blob `ebf61f1c8e1f0cd1131598a347763d87ab917f84`. It defines `ka10059`, `POST /api/dostk/stkinfo`, `amt_qty_tp` amount/quantity, `trde_tp` net/buy/sell, `unit_tp` 1/1000, and row fields `stk_invsr_orgn`, `dt`, `acc_trde_qty`, `acc_trde_prica`, `frgnr_invsr`, `orgn`. Parameter documentation is NOT actual historical retention, publication-time equivalence or units cross-validation. Historical foreign/institution net-buy value/turnover ratios remain unadmitted.

**Next blocker:** use a separately authorised, non-mutating, already provisioned read-only environment to observe authentic `ka10059` response metadata. Railway inventory showed `indexalert-kiwoom-real-readonly-run` is configured with `print(INDEXALERT_START_COMMAND_ATTESTED_NO_NETWORK=true)` and `indexalert-kiwoom-real-readonly` uses `python -B smoke.py`. Neither currently provides a verified non-disruptive path for the bounded source query through the available connection, so no Railway redeployment, start-command change, variable export or secret migration was performed. Read-only Github Actions probe remained `AUTH_NOT_CONFIGURED`.

## 2026-10-13 continuation — independent KRX/Kiwoom parity contract

The isolated branch now includes `research_v1_kiwoom_krx_flow_parity.py` and `test_research_v1_kiwoom_krx_flow_parity.py`. These are **offline schema/semantics checks only** that can be used *after* separately approved, normalized real records exist. Nothing here acquires or persists numeric external data.

### Why this separate verifier is needed

- Official Kiwoom `ka10059` documents `frgnr_invsr`, `orgn` and cumulative trading fields, but their exact KRW normalization, data-finality and historical retention/vintage are **not established** by sample code.
- KRX Data Marketplace presents investor-trading data by individual securities; the prior 3-day `MDCSTAT02303` sample established limited route reachability but neither full history nor disclosure-time PIT.
- Official KRX data distribution guidance distinguishes simple viewing from redistribution or revenue-generating program development which may require a separate agreement: https://openapi.krx.co.kr/contents/OPP/DATA/OPPDATA003.jsp . This guidance does NOT itself establish the commercial/user-specific rights for any requested data route; source-specific intended-use rights remain independently unverified.
- KRX / NXT / SOR and broker consolidated results cannot be automatically compared or summed. `orgn` is the aggregate institutional measure and must not be summed with its own constituent categories or unrelated `etc_corp`.

### Implemented parity guard

- Requires **same ISIN, symbol, trade day, KRX-only venue/scope and investor metric**. Compares separate `FOREIGN_NET_BUY_VALUE` and `INSTITUTION_NET_BUY_VALUE` records, never arbitrary blended categories.
- Expects each side to have been independently normalized to *exact signed integer KRW* with a pinned normalization contract and response digest, otherwise rejects; **does not assert that a caller-supplied contract hash proves correct units**.
- Counts all unmatched dates/issuer/metrics in each source and all numeric disagreements. It does not drop nonmatching rows, assume 0 for missing, silently select only matching transactions or tune a comparison tolerance to the observed result.
- Even exact numeric agreement sets `source_originals_authenticated=false`, `historical_units_independently_attested=false`, `original_as_published_pit_verified=false`, `historical_issuer_universe_complete=false`, `source_admitted=false`, `performance_testing_authorized=false`, `holdout_authorized=false`, `ordering_enabled=false`. No strategy experiment was preregistered.

### Actual tests and resolution

The first all-module CI run [#38417196181](https://github.com/kims34/openpilot-opkr/actions/runs/38417196181) returned **2 test fixture errors** due to mistaken positional synthetic helper arguments (sample amount was passed as source label); the source guard did not silently pass. Corrected the test fixtures, then reran the full suite:

**[GitHub Actions #38417306875](https://github.com/kims34/openpilot-opkr/actions/runs/38417306875)**, commit `94a7f6aee7d46c2e008b73d4b39cdf7008bf5663`, **SUCCESS, `Ran 70 tests`, `OK`**. These are 70 offline **unit/safety/negative tests**, not 70 live responses or profitability backtests.

### Missing evidence to actually move toward profitability

1. An approved, non-disruptive authenticated read-only `ka10059` route with redacted source metadata in the **already approved** environment (do not copy credentials or change another team's REAL service).
2. Independently verified original historical value, source response, as-published release instant, revision and exact Kiwoom-vs-KRX unit+venue+definition mapping.
3. An attested all-stock PIT historical universe including halted/delisted/renamed securities, plus licence/permitted archival and economic backtest use.
4. Only then register independent single-shot comparison of volume/foreign/institutional factors using Frozen protocols, net post-cost/post-tax economics and untouched independent Holdout procedure.

All missing items remain unverified. No direct orders, fund movements, account/secret modifications, service redeploys or H5/M20/Champion/Holdout changes were performed.

## Follow-up — reject falsely matched partial foreign/institution flow panels

The prior `research_v1_kiwoom_krx_flow_parity.py` code could emit
`declared_scope_exact_numeric_match=true` when **only foreign flow** was
present in both normalized source candidates and the institution leg was
missing from both. It could also report numeric parity across two
**different declared normalization contract hashes**. Neither was safe as
a readiness signal for the intended foreign+institution comparative study.

**Code changes (isolated branch only):**
- Require both `FOREIGN_NET_BUY_VALUE` and `INSTITUTION_NET_BUY_VALUE`
  for every declared security/day **in each source** before a complete
  declared-scope match can be true. `declared_incomplete_measure_pair_count`
  counts incomplete issuer/day pairs, rather than silently using the
  intersection or imputing zeros.
- Require the two sources to declare the **same pinned KRW-normalization
  contract hash** for `declared_scope_exact_numeric_match`. A same-hash
  *claim* by itself is not proof of correct unit conversion; the
  `historical_units_independently_attested` flag remains false.
- Enforce canonical signed integer KRW text. Fractional, scientific
  notation, thousands separators and whitespace fail closed; negative
  institutional/foreign net-buy values are legitimate.
- Preserve zero source/holdout/trading authority: matched mock values
  cannot establish timestamp vintage, rights, issuer mapping or
  post-tax/post-cost profitability.

**Real executed CI:** initial code/test update exposed a pre-existing
test expectation mismatch for an intentionally malformed amount
([#38419234583](https://github.com/kims34/openpilot-opkr/actions/runs/38419234583),
`77` run, `1` assertion failure). This was corrected without
changing the new guard. [GitHub Actions
#38419356861](https://github.com/kims34/openpilot-opkr/actions/runs/38419356861),
commit `18dd88182310facc57040d8611dfa6a4732cb334`, then ran
**77/77** offline unit and synthetic negative tests: `SUCCESS`,
`Ran 77 tests`, `OK`. This is **zero** actual market-data
performance trials.

**Handoff state:** `SOURCE_NOT_ADMITTED` / `NO_PERFORMANCE_RUN`.
Full archived and authorized historical KRX/Kiwoom original responses,
point-in-time publication/revision lineage, delisted/paused security
universe, same-unit venue definitions and legal-use permissions remain
missing. Prior GitHub Actions bounded probe was
`AUTH_NOT_CONFIGURED`; no credential migration or Railway mutation
was performed. Draft PR #416 remains unmerged. Do not change
Frozen/H5/M20, Champion, Holdout or `ORDERING=false`.

## 2026-10-14 KST — separate retrospective versus prospective data-ingestion semantics

Review of `research_v1_kiwoom_flow_pit_structural.py` found an ambiguity: the module checked `available_at <= decision_at` but did not distinguish historical **as-published replay** from an actual prospective data capture. Those two cases require different conditions for the local ingestion clock; applying `ingested_at <= decision_at` indiscriminately would falsely exclude valid historical archive downloads done long after an actual historical decision, while omitting that rule for live capture would allow a network response arriving after the decision into an allegedly contemporaneous signal.

In the **isolated source-audit branch only**, the candidate structural validator now requires an explicit `capture_mode` for every row:

- `HISTORICAL_RECONSTRUCTION`: permits later archival local ingestion *structurally*, but **does not trust self-declared broker `published_at` / `available_at` timestamps**; original archived release/vintage, rights, revision records and independent contemporaneous availability remain unverified, so `source_admitted=false` and all performance/holdout permissions remain false.
- `PROSPECTIVE_CAPTURE`: additionally requires `ingested_at <= decision_at`; the source can claim an early publication but cannot be used to generate a signal before its actual local ingestion. The existing chronological constraints `event_day_start <= published_at <= available_at <= ingested_at` and `available_at <= decision_at` remain.
- Unknown, missing or nonstring capture modes and mixed historical/prospective modes in one batch fail closed; no implicit mode conversion is performed.

**Actually executed test result**: [GitHub Actions #38464634914](https://github.com/kims34/openpilot-opkr/actions/runs/38464634914), commit `c5e0cc678589647606762b5c5ff3157cce90af41`, **SUCCESS: `Ran 85 tests`, `OK`**. Eight new offline synthetic tests address late retrospective archival ingestion, prospective late arrival, valid prospective timing, unknown/missing/mixed modes and nonstring capture mode. These tests are **not** genuine KRX/Kiwoom historical-data PIT proof or trading-performance tests.

**Additional non-mutating Railway observation (2026-10-14 KST):** inspected up to 120 most recent runtime-log entries for each of two existing REAL read-only services (`indexalert-kiwoom-real-readonly-run`, `indexalert-kiwoom-real-readonly`); log result included 64 and 42 entries respectively, service status `SUCCESS`. No rows in those inspected logs carried `ka10059`, `INVESTOR_FLOW_PROBE`, `SOURCE_REACHABLE`, or `AUTH_NOT_CONFIGURED` indicators. Absence of those terms within that bounded log query **cannot prove no earlier broker requests happened**. No API requests, Railway redeploys, service configuration changes, auth-variable reads or key movement were performed. Authenticated broker source evidence remains **not established** in this task.

**Coordinator handoff:** continue at `SOURCE_NOT_ADMITTED` / `NEW_OFFICIAL_SOURCE_EVIDENCE_REQUIRED`. Existing H5/M20, Champion, Frozen conditions, sealed Holdout and `ORDERING=false` unchanged. PR #416 remains draft/unmerged.

## 2026-10-14 05:52 KST — bounded Kiwoom source parser correction and genuine-access feasibility

**Actual non-mutating access inventory:**

- GitHub Actions `indexalert-investor-flow-bounded-kiwoom-readonly.yml` accepts optional GitHub repository secrets `KIWOOM_APP_KEY`, `KIWOOM_APP_SECRET`; the last actually observed bounded run #38382700355 returned `AUTH_NOT_CONFIGURED`, i.e. it did NOT obtain an authenticated `ka10059` response. The existing isolated source-gate CI is deliberately synthetic and cannot fix absent broker credentials.
- Existing Railway services `indexalert-kiwoom-real-readonly` and `indexalert-kiwoom-real-readonly-run` have credential **variable names** already configured in production, but currently run a separate `smoke.py` job and a no-network attestation, respectively. The available connector does not provide a command-execution path inside their existing environment. No values were read, referenced into a new service, re-scoped, copied or exported. No deployment, configuration, account, permissions, ordering or key modifications were performed.
- Without an independently authorised *isolated execution environment using the existing secret scope*, no genuine `ka10059` sample is yet proven. **Do not substitute offline test success for source availability** and do not open performance validation or sealed Holdout.

**Code defects found and corrected in this continuation:**

1. `research_v1_kiwoom_investor_flow_probe.py` used an over-escaped decimal regex in its negative cumulative-activity guard. The field-shape validator accepted `-0.5`, but the negative counter could miss it. The source now uses a single shared canonical numeric regex and exact `Decimal` checks instead of floating-point conversion, rejecting negative fractional trading value/quantity and large-magnitude negative values without overflow. Signed foreign/institution net buying remains allowed; nonnegative fractional input is only schema metadata pending independent units validation.
2. Duplicate source trading-day observations are now marked `PAGINATION_VALIDATION_REJECTED` directly, not merely flagged by a downstream gate. Across-page reversed chronology is likewise rejected even if each individual page happens to be internally ordered.
3. An unfinished broker continuation at the fixed maximum of **three pages** is explicitly `PAGINATION_LIMIT_REACHED`; it cannot be presented as `SOURCE_REACHABLE_METADATA_ONLY` or full-history success. Even fully exhausted pagination never proves original 2015–2026 historical retention or PIT vintages.

**Executed Actions evidence**: [CI #38466211267](https://github.com/kims34/openpilot-opkr/actions/runs/38466211267), commit `c4d892a4d686b8001fad2b2590795875cf92e242`, **SUCCESS**, `Ran 91 tests in 1.215s`, `OK`. Added six specific synthetic safety regression cases (fractional/large negative activity, nonnegative fractional no-admission, explicit duplicated-day status, out-of-order pages and page cap). All 91 cases are offline and cannot attest authenticated broker source, licence, security history, original publication timestamps or actual post-cost strategy profits.

**Remaining hard gate**: `SOURCE_NOT_ADMITTED` (authenticated bounded live metadata, official licence/definitions, source vintage/PIT/complete universe unavailable). Stop at safe evidence collection; no Champion/H5/M20/Frozen/holdout changes and `ORDERING=false` remains unchanged. Draft PR #416 remains unmerged.

## 2026-10-14 KST — source-route prioritization backed by actual other-workstream evidence

**Reason for this handoff:** the blocker is *authenticated historical investor-flow primary source*, not a shortage of offline test cases. Distinguish **three different** data collections before initiating any profitability run:

1. **KRX investor-flow, actual historical sample route observed:** committed `INDEXALERT_KRX_INVESTOR_FLOW_TINY_PROBE_EVIDENCE.json` records authenticated Data Marketplace `MDCSTAT02303` call in [Actions #36976873119](https://github.com/kims34/openpilot-opkr/actions/runs/36976873119) (2026-10-02), Samsung Electronics `005930`, 2026-09-21 to 2026-09-23, **3 observed rows**, and expected KRX investor-category schema. The call did **not** preserve original numeric market rows, does **not** prove 2022 availability, full historical coverage or contemporaneous archived vintages and does **not** authorize investor-flow performance evaluation. `INDEXALERT_KRX_AUTH_EVIDENCE_INVESTOR_FLOW.json` attests KRX personal/internal research low/high frequency programmatic collection permission with nondistribution requirements for that *route/scope*, but separate historical acquisition execution contract and source proofs remain applicable.
2. **KRX KOSPI daily market data are a different dataset:** cross-read the dedicated KRX source team's `indexalert-krx-pit-source-audit-20261013` branch, HEAD `595db195b7a107ebab4e9c53eb629a5aa4de511c`, report `evidence/krx/2026-10-13-krx-market-source-pit-handoff.md` and `evidence/krx/2026-10-14-krx-exact-private-date-set-reconciliation-handoff.md`. The private KRX OpenAPI **daily price/security master** store audit recorded **3,071 weekday source checkpoints, 184 unclassified dates and 27 quarantined securities**. Those private raw records are NOT investor-category net-buy data; its completeness, official trading calendar, status mapping, original PIT and eligibility remain unresolved. Do not treat its OHLC/turnover rows as Kiwoom or KRX investor-flow evidence, substitute them for `MDCSTAT02303` records, or assert official PIT.
3. **Kiwoom `ka10059` not authenticated in current flow branch:** bounded GitHub Actions run [#38382700355](https://github.com/kims34/openpilot-opkr/actions/runs/38382700355) returned `AUTH_NOT_CONFIGURED` **in that workflow environment**. Railway REAL read-only services have key variable names present but no non-mutating command execution capability was identified in that existing scope. No original Kiwoom source row, historical broker publication contract, 2015–2026 completeness or after-cost Alpha evidence exists.

**Research route decision:** prioritize KRX `MDCSTAT02303` as the *already-bounded-authenticated* **candidate primary source** over waiting for Kiwoom REAL keys to be copied into GitHub; reserve Kiwoom for optional independent comparison once safely available. This is an execution-order recommendation, NOT source admission. Obtain a separately properly authorized 2022 original historical KRX per-issuer sample and record original SHA-bound private receipts, venue/amount/category scaling and date-valid publication vintage. Then verify expected historical universe/episode and as-of eligibility; only *after* complete source admission preregister independent Net-EV post-cost/post-tax research. No protected network flow run or new resource access was initiated by this handoff.

Machine-readable handoff: `evidence/investor_flow/2026-10-14-krx-first-source-handoff.json`. This can be consumed by the KRX data and profitability coordinator rooms without treating old cached OHLC rows as investor flow. Source gates remain `SOURCE_NOT_ADMITTED`, `performance_testing_authorized=false`, `ORDERING=false`; Frozen H5/M20/Champion/Holdout intact.

**Verification at handoff:** the already completed [isolated branch CI #38466312612](https://github.com/kims34/openpilot-opkr/actions/runs/38466312612) passed **91/91 purely offline guard tests**. This source-routing evidence records facts from other completed authenticated tiny-probe and storage audit results, *not* any new market request or new performance test.

## 2026-10-14 — 2022 KRX source-receipt structural gate (not original-vintage admission)

**Primary-source web reference checked:** [KRX investor-trading daily page](https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd?screenId=MDCSTAT022) explicitly states that final day-D investor results are available **after 20:00** KST. KRX Data Marketplace also lists a distinct *per-security investor-trading* route and [third-party pinned client mapping](https://github.com/beaten-by-the-market/krx-data-api/blob/main/README.md) identifies `MDCSTAT02303` as `investor_trading_individual_daily`. These web page/documentation observations verify an advertised 20:00 **floor**, not an exact 2022 original timestamp, immutable 2022 snapshot, official original year availability, revision lineage or historical trade universe. Today’s public page cannot be retroactively treated as original 2022-vintage documentation.

The previously recorded authenticated 3-day KRX 2026 source-feasibility probe reported 13 categories including **financial-investment, insurance, fund, private, bank, other-financial, pension, nonfinancial corporations, individuals, foreign investors and other-foreign investors**. The 2026 observed bucket list is not itself proof of the 2022 schema or a verified `기관 합계`/foreign-total definition. In particular, `외국인` and `기타외국인` are **separate fields**, and the KRX site may also display an aggregate institution/foreign view in another mode. Never infer a 2022 aggregate numerator, silently sum unapproved 2026 buckets or use exchange consolidated figures as a broker venue-subset signal.

**New isolated code:** `research_v1_krx_flow_2022_receipt_gate.py` and `test_research_v1_krx_flow_2022_receipt_gate.py`. The 2022 candidate check requires a single KOSPI issuer (explicit symbol + ISIN format), exact `MDCSTAT02303` Data Marketplace request route, `ask_bid=3` net-buy and `trade_volume_value=2` monetary mode, a strictly bounded 2022 request/observed-day window, canonical schema of the *previously observed 2026 sample*, signed raw-response/schema SHA256 placeholders, timezone-aware later retrieval and `HISTORICAL_RECONSTRUCTION` capture mode. It **does not accept original numeric source rows**, secrets, or arbitrary proof flags in its public-safe metadata. The untrusted response digest is NOT verified against private source bytes here; format/syntax does not authenticate a KRX response. It does not compute institution or foreign aggregates and sets **all** source, 2022 authenticated vintage/PIT, units, issuer episode, broad coverage, experiment, Holdout and trading authorities to false.

**Executed source-protection CI:** [Actions #38485726290](https://github.com/kims34/openpilot-opkr/actions/runs/38485726290), source commit `44b211c7ca42c73201fea2dc7f0615358e08203c`: **SUCCESS, `Ran 113 tests`, `OK`**. This is **91 prior + 22 new** synthetic/network-free validation and negative cases. It is neither 2022 KRX request success nor any Alpha/profitability result.

**Next independent protected-source proof:** within the existing *KRX owner's* authorized and private Data Marketplace scope, obtain one 2022 one-issuer response whose private, immutable provider bytes are SHA256-bound to the receipt, plus captured retrieval clock, request parameters, original date/session and 2022 category/unit definition. A currently retrieved 2022 value alone cannot establish the as-published 2022 original; independently archived contemporaneous vintage or a verified and sufficiently precise original KRX historical revision/publication policy would be needed for PIT admission. Check historical issuer/delisting/halts and entire source coverage before any statistical performance experiment. No new authenticated request or consent-gated Railway/GitHub runtime execution occurred in this continuation.

**Authority:** only isolated branch source-check code/tests and evidence changed. `INDEXALERT_MASTER_SPEC`, Frozen H5/M20, Champion, sealed Holdout, `ORDERING=false`, genuine orders, production deployments and secrets are unchanged. Draft PR #416 remains unmerged.

## 2026-10-14 11:02 KST — critical existing 2015–2026 **KRX investor flow private checkpoint** discovery

Cross-checked **the existing KRX historical acquisition source, not just the public tiny probe**:

- Frozen `INDEXALERT_KRX_PER_SECURITY_HISTORY_PREPARATION_EVIDENCE.json` breaks the **14,296 exact private requests** down into **9,485 `investor_trading_individual_daily`** (KRX `MDCSTAT02303`, yearly issuer windows) and **4,811 `trading_halt`** tasks. Preparation's manifest-set SHA256 is `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`; manifest metadata SHA256 `0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116`. The original frozen per-security job builds *both* kinds in `research_v1_krx_historical_batch_orchestrator.py`.
- Frozen `INDEXALERT_KRX_PER_SECURITY_HISTORY_INTERRUPTION_EVIDENCE.json` records **11,750 completed, 2,546 remaining, 0 failed** private checkpoint **tasks** as of 2026-10-03. It does **NOT** disclose completion counts per source kind or by 2022 issuer/year. Since there are only 4,811 halt tasks, elementary bounds imply **at least 6,939 and at most 9,485 completed investor-flow tasks**, **assuming** those frozen manifest and status records accurately describe the same underlying task set. This is a bound on completed archived requests/receipts, **not raw daily rows, PIT-usable observations, signal history or independently re-verified private originals**.
- `research_v1_krx_historical_worker_core.py` on the research snapshot writes full protected raw objects by SHA256 and source receipts; `research_v1_krx_historical_batch_state.py` stores `completed` entries keyed by preregistered task SHA (row counts and original raw/receipt hashes). This private archive likely includes historical investor-flow responses, but *whether an actual 2022 issuer-window checkpoint is present* and whether its raw source bytes still re-hash correctly is **not yet verified**. Do not waste requests by blindly re-fetching until exact private inventory is checked.
- The research worktree uses pinned KRX client `beaten-by-the-market/krx-data-api` commit `e6ebac9b71482db127348d8a08ebc6743aa3b50e`. Its original pinned `krx_data_api/endpoints.py` `investor_trading_individual_daily` defaults are `bld=MDCSTAT02303`, `inqTpCd=2`, `askBid=3` (**net buy**), `trdVolVal=2` (**value**), `money=1` (scale not independently verified), CSV. The original `research_v1_krx_historical_fetchers.resolve_pinned_endpoint_request` merges these defaults with task request parameters. Thus **previously acquired KRX flow tasks target net-buy trading-value mode** as defined by the pinned client; independent final KRW numeric scaling/source schema still needs private original verification. The third-party catalog is the **pinned client contract**, not contemporaneous official 2022 publication proof.
- The currently deployed Railway `indexalert-krx-historical-worker` is bound to source `1e6367d2863a86c3470da13d81a955d277eba485`, start `python -B research_v1_krx_openapi_missing_2017_2022_integrity_audit.py --audit`; the bounded runtime log inspection found no literal `MDCSTAT02303`/investor source report in its recent entries. Its ongoing work is primarily KOSPI daily trading OHLC integrity; **that does not erase the separately captured historical per-security task archive on the protected volume**. There was NO runtime mutation, redeployment, key exposure or broker/order operation here.
- Prior per-security acquisition network authority is explicitly **consumed** (`INDEXALERT_KRX_PER_SECURITY_HISTORY_CONSENT_CONTRACT.json`); **2,546-task continuation cannot be implicitly resumed** and requires fresh exact per-stage/bulk/resume authority. A *network-free audit of existing private checkpoints* is the first priority, not a new authenticated download.

**New code ready for the KRX data owner to run ONLY in its already authorised private volume:**
`research_v1_krx_flow_existing_private_checkpoint_inventory.py` provides
`summarise_frozen_2026_10_03_checkpoint_set(manifest, phase_state)`. It:
1. Receives existing private `task_manifests/per-security-history-v3.json` and `batch_state/PER_SECURITY_HISTORY.json` **in memory**, from the trusted KRX private worker. The module itself makes zero network, file reads, writes or order calls.
2. Enforces exact original task-set ID SHA256, original per-kind task counts, per-task pinned SHA, receipt digest shapes, bounded issuer-year request metadata, completion membership/row-count integrity and no failed task states. It reports **only aggregate** total/complete/remaining foreign+institution source requests and **2022 investor-flow task counts** (including empty vs nonempty response checkpoints).
3. It **never** returns security identifiers, task IDs, source raw data or source digests, and never claims the protected raw bytes were independently re-verified. All as-of publication/vintage, 2022 original PIT, issuer/full-universe eligibility, performance, Holdout and trading flags remain false.

Example **read-only integration only for the KRX source owner after independently reviewing the audit code in the same private worker context** (not performed in this session; the isolated PR branch is not deployed):
```python
from pathlib import Path
import os
from research_v1_krx_private_store import read_private_json
from research_v1_krx_flow_existing_private_checkpoint_inventory import (
    summarise_frozen_2026_10_03_checkpoint_set,
)
root = os.environ["KRX_PRIVATE_RAW_DIR"]
worktree = str(Path.cwd().resolve())
manifest = read_private_json(
    root, "task_manifests/per-security-history-v3.json",
    git_worktree=worktree,
)["value"]
phase_state = read_private_json(
    root, "batch_state/PER_SECURITY_HISTORY.json",
    git_worktree=worktree,
)["value"]
summary = summarise_frozen_2026_10_03_checkpoint_set(manifest, phase_state)
# Only publicly safe counts and nonadmission markers; never print manifest/state
print(summary)
```
Before any verification of original 2022 source, KRX source owner must compare
the exact private 2022 task's stored raw-object bytes and receipt to their
SHA256 records, its actual response columns/scaling/issuer episode, and its
original-as-published/available-at release lineage. The function above checks
**metadata only**; it does not replace this raw-source step.

**CI evidence:** [Actions #38498924464](https://github.com/kims34/openpilot-opkr/actions/runs/38498924464), commit `9ff21013e5084b9b266b29d44a94801916f6f0ff`, **128/128 network-free synthetic tests passed** (15 additional inventory cases). These are not private Railway data or profitability tests. No new authenticated KRX query, consent use, raw file read or workflow dispatch occurred.
