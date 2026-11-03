"""M20 2022 earliest filed OpenDART SGML tag/section ancestry census.

Different from repeated adjacent-word scans: count explicit SGML tag/section
nesting of exact-label operating income table rows. Open/close nesting is
diagnostic, never legal accounting statement attribution or financial PIT.
No provider text, financial amounts, identifiers, tag attributes, report names
or API credentials are written or printed. Fixed slot 5, first edition only,
maximum three official source calls and exact pinned source ZIP SHA256.
"""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import hashlib
import io
import json
import os
from pathlib import Path
import zipfile
import re
import unicodedata

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_source_proof import EXPECTED_ORIGINAL_DOCUMENT_SHA256
from research_v1_opendart_m20_2022_first_document_pilot import (
    _fetch_first_document, _decode_disclosure_markup,
    inspect_official_original_document, OPERATING_ROW_LABELS,
)

OUTPUT = Path("research_results/opendart_m20_original_tag_ancestry/counts.json")
ALLOWED_TAGS = frozenset(("document", "section", "subsection", "article",
                           "body", "div", "title", "table", "tr",
                           "h1", "h2", "h3", "head", "acont", "p"))
SCOPE_TAGS = frozenset(("section", "subsection", "article", "document"))
MAX_NODES = 1_000_000
MAX_TABLES = 4000
MAX_NEST = 80
MAX_ROW_CELLS = 150
MAX_CELL_CHARS = 8192
MAX_HEADING_CHARS = 512
MAX_TEXT_CHARS = 35_000_000
MAX_CALLS = 3
SAFETY = {
    "first_original_cfs_statement_ancestry_verified": False,
    "2022_and_2021_q3_three_month_cfs_operating_profit_verified": False,
    "sgml_section_title_is_authoritative_accounting_statement": False,
    "xbrl_2022_first_report_available_verified": False,
    "historical_filing_publication_instant_verified": False,
    "historical_corp_security_mapping_pit_verified": False,
    "historical_correction_cell_lineage_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "raw_source_amounts_identifiers_headings_or_credentials_saved": False,
    "ordering": "DISABLED",
}


class SectionGap(ValueError):
    """Only fixed redacted reason codes allowed outside the parser."""


def norm(s: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s))


def heading_shape(s: str) -> str:
    """Predeclared categories only; never print original title strings."""
    compact = norm(s)
    if "연결포괄손익계산서" in compact or "연결손익계산서" in compact:
        return "exact_cfs_income"
    if "포괄손익계산서" in compact or "손익계산서" in compact:
        return "income_scope_unspecified"
    if "재무제표" in compact:
        return "financial_statement_general"
    if "주석" in compact:
        return "notes"
    return "other"


