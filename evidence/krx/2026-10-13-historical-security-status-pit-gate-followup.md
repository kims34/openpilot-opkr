# KRX historical security status and PIT evidence follow-up

Date: 2026-10-13 KST

## Read-only source comparison

The KRX official public website has pages for current [halted securities](https://open.krx.co.kr/contents/MKD/04/0403/04030300/MKD04030300.jsp), current [cleanup-trading securities](https://open.krx.co.kr/contents/MKD/04/0403/04030200/MKD04030200.jsp) and [exchange closures](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp). The public halted/cleanup listings are dynamic, current-state displays with export options. Their presence establishes possible source routes but does NOT establish full historical dated effective episodes, original publication time, or legal/technical permission for scraping/bulk export. No historical rows, securities or private originals were accessed or published in this follow-up.

## New regression and implementation

- [Historical trading-state temporal preflight](../../research_v1_krx_historical_status_pit_gate.py): an offline parser for sanitized provenance claims of the ORIGINAL dated securities-status archive. It checks the interval boundaries, duplicate records, market episode consistency, explicit timezone, original publication and first availability relative to decision time, retrospective retrieval and overlapping opposing states.
- [Synthetic tests](../../test_indexalert_krx_historical_status_pit_gate.py): positive/negative state, historical halt/cleanup/delist, current-snapshot misuse, late publication and availability, contradictions and unsafe timestamp formats.
- [Offline CI run 38416976458](https://github.com/kims34/openpilot-opkr/actions/runs/38416976458): success, **38 total tests** across existing source, calendar, adapter and historical-status suites.
- A SHA-like document fingerprint supplied in a metadata record remains an **unverified claim** until independent verification of the underlying original official dated notice, applicability, access scope and publication chronology. Even internally consistent original-date metadata never automatically releases securities into the investible universe.

## Current source-admission disposition

- KRX weekday acquisition/checkpoint pairs: **3,071** (2015-2026); integrity only.
- Calendar/empty provider response ambiguities: **184**, not resolved by modern online schedule pages.
- Exact problematic historical securities: **27 quarantined**; none cleared or traded by this test.
- Original source Gate C and D: **BLOCKED**. No newly admitted PIT market dates/securities and no NetEV/holdout decision made.
- Existing KRX OpenAPI six-GET test already completed; no re-dispatch and no broadened endpoint permission.
- No Railway service deployment/config changes, no KRX protected API reads, no live trades; ORDERING remains disabled.
- Separate branch only, unchanged Frozen/H5, Champion, Holdout.

Next useful evidence is a **date- and version-attested** official archive of KOSPI market sessions and historic security halt/resumption/cleanup/delist announcements with original published/available-at proofs, scoped access permission. Without it, keep the 184 date gaps and 27 securities unadmitted. Do not confuse code-test success with actual historical provider-source PIT validation.
