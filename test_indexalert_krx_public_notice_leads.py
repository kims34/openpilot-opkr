"""Public market calendar lead audit; tests never claim private date matches."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from research_v1_krx_public_notice_leads import review_public_year_end_sources as check
MANIFEST=Path(__file__).resolve().parent/"evidence/krx/2026-10-14-krx-year-end-exchange-notice-candidates.json"


class PublicHolidayYearEndNoticeLeads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_separate_krx_kind_hosted_from_broker_sources(self):
        x=check(self.m)
        self.assertEqual(x["status"],"DATED_PUBLIC_NOTICE_LEADS_ONLY_NO_OFFICIAL_SESSION_PIT")
        self.assertEqual(x["recognized_sources"],6)
        self.assertEqual(x["krx_kind_hosted_years"],[2024])
        self.assertEqual(len(x["recorded_holiday_date_candidates"]),6)
        self.assertEqual(x["retrospective_or_undated_years"],[2019,2023,2025])

    def test_source_text_read_is_not_six_verified_primary_sources(self):
        x=check(self.m)
        self.assertEqual(x["declared_detail_page_text_read_years"],[2019,2022,2024,2025])
        self.assertEqual(x["declared_index_listing_only_years"],[2021])
        self.assertEqual(x["declared_detail_unavailable_years"],[2023])
        self.assertFalse(x["public_web_observations_independently_verified_by_this_function"])
        self.assertFalse(x["original_krx_source_document_verified"])

    def test_unreadable_detail_cannot_be_relabelled_as_read(self):
        m=deepcopy(self.m)
        m["reported_year_end_market_closure_candidates"][3]["public_page_observation_status"]="DIRECT_PAGE_TEXT_READ_BROKER"
        self.assertTrue(check(m)["status"].startswith("FAIL_CLOSED"))
        m=deepcopy(self.m)
        m["reported_year_end_market_closure_candidates"][4]["original_krx_notice_exact_first_publication_attested"]=True
        self.assertTrue(check(m)["status"].startswith("FAIL_CLOSED"))

    def test_2024_krx_notice_holiday_cannot_admit_market_receipts(self):
        x=check(self.m)
        self.assertIn("2024-12-31",x["recorded_holiday_date_candidates"])
        self.assertFalse(x["krx_raw_provider_empty_day_receipts_date_matched"])
        self.assertFalse(x["original_krx_source_document_verified"])
        self.assertEqual(x["calendar_dates_pit_admitted"],0)
        self.assertFalse(x["real_orders_authorized"])
        self.assertEqual(x["ordering"],"DISABLED")

    def test_fake_institution_krx_url_rejected(self):
        raw=deepcopy(self.m)
        raw["reported_year_end_market_closure_candidates"][4]["reference_url"]="https://example.com/2024/12/17/notice"
        self.assertTrue(check(raw)["status"].startswith("FAIL_CLOSED"))

    def test_wrong_krx_kind_url_date_rejected(self):
        raw=deepcopy(self.m)
        raw["reported_year_end_market_closure_candidates"][4]["source_date_kst"]="2024-12-18"
        self.assertTrue(check(raw)["status"].startswith("FAIL_CLOSED"))

    def test_2019_post_holiday_institution_reply_must_be_retrospective(self):
        x=check(self.m)
        self.assertIn(2019,x["retrospective_or_undated_years"])

    def test_wrong_original_verification_flags_fail_closed(self):
        for k in ("source_original_binary_document_bytes_downloaded",
                  "krx_original_notice_initial_publication_times_attested",
                  "underlying_krx_official_full_year_daily_calendar_verified",
                  "private_krx_source_receipts_date_level_compared",
                  "actual_profitability_backtest_authorized"):
            with self.subTest(field=k):
                m=deepcopy(self.m);m[k]=True
                self.assertTrue(check(m)["status"].startswith("FAIL_CLOSED"))

    def test_duplicate_years_or_fake_closed_weekends_fail_closed(self):
        m=deepcopy(self.m);m["reported_year_end_market_closure_candidates"][1]["year"]=2019
        self.assertTrue(check(m)["status"].startswith("FAIL_CLOSED"))
        m=deepcopy(self.m);m["reported_year_end_market_closure_candidates"][4]["closure_date"]="2024-12-28"
        self.assertTrue(check(m)["status"].startswith("FAIL_CLOSED"))

    def test_not_a_complete_exchange_calendar(self):
        x=check(self.m)
        self.assertFalse(x["official_complete_2015_2026_market_calendar_attested"])
        self.assertFalse(x["original_notice_first_publication_instant_verified"])
        self.assertFalse(x["archived_web_page_bytes_hash_verified"])
        self.assertEqual(x["provider_network_requests"],0)
        self.assertFalse(x["27_quarantined_securities_released"])
        self.assertFalse(x["profitability_testing_authorized"])


if __name__=="__main__":
    unittest.main()
