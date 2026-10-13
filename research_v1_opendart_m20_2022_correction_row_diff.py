"""Compare exact-label operating-profit ROW TEXT in first and amended SGML.

This is a diagnostic only, not a normalized CFS/account/quarter/period value
binding. Ephemeral row texts/numeric cells are never printed, written or
hashed into output; only bounded aggregate counts and difference booleans.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
import unicodedata
import zipfile

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_correction_source_pair import _source_pair
from research_v1_opendart_m20_2022_later_edition_census import LATER_BEGIN, AS_OF
from research_v1_opendart_m20_2022_source_proof import EXPECTED_ORIGINAL_DOCUMENT_SHA256
from research_v1_opendart_m20_2022_first_document_pilot import (
    _fetch_first_document, inspect_official_original_document,
    _decode_disclosure_markup, OPERATING_ROW_LABELS,
)
import hashlib

CORRECTED_ZIP_SHA256 = "606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30"
OUTPUT = Path("research_results/opendart_m20_2022_row_diff/counts.json")
MAX_CALLS = 5
MAX_CANDIDATES = 256
MAX_ROWS = 150000
MAX_HTML_NODES = 1000000
MAX_CELLS_PER_ROW = 150
MAX_CELL_LENGTH = 8192
NUMERIC = re.compile(r"^-?(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]+)?$")
SAFE_FALSE = (
    "normalized_cfs_operating_profit_changed_verified",
    "original_cfs_q3_2022_2021_three_month_profit_verified",
    "original_vs_amended_period_cell_lineage_verified",
    "full_correction_lineage_verified",
    "historical_publication_instant_pit_verified",
    "historical_corp_security_mapping_verified",
    "m20_feature_pit_admitted", "m20_performance_run_authorized",
    "independent_holdout_authorized", "champion_change_authorized",
    "real_orders_authorized", "funds_movement_authorized",
    "permissions_change_authorized",
    "raw_source_rows_values_or_identifiers_persisted",
)


class RowShapeGap(ValueError):
    """Bounded provider-independent error class."""


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


class _CandidateRows(HTMLParser):
    """Limited row/cell scanner. No financial authority inferred from matches."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = 0
        self.rows = 0
        self.in_row = False
        self.in_cell = False
        self.parts: list[str] = []
        self.cells: list[str] = []
        self.full = Counter()
        self.numeric = Counter()

    def _cell(self):
        if self.in_cell:
            if len(self.cells) >= MAX_CELLS_PER_ROW:
                raise RowShapeGap("ROW_CELL_COUNT_EXCEEDED")
            self.cells.append(_norm("".join(self.parts)))
            self.in_cell = False
            self.parts = []

    def _row(self):
        self._cell()
        if self.in_row:
            self.rows += 1
            if self.rows > MAX_ROWS:
                raise RowShapeGap("ROW_SCAN_BUDGET_EXCEEDED")
            if any(x in OPERATING_ROW_LABELS for x in self.cells[:2]):
                if sum(self.full.values()) >= MAX_CANDIDATES:
                    raise RowShapeGap("ROW_CANDIDATE_BUDGET_EXCEEDED")
                row = tuple(self.cells)
                # In-memory comparison only. Labels may occur in notes.
                self.full[row] += 1
                number_cells = tuple(x for x in self.cells[1:] if NUMERIC.fullmatch(x))
                self.numeric[(self.cells[0], number_cells)] += 1
            self.in_row = False
            self.cells = []

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > MAX_HTML_NODES:
            raise RowShapeGap("HTML_NODES_BUDGET_EXCEEDED")
        if tag == "tr":
            self._row()
            self.in_row = True
        elif tag in ("td", "th") and self.in_row:
            self._cell()
            self.in_cell = True

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self._cell()
        elif tag == "tr":
            self._row()

    def handle_data(self, data):
        if self.in_cell:
            if sum(map(len, self.parts)) + len(data) > MAX_CELL_LENGTH:
                raise RowShapeGap("ROW_CELL_TEXT_BUDGET_EXCEEDED")
            self.parts.append(data)

    def finish(self):
        self._row()
        if not self.full:
            raise RowShapeGap("NO_EXACT_OPERATING_ROW_CANDIDATES")
        return self.full, self.numeric


