"""Original DART financial TOC subdocument retrieval feasibility; NO PIT.

Select *all* (max 4) first-receipt viewer TOC entries containing 재무제표,
fetch each directly from HTTPS viewer.do using pinned original receipt and
validated bounded metadata. Count only lexical/HTML structure flags in memory.
A viewer subsection may be dynamically rendered, changed or not correspond
to an authoritative original CFS quarter. Never save identifiers, titles,
financial values, raw HTML, disclosure instants, or broker permissions.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re

from research_v1_opendart_m20_2022_first_viewer_toc import (
    NODE, RECEIPT, VIEWER_URL, _viewer_fetch, _safe_counts, ViewerGap,
    MAX_ITEMS, MAX_BYTES,
)
from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_first_document_pilot import OPERATING_ROW_LABELS

DEST = Path("research_results/opendart_m20_2022_original_viewer_financial_sections/counts.json")
SECTION_URL = "https://dart.fss.or.kr/report/viewer.do"
MAX_SECTIONS = 4
MAX_SECTION_BYTES = 4 * 1024 * 1024
MAX_SCAN_NODES = 750_000
MAX_TEXT = 4 * 1024 * 1024
MAX_OFFICIAL_CALLS = 2
MAX_VIEWER_CALLS = 1 + MAX_SECTIONS
SAFE = {
    "original_2022_cfs_profit_three_month_verified": False,
    "original_2021_comparator_three_month_verified": False,
    "original_viewer_html_is_immutable_filing_proof": False,
    "viewer_financial_toc_is_accounting_statement_lineage": False,
    "original_2022_xbrl_verified": False,
    "original_publication_instant_verified": False,
    "historical_issuer_security_pit_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "raw_amounts_document_ids_titles_url_params_source_or_secrets_saved": False,
    "ordering": "DISABLED",
}


class SectionGap(ValueError):
    """Only predefined safe reason codes may leave the source probe."""


def _choose_first_edition_sections(html: str, first: str) -> list[dict]:
    if not RECEIPT.fullmatch(first) or len(html) > MAX_BYTES:
        raise SectionGap("ORIGINAL_VIEWER_INPUT_INVALID")
    # Apply the upstream original-edition identity guard to the entire viewer
    # before accepting a subset of its financial nodes. Otherwise an amended
    # rcpNo assignment on a malformed nonfinancial record could be skipped.
    try:
        _safe_counts(html, first)
    except ViewerGap:
        raise SectionGap("VIEWER_RECEIPT_EDITION_MISMATCH") from None
    matches = list(NODE.finditer(html))
    if not 0 < len(matches) <= MAX_ITEMS:
        raise SectionGap("ORIGINAL_VIEWER_TOC_UNAVAILABLE")
    if any(x.group("receipt") != first for x in matches):
        raise SectionGap("VIEWER_RECEIPT_EDITION_MISMATCH")
    financial = [x for x in matches if "재무제표" in x.group("title")]
    if not 1 <= len(financial) <= MAX_SECTIONS:
        raise SectionGap("FINANCIAL_SUBDOCUMENT_COUNT_UNVERIFIED")
    selected = []
    keys = set()
    for match in financial:
        fields = {name: match.group(name) for name in
                  ("receipt", "document", "element", "offset", "length", "dtd")}
        key = (fields["document"], fields["element"], fields["offset"], fields["length"])
        if key in keys:
            raise SectionGap("FINANCIAL_SUBDOCUMENT_DUPLICATE_METADATA")
        keys.add(key)
        selected.append(fields)
    return selected


class SectionShape(HTMLParser):
    """Count hint categories only, discard every parsed textual value."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = 0
        self.chars = 0
        self.table_depth = 0
        self.table_tags = 0
        self.cell_parts = None
        self.row = []
        self.row_open = False
        self.operating_rows = 0
        self.all_parts = []

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > MAX_SCAN_NODES:
            raise SectionGap("VIEWER_SECTION_NODE_LIMIT")
        if tag == "table":
            self.table_depth += 1
            self.table_tags += 1
        if tag == "tr" and self.table_depth:
            self._end_row()
            self.row_open = True
        if tag in ("td", "th") and self.row_open:
            self._end_cell()
            self.cell_parts = []

    def handle_data(self, text):
        self.chars += len(text)
        if self.chars > MAX_TEXT:
            raise SectionGap("VIEWER_SECTION_TEXT_LIMIT")
        # Whole page held ephemerally in RAM, no persisted text.
        self.all_parts.append(text)
        if self.cell_parts is not None:
            self.cell_parts.append(text)

    def _end_cell(self):
        if self.cell_parts is not None:
            if len(self.row) > 150:
                raise SectionGap("VIEWER_SECTION_CELL_LIMIT")
            self.row.append("".join(self.cell_parts))
            self.cell_parts = None

    def _end_row(self):
        self._end_cell()
        if self.row_open and self.table_depth:
            short = [re.sub(r"\s+", "", text) for text in self.row[:2]]
            if any(x in OPERATING_ROW_LABELS for x in short):
                self.operating_rows += 1
        self.row_open = False
        self.row = []

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self._end_cell()
        elif tag == "tr":
            self._end_row()
        elif tag == "table":
            self._end_row()
            if self.table_depth == 0:
                raise SectionGap("VIEWER_SECTION_TABLE_UNBALANCED")
            self.table_depth -= 1

    def result(self):
        if self.table_depth:
            raise SectionGap("VIEWER_SECTION_TABLE_UNBALANCED")
        body = re.sub(r"\s+", "", "".join(self.all_parts))
        return {
            "table_tags": self.table_tags,
            "exact_operating_row_candidates": self.operating_rows,
            "exact_cfs_income_heading_lexical_hint": any(
                x in body for x in ("연결손익계산서", "연결포괄손익계산서")),
            "generic_consolidated_financial_lexical_hint": "연결재무제표" in body,
            "three_month_lexical_hint": "3개월" in body,
            "year_2022_lexical_hint": "2022" in body,
            "year_2021_lexical_hint": "2021" in body,
        }


