"""2022 Q3 fixed original receipt: historical DART list clock availability probe.

Uses the OFFICIAL original-filing index to select the first submitted receipt,
then ONE public DART recent-disclosure page by its *receipt date*. Checks
whether the exact original receipt appears in a bounded table row and whether
that SAME row contains a single HH:MM or HH:MM:SS cell.

The website is a mutable historical *rendering*, not an audited proof of
original intraday public availability. NEVER infer an original financial fact,
PIT eligibility, earlier-hour availability, trading/holdout/performance, or
an authoritative first-publication timestamp, regardless of result.
No raw issuer/receipt/time/date/webpage, source values, IDs or hash saved.
"""
from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
import json
import os
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt

OUTPUT = Path("research_results/m20_2022_first_historical_dart_clock/counts.json")
PUBLIC_LIST_URL = "https://dart.fss.or.kr/dsac001/mainAll.do"
MAX_PUBLIC_CALLS = 1
MAX_OFFICIAL_CALLS = 2
MAX_HTML_BYTES = 2 * 1024 * 1024
MAX_HTML_NODES = 250000
MAX_ROWS = 7000
MAX_ROW_CHARS = 20000
MAX_CELLS = 45
REC = re.compile(r"[0-9]{14}\Z")
DAY = re.compile(r"[0-9]{8}\Z")
CLOCK = re.compile(r"(?:[01][0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?\Z")
DIGITS14 = re.compile(r"(?<![0-9])[0-9]{14}(?![0-9])")
SAFE = {
    "website_clock_is_authoritative_first_release_instant": False,
    "exact_original_first_publication_timestamp_verified": False,
    "original_2022_q3_three_month_cfs_operating_profit_verified": False,
    "original_2021_q3_three_month_cfs_comparator_verified": False,
    "historical_issuer_security_pit_verified": False,
    "financial_correction_vintage_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "source_html_raw_receipt_time_date_company_or_values_saved": False,
    "ordering": "DISABLED",
}


class ClockGap(ValueError):
    """Public-safe fixed diagnostics only."""


def _first_receipt_and_day(index: dict) -> tuple[str, str]:
    first = original_first_receipt(index, 2022)
    if not REC.fullmatch(first):
        raise ClockGap("FIRST_RECEIPT_FORMAT_INVALID")
    matches = [row for row in index.get("list", []) if row.get("rcept_no") == first]
    if len(matches) != 1:
        raise ClockGap("FIRST_RECEIPT_INDEX_AMBIGUOUS")
    date = matches[0].get("rcept_dt")
    if type(date) is not str or not DAY.fullmatch(date) or date != first[:8]:
        raise ClockGap("ORIGINAL_RECEIPT_DATE_UNVERIFIED")
    try:
        datetime.strptime(date, "%Y%m%d")
    except ValueError:
        raise ClockGap("ORIGINAL_RECEIPT_DATE_INVALID") from None
    return first, date


class ExactReceiptRows(HTMLParser):
    """Retain only one row at a time; count row-matched time cells only."""

    def __init__(self, target: str):
        if type(target) is not str or not REC.fullmatch(target):
            raise ClockGap("TARGET_RECEIPT_INVALID")
        super().__init__(convert_charrefs=True)
        self.target = target
        self.nodes = 0
        self.rows = 0
        self.active = False
        self.row_chars = 0
        self.receipt_matches = []
        self.td_level = 0
        self.cell = None
        self.cells = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > MAX_HTML_NODES:
            raise ClockGap("HISTORIC_LIST_NODE_LIMIT")
        if tag == "tr":
            if self.active:
                raise ClockGap("HISTORIC_LIST_NESTED_ROWS")
            self.active = True
            self.row_chars = 0
            self.ids = set()
            self.cells = []
            self.cell = None
            self.td_level = 0
        elif self.active:
            for _, value in attrs:
                if value:
                    self.row_chars += len(value)
                    if self.row_chars > MAX_ROW_CHARS:
                        raise ClockGap("HISTORIC_LIST_ROW_TEXT_LIMIT")
                    for found in DIGITS14.findall(value):
                        self.ids.add(found)
            if tag == "td":
                if self.td_level:
                    raise ClockGap("HISTORIC_LIST_NESTED_CELLS")
                self.td_level = 1
                self.cell = []

    def handle_data(self, value):
        if not self.active:
            return
        self.row_chars += len(value)
        if self.row_chars > MAX_ROW_CHARS:
            raise ClockGap("HISTORIC_LIST_ROW_TEXT_LIMIT")
        for found in DIGITS14.findall(value):
            self.ids.add(found)
        if self.cell is not None:
            self.cell.append(value)

    def handle_endtag(self, tag):
        if not self.active:
            return
        if tag == "td":
            if self.cell is not None:
                if len(self.cells) >= MAX_CELLS:
                    raise ClockGap("HISTORIC_LIST_ROW_CELL_LIMIT")
                self.cells.append("".join(self.cell).strip())
            self.cell = None
            self.td_level = 0
        elif tag == "tr":
            self.rows += 1
            if self.rows > MAX_ROWS:
                raise ClockGap("HISTORIC_LIST_ROW_COUNT_LIMIT")
            if self.target in self.ids:
                if len(self.ids) != 1:
                    raise ClockGap("HISTORIC_LIST_MIXED_RECEIPTS_IN_ROW")
                clocks = {value for cell in self.cells
                          if CLOCK.fullmatch(value := re.sub(r"\s+", "", cell))}
                if len(clocks) > 1:
                    raise ClockGap("HISTORIC_LIST_MULTIPLE_ROW_CLOCKS")
                self.receipt_matches.append(bool(clocks))
            self.active = False
            self.cells = []
            self.cell = None
            self.ids.clear()

    def verdict(self) -> dict:
        if self.active or self.rows == 0:
            raise ClockGap("HISTORIC_LIST_TABLE_ROWS_UNVERIFIED")
        if len(self.receipt_matches) > 1:
            raise ClockGap("HISTORIC_LIST_DUPLICATE_FIRST_RECEIPT")
        if len(self.receipt_matches) == 0:
            raise ClockGap("HISTORIC_LIST_FIRST_RECEIPT_NOT_VISIBLE")
        return {
            "source_status": "FIRST_RECEIPT_HISTORIC_LIST_ROW_CLOCK_SHAPE_ONLY",
            "first_original_receipt_row_on_selected_listing_page": True,
            "first_original_receipt_row_has_unique_time_cell": self.receipt_matches[0],
            "source_website_time_value_discarded": True,
            "row_clock_is_not_original_first_published_time": True,
            "historical_listing_pagination_or_archive_completeness_verified": False,
        }


