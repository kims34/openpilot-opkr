"""2022 first-original SGML accounting-heading neighborhood audit, SOURCE-ONLY.

This fixed slot-5 probe uses exactly corpCode.xml, the first-original Q3
list.json index and the SHA-pinned original document.xml. An intentionally
broader 12k-character preceding text window and all-table period/header
scan are diagnostics ONLY. They do not establish CFS attribution, exact
standalone 3-month numeric cells, intraday disclosure, or M20 PIT.
Nothing from the original SGML, issuer/receipt or numerical cells persists.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import hashlib
import io
import json
import os
import re
import unicodedata
import zipfile

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_source_proof import EXPECTED_ORIGINAL_DOCUMENT_SHA256
from research_v1_opendart_m20_2022_first_document_pilot import (
    _decode_disclosure_markup, _fetch_first_document,
    inspect_official_original_document, _has_q3_period_window,
    OPERATING_ROW_LABELS,
)

OUTPUT = Path("research_results/opendart_m20_first_original_neighborhood/counts.json")
MAX_OFFICIAL_CALLS = 3
MAX_TABLES = 4000
MAX_NODES = 1000000
MAX_TEXT = 35 * 1024 * 1024
MAX_TABLE_TEXT = 4 * 1024 * 1024
MAX_CELL = 8192
MAX_PREFIX = 12000
NUMERIC = re.compile(r"^-?(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)(?:\.[0-9]+)?$")
SAFETY = {
    "original_2022_2021_cfs_quarter_facts_semantically_bound": False,
    "first_published_operating_profit_values_verified": False,
    "original_xbrl_available_verified": False,
    "original_period_statement_currency_unit_verified": False,
    "historical_original_filing_publication_instant_verified": False,
    "historical_issuer_security_pit_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "raw_values_labels_company_receipts_or_source_persisted": False,
    "ordering": "DISABLED",
}

class SGMLGap(ValueError):
    """Sanitized, fixed reason code only."""


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


class Neighborhood(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames = []
        self.outside = ""
        self.cell = None
        self.row = []
        self.in_row = False
        self.nodes = 0
        self.total_input = 0
        self.tables = 0
        self.candidates = 0
        self.counts = {key: 0 for key in (
            "numeric_peers_at_least_two",
            "numeric_peers_at_least_four",
            "table_contains_exact_cfs_title",
            "prefix_2400_exact_cfs_title",
            "prefix_12000_exact_cfs_title",
            "table_contains_three_month_literal",
            "table_contains_quarter_literal",
            "table_contains_current_prior_quarter_terms",
            "table_contains_q3_2022_full_window",
            "table_contains_q3_2021_full_window",
            "table_contains_both_q3_full_windows",
            "prefix_12000_contains_three_month_literal",
            "prefix_12000_contains_q3_2022_full_window",
            "prefix_12000_contains_q3_2021_full_window",
            "table_contains_cfs_and_3month_and_both_periods",
            "operating_row_cells_at_least_five",
        )}

    def _cell_end(self):
        if self.cell is not None:
            if len(self.row) >= 150:
                raise SGMLGap("CELL_COUNT_BUDGET")
            self.row.append(normalized("".join(self.cell)))
            self.cell = None

    def _row_end(self):
        self._cell_end()
        if self.in_row and self.frames:
            frame = self.frames[-1]
            if any(x in OPERATING_ROW_LABELS for x in self.row[:2]):
                frame["operating"] += 1
                numbers = sum(bool(NUMERIC.fullmatch(x)) for x in self.row[1:])
                frame["two"] |= numbers >= 2
                frame["four"] |= numbers >= 4
                frame["five_cells"] |= len(self.row) >= 5
        self.in_row = False
        self.row = []

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise SGMLGap("HTML_NODE_BUDGET")
        if tag == "table":
            if len(self.frames) >= 40 or self.tables + len(self.frames) >= MAX_TABLES:
                raise SGMLGap("TABLE_COUNT_BUDGET")
            self.frames.append({
                "prefix": normalized(self.outside[-MAX_PREFIX:]),
                "parts": [], "operating": 0,
                "two": False, "four": False, "five_cells": False,
            })
        elif tag == "tr" and self.frames:
            self._row_end()
            self.in_row = True
        elif tag in ("td", "th") and self.frames and self.in_row:
            self._cell_end()
            self.cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self._cell_end()
        elif tag == "tr":
            self._row_end()
        elif tag == "table":
            self._row_end()
            if not self.frames:
                raise SGMLGap("TABLE_NESTING_INVALID")
            frame = self.frames.pop()
            self.tables += 1
            if self.tables > MAX_TABLES:
                raise SGMLGap("TABLE_COUNT_BUDGET")
            if not frame["operating"]:
                return
            self.candidates += 1
            txt = normalized("".join(frame["parts"]))
            before = frame["prefix"]
            if len(txt) > MAX_TABLE_TEXT:
                raise SGMLGap("TABLE_TEXT_BUDGET")
            cfs = ("연결손익계산서", "연결포괄손익계산서")
            t22 = _has_q3_period_window(txt, 2022)
            t21 = _has_q3_period_window(txt, 2021)
            evidence = {
                "numeric_peers_at_least_two": frame["two"],
                "numeric_peers_at_least_four": frame["four"],
                "table_contains_exact_cfs_title": any(k in txt for k in cfs),
                "prefix_2400_exact_cfs_title": any(k in before[-2400:] for k in cfs),
                "prefix_12000_exact_cfs_title": any(k in before for k in cfs),
                "table_contains_three_month_literal": "3개월" in txt,
                "table_contains_quarter_literal": any(k in txt for k in
                    ("제3분기", "3분기", "당분기", "전분기")),
                "table_contains_current_prior_quarter_terms": (
                    "당분기" in txt and "전분기" in txt
                ),
                "table_contains_q3_2022_full_window": t22,
                "table_contains_q3_2021_full_window": t21,
                "table_contains_both_q3_full_windows": t22 and t21,
                "prefix_12000_contains_three_month_literal": "3개월" in before,
                "prefix_12000_contains_q3_2022_full_window":
                    _has_q3_period_window(before, 2022),
                "prefix_12000_contains_q3_2021_full_window":
                    _has_q3_period_window(before, 2021),
                "table_contains_cfs_and_3month_and_both_periods":
                    any(k in txt for k in cfs) and "3개월" in txt and t22 and t21,
                "operating_row_cells_at_least_five": frame["five_cells"],
            }
            for key, v in evidence.items():
                self.counts[key] += bool(v)

    def handle_data(self, data):
        self.total_input += len(data)
        if self.total_input > MAX_TEXT:
            raise SGMLGap("HTML_TEXT_BUDGET")
        if self.frames:
            for frame in self.frames:
                if sum(map(len, frame["parts"])) + len(data) > MAX_TABLE_TEXT:
                    raise SGMLGap("TABLE_TEXT_BUDGET")
                frame["parts"].append(data)
        else:
            self.outside = (self.outside + data)[-MAX_PREFIX:]
        if self.cell is not None:
            if sum(map(len, self.cell)) + len(data) > MAX_CELL:
                raise SGMLGap("CELL_TEXT_BUDGET")
            self.cell.append(data)

    def finish(self):
        if self.frames or not self.tables:
            raise SGMLGap("TABLE_NESTING_INVALID")
        if self.candidates != 15:
            raise SGMLGap("OPERATING_TABLE_CARDINALITY_CHANGED")
        if any(x > self.candidates for x in self.counts.values()):
            raise SGMLGap("SOURCE_CONTEXT_COUNTER_INVALID")
        return {
            "source_status": "PINNED_ORIGINAL_SGML_HEADING_PERIOD_DIAGNOSTIC_ONLY",
            "original_sgml_tables_examined": self.tables,
            "exact_label_operating_table_candidates": self.candidates,
            **self.counts,
            "heading_proximity_is_authoritative_statement_identity": False,
            "period_text_proximity_is_accounting_fact": False,
            "actual_q3_cfs_quarter_values_unverified": True,
        }


def inspect(raw: bytes) -> dict:
    if hashlib.sha256(raw).hexdigest() != EXPECTED_ORIGINAL_DOCUMENT_SHA256:
        raise SGMLGap("FIRST_ORIGINAL_ZIP_SHA_DRIFT")
    official = inspect_official_original_document(raw)
    if official.get("official_original_document_zip_received") is not True:
        raise SGMLGap("FIRST_ORIGINAL_ZIP_INVALID")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        items = [x for x in z.infolist()
                 if not x.is_dir() and x.filename.lower().endswith(
                     (".xml", ".htm", ".html", ".xhtml"))]
        if len(items) != 1 or items[0].file_size > 32*1024*1024:
            raise SGMLGap("FIRST_ORIGINAL_MARKUP_CARDINALITY")
        content = _decode_disclosure_markup(z.read(items[0]))
    parser = Neighborhood()
    parser.feed(content)
    parser.close()
    return parser.finish()


def execute(session, key: str) -> dict:
    registry = _official_get(session, "corpCode.xml", {"crtfc_key": key}, zip_response=True)
    company = _registry(registry).get(COHORT[5])
    if company is None:
        raise SGMLGap("FIXED_ISSUER_NOT_FOUND")
    start, end = _window(2022)
    index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": company, "bgn_de": start, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    first = original_first_receipt(index, 2022)
    return inspect(_fetch_first_document(session, key, first))


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    report = {
        "purpose": "FROZEN_M20_SLOT5_2022_FIRST_ORIGINAL_SGML_SEMANTIC_NEIGHBORHOOD",
        "fixed_cohort_slot": 5,
        "max_official_requests": MAX_OFFICIAL_CALLS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFETY,
    }
    if not key:
        return report
    if session is None:
        import requests
        session = requests.Session()
    try:
        report.update(execute(session, key))
    except Exception as exc:
        safe = {
            "FIRST_ORIGINAL_ZIP_SHA_DRIFT", "FIRST_ORIGINAL_ZIP_INVALID",
            "FIRST_ORIGINAL_MARKUP_CARDINALITY", "FIXED_ISSUER_NOT_FOUND",
            "HTML_NODE_BUDGET", "TABLE_COUNT_BUDGET", "TABLE_TEXT_BUDGET",
            "TABLE_NESTING_INVALID", "HTML_TEXT_BUDGET", "CELL_COUNT_BUDGET",
            "CELL_TEXT_BUDGET", "OPERATING_TABLE_CARDINALITY_CHANGED",
            "SOURCE_CONTEXT_COUNTER_INVALID",
        }
        reason = str(exc) if type(exc) is SGMLGap else ""
        report["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        report["source_gap_reason"] = reason if reason in safe else "FIRST_ORIGINAL_SOURCE_OR_PARSE_UNVERIFIED"
    return report


if __name__ == "__main__":
    report = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_2022_ORIGINAL_SGML_CONTEXT=" + json.dumps(report, sort_keys=True), flush=True)
