# KRX holiday XLSX: workbook-linked auxiliary parts must be real, not ZIP decoys

**Review date:** 2026-10-22 KST. Work restricted to `indexalert-krx-pit-source-audit-20261013`, not live development or real-money deployment.

## Confirmed defect fixed

Our prior XLSX holiday original-byte validator already required:
- strict ZIP part allowlist, bounded extracted bytes, SHA-bound source-to-sidecar dates;
- first-party-like package-root workbook relationship and core OPC ContentType overrides;
- workbook-to-visible-sheet relationship, complete date numeric styles and no invisible worksheet rows.

However, after opening `xl/workbook.xml`, it unconditionally read **`xl/styles.xml`** or **`xl/sharedStrings.xml`** if the files merely existed in the ZIP. The workbook could have **no relationship to either part**, or a relationship to a different XML file, while the validator would still parse the decoy auxiliary files as though Excel displayed them. In particular a numeric Excel date serial could pass when its alleged date style existed **only as an unused ZIP entry**, and Excel would instead display a bare number.

## Safe remediation

- [XLSX validator](../../research_v1_krx_calendar_xlsx_source_validator.py): require a single correctly typed `styles` link for `xl/styles.xml` and a single correctly typed `sharedStrings` link for `xl/sharedStrings.xml` when those parts are present; forbid references to either if corresponding parts are missing.
- Verify the linked targets are specifically `styles.xml` / `sharedStrings.xml` (or their canonical absolute `/xl/...` forms), and fail closed on duplicate workbook relationship IDs.
- Require the optional actual sharedStrings part's ContentType declaration to match its expected OOXML MIME type.
- [Offline regression fixtures](../../test_indexalert_krx_calendar_xlsx_source_validator.py): add synthetic cases for **missing style relationship**, wrong style target, wrong shared-string target/missing shared string relationship, duplicate IDs, and fully valid linked auxiliary parts; keep normal numeric Excel dates and visible-source date matches accepted only at the narrow `NOT_PIT` status.

## Execution proof

[GitHub Actions #39714202742](https://github.com/kims34/openpilot-opkr/actions/runs/39714202742) on `82a15b9f824a3fa7b494019201c20441c1ec37a5`: **SUCCESS, Ran 162 tests, OK**. Parser code commit `4ff157e8642de9c472cb079419ee979479282781`. Intermediate changes without updated synthetic fixtures had failing workflow runs; the final corresponding code-and-test revision passed.

This proves **only the offline parser invariant**, not KRX source provenance or historical PIT. No KRX original holiday exports were downloaded or SHA-attested during this review, and no private original daily provider pair data was accessed.

## Strict trust boundary remains

The previously verified Railway original storage report remains 3,071 SHA-backed weekday receipt pairs for 2015–2026 (2026 pinned through Oct08), with **184** ambiguous source-empty weekdays and **27** historical securities quarantined. These were **not re-audited or reduced in this work**. The Railway connector was unavailable in this turn; therefore no claim is made that the deployed Railway service's latest 2026-10-22 state was directly inspected. No deployed environment, protected data volume, credential, secret, broker settings, data rights or funds were changed.

Full original KRX cash-equity annual holiday/session files, authentic provenance, historical versions/first-published-at timestamps and permitted private date-by-date comparison remain missing. PIT source C/D, M20 independent profitability, frozen Champion promotion and holdout stay unauthorized; `ORDERING=false`; no live orders or additional authenticated KRX OpenAPI calls.

**Actual unblock:** obtain lawful original first-party full-year calendar bytes for KOSPI cash equities and independent SHA/version proof, then run a read-only, SHA-pinned private exact day-set comparison in an explicitly authorized protected environment. An offline 162-test pass must not be treated as source PIT proof.
