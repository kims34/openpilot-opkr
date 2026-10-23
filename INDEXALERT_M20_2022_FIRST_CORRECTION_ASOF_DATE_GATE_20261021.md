# IndexAlert M20 — first-vintage vs corrected-vintage as-of boundary and retrospective OpenDART data warning

**Verified October 21, 2026 KST.** Research scope: original fixed issuer cohort slot 5, first-filed 2022 Q3 report and one independently recorded later correction. **NO original CFS financial PIT admission, NO performance run, NO live orders.**

## Source evidence already established

- The earlier official read-only OpenDART issuer/report census verified an original 2022 Q3 receipt and **one later 2022 Q3 correction** in a separate date window through October 13, 2026. Original and correction SGML document ZIPs have distinct pinned fingerprints, but their scanner-selected 15 exact-label operating-profit rows matched. There is no proof those SGML row texts correspond to the originally published **standalone three-month CFS operating-income amounts** for 2022 Q3 and 2021 Q3; the first-original 2022 standardized XBRL request returned `014` and normalized current 2022 Q3 CFS remained unavailable.
- Official OpenDART `rcept_dt` supplies an eight-digit **receipt day**, not an authoritative intraday publication time. A fourteen-digit filing receipt ID is not a clock. Previous code `research_v1_m20_dart_receipt_date_floor.py` blocks decisions on or before the first receipt date, requires separately verified official historical trading sessions, and never admits financial features on date matching alone; [offline 14-case CI #39347856501](https://github.com/kims34/openpilot-opkr/actions/runs/39347856501) passed.
- **Separate, source-quality warning discovered by checking the actual official [OpenDART bulk financial statement download table](https://opendart.fss.or.kr/disclosureinfo/fnltt/dwld/list.do):** its current page displays the **2022 third-quarter** aggregate-download entry with a file **generation date 2024-06-11**. This is batch-product metadata, not a company-specific earliest release date, and **not proof the given first-filing source existed in that bulk form in 2022**. Retrospectively generated bulk financial statements cannot automatically be substituted for first-vintage as-of evidence. The related official [OpenDART XBRL download interface](https://opendart.fss.or.kr/disclosureinfo/fnltt/xbrl/main.do) likewise does not by itself provide a verified historical as-of snapshot. Neither public download was imported into frozen PIT financial inputs.

## This turn: first-vs-corrected as-of date-scope contract

- New `research_v1_m20_original_correction_asof_floor.py`, `test_research_v1_m20_original_correction_asof_floor.py`, and `.github/workflows/indexalert-m20-original-correction-asof-floor.yml` on the existing isolated branch.
- Given independently attested first-original receipt date, later correction date, a **full verified correction index**, and an explicitly attested official historical session calendar, it reports categorical *possible date scopes* only:
  - On/before initial first receipt day: **rejected**.
  - Strictly later than original and earlier than correction, on actual attested session: **original-edition DATE-SCOPE candidate only**.
  - On the correction receipt day: **rejected**, regardless of possible actual release time.
  - Strictly later than correction, on actual attested session: **corrected-edition DATE-SCOPE candidate only**; never insert revised values into any earlier date.
  - Missing provenance, missing/invalid historical calendar, malformed dates, excessive horizon or ambiguous chronology: **fail closed**.
- This contract has **no actual receipt numbers, company names, real calendar, financial amounts, amendment values, or generated strategy returns**. All examples are synthetic. It does not assume every future original historical session is eligible, does not derive timestamps from receipt numbers, and it has no way to authorize source/PIT/performance/orders.
- [Actual GitHub Actions #39515663632](https://github.com/kims34/openpilot-opkr/actions/runs/39515663632) **completed SUCCESS, 18 offline regression tests**, all static no-network and no-order checks passed. Safe, synthetic-only artifact ID `12306918817`, SHA256 `b38b1120718c9dcf22a734eecbbb35c85bbfb673446f59c77c9f938c805d4053`, expires `2026-10-27T23:32:25Z`. The original four-source **30-day replay capsule** ID `12138239045` remains unexpired, digest `sha256:c9465d204b6a5c0b109807b06c352e46e12a50d8d717e953bd06ab3e9176036b`, expires `2026-11-17T13:42:08Z`.
- Code/test commits `837ad587ba74cd8a8ccdfa65bb97153c58ccc7e7`, `b4f0dd3452474efb421e80c849d25363ad6673d7`, `6439fd06d3936d92350ccd73c8d8d88ab7aa11b2`; workflow commit `248464cbb408611570a8aab40ed494a005953b0c`.

## Exact remaining independent proof threshold

1. Identify first-filed original **CFS statement**, recognized concept/account, currency/scale, column-axis, standalone 2022 July–September and 2021 July–September original numeric cells, not a current/revised download.
2. Independently establish **historical first public availability** (or independently attested conservative trading-session delay), and complete corrections’ first-publication chronology.
3. Validate official historical tradable securities/session calendar/issuer-security PIT, corporate actions, prices, order simulation, costs/taxes, Walk-Forward and independent Holdout under original Frozen H5/M20 criteria. Separate workrooms own KRX and broker data.
4. No preliminary 2022 Q3 CFS numeric feature, no result-based champion change, no HOLDOUT access and no REAL orders until all required source controls pass.

**Mandatory guards remain:** `original_2022_q3_three_month_cfs_value_verified=false`, `original_2021_comparator_three_month_cfs_value_verified=false`, `historical_issuer_security_pit_verified=false`, `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, no funds or permissions, `ORDERING=DISABLED`. Draft PR #412 stays unmerged. No change to historical market files, frozen strategy, Railway environment, Kiwoom keys or hourly task.
