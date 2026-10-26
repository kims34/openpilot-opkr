"""One-day fixed 2022-Q3 OpenDART correction-index extension: 2026-10-22.

Two authenticated READ-ONLY official OpenDART requests maximum: frozen issuer
corpCode.xml and one complete list.json page for the last fully completed KST
date, 2026-10-22. Strictly contiguous after independently verified Oct21.
This is an OBSERVED CURRENT LIST INDEX census, not a historical immutable
snapshot, original 2022 CFS financial cell, PIT or performance permission.
No actual company, source filing ID, dates from returned rows, raw response,
amounts or credentials are ever persisted in CI output.
"""
from __future__ import annotations

from datetime import datetime, date, timedelta, timezone
import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry
from research_v1_opendart_m20_2022_later_edition_census import REPORT, CATEGORIES
from research_v1_m20_2022_q3_incremental_correction_census import END as VERIFIED_PRIOR_END

START = "20261022"
END = "20261022"
MAX_GETS = 2
MAX_ROWS = 100
SLOT = 5
OUT = Path("research_results/m20_2022_q3_oct22_amendment_index/counts.json")
YMD = re.compile(r"[0-9]{8}\Z")
CORP = re.compile(r"[0-9]{8}\Z")
RECEIPT = re.compile(r"[0-9]{14}\Z")
GUARDS = {
    "first_2022_cfs_three_month_operating_profit_verified": False,
    "original_2021_q3_cfs_comparator_verified": False,
    "original_vs_corrected_financial_cell_lineage_verified": False,
    "original_first_publication_instant_verified": False,
    "historical_issuer_security_pit_verified": False,
    "historical_market_trading_days_verified": False,
    "immutable_historical_edition_inventory_verified": False,
    "entire_later_edition_history_independently_complete": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "provider_company_ids_receipts_days_titles_content_or_key_saved": False,
    "ordering": "DISABLED",
}

class Oct22SourceGap(ValueError):
    """Every surfaced failure is a fixed identifier, never a provider string."""


def _day(value: str) -> date:
    if type(value) is not str or not YMD.fullmatch(value):
        raise Oct22SourceGap("INDEX_DAY_SHAPE_INVALID")
    try:
        return date(int(value[:4]), int(value[4:6]), int(value[6:]))
    except ValueError:
        raise Oct22SourceGap("INDEX_DAY_INVALID") from None


def scope() -> None:
    if (_day(VERIFIED_PRIOR_END) + timedelta(days=1) != _day(START)
            or _day(START) != _day(END)):
        raise Oct22SourceGap("PREVIOUS_CENSUS_WINDOW_NOT_ADJACENT")
    today = datetime.now(timezone(timedelta(hours=9))).date()
    if today <= _day(END):
        raise Oct22SourceGap("CENSUS_KOREA_LOCAL_DAY_NOT_COMPLETE")


