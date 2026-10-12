"""Offline bounded OpenDART financial-line shape diagnostics.

No raw rows, values, account names, company IDs, filing IDs or secrets are
returned. Counts alone never admit PIT evidence or justify account fallbacks.
"""
from __future__ import annotations

import re


def line_shape_counts(
    payload: dict, corp_code: str, receipts: set[str],
    *, year: str, report_code: str, exact_account_id: str,
) -> dict[str, int]:
    if not isinstance(payload, dict) or payload.get("status") != "000":
        raise ValueError("invalid official financial payload")
    rows = payload.get("list")
    if not isinstance(rows, list) or len(rows) > 10000:
        raise ValueError("invalid official financial rows")
    result = {
        "total_financial_rows": len(rows),
        "matching_corp_year_report_rows": 0,
        "matching_is_cis_rows": 0,
        "matching_exact_account_id_rows": 0,
        "matching_exact_account_id_is_rows": 0,
        "matching_exact_account_id_cis_rows": 0,
        "matching_dart_operating_income_id_rows": 0,
        "matching_ifrs_legacy_operating_profit_id_rows": 0,
        "exact_account_valid_receipt_rows": 0,
        "exact_account_filing_linked_rows": 0,
        "exact_account_quarter_amount_shape_rows": 0,
        "exact_account_dash_detail_rows": 0,
    }
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid financial row")
        if not (row.get("corp_code") == corp_code
                and row.get("bsns_year") == year
                and row.get("reprt_code") == report_code):
            continue
        result["matching_corp_year_report_rows"] += 1
        sj_div = row.get("sj_div")
        if sj_div not in ("IS", "CIS"):
            continue
        result["matching_is_cis_rows"] += 1
        account = row.get("account_id")
        if account == "dart_OperatingIncomeLoss":
            result["matching_dart_operating_income_id_rows"] += 1
        if account == "ifrs_ProfitLossFromOperatingActivities":
            result["matching_ifrs_legacy_operating_profit_id_rows"] += 1
        if account != exact_account_id:
            continue
        result["matching_exact_account_id_rows"] += 1
        result["matching_exact_account_id_" + sj_div.lower() + "_rows"] += 1
        if row.get("account_detail") == "-":
            result["exact_account_dash_detail_rows"] += 1
        receipt = row.get("rcept_no")
        if not isinstance(receipt, str) or not re.fullmatch(r"[0-9]{14}", receipt):
            continue
        result["exact_account_valid_receipt_rows"] += 1
        if receipt not in receipts:
            continue
        result["exact_account_filing_linked_rows"] += 1
        if all(isinstance(v, str) and re.fullmatch(r"-?[0-9][0-9,]*", v)
               for v in (row.get("thstrm_amount"), row.get("frmtrm_q_amount"))):
            result["exact_account_quarter_amount_shape_rows"] += 1
    return result
