# KRX official market source: 2015–2026 read-only evidence handoff

Audit date: **2026-10-13 KST**  
Disposition: **Private KRX source storage integrity is verified over the observed weekday grid; official exchange calendar, historical PIT and tradability are NOT admitted.**  
Scope: metadata-only independent review, no newly dispatched KRX network operation, no order, no runtime configuration change.

## Pinned sources inspected

| Component | Exact observation |
|---|---|
| Development base | `index-alert-position-regen-fix-v1` at `1e6367d2863a86c3470da13d81a955d277eba485` |
| Research snapshot | `index-alert-research-v1` at `3b8b7830612a6284d7c7a60628cb527cb741627a` (2026-10-13 observation; separate ongoing M20 work is not touched) |
| Railway worker | `indexalert-krx-historical-worker`, service `003812ee-102b-42b6-bda4-36925885b428`, private volume `indexalert-krx-historical-data` mounted at `/data` |
| Production deployment observed | `16c93d7c-7cd0-4d84-a327-298d2805376c`, SUCCESS; start command `python -B research_v1_krx_openapi_missing_2017_2022_integrity_audit.py --audit` |
| Existing six-GET OpenAPI sample | [GitHub Actions run 38203814820](https://github.com/kims34/openpilot-opkr/actions/runs/38203814820), SUCCESS, job `114674734929`, metadata-only artifact `11727893147` |

The actual latest worker deployment logs were inspected, not inferred from CI. GitHub Actions [2017–2022 six-year offline test](https://github.com/kims34/openpilot-opkr/actions/runs/38251143908) passed including container build; the [recent 2023–2026 offline integrity check](https://github.com/kims34/openpilot-opkr/actions/runs/38212546566) passed. Successful offline CI proves the audited **code path** and assertions, not PIT eligibility of the underlying original market records.

## Verified storage scope vs unresolved historical market facts

| KOSPI year group | Source weekday date pairs verified on private store | No missing requested weekday checkpoint | Calendar-or-source-empty dates **not independently classified** | Historical PIT admitted |
|---|---:|---|---:|---|
| 2015–2016 | 522 | Yes | 28 | **No** |
| 2017–2022 | 1,565 | Yes | 90 | **No** |
| 2023–2026 (through observed partial 2026 collection) | 984 | Yes | 66 | **No** |
| **Combined** | **3,071** | **Yes** | **184** | **No** |

**Interpretation is important:** these are **weekday fetch/checkpoint pairs**, *not confirmed exchange trading days*. An empty official response could be a holiday, a provider-side source gap or a genuine zero-observation state; without an independently verified KRX calendar and per-episode security status, these are not interchangeable. `missing_weekday_pairs=0` does **not** imply there are no missing trade observations.

Actual independent 2015–2016 worker logs report `INDEXALERT_PRIVATE_KRX_OPENAPI_INTEGRITY` with fingerprints `919b306be06696ecad8e32578d981b6e1fc7479c38bfee2a55cdbfd39c5970f6` (2015) and `99720d33ed393db89ff7186d09e79ccd19f30647a7552be1abc1dc30a1263590` (2016). The 2017–2022 `INDEXALERT_MISSING_2017_2022_INTEGRITY_FINAL` fingerprint is `e2503a3bc623d4386e5783ec19272916fe6abba9bc191c14040d2c0831c7f01a`; the 2023–2026 `INDEXALERT_RECENT_INTEGRITY_FINAL` fingerprint is `be12af649926d95a9694381e41f3dffa0add637b72fd46fe1e7aed9a407499a0`.

2017–2022 source acquisition had 3,130 observed approved OpenAPI requests and 2,773 new private content-addressed raw objects. The **follow-up integrity audit** was network-free: 1,565/1,565 pairs, no missing checkpoints and 90 unresolved calendar/source-empty dates. Do not confuse the acquisition requests with the audit's zero-network execution.

Stored OHLC samples contained some zero-activity/invalid observations; no unsafe zero-volume-to-trading-halt inference or automatic fill assumption is permitted. Original security identifiers and price rows remain on the private Railway volume and are not published here.

## Trading status, delistings, corporate actions, PIT

- **27 problem securities are explicitly quarantined:** not recognized as verified tradable securities or admitted into an investible universe until independently sourced official trading state and effective times are verified. The 27-request *identity seed* in earlier source evidence does not by itself establish these 27 securities' tradability; do not conflate those counts.
- KRX approved OpenAPI `stk_isu_base_info` and `stk_bydd_trd` cover security-basic and daily-trading services only. Reachability of screen-data `MDCSTAT21301` (halt), `MDCSTAT23801` (delisting/cleanup intervals), `MDCSTAT23902` (delisted prices) in earlier probes is not an accepted authorization or an independently complete PIT source.
- Official KRX exchange trading-day calendar is **not reconciled**, and the unresolved 184 dates are not classified as holidays, losses of data, or official halts.
- Historical identity mapping, listing-to-delisting episodes, halt/resume dates, cleanup dates, splits/dividends/rights/other corporate actions and actual fill/recovery economics remain **unverified** for final source admission.
- Retrospective KRX query time must never masquerade as the timestamp at which market data originally became available. Per-record original `event_time / published_at / available_at / ingested_at` lineage and decision cutoffs remain open.
- Existing KRX source admission Gate C (full historical security/status coverage) and Gate D (original historical PIT availability) stay **BLOCKED**; A/B remain route/schema-scoped, not a blanket pass. Profitability experiments, independent holdout and model promotion remain unauthorized on this input.

## Already approved six-request first sample: verified complete, do not repeat

The `HKG_community` default-branch workflow `.github/workflows/indexalert-krx-openapi-approved-six-get-bridge.yml` already ran on 2026-10-12. Run `38203814820` explicitly passed the exact checked-out research SHA `dd839a3146af2261be4e3fde810a4a62881bacd3`, 16/16 offline contract unit tests, the six-request guard and the metadata-only artifact upload. The existing [user consent scope](https://github.com/kims34/openpilot-opkr/blob/index-alert-research-v1/INDEXALERT_KRX_OPENAPI_HISTORY_USER_CONSENT_2026_10_12.json) was **two named KOSPI endpoints × three fixed dates** (`20150105`, `20260928`, `20261001`), max six GETs, manual dispatch only.

This sample proves a bounded official endpoint path and validation under the existing authority. It does **not** resolve historical calendar, status, original PIT availability or source admission. No duplicate request was dispatched by this audit and no further user action is required merely to repeat that sample.

## Downstream source-admission instructions

1. Consumers may use this manifest only as an **integrity/capture inventory** or as a list of open blockers. **PIT-usable full-universe official dates/securities: none newly admitted.**
2. Review already existing private raw/receipt data and independently reconcile the official calendar first; reuse each content-addressed raw object. Resolve the 184 ambiguous dates without silently replacing them, excluding them as false holidays or inventing zero-activity sessions.
3. Independently validate the *exact 27 affected securities* against official halt/resumption, cleanup and delisting status. Do not admit a position, even with nonzero OHLC, before official status/effective-time proof.
4. Capture dated corporate-action mapping and publication/availability lineage. Reconcile prices and market cap to the original KRX episode identity, and confirm transaction cost/market execution restrictions before any PIT historical backtest.
5. Do **not** authorize authenticated Data Marketplace sessions, broad status collection, account changes, new expensive API products, model promotion, sealed holdout or actual trading from this handoff. Each extra protected run must pass its own exact consent and source-access gate.
6. Keep `ORDERING=false`, H5/Frozen/Champion/Holdout unchanged. Do not edit worker launch config for the purpose of merely producing a report.

## Machine-readable cross-check

- [Sanitized full evidence](./2026-10-13-krx-market-source-pit-boundaries.json)
- [Zero-network, metadata-only safety regression](../../test_indexalert_krx_market_source_pit_boundaries.py) — run from repository root: `python -m unittest -v test_indexalert_krx_market_source_pit_boundaries.py`.
- Frozen result: **`STORAGE_INTEGRITY_VERIFIED; EXCHANGE_CALENDAR_NOT_ATTESTED; OFFICIAL_STATUS_NOT_ADMITTED; PIT_NOT_ADMITTED; 27_QUARANTINED; ORDERS_DISABLED`.**

No raw provider rows, exact private security identifiers, credentials or API secret values are included.

## 2026-10-13 continued execution: offline calendar discrepancy guard

An independent metadata-only candidate classifier was committed on the same isolated branch:
- [Calendar gap classifier](../../research_v1_krx_calendar_gap_boundary.py): inputs are date-scoped SHA-bound **existing** response receipts and separately supplied claimed KRX calendar metadata; no network, no private Railway access, no broker access or mutations.
- [Synthetic-only regression suite](../../test_indexalert_krx_calendar_gap_boundary.py): handles empty-on-open (possible source gap), empty-on-closed (closure *candidate only*), nonempty-on-closed (contradiction), unsupported sources, missing dates, duplicate dates, impossible dates and weekend exclusion. All classes remain fail-closed to real PIT admission.
- [Offline guard Actions workflow](../../.github/workflows/indexalert-krx-pit-handoff-offline-guard.yml) runs this alongside the existing 6 handoff tests.

**Important data boundary:** the classifier has not ingested actual per-date private KRX receipts or an independently authenticated original KRX trading calendar. A string declaring `KRX_OFFICIAL_EXCHANGE_CALENDAR` and a SHA digest cannot authenticate a source document. The outputs are **provisional consistency categories**, not independently certified trading days, missing rows, PIT features or approval to run profitability analysis. The unresolved 184-day historical tally is unchanged and the 27 risky securities stay quarantined. An authorized and independently attested date-by-date source must be acquired and validated before updating the source-admission manifest. No new provider calls were executed by this continued audit.

## Official public calendar reference discovered (read-only, not reconciled)

The Korea Exchange maintains a public [KRX stock-market holiday / schedule lookup page](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp), with an interactive search/download interface. KRX's [stock market trading day and closure rules](https://regulation.krx.co.kr/contents/RGL/03/03010100/RGL03010100T1.jsp) give the closure classes, including exchange-designated exceptional closures. This is a more appropriate **independent official source candidate** than merely assuming that all ordinary public holidays equal historic KOSPI closures; the rule text by itself does not establish each original 2015–2026 calendar date.

No historic per-date results were downloaded or authenticated during this audit: the public page's dynamic table is not a proven full historic 2015–2026 machine-readable source. Check market=KRX and KOSPI applicability, date coverage, special year-end/temporary closures, date-by-date provenance and applicable data rights before comparing private SHA-backed per-day observations. The KRX OpenAPI service list and two already-approved endpoint scopes have not been expanded. No new KRX request or PIT permission is implied.
