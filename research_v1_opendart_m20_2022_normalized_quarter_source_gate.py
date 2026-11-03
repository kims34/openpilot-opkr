"""Probe official 2022 Q3 normalized CFS 3-month schema, CURRENT snapshot only.

The OpenDART fnlttSinglAcntAll.json API is keyed by fiscal year/report/CFS,
NOT an original disclosure vintage or publication instant. Even if a response
uses an original-looking receipt, the endpoint's present-day data must NEVER
be backfilled as original PIT, compared to research returns, or admitted to M20.
All raw amounts, names, receipts, issuer IDs and credentials remain ephemeral.

Official API guide: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
The guide defines thstrm_amount and frmtrm_q_amount as quarterly IS/CIS
standalone 3-month amounts; *_add_amount is cumulative and NOT substitutable.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry, _window
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import original_first_receipt
from research_v1_opendart_m20_2022_correction_source_pair import _source_pair
from research_v1_opendart_m20_2022_later_edition_census import LATER_BEGIN, AS_OF

COHORT_SLOT = 5
YEAR = "2022"
REPORT = "11014"
FS = "CFS"
MAX_REQUESTS = 4
MAX_ROWS = 12000
OUT = Path("research_results/opendart_m20_2022_normalized_quarter/shape.json")
OPERATING_IDS = frozenset({
    "dart_OperatingIncomeLoss",
    "ifrs-full_ProfitLossFromOperatingActivities",
})
OPERATING_LABELS = frozenset({
    "영업이익", "영업이익(손실)", "영업이익(영업손실)", "영업손실",
})
SIGNED_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+)\Z")
RECEIPT = re.compile(r"[0-9]{14}\Z")
SAFETY = {
    "original_2022_filing_standardized_xbrl_verified": False,
    "first_published_2022_q3_cfs_three_month_profit_verified": False,
    "original_2021_q3_cfs_comparative_profit_verified": False,
    "historical_original_vs_amended_cells_reconciled": False,
    "this_endpoint_supports_original_filing_vintage_selection": False,
    "api_financial_cells_original_pit_admitted": False,
    "exact_historical_publication_instant_verified": False,
    "historical_issuer_security_pit_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "raw_api_amounts_receipts_company_names_or_ids_persisted": False,
    "ordering": "DISABLED",
}


class NormalizedQuarterGap(ValueError):
    """Fixed public-safe diagnostics, never provider status message or data."""


def _receipt_classification(receipt: str, original: str, corrected: str) -> str:
    if type(receipt) is not str or not RECEIPT.fullmatch(receipt):
        raise NormalizedQuarterGap("NORMALIZED_RECEIPT_SHAPE_INVALID")
    if receipt == original:
        return "SAME_ID_AS_FIRST_FILING_NOT_VINTAGE_PROOF"
    if receipt == corrected:
        return "SAME_ID_AS_LATER_CORRECTION_NOT_VINTAGE_PROOF"
    return "DIFFERENT_EDITION_NOT_VINTAGE_PROOF"


def inspect_normalized(payload: dict, corp: str, original: str, amended: str) -> dict:
    """Inspect account IDs and numeric *shapes*; never publish numeric values."""
    if type(payload) is not dict:
        raise NormalizedQuarterGap("NORMALIZED_RESPONSE_INVALID")
    status = payload.get("status")
    if status != "000":
        if status in ("013", "014"):
            raise NormalizedQuarterGap("OFFICIAL_2022_NORMALIZED_FINANCIALS_ABSENT")
        raise NormalizedQuarterGap("NORMALIZED_OFFICIAL_STATUS_UNVERIFIED")
    rows = payload.get("list")
    if not isinstance(rows, list) or not 0 < len(rows) <= MAX_ROWS:
        raise NormalizedQuarterGap("NORMALIZED_FINANCIAL_LIST_INVALID")
    cfs_is_rows = 0
    operating_rows = []
    for row in rows:
        if not isinstance(row, dict):
            raise NormalizedQuarterGap("NORMALIZED_FINANCIAL_ROW_INVALID")
        if (row.get("corp_code") != corp or row.get("bsns_year") != YEAR
                or row.get("reprt_code") != REPORT):
            raise NormalizedQuarterGap("NORMALIZED_ROW_ISSUER_PERIOD_MISMATCH")
        if row.get("sj_div") not in ("IS", "CIS"):
            continue
        cfs_is_rows += 1
        if row.get("account_id") in OPERATING_IDS:
            if row.get("account_nm") not in OPERATING_LABELS:
                raise NormalizedQuarterGap("OPERATING_ACCOUNT_LABEL_MISMATCH")
            if row.get("currency") != "KRW":
                raise NormalizedQuarterGap("OPERATING_ACCOUNT_CURRENCY_MISMATCH")
            operating_rows.append(row)
    if len(operating_rows) != 1:
        raise NormalizedQuarterGap("NORMALIZED_OPERATING_ACCOUNT_NOT_UNIQUE")
    op = operating_rows[0]
    current = op.get("thstrm_amount")
    prior = op.get("frmtrm_q_amount")
    if (type(current) is not str or type(prior) is not str
            or len(current) > 32 or len(prior) > 32
            or not SIGNED_NUMBER.fullmatch(current)
            or not SIGNED_NUMBER.fullmatch(prior)):
        raise NormalizedQuarterGap("NORMALIZED_THREE_MONTH_AMOUNT_SHAPE_INVALID")
    receipt_class = _receipt_classification(op.get("rcept_no"), original, amended)
    return {
        "source_status": "CURRENT_API_NORMALIZED_CFS_2022_Q3_AMOUNT_SHAPE_ONLY_NOT_PIT",
        "official_q3_report_code_and_cfs_query_fixed": True,
        "current_api_income_statement_rows_checked": cfs_is_rows,
        "recognized_unique_operating_account_id_count": len(operating_rows),
        "current_api_2022_q3_3month_amount_shape_present": True,
        "current_api_2021_q3_3month_comparative_shape_present": True,
        "current_api_reported_receipt_classification": receipt_class,
        "current_api_reported_receipt_is_first_published_version_verified": False,
        "current_api_has_as_of_original_version_parameter": False,
        "current_api_year_end_cumulative_values_substituted": False,
        "source_only_semantics_not_original_pit": True,
    }


def execute(session, key: str) -> dict:
    registry = _official_get(
        session, "corpCode.xml", {"crtfc_key": key}, zip_response=True
    )
    corp = _registry(registry).get(COHORT[COHORT_SLOT])
    if corp is None:
        raise NormalizedQuarterGap("FIXED_COHORT_REGISTRY_MAPPING_MISSING")
    begin, end = _window(2022)
    first = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": corp, "bgn_de": begin, "end_de": end,
        "pblntf_ty": "A", "last_reprt_at": "N", "page_count": "100",
    })
    first_receipt = original_first_receipt(first, 2022)
    later = _official_get(session, "list.json", {
        "crtfc_key": key, "corp_code": corp,
        "bgn_de": LATER_BEGIN, "end_de": AS_OF,
        "pblntf_ty": "A", "last_reprt_at": "N",
        "page_no": "1", "page_count": "100",
    })
    corrected_receipt = _source_pair(first, later, first_receipt)
    data = _official_get(session, "fnlttSinglAcntAll.json", {
        "crtfc_key": key, "corp_code": corp,
        "bsns_year": YEAR, "reprt_code": REPORT, "fs_div": FS,
    })
    return inspect_normalized(data, corp, first_receipt, corrected_receipt)


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    result = {
        "purpose": "FROZEN_M20_2022_Q3_CURRENT_NORMALIZED_SOURCE_SCHEMA_ONLY",
        "fixed_cohort_slot": COHORT_SLOT,
        "fixed_report_year": YEAR,
        "fixed_report_code": REPORT,
        "fixed_statement": FS,
        "max_official_requests": MAX_REQUESTS,
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
        allowed = {
            "FIXED_COHORT_REGISTRY_MAPPING_MISSING",
            "NORMALIZED_RECEIPT_SHAPE_INVALID",
            "NORMALIZED_RESPONSE_INVALID",
            "OFFICIAL_2022_NORMALIZED_FINANCIALS_ABSENT",
            "NORMALIZED_OFFICIAL_STATUS_UNVERIFIED",
            "NORMALIZED_FINANCIAL_LIST_INVALID",
            "NORMALIZED_FINANCIAL_ROW_INVALID",
            "NORMALIZED_ROW_ISSUER_PERIOD_MISMATCH",
            "OPERATING_ACCOUNT_LABEL_MISMATCH",
            "OPERATING_ACCOUNT_CURRENCY_MISMATCH",
            "NORMALIZED_OPERATING_ACCOUNT_NOT_UNIQUE",
            "NORMALIZED_THREE_MONTH_AMOUNT_SHAPE_INVALID",
        }
        reason = str(exc) if type(exc) is NormalizedQuarterGap else ""
        result["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        result["source_gap_reason"] = reason if reason in allowed else "OFFICIAL_NORMALIZED_SOURCE_UNVERIFIED"
    return result


if __name__ == "__main__":
    report = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("M20_2022_Q3_NORMALIZED_SOURCE_ONLY=" + json.dumps(report, sort_keys=True), flush=True)
