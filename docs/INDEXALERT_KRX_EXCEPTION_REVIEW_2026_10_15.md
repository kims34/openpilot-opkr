# KRX exceptional 2017–2022 weekdays and nonpositive-price review — isolated offline candidate

**Date:** 2026-10-15 KST. **Status:** experimental acceptance harness; official historical PIT and profit tests remain blocked.

## Evidence / non-goals

- The dedicated Railway read-only six-year worker independently hash-verified 1,565/1,565 private captured weekday daily/master pairs, while flagging **90 exchange-calendar vs source-gap uncertainty days**. It also recorded 12,003 sampled zero-activity OHLC rows and one other invalid sampled OHLC shape.
- An independent prospective read-only ingestion failed closed on 27 nonpositive-OHLC common-stock rows out of 803 sampled common-stock rows. These 27 are **not** proven legal suspensions or tradable securities.
- The previously approved KRX routes were `stk_bydd_trd` and `stk_isu_base_info`. No new KRX provider request/endpoint, permission, secret, Railway deployment, private original source mutation, market action or brokerage activity occurs here.

## Implemented: pure-Python compatibility checks, not original source admission

`research_v1_krx_offline_exception_review.py` is an **offline receipt-format and contradiction checker**. The isolated `test_research_v1_krx_offline_exception_review.py` includes synthetic positive and negative cases with **no real symbol, price, receipt, holiday calendar or account**. Explicit `exception_dates` must be unique sorted 2017–2022 weekdays and match SHA-shaped private `raw_day` source receipts exactly.

- Optional independently claimed calendar receipts may label only `OPEN` or `CLOSED`. A closed session with source trade rows, or an open session with zero source rows, **fails closed** instead of being treated as a verified holiday or market gap. Missing day claims stay unresolved.
- Optional security/day receipts may label `SUSPENDED`, `DELISTED`, `LISTED`, or `UNKNOWN`, and must match SHA-only quarantined nonpositive-OHLC security/day tokens exactly. They **never** authorize fills even if status is `LISTED`.
- Claims carry strict per-source 64-digit SHA-256 format and explicit source category. Such metadata **is not authenticated by this local function**, and no external publisher or as-of-vintage signature is verified by this candidate. This function deliberately returns `calendar_original_publication_pit_verified=false`, `individual_tradability_verified=false`, `historical_corporate_actions_verified=false`, `full_universe_source_admitted=false`, `m20_performance_run_authorized=false`, `live_orders_authorized=false`, `ordering=DISABLED` regardless of apparent consistency.
- No actual list of 90 dates, individual 27 securities, full source hashes, raw rows, market close prices or brokerage identifiers appears in GitHub Actions. GitHub unit-test success proves only **synthetic guard logic**, not completeness/accuracy of KRX historical calendar or any real market-data admission.

## Mandatory next official proofs

The authorized KRX evidence owner must privately compare every unknown weekday to **date-specific official exchange open/close status with independent source provenance**, preserving unresolved classifications if source evidence is absent. Separately, each quarantined stock/day must be matched to independently authenticated **historical listing/suspension/delisting/corporate-action timelines** and original security mapping without survivorship or look-ahead. Distinguish an exchange-wide session from *individual executable tradability*. A present-day index daily series might corroborate sessions if separately approved, but **cannot certify per-security status** and no new service authorization is implied here.

Only after external-source integrity, availability/as-of PIT, authentic issuer/security mappings, full universe & calendar, costs/taxes/fills and independent risk gates pass can any full H5/M20 market-data profitability run be considered. Frozen protocols, WF504/126/126, Purged/CPCV, holdout and Champion do not change; NO_TRADE remains an option. No live order/funds/permissions or branch merge permitted by this draft.


## Cross-horizon correction — 2026 prospective 27 rows are not the 2017–2022 90 historical exceptions

An independent Railway prospective runtime log explicitly reports `source_failure_session=2026-09-28`, `COMMON_OHLC_NONPOSITIVE`, **27** common-stock nonpositive OHLC rows; the same deployment reports `session=2026-10-14`. This is **not** part of the separate historical 2017–2022 90 exceptional weekdays; do not treat the recent 27 rows as 2017–2022 date-scoped observations or silently drop them because their year does not match the historic calendar validator.

- [Source correction `6b0e3c3`](https://github.com/kims34/openpilot-opkr/commit/6b0e3c304254d7ebcfde54275cd92811191b0ed7) keeps the KRX calendar exception window strictly **2017–2022**, while allowing **only exact 2026-09-28** in the independent quarantined anomaly/security-status claim scope. No other 2023–2027 date is admitted from this log. For historical anomalies, the date must be in the matching captured original source-pair exception scope; prospective anomaly claims remain independent of old stored pair hashes.
- [Six extra synthetic tests `dafe3aa`](https://github.com/kims34/openpilot-opkr/commit/dafe3aa987d794a468995a5431de540e3fd9f6ff) prove cross-horizon separation, reject unrelated dates, reject prospective status based on a mismatched historical row, reject unsupported historical anomaly days and ensure that a 2026 market calendar claim cannot masquerade as 2017–2022 holiday proof.
- New independent diagnostic fields `prospective_nonpositive_ohlc_rows_quarantined`, `historical_nonpositive_ohlc_rows_quarantined`, `prospective_input_source_pit_authenticated=false` and `retrospective_claims_independently_authenticated=false` clarify what the synthetic fixture does **not** establish.
- **No actual 2026 security/day source rows, identifiers, brokerage connection or data source credentials were loaded**. Tests use invented SHA-shaped tokens only; any comparison with actual 27 source records must happen under an independent source-authorized private worker. Even a passing synthetic result cannot approve PIT/economics/individual fills or change `ORDERING=DISABLED`.
