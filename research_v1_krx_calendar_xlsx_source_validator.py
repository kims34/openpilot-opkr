"""Strict *offline* XLSX source-ROW holiday schedule comparison.

This checks the actual bytes of ONE plainly readable XLSX worksheet against
the independently pinned original source digest and sidecar date claims.
Only a narrow, testable XLSX subset is accepted; unsupported or ambiguous
workbooks, formulas, hidden worksheets, external relationships, macros,
unsafe zip entries, and unknown date formats FAIL CLOSED, not "best effort".

This cannot establish that a file was actually provided by KRX, document
licensing, original year-specific historical publication, cash-market scope
or original PIT eligibility. No network, private KRX price reads or orders.
"""
from __future__ import annotations

from datetime import date, timedelta
import io
import re
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET

from research_v1_krx_official_calendar_input_preflight import normalize_calendar_export_claim

SS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
PKGREL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PACKAGE_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
SHEET_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_XML = 8_000_000
MAX_UNCOMPRESSED = 12_000_000
ALLOWED_PREFIXES = ("xl/theme/", "docProps/")
ALLOWED = {
    "[Content_Types].xml", "_rels/.rels", "xl/workbook.xml",
    "xl/_rels/workbook.xml.rels", "xl/styles.xml",
    "xl/sharedStrings.xml", "xl/worksheets/sheet1.xml",
}
BUILTIN_DATE_FORMAT_IDS = {14, 15, 16, 17, 22}


def refuse():
    return {
        "status": "FAIL_CLOSED_XLSX_SOURCE_ROWS_UNTRUSTED_OR_UNSUPPORTED",
        "parsed_source_days": 0,
        "dates": [],
        "xlsx_source_rows_match_claim": False,
        "original_krx_provider_authenticated": False,
        "original_publication_pit_attested": False,
        "exchange_session_source_admitted": False,
        "27_problem_securities_released": False,
        "ordering": "DISABLED",
        "live_orders_authorized": False,
        "network_requests_made": False,
    }


def parse_xml(content: bytes):
    if len(content) > MAX_XML or b"<!DOCTYPE" in content.upper():
        raise ValueError("UNSAFE_XML")
    return ET.fromstring(content)


def strings_from_shared(root):
    rows = []
    for item in root.findall(SS+"si"):
        rows.append("".join((x.text or "") for x in item.iter(SS+"t")))
        if len(rows) > 5000:
            raise ValueError("SHARED_STRINGS_TOO_LARGE")
    return rows


def date_style_indices(root):
    fmts = {}
    parent = root.find(SS+"numFmts")
    if parent is not None:
        for item in parent.findall(SS+"numFmt"):
            idx = int(item.attrib.get("numFmtId", "-1"))
            fmt = item.attrib.get("formatCode","").lower()
            fmts[idx] = fmt
    xfs = root.find(SS+"cellXfs")
    if xfs is None:
        return set()
    good=set()
    for i, xf in enumerate(xfs.findall(SS+"xf")):
        idx=int(xf.attrib.get("numFmtId","0"))
        fmt=fmts.get(idx,"")
        # A custom format must specifically spell out year/day and month,
        # rather than merely containing a time token.
        if idx in BUILTIN_DATE_FORMAT_IDS or (
            "yyyy" in fmt and "mm" in fmt and "dd" in fmt
            and "[" not in fmt
        ):
            good.add(i)
    return good


def text_of_cell(cell, shared):
    if cell.find(SS+"f") is not None:
        raise ValueError("FORMULA_NOT_ORIGINAL_VALUE")
    kind=cell.attrib.get("t")
    if kind == "inlineStr":
        inline=cell.find(SS+"is")
        if inline is None:
            raise ValueError("INLINE_STRING_MISSING")
        return "".join((x.text or "") for x in inline.iter(SS+"t")),False
    value=cell.find(SS+"v")
    if value is None or value.text is None:
        raise ValueError("EMPTY_CELL")
    if kind == "s":
        n=int(value.text)
        if n < 0 or n>=len(shared):
            raise ValueError("SHARED_STRING_INDEX")
        return shared[n],False
    if kind in (None,"n"):
        return value.text,True
    if kind == "str":
        return value.text,False
    raise ValueError("UNSUPPORTED_CELL_TYPE")


