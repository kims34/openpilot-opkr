"""Secondary timestamp verification must not promote private PIT source."""
import json
from copy import deepcopy
from pathlib import Path
import unittest

from research_v1_krx_2026_notice_asof_boundary import validate_report_asof as check

ROOT=Path(__file__).resolve().parent
NOTICE=ROOT/"evidence/krx/2026-10-14-krx-secondary-contemporaneous-notice-2026.json"
COUNT=ROOT/"evidence/krx/2026-10-14-krx-calendar-count-candidates.json"


class ReportedKRXClosureAsOf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=json.loads(NOTICE.read_text(encoding="utf-8"))
        cls.count=json.loads(COUNT.read_text(encoding="utf-8"))

    def test_contemporaneous_article_precedes_both_events(self):
        r=check(self.raw,decision_at_kst="2026-05-20T10:58:00+09:00")
        self.assertEqual(r["status"],"CONTEMPORANEOUS_SECONDARY_REPORT_ONLY_NO_KRX_PIT_ADMISSION")
        self.assertEqual(r["secondary_reporting_published_before_event_count"],2)
        self.assertEqual(r["secondary_news_asof_candidate_dates"],["2026-06-03","2026-07-17"])
        self.assertFalse(r["original_krx_notice_authenticated"])
        self.assertFalse(r["original_krx_published_at_confirmed"])
        self.assertFalse(r["private_receipt_day_level_matched"])
        self.assertFalse(r["2015_2026_pit_data_admitted"])

    def test_same_two_candidates_as_count_only_reference(self):
        self.assertEqual(self.raw["reported_cash_stock_market_closed_dates"],
                         self.count["2026_secondary_calendar_known_missing_officially_announced_closure_candidates"])
        self.assertEqual(self.raw["aggregate_184_unresolved_dates_remaining"],184)
        self.assertTrue(self.raw["securities_27_quarantined"] if "securities_27_quarantined" in self.raw else
                        not self.raw["quarantine_27_released"])

    def test_news_cannot_be_used_before_newspaper_publication(self):
        out=check(self.raw,decision_at_kst="2026-05-20T10:57:59+09:00")
        self.assertEqual(out["status"],"SECONDARY_REPORT_NOT_AVAILABLE_AS_OF_DECISION")
        self.assertEqual(out["secondary_news_asof_candidate_dates"],[])

    def test_original_notice_claim_forgery_fails_closed(self):
        for k in ("original_publication_pit_verified","private_volume_date_receipts_examined",
                  "krx_own_original_notice_document_retrieved","provider_source_receipt_day_set_equality_verified",
                  "source_pit_admitted","m20_profitability_authorized","quarantine_27_released"):
            with self.subTest(key=k):
                raw=deepcopy(self.raw);raw[k]=True
                self.assertEqual(check(raw,decision_at_kst="2026-06-01T09:00:00+09:00")["status"],
                                 "FAIL_CLOSED_BAD_SECONDARY_CLOSURE_EVIDENCE")

    def test_wrong_article_timestamp_or_nonkst_decision(self):
        for time in ("2026-05-20T10:58:00+00:00","2026-05-20T10:58:00","bad"):
            with self.subTest(time=time):
                raw=deepcopy(self.raw)
                raw["contemporaneous_report_source"]["article_published_at_kst"]=time
                self.assertEqual(check(raw,decision_at_kst="2026-06-01T09:00:00+09:00")["status"],
                                 "FAIL_CLOSED_BAD_SECONDARY_CLOSURE_EVIDENCE")
        self.assertEqual(check(self.raw,decision_at_kst="2026-06-01T00:00:00Z")["status"],
                         "FAIL_CLOSED_BAD_SECONDARY_CLOSURE_EVIDENCE")

    def test_late_report_cannot_assert_prospective_event(self):
        raw=deepcopy(self.raw)
        raw["contemporaneous_report_source"]["article_published_at_kst"]="2026-08-01T10:00:00+09:00"
        raw["contemporaneous_report_source"]["article_last_updated_at_kst"]="2026-08-01T10:00:00+09:00"
        self.assertEqual(check(raw,decision_at_kst="2026-09-01T00:00:00+09:00")["status"],
                         "FAIL_CLOSED_BAD_SECONDARY_CLOSURE_EVIDENCE")

    def test_secondary_sources_not_independent_original_krx(self):
        r=check(self.raw,decision_at_kst="2026-10-14T10:55:00+09:00")
        self.assertFalse(r["m20_performance_authorized"])
        self.assertFalse(r["27_quarantined_securities_released"])
        self.assertFalse(r["real_orders_authorized"])
        self.assertEqual(r["krx_provider_network_calls"],0)
        self.assertEqual(r["ordering"],"DISABLED")


if __name__=="__main__":
    unittest.main()