def _public_listing(session, receipt_day: str) -> str:
    if type(receipt_day) is not str or not DAY.fullmatch(receipt_day):
        raise ClockGap("HISTORIC_LIST_REQUEST_DATE_INVALID")
    pretty = ".".join((receipt_day[:4],receipt_day[4:6],receipt_day[6:]))
    try:
        resp = session.get(
            PUBLIC_LIST_URL, params={"selectDate": pretty},
            allow_redirects=False, stream=True, timeout=20,
            headers={"User-Agent": "IndexAlert-ReadOnlyResearch/1.0"},
        )
    except Exception:
        raise ClockGap("HISTORIC_LIST_NETWORK_UNAVAILABLE") from None
    try:
        if resp.status_code != 200:
            raise ClockGap("HISTORIC_LIST_HTTP_UNAVAILABLE")
        if "text/html" not in resp.headers.get("Content-Type", "").lower():
            raise ClockGap("HISTORIC_LIST_CONTENT_TYPE_INVALID")
        chunks = bytearray()
        for item in resp.iter_content(chunk_size=32768):
            chunks.extend(item)
            if len(chunks) > MAX_HTML_BYTES:
                raise ClockGap("HISTORIC_LIST_HTML_SIZE_LIMIT")
        for encoding in ("utf-8", "cp949", "euc-kr"):
            try:
                return bytes(chunks).decode(encoding, "strict")
            except UnicodeError:
                pass
        raise ClockGap("HISTORIC_LIST_ENCODING_UNVERIFIED")
    finally:
        resp.close()


def execute(session, key: str) -> dict:
    raw = _official_get(session, "corpCode.xml",
                        {"crtfc_key": key}, zip_response=True)
    issuer = _registry(raw).get(COHORT[5])
    if issuer is None:
        raise ClockGap("FIXED_ORIGINAL_ISSUER_MISSING")
    begin, end = _window(2022)
    index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": issuer,
        "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    first, day = _first_receipt_and_day(index)
    parser = ExactReceiptRows(first)
    parser.feed(_public_listing(session, day))
    parser.close()
    return parser.verdict()


def run(session=None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    result = {
        "purpose": "M20_FIXED_SLOT5_2022_FIRST_ORIGINAL_HISTORIC_DART_LIST_CLOCK_SHAPE",
        "fixed_cohort_slot": 5,
        "official_api_request_ceiling": MAX_OFFICIAL_CALLS,
        "public_dart_page_request_ceiling": MAX_PUBLIC_CALLS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFE,
    }
    if not key:
        return result
    if session is None:
        import requests
        session = requests.Session()
    try:
        result.update(execute(session, key))
    except Exception as exc:
        valid = {
            "FIRST_RECEIPT_FORMAT_INVALID", "FIRST_RECEIPT_INDEX_AMBIGUOUS",
            "ORIGINAL_RECEIPT_DATE_UNVERIFIED", "ORIGINAL_RECEIPT_DATE_INVALID",
            "TARGET_RECEIPT_INVALID", "HISTORIC_LIST_NODE_LIMIT",
            "HISTORIC_LIST_NESTED_ROWS", "HISTORIC_LIST_ROW_TEXT_LIMIT",
            "HISTORIC_LIST_NESTED_CELLS", "HISTORIC_LIST_ROW_CELL_LIMIT",
            "HISTORIC_LIST_ROW_COUNT_LIMIT", "HISTORIC_LIST_MULTIPLE_ROW_CLOCKS",
            "HISTORIC_LIST_MIXED_RECEIPTS_IN_ROW",
            "HISTORIC_LIST_TABLE_ROWS_UNVERIFIED",
            "HISTORIC_LIST_DUPLICATE_FIRST_RECEIPT",
            "HISTORIC_LIST_FIRST_RECEIPT_NOT_VISIBLE",
            "HISTORIC_LIST_REQUEST_DATE_INVALID",
            "HISTORIC_LIST_NETWORK_UNAVAILABLE", "HISTORIC_LIST_HTTP_UNAVAILABLE",
            "HISTORIC_LIST_CONTENT_TYPE_INVALID",
            "HISTORIC_LIST_HTML_SIZE_LIMIT", "HISTORIC_LIST_ENCODING_UNVERIFIED",
            "FIXED_ORIGINAL_ISSUER_MISSING",
        }
        code = str(exc) if type(exc) is ClockGap else ""
        result["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        result["source_gap_reason"] = code if code in valid else "ORIGINAL_HISTORIC_LIST_CLOCK_UNVERIFIED"
    return result


if __name__ == "__main__":
    report = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_HISTORIC_DART_LIST_CLOCK=" + json.dumps(report, sort_keys=True))
