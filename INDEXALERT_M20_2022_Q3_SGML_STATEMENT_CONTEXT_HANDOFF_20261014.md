# M20 SGML historical 2022 Q3 statement-context review

Prior official [run #38464847141](https://github.com/kims34/openpilot-opkr/actions/runs/38464847141) passed offline and read-only checks. The original and amended ZIPs differ, and their decompressed inner SGML document content also differs, even though all 15 exact-label operating-income row candidates remain equal. No financial amounts or raw documents are persisted.

Prior [run #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990) found no candidate tables with exact three-month headings or nearby exact consolidated-income-statement titles, and no both-years Q3 date-window match. Therefore no authoritative 2022-versus-2021 Q3 consolidated 3-month income row is established.

Branch commit `16dcc1fffb026ac6c72d663fc92e79ff525da2e2` now tests first-filed and amended SGML layouts separately, recording counts of three-month headers, CFS titles, period windows and quarter context. Offline regressions passed. [Official-source run #38466077093](https://github.com/kims34/openpilot-opkr/actions/runs/38466077093) was still in progress when the note was written; do not infer success until final Actions logs are examined.

Initial XBRL 014, original three-month CFS profit, prior comparator, precise PIT release instant, and historical issuer/security mapping remain unverified. M20 feature/performance/Holdout/Champion/live are blocked; `ORDERING=DISABLED`. Draft PR #412 only, not merged.


## 2026-10-14 follow-up official table-text census

- [Actual OpenDART CI run #38484411722](https://github.com/kims34/openpilot-opkr/actions/runs/38484411722) on source-only commit `34907e2781cae5638b945c6b002599cbe725875a`: offline safety and official read-only jobs **both SUCCESS**.
- Under exact previously pinned original and corrected ZIP bytes, the bounded decompressed-SGML table text-multiset scanner found **1,570 original tables, 1,576 corrected tables, 1,570 normalized table-text multiset members in common**, and **six corrected-only table-text members**. All original text-table signatures have counterparts in corrected source. This is **not** a table-position- or accounting-statement lineage assertion; whitespace normalization and nested tables are source-only.
- Previously independently proven 15/15 exact-label operating-income row candidates and numeric-peer candidates remain unchanged. The newly detected six extra source-text tables are *not proven* to be related or unrelated to authoritative CFS 3-month operating income; no row text or amount was saved.
- Code+test SHA `34907e2781cae5638b945c6b002599cbe725875a`; flags-only artifact ID `11858509198`, name `indexalert-m20-operating-row-diff-counts-only`, ZIP digest `sha256:a324176ba629290937cdad7bd1ef6eb420d0859347b874e8829c2042e1113508` (7-day retention).
- **Next source problem:** if future official probes are needed, attribute the six added source tables to validated statement/note sections *without* disclosing source values, and independently obtain exact original 2022/2021 3-month CFS financial cells, original release time, amendments' actual publication times and historical issuer/security PIT. Missing standardized original XBRL remains code `014`. Do not backfill using amended filings.
- M20 historical PIT/performance/Holdout/Champion/real order/funds/permissions remain blocked and `ORDERING=DISABLED`.
