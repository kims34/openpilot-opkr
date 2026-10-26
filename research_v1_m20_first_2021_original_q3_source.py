"""Read-only independent 2021-Q3 ORIGINAL filing for fixed M20 slot 5.

This *new year* is deliberately isolated from the frozen 2022/2023 cohorts:
never modify COHORT, frozen strategy, Q3 original selector, or trading.
At most THREE approved official reads: corpCode.xml, one fully paginated
2021-10-01..2022-02-28 list.json, then exact earliest first-edition
document.xml. ZIP is integrity-read only and discarded; SHA256 and bounded
table/header COUNT hints may be saved. First-2021 original evidence does NOT
by itself bind the 2022 original report's 2021 comparative numeric cell:
no original financial amount, original CFS statement, monetary unit, vintage
as-of clock, historical issuer/security PIT, performance or trading admitted.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry
from research_v1_opendart_m20_2022_first_document_pilot import (
    _fetch_first_document, inspect_original_document_layout,
)

OUT = Path("research_results/opendart_m20_first_2021_q3_original/source_only.json")
SLOT = 5
YEAR = 2021
START, END = "20211001", "20220228"
MAX_OFFICIAL_GETS = 3
# First independent official original source validation #40262282075.
# This pins the exact submitted-document ZIP bytes, NOT earnings values.
EXPECTED_FIRST_2021_DOCUMENT_SHA256 = (
    "8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625"
)
MAX_ROWS = 100
DATE = re.compile(r"[0-9]{8}\Z")
RECEIPT = re.compile(r"[0-9]{14}\Z")
CORP = re.compile(r"[0-9]{8}\Z")
TITLE = "분기보고서 (2021.09)"
PREFIXES = {
    TITLE: "ORIGINAL",
    "[기재정정]" + TITLE: "CORRECTION",
    "[첨부정정]" + TITLE: "CORRECTION",
    "[첨부추가]" + TITLE: "ATTACHMENT",
}
BLOCKED = {
    "original_2021_q3_three_month_cfs_profit_cell_verified": False,
    "first_2022_q3_report_2021_comparator_cell_verified": False,
    "2021_vs_2022_original_comparator_amounts_verified": False,
    "original_financial_xbrl_attested": False,
    "2021_first_publication_instant_verified": False,
    "2022_first_publication_instant_verified": False,
    "historical_issuer_security_pit_verified": False,
    "historical_market_session_pit_verified": False,
    "full_2021_amendment_vintage_chain_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "original_document_amounts_receipts_company_ids_dates_or_raw_zip_saved": False,
    "ordering": "DISABLED",
}


class First2021Gap(ValueError):
    """Fixed public-safe failure labels only, never provider error bodies."""


def _day(value: str) -> date:
    if type(value) is not str or not DATE.fullmatch(value):
        raise First2021Gap("FIRST_2021_FILING_DAY_INVALID")
    try:
        return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
    except ValueError:
        raise First2021Gap("FIRST_2021_FILING_DAY_INVALID") from None


def earliest_first_receipt(payload: dict, *, issuer: str) -> tuple[str, int]:
    """Demand a complete initial-period source page, no silent amendments."""
    if type(issuer) is not str or not CORP.fullmatch(issuer):
        raise First2021Gap("FIRST_2021_CURRENT_REGISTRY_ID_INVALID")
    if type(payload) is not dict or payload.get("status") != "000":
        raise First2021Gap("FIRST_2021_FILING_LIST_UNAVAILABLE")
    def count(k: str) -> int:
        v = payload.get(k)
        if type(v) is int and 0 <= v <= MAX_ROWS:
            return v
        if type(v) is str and re.fullmatch(r"(0|[1-9][0-9]*)", v):
            n = int(v)
            if 0 <= n <= MAX_ROWS:
                return n
        raise First2021Gap("FIRST_2021_LIST_PAGINATION_INVALID")
    count_rows = count("total_count")
    count_pages = count("total_page")
    page = count("page_no")
    records = payload.get("list")
    if (not 1 <= count_rows <= MAX_ROWS or count_pages != 1 or page != 1
            or type(records) is not list or len(records) != count_rows):
        raise First2021Gap("FIRST_2021_LIST_PAGINATION_NOT_EXHAUSTIVE")
    seen = set()
    matching = []
    for row in records:
        if type(row) is not dict:
            raise First2021Gap("FIRST_2021_LIST_ROW_INVALID")
        number, submitted, company, title = (
            row.get("rcept_no"), row.get("rcept_dt"), row.get("corp_code"),
            row.get("report_nm"),
        )
        if (type(number) is not str or not RECEIPT.fullmatch(number)
                or number in seen or type(title) is not str
                or type(submitted) is not str or company != issuer):
            raise First2021Gap("FIRST_2021_LIST_ISSUER_OR_RECEIPT_INVALID")
        seen.add(number)
        filing = _day(submitted)
        if (not _day(START) <= filing <= _day(END)
                or number[:8] != submitted):
            raise First2021Gap("FIRST_2021_LIST_DATE_OR_WINDOW_INVALID")
        if TITLE in title:
            if filing <= date(2021, 9, 30):
                raise First2021Gap("FIRST_2021_REPORT_PRECEDES_Q3")
            edition = PREFIXES.get(title.strip())
            if edition is None:
                raise First2021Gap("FIRST_2021_UNCLASSIFIED_EDITION")
            matching.append((filing, number, edition, row))
    if not matching:
        raise First2021Gap("FIRST_2021_ORIGINAL_REPORT_MISSING")
    earliest = min(m[0] for m in matching)
    first = [m for m in matching if m[0] == earliest]
    if len(first) != 1 or first[0][2] != "ORIGINAL":
        raise First2021Gap("FIRST_2021_SAME_DAY_OR_AMENDED_AMBIGUOUS")
    if "철" in (first[0][3].get("rm") or ""):
        raise First2021Gap("FIRST_2021_WITHDRAWN_ORIGINAL")
    for filing, _, kind, _ in matching:
        if filing > earliest and kind == "ORIGINAL":
            raise First2021Gap("FIRST_2021_MULTIPLE_ORIGINAL_EDITION")
    return first[0][1], len(matching)


def execute(session, key: str) -> dict:
    registry = _official_get(session, "corpCode.xml",
                             {"crtfc_key": key}, zip_response=True)
    issuer = _registry(registry).get(COHORT[SLOT])
    if issuer is None:
        raise First2021Gap("FIRST_2021_FIXED_ISSUER_REGISTRY_MISSING")
    source_index = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": issuer, "bgn_de": START,
        "end_de": END, "pblntf_ty": "A", "last_reprt_at": "N",
        "page_no": "1", "page_count": str(MAX_ROWS),
    })
    first, edition_count = earliest_first_receipt(source_index, issuer=issuer)
    original_zip = _fetch_first_document(session, key, first)
    source_hash = hashlib.sha256(original_zip).hexdigest()
    if source_hash != EXPECTED_FIRST_2021_DOCUMENT_SHA256:
        # File repackage/content drift is NOT silently treated as the
        # original financial vintage. Do not emit the unexpected SHA.
        raise First2021Gap("FIRST_2021_DOCUMENT_SHA256_DRIFT")
    original = inspect_original_document_layout(original_zip)
    if (original.get("official_original_document_zip_received") is not True
            or original.get("zip_crc_and_bounded_read_completed") is not True):
        raise First2021Gap("FIRST_2021_DOCUMENT_ZIP_INTEGRITY_NOT_PROVEN")
    return {
        "source_status": "FIRST_SUBMITTED_2021_Q3_DOCUMENT_SOURCE_SHAPE_ONLY",
        "2021_initial_report_index_complete_single_page": True,
        "original_2021_first_edition_unambiguous": True,
        "initial_2021_q3_versions_seen": edition_count,
        "2021_original_zip_sha256": source_hash,
        "2021_original_archive_integrity_checked": True,
        "2021_original_structured_markup_files": original[
            "structured_markup_entries_inspected"],
        "2021_original_non_xml_sgml_files": original[
            "non_xml_sgml_html_layout_entries"],
        "2021_original_table_shapes": original["source_tables_examined"],
        "2021_original_operating_label_table_candidates": original[
            "tables_with_exact_operating_row"],
        "2021_original_operating_labels_with_q3_2021_period_same_table": original[
            "tables_profit_2021_q3_window_in_first_twelve_rows"],
        "2021_original_operating_labels_with_three_month_word_same_table": original[
            "tables_with_operating_row_and_three_month_header"],
        "original_2021_q3_comparative_is_not_bound_to_2022": True,
    }


def run(session=None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    evidence = {
        "purpose": "FIXED_M20_SLOT5_INDEPENDENT_2021_Q3_FIRST_ORIGINAL_ONLY",
        "fixed_cohort_slot": SLOT,
        "max_authenticated_official_requests": MAX_OFFICIAL_GETS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **BLOCKED,
    }
    if not key:
        return evidence
    if session is None:
        import requests
        session = requests.Session()
    try:
        evidence.update(execute(session, key))
    except Exception as e:
        allowed = {
            "FIRST_2021_CURRENT_REGISTRY_ID_INVALID",
            "FIRST_2021_FILING_LIST_UNAVAILABLE",
            "FIRST_2021_LIST_PAGINATION_INVALID",
            "FIRST_2021_LIST_PAGINATION_NOT_EXHAUSTIVE",
            "FIRST_2021_LIST_ROW_INVALID",
            "FIRST_2021_LIST_ISSUER_OR_RECEIPT_INVALID",
            "FIRST_2021_LIST_DATE_OR_WINDOW_INVALID",
            "FIRST_2021_REPORT_PRECEDES_Q3",
            "FIRST_2021_UNCLASSIFIED_EDITION",
            "FIRST_2021_ORIGINAL_REPORT_MISSING",
            "FIRST_2021_SAME_DAY_OR_AMENDED_AMBIGUOUS",
            "FIRST_2021_WITHDRAWN_ORIGINAL",
            "FIRST_2021_MULTIPLE_ORIGINAL_EDITION",
            "FIRST_2021_FIXED_ISSUER_REGISTRY_MISSING",
            "FIRST_2021_DOCUMENT_ZIP_INTEGRITY_NOT_PROVEN",
            "FIRST_2021_DOCUMENT_SHA256_DRIFT",
        }
        reason = str(e) if type(e) is First2021Gap else ""
        evidence["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        evidence["source_gap_reason"] = reason if reason in allowed else "FIRST_2021_SOURCE_NOT_VERIFIED"
    return evidence


if __name__ == "__main__":
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2),
                   encoding="utf-8")
    print("M20_2021_FIRST_ORIGINAL=" +
          json.dumps(result, sort_keys=True), flush=True)