def inspect(payload: dict, *, expected_company: str) -> dict:
    if type(expected_company) is not str or not CORP.fullmatch(expected_company):
        raise Oct22SourceGap("CURRENT_ISSUER_LOOKUP_INVALID")
    if type(payload) is not dict:
        raise Oct22SourceGap("OFFICIAL_RESPONSE_NOT_OBJECT")
    if payload.get("status") == "013":
        if (payload.get("list") not in (None, [])
                or any(payload.get(k) not in (None, 0, "0")
                       for k in ("total_count", "total_page", "page_no"))):
            raise Oct22SourceGap("NO_RESULTS_STATUS_CONTAINS_ROWS")
        return {
            "source_status": "OFFICIAL_INDEX_013_NO_PERIODIC_ROWS_OCT22",
            "official_day_index_observed": True,
            "query_status_013_no_periodic_filings": True,
            "scoped_periodic_rows_checked": 0,
            "new_q3_2022_correction_rows": 0,
            "new_q3_2022_attachment_rows": 0,
            "target_report_new_vintage_found_quarantine": False,
            "verified_window_start": START,
            "verified_window_end": END,
        }
    if payload.get("status") != "000":
        raise Oct22SourceGap("OFFICIAL_INDEX_PROVIDER_STATUS_NOT_APPROVED")

    def natural(k: str) -> int:
        value = payload.get(k)
        if type(value) is int and 0 <= value <= MAX_ROWS:
            return value
        if type(value) is str and re.fullmatch(r"0|[1-9][0-9]*", value):
            parsed = int(value)
            if parsed <= MAX_ROWS:
                return parsed
        raise Oct22SourceGap("OFFICIAL_PAGINATION_INVALID")
    total = natural("total_count")
    pages = natural("total_page")
    number = natural("page_no")
    rows = payload.get("list")
    if (not 1 <= total <= MAX_ROWS or pages != 1 or number != 1
            or type(rows) is not list or len(rows) != total):
        raise Oct22SourceGap("OFFICIAL_PAGE_NOT_EXHAUSTIVE")
    seen = set()
    corrections = attachments = 0
    for row in rows:
        if type(row) is not dict:
            raise Oct22SourceGap("OFFICIAL_ROW_SCHEMA_INVALID")
        receipt = row.get("rcept_no")
        when = row.get("rcept_dt")
        issuer = row.get("corp_code")
        title = row.get("report_nm")
        if (type(receipt) is not str or not RECEIPT.fullmatch(receipt)
                or receipt in seen or issuer != expected_company
                or type(title) is not str or type(when) is not str
                or not YMD.fullmatch(when)):
            raise Oct22SourceGap("OFFICIAL_ROW_ISSUER_OR_RECEIPT_INVALID")
        seen.add(receipt)
        if receipt[:8] != when or _day(when) != _day(START):
            raise Oct22SourceGap("OFFICIAL_ROW_OUTSIDE_OCT22_WINDOW")
        if REPORT not in title:
            continue
        kind = CATEGORIES.get(title.strip())
        if kind == "CORRECTION":
            corrections += 1
        elif kind == "ATTACHMENT_ADDITION":
            attachments += 1
        else:
            raise Oct22SourceGap("NEW_TARGET_REPORT_EDITION_UNCLASSIFIED")
    detected = corrections + attachments > 0
    return {
        "source_status": (
            "NEW_FIRST_SOURCE_VINTAGE_QUARANTINED"
            if detected else "OFFICIAL_INDEX_000_NO_TARGET_Q3_EDITION_OCT22"
        ),
        "official_day_index_observed": True,
        "query_status_013_no_periodic_filings": False,
        "scoped_periodic_rows_checked": total,
        "new_q3_2022_correction_rows": corrections,
        "new_q3_2022_attachment_rows": attachments,
        "target_report_new_vintage_found_quarantine": detected,
        "verified_window_start": START,
        "verified_window_end": END,
    }


def execute(session, api_key: str) -> dict:
    scope()
    zipped = _official_get(session, "corpCode.xml",
                           {"crtfc_key": api_key}, zip_response=True)
    issuer = _registry(zipped).get(COHORT[SLOT])
    if issuer is None:
        raise Oct22SourceGap("FROZEN_ISSUER_CURRENT_MAPPING_MISSING")
    payload = _official_get(session, "list.json", {
        "crtfc_key": api_key, "corp_code": issuer, "bgn_de": START,
        "end_de": END, "pblntf_ty": "A", "last_reprt_at": "N",
        "page_no": "1", "page_count": str(MAX_ROWS),
    })
    return inspect(payload, expected_company=issuer)


def run(session=None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    answer = {
        "purpose": "FROZEN_SLOT5_2022_Q3_SINGLE_ELAPSED_20261022_OFFICIAL_CENSUS",
        "fixed_cohort_slot": SLOT,
        "max_authenticated_official_requests": MAX_GETS,
        "credential_present": bool(key),
        "source_status": "PENDING" if key else "AUTH_NOT_CONFIGURED",
        **GUARDS,
    }
    if not key:
        return answer
    if session is None:
        import requests
        session = requests.Session()
    try:
        answer.update(execute(session, key))
    except Exception as error:
        allow = {
            "INDEX_DAY_SHAPE_INVALID", "INDEX_DAY_INVALID",
            "PREVIOUS_CENSUS_WINDOW_NOT_ADJACENT",
            "CENSUS_KOREA_LOCAL_DAY_NOT_COMPLETE",
            "CURRENT_ISSUER_LOOKUP_INVALID", "OFFICIAL_RESPONSE_NOT_OBJECT",
            "NO_RESULTS_STATUS_CONTAINS_ROWS",
            "OFFICIAL_INDEX_PROVIDER_STATUS_NOT_APPROVED",
            "OFFICIAL_PAGINATION_INVALID", "OFFICIAL_PAGE_NOT_EXHAUSTIVE",
            "OFFICIAL_ROW_SCHEMA_INVALID",
            "OFFICIAL_ROW_ISSUER_OR_RECEIPT_INVALID",
            "OFFICIAL_ROW_OUTSIDE_OCT22_WINDOW",
            "NEW_TARGET_REPORT_EDITION_UNCLASSIFIED",
            "FROZEN_ISSUER_CURRENT_MAPPING_MISSING",
        }
        reason = str(error) if type(error) is Oct22SourceGap else ""
        answer["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        answer["source_gap_reason"] = reason if reason in allow else "OFFICIAL_SOURCE_UNVERIFIED"
    return answer


if __name__ == "__main__":
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_2022_Q3_OCT22_INCREMENTAL_CENSUS=" +
          json.dumps(result, sort_keys=True), flush=True)
