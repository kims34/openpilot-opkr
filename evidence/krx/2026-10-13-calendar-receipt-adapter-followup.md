# KRX calendar receipt adapter follow-up (2026-10-13)

This evidence is a code-and-synthetic-tests handoff, not a new source admission.

- Source: the existing original KRX SHA-backed offline audit returns per-day metadata (`day`, `pair_sha256`, `daily_rows`, `common_rows`, `source_day_class`).
- Adapter: `research_v1_krx_calendar_receipt_adapter.py` validates those metadata fields and converts the three known classes into EMPTY/NONEMPTY observations. It does not independently rehash original data or attest the upstream caller.
- Reconciliation: `research_v1_krx_calendar_gap_boundary.py` generates *unverified source/calendar consistency candidates only*. It does not validate third-party calendar authenticity, PIT timestamps, securities, or economic execution.
- CI: workflow `indexalert-krx-pit-handoff-offline-guard.yml`, run 38415935889, completed SUCCESS: all 25 offline synthetic/metadata tests passed.
- Independent references: KRX equities trading-day rules (https://regulation.krx.co.kr/contents/RGL/03/03010100/RGL03010100T1.jsp) and KRX holiday page (https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp). The interactive page was found, not converted into an independently attested historical 2015-2026 KOSPI calendar. Modern rules must not be retroactively treated as original historic date-level evidence.

Still open: 184 ambiguous stored-source dates; independently proven historical official KOSPI trading sessions; 27 historically questionable securities (excluded); official halt/delist/corporate actions; original published/available-at PIT chronology. No KRX raw market-data network requests or worker config updates were performed by this follow-up. No model promotion, holdout unlock, real orders, funds movement, or additional OpenAPI endpoints are authorized. `ORDERING=false`.
