"""First-filing 2022 Q3 DART viewer: source table HEADER-CELL layout only.

Look for structurally distinct heading rows BEFORE operating-profit rows in the
same first-receipt financial table. Do not persist raw text, numbers, titles,
receipt/document IDs, cell offsets, data fingerprints or original viewer HTML.
Even correct TH/TD relationships do not establish immutable historical PIT,
CFS scope, currency, publication instant or quantitative feature eligibility.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import unicodedata

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_first_document_pilot import OPERATING_ROW_LABELS
from research_v1_opendart_m20_2022_first_viewer_financial_sections import (
    SAFE, SectionGap, _choose_first_edition_sections, _bounded_public_get,
)
from research_v1_opendart_m20_2022_first_viewer_toc import _viewer_fetch

OUT = Path("research_results/opendart_m20_2022_first_viewer_header_layout/counts.json")
MAX_NODE_COUNT = 900_000
MAX_TOTAL_TEXT = 4 * 1024 * 1024
MAX_CELL_LENGTH = 8192
MAX_TABLE_DEPTH = 40
MAX_TABLES = 2000
MAX_ROWS_PER_TABLE = 5000
MAX_CELLS_PER_ROW = 150
MAX_VIEWER_GETS = 5
MAX_OFFICIAL_GETS = 2
NUMBER = re.compile(r"^-?(?:0|[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+)(?:\.[0-9]+)?$")
LABELS = frozenset(
    re.sub(r"\s+", "", unicodedata.normalize("NFKC", k))
    for k in OPERATING_ROW_LABELS
)
COUNT_KEYS = (
    "operating_candidate_tables",
    "operating_candidate_rows",
    "operating_with_four_numeric_peers",
    "operating_rows_with_preceding_table_row",
    "operating_with_preceding_th_cell",
    "operating_with_preceding_explicit_quarter_words",
    "operating_with_preceding_current_and_prior_quarter_words",
    "operating_with_same_header_row_current_and_prior_words",
    "operating_with_preceding_three_month_word",
    "operating_with_preceding_cumulative_word",
    "operating_with_preceding_third_quarter_word",
    "operating_with_preceding_colspan_or_rowspan",
    "operating_with_direct_numeric_cells_and_four_peers",
    "operating_candidate_in_nested_table",
    "operating_candidate_table_has_nested_child",
)

PIT_BLOCK = {
    "first_filing_immutable_viewer_snapshot_verified": False,
    "original_cfs_identity_and_profit_colmap_verified": False,
    "original_2022_q3_standalone_cfs_operating_amount_verified": False,
    "original_2021_q3_standalone_comparator_verified": False,
    "original_2022_period_and_monetary_units_verified": False,
    "historical_first_publication_instant_verified": False,
    "historical_corp_security_pit_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "raw_headers_cell_values_row_positions_or_identifiers_saved": False,
    "ordering": "DISABLED",
}


def _norm(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


class HeaderRows(HTMLParser):
    """Finite scan of header row/cell structure with bounded transient text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames = []
        self.tables = 0
        self.nodes = 0
        self.input_chars = 0
        self.counts = {k: 0 for k in COUNT_KEYS}

    def _close_cell(self, f):
        if f["cell"] is None:
            return
        if len(f["row"]) >= MAX_CELLS_PER_ROW:
            raise SectionGap("HEADER_CELL_COUNT_LIMIT")
        c = f["cell"]
        c["value"] = _norm("".join(c.pop("parts")))
        f["row"].append(c)
        f["cell"] = None

    def _close_row(self, f):
        self._close_cell(f)
        if f["row"]:
            if len(f["rows"]) >= MAX_ROWS_PER_TABLE:
                raise SectionGap("HEADER_ROW_COUNT_LIMIT")
            f["rows"].append(f["row"])
        f["row"] = []

    @staticmethod
    def _has(text: str, marker: str) -> bool:
        return marker in text

    def _evaluate(self, f):
        if not f["rows"]:
            return
        candidates = []
        for index, row in enumerate(f["rows"]):
            values = [c["value"] for c in row]
            if any(k in LABELS for k in values[:2]):
                candidates.append((index, row))
        if not candidates:
            return
        self.counts["operating_candidate_tables"] += 1
        self.counts["operating_candidate_in_nested_table"] += bool(f["nested"])
        self.counts["operating_candidate_table_has_nested_child"] += bool(f["child"])
        for index, row in candidates:
            self.counts["operating_candidate_rows"] += 1
            direct = any(c["value"] in LABELS for c in row[:2])
            values = [c["value"] for c in row]
            peers = sum(bool(NUMBER.fullmatch(v)) for v in values[1:])
            self.counts["operating_with_four_numeric_peers"] += peers >= 4
            self.counts["operating_with_direct_numeric_cells_and_four_peers"] += direct and peers >= 4
            before = f["rows"][:index]
            all_preceding_cells = [c for prior in before for c in prior]
            preceding_text = "".join(c["value"] for c in all_preceding_cells)
            self.counts["operating_rows_with_preceding_table_row"] += bool(before)
            self.counts["operating_with_preceding_th_cell"] += any(
                c["tag"] == "th" for c in all_preceding_cells
            )
            current = "당분기" in preceding_text
            prior = "전분기" in preceding_text
            self.counts["operating_with_preceding_explicit_quarter_words"] += current or prior
            self.counts["operating_with_preceding_current_and_prior_quarter_words"] += current and prior
            self.counts["operating_with_same_header_row_current_and_prior_words"] += any(
                "당분기" in "".join(c["value"] for c in earlier)
                and "전분기" in "".join(c["value"] for c in earlier)
                for earlier in before
            )
            self.counts["operating_with_preceding_three_month_word"] += "3개월" in preceding_text
            self.counts["operating_with_preceding_cumulative_word"] += "누적" in preceding_text
            self.counts["operating_with_preceding_third_quarter_word"] += any(
                x in preceding_text for x in ("3분기", "제3분기", "3사분기")
            )
            self.counts["operating_with_preceding_colspan_or_rowspan"] += any(
                c["merged"] for c in all_preceding_cells
            )

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > MAX_NODE_COUNT:
            raise SectionGap("HEADER_HTML_NODE_LIMIT")
        if tag == "table":
            if len(self.frames) >= MAX_TABLE_DEPTH or self.tables + len(self.frames) >= MAX_TABLES:
                raise SectionGap("HEADER_TABLE_COUNT_LIMIT")
            if self.frames:
                self.frames[-1]["child"] = True
            self.frames.append({"nested": bool(self.frames), "child": False,
                                "rows": [], "row": [], "cell": None})
        elif tag == "tr" and self.frames:
            self._close_row(self.frames[-1])
        elif tag in ("td", "th") and self.frames:
            f = self.frames[-1]
            if f["cell"] is not None:
                self._close_cell(f)
            kv = dict(attrs)
            merged = False
            for attr in ("colspan", "rowspan"):
                value = kv.get(attr)
                if value is not None:
                    if not str(value).isdigit() or not 1 <= int(value) <= MAX_CELLS_PER_ROW:
                        raise SectionGap("HEADER_CELL_SPAN_INVALID")
                    merged |= int(value) > 1
            f["cell"] = {"parts": [], "n": 0, "tag": tag, "merged": merged}

    def handle_data(self, value):
        self.input_chars += len(value)
        if self.input_chars > MAX_TOTAL_TEXT:
            raise SectionGap("HEADER_SOURCE_TEXT_LIMIT")
        if self.frames and self.frames[-1]["cell"] is not None:
            cell = self.frames[-1]["cell"]
            cell["n"] += len(value)
            if cell["n"] > MAX_CELL_LENGTH:
                raise SectionGap("HEADER_CELL_TEXT_LIMIT")
            cell["parts"].append(value)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.frames:
            self._close_cell(self.frames[-1])
        elif tag == "tr" and self.frames:
            self._close_row(self.frames[-1])
        elif tag == "table":
            if not self.frames:
                raise SectionGap("HEADER_TABLE_UNBALANCED")
            frame = self.frames.pop()
            self._close_row(frame)
            self.tables += 1
            self._evaluate(frame)

    def finish(self):
        if self.frames or not self.tables:
            raise SectionGap("HEADER_TABLE_UNBALANCED")
        if self.counts["operating_candidate_tables"] > self.tables:
            raise SectionGap("HEADER_CANDIDATE_COUNT_INVALID")
        return {"table_tags": self.tables, **self.counts}


