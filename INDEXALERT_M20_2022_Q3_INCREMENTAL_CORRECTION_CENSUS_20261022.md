# IndexAlert M20 — official incremental 2022-Q3 correction census through 2026-10-21

**Read-only source verification at 2026-10-22 KST: SUCCESS.** Only the fixed frozen original cohort slot **5** and the previously independently discovered first 2022-Q3 filing/later-corrected filing are within scope. No 2022 original financial CFS 3-month numbers, strategy returns, market data or orders are admitted.

## Why this independent source request is justified

The previously validated [historical correction census](INDEXALERT_M20_OPENDART_2022_CORRECTION_SOURCE_PAIR_HANDOFF_20261013.md) ended at **2026-10-13** and had found a single later correction of the original `분기보고서 (2022.09)`. The new [as-of date/cutoff admission guard](INDEXALERT_M20_CORRECTION_INDEX_CUTOFF_GUARD_20261022.md) demonstrated that an edition catalog ending on 2026-10-13 cannot be assumed complete for decisions after that day. An explicitly separate narrow official source query was therefore warranted to check **2026-10-14 through 2026-10-21, inclusive**. The query intentionally ended at the last fully elapsed Korea-local date before the current day; it did not claim that October 22 is a completed session.

## Exact new official read-only verification

- Code: `research_v1_m20_2022_q3_incremental_correction_census.py`
- Synthetic safety tests: `test_research_v1_m20_2022_q3_incremental_correction_census.py`
- Dedicated workflow: `.github/workflows/indexalert-m20-incremental-correction-census.yml`
- Existing isolated research branch, original fixed cohort position **5**, no reselection or changing live/research branches.
- **Maximum two authenticated official OpenDART requests:** `corpCode.xml` to resolve the existing frozen issuer, then `list.json` for the one exact 2026-10-14..21 window, only periodic disclosure type `A`, `last_reprt_at=N`, 100 max rows, one page. Pagination, response code, company/receipt metadata, window day identity and any matching correction/attachment labels are validated **in memory**, never logged raw. No public DART web rendering, KRX, Kiwoom, Railway or account access.
- Official list API status `013` is documented **"조회된 데이터가 없습니다"** (no queried data); other error statuses fail closed, including `014` file-not-found and `020` request limit. The code expressly rejects `013` if it is accompanied by substantive rows or incompatible pagination metadata. Official docs: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001.

**Actual [GitHub Actions #39715224915](https://github.com/kims34/openpilot-opkr/actions/runs/39715224915): OFFLINE SUCCESS (16 tests), OFFICIAL SOURCE SUCCESS.** Exact redacted official response interpretation:

| Source-only indicator | Verified result |
| --- | --- |
| Authenticated two-call budget adhered to | Yes |
| Actual official `list.json` result | `013`: no queried data |
| Actual scoped query rows (all periodic filings) | **0** |
| New 2022 Q3 corrected filing rows in this bounded window | **0** |
| New matching 2022 Q3 attachment-addition rows | **0** |
| Original-to-amended profit financial-cell/PIT verification | **No** |
| M20 features/backtest/holdout/orders approved | **No** |

Immutable safe status-only Actions artifact `12399026032`, digest `sha256:79f387b37b9766d01b6328724dd555d561b6429a6c96f958bbe7be20467921d3`, expires `2026-10-29T03:09:12Z`. None of issuer identifiers, receipt IDs, actual original/correction dates, text of company filings, sensitive report contents, monetary cells or API credentials appear in saved CI output. Source+test+workflow source commits `ea72dcbd88666febc8ca570571736a66b5a11b4c`, `d458d27b2dd1b33b6a645f2151c5e9ff0bb3457b`, `b7aa8e5b44e5ca8da34add14c14810bdc5419c9f`.

## Exact inference bound and next open evidence

The **bounded no-new-periodic-result** plus previously separately verified correction-index window provides complementary **observed list-index evidence through 2026-10-21** for this frozen issuer. It does not prove absolute completeness, prevent retrospective restatements, confirm prior first-edition financial cells or independently attest a historical intraday disclosure instant. The 2026-10-22 day itself is **not** checked and cannot yet be marked complete. Current registry lookup is not historical ticker↔issuer PIT. The earlier original 2022 Q3 `fnlttXbrl.xml` endpoint returned `014`, and current normalized 2022 CFS did not yield independently acceptable original cells; the viewer’s **329** tables and **2** earnings-label candidates remain semantically unbound.

**Remain blocked:** exact first-filed 2022 Q3 and comparative 2021 Q3 **standalone three-month consolidated operating-profit account/currency/amount/cell**, complete original vs correction financial-cell lineage, independently proved first-public availability, KRX historical session/universe/security PIT and authentic economic features. This task does **not** authorize backfilling 2022 Q3 values from a later corrected/current filing or provider download. If a future correction appears, the narrow census must halt and require first-edition re-attestation rather than silently overwrite an original vintage.

Maintain Frozen H5/M20, preregistered research, independent Holdout, all costs/taxes and proof-before-profitability. `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, no funds or permissions, **`ORDERING=DISABLED`**. Research [Draft PR #412](https://github.com/kims34/openpilot-opkr/pull/412) must not be merged based on source-count/date-only evidence. Existing hourly automation, Kiwoom credentials, Railway and brokerage ordering remain untouched.

## Historical source boundary

The previously retained four-source original-viewer **30-day sealed count capsule** ID `12138239045`, digest `sha256:c9465d204b6a5c0b109807b06c352e46e12a50d8d717e953bd06ab3e9176036b`, reported expiry **2026-11-17T13:42:08Z** is unmodified. It verifies historical *counts/flag outputs* only; it is not an archived signed original CFS financial statement or a financial PIT admission.
