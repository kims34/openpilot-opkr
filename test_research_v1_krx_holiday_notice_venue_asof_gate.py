"""Synthetic adversarial tests: no provider calls, no data, no PIT admission."""
import unittest

from research_v1_krx_holiday_notice_venue_asof_gate import (
    CalendarNoticeGap, DENIED, classify_notice,
)

def case(**kwargs):
    fields = {
        "session_day": "20221230",
        "required_market": "KOSPI",
        "source_kind": "REPORTED_KRX_MARKET_NOTICE",
        "notice_market": "ALL_EQUITIES",
        # Contemporary Yonhap report of KRX year-end closure.
        "public_report_at_kst": "2022-12-15T10:31+09:00",
        "signal_asof_kst": "2022-12-29T15:00+09:00",
    }
    fields.update(kwargs)
    return classify_notice(**fields)

class MarketNoticeSourceScopeTest(unittest.TestCase):
    def test_later_published_2022_equity_notice_is_a_hint_not_original(self):
        out = case()
        self.assertEqual(out["status"], "CANDIDATE_ONLY_NOT_AUTHENTICATED")
        self.assertTrue(out["candidate_notice_may_be_considered_not_pit"])
        for key, denied in DENIED.items():
            self.assertEqual(out[key], denied, key)

    def test_same_day_signal_precedes_published_article(self):
        out = case(signal_asof_kst="2022-12-15T09:00+09:00")
        self.assertEqual(out["status"], "REPORT_NOT_AVAILABLE_BY_SIGNAL")
        self.assertFalse(out["candidate_notice_may_be_considered_not_pit"])

    def test_same_day_after_report_research_hint_only(self):
        out = case(signal_asof_kst="2022-12-15T10:32+09:00")
        self.assertTrue(out["reported_evidence_available_by_signal"])
        self.assertFalse(out["original_exchange_market_status_pit_verified"])

    def test_future_2022_year_end_notice_not_known_in_january(self):
        out = case(signal_asof_kst="2022-01-13T10:00+09:00")
        self.assertFalse(out["candidate_notice_may_be_considered_not_pit"])

    def test_krx_kind_kosdaq_election_notice_cannot_prove_kospi(self):
        out = case(
            session_day="20220309",
            notice_market="KOSDAQ",
            source_kind="KRX_PRIMARY_MARKET_NOTICE",
            public_report_at_kst="2022-02-10T10:50+09:00",
            signal_asof_kst="2022-03-08T15:00+09:00",
        )
        self.assertEqual(out["status"], "WRONG_MARKET_SCOPE")
        self.assertFalse(out["candidate_market_scope_consistent"])
        self.assertFalse(out["source_admitted"])

    def test_original_derivatives_notice_cannot_prove_equity(self):
        out = case(
            notice_market="DERIVATIVES",
            source_kind="KRX_PRIMARY_MARKET_NOTICE",
        )
        self.assertEqual(out["status"], "WRONG_MARKET_SCOPE")

    def test_government_holiday_is_not_market_closure_authority(self):
        out = case(
            source_kind="GOVERNMENT_PUBLIC_HOLIDAY",
            notice_market="GENERAL_PUBLIC",
        )
        self.assertEqual(out["status"], "NON_EXCHANGE_SOURCE")
        self.assertFalse(out["candidate_notice_may_be_considered_not_pit"])

    def test_issuer_product_disclosure_does_not_certify_market_holiday(self):
        out = case(source_kind="ISSUER_PRODUCT_DISCLOSURE", notice_market="KOSPI")
        self.assertEqual(out["status"], "NON_EXCHANGE_SOURCE")

    def test_reported_krx_notice_on_2021_august_four_is_not_preopen(self):
        data = {
            "session_day": "20210816",
            "required_market": "KOSPI",
            "source_kind": "REPORTED_KRX_MARKET_NOTICE",
            "notice_market": "ALL_EQUITIES",
            "public_report_at_kst": "2021-08-04T13:37+09:00",
        }
        out = classify_notice(
            **data, signal_asof_kst="2021-08-04T09:00+09:00")
        self.assertFalse(out["candidate_notice_may_be_considered_not_pit"])
        self.assertEqual(out["status"], "REPORT_NOT_AVAILABLE_BY_SIGNAL")
        later = classify_notice(
            **data, signal_asof_kst="2021-08-04T15:30+09:00")
        self.assertTrue(later["candidate_notice_may_be_considered_not_pit"])
        self.assertFalse(later["official_original_market_calendar_authenticated"])

    def test_exact_equity_market_primary_text_is_still_not_authenticated(self):
        z = case(source_kind="KRX_PRIMARY_MARKET_NOTICE", notice_market="KOSPI")
        self.assertEqual(z["status"], "CANDIDATE_ONLY_NOT_AUTHENTICATED")
        self.assertFalse(z["original_exchange_market_status_pit_verified"])

    def test_bad_types_and_market_labels_fail_closed(self):
        for kwargs in (
            {"required_market": "KRX"}, {"notice_market": "BOTH"},
            {"source_kind": "UNKNOWN"}, {"session_day": "20220230"},
            {"session_day": "2022-12-30"}, {"source_kind": True},
            {"notice_market": ["KOSPI"]},
            {"public_report_at_kst": "2022-12-15"},
            {"public_report_at_kst": "2022-12-15T10:31Z"},
            {"signal_asof_kst": "2022-12-15T10:31+00:00"},
            {"signal_asof_kst": "2022-12-15T09:60+09:00"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(CalendarNoticeGap):
                case(**kwargs)

    def test_future_publication_after_target_not_available(self):
        result = case(
            public_report_at_kst="2023-01-15T09:00+09:00",
            signal_asof_kst="2022-12-30T12:00+09:00"
        )
        self.assertFalse(result["candidate_notice_may_be_considered_not_pit"])

    def test_historical_signal_after_session_is_invalid(self):
        with self.assertRaisesRegex(CalendarNoticeGap, "AFTER_TARGET_SESSION"):
            case(signal_asof_kst="2023-01-02T12:00+09:00")

if __name__ == "__main__":
    unittest.main()