def inspect(session, toc: str, first: str) -> dict:
    metadata = _choose_first_edition_sections(toc, first)
    if len(metadata) != 4:
        raise SectionGap("HEADER_FOUR_FIRST_SECTIONS_REQUIRED")
    pages = []
    for section in metadata:
        scanner = HeaderRows()
        scanner.feed(_bounded_public_get(session, section, first))
        scanner.close()
        pages.append(scanner.finish())
    report = {k: sum(page[k] for page in pages) for k in COUNT_KEYS}
    if report["operating_candidate_tables"] > 10 or report["operating_candidate_rows"] > 20:
        raise SectionGap("HEADER_ORIGINAL_ROW_CANDIDATES_DRIFT")
    return {
        "source_status": "FIRST_RECEIPT_VIEWER_HEADER_ROW_SHAPES_ONLY",
        "fixed_first_filing_financial_subdocuments": len(pages),
        "source_table_tags": sum(page["table_tags"] for page in pages),
        **report,
        "header_word_column_or_group_identity_verified": False,
        "viewer_header_row_is_not_original_accounting_fact": True,
    }


def execute(session, key: str) -> dict:
    raw = _official_get(session, "corpCode.xml", {"crtfc_key": key}, zip_response=True)
    issuer = _registry(raw).get(COHORT[5])
    if issuer is None:
        raise SectionGap("HEADER_FROZEN_ISSUER_MISSING")
    begin, end = _window(2022)
    listing = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": issuer, "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    first = original_first_receipt(listing, 2022)
    return inspect(session, _viewer_fetch(session, first), first)


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    result = {
        "purpose": "FROZEN_M20_2022_Q3_FIRST_RECEIPT_VIEWER_HEADER_LAYOUT_ONLY",
        "fixed_cohort_slot": 5,
        "max_official_api_calls": MAX_OFFICIAL_GETS,
        "max_public_viewer_calls": MAX_VIEWER_GETS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFE, **PIT_BLOCK,
    }
    if not key:
        return result
    if session is None:
        import requests
        session = requests.Session()
    try:
        result.update(execute(session, key))
    except Exception as exc:
        codes = {
            "HEADER_CELL_COUNT_LIMIT", "HEADER_ROW_COUNT_LIMIT",
            "HEADER_HTML_NODE_LIMIT", "HEADER_TABLE_COUNT_LIMIT",
            "HEADER_CELL_SPAN_INVALID", "HEADER_SOURCE_TEXT_LIMIT",
            "HEADER_CELL_TEXT_LIMIT", "HEADER_TABLE_UNBALANCED",
            "HEADER_CANDIDATE_COUNT_INVALID", "HEADER_FOUR_FIRST_SECTIONS_REQUIRED",
            "HEADER_ORIGINAL_ROW_CANDIDATES_DRIFT", "HEADER_FROZEN_ISSUER_MISSING",
        }
        status = str(exc) if type(exc) is SectionGap else ""
        result["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        result["failure_code"] = status if status in codes else "ORIGINAL_VIEWER_HEADER_SOURCE_NOT_VERIFIED"
    return result


if __name__ == "__main__":
    status = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    print("M20_FIRST_VIEWER_HEADER_ROW=" + json.dumps(status, sort_keys=True), flush=True)
