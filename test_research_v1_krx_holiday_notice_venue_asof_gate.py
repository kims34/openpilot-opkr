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
            original_kind_notice_url=(
                "https://kind.krx.co.kr/external/2022/02/10/000126/"
                "20220209001809/71985.htm"),
            public_report_at_kst="2022-02-10T10:50+09:00",
            signal_asof_kst="2022-03-08T15:00+09:00",
        )
        self.assertEqual(out["status"], "WRONG_MARKET_SCOPE")
        self.assertFalse(out["candidate_market_scope_consistent"])
        self.assertFalse(out["source_admitted"])

    def test_original_derivatives_notice_cannot_prove_equity(self):
        out = case(
            session_day="20211004",
            notice_market="DERIVATIVES",
            source_kind="KRX_PRIMARY_MARKET_NOTICE",
            original_kind_notice_url=(
                "https://kind.krx.co.kr/external/2021/09/27/000115/"
                "20210927000265/70868.htm"),
            public_report_at_kst="2021-09-28T12:00+09:00",
            signal_asof_kst="2021-10-01T15:00+09:00",
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

    def test_unpinned_primary_kospi_label_must_fail_closed(self):
        with self.assertRaisesRegex(CalendarNoticeGap, "URL_REQUIRED"):
            case(source_kind="KRX_PRIMARY_MARKET_NOTICE", notice_market="KOSPI")

    def test_pinned_primary_kospi_aug_2021_notice_is_venue_bound_only(self):
        out = case(
            session_day="20210816",
            required_market="KOSPI",
            source_kind="KRX_PRIMARY_MARKET_NOTICE",
            notice_market="KOSPI",
            original_kind_notice_url=(
                "https://kind.krx.co.kr/external/2021/08/04/000158/"
                "20210804000347/99340.htm"),
            # Synthetic time fixture; not an authenticated original filing instant.
            public_report_at_kst="2021-08-05T10:00+09:00",
            signal_asof_kst="2021-08-13T15:00+09:00",
        )
        self.assertTrue(out["original_kind_url_venue_date_profile_checked"])
        self.assertTrue(out["candidate_notice_may_be_considered_not_pit"])
        for key, denied in DENIED.items():
            self.assertEqual(out[key], denied, key)

    def test_2021_derivatives_primary_notice_cannot_cross_certify_kospi(self):
        url = ("https://kind.krx.co.kr/external/2021/09/27/000115/"
               "20210927000265/70868.htm")
        with self.assertRaisesRegex(CalendarNoticeGap,
                                    "MARKET_OR_DAY_CONFLICT"):
            case(
                session_day="20211004",
                source_kind="KRX_PRIMARY_MARKET_NOTICE",
                original_kind_notice_url=url,
                notice_market="KOSPI",
                public_report_at_kst="2021-09-28T12:00+09:00",
                signal_asof_kst="2021-10-01T15:00+09:00")
        honest = case(
            session_day="20211004",
            source_kind="KRX_PRIMARY_MARKET_NOTICE",
            original_kind_notice_url=url,
            notice_market="DERIVATIVES",
            public_report_at_kst="2021-09-28T12:00+09:00",
            signal_asof_kst="2021-10-01T15:00+09:00")
        self.assertEqual(honest["status"], "WRONG_MARKET_SCOPE")
        self.assertFalse(honest["original_exchange_market_status_pit_verified"])

    def test_primary_2021_oct_kosdaq_cash_notice_is_exact_venue_only(self):
        # New first-party original KRX KIND KOSDAQ notice, not a KOSPI notice.
        url = ("https://kind.krx.co.kr/external/2021/09/27/000113/"
               "20210915000217/71985.htm")
        for d in ("20211004", "20211011"):
            with self.subTest(day=d):
                source = dict(
                    session_day=d,
                    source_kind="KRX_PRIMARY_MARKET_NOTICE",
                    original_kind_notice_url=url,
                    notice_market="KOSDAQ",
                    # Synthetic date/time only; original posting clock not attested.
                    public_report_at_kst="2021-09-28T12:00+09:00",
                    signal_asof_kst="2021-10-01T15:00+09:00",
                )
                right = case(required_market="KOSDAQ", **source)
                self.assertTrue(right["original_kind_url_venue_date_profile_checked"])
                self.assertTrue(right["candidate_notice_may_be_considered_not_pit"])
                self.assertFalse(right["original_exchange_market_status_pit_verified"])
                self.assertFalse(right["independently_authenticated_publication_instant"])
                for key, denied in DENIED.items():
                    self.assertEqual(right[key], denied, key)
                wrong_venue = case(required_market="KOSPI", **source)
                self.assertEqual(wrong_venue["status"], "WRONG_MARKET_SCOPE")
                self.assertFalse(
                    wrong_venue["candidate_notice_may_be_considered_not_pit"])

    def test_primary_2021_oct_kosdaq_notice_cannot_be_forged_as_kospi(self):
        url = ("https://kind.krx.co.kr/external/2021/09/27/000113/"
               "20210915000217/71985.htm")
        base = dict(
            session_day="20211004",
            source_kind="KRX_PRIMARY_MARKET_NOTICE",
            original_kind_notice_url=url,
            notice_market="KOSDAQ",
            public_report_at_kst="2021-09-28T12:00+09:00",
            signal_asof_kst="2021-10-01T15:00+09:00",
        )
        for change in (
            {"notice_market": "KOSPI"},
            {"notice_market": "ALL_EQUITIES"},
            {"notice_market": "DERIVATIVES"},
            {"session_day": "20211005"},
            {"original_kind_notice_url": url + "?source=relabeled"},
            {"source_kind": "REPORTED_KRX_MARKET_NOTICE"},
        ):
            with self.subTest(change=change), self.assertRaises(CalendarNoticeGap):
                case(**dict(base, **change))

    def test_2022_kosdaq_election_kind_notice_cannot_be_relabelled_kospi(self):
        url = ("https://kind.krx.co.kr/external/2022/02/10/000126/"
               "20220209001809/71985.htm")
        with self.assertRaisesRegex(CalendarNoticeGap,
                                    "MARKET_OR_DAY_CONFLICT"):
            case(
                session_day="20220309",
                source_kind="KRX_PRIMARY_MARKET_NOTICE",
                original_kind_notice_url=url,
                notice_market="ALL_EQUITIES",
                public_report_at_kst="2022-02-11T12:00+09:00",
                signal_asof_kst="2022-03-08T15:00+09:00")
        honest = case(
            session_day="20220309",
            source_kind="KRX_PRIMARY_MARKET_NOTICE",
            original_kind_notice_url=url,
            notice_market="KOSDAQ",
            public_report_at_kst="2022-02-11T12:00+09:00",
            signal_asof_kst="2022-03-08T15:00+09:00")
        self.assertFalse(honest["candidate_notice_may_be_considered_not_pit"])
        self.assertEqual(honest["status"], "WRONG_MARKET_SCOPE")

    def test_pinned_kind_url_unknown_wrong_date_or_report_class_rejected(self):
        known = ("https://kind.krx.co.kr/external/2021/08/04/000158/"
                 "20210804000347/99340.htm")
        for override in (
            {"original_kind_notice_url": "https://kind.krx.co.kr/unknown"},
            {"original_kind_notice_url": known, "session_day": "20210817"},
            {"original_kind_notice_url": known,
             "source_kind": "REPORTED_KRX_MARKET_NOTICE"},
        ):
            with self.subTest(override=override), self.assertRaises(
                CalendarNoticeGap
            ):
                fields = dict(
                    session_day="20210816",
                    required_market="KOSPI",
                    source_kind="KRX_PRIMARY_MARKET_NOTICE",
                    notice_market="KOSPI",
                    public_report_at_kst="2021-08-05T10:00+09:00",
                    signal_asof_kst="2021-08-13T15:00+09:00",
                    original_kind_notice_url=known,
                )
                fields.update(override)
                classify_notice(**fields)

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
