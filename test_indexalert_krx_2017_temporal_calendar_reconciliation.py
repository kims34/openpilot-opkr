"""Tests 2017 exchange holiday late announcement without forward-looking PIT leak."""
import json
from pathlib import Path
from copy import deepcopy
import unittest

from research_v1_krx_2017_temporal_calendar_reconciliation import (
    reconcile_2017_public_sources as check,
)
BASE=Path(__file__).resolve().parent
DOC=BASE/"evidence/krx/2026-10-14-krx-2017-holiday-temporal-source-reconciliation.json"
ORIGINAL=BASE/"evidence/krx/2026-10-13-krx-market-source-pit-boundaries.json"


class Historic2017CalendarAsOfBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads(DOC.read_text(encoding="utf-8"))
        worker=json.loads(ORIGINAL.read_text(encoding="utf-8"))
        cls.year=next(r for r in worker["offline_verification"]["per_year"]
                      if r["year"]==2017)

    def check_at(self,at,doc=None):
        return check(doc or self.manifest,self.year,decision_at_kst=at)

    def test_before_july_16_snapshot_no_document(self):
        r=self.check_at("2017-07-16T15:44:59+09:00")
        self.assertEqual(r["status"],"JULY_EXPORT_MIRROR_NOT_YET_AVAILABLE")
        self.assertEqual(r["asof_source_calendar_closures_candidate"],[])

    def test_july_source_snapshot_16_does_not_infer_october2(self):
        r=self.check_at("2017-07-17T09:00:00+09:00")
        self.assertEqual(r["status"],"JULY_16_SECONDARY_SNAPSHOT_ONLY")
        self.assertEqual(len(r["asof_source_calendar_closures_candidate"]),16)
        self.assertNotIn("2017-10-02",r["asof_source_calendar_closures_candidate"])
        self.assertEqual(r["private_worker_reported_empty_count"],17)
        self.assertFalse(r["candidate_count_matches_worker_aggregate"])

    def test_september5_government_notice_is_not_exchange_original(self):
        r=self.check_at("2017-09-06T09:00:00+09:00")
        self.assertEqual(r["status"],"NEW_GOVERNMENT_HOLIDAY_PENDING_EXCHANGE_CONFIRMATION")
        self.assertEqual(len(r["asof_source_calendar_closures_candidate"]),16)
        self.assertTrue(r["new_2017_10_02_status"].startswith("GOVERNMENT"))

    def test_september18_exchange_news_has_unknown_intraday_release(self):
        r=self.check_at("2017-09-18T23:59:59+09:00")
        self.assertEqual(r["status"],"NEW_GOVERNMENT_HOLIDAY_PENDING_EXCHANGE_CONFIRMATION")
        self.assertNotIn("2017-10-02",r["asof_source_calendar_closures_candidate"])

    def test_september19_candidate_adds_exactly_october2(self):
        r=self.check_at("2017-09-19T00:00:00+09:00")
        self.assertEqual(r["status"],"2017_17_CANDIDATES_AGREE_WITH_PRIVATE_YEARLY_COUNT_ONLY")
        self.assertEqual(len(r["asof_source_calendar_closures_candidate"]),17)
        self.assertIn("2017-10-02",r["asof_source_calendar_closures_candidate"])
        self.assertTrue(r["candidate_count_matches_worker_aggregate"])
        self.assertFalse(r["source_2017_private_receipt_dates_matched"])
        self.assertFalse(r["original_krx_2017_final_calendar_pit_admitted"])
        self.assertEqual(r["ordering"],"DISABLED")

    def test_secondary_17_dates_do_not_authorize_27_release_or_m20(self):
        r=self.check_at("2026-10-14T12:06:00+09:00")
        self.assertFalse(r["27_problem_securities_released"])
        self.assertFalse(r["holdout_authorized"])
        self.assertFalse(r["profitability_run_authorized"])
        self.assertFalse(r["real_orders_authorized"])

    def test_prior_july_snapshot_forgery_refused(self):
        m=deepcopy(self.manifest)
        m["archived_july_publication"]["visible_text_tabled_2017_weekday_closures"].append("2017-10-02")
        self.assertTrue(self.check_at("2017-10-03T00:00:00+09:00",m)["status"].startswith("FAIL_CLOSED"))

    def test_gov_notice_does_not_prove_original_krx(self):
        m=deepcopy(self.manifest)
        m["date_change"]["original_KRX_notice_bytes_or_first_publication_instant_authenticated"]=True
        self.assertTrue(self.check_at("2017-10-03T00:00:00+09:00",m)["status"].startswith("FAIL_CLOSED"))

    def test_mismatch_original_2017_count_refused(self):
        m=deepcopy(self.year)
        m["unverified_exchange_calendar_or_source_gap_days"]=16
        self.assertTrue(check(self.manifest,m,decision_at_kst="2017-10-03T09:00:00+09:00")["status"].startswith("FAIL_CLOSED"))

    def test_snapshot_date_leak_after_original_document_missing(self):
        m=deepcopy(self.manifest)
        m["archived_july_publication"]["original_export_xls_bytes_downloaded_and_SHA_authenticated"]=True
        self.assertTrue(self.check_at("2017-10-03T00:00:00+09:00",m)["status"].startswith("FAIL_CLOSED"))


if __name__=="__main__":
    unittest.main()
