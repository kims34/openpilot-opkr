"""M20 first-filed viewer Q3: bounded same-table structure counts, never PIT.

Investigates whether any first-receipt financial-viewer *table* with an exact
operating-profit row also contains standalone three-month header/quarter label,
numeric peer shapes, unit hints, original CFS labels or exact 2022/2021 Q3
period windows. Neither proximity nor a same-table header validates CFS
accounting cell/vintage. Nothing besides aggregate counts is persisted.
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
from research_v1_opendart_m20_2022_first_document_pilot import (
    OPERATING_ROW_LABELS, _has_q3_period_window,
)
from research_v1_opendart_m20_2022_first_viewer_financial_sections import (
    _choose_first_edition_sections, _bounded_public_get, SectionGap, SAFE,
)
from research_v1_opendart_m20_2022_first_viewer_toc import _viewer_fetch

OUT = Path("research_results/opendart_m20_original_viewer_quarter_table/counts.json")
MAX_OFFICIAL = 2
MAX_VIEWER = 5
MAX_TABLES = 2000
MAX_NODES = 800000
MAX_TEXT = 4 * 1024 * 1024
MAX_TABLE_TEXT = 2 * 1024 * 1024
MAX_CELL = 8192
AMOUNT = re.compile(r"^-?(?:0|[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+)(?:\.[0-9]+)?$")
LABELS = frozenset(
    re.sub(r"\s+", "", unicodedata.normalize("NFKC", label))
    for label in OPERATING_ROW_LABELS
)
HINT_KEYS = (
    "profit_candidate_tables",
    "profit_nested_candidate_tables",
    "profit_in_outer_table_with_nested_children",
    "profit_rows_with_two_numeric_peer_cells",
    "profit_rows_with_four_numeric_peer_cells",
    "profit_tables_with_three_month_header",
    "profit_tables_with_current_and_prior_quarter_headers",
    "profit_tables_with_complete_2022_q3_date_window",
    "profit_tables_with_complete_2021_q3_date_window",
    "profit_tables_with_both_complete_q3_date_windows",
    "profit_tables_with_explicit_cfs_income_heading",
    "profit_tables_with_currency_unit_lexical_hint",
)
NO_PIT = {
    "source_table_is_authoritative_cfs_statement": False,
    "original_2022_2021_three_month_cfs_profit_cells_verified": False,
    "original_filing_vintage_as_of_pit_verified": False,
    "historical_publication_instant_verified": False,
    "historical_corp_security_pit_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "raw_source_titles_dates_amounts_table_positions_or_ids_persisted": False,
    "ordering": "DISABLED",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s))


class TableHints(HTMLParser):
    """Direct table/frame scan, nested structures are separately ambiguous."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames = []
        self.tables = 0
        self.nodes = 0
        self.chars = 0
        self.counts = {k: 0 for k in HINT_KEYS}

    def _cell_end(self, frame):
        if frame["cell"] is not None:
            if len(frame["row"]) >= 150:
                raise SectionGap("TABLE_Q3_ROW_CELL_LIMIT")
            frame["row"].append(norm("".join(frame["cell"])))
            frame["cell"] = None

    def _row_end(self, frame):
        self._cell_end(frame)
        if frame["row"] and any(x in LABELS for x in frame["row"][:2]):
            frame["profit"] = True
            peers = sum(bool(AMOUNT.fullmatch(x)) for x in frame["row"][1:])
            frame["numeric2"] |= peers >= 2
            frame["numeric4"] |= peers >= 4
        frame["row"] = []

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise SectionGap("TABLE_Q3_NODE_LIMIT")
        if tag == "table":
            if len(self.frames) > 40 or self.tables + len(self.frames) >= MAX_TABLES:
                raise SectionGap("TABLE_Q3_TABLE_LIMIT")
            if self.frames:
                self.frames[-1]["has_child"] = True
            self.frames.append({
                "text": [], "nchars": 0, "row": [], "cell": None,
                "profit": False, "numeric2": False, "numeric4": False,
                "nested": bool(self.frames), "has_child": False,
            })
        elif tag == "tr" and self.frames:
            self._row_end(self.frames[-1])
        elif tag in ("td", "th") and self.frames:
            f = self.frames[-1]
            self._cell_end(f)
            f["cell"] = []

    def handle_data(self, data):
        self.chars += len(data)
        if self.chars > MAX_TEXT:
            raise SectionGap("TABLE_Q3_TEXT_LIMIT")
        for f in self.frames:
            f["nchars"] += len(data)
            if f["nchars"] > MAX_TABLE_TEXT:
                raise SectionGap("TABLE_Q3_TABLE_TEXT_LIMIT")
            f["text"].append(data)
        if self.frames and self.frames[-1]["cell"] is not None:
            f = self.frames[-1]
            if sum(len(x) for x in f["cell"]) + len(data) > MAX_CELL:
                raise SectionGap("TABLE_Q3_CELL_LIMIT")
            f["cell"].append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.frames:
            self._cell_end(self.frames[-1])
        elif tag == "tr" and self.frames:
            self._row_end(self.frames[-1])
        elif tag == "table":
            if not self.frames:
                raise SectionGap("TABLE_Q3_UNBALANCED")
            f = self.frames.pop()
            self._row_end(f)
            self.tables += 1
            if not f["profit"]:
                return
            body = norm("".join(f["text"]))
            full22 = _has_q3_period_window(body, 2022)
            full21 = _has_q3_period_window(body, 2021)
            flags = {
                "profit_candidate_tables": True,
                "profit_nested_candidate_tables": f["nested"],
                "profit_in_outer_table_with_nested_children": f["has_child"],
                "profit_rows_with_two_numeric_peer_cells": f["numeric2"],
                "profit_rows_with_four_numeric_peer_cells": f["numeric4"],
                "profit_tables_with_three_month_header": "3개월" in body,
                "profit_tables_with_current_and_prior_quarter_headers": (
                    "당분기" in body and "전분기" in body
                ),
                "profit_tables_with_complete_2022_q3_date_window": full22,
                "profit_tables_with_complete_2021_q3_date_window": full21,
                "profit_tables_with_both_complete_q3_date_windows": full22 and full21,
                "profit_tables_with_explicit_cfs_income_heading": any(
                    x in body for x in ("연결손익계산서", "연결포괄손익계산서")
                ),
                "profit_tables_with_currency_unit_lexical_hint": any(
                    x in body for x in ("단위:원", "단위:천원", "단위:백만원")
                ),
            }
            for key, present in flags.items():
                self.counts[key] += bool(present)

    def finish(self):
        if self.frames or self.tables == 0:
            raise SectionGap("TABLE_Q3_UNBALANCED")
        if any(x > self.counts["profit_candidate_tables"] for x in self.counts.values()):
            raise SectionGap("TABLE_Q3_COUNTS_INVALID")
        return {
            "all_tables": self.tables,
            **self.counts,
        }


