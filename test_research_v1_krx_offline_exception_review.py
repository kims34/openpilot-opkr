"""No-network synthetic acceptance/negative tests for KRX exception review."""
import copy
import unittest

from research_v1_krx_offline_exception_review import (
    EvidenceNotAdmitted, review_exceptions,
)

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
D1 = "2018-01-01"
D2 = "2018-01-02"


def sample():
    return dict(
        exception_dates=[D1, D2],
        private_raw_days=[
            {"date": D1, "pair_sha256": SHA_A, "daily_row_count": 0},
            {"date": D2, "pair_sha256": SHA_B, "daily_row_count": 10},
        ],
        independent_calendar=[
            {"date": D1, "session": "CLOSED", "evidence_sha256": SHA_B,
             "source_kind": "INDEPENDENT_OFFICIAL_SESSION_CLAIM, "market_scope": "KOSPI_EQUITIES"},
            {"date": D2, "session": "OPEN", "evidence_sha256": SHA_C,
             "source_kind": "INDEPENDENT_OFFICIAL_SESSION_CLAIM, "market_scope": "KOSPI_EQUITIES"},
        ],
        price_anomalies=[
            {"date": D2, "security_token_sha256": SHA_A, "row_sha256": SHA_B,
             "nonpositive_ohlc": True},
        ],
        independent_security_days=[
            {"date": D2, "security_token_sha256": SHA_A, "state": "SUSPENDED",
             "evidence_sha256": SHA_C,
             "source_kind": "INDEPENDENT_OFFICIAL_SECURITY_DAY_CLAIM"},
        ],
    )


class OfflineExceptionReviewTest(unittest.TestCase):
    def test_matching_claims_still_deny_every_runtime_permission(self):
        data = review_exceptions(**sample())
        self.assertEqual(data["exception_weekdays_checked"], 2)
        self.assertEqual(data["calendar_claimed_closed"], 1)
        self.assertEqual(data["calendar_claimed_open"], 1)
        self.assertEqual(data["nonpositive_ohlc_rows_quarantined"], 1)
        self.assertEqual(data["calendar_unresolved"], 0)
        self.assertEqual(data["stock_states_unresolved"], 0)
        self.assertEqual(data["source_status"], "SOURCE_ONLY_RETROSPECTIVE_CLAIMS_NOT_PIT")
        self.assertEqual(data["ordering"], "DISABLED")
        for key in ("individual_tradability_verified", "calendar_original_publication_pit_verified",
                    "historical_corporate_actions_verified", "full_universe_source_admitted",
                    "m20_performance_run_authorized", "holdout_access_authorized",
                    "champion_change_authorized", "live_orders_authorized",
                    "funds_movement_authorized", "permissions_change_authorized",
                    "official_network_requests_made", "storage_mutated", "raw_security_data_emitted"):
            self.assertIs(data[key], False, key)

    def test_missing_claimed_calendar_is_not_backfilled_as_holiday(self):
        x = sample()
        x["independent_calendar"] = []
        x["independent_security_days"] = []
        result = review_exceptions(**x)
        self.assertEqual(result["calendar_unresolved"], 2)
        self.assertEqual(result["stock_states_unresolved"], 1)
        self.assertIs(result["individual_tradability_verified"], False)

    def test_suspended_or_listed_is_never_executable_price_evidence(self):
        for status in ("SUSPENDED", "DELISTED", "LISTED", "UNKNOWN"):
            x = sample()
            x["independent_security_days"][0]["state"] = status
            with self.subTest(status=status):
                y = review_exceptions(**x)
                self.assertEqual(y["nonpositive_ohlc_rows_quarantined"], 1)
                self.assertIs(y["live_orders_authorized"], False)

    def test_market_open_but_no_rows_is_source_gap_not_trading_day_proof(self):
        x = sample()
        x["independent_calendar"][0]["session"] = "OPEN"
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_market_closed_with_rows_is_not_holiday(self):
        x = sample()
        x["independent_calendar"][1]["session"] = "CLOSED"
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_wrong_market_source_or_status_rejected(self):
        for key, value in (("source_kind", "CURRENT_PRICE_INDEX"),
                           ("session", "TRADABLE"),
                           ("session", None), ("evidence_sha256", "bad")):
            x = sample()
            x["independent_calendar"][1][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(EvidenceNotAdmitted):
                review_exceptions(**x)

    def test_duplicate_or_unsorted_days_rejected(self):
        for bad in ([D1, D1], [D2, D1], [], ["2018-01-06"],
                    ["2018-02-30"], ["2026-01-01"], ["2018-01-1"]):
            x = sample()
            x["exception_dates"] = bad
            with self.subTest(dates=bad), self.assertRaises(EvidenceNotAdmitted):
                review_exceptions(**x)

    def test_source_days_must_match_exact_exception_scope(self):
        for change in ("remove", "extra", "duplicate"):
            x = sample()
            if change == "remove":
                x["private_raw_days"].pop()
            elif change == "extra":
                x["private_raw_days"].append({"date": "2018-01-03",
                                               "pair_sha256": SHA_C, "daily_row_count": 0})
            else:
                x["private_raw_days"].append(copy.deepcopy(x["private_raw_days"][0]))
            with self.subTest(change=change), self.assertRaises(EvidenceNotAdmitted):
                review_exceptions(**x)

    def test_date_scoped_stock_claim_must_match_quarantined_row(self):
        x = sample()
        x["independent_security_days"][0]["security_token_sha256"] = SHA_C
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_status_cannot_be_based_on_index_daily_row(self):
        x = sample()
        x["independent_security_days"][0]["source_kind"] = "KOSPI_INDEX_DAILY"
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_nonpositive_flag_requires_literal_true(self):
        for bad in (1, "true", None, False):
            x = sample()
            x["price_anomalies"][0]["nonpositive_ohlc"] = bad
            with self.subTest(flag=bad), self.assertRaises(EvidenceNotAdmitted):
                review_exceptions(**x)

    def test_row_count_boolean_or_negative_or_nonnumeric_rejected(self):
        for bad in (True, -1, 100001, "0"):
            x = sample()
            x["private_raw_days"][0]["daily_row_count"] = bad
            with self.subTest(count=bad), self.assertRaises(EvidenceNotAdmitted):
                review_exceptions(**x)

    def test_no_hidden_issuer_names_raw_prices_or_account_keys_accepted(self):
        x = sample()
        x["private_raw_days"][0]["stock_code"] = "SYNTHETIC"
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_duplicate_security_day_rejected(self):
        x = sample()
        x["price_anomalies"].append(copy.deepcopy(x["price_anomalies"][0]))
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_extra_calendar_claim_outside_scope_rejected(self):
        x = sample()
        x["independent_calendar"].append(
            {"date": "2018-01-03", "session": "CLOSED", "evidence_sha256": SHA_A,
             "source_kind": "INDEPENDENT_OFFICIAL_SESSION_CLAIM, "market_scope": "KOSPI_EQUITIES"})
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)


    def test_fixed_2026_prospective_failure_separate_from_90_day_history(self):
        x = sample()
        x["price_anomalies"][0]["date"] = "2026-09-28"
        x["independent_security_days"][0]["date"] = "2026-09-28"
        y = review_exceptions(**x)
        self.assertEqual(y["prospective_source_failure_session"], "2026-09-28")
        self.assertEqual(y["prospective_nonpositive_ohlc_rows_quarantined"], 1)
        self.assertEqual(y["historical_nonpositive_ohlc_rows_quarantined"], 0)
        self.assertEqual(y["exception_weekdays_checked"], 2)
        self.assertIs(y["prospective_input_source_pit_authenticated"], False)
        self.assertIs(y["retrospective_claims_independently_authenticated"], False)
        self.assertIs(y["live_orders_authorized"], False)

    def test_2026_prospective_price_row_without_stock_claim_stays_unresolved(self):
        x = sample()
        x["price_anomalies"][0]["date"] = "2026-09-28"
        x["independent_security_days"] = []
        y = review_exceptions(**x)
        self.assertEqual(y["stock_states_unresolved"], 1)
        self.assertEqual(y["prospective_nonpositive_ohlc_rows_quarantined"], 1)

    def test_only_actual_observed_prospective_failure_session_is_accepted(self):
        for day in ("2026-09-29", "2026-10-14", "2027-09-28",
                    "2026-09-27", "2023-09-28"):
            x = sample()
            x["price_anomalies"][0]["date"] = day
            x["independent_security_days"][0]["date"] = day
            with self.subTest(day=day), self.assertRaises(EvidenceNotAdmitted):
                review_exceptions(**x)

    def test_prospective_day_not_interpreted_as_historical_exchange_holiday(self):
        x = sample()
        x["independent_calendar"].append(
            {"date": "2026-09-28", "session": "CLOSED",
             "evidence_sha256": SHA_A,
             "source_kind": "INDEPENDENT_OFFICIAL_SESSION_CLAIM, "market_scope": "KOSPI_EQUITIES"})
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_other_historical_stock_day_without_raw_pair_is_rejected(self):
        x = sample()
        x["price_anomalies"][0]["date"] = "2019-03-04"
        x["independent_security_days"][0]["date"] = "2019-03-04"
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_2026_security_claim_cannot_match_historical_anomaly(self):
        x = sample()
        x["independent_security_days"][0]["date"] = "2026-09-28"
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)


    def test_prospective_only_2026_quarantine_without_fake_historical_receipts(self):
        x = sample()
        x["exception_dates"] = []
        x["private_raw_days"] = []
        x["independent_calendar"] = []
        x["price_anomalies"][0]["date"] = "2026-09-28"
        x["independent_security_days"][0]["date"] = "2026-09-28"
        y = review_exceptions(**x)
        self.assertEqual(y["exception_weekdays_checked"], 0)
        self.assertEqual(y["raw_source_day_hash_shape_checked"], 0)
        self.assertEqual(y["calendar_unresolved"], 0)
        self.assertEqual(y["prospective_nonpositive_ohlc_rows_quarantined"], 1)
        self.assertEqual(y["historical_nonpositive_ohlc_rows_quarantined"], 0)
        self.assertFalse(y["prospective_input_source_pit_authenticated"])
        self.assertFalse(y["individual_tradability_verified"])
        self.assertFalse(y["live_orders_authorized"])
        self.assertEqual(y["ordering"], "DISABLED")

    def test_prospective_only_without_security_status_remains_quarantined(self):
        x = sample()
        x["exception_dates"] = []
        x["private_raw_days"] = []
        x["independent_calendar"] = []
        x["price_anomalies"][0]["date"] = "2026-09-28"
        x["independent_security_days"] = []
        y = review_exceptions(**x)
        self.assertEqual(y["prospective_nonpositive_ohlc_rows_quarantined"], 1)
        self.assertEqual(y["stock_states_unresolved"], 1)
        self.assertFalse(y["full_universe_source_admitted"])

    def test_blank_historical_and_prospective_inputs_fail_closed(self):
        x = sample()
        for key in ("exception_dates", "private_raw_days",
                    "independent_calendar", "price_anomalies",
                    "independent_security_days"):
            x[key] = []
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_unscoped_historical_anomaly_cannot_bypass_prospective_only_gate(self):
        x = sample()
        x["exception_dates"] = []
        x["private_raw_days"] = []
        x["independent_calendar"] = []
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_historical_only_calendar_without_price_anomalies_still_allowed(self):
        x = sample()
        x["price_anomalies"] = []
        x["independent_security_days"] = []
        y = review_exceptions(**x)
        self.assertEqual(y["exception_weekdays_checked"], 2)
        self.assertEqual(y["prospective_nonpositive_ohlc_rows_quarantined"], 0)
        self.assertFalse(y["m20_performance_run_authorized"])


    def test_historical_zero_row_day_cannot_have_ohlc_anomaly(self):
        x = sample()
        x["price_anomalies"][0]["date"] = D1
        x["independent_security_days"][0]["date"] = D1
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_anomaly_count_cannot_exceed_captured_historical_rows(self):
        x = sample()
        x["private_raw_days"][1]["daily_row_count"] = 1
        x["price_anomalies"].append({
            "date": D2, "security_token_sha256": SHA_C,
            "row_sha256": SHA_A, "nonpositive_ohlc": True,
        })
        # This is two different stock/day anomalies but only one raw source
        # security row. The second anomaly cannot be sourced from that day.
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)

    def test_anomaly_count_equal_to_captured_rows_still_not_pit(self):
        x = sample()
        x["private_raw_days"][1]["daily_row_count"] = 1
        y = review_exceptions(**x)
        self.assertEqual(y["historical_nonpositive_ohlc_rows_quarantined"], 1)
        self.assertFalse(y["individual_tradability_verified"])
        self.assertFalse(y["full_universe_source_admitted"])
        self.assertFalse(y["m20_performance_run_authorized"])

    def test_missing_calendar_cannot_explain_impossible_historical_anomaly(self):
        x = sample()
        x["independent_calendar"] = []
        x["price_anomalies"][0]["date"] = D1
        x["independent_security_days"] = []
        with self.assertRaises(EvidenceNotAdmitted):
            review_exceptions(**x)


    def test_2021_added_exchange_closures_actual_dates_with_zero_rows_still_not_pit(self):
        x = sample()
        extra = ["2021-08-16", "2021-10-04", "2021-10-11"]
        x["exception_dates"] = extra
        x["private_raw_days"] = [
            {"date": d, "pair_sha256": SHA_A, "daily_row_count": 0}
            for d in extra
        ]
        x["independent_calendar"] = [
            {"date": d, "session": "CLOSED", "evidence_sha256": SHA_B,
             "source_kind": "INDEPENDENT_OFFICIAL_SESSION_CLAIM, "market_scope": "KOSPI_EQUITIES"}
            for d in extra
        ]
        x["price_anomalies"] = []
        x["independent_security_days"] = []
        result = review_exceptions(**x)
        self.assertEqual(result["krx_2021_later_added_closure_notice_date"], "2021-08-04")
        self.assertEqual(result["krx_2021_later_added_closure_dates_in_source_scope"], 3)
        self.assertEqual(result["krx_2021_later_added_closure_dates_missing_from_source_scope"], 0)
        self.assertFalse(result["historical_2021_official_calendar_fully_reconciled"])
        self.assertFalse(result["calendar_original_publication_pit_verified"])
        self.assertFalse(result["full_universe_source_admitted"])
        self.assertEqual(result["ordering"], "DISABLED")

    def test_2021_added_closure_with_trade_rows_is_invalid(self):
        x = sample()
        x["exception_dates"] = ["2021-08-16"]
        x["private_raw_days"] = [
            {"date": "2021-08-16", "pair_sha256": SHA_A, "daily_row_count": 1}
        ]
        x["independent_calendar"] = []
        x["price_anomalies"] = []
        x["independent_security_days"] = []
        with self.assertRaisesRegex(EvidenceNotAdmitted, "2021 KRX added market closure"):
            review_exceptions(**x)

    def test_2021_added_closure_cannot_be_claimed_as_open(self):
        x = sample()
        x["exception_dates"] = ["2021-10-04"]
        x["private_raw_days"] = [
            {"date": "2021-10-04", "pair_sha256": SHA_A, "daily_row_count": 0}
        ]
        x["independent_calendar"] = [
            {"date": "2021-10-04", "session": "OPEN", "evidence_sha256": SHA_C,
             "source_kind": "INDEPENDENT_OFFICIAL_SESSION_CLAIM, "market_scope": "KOSPI_EQUITIES"}
        ]
        x["price_anomalies"] = []
        x["independent_security_days"] = []
        with self.assertRaisesRegex(EvidenceNotAdmitted, "2021 added exchange closure"):
            review_exceptions(**x)

    def test_2021_late_closure_absent_from_small_scope_is_not_claimed_as_verified(self):
        x = sample()
        result = review_exceptions(**x)
        self.assertEqual(result["krx_2021_later_added_closure_dates_in_source_scope"], 0)
        self.assertEqual(result["krx_2021_later_added_closure_dates_missing_from_source_scope"], 3)
        self.assertFalse(result["historical_2021_official_calendar_fully_reconciled"])

    def test_2021_announcement_date_is_not_a_market_holiday(self):
        x = sample()
        x["exception_dates"] = ["2021-08-04"]
        x["private_raw_days"] = [
            {"date": "2021-08-04", "pair_sha256": SHA_A, "daily_row_count": 10}
        ]
        x["independent_calendar"] = [
            {"date": "2021-08-04", "session": "OPEN", "evidence_sha256": SHA_C,
             "source_kind": "INDEPENDENT_OFFICIAL_SESSION_CLAIM, "market_scope": "KOSPI_EQUITIES"}
        ]
        x["price_anomalies"] = []
        x["independent_security_days"] = []
        y = review_exceptions(**x)
        self.assertEqual(y["krx_2021_later_added_closure_dates_in_source_scope"], 0)
        self.assertEqual(y["calendar_claimed_open"], 1)
        self.assertFalse(y["historical_2021_official_calendar_fully_reconciled"])


    def test_derivatives_market_closure_cannot_certify_kospi_stock_session(self):
        x = sample()
        x["independent_calendar"][0]["market_scope"] = "KRX_DERIVATIVES"
        with self.assertRaisesRegex(
            EvidenceNotAdmitted, "non-equity or ambiguous market calendar"
        ):
            review_exceptions(**x)

    def test_issuer_etf_market_note_is_not_exchange_equity_calendar_receipt(self):
        x = sample()
        x["independent_calendar"][0]["market_scope"] = "ETF_ISSUER_DISCLOSURE"
        with self.assertRaisesRegex(
            EvidenceNotAdmitted, "non-equity or ambiguous market calendar"
        ):
            review_exceptions(**x)

    def test_omitted_equity_scope_or_nonstring_scope_rejected(self):
        for change in ("OMIT", None, 123, False, [], "KOSPI", "ALL_MARKETS"):
            x = sample()
            if change == "OMIT":
                del x["independent_calendar"][0]["market_scope"]
            else:
                x["independent_calendar"][0]["market_scope"] = change
            with self.subTest(scope=str(change)), self.assertRaises(
                EvidenceNotAdmitted
            ):
                review_exceptions(**x)

    def test_explicit_kospi_equities_calendar_still_remains_unverified_claim(self):
        x = sample()
        y = review_exceptions(**x)
        self.assertEqual(y["schema"], "indexalert-krx-offline-exception-review-v2")
        self.assertFalse(y["retrospective_claims_independently_authenticated"])
        self.assertFalse(y["calendar_original_publication_pit_verified"])
        self.assertFalse(y["full_universe_source_admitted"])
        self.assertFalse(y["live_orders_authorized"])
        self.assertEqual(y["ordering"], "DISABLED")


if __name__ == "__main__":
    unittest.main()
