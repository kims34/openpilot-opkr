# IndexAlert M20 — correction-index coverage cutoff is an as-of feature prerequisite

**Date:** October 22, 2026 KST. **Verified offline safety logic; NO source, financial/PIT, profitability or live-trading admission.**

## Concrete prior research boundary

Independent official source-only issuer discovery identified the first 2022 Q3 filing plus **one later correction** for frozen cohort slot 5, but its final bounded historical correction index ended on **2026-10-13**. This result never established that *no new correction* could have appeared after that day. Existing `research_v1_m20_original_correction_asof_floor.py` initially took `correction_index_complete_for_window=True` as a boolean without binding the end of that verified window to the particular requested simulated trading day.

**Risk found and fixed:** with a hypothetical trade date after the known census cutoff, the old date-only *candidate* rule might have regarded the most recently observed corrected edition as a complete historical edition chain. This was **not** an authorized PIT feature or actual trading vulnerability (the contract always kept feature/PIT/orders blocked), but it could mislead later integrations that treat date-scope candidates too strongly.

## Change to fail-closed edition-date rule

- Add compulsory `correction_index_coverage_through_day` to `edition_date_floor`. Validate its strict `YYYYMMDD` shape through the preexisting date-only parser.
- Reject a supplied index cutoff **earlier than the latest separately attested corrected filing day**. If the cutoff predates the requested decision day, report `CORRECTION_INDEX_COVERAGE_ENDS_BEFORE_DECISION` with both original-edition and corrected-edition candidates **FALSE**, without inferring future correction status.
- Run original/correction day-floor checks *only when* initial filing, correction receipt, full bounded correction index and independently supplied official market session calendar are all attested. This avoids incorrectly assigning an episode when the chronology is incomplete.
- Preserve prohibition on trading from either filing's receipt date, edition overlap, inferred weekdays/holidays or synthetic intraday receipt timestamps; maintain the prior conservative one-year period between date and target decision for the independent candidate check.
- Never persist actual filing dates, issuer/stock IDs, calendar, financial source values, receipt IDs or provider details. New tests use **synthetic** dates including one example after a census cutoff, and are **not** an actual October 2026 disclosure query.
- Source and test changes on the dedicated unmerged branch: `research_v1_m20_original_correction_asof_floor.py`, `test_research_v1_m20_original_correction_asof_floor.py`, `.github/workflows/indexalert-m20-original-correction-asof-floor.yml`. Commits `dabe5140f5b77475a0544d344a90deb61f6778b1`, `8f2c182cb92f3bd01be656cb7a6d948264765fca`, `0b8280869dc0cdaf4be278de50e65002f87724b3`, `5247c83ec7e3afc248d8329cda2533b74eade7a8`, and final fixture isolation `02ce89b858cbc307670b8f401a654e69f215d3e9`.

## Actual reproducible GitHub CI

[Final GitHub Actions #39714478908](https://github.com/kims34/openpilot-opkr/actions/runs/39714478908) **SUCCESS**, all **23** source-date/epoch/regression tests passed, safe synthetic contract JSON generated, and no-network, no-DART, no-KRX, no-broker guard passed. The additional tests cover stale correction cutoff, future-day false confidence, malformed cutoff, cutoff before a known correction, independent calendar absence, no same-day eligibility, date-horizon and positive *candidate-only* behavior for separately attested complete index coverage.

Earlier CI [#39714389682](https://github.com/kims34/openpilot-opkr/actions/runs/39714389682) and [#39714414463](https://github.com/kims34/openpilot-opkr/actions/runs/39714414463) failed **only because an older non-trading-day synthetic test had not extended the newly mandatory correction-index coverage to its mock decision day**. The test was corrected to isolate a genuinely absent trading day from a stale correction census. Final CI was verified after this correction. No real source/correction values were ever admitted during CI.

- Final flags-only artifact: `12398780594`, digest `sha256:f7c2a61f7a29df4685ae5f09da6a62130f52270feef7abd1d8541f3bc9483935`, expires `2026-10-29T03:00:39Z`.
- The separately sealed previously verified four-result original 2022 Q3 viewer count capsule remains `12138239045`, digest `sha256:c9465d204b6a5c0b109807b06c352e46e12a50d8d717e953bd06ab3e9176036b`, expiry `2026-11-17T13:42:08Z`. This immutable counts-only archive is not an original signed CFS statement, not a historical release timestamp, and was not updated by this task.

## Financial source/PIT blockers remain independent

The previous [bounded public DART 8-page historical clock probe #39516110459](https://github.com/kims34/openpilot-opkr/actions/runs/39516110459) did not locate an exact first-filing row and stayed **FAIL CLOSED**, not proof that no historical public timestamp exists. Official OpenDART `rcept_dt` is only the receipt **day**; a fourteen-digit receipt number is not verified intraday time. No repeated public-page polling was conducted today.

First-edition 2022 July–September CFS operating-income **account/three-month monetary cell** and comparative 2021 equivalent, source-unit identity, original first-public availability, original/amended edition and exact numerical lineage, official historical issuer↔security PIT and full historical tradable market calendar are still **not independently attested**. Existing 2022 first-original XBRL API returned `014`. A later normalized filing or retrospectively generated bulk financial product must not be silently backdated to the original.

**Disposition:** Maintain Frozen H5/M20, all costs/taxes/Walk-Forward criteria, original cohort, Holdout seal and research Draft PR #412 (unmerged); **`ORDERING=DISABLED`**; `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, no funds/permission changes. No Railway environment, Kiwoom credential, live account or hourly automation was modified. Only a new separately sourced, positively attested accounting/provenance path can move the original 2022 Q3 PIT blocker.

## External basis

- Official [OpenDART filing-list API guide](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001): receipt date `rcept_dt` vs receipt identifier `rcept_no`.
- Official [OpenDART XBRL downloadable statement interface](https://opendart.fss.or.kr/disclosureinfo/fnltt/xbrl/main.do): available current source is not by itself proof of as-of first-filing edition.