def _bounded_public_get(session, meta: dict, expected_receipt: str) -> str:
    if (meta["receipt"] != expected_receipt or
            not RECEIPT.fullmatch(expected_receipt)):
        raise SectionGap("SUBDOC_ORIGINAL_RECEIPT_UNVERIFIED")
    # These six explicit arguments are obtained from the exact original TOC
    # and validated by a narrow digits/DTD regex, never from an outside URL.
    params = {"rcpNo": expected_receipt, "dcmNo": meta["document"],
              "eleId": meta["element"], "offset": meta["offset"],
              "length": meta["length"], "dtd": meta["dtd"]}
    try:
        response = session.get(SECTION_URL, params=params, timeout=20,
                               allow_redirects=False, stream=True,
                               headers={"User-Agent": "IndexAlert-ReadOnlyResearch/1.0"})
    except Exception:
        raise SectionGap("VIEWER_SUBDOC_NETWORK_UNAVAILABLE") from None
    try:
        if response.status_code != 200:
            raise SectionGap("VIEWER_SUBDOC_HTTP_UNAVAILABLE")
        if "text/html" not in response.headers.get("Content-Type", "").lower():
            raise SectionGap("VIEWER_SUBDOC_CONTENT_TYPE_UNEXPECTED")
        data = bytearray()
        for chunk in response.iter_content(chunk_size=65536):
            data.extend(chunk)
            if len(data) > MAX_SECTION_BYTES:
                raise SectionGap("VIEWER_SUBDOC_SIZE_LIMIT")
        for enc in ("utf-8", "cp949", "euc-kr"):
            try:
                page = bytes(data).decode(enc, errors="strict")
                if "<html" not in page.lower() and "<table" not in page.lower():
                    raise SectionGap("VIEWER_SUBDOC_HTML_MISSING")
                return page
            except UnicodeError:
                continue
        raise SectionGap("VIEWER_SUBDOC_ENCODING_UNVERIFIED")
    finally:
        response.close()


