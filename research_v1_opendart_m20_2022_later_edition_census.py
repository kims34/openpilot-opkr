"""Fixed 2022-Q3 source-only subsequent filing-version census.

Queries the already approved OpenDART corpCode.xml + list.json routes for
the frozen issuer slot 5. Only 2023-03-01 to 2026-10-13 (initial window ended
2023-02-28). This is NOT an amended financial-value reconstruction or PIT
admission. Original prior-window rm=정 hint was independently observed in
official Actions run 38413190868. Never log identities, filing numbers,
timestamps, raw rows, amounts, credentials, or provider exception strings.
"""
from __future__ import annotations

from datetime import date
import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import (
    COHORT, _registry,
)

SLOT = 5
YEAR = 2022
LATER_BEGIN = "20230301"
AS_OF = "20261013"
PAGE_SIZE = 100
MAX_PAGES = 4
MAX_OFFICIAL_REQUESTS = 1 + MAX_PAGES
OUTPUT = Path("research_results/opendart_m20_2022_later_editions/summary.json")
REPORT = f"분기보고서 ({YEAR}.09)"
CATEGORIES = {
    f"[기재정정]{REPORT}": "CORRECTION",
    f"[첨부정정]{REPORT}": "CORRECTION",
    f"[첨부추가]{REPORT}": "ATTACHMENT_ADDITION",
}
RECEIPT = re.compile(r"[0-9]{14}\Z")
YMD = re.compile(r"[0-9]{8}\Z")
SAFETY = {
    "full_correction_lineage_verified": False,
    "original_q3_cfs_three_month_operating_profit_verified": False,
    "original_q3_qminus4_comparability_verified": False,
    "historical_corp_security_mapping_verified": False,
    "historical_publication_instant_pit_verified": False,
    "original_xbrl_2022_source_gap_resolved": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "raw_source_identifiers_dates_or_values_persisted": False,
    "ordering": "DISABLED",
}


class LaterEditionGap(ValueError):
    """Allowlisted fixed diagnostics only."""


def _day(s: str) -> date:
    if not isinstance(s, str) or not YMD.fullmatch(s):
        raise LaterEditionGap("LIST_DATE_FORMAT_INVALID")
    try:
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except ValueError:
        raise LaterEditionGap("LIST_DATE_INVALID") from None


def assess_pages(pages: list[dict]) -> dict:
    """Fail closed on gaps/overlaps/truncation, not on a missing target count."""
    if not isinstance(pages, list) or not 1 <= len(pages) <= MAX_PAGES:
        raise LaterEditionGap("BOUNDED_COMPLETE_PAGES_REQUIRED")
    seen: set[str] = set()
    total = None
    count = 0
    corrections = 0
    attachments = 0
    lower, upper = _day(LATER_BEGIN), _day(AS_OF)
    for pageno, payload in enumerate(pages, 1):
        if not isinstance(payload, dict) or payload.get("status") != "000":
            raise LaterEditionGap("OFFICIAL_INDEX_STATUS_UNVERIFIED")
        meta = []
        for attr in ("total_count", "total_page", "page_no"):
            value = payload.get(attr)
            if type(value) not in (int, str) or not re.fullmatch(r"[0-9]+", str(value)):
                raise LaterEditionGap("OFFICIAL_INDEX_PAGINATION_INVALID")
            meta.append(int(value))
        num_rows, num_pages, actual_page = meta
        if (num_pages < 1 or num_pages > MAX_PAGES or actual_page != pageno
                or num_pages != len(pages) or num_rows < 1
                or num_rows > MAX_PAGES * PAGE_SIZE):
            raise LaterEditionGap("OFFICIAL_INDEX_PAGINATION_INCOMPLETE")
        if total is None:
            total = num_rows
        if total != num_rows:
            raise LaterEditionGap("OFFICIAL_INDEX_PAGINATION_CHANGED")
        rows = payload.get("list")
        expected_rows = min(PAGE_SIZE, num_rows - (pageno-1)*PAGE_SIZE)
        if not isinstance(rows, list) or len(rows) != expected_rows:
            raise LaterEditionGap("OFFICIAL_INDEX_CARDINALITY_INVALID")
        for row in rows:
            if not isinstance(row, dict):
                raise LaterEditionGap("OFFICIAL_INDEX_ROW_INVALID")
            receipt, filing_day, title = (
                row.get("rcept_no"), row.get("rcept_dt"), row.get("report_nm")
            )
            if (not isinstance(receipt, str) or not RECEIPT.fullmatch(receipt)
                    or receipt in seen or not isinstance(title, str)):
                raise LaterEditionGap("OFFICIAL_INDEX_ROW_INVALID")
            seen.add(receipt)
            event_date = _day(filing_day)
            if (receipt[:8] != filing_day or not lower <= event_date <= upper):
                raise LaterEditionGap("OFFICIAL_INDEX_CHRONOLOGY_INVALID")
            count += 1
            if REPORT not in title:
                continue
            subtype = CATEGORIES.get(title.strip())
            if subtype is None:
                raise LaterEditionGap("UNKNOWN_2022_Q3_EDITION_NAME")
            if subtype == "CORRECTION":
                corrections += 1
            else:
                attachments += 1
    if count != total:
        raise LaterEditionGap("OFFICIAL_INDEX_TOTAL_INCONSISTENT")
    return {
        "source_status": "POST_WINDOW_SOURCE_EDITION_COUNTS_ONLY_NOT_PIT",
        "late_index_complete_for_fixed_bounded_window": True,
        "late_index_pages_checked": len(pages),
        "late_index_all_periodic_rows_validated": count,
        "2022_q3_late_confirmed_corrections": corrections,
        "2022_q3_late_attachment_additions": attachments,
        # A known earlier original rm=정 flag and zero matching followups
        # would indicate a provenance disconnect, never infer no corrections.
        "initial_original_rm_correction_hint_from_prior_official_evidence": True,
        "initial_and_later_edition_lineage_semantically_linked": False,
        "2022_q3_correction_flag_reconciled_to_late_index": corrections > 0,
        "all_revisions_ever_identified": False,
    }