class SectionStructure(HTMLParser):
    """Counts only explicit structural SGML containers and exact row labels."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = Counter()
        self.nodes = 0
        self.chars = 0
        self.sections = []
        self.table_depth = 0
        self.tables = 0
        self.row_open = False
        self.cell = None
        self.cells = []
        self.heading = None
        self.heading_kind_counts = Counter()
        self.operating_rows = 0
        self.earnings_structures = Counter()
        self.ambiguous_scope_closes = 0

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise SectionGap("SGML_NODE_BUDGET_EXCEEDED")
        if tag in ALLOWED_TAGS:
            self.tags[tag] += 1
        if tag in SCOPE_TAGS:
            if len(self.sections) >= MAX_NEST:
                raise SectionGap("SGML_SCOPE_DEPTH_BUDGET_EXCEEDED")
            self.sections.append({"tag": tag, "heading": "unlabeled"})
        if tag == "title":
            self.heading = []
        if tag == "table":
            self.table_depth += 1
            self.tables += 1
            if self.table_depth > MAX_NEST or self.tables > MAX_TABLES:
                raise SectionGap("SGML_TABLE_BUDGET_EXCEEDED")
        if tag == "tr" and self.table_depth:
            self._finish_row()
            self.row_open = True
        if tag in ("td", "th") and self.row_open and self.table_depth:
            self._finish_cell()
            self.cell = []

    def _finish_cell(self):
        if self.cell is not None:
            if len(self.cells) >= MAX_ROW_CELLS:
                raise SectionGap("SGML_ROW_CELL_BUDGET_EXCEEDED")
            self.cells.append(norm("".join(self.cell)))
            self.cell = None

    def _finish_row(self):
        self._finish_cell()
        if self.row_open and any(x in OPERATING_ROW_LABELS for x in self.cells[:2]):
            self.operating_rows += 1
            self.earnings_structures["any_scoped_container"] += bool(self.sections)
            self.earnings_structures["explicit_section_or_subsection"] += any(
                x["tag"] in ("section", "subsection") for x in self.sections
            )
            self.earnings_structures["only_document_or_article_ancestry"] += bool(
                self.sections
            ) and not any(x["tag"] in ("section", "subsection") for x in self.sections)
            self.earnings_structures["explicit_scoped_cfs_title"] += any(
                x["heading"] == "exact_cfs_income" for x in self.sections
            )
            self.earnings_structures["explicit_scoped_generic_financial_title"] += any(
                x["heading"] == "financial_statement_general" for x in self.sections
            )
            self.earnings_structures["explicit_scoped_notes_title"] += any(
                x["heading"] == "notes" for x in self.sections
            )
            self.earnings_structures["within_nested_table"] += self.table_depth > 1
            self.earnings_structures["no_explicit_scope"] += not self.sections
        self.row_open = False
        self.cells = []

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self._finish_cell()
        elif tag == "tr":
            self._finish_row()
        elif tag == "table":
            self._finish_row()
            if self.table_depth == 0:
                raise SectionGap("SGML_TABLE_NESTING_UNVERIFIED")
            self.table_depth -= 1
        elif tag == "title" and self.heading is not None:
            category = heading_shape("".join(self.heading))
            self.heading_kind_counts[category] += 1
            if self.sections:
                self.sections[-1]["heading"] = category
            self.heading = None
        elif tag in SCOPE_TAGS:
            if not self.sections:
                self.ambiguous_scope_closes += 1
            elif self.sections[-1]["tag"] != tag:
                self.ambiguous_scope_closes += 1
                # On out-of-order SGML endings ancestry is unknown, not safe.
                self.sections.clear()
            else:
                self.sections.pop()

    def handle_data(self, data):
        self.chars += len(data)
        if self.chars > MAX_TEXT_CHARS:
            raise SectionGap("SGML_TEXT_BUDGET_EXCEEDED")
        if self.heading is not None:
            if sum(map(len, self.heading)) + len(data) > MAX_HEADING_CHARS:
                raise SectionGap("SGML_HEADING_BUDGET_EXCEEDED")
            self.heading.append(data)
        if self.cell is not None:
            if sum(map(len, self.cell)) + len(data) > MAX_CELL_CHARS:
                raise SectionGap("SGML_CELL_BUDGET_EXCEEDED")
            self.cell.append(data)

    def finish(self):
        self._finish_row()
        if self.table_depth or self.sections or self.heading is not None:
            raise SectionGap("SGML_UNCLOSED_SCOPE_OR_TABLE")
        if self.ambiguous_scope_closes:
            raise SectionGap("SGML_SCOPE_STRUCTURE_AMBIGUOUS")
        if self.operating_rows != 15:
            raise SectionGap("SGML_OPERATING_ROW_CANDIDATES_DRIFTED")
        if self.tables != 1570:
            raise SectionGap("SGML_SOURCE_TABLE_COUNT_DRIFTED")
        return {
            "source_status": "FIRST_ORIGINAL_SGML_EXPLICIT_TAG_STRUCTURE_ONLY",
            "first_original_table_tags_seen": self.tables,
            "first_original_exact_operating_row_candidates": self.operating_rows,
            **{f"tag_{tag}_start_count": self.tags[tag] for tag in sorted(ALLOWED_TAGS)},
            **{f"explicit_title_category_{category}_count": self.heading_kind_counts[category]
               for category in ("exact_cfs_income", "income_scope_unspecified",
                                "financial_statement_general", "notes", "other")},
            **{f"operating_candidate_{key}_count": self.earnings_structures[key]
               for key in ("any_scoped_container", "explicit_section_or_subsection",
                           "only_document_or_article_ancestry",
                           "explicit_scoped_cfs_title",
                           "explicit_scoped_generic_financial_title",
                           "explicit_scoped_notes_title", "within_nested_table",
                           "no_explicit_scope")},
            "explicit_scope_tag_presence_does_not_establish_financial_values": True,
        }


def inspect(original: bytes) -> dict:
    if hashlib.sha256(original).hexdigest() != EXPECTED_ORIGINAL_DOCUMENT_SHA256:
        raise SectionGap("PINNED_ORIGINAL_ARCHIVE_SHA_DRIFT")
    if inspect_official_original_document(original).get(
        "official_original_document_zip_received"
    ) is not True:
        raise SectionGap("ORIGINAL_ARCHIVE_INTEGRITY_UNVERIFIED")
    with zipfile.ZipFile(io.BytesIO(original)) as zipfile_obj:
        entries = [entry for entry in zipfile_obj.infolist()
                   if not entry.is_dir() and entry.filename.lower().endswith(
                       (".xml", ".htm", ".html", ".xhtml"))]
        if len(entries) != 1 or entries[0].file_size > 32*1024*1024:
            raise SectionGap("ORIGINAL_LEGACY_SGML_MEMBER_INVALID")
        text = _decode_disclosure_markup(zipfile_obj.read(entries[0]))
    scanner = SectionStructure()
    scanner.feed(text)
    scanner.close()
    return scanner.finish()


def execute(session, key: str) -> dict:
    registry = _official_get(session, "corpCode.xml", {"crtfc_key": key},
                             zip_response=True)
    corp = _registry(registry).get(COHORT[5])
    if corp is None:
        raise SectionGap("COHORT_CORP_MAPPING_INVALID")
    begin, end = _window(2022)
    first = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": corp, "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    receipt = original_first_receipt(first, 2022)
    return inspect(_fetch_first_document(session, key, receipt))


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    result = {
        "purpose": "FROZEN_SLOT5_2022_Q3_FIRST_FILED_SGML_TAG_ANCESTRY",
        "fixed_cohort_slot": 5,
        "max_official_requests": MAX_CALLS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFETY,
    }
    if not key:
        return result
    if session is None:
        import requests
        session = requests.Session()
    try:
        result.update(execute(session, key))
    except Exception as exc:
        known = {
            "SGML_NODE_BUDGET_EXCEEDED", "SGML_SCOPE_DEPTH_BUDGET_EXCEEDED",
            "SGML_TABLE_BUDGET_EXCEEDED", "SGML_ROW_CELL_BUDGET_EXCEEDED",
            "SGML_TABLE_NESTING_UNVERIFIED", "SGML_HEADING_BUDGET_EXCEEDED",
            "SGML_TEXT_BUDGET_EXCEEDED", "SGML_CELL_BUDGET_EXCEEDED",
            "SGML_UNCLOSED_SCOPE_OR_TABLE", "SGML_SCOPE_STRUCTURE_AMBIGUOUS",
            "SGML_OPERATING_ROW_CANDIDATES_DRIFTED",
            "SGML_SOURCE_TABLE_COUNT_DRIFTED", "PINNED_ORIGINAL_ARCHIVE_SHA_DRIFT",
            "ORIGINAL_ARCHIVE_INTEGRITY_UNVERIFIED",
            "ORIGINAL_LEGACY_SGML_MEMBER_INVALID", "COHORT_CORP_MAPPING_INVALID",
        }
        reason = str(exc) if type(exc) is SectionGap else ""
        result["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        result["failure_code"] = reason if reason in known else "FIRST_ORIGINAL_SGML_SCOPE_NOT_PROVEN"
    return result


if __name__ == "__main__":
    x = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(x, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_ORIGINAL_SGML_TAG_ANCESTRY=" + json.dumps(x, sort_keys=True), flush=True)