def _diagnostic_rows(raw: bytes, *, expected_digest: str) -> tuple[Counter, Counter]:
    if hashlib.sha256(raw).hexdigest() != expected_digest:
        raise RowShapeGap("DOCUMENT_SHA256_CHANGED")
    official = inspect_official_original_document(raw)
    if official.get("official_original_document_zip_received") is not True:
        raise RowShapeGap("DOCUMENT_ZIP_NOT_VALIDATED")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        markup = [x for x in archive.infolist() if x.filename.lower().endswith(
            (".xml", ".htm", ".html", ".xhtml")
        ) and not x.is_dir()]
        if len(markup) != 1 or markup[0].file_size > 32 * 1024 * 1024:
            raise RowShapeGap("DOCUMENT_MARKUP_CARDINALITY_UNVERIFIED")
        decoded = _decode_disclosure_markup(archive.read(markup[0]))
    if "<table" not in decoded.lower():
        raise RowShapeGap("DOCUMENT_TABLES_NOT_FOUND")
    parser = _CandidateRows()
    parser.feed(decoded)
    parser.close()
    return parser.finish()


def compare(raw_original: bytes, raw_corrected: bytes) -> dict:
    a, anum = _diagnostic_rows(raw_original, expected_digest=EXPECTED_ORIGINAL_DOCUMENT_SHA256)
    b, bnum = _diagnostic_rows(raw_corrected, expected_digest=CORRECTED_ZIP_SHA256)
    shared = sum((a & b).values())
    shared_numeric = sum((anum & bnum).values())
    return {
        "source_status": "ORIGINAL_CORRECTION_EXACT_OPERATING_ROW_SHAPE_COMPARE_ONLY",
        "first_edition_exact_label_row_candidates": sum(a.values()),
        "corrected_edition_exact_label_row_candidates": sum(b.values()),
        "identical_exact_label_row_candidates_multiset": shared,
        "exact_label_row_text_multisets_differ": a != b,
        "numeric_peer_shape_multisets_differ": anum != bnum,
        "identical_numeric_peer_row_candidates_multiset": shared_numeric,
        "financial_semantic_differences_still_unverified": True,
        "published_financial_amounts_disclosed": False,
    }


def execute(session, key: str) -> dict:
    registry = _official_get(session, "corpCode.xml", {"crtfc_key": key}, zip_response=True)
    company = _registry(registry).get(COHORT[5])
    if company is None:
        raise RowShapeGap("FIXED_ISSUER_MAPPING_UNVERIFIED")
    begin, end = _window(2022)
    first_index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": company, "bgn_de": begin,
        "end_de": end, "pblntf_ty": "A", "last_reprt_at": "N",
        "page_count": "100",
    })
    original_receipt = original_first_receipt(first_index, 2022)
    later_index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": company, "bgn_de": LATER_BEGIN,
        "end_de": AS_OF, "pblntf_ty": "A", "last_reprt_at": "N",
        "page_no": "1", "page_count": "100",
    })
    later_receipt = _source_pair(first_index, later_index, original_receipt)
    original = _fetch_first_document(session, key, original_receipt)
    amended = _fetch_first_document(session, key, later_receipt)
    return compare(original, amended)


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    result = {
        "purpose": "FROZEN_M20_2022_Q3_FIRST_AMENDED_OPERATING_ROW_DIAGNOSTIC",
        "fixed_cohort_slot": 5,
        "max_official_requests": MAX_CALLS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        "ordering": "DISABLED",
        **{x: False for x in SAFE_FALSE},
    }
    if not key:
        return result
    if session is None:
        import requests
        session = requests.Session()
    try:
        result.update(execute(session, key))
    except Exception as exc:
        allowed = {
            "DOCUMENT_SHA256_CHANGED", "DOCUMENT_ZIP_NOT_VALIDATED",
            "DOCUMENT_MARKUP_CARDINALITY_UNVERIFIED", "DOCUMENT_TABLES_NOT_FOUND",
            "ROW_CELL_COUNT_EXCEEDED", "ROW_SCAN_BUDGET_EXCEEDED",
            "HTML_NODES_BUDGET_EXCEEDED", "ROW_CANDIDATE_BUDGET_EXCEEDED",
            "ROW_CELL_TEXT_BUDGET_EXCEEDED", "NO_EXACT_OPERATING_ROW_CANDIDATES",
            "FIXED_ISSUER_MAPPING_UNVERIFIED",
        }
        why = str(exc) if type(exc) is RowShapeGap else ""
        result["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        result["failure_code"] = why if why in allowed else "OFFICIAL_CANDIDATE_ROW_SOURCE_UNVERIFIED"
    return result


if __name__ == "__main__":
    answer = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(answer, indent=2, sort_keys=True), encoding="utf-8")
    print("M20_ORIGINAL_CORRECTED_ROW_DIFF=" + json.dumps(answer, sort_keys=True), flush=True)
