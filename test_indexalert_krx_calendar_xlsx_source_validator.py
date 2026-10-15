"""Synthetic XLSX byte-level source binding with no third party deps/network."""
import hashlib
from io import BytesIO
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from research_v1_krx_calendar_xlsx_source_validator import read_holiday_source_xlsx as check
from research_v1_krx_official_calendar_input_preflight import SOURCE_PAGE

S="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DATE="2026-06-03"
OTHER="2026-07-17"
def make_book(d1=DATE,d2=OTHER,duplicate=False,formula=False,serial=False,
              bad_style=False,second_sheet=False,extra_path=None,external=False,
              hidden=False,mislinked=False,hidden_row=False,hidden_column=False,
              filtered=False,merged=False,zero_height=False,row_ht_zero=False):
    def cell(addr, data, num=False, style=""):
        if num:
            return f'<c r="{addr}"{style}><v>{data}</v></c>'
        return f'<c r="{addr}" t="inlineStr"><is><t>{data}</t></is></c>'
    hdr=''.join(cell(a+"1",v) for a,v in (("A","일자"),("B","요일"),("C","비고")))
    a2=cell("A2","46176",num=True,style=' s="1"' if not bad_style else ' s="0"') if serial else cell("A2",d1)
    if formula:
        a2='<c r="A2"><f>DATE(2026,6,3)</f><v>46176</v></c>'
    r2=a2+cell("B2","수")+cell("C2","선거일")
    r3=cell("A3",d1 if duplicate else d2)+cell("B3","수" if duplicate else "금")+cell("C3","휴장")
    row_attr=' hidden="1"' if hidden_row else (' ht="0"' if row_ht_zero else "")
    cols='<cols><col min="1" max="1" hidden="true"/></cols>' if hidden_column else ""
    filt='<autoFilter ref="A1:C3"/>' if filtered else ""
    merge='<mergeCells count="1"><mergeCell ref="A1:B1"/></mergeCells>' if merged else ""
    fmt='<sheetFormatPr zeroHeight="true"/>' if zero_height else ""
    xml=(f'<worksheet xmlns="{S}">{fmt}{cols}<sheetData>'
         f'<row r="1">{hdr}</row><row r="2"{row_attr}>{r2}</row>'
         f'<row r="3">{r3}</row></sheetData>{filt}{merge}</worksheet>')
    state=' state="hidden"' if hidden else ""
    sheet2='<sheet name="Second" sheetId="2"/>' if second_sheet else ""
    w=f'<workbook xmlns="{S}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Holidays" sheetId="1" r:id="rId1"{state}/>{sheet2}</sheets></workbook>'
    styles=f'<styleSheet xmlns="{S}"><cellXfs count="2"><xf numFmtId="0"/><xf numFmtId="14"/></cellXfs></styleSheet>'
    content_types='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>'
    with BytesIO() as output:
        with ZipFile(output,mode="w",compression=ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml",content_types)
            z.writestr("xl/workbook.xml",w)
            z.writestr("xl/styles.xml",styles)
            z.writestr("xl/worksheets/sheet1.xml",xml)
            if extra_path:
                z.writestr(extra_path,b"x")
            rel_target = "worksheets/sheet2.xml" if mislinked else "worksheets/sheet1.xml"
            target_mode = ' TargetMode="External"' if external else ""
            if external:
                rel_target = "https://example.com/evil.xml"
            z.writestr("xl/_rels/workbook.xml.rels",
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"'
                + target_mode + ' Target="' + rel_target + '"/></Relationships>')
        return output.getvalue()


def claim(raw,dates=None):
    return {"source_kind":"KRX_HUMAN_EXPORTED_HOLIDAY_SCHEDULE",
            "market":"KOSPI_CASH_EQUITIES","year":2026,
            "source_page_url":SOURCE_PAGE,
            "downloaded_at_utc":"2026-10-14T00:00:00Z",
            "source_document_sha256":hashlib.sha256(raw).hexdigest(),
            "calendar_closed_days":dates if dates is not None else [DATE,OTHER]}


class XlsxSourceRows(unittest.TestCase):
    def test_actual_xlsx_date_rows_match_original_pinned_bytes(self):
        raw=make_book()
        x=check(raw,claim(raw),2026)
        self.assertEqual(x["status"],"SOURCE_XLSX_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT")
        self.assertTrue(x["xlsx_source_rows_match_claim"])
        self.assertEqual(x["dates"],[DATE,OTHER])
        self.assertFalse(x["original_krx_provider_authenticated"])
        self.assertFalse(x["exchange_session_source_admitted"])
        self.assertFalse(x["live_orders_authorized"])

    def test_claimed_dates_mismatched_even_though_same_sha(self):
        raw=make_book()
        x=check(raw,claim(raw,[DATE,"2026-07-16"]),2026)
        self.assertTrue(x["status"].startswith("FAIL_CLOSED"))

    def test_binary_tampering_against_sha_fails(self):
        raw=make_book()
        self.assertTrue(check(raw+b"garbage",claim(raw),2026)["status"].startswith("FAIL_CLOSED"))

    def test_duplicate_holiday_rejected(self):
        raw=make_book(duplicate=True)
        self.assertTrue(check(raw,claim(raw),2026)["status"].startswith("FAIL_CLOSED"))

    def test_formula_cell_never_accepted_as_original(self):
        raw=make_book(formula=True)
        self.assertTrue(check(raw,claim(raw),2026)["status"].startswith("FAIL_CLOSED"))

    def test_hidden_and_multiple_sheets_fail_closed(self):
        for opts in ({"hidden":True},{"second_sheet":True}):
            raw=make_book(**opts)
            self.assertTrue(check(raw,claim(raw),2026)["status"].startswith("FAIL_CLOSED"))

    def test_unsafe_traversal_and_external_relationships_fail(self):
        for opts in ({"extra_path":"../../secret.xml"},{"external":True},
                     {"extra_path":"xl/externalLinks/link1.xml"},{"mislinked":True}):
            raw=make_book(**opts)
            self.assertTrue(check(raw,claim(raw),2026)["status"].startswith("FAIL_CLOSED"))

    def test_invisible_or_filtered_date_rows_cannot_pass_human_visible_source_claim(self):
        # A sidecar can accurately list XML rows but still misrepresent
        # what an operator sees if a KRX holiday row/column was hidden.
        for opts in ({"hidden_row":True},{"hidden_column":True},
                     {"filtered":True},{"merged":True},
                     {"zero_height":True},{"row_ht_zero":True}):
            with self.subTest(opts=opts):
                raw=make_book(**opts)
                result=check(raw,claim(raw),2026)
                self.assertEqual(
                    result["status"],
                    "FAIL_CLOSED_XLSX_SOURCE_ROWS_UNTRUSTED_OR_UNSUPPORTED")
                self.assertFalse(result["exchange_session_source_admitted"])
                self.assertEqual(result["parsed_source_days"],0)

    def test_normal_visible_xlsx_still_reconciles_without_metadata_claiming_pit(self):
        raw=make_book()
        result=check(raw,claim(raw),2026)
        self.assertEqual(result["status"],
                         "SOURCE_XLSX_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT")
        self.assertFalse(result["original_publication_pit_attested"])

    def test_excel_serial_requires_date_style(self):
        raw=make_book(serial=True)
        x=check(raw,claim(raw),2026)
        # Serial 46176 is the Excel serial date for 2026-06-03.
        self.assertEqual(x["status"],"SOURCE_XLSX_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT")
        raw=make_book(serial=True,bad_style=True)
        self.assertTrue(check(raw,claim(raw),2026)["status"].startswith("FAIL_CLOSED"))

    def test_xlsx_wrong_year_or_opaque_xls_rejected(self):
        raw=make_book()
        self.assertTrue(check(raw,claim(raw),2025)["status"].startswith("FAIL_CLOSED"))
        self.assertTrue(check(b"\xd0\xcf\x11\xe0"+b"x"*90,claim(raw),2026)["status"].startswith("FAIL_CLOSED"))

    def test_source_checksum_not_source_authentication(self):
        raw=make_book()
        x=check(raw,claim(raw),2026)
        self.assertEqual(x["ordering"],"DISABLED")
        self.assertFalse(x["original_publication_pit_attested"])
        self.assertEqual(x["network_requests_made"],False)
        self.assertFalse(x["27_problem_securities_released"])

if __name__=="__main__":
    unittest.main()
