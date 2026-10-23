"""Offline contract tests for date-only DART receipt vs actual calendar sessions."""
import json
import unittest
from unittest.mock import patch

import research_v1_m20_dart_receipt_date_floor as p


CALENDAR=["20221013","20221014","20221017","20221018"]

def check(receipt, trade, sessions=CALENDAR, *, source=True, calendar=True):
    return p.source_date_floor(receipt,trade,sessions,
        first_receipt_verified=source,
        calendar_official_historical_pit_verified=calendar)


class DateOnlyReceiptNoLookaheadTests(unittest.TestCase):
    def test_unsafe_same_day_trading_rejected_even_when_on_official_calendar(self):
        v=check("20221014","20221014")
        self.assertTrue(v["receipt_day_or_earlier_rejected"])
        self.assertTrue(v["trade_day_on_official_calendar"])
        self.assertFalse(v["after_receipt_trading_session_candidate"])
        self.assertFalse(v["source_public_availability_verified"])

    def test_prior_date_on_official_calendar_rejected(self):
        v=check("20221014","20221013")
        self.assertTrue(v["receipt_day_or_earlier_rejected"])
        self.assertFalse(v["after_receipt_trading_session_candidate"])

    def test_first_explicit_trading_session_after_friday_is_candidate_not_pit(self):
        v=check("20221014","20221017")
        self.assertTrue(v["after_receipt_trading_session_candidate"])
        self.assertEqual(v["source_date_gate_status"],
                         "AFTER_RECEIPT_TRADING_SESSION_CANDIDATE_ONLY")
        self.assertTrue(v["date_floor_does_not_admit_accounting_or_pit"])
        self.assertFalse(v["source_public_availability_verified"])

    def test_nontrading_day_cannot_be_inferred_from_weekday(self):
        v=check("20221014","20221016")
        self.assertFalse(v["trade_day_on_official_calendar"])
        self.assertFalse(v["after_receipt_trading_session_candidate"])

    def test_non_calendar_weekday_also_not_candidate(self):
        v=check("20221014","20221019")
        self.assertFalse(v["trade_day_on_official_calendar"])
        self.assertFalse(v["after_receipt_trading_session_candidate"])

    def test_missing_original_first_receipt_provenance_denies_all(self):
        v=check("20221014","20221017",source=False)
        self.assertEqual(v["source_date_gate_status"],
                         "FIRST_ORIGINAL_FILING_RECEIPT_NOT_ATTESTED")
        self.assertFalse(v["after_receipt_trading_session_candidate"])

    def test_missing_independent_official_calendar_attestation_denies(self):
        v=check("20221014","20221017",calendar=False)
        self.assertEqual(v["source_date_gate_status"],
                         "HISTORICAL_OFFICIAL_TRADING_CALENDAR_NOT_ATTESTED")
        self.assertFalse(v["after_receipt_trading_session_candidate"])

    def test_fake_attestation_truthy_strings_are_rejected(self):
        with self.assertRaisesRegex(p.ReceiptDateGap,"SOURCE_ATTESTATIONS_MUST_BE_BOOLEAN"):
            p.source_date_floor("20221014","20221017",CALENDAR,
                first_receipt_verified="yes",
                calendar_official_historical_pit_verified=True)

    def test_no_implicit_seconds_or_timezone_parsing(self):
        for fake in ("20221014153000","2022-10-14T15:30:00+09:00",
                     "2022-10-14","20221014Z", "", None, 20221014):
            with self.subTest(fake=fake),self.assertRaises(p.ReceiptDateGap):
                p.parse_day(fake)

    def test_invalid_dates_and_huge_or_unordered_calendars_rejected(self):
        for fake in ("20220229","20221301","20220001","19991231","22000101"):
            with self.subTest(fake=fake),self.assertRaises(p.ReceiptDateGap):
                p.parse_day(fake)
        for days in ([],["20221017","20221014"],["20221017","20221017"],
                     ["20221014"]*601,("20221014","20221017")):
            with self.subTest(days=len(days)),self.assertRaises(p.ReceiptDateGap):
                check("20221014","20221017",days)

    def test_unsupported_calendar_date_or_large_horizon_is_rejected(self):
        with self.assertRaisesRegex(p.ReceiptDateGap,
                                    "TRADE_DAY_OUTSIDE_SOURCE_TEST_HORIZON"):
            check("20221014","20250101")

    def test_trading_date_does_not_equal_calendar_first_only(self):
        v=check("20221014","20221018")
        self.assertTrue(v["after_receipt_trading_session_candidate"])
        self.assertFalse(v["source_public_availability_verified"])

    def test_offline_dry_run_leaks_no_fixture_dates_or_ids(self):
        result=p.dry_run()
        serialized=json.dumps(result)
        for private in ("20221014","20221017","20221013","rcept_no","corp_code"):
            self.assertNotIn(private, serialized)
        self.assertTrue(result["same_day_trading_from_rcept_dt_is_prohibited"])
        self.assertFalse(result["m20_feature_pit_admitted"])
        self.assertFalse(result["m20_performance_run_authorized"])
        self.assertFalse(result["real_orders_authorized"])
        self.assertFalse(result["independent_holdout_authorized"])
        self.assertFalse(result["source_first_public_release_instant_verified"])
        self.assertEqual(result["ordering"],"DISABLED")

    def test_no_web_or_provider_access_required_in_rule(self):
        with patch.object(p, "parse_day",wraps=p.parse_day) as parse:
            out=check("20221014","20221017")
        self.assertTrue(out["after_receipt_trading_session_candidate"])
        self.assertGreaterEqual(parse.call_count,5)


if __name__=="__main__":
    unittest.main()