def _inspect_sections(session, toc_html: str, first: str) -> dict:
    metas = _choose_first_edition_sections(toc_html, first)
    values = []
    for meta in metas:
        reader = SectionShape()
        reader.feed(_bounded_public_get(session, meta, first))
        reader.close()
        values.append(reader.result())
    if len(values) != len(metas):
        raise SectionGap("VIEWER_SECTION_COUNT_UNVERIFIED")
    return {
        "source_status": "FIRST_SUBMITTED_VIEWER_FINANCIAL_SUBDOC_LEXICAL_DIAGNOSTIC_ONLY",
        "first_receipt_financial_toc_sections_selected": len(metas),
        "viewer_financial_sections_returned_html": len(values),
        "viewer_financial_sections_with_tables": sum(x["table_tags"] > 0 for x in values),
        "viewer_financial_total_table_tags": sum(x["table_tags"] for x in values),
        "viewer_financial_total_operating_row_text_candidates": sum(
            x["exact_operating_row_candidates"] for x in values),
        "viewer_sections_exact_cfs_income_heading_hints": sum(
            x["exact_cfs_income_heading_lexical_hint"] for x in values),
        "viewer_sections_consolidated_financial_hints": sum(
            x["generic_consolidated_financial_lexical_hint"] for x in values),
        "viewer_sections_three_month_hints": sum(
            x["three_month_lexical_hint"] for x in values),
        "viewer_sections_both_2022_and_2021_year_hints": sum(
            x["year_2022_lexical_hint"] and x["year_2021_lexical_hint"]
            for x in values),
        "viewer_section_lexical_metadata_is_not_original_pit_proof": True,
    }


def execute(session, key: str) -> dict:
    raw = _official_get(session, "corpCode.xml",
                        {"crtfc_key": key}, zip_response=True)
    corp = _registry(raw).get(COHORT[5])
    if corp is None:
        raise SectionGap("FIRST_CORP_REGISTRY_MISSING")
    begin, end = _window(2022)
    index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": corp,
        "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    first = original_first_receipt(index, 2022)
    toc = _viewer_fetch(session, first)
    return _inspect_sections(session, toc, first)


def run(session=None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    report = {
        "purpose": "M20_FROZEN_SLOT5_2022_ORIGINAL_PUBLIC_VIEWER_FINANCIAL_SECTIONS_ONLY",
        "fixed_cohort_slot": 5, "max_official_requests": MAX_OFFICIAL_CALLS,
        "max_public_viewer_requests": MAX_VIEWER_CALLS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFE,
    }
    if not key:
        return report
    if session is None:
        import requests
        session = requests.Session()
    try:
        report.update(execute(session, key))
    except Exception as exc:
        codes = {
            "ORIGINAL_VIEWER_INPUT_INVALID", "ORIGINAL_VIEWER_TOC_UNAVAILABLE",
            "VIEWER_RECEIPT_EDITION_MISMATCH",
            "FINANCIAL_SUBDOCUMENT_COUNT_UNVERIFIED",
            "FINANCIAL_SUBDOCUMENT_DUPLICATE_METADATA",
            "VIEWER_SECTION_NODE_LIMIT", "VIEWER_SECTION_TEXT_LIMIT",
            "VIEWER_SECTION_CELL_LIMIT", "VIEWER_SECTION_TABLE_UNBALANCED",
            "SUBDOC_ORIGINAL_RECEIPT_UNVERIFIED",
            "VIEWER_SUBDOC_NETWORK_UNAVAILABLE", "VIEWER_SUBDOC_HTTP_UNAVAILABLE",
            "VIEWER_SUBDOC_CONTENT_TYPE_UNEXPECTED", "VIEWER_SUBDOC_SIZE_LIMIT",
            "VIEWER_SUBDOC_HTML_MISSING", "VIEWER_SUBDOC_ENCODING_UNVERIFIED",
            "VIEWER_SECTION_COUNT_UNVERIFIED", "FIRST_CORP_REGISTRY_MISSING",
        }
        reason = str(exc) if type(exc) is SectionGap else ""
        report["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        report["failure_code"] = reason if reason in codes else "VIEWER_FINANCIAL_SECTION_UNVERIFIED"
    return report


if __name__ == "__main__":
    result = run()
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("M20_VIEWER_FINANCIAL_SUBDOC=" + json.dumps(result, sort_keys=True), flush=True)
