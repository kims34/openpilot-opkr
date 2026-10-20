"""No-network first-vs-corrected edition date-only historical PIT tests."""
import json
import unittest
from unittest.mock import patch

import research_v1_m20_original_correction_asof_floor as p

FIRST="20221014"
CORRECTED="20231214"
CAL=["20221013","20221014","20221017","20231214","20231215"]


def check(decision, *, origin=FIRST, corrected=CORRECTED, sessions=CAL,
          first_ok=True, corrected_ok=True, index_ok=True, calendar_ok=True):
    return p.edition_date_floor(
        original_receipt_day=origin, correction_receipt_day=corrected,
        trade_session_day=decision, official_historical_sessions=sessions,
        original_first_filing_verified=first_ok,
        later_correction_receipt_verified=corrected_ok,
        correction_index_complete_for_window=index_ok,
        calendar_official_historical_pit_verified=calendar_ok,
    )


class DateOnlyOriginalCorrectedAsOfTests(unittest.TestCase):
    def test_first_receipt_day_never_available_for_trading(self):
        out=check(FIRST)
        self.assertEqual(out["date_only_edition_scope"],"ON_OR_BEFORE_FIRST_RECEIPT_REJECTED")
        self.assertFalse(out["original_edition_date_scope_candidate"])
        self.assertFalse(out["corrected_edition_date_scope_candidate"])

    def test_pre_original_trade_rejected(self):
        out=check("20221013")
        self.assertFalse(out["original_edition_date_scope_candidate"])
        self.assertFalse(out["source_first_public_availability_verified"])

    def test_original_between_first_and_correction_only_date_candidate(self):
        out=check("20221017")
        self.assertEqual(out["date_only_edition_scope"],
                         "ORIGINAL_EDITION_DATE_SCOPE_CANDIDATE_ONLY")
        self.assertTrue(out["original_edition_date_scope_candidate"])
        self.assertFalse(out["corrected_edition_date_scope_candidate"])
        self.assertFalse(out["m20_feature_pit_admitted"])

    def test_correction_day_never_immediately_admitted(self):
        out=check(CORRECTED)
        self.assertEqual(out["date_only_edition_scope"],"CORRECTION_RECEIPT_DAY_REJECTED")
        self.assertFalse(out["corrected_edition_date_scope_candidate"])
        self.assertFalse(out["original_edition_date_scope_candidate"])

    def test_future_session_only_corrected_edition_could_apply(self):
        out=check("20231215")
        self.assertEqual(out["date_only_edition_scope"],
                         "CORRECTED_EDITION_DATE_SCOPE_CANDIDATE_ONLY")
        self.assertFalse(out["original_edition_date_scope_candidate"])
        self.assertTrue(out["corrected_edition_date_scope_candidate"])
        self.assertFalse(out["real_orders_authorized"])
        self.assertFalse(out["m20_performance_run_authorized"])

    def test_both_versions_never_coeligible(self):
        for trade in (FIRST,"20221017",CORRECTED,"20231215"):
            with self.subTest(trade=trade):
                out=check(trade)
                self.assertTrue(out["correction_and_original_never_coeligible"])

    def test_missing_complete_revision_index_denies_all_versions(self):
        for trade in ("20221017","20231215"):
            with self.subTest(trade=trade):
                out=check(trade,index_ok=False)
                self.assertEqual(out["date_only_edition_scope"],
                                 "EDITION_CALENDAR_OR_LINEAGE_UNATTESTED")
                self.assertFalse(out["original_edition_date_scope_candidate"])
                self.assertFalse(out["corrected_edition_date_scope_candidate"])

    def test_missing_correction_provenance_cannot_allow_original_either(self):
        out=check("20221017",corrected_ok=False)
        self.assertFalse(out["original_edition_date_scope_candidate"])
        self.assertEqual(out["date_only_edition_scope"],
                         "EDITION_CALENDAR_OR_LINEAGE_UNATTESTED")

    def test_missing_original_receipt_provenance_denies_later_editions(self):
        out=check("20231215",first_ok=False)
        self.assertFalse(out["corrected_edition_date_scope_candidate"])

    def test_unverified_official_historical_calendar_denies_both(self):
        for trade in ("20221017","20231215"):
            with self.subTest(trade=trade):
                out=check(trade,calendar_ok=False)
                self.assertFalse(out["original_edition_date_scope_candidate"])
                self.assertFalse(out["corrected_edition_date_scope_candidate"])

    def test_nontrading_weekday_not_in_calendar_never_assumed_open(self):
        out=check("20231218")
        self.assertEqual(out["date_only_edition_scope"],"NO_ELIGIBLE_ATTESTED_SESSION")
        self.assertFalse(out["corrected_edition_date_scope_candidate"])

    def test_same_day_collision_or_reversed_correction_blocked(self):
        for corrected in ("20221014","20221013","20301214"):
            with self.subTest(corrected=corrected), self.assertRaisesRegex(
                p.EditionFloorGap,"EDITION_DATE_ORDER_OR_SCOPE_INVALID"
            ):
                check("20221017",corrected=corrected)

    def test_malformed_receipt_date_or_timestamp_rejected(self):
        for wrong in ("2022-10-14","20221014153000","20220230"):
            with self.subTest(wrong=wrong),self.assertRaisesRegex(
                p.EditionFloorGap,"EDITION_DAY_SHAPE_INVALID"
            ):
                check("20221017",origin=wrong)

    def test_fake_bool_attestations_are_not_accepted(self):
        with self.assertRaisesRegex(p.EditionFloorGap,"EDITION_ATTESTATION_TYPE_INVALID"):
            check("20221017",calendar_ok="yes")

    def test_invalid_unsorted_official_calendar_cannot_pass(self):
        with self.assertRaisesRegex(p.EditionFloorGap,"ORIGINAL_DATE_FLOOR_OR_CALENDAR_INVALID"):
            check("20221017",sessions=["20221017","20221014"])

    def test_corrected_late_trade_horizon_relative_to_correction_only(self):
        out=check("20231215")
        self.assertTrue(out["corrected_edition_date_scope_candidate"])
        with self.assertRaisesRegex(p.EditionFloorGap,
                                    "CORRECTION_DATE_FLOOR_OR_CALENDAR_INVALID"):
            check("20260102",sessions=CAL+["20260102"])

    def test_safe_public_outputs_do_not_contain_dates_ids_or_amounts(self):
        result=p.dry_run()
        serialized=json.dumps(result,sort_keys=True)
        for secret in (FIRST,CORRECTED,"20231215","20221017",
                       "corp_code","rcept_no","100,000"):
            self.assertNotIn(secret,serialized)
        self.assertTrue(result["synthetic_original_window_test_passed"])
        self.assertTrue(result["synthetic_correction_window_test_passed"])
        self.assertFalse(result["original_2022_q3_three_month_cfs_value_verified"])
        self.assertFalse(result["m20_feature_pit_admitted"])
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertFalse(result["independent_holdout_authorized"])
        self.assertFalse(result["real_orders_authorized"])
        self.assertEqual(result["ordering"],"DISABLED")

    def test_declared_rule_does_not_require_live_network(self):
        with patch.object(p,"source_date_floor",wraps=p.source_date_floor) as f:
            out=check("20231215")
        self.assertTrue(out["corrected_edition_date_scope_candidate"])
        self.assertEqual(f.call_count,1)


if __name__=="__main__":
    unittest.main()
