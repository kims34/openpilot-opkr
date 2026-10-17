"""Source-only OpenDART original-vs-corrected 2022 Q3 document lineage.

Frozen source sample slot 5, period 2022.09. Exactly five read-only official
requests in the successful path: registry, two bounded filing indexes,
original document ZIP and uniquely identified 2023-2026 correction ZIP.
Never store/log receipt IDs, corp IDs, precise filing dates, source ZIP,
financial amounts, or credentials. Archive hashes and shape-only flags do NOT
prove a changed financial fact, intraday PIT, or admissible M20 history.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_source_proof import (
    _bounded_revision_shape, EXPECTED_ORIGINAL_DOCUMENT_SHA256,
)
from research_v1_opendart_m20_2022_later_edition_census import (
    LATER_BEGIN, AS_OF, REPORT, RECEIPT, CATEGORIES, assess_pages,
)
from research_v1_opendart_m20_2022_first_document_pilot import (
    _fetch_first_document, inspect_official_original_document,
    inspect_original_document_layout,
)

MAX_OFFICIAL_REQUESTS = 5

# Counts from strict existing source-only diagnostics; never financial facts.
# These guards locate WHY exact Q3 CFS 3-month values remain unbound.
STATEMENT_LAYOUT_SHAPES = {
    "candidate_three_month_header": "tables_with_operating_row_and_three_month_header",
    "candidate_nearby_exact_cfs_title": "tables_profit_with_nearby_exact_consolidated_income_heading",
    "candidate_last_title_exact_cfs": "tables_with_operating_row_and_last_title_consolidated_income_context",
    "candidate_both_q3_period_windows": "tables_profit_both_q3_windows_in_first_twelve_rows",
    "candidate_quarter_and_cfs_context": "tables_profit_with_quarter_and_nearby_consolidated_heading",
}

OUTPUT = Path("research_results/opendart_m20_2022_correction_document/source_pair.json")
SAFETY = {
    "original_standardized_xbrl_verified": False,
    "original_cfs_q3_2022_2021_three_month_profit_verified": False,
    "correction_changed_cfs_operating_profit_verified": False,
    "initial_and_later_edition_financial_cells_bound": False,
    "full_correction_lineage_verified": False,
    "historical_publication_instant_pit_verified": False,
    "historical_corp_security_mapping_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "raw_source_ids_dates_financial_values_persisted": False,
    "ordering": "DISABLED",
}


class CorrectionPairGap(ValueError):
    """Never forward untrusted provider message text."""


def _source_pair(original_index: dict, later_index: dict, original_receipt: str) -> str:
    """Return one internal-only corrected receipt, after validating both indexes."""
    initial = _bounded_revision_shape(original_index, original_receipt)
    if not initial["original_index_indicates_possible_later_correction"]:
        raise CorrectionPairGap("ORIGINAL_CORRECTION_MARKER_ABSENT")
    if initial["same_period_confirmed_corrections_in_initial_window"] != 0:
        raise CorrectionPairGap("INITIAL_EDITION_CORRECTION_COUNT_CHANGED")
    census = assess_pages([later_index])
    if (census["2022_q3_late_confirmed_corrections"] != 1
            or census["2022_q3_late_attachment_additions"] != 0):
        raise CorrectionPairGap("LATER_CORRECTION_CARDINALITY_CHANGED")
    rows = later_index["list"]
    matches = [r for r in rows if r["report_nm"].strip() in (
        f"[기재정정]{REPORT}", f"[첨부정정]{REPORT}"
    )]
    if len(matches) != 1:
        raise CorrectionPairGap("LATER_CORRECTION_NOT_UNIQUE")
    receipt = matches[0]["rcept_no"]
    if not RECEIPT.fullmatch(receipt):
        raise CorrectionPairGap("LATER_CORRECTION_RECEIPT_INVALID")
    return receipt


def _archive_fingerprint(session, key: str, receipt: str, *, original: bool) -> dict:
    source = _fetch_first_document(session, key, receipt)
    digest = hashlib.sha256(source).hexdigest()
    if original and digest != EXPECTED_ORIGINAL_DOCUMENT_SHA256:
        raise CorrectionPairGap("ORIGINAL_ARCHIVE_SHA_DRIFT")
    checked = inspect_official_original_document(source)
    if checked.get("official_original_document_zip_received") is not True:
        raise CorrectionPairGap("OFFICIAL_ARCHIVE_NOT_VERIFIED")
    layout = inspect_original_document_layout(source)
    if layout.get("zip_crc_and_bounded_read_completed") is not True:
        raise CorrectionPairGap("OFFICIAL_ARCHIVE_NOT_VERIFIED")
    return {
        "digest": digest,
        "sgml_html_entries": layout["non_xml_sgml_html_layout_entries"],
        "strict_xml_entries": layout["safely_parsed_strict_xml_count"],
        "profit_row_candidate_tables_not_facts": layout["tables_with_exact_operating_row"],
        "q3_2022_profit_table_period_hint_not_fact": (
            layout["tables_profit_2022_q3_window_in_first_twelve_rows"] > 0
        ),
        "q3_2021_profit_table_period_hint_not_fact": (
            layout["tables_profit_2021_q3_window_in_first_twelve_rows"] > 0
        ),
        **{k: layout[v] for k, v in STATEMENT_LAYOUT_SHAPES.items()},
        "cfs_three_month_financial_semantics_verified": False,
    }


def execute(session, key: str) -> dict:
    registry = _official_get(
        session, "corpCode.xml", {"crtfc_key": key}, zip_response=True
    )
    company = _registry(registry).get(COHORT[5])
    if company is None:
        raise CorrectionPairGap("FIXED_ISSUER_REGISTRY_MISSING")

    begin, end = _window(2022)
    first = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": company,
        "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N",
        "page_count": "100",
    })
    first_receipt = original_first_receipt(first, 2022)
    later = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": company,
        "bgn_de": LATER_BEGIN, "end_de": AS_OF,
        "pblntf_ty": "A", "last_reprt_at": "N",
        "page_no": "1", "page_count": "100",
    })
    amended_receipt = _source_pair(first, later, first_receipt)
    earliest = _archive_fingerprint(session, key, first_receipt, original=True)
    amended = _archive_fingerprint(session, key, amended_receipt, original=False)
    return {
        "source_status": "OFFICIAL_ORIGINAL_AND_CORRECTION_DOCUMENTS_VALIDATED_SHAPE_ONLY",
        "verified_original_and_corrected_archives_count": 2,
        "original_document_sha256": earliest["digest"],
        "corrected_document_sha256": amended["digest"],
        "original_and_corrected_zip_bytes_differ": earliest["digest"] != amended["digest"],
        "original_sgml_html_entries": earliest["sgml_html_entries"],
        "corrected_sgml_html_entries": amended["sgml_html_entries"],
        "original_strict_xml_entries": earliest["strict_xml_entries"],
        "corrected_strict_xml_entries": amended["strict_xml_entries"],
        "original_profit_row_candidate_tables_not_facts": earliest["profit_row_candidate_tables_not_facts"],
        "corrected_profit_row_candidate_tables_not_facts": amended["profit_row_candidate_tables_not_facts"],
        "original_2022_period_table_hint_not_fact": earliest["q3_2022_profit_table_period_hint_not_fact"],
        "corrected_2022_period_table_hint_not_fact": amended["q3_2022_profit_table_period_hint_not_fact"],
        "original_2021_period_table_hint_not_fact": earliest["q3_2021_profit_table_period_hint_not_fact"],
        "corrected_2021_period_table_hint_not_fact": amended["q3_2021_profit_table_period_hint_not_fact"],
        **{f"original_{name}": earliest[name] for name in STATEMENT_LAYOUT_SHAPES},
        **{f"corrected_{name}": amended[name] for name in STATEMENT_LAYOUT_SHAPES},
        # Even multiple nearby labels are not sufficient as the authoritative
        # 2022/2021 consolidated July–September statement/cell binding.
        "strict_source_financial_semantics_still_unverified": True,
        "source_pair_index_period_links_validated": True,
        "source_pair_actual_financial_changes_unverified": True,
        "source_pair_publication_instants_unverified": True,
    }


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    result = {
        "purpose": "FROZEN_M20_SLOT5_ORIGINAL_CORRECTED_2022_Q3_SOURCE_PAIR",
        "fixed_cohort_slot": 5,
        "max_official_requests": MAX_OFFICIAL_REQUESTS,
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
        reason = str(exc) if type(exc) is CorrectionPairGap else ""
        allowed = {
            "ORIGINAL_CORRECTION_MARKER_ABSENT",
            "INITIAL_EDITION_CORRECTION_COUNT_CHANGED",
            "LATER_CORRECTION_CARDINALITY_CHANGED",
            "LATER_CORRECTION_NOT_UNIQUE",
            "LATER_CORRECTION_RECEIPT_INVALID",
            "ORIGINAL_ARCHIVE_SHA_DRIFT",
            "OFFICIAL_ARCHIVE_NOT_VERIFIED",
            "FIXED_ISSUER_REGISTRY_MISSING",
        }
        result["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        result["failure_code"] = reason if reason in allowed else "OFFICIAL_PAIR_SOURCE_OR_LAYOUT_UNVERIFIED"
    return result


if __name__ == "__main__":
    result = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_2022_CORRECTED_SOURCE_PAIR=" + json.dumps(result, sort_keys=True), flush=True)
