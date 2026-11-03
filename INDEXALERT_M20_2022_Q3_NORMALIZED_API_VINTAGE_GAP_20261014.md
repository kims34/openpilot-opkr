# M20 2022 Q3 frozen cohort slot 5: normalized CFS source availability gate

**Disposition: FAIL-CLOSED. NOT PIT ADMISSIBLE. No trading.**

On 2026-10-14, the official OpenDART 2022-Q3 3-month CFS schema probe was run read-only under [Actions #38508181214](https://github.com/kims34/openpilot-opkr/actions/runs/38508181214), source commit `e85de9567963e20d65ad7ed2e93f75fd2bcc4cda`.

The **offline regression/security job passed**, including controlled checks that current `thstrm_amount` and preceding `frmtrm_q_amount` have distinct 3-month semantics and that no API output can enable original PIT, Holdout or orders. The **actual official source job failed closed**, with safe output `source_status=SOURCE_GAP_FAIL_CLOSED`, `source_gap_reason=OFFICIAL_2022_NORMALIZED_FINANCIALS_ABSENT`. The code groups official `013` no-data and `014` no-file into this single safe class; the individual upstream code was **not retained**, so neither one may be asserted specifically. The official full-statements API yielded no admissible normalized 2022-Q3 CFS financial records at this frozen issuer/report target.

Official guide: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020. It specifies `bsns_year=2022`, `reprt_code=11014`, `fs_div=CFS`, and for quarter IS/CIS records `thstrm_amount` and `frmtrm_q_amount` as the **current/prior standalone three-month financial amounts**, while `*_add_amount` are cumulative. The API has no first-original/as-of-publication edition-selector query argument. **Even successful current API fields would not prove a 2022-original PIT vintage.**

Evidence artifact `11868283548`, counts/status-only, SHA256 `53bc73cef55f4484be1f3cd43d9a4fcaa706c49d0629c5dbb526f5e48e29a03f`, 7-day retention. New source/CI/tests are:
- `research_v1_opendart_m20_2022_normalized_quarter_source_gate.py`
- `test_research_v1_opendart_m20_2022_normalized_quarter_source_gate.py`
- `.github/workflows/indexalert-m20-2022-normalized-quarter-source.yml`

No firm identity, receipt IDs, API key, full official API payload or financial amount was emitted/saved. This probe did not retrieve the 2022 first-filed XBRL `014` archive; that earlier source remains unavailable and is a separate independent blocker. The official first-filed 2022 Q3 SGML document and one later amendment have previously been checksum-pinned and content/row/sequence compared. The original and corrected source statement/cell semantics, 2022-versus-2021 standalone-quarter values, first publication instant, revision timeline and historical issuer↔security PIT mapping remain unverified.

**Do not re-label this as an API success or infer the absence of 2022 financial facts from one failed normalized endpoint.** No change to Frozen H5, preregistered M20, original cohort slot 5, baseline, taxes/costs, Purged/CPCV, Walk-Forward, holdout or Champion. `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, no orders/funds/permissions and `ORDERING=DISABLED`; retain Draft PR #412 unmerged.

**Next appropriate research:** identify a separately provenance-audited *original-vintage* XBRL/XML or manually auditable SGML statement+period+currency+lineage evidence; do not backfill the 2022 original with revised data and do not repeat the failed current API query without a new hypothesis.
