"""KRX-hosted 2017 PDF source event metadata never admits trading PIT."""
import json
from copy import deepcopy
from pathlib import Path
import unittest
from research_v1_krx_official_2017_notice_crosscheck import inspect_official_2017_notice as verify
ROOT=Path(__file__).resolve().parent
FILE=ROOT/"evidence/krx/2026-10-14-krx-official-2017-year-end-market-pdf-source.json"
TEMPORAL=ROOT/"evidence/krx/2026-10-14-krx-2017-holiday-temporal-source-reconciliation.json"

class YearEndKRX2017PDFSourceCandidates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads(FILE.read_text(encoding="utf-8"))
        cls.july=json.loads(TEMPORAL.read_text(encoding="utf-8"))[
            "archived_july_publication"]["visible_text_tabled_2017_weekday_closures"]
    def test_official_2017_market_close_and_next_open(self):
        x=verify(self.m,july_2017_candidate=self.july)
        self.assertEqual(x["status"],"FIRST_PARTY_KRX_DOMAIN_YEAR_END_EVENT_CORROBORATION_ONLY")
        self.assertEqual(x["listed_2017_cash_close_dates"],["2017-12-29"])
        self.assertEqual(x["next_year_delayed_open_dates"],["2018-01-02"])
        self.assertTrue(x["2017_year_end_date_present_in_july_secondary"])
        self.assertFalse(x["complete_year_market_calendar_verified"])
    def test_do_not_mislabel_delayed_open_as_holiday(self):
        m=deepcopy(self.m);m["listed_cash_market_events"][2]["event"]="YEAR_END_CLOSED"
        self.assertTrue(verify(m,july_2017_candidate=self.july)["status"].startswith("FAIL_CLOSED"))
        m=deepcopy(self.m);m["listed_cash_market_events"][2]["regular_market_open_kst"]="09:00"
        self.assertTrue(verify(m,july_2017_candidate=self.july)["status"].startswith("FAIL_CLOSED"))
    def test_must_restrict_KOSPI_cash_not_OTC_CCP(self):
        m=deepcopy(self.m);m["listed_cash_market_events"][1]["market"]="KRX_OTC_CCP"
        self.assertTrue(verify(m,july_2017_candidate=self.july)["status"].startswith("FAIL_CLOSED"))
    def test_unverified_PDF_bytes_cannot_be_self_attested(self):
        for key in ["original_pdf_binary_sha256_attested",
                    "original_pdf_initial_publication_instant_attested",
                    "original_notice_revision_lineage_complete",
                    "original_2017_private_source_empty_day_receipts_read"]:
            m=deepcopy(self.m);m[key]=True
            self.assertTrue(verify(m,july_2017_candidate=self.july)["status"].startswith("FAIL_CLOSED"))
    def test_july_2017_mirror_is_not_updated_asif_october_holiday_preannounced(self):
        july=[*self.july,"2017-10-02"]
        self.assertTrue(verify(self.m,july_2017_candidate=july)["status"].startswith("FAIL_CLOSED"))
    def test_no_performance_holdout_trading_permissions(self):
        x=verify(self.m,july_2017_candidate=self.july)
        self.assertFalse(x["original_pdf_first_publication_pit_verified"])
        self.assertFalse(x["2017_original_private_empty_day_receipts_matched"])
        self.assertFalse(x["27_securities_released"])
        self.assertFalse(x["m20_performance_authorized"])
        self.assertFalse(x["sealed_holdout_authorized"])
        self.assertFalse(x["real_orders_authorized"])
        self.assertEqual(x["ordering"],"DISABLED")
        self.assertEqual(x["authenticated_KRX_provider_calls"],0)

if __name__=="__main__":
    unittest.main()