def inspect(session, toc: str, first: str) -> dict:
    metas = _choose_first_edition_sections(toc, first)
    if len(metas) != 4:
        raise SectionGap("TABLE_Q3_FOUR_SECTIONS_REQUIRED")
    forms = []
    for meta in metas:
        scan = TableHints()
        scan.feed(_bounded_public_get(session, meta, first))
        scan.close()
        forms.append(scan.finish())
    sums = {key: sum(f[key] for f in forms) for key in HINT_KEYS}
    if sums["profit_candidate_tables"] > 10:
        raise SectionGap("TABLE_Q3_PROFIT_TABLE_DRIFT")
    return {
        "source_status": "FIRST_ORIGINAL_VIEWER_SAME_TABLE_Q3_SHAPE_ONLY",
        "first_original_financial_viewer_sections": len(forms),
        "total_viewer_tables_in_financial_sections": sum(f["all_tables"] for f in forms),
        **sums,
        "nested_original_tables_are_not_authoritatively_bound": True,
        "same_table_header_is_not_source_financial_semantics": True,
    }


def execute(session, key: str) -> dict:
    registry = _official_get(session, "corpCode.xml",
                             {"crtfc_key": key}, zip_response=True)
    issuer = _registry(registry).get(COHORT[5])
    if issuer is None:
        raise SectionGap("TABLE_Q3_FIXED_ISSUER_MISSING")
    begin, end = _window(2022)
    reports = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": issuer, "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    first = original_first_receipt(reports, 2022)
    toc = _viewer_fetch(session, first)
    return inspect(session, toc, first)


def run(session=None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    output = {
        "purpose": "FROZEN_M20_ORIGINAL_VIEWER_TABLE_PERIOD_TEXT_SHAPES",
        "fixed_cohort_slot": 5,
        "max_official_api_calls": MAX_OFFICIAL,
        "max_public_viewer_calls": MAX_VIEWER,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFE, **NO_PIT,
    }
    if not key:
        return output
    if session is None:
        import requests
        session = requests.Session()
    try:
        output.update(execute(session, key))
    except Exception as exc:
        allowed = {
            "TABLE_Q3_ROW_CELL_LIMIT", "TABLE_Q3_NODE_LIMIT",
            "TABLE_Q3_TABLE_LIMIT", "TABLE_Q3_TEXT_LIMIT",
            "TABLE_Q3_TABLE_TEXT_LIMIT", "TABLE_Q3_CELL_LIMIT",
            "TABLE_Q3_UNBALANCED", "TABLE_Q3_COUNTS_INVALID",
            "TABLE_Q3_FOUR_SECTIONS_REQUIRED",
            "TABLE_Q3_PROFIT_TABLE_DRIFT", "TABLE_Q3_FIXED_ISSUER_MISSING",
        }
        reason = str(exc) if type(exc) is SectionGap else ""
        output["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        output["failure_code"] = reason if reason in allowed else "FIRST_ORIGINAL_TABLE_ACCOUNTING_SOURCE_UNVERIFIED"
    return output


if __name__ == "__main__":
    evidence = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    print("M20_ORIGINAL_VIEWER_TABLE_Q3=" + json.dumps(evidence, sort_keys=True), flush=True)
