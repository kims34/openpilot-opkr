"""M20 first-filed 2022 Q3 official document provenance snapshot (SOURCE ONLY).

One immutable, predeclared cohort slot (5); exactly the existing approved
OpenDART corpCode.xml, list.json and document.xml sequence (max 3 requests).
Reuses the existing strict index, ZIP integrity and SGML layout probes.
Outputs only bounded non-financial evidence plus a ZIP SHA-256 fingerprint.
A date-only receipt index is NEVER an intraday PIT timestamp; the bounded
initial search window is NEVER a completed later-correction history.
No financial amounts, company or receipt IDs, raw source, price, labels,
market-data access, HOLDOUT, performance or broker actions are output.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import (
    COHORT, _registry, _window,
)
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import (
    original_first_receipt,
)
from research_v1_opendart_m20_2022_first_document_pilot import (
    _fetch_first_document, inspect_original_document_layout,
    OriginalDocumentGap,
)

SLOT = 5
YEAR = 2022
MAX_CALLS = 3
# Pinned from the independent successful official first-filing run #38381866190.
# A ZIP digest change may be a provider repackage, revised content, or a
# changed retrieval; none is silently admitted as the audited original.
EXPECTED_ORIGINAL_DOCUMENT_SHA256 = (
    "56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb"
)
OUTPUT = Path("research_results/opendart_m20_2022_provenance/proof.json")
SAFE_FALSE = (
    "is_standardized_financial_xbrl",
    "original_cfs_q3_three_month_operating_profit_verified",
    "original_q3_qminus4_comparability_verified",
    "historical_corp_security_mapping_verified",
    "historical_publication_instant_pit_verified",
    "full_correction_lineage_verified",
    "complete_universe_historical_panel_verified",
    "market_cap_and_tradability_verified",
    "m20_feature_pit_admitted",
    "m20_performance_run_authorized",
    "independent_holdout_authorized",
    "champion_change_authorized",
    "real_orders_authorized",
    "funds_movement_authorized",
    "permissions_change_authorized",
    "raw_document_identifiers_or_financial_values_persisted",
)

class SourceGap(ValueError):
    """Non-sensitive error code only."""


def _bounded_revision_shape(index: dict, receipt: str) -> dict:
    """Inspect same-period filing matches; never claim full correction lineage."""
    rows = index.get("list")
    if not isinstance(rows, list):
        raise SourceGap("FILING_INDEX_NOT_VALIDATED")
    matches = [r for r in rows
               if isinstance(r, dict)
               and f"분기보고서 ({YEAR}.09)" in str(r.get("report_nm", ""))]
    if not matches:
        raise SourceGap("FIRST_REPORT_NOT_IN_INDEX")
    original = [r for r in matches if r.get("rcept_no") == receipt]
    if len(original) != 1 or original[0].get("report_nm", "").strip() != f"분기보고서 ({YEAR}.09)":
        raise SourceGap("FIRST_VERSION_MISMATCH")
    date = original[0]["rcept_dt"]
    later = [r for r in matches if r["rcept_no"] != receipt and r["rcept_dt"] > date]
    if len(later) != len(matches)-1:
        raise SourceGap("AMBIGUOUS_SAME_DAY_OR_EARLIER_VERSION")
    return {
        "original_receipt_date_confirmed_from_official_index": True,
        "same_period_later_version_rows_in_initial_window": len(later),
        "initial_window_fully_paginated": True,
        "index_is_date_precision_not_publication_time": True,
        "full_later_correction_history_not_enumerated": True,
    }


def run(session=None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    report = {
        "purpose": "FIXED_M20_SLOT5_2022_FIRST_DOCUMENT_PROVENANCE",
        "fixed_cohort_slot": SLOT,
        "original_year": YEAR,
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        "credential_present": bool(key),
        "max_official_requests": MAX_CALLS,
        "first_submitted_original_only": True,
        "ordering": "DISABLED",
        **{k: False for k in SAFE_FALSE},
    }
    if not key:
        return report
    if session is None:
        import requests
        session = requests.Session()
    stage = "REGISTRY"
    try:
        registry = _official_get(
            session, "corpCode.xml", {"crtfc_key": key}, zip_response=True)
        company = _registry(registry).get(COHORT[SLOT])
        if company is None:
            raise SourceGap("FIXED_ISSUER_MAPPING_ABSENT")
        stage = "FIRST_FILING_INDEX"
        start, end = _window(YEAR)
        index = _official_get(session, "list.json", {
            "crtfc_key": key, "corp_code": company, "bgn_de": start,
            "end_de": end, "pblntf_ty": "A", "page_count": "100",
        })
        first_receipt = original_first_receipt(index, YEAR)
        revision = _bounded_revision_shape(index, first_receipt)
        stage = "ORIGINAL_DOCUMENT_ZIP"
        source = _fetch_first_document(session, key, first_receipt)
        source_digest = hashlib.sha256(source).hexdigest()
        if source_digest != EXPECTED_ORIGINAL_DOCUMENT_SHA256:
            # Neither an apparently valid ZIP nor a dated receipt can override
            # the bytes previously pinned by a successful official read.
            raise SourceGap("ORIGINAL_DOCUMENT_SHA256_DRIFT")
        parsed = inspect_original_document_layout(source)
        if (not parsed["official_original_document_zip_received"]
                or not parsed["zip_crc_and_bounded_read_completed"]):
            raise SourceGap("ORIGINAL_ARCHIVE_NOT_INTACT")
        report.update(revision)
        report.update({
            "official_initial_2022_document_received": True,
            "document_sha256": source_digest,
            "zip_integrity_confirmed": True,
            "structured_markup_entries": parsed["structured_markup_entries_inspected"],
            "sgml_html_entries": parsed["non_xml_sgml_html_layout_entries"],
            "standardized_financial_xbrl_absent_in_document_probe": (
                parsed["non_xml_sgml_html_layout_entries"] > 0
                and parsed["safely_parsed_strict_xml_count"] == 0
            ),
            "exact_operating_row_table_candidates_not_facts": (
                parsed["tables_with_exact_operating_row"]
            ),
            "2022_q3_window_bound_to_profit_table": (
                parsed["tables_profit_2022_q3_window_in_first_twelve_rows"] > 0
            ),
            "2021_q3_window_bound_to_profit_table": (
                parsed["tables_profit_2021_q3_window_in_first_twelve_rows"] > 0
            ),
            "financial_values_extracted": False,
            "source_status": "FIRST_FILED_2022_DOCUMENT_PROVENANCE_ONLY_NOT_PIT",
        })
        # Even apparent row/window proximity is not a statement-level fact.
        if (parsed["original_q3_cfs_three_month_profit_bound"]
                or parsed["original_document_financial_semantics_validated"]):
            raise SourceGap("UNAUTHORIZED_FINANCIAL_ADMISSION")
    except Exception as exc:
        report["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        report["failure_stage"] = stage
        allowed = {
            "FIXED_ISSUER_MAPPING_ABSENT", "FILING_INDEX_NOT_VALIDATED",
            "FIRST_REPORT_NOT_IN_INDEX", "FIRST_VERSION_MISMATCH",
            "AMBIGUOUS_SAME_DAY_OR_EARLIER_VERSION",
            "ORIGINAL_ARCHIVE_NOT_INTACT", "ORIGINAL_DOCUMENT_SHA256_DRIFT",
            "UNAUTHORIZED_FINANCIAL_ADMISSION",
        }
        reason = str(exc) if type(exc) in (SourceGap, OriginalDocumentGap) else ""
        report["failure_code"] = reason if reason in allowed else "OFFICIAL_SOURCE_OR_LAYOUT_UNVERIFIED"
        report.pop("document_sha256", None)
        report.pop("official_initial_2022_document_received", None)
    return report


if __name__ == "__main__":
    proof = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(proof, sort_keys=True, indent=2), encoding="utf-8")
    print("OPENDART_M20_2022_SOURCE_PROOF=" + json.dumps(proof, sort_keys=True), flush=True)