def read_holiday_source_xlsx(source_bytes: bytes, claim: dict, year: int) -> dict:
    error=refuse()
    baseline=normalize_calendar_export_claim(source_bytes,claim,year)
    if baseline["status"]!="SOURCE_BYTES_HASH_BOUND_CALENDAR_CLAIM_ONLY_NOT_PIT":
        return error
    if not source_bytes.startswith(b"PK\x03\x04"):
        return error
    try:
        with ZipFile(io.BytesIO(source_bytes), "r") as book:
            items=book.infolist()
            if len(items)>80 or not items:
                return error
            names=set()
            total=0
            for item in items:
                name=item.filename
                if (name in names or name.startswith("/") or "\\" in name
                        or ".." in name.split("/") or name.endswith("/")
                        or item.is_dir() or item.flag_bits & 1
                        or name not in ALLOWED and not name.startswith(ALLOWED_PREFIXES)
                        or name.startswith("xl/theme/") and not name.endswith(".xml")
                        or name.startswith("docProps/") and not name.endswith(".xml")
                        or item.file_size>MAX_XML):
                    return error
                names.add(name)
                total+=item.file_size
            if total > MAX_UNCOMPRESSED or not (
                {"[Content_Types].xml","xl/workbook.xml","xl/worksheets/sheet1.xml",
                 "xl/_rels/workbook.xml.rels"} <= names
            ):
                return error
            # Relationship XML may carry remote links. Reject all external
            # relationships rather than relying on URI dereference behavior.
            for name in names:
                if name.endswith(".rels"):
                    rel=parse_xml(book.read(name))
                    for r in rel.iter():
                        if r.attrib.get("TargetMode","").lower()=="external":
                            return error
            workbook=parse_xml(book.read("xl/workbook.xml"))
            sheets=workbook.find(SS+"sheets")
            if sheets is None or len(sheets.findall(SS+"sheet")) != 1:
                return error
            views=workbook.find(SS+"workbookPr")
            if views is not None and views.attrib.get("date1904","false").lower() in ("1","true"):
                return error
            sheet=sheets.find(SS+"sheet")
            if sheet.attrib.get("state","visible")!="visible":
                return error
            # The displayed workbook's one declared worksheet MUST resolve
            # via its actual relationship ID to exactly the XML we parse.
            # Otherwise an attacker can place correct dates in an unused
            # sheet1.xml while the workbook displays a different sheet.
            relationship_id=sheet.attrib.get(PKGREL+"id")
            if not relationship_id:
                return error
            relroot=parse_xml(book.read("xl/_rels/workbook.xml.rels"))
            worksheet_targets=[
                r for r in relroot.findall(PACKAGE_REL+"Relationship")
                if r.attrib.get("Type")==SHEET_TYPE
            ]
            if (len(worksheet_targets)!=1
                    or worksheet_targets[0].attrib.get("Id")!=relationship_id
                    or worksheet_targets[0].attrib.get("Target") not in (
                        "worksheets/sheet1.xml", "/xl/worksheets/sheet1.xml"
                    )):
                return error
            shared=(strings_from_shared(parse_xml(book.read("xl/sharedStrings.xml")))
                    if "xl/sharedStrings.xml" in names else [])
            styles=(date_style_indices(parse_xml(book.read("xl/styles.xml")))
                    if "xl/styles.xml" in names else set())
            root=parse_xml(book.read("xl/worksheets/sheet1.xml"))
            # Do not count dates in spreadsheet rows that an operator
            # cannot see. Filters, hidden rows/columns, and zero-height
            # defaults can make a human-visible KRX calendar differ from
            # the XML rows. Reject such documents rather than pretending
            # all parsed dates were visibly exported.
            fmt=root.find(SS+"sheetFormatPr")
            if (fmt is not None
                    and fmt.attrib.get("zeroHeight", "0").lower() in ("1","true")):
                return error
            if (root.find(SS+"autoFilter") is not None
                    or root.find(SS+"mergeCells") is not None):
                return error
            cols=root.find(SS+"cols")
            if cols is not None:
                for col in cols.findall(SS+"col"):
                    if col.attrib.get("hidden", "0").lower() in ("1","true"):
                        return error
            data=root.find(SS+"sheetData")
            if data is None:
                return error
            lines=data.findall(SS+"row")
            if not 2 <= len(lines) <= 400:
                return error
            dates=[]
            seen=set()
            for i,row in enumerate(lines,start=1):
                if (row.attrib.get("hidden","0").lower() in ("1","true")
                        or row.attrib.get("ht") in ("0","0.0")
                        or row.attrib.get("r",str(i))!=str(i)):
                    return error
                cells={}
                for c in row.findall(SS+"c"):
                    addr=c.attrib.get("r")
                    if addr not in (f"A{i}",f"B{i}",f"C{i}") or addr in cells:
                        return error
                    cells[addr]=c
                if len(cells)!=3:
                    return error
                dval,dnum=text_of_cell(cells[f"A{i}"],shared)
                weekday,_=text_of_cell(cells[f"B{i}"],shared)
                note,_=text_of_cell(cells[f"C{i}"],shared)
                if len(note)>300:
                    return error
                if i==1:
                    if (dval.strip(),weekday.strip(),note.strip()) != ("일자","요일","비고"):
                        return error
                    continue
                if dnum:
                    # Numeric date serial is only recognized when the source
                    # cell's style is an explicit Excel date number format.
                    if int(cells[f"A{i}"].attrib.get("s","0")) not in styles:
                        return error
                    number=int(dval)
                    if str(number)!=dval or number<40000 or number>50000:
                        return error
                    d=date(1899,12,30)+timedelta(days=number)
                else:
                    if not DAY.fullmatch(dval):
                        return error
                    d=date.fromisoformat(dval)
                    if d.isoformat()!=dval:
                        return error
                day=d.isoformat()
                if day in seen or d.year!=year:
                    return error
                seen.add(day)
                if weekday.strip() not in ("월화수목금토일"[d.weekday()],
                                           "월화수목금토일"[d.weekday()]+"요일"):
                    return error
                if d.weekday()<5:
                    dates.append(day)
            if not dates or sorted(dates)!=baseline["dates"]:
                return error
            return {
                **baseline,
                "status":"SOURCE_XLSX_ROWS_EXACT_MATCH_CLAIM_ONLY_NOT_PIT",
                "xlsx_source_rows_match_claim":True,
                "parsed_source_days":len(dates),
                "original_krx_provider_authenticated":False,
                "original_publication_pit_attested":False,
                "exchange_session_source_admitted":False,
                "27_problem_securities_released":False,
                "ordering":"DISABLED",
                "live_orders_authorized":False,
                "network_requests_made":False,
            }
    except (ValueError,TypeError,OverflowError,ET.ParseError,BadZipFile,
            KeyError,IndexError,UnicodeDecodeError):
        return error
