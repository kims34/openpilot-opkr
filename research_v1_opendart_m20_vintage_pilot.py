"""M20 pre-registered Q3 filing *date-level* vintage probe (read-only).

Only official authenticated OpenDART corpCode.xml and list.json are queried,
for one FIXED issuer and filing types, under the already configured Actions
secret. Raw documents, receipts, issuer IDs and secrets are never logged or
saved. Verified metadata DOES NOT prove exact publication time, historically
observed source revisions, q-4 economic comparability or strategy PIT admission.

Never reuses modern revised values as if they were historically available.
Existing Frozen, independent holdout, costs, Net EV and order gates untouched.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping

import requests

from research_v1_opendart_lineage_pilot import (
    _official_get, corp_from_official_zip, STOCK_CODE
)

BEGIN = "20241001"
END = "20261012"
TARGETS = {"Q_MINUS_4": ("2024.09", date(2024, 9, 30)),
           "Q_CURRENT": ("2025.09", date(2025, 9, 30))}
OUTPUT = Path("research_results/opendart_m20_vintage/summary.json")
RECEIPT = re.compile(r"[0-9]{14}\Z")
DAY = re.compile(r"[0-9]{8}\Z")


class VintageEvidenceError(ValueError):
    pass


def _day(value: object) -> date:
    if type(value) is not str or not DAY.fullmatch(value):
        raise VintageEvidenceError("FILING_DAY_INVALID")
    try:
        d = datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        raise VintageEvidenceError("FILING_DAY_INVALID") from None
    if d.strftime("%Y%m%d") != value:
        raise VintageEvidenceError("FILING_DAY_INVALID")
    return d


def _integer(value: object) -> int:
    if type(value) is int:
        result = value
    elif type(value) is str and re.fullmatch(r"(0|[1-9][0-9]*)", value):
        result = int(value)
    else:
        raise VintageEvidenceError("FILING_PAGINATION_INVALID")
    if result < 0 or result > 100000:
        raise VintageEvidenceError("FILING_PAGINATION_INVALID")
    return result


def validate_complete_q3_filing_index(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Date-level evidence only; never returns the original receipt identifiers."""
    if not isinstance(payload, Mapping) or payload.get("status") != "000":
        raise VintageEvidenceError("OFFICIAL_FILING_INDEX_NOT_ADMITTED")
    page_count = _integer(payload.get("total_page"))
    row_count = _integer(payload.get("total_count"))
    page_no = _integer(payload.get("page_no", 1))
    rows = payload.get("list")
    if (page_count != 1 or page_no != 1 or row_count > 100
            or type(rows) is not list or len(rows) != row_count):
        raise VintageEvidenceError("FILING_HISTORY_NOT_COMPLETE")
    all_receipts: set[str] = set()
    identified: dict[str, list[tuple[date, str]]] = defaultdict(list)
    for row in rows:
        if not isinstance(row, Mapping):
            raise VintageEvidenceError("FILING_ROW_INVALID")
        receipt, name = row.get("rcept_no"), row.get("report_nm")
        day_str = row.get("rcept_dt")
        if type(receipt) is not str or not RECEIPT.fullmatch(receipt):
            raise VintageEvidenceError("FILING_RECEIPT_INVALID")
        if receipt in all_receipts:
            raise VintageEvidenceError("FILING_RECEIPT_DUPLICATED")
        all_receipts.add(receipt)
        day = _day(day_str)
        if receipt[:8] != day_str or not (_day(BEGIN) <= day <= _day(END)):
            raise VintageEvidenceError("FILING_INDEX_CHRONOLOGY_INVALID")
        if type(name) is not str:
            raise VintageEvidenceError("FILING_ROW_INVALID")
        for key, (period, cutoff) in TARGETS.items():
            if f"분기보고서 ({period})" in name:
                if day <= cutoff:
                    raise VintageEvidenceError("REPORT_BEFORE_QUARTER_END")
                identified[key].append((day, receipt))
    if not all(identified[key] for key in TARGETS):
        raise VintageEvidenceError("REQUIRED_Q3_REPORT_NOT_FOUND")
    earliest = {key: min(identified[key])[0] for key in TARGETS}
    if earliest["Q_MINUS_4"] >= earliest["Q_CURRENT"]:
        raise VintageEvidenceError("VINTAGE_SEQUENCE_INVALID")
    # The endpoints expose only submission dates. Multiple same-day
    # corrections are not ordered by a trustworthy publication clock.
    same_day_any = any(
        len([1 for when, _receipt in identified[k] if when == earliest[k]]) > 1
        for k in TARGETS
    )
    return {
        "official_list_index_complete_for_fixed_window": True,
        "q_minus_4_initial_filing_date": earliest["Q_MINUS_4"].isoformat(),
        "q_current_initial_filing_date": earliest["Q_CURRENT"].isoformat(),
        "q_minus_4_filing_versions_observed": len(identified["Q_MINUS_4"]),
        "q_current_filing_versions_observed": len(identified["Q_CURRENT"]),
        "multiple_versions_on_initial_filing_date": same_day_any,
        "q4_before_current_filing_date": True,
        "receipt_date_only_no_intraday_publication_clock": True,
        "original_document_vintage_authenticated": False,
        "historical_revision_lineage_independently_verified": False,
        "historical_publication_time_verified": False,
        "quarter_and_prior_year_amounts_comparable_verified": False,
    }


