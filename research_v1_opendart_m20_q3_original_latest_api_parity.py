"""M20 Q3 historical-original vs OpenDART latest CFS API 3-month amount parity.

Official guide distinguishes thstrm_amount and frmtrm_q_amount as Q3
three-month values, NOT YTD thstrm_add_amount/frmtrm_add_amount.

Fixed preselected ONE issuer, originals 2024Q3/2025Q3 only. Compare exact
KRW consolidated original Q3 operating-profit amounts to CURRENT API
2025Q3 current quarter & prior-year 3-month columns, solely in memory.
If any difference occurs: report *only booleans*, never a financial amount,
absolute difference, direction, receipt number, original ZIP or auth key.
Parity does NOT admit original filing historical PIT, restatement completeness,
full issuer panel, trading economics or source/performance/live authority.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import (
    _official_get, corp_from_official_zip, STOCK_CODE,
    ACCOUNT_ID, LEGACY_ACCOUNT_ID, OPERATING_LABELS,
    BUSINESS_YEAR, REPORT_CODE,
)
from research_v1_opendart_m20_vintage_pilot import BEGIN, END
from research_v1_opendart_original_xbrl_pilot import (
    _official_xbrl_get, first_q3_original_receipts,
)
from research_v1_opendart_m20_q3_original_numeric_compat import (
    _numeric_pair_atom, check_two_original_q3_numbers, AUTHORITY,
)

SOURCE = "OpenDART_OFFICIAL_FIXED_CFS"
OUTPUT=Path("research_results/opendart_m20_original_q3_api_parity/summary.json")
MONEY=re.compile(r"-?(?:0|[1-9]\d*)(?:,[0-9]{3})*\Z")
RECEIPT=re.compile(r"[0-9]{14}\Z")


class OriginalAPIParityError(ValueError):
    pass


def _money(value):
    """Parse only the source-approved 3-month money format, no output."""
    if type(value) is not str or not MONEY.fullmatch(value.strip()):
        raise OriginalAPIParityError("SOURCE_CFS_QUARTER_AMOUNT_INVALID")
    try:
        val=Decimal(value.strip().replace(",",""))
    except (InvalidOperation,TypeError,ValueError):
        raise OriginalAPIParityError("SOURCE_CFS_QUARTER_AMOUNT_INVALID") from None
    if not val.is_finite():
        raise OriginalAPIParityError("SOURCE_CFS_QUARTER_AMOUNT_INVALID")
    return val


def latest_consolidated_q3_operating_line(payload, *, corp_code, original_receipt) -> tuple:
    if type(payload) is not dict or payload.get("status")!="000":
        raise OriginalAPIParityError("CURRENT_CFS_API_NOT_AVAILABLE")
    rows=payload.get("list")
    if type(rows) is not list:
        raise OriginalAPIParityError("CURRENT_CFS_ACCOUNT_ROWS_ABSENT")
    found=[]
    for row in rows:
        if type(row) is not dict:
            raise OriginalAPIParityError("CURRENT_CFS_ACCOUNT_ROW_INVALID")
        if (row.get("corp_code")!=corp_code or row.get("bsns_year")!=BUSINESS_YEAR
                or row.get("reprt_code")!=REPORT_CODE
                or row.get("sj_div") not in ("IS","CIS")):
            continue
        if row.get("account_id")==LEGACY_ACCOUNT_ID:
            raise OriginalAPIParityError("CURRENT_CFS_LEGACY_CONCEPT_CONFLICT")
        if row.get("account_id")!=ACCOUNT_ID:
            continue
        if (row.get("currency")!="KRW"
                or row.get("account_nm") not in OPERATING_LABELS):
            raise OriginalAPIParityError("CURRENT_CFS_OPERATING_ACCOUNT_SEMANTICS_INVALID")
        receipt=row.get("rcept_no")
        if type(receipt) is not str or not RECEIPT.fullmatch(receipt):
            raise OriginalAPIParityError("CURRENT_CFS_ACCOUNT_RECEIPT_INVALID")
        # Guide: *three-month* fields for quarterly IS/CIS. Do not read the
        # YTD thstrm_add_amount nor frmtrm_add_amount as if standalone Q3.
        found.append((
            _money(row.get("thstrm_amount")),
            _money(row.get("frmtrm_q_amount")),
            receipt==original_receipt,
        ))
    if len(found)!=1:
        raise OriginalAPIParityError("CURRENT_CFS_OPERATING_ACCOUNT_NOT_UNIQUE")
    return found[0]


def check_original_latest_parity(
    *, original24: bytes, original25: bytes, latest_api: dict,
    corp_code: str, first_2025_receipt: str,
) -> dict:
    representation=check_two_original_q3_numbers(
        original24=original24,original25=original25)
    if not representation["minimal_original_pair_representation_consistent"]:
        raise OriginalAPIParityError("ORIGINAL_Q3_PAIR_REPRESENTATION_MISMATCH")
    current,previous,receipt_same=latest_consolidated_q3_operating_line(
        latest_api,corp_code=corp_code,original_receipt=first_2025_receipt)
    atom24=_numeric_pair_atom(original24,2024)
    atom25=_numeric_pair_atom(original25,2025)
    q_current_equal=current==atom25[3]
    q_minus_4_equal=previous==atom24[3]
    return {
        "original_2024_q3_first_filing_available_shape":True,
        "original_2025_q3_first_filing_available_shape":True,
        "latest_api_2025_q3_cfs_line_count":1,
        "latest_api_receipt_is_first_filed_2025_q3":receipt_same,
        "latest_api_2025_three_month_matches_first_filing":q_current_equal,
        "latest_api_2024_comparative_three_month_matches_first_filing":q_minus_4_equal,
        "two_earliest_originals_numeric_representation_consistent":True,
        "original_and_latest_api_three_month_parity_observed":(
            receipt_same and q_current_equal and q_minus_4_equal
        ),
        "historical_restatement_completeness_verified":False,
        "quarter_money_values_delta_or_sign_saved":False,
        **AUTHORITY,
    }


def run(session=None):
    key=os.getenv("OPENDART_API_KEY","").strip()
    out={
        "purpose":"M20_ORIGINAL_2024_2025_CFS_Q3_VS_LATEST_API_3MONTH_PARITY_NOT_PIT",
        "official_source":SOURCE,
        "pilot_stock":STOCK_CODE,
        "source_status":"AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "credential_present":bool(key),
        "original_q3_reports_examined":0,
        "latest_api_consolidated_income_statement_checked":False,
        "original_and_latest_api_three_month_parity_observed":False,
        "amounts_or_identifiers_saved":False,
        **AUTHORITY,
    }
    if not key:
        return out
    if session is None:
        import requests
        session=requests.Session()
    stage="OFFICIAL_CORPORATION_MAPPING"
    try:
        corp=corp_from_official_zip(_official_get(
            session,"corpCode.xml",{"crtfc_key":key},zip_response=True))
        stage="ORIGINAL_RECEIPT_LINEAGE"
        listed=_official_get(session,"list.json",{
            "crtfc_key":key, "corp_code":corp,
            "bgn_de":BEGIN,"end_de":END,"pblntf_ty":"A","page_count":"100",
        })
        receipts=first_q3_original_receipts(listed)
        stage="ORIGINAL_2024_Q3_XBRL"
        raw24=_official_xbrl_get(session,key,receipts["Q_MINUS_4"])
        stage="ORIGINAL_2025_Q3_XBRL"
        raw25=_official_xbrl_get(session,key,receipts["Q_CURRENT"])
        stage="LATEST_CFS_API_THREE_MONTHS"
        latest=_official_get(session,"fnlttSinglAcntAll.json",{
            "crtfc_key":key, "corp_code":corp,
            "bsns_year":BUSINESS_YEAR,"reprt_code":REPORT_CODE,"fs_div":"CFS",
        })
        out.update(check_original_latest_parity(
            original24=raw24,original25=raw25,latest_api=latest,
            corp_code=corp,first_2025_receipt=receipts["Q_CURRENT"],
        ))
        out["original_q3_reports_examined"]=2
        out["latest_api_consolidated_income_statement_checked"]=True
        out["source_status"]="THREE_MONTH_ORIGINAL_VS_LATEST_API_PARITY_DIAGNOSTIC_ONLY"
    except Exception as exc:
        out["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        out["failure_stage"]=stage
        allowed={
            "CURRENT_CFS_API_NOT_AVAILABLE","CURRENT_CFS_ACCOUNT_ROWS_ABSENT",
            "CURRENT_CFS_ACCOUNT_ROW_INVALID","CURRENT_CFS_LEGACY_CONCEPT_CONFLICT",
            "CURRENT_CFS_OPERATING_ACCOUNT_SEMANTICS_INVALID",
            "CURRENT_CFS_ACCOUNT_RECEIPT_INVALID",
            "CURRENT_CFS_QUARTER_AMOUNT_INVALID",
            "CURRENT_CFS_OPERATING_ACCOUNT_NOT_UNIQUE",
            "SOURCE_CFS_QUARTER_AMOUNT_INVALID",
            "ORIGINAL_Q3_PAIR_REPRESENTATION_MISMATCH",
        }
        reason=str(exc) if type(exc) is OriginalAPIParityError else ""
        out["failure_reason_code"]=reason if reason in allowed else "UNCLASSIFIED"
    return out


if __name__=="__main__":
    out=run()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,sort_keys=True,indent=2),encoding="utf-8")
    print("OPENDART_M20_Q3_ORIGINAL_LATEST_PARITY="+json.dumps(out,sort_keys=True),flush=True)
