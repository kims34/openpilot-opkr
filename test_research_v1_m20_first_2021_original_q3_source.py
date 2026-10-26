"""Offline safety tests for fixed 2021 original first-edition DART source."""
import hashlib
import io
import os
import unittest
from unittest.mock import patch
import zipfile

import research_v1_m20_first_2021_original_q3_source as p

COMPANY = "00001234"
FIRST = "20211115000001"


def row(day="20211115", no="000001", name=p.TITLE, issuer=COMPANY, rm=""):
    return {"rcept_no": day+no, "rcept_dt": day,
            "corp_code": issuer, "report_nm": name, "rm": rm}


def index(rows=None):
    if rows is None:
        rows = [row()]
    return {"status": "000", "total_count": str(len(rows)),
            "total_page": "1", "page_no": "1", "list": rows}


def zip_document(markup=b"<DOCUMENT><TABLE><TR><TD>other</TD></TR></TABLE></DOCUMENT>"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("original.xml", markup)
    return buffer.getvalue()


class First2021OriginalTests(unittest.TestCase):
    def test_unique_earliest_original_validates_complete_page(self):
        receipt, n = p.earliest_first_receipt(index([
            row(rm="정"),
            row(day="20220110",name="[기재정정]"+p.TITLE),
        ]), issuer=COMPANY)
        self.assertEqual(receipt, FIRST)
        self.assertEqual(n, 2)

    def test_missing_first_original_denies_data(self):
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_SAME_DAY_OR_AMENDED_AMBIGUOUS"):
            p.earliest_first_receipt(index([
                row(name="[기재정정]"+p.TITLE)
            ]),issuer=COMPANY)

    def test_same_day_original_and_correction_fails_closed(self):
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_SAME_DAY_OR_AMENDED_AMBIGUOUS"):
            p.earliest_first_receipt(index([
                row(), row(no="000002",name="[기재정정]"+p.TITLE)
            ]),issuer=COMPANY)

    def test_duplicate_receipts_and_forged_corp_fails_closed(self):
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_LIST_ISSUER_OR_RECEIPT_INVALID"):
            p.earliest_first_receipt(index([row(),row()]),issuer=COMPANY)
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_LIST_ISSUER_OR_RECEIPT_INVALID"):
            p.earliest_first_receipt(index([row(issuer="99999999")]),issuer=COMPANY)

    def test_report_edition_unrecognized_or_withdrawn_denied(self):
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_UNCLASSIFIED_EDITION"):
            p.earliest_first_receipt(index([
                row(),row(day="20220110",name="[기타정정]"+p.TITLE)
            ]),issuer=COMPANY)
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_WITHDRAWN_ORIGINAL"):
            p.earliest_first_receipt(index([row(rm="철정")]),issuer=COMPANY)

    def test_incomplete_pagination_and_no_data_not_called_original(self):
        bad = index()
        bad["total_page"] = "2"
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_LIST_PAGINATION_NOT_EXHAUSTIVE"):
            p.earliest_first_receipt(bad,issuer=COMPANY)
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_FILING_LIST_UNAVAILABLE"):
            p.earliest_first_receipt({"status":"013"},issuer=COMPANY)

    def test_year_window_and_receipt_day_never_trusted_if_mismatched(self):
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_LIST_DATE_OR_WINDOW_INVALID"):
            p.earliest_first_receipt(index([row(day="20221001")]),issuer=COMPANY)
        fake = index()
        fake["list"][0]["rcept_no"]="20211116000001"
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_LIST_DATE_OR_WINDOW_INVALID"):
            p.earliest_first_receipt(fake,issuer=COMPANY)

    def test_second_original_does_not_get_silently_selected(self):
        with self.assertRaisesRegex(p.First2021Gap,"FIRST_2021_MULTIPLE_ORIGINAL_EDITION"):
            p.earliest_first_receipt(index([row(),row(day="20220111",name=p.TITLE)]),
                                      issuer=COMPANY)

    def test_only_three_official_calls_with_original_document(self):
        source = zip_document()
        calls=[]
        def fake(session,endpoint,params,zip_response=False):
            calls.append((endpoint,params.copy()))
            if endpoint=="corpCode.xml":return b"fake_registry"
            if endpoint=="list.json":return index()
            raise AssertionError("unapproved route")
        with (patch.object(p,"_official_get",side_effect=fake),
              patch.object(p,"_registry",return_value={p.COHORT[p.SLOT]:COMPANY}),
              patch.object(p,"_fetch_first_document",return_value=source) as getter):
            result = p.execute(object(),"PRIVATE_KEY")
        getter.assert_called_once()
        self.assertEqual(getter.call_args.args[2],FIRST)
        self.assertEqual(len(calls),2)
        self.assertEqual([x[0] for x in calls],["corpCode.xml","list.json"])
        self.assertEqual(calls[1][1]["bgn_de"],"20211001")
        self.assertEqual(calls[1][1]["end_de"],"20220228")
        self.assertEqual(calls[1][1]["last_reprt_at"],"N")
        self.assertEqual(result["2021_original_zip_sha256"],hashlib.sha256(source).hexdigest())
        self.assertEqual(result["source_status"],
                         "FIRST_SUBMITTED_2021_Q3_DOCUMENT_SOURCE_SHAPE_ONLY")
        self.assertFalse(result.get("m20_feature_pit_admitted", False))
        for secret in (FIRST,COMPANY,"PRIVATE_KEY","original.xml"):
            self.assertNotIn(secret,str(result))

    def test_source_table_label_is_never_original_fiscal_cell_proof(self):
        source=zip_document((
            "<DOCUMENT><TABLE><TR><TH>2021 3개월</TH></TR>"
            "<TR><TD>영업이익</TD><TD>1,000,000</TD></TR>"
            "</TABLE></DOCUMENT>"
        ).encode())
        with (patch.object(p,"_official_get",side_effect=[
                   b"fake_registry",index()]),
              patch.object(p,"_registry",return_value={p.COHORT[p.SLOT]:COMPANY}),
              patch.object(p,"_fetch_first_document",return_value=source)):
            x=p.execute(object(),"PRIVATE_KEY")
        self.assertGreaterEqual(x["2021_original_operating_label_table_candidates"],1)
        self.assertTrue(x["original_2021_q3_comparative_is_not_bound_to_2022"])
        self.assertNotIn("1,000,000",str(x))

    def test_empty_auth_means_no_official_requests(self):
        with (patch.dict(os.environ,{"OPENDART_API_KEY":""}),
              patch.object(p,"_official_get") as api):
            x=p.run(object())
        api.assert_not_called()
        self.assertEqual(x["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertFalse(x["original_2021_q3_three_month_cfs_profit_cell_verified"])
        self.assertEqual(x["ordering"],"DISABLED")

    def test_source_failure_redacts_key_and_financial_figures(self):
        with (patch.dict(os.environ,{"OPENDART_API_KEY":"PRIVATE_KEY"}),
              patch.object(p,"_official_get",side_effect=ValueError(
                    "PRIVATE_KEY 20211115000001 3,000,000"))):
            x=p.run(object())
        self.assertEqual(x["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        for t in ("PRIVATE_KEY",FIRST,"3,000,000"):
            self.assertNotIn(t,str(x))
        self.assertFalse(x["m20_performance_run_authorized"])
        self.assertFalse(x["real_orders_authorized"])


if __name__=="__main__":
    unittest.main()