def execute(session, key: str) -> dict:
    registry = _official_get(
        session, "corpCode.xml", {"crtfc_key": key}, zip_response=True
    )
    company = _registry(registry).get(COHORT[SLOT])
    if company is None:
        raise LaterEditionGap("FIXED_ISSUER_REGISTRY_MISSING")
    pages: list[dict] = []
    # Only run multiple pages if the first actual verified response requires it.
    for page in range(1, MAX_PAGES+1):
        payload = _official_get(session, "list.json", {
            "crtfc_key": key, "corp_code": company,
            "bgn_de": LATER_BEGIN, "end_de": AS_OF,
            "pblntf_ty": "A", "last_reprt_at": "N",
            "page_no": str(page), "page_count": str(PAGE_SIZE),
        })
        if not isinstance(payload, dict):
            raise LaterEditionGap("OFFICIAL_INDEX_STATUS_UNVERIFIED")
        if payload.get("status") != "000":
            raise LaterEditionGap("OFFICIAL_INDEX_STATUS_UNVERIFIED")
        try:
            n = int(payload["total_page"])
        except (KeyError, ValueError, TypeError):
            raise LaterEditionGap("OFFICIAL_INDEX_PAGINATION_INVALID") from None
        if n < 1 or n > MAX_PAGES:
            raise LaterEditionGap("OFFICIAL_INDEX_EXCEEDS_APPROVED_BUDGET")
        pages.append(payload)
        if page == n:
            break
    return assess_pages(pages)


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    outcome = {
        "purpose": "FROZEN_M20_SLOT5_2022_Q3_POST_INITIAL_AMENDMENT_CENSUS",
        "fixed_cohort_slot": SLOT,
        "initial_index_ends": "20230228",
        "late_index_begin": LATER_BEGIN,
        "source_as_of": AS_OF,
        "max_official_requests": MAX_OFFICIAL_REQUESTS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFETY,
    }
    if not key:
        return outcome
    if session is None:
        import requests
        session = requests.Session()
    try:
        outcome.update(execute(session, key))
    except Exception as exc:
        whitelist = {
            "BOUNDED_COMPLETE_PAGES_REQUIRED", "LIST_DATE_FORMAT_INVALID",
            "LIST_DATE_INVALID", "OFFICIAL_INDEX_STATUS_UNVERIFIED",
            "OFFICIAL_INDEX_PAGINATION_INVALID",
            "OFFICIAL_INDEX_PAGINATION_INCOMPLETE",
            "OFFICIAL_INDEX_PAGINATION_CHANGED",
            "OFFICIAL_INDEX_CARDINALITY_INVALID",
            "OFFICIAL_INDEX_ROW_INVALID",
            "OFFICIAL_INDEX_CHRONOLOGY_INVALID",
            "OFFICIAL_INDEX_TOTAL_INCONSISTENT",
            "UNKNOWN_2022_Q3_EDITION_NAME",
            "FIXED_ISSUER_REGISTRY_MISSING",
            "OFFICIAL_INDEX_EXCEEDS_APPROVED_BUDGET",
        }
        reason = str(exc) if type(exc) is LaterEditionGap else ""
        outcome["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        outcome["failure_code"] = reason if reason in whitelist else "OFFICIAL_PROVIDER_OR_REGISTRY_UNVERIFIED"
    return outcome


if __name__ == "__main__":
    result = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_2022_Q3_LATER_CENSUS=" + json.dumps(result, sort_keys=True), flush=True)