def conservative_earliest_date_allowed(
    *, filing_date: str, decision_date: str, historical_available_at_verified: bool
) -> bool:
    """No same-day decision; even a next-day date needs separate PIT admission."""
    try:
        filed = date.fromisoformat(filing_date)
        decision = date.fromisoformat(decision_date)
    except (ValueError, TypeError):
        raise VintageEvidenceError("DECISION_DAY_INVALID") from None
    if filed.isoformat() != filing_date or decision.isoformat() != decision_date:
        raise VintageEvidenceError("DECISION_DAY_INVALID")
    if type(historical_available_at_verified) is not bool:
        raise VintageEvidenceError("PIT_AUTHORITY_INVALID")
    return bool(decision > filed and historical_available_at_verified)


def run(session: requests.Session | None = None) -> dict[str, Any]:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    report: dict[str, Any] = {
        "purpose": "FIXED_ISSUER_Q3_FILING_VINTAGE_DATE_ONLY",
        "pilot_stock": STOCK_CODE,
        "official_source": "OpenDART",
        "query_start": BEGIN,
        "query_end": END,
        "source_status": "AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "credential_configured": bool(key),
        "current_corporation_mapping_not_historical": True,
        "original_document_vintage_authenticated": False,
        "historical_revision_lineage_independently_verified": False,
        "historical_publication_time_verified": False,
        "quarter_and_prior_year_amounts_comparable_verified": False,
        "pit_source_admitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "champion_change_authorized": False,
        "live_order_authorized": False,
        "ordering": "DISABLED",
        "raw_provider_data_saved": False,
    }
    if not key:
        return report
    if session is None:
        session = requests.Session()
    stage = "FIXED_ISSUER_MAPPING"
    try:
        corp_code = corp_from_official_zip(_official_get(
            session, "corpCode.xml", {"crtfc_key": key}, zip_response=True))
        stage = "HISTORICAL_FILING_INDEX"
        original = _official_get(
            session, "list.json", {
                "crtfc_key": key, "corp_code": corp_code,
                "bgn_de": BEGIN, "end_de": END,
                "pblntf_ty": "A", "page_count": "100",
            })
        report.update(validate_complete_q3_filing_index(original))
        report["source_status"] = "DATE_LEVEL_REPORT_VINTAGE_PILOT_ONLY"
    except Exception as exc:
        report["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        report["failure_stage"] = stage
        allowlisted = {
            "FILING_DAY_INVALID", "FILING_PAGINATION_INVALID",
            "OFFICIAL_FILING_INDEX_NOT_ADMITTED", "FILING_HISTORY_NOT_COMPLETE",
            "FILING_ROW_INVALID", "FILING_RECEIPT_INVALID", "FILING_RECEIPT_DUPLICATED",
            "FILING_INDEX_CHRONOLOGY_INVALID", "REPORT_BEFORE_QUARTER_END",
            "REQUIRED_Q3_REPORT_NOT_FOUND", "VINTAGE_SEQUENCE_INVALID",
        }
        # Never propagate vendor messages, URLs or tokens in public logs.
        error = str(exc) if type(exc) is VintageEvidenceError else ""
        report["failure_reason"] = error if error in allowlisted else "UNCLASSIFIED"
    return report


if __name__ == "__main__":
    result = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OPENDART_M20_VINTAGE=" + json.dumps(result, ensure_ascii=False))
