"""Compare 2022/2023 first-filed Q3 operating profit with official 2023 CFS.

One predeclared fixed six-issuer source-feasibility cohort (per-slot jobs).
Per issuer: 1 current DART registry, 2 bounded original Q3 list.json
indexes, 2 original source XBRL ZIP downloads and one 2023Q3
fnlttSinglAcntAll.json CFS API request. At most SIX existing approved
official OpenDART requests; no KRX, no broker or trading endpoints.

Quarterly 2023 current thstrm_amount and prior-year frmtrm_q_amount are
3-month income-statement fields (NOT cumulative *_add_amount), per
OpenDART official documentation. Amounts are compared in memory to
strict unique historical first-submitted CFS/KRW original XBRL facts.

The official current API may reflect corrections/revisions as of 2026.
Matching amounts are NOT proof that different historical XBRL QName
concepts have identical definitions or historical PIT availability.
No XBRL, source rows, issuer/filing IDs, value, sign or delta persist.
"""
from __future__ import annotations
import argparse
from decimal import Decimal,InvalidOperation
import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import (
    _official_get,ACCOUNT_ID,LEGACY_ACCOUNT_ID,OPERATING_LABELS,
)
from research_v1_opendart_original_xbrl_pilot import _official_xbrl_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import (
    COHORT,_registry,_window,
)
from research_v1_opendart_m20_six_issuer_2022_2023_q3_originals import (
    YEARS,FROZEN_SLOTS,original_first_receipt,original_quarter_fact,
)

OUTPUT=Path("research_results/opendart_m20_2022_23_cfs_comparative_parity")
MAX_CALLS=6
KRW=re.compile(r"-?(?:0|[1-9]\d*)(?:,[0-9]{3})*\Z")
RCPT=re.compile(r"[0-9]{14}\Z")
SAFETY={
    "historical_xbrl_qname_equivalence_verified":False,
    "initial_xbrl_statement_table_binding_verified":False,
    "historical_security_corp_mapping_verified":False,
    "historical_intraday_publication_pit_verified":False,
    "historical_correction_lineage_complete":False,
    "market_status_and_true_cost_return_path_verified":False,
    "full_universe_history_verified":False,
    "m20_feature_pit_admitted":False,
    "m20_performance_run_authorized":False,
    "independent_holdout_authorized":False,
    "champion_change_authorized":False,
    "real_orders_authorized":False,
    "funds_movement_authorized":False,
    "permissions_change_authorized":False,
    "data_values_issuer_ids_and_source_rows_saved":False,
    "ordering":"DISABLED",
}


class OriginalComparativeGap(ValueError):
    pass


def _money(value:object)->Decimal:
    if type(value) is not str or not KRW.fullmatch(value.strip()):
        raise OriginalComparativeGap("LATEST_CFS_THREE_MONTH_KRW_INVALID")
    try:
        amount=Decimal(value.strip().replace(",",""))
    except (InvalidOperation,ValueError):
        raise OriginalComparativeGap("LATEST_CFS_THREE_MONTH_KRW_INVALID") from None
    if not amount.is_finite():
        raise OriginalComparativeGap("LATEST_CFS_THREE_MONTH_KRW_INVALID")
    return amount


def latest_q3_2023_cfs_pair(payload:dict,*,corp_code:str,first_receipt:str):
    if type(payload) is not dict or payload.get("status")!="000":
        raise OriginalComparativeGap("LATEST_CFS_API_NOT_AVAILABLE")
    rows=payload.get("list")
    if type(rows) is not list or len(rows)>5000:
        raise OriginalComparativeGap("LATEST_CFS_API_ROWS_INVALID")
    found=[]
    for row in rows:
        if type(row) is not dict:
            raise OriginalComparativeGap("LATEST_CFS_API_ROW_INVALID")
        if (row.get("corp_code")!=corp_code or row.get("bsns_year")!="2023"
                or row.get("reprt_code")!="11014"
                or row.get("sj_div") not in ("IS","CIS")):
            continue
        if row.get("account_id") not in (ACCOUNT_ID,LEGACY_ACCOUNT_ID):
            continue
        if (row.get("currency")!="KRW"
                or row.get("account_nm") not in OPERATING_LABELS
                or row.get("fs_div") not in (None,"CFS")):
            raise OriginalComparativeGap("LATEST_CFS_OPERATING_SEMANTIC_INVALID")
        rcpt=row.get("rcept_no")
        if type(rcpt) is not str or not RCPT.fullmatch(rcpt):
            raise OriginalComparativeGap("LATEST_CFS_RECEIPT_INVALID")
        # Explicitly never read thstrm_add_amount or frmtrm_add_amount.
        current=_money(row.get("thstrm_amount"))
        preceding=_money(row.get("frmtrm_q_amount"))
        found.append((current,preceding,rcpt==first_receipt,
                      row["account_id"]==ACCOUNT_ID))
    if len(found)!=1:
        raise OriginalComparativeGap("LATEST_CFS_OPERATING_ACCOUNT_NOT_UNIQUE")
    return found[0]


def inspect_original_vs_latest(archive22:bytes,archive23:bytes,api:dict,
                               *,corp_code:str,receipt23:str)->dict:
    first22=original_quarter_fact(archive22,2022)
    first23=original_quarter_fact(archive23,2023)
    now,prior,receipt_match,api_uses_dart=latest_q3_2023_cfs_pair(
        api,corp_code=corp_code,first_receipt=receipt23)
    return {
        "two_initial_original_Q3_XBRL_financial_facts_found":True,
        "initial_qnames_same":first22[0]==first23[0],
        "initial_local_concept_name_same":first22[0].rsplit("}",1)[-1]==
                                          first23[0].rsplit("}",1)[-1],
        "initial_source_namespace_same":first22[0].split("}")[0]==
                                         first23[0].split("}")[0],
        "initial_reporter_identity_same":first22[2]==first23[2],
        "initial_declared_precision_same":first22[1]==first23[1],
        "api_2023_3month_equals_2023_first_original":now==first23[3],
        "api_2022_comparative_3month_equals_2022_first_original":prior==first22[3],
        "api_2023_receipt_is_first_submitted":receipt_match,
        "api_operating_account_uses_dart_namespace":api_uses_dart,
        "origins_versus_current_2023_CFS_both_values_match":bool(
            now==first23[3] and prior==first22[3] and receipt_match),
        "historic_xbrl_qname_compatibility_admitted":False,
        "numeric_values_delta_or_sign_logged":False,
    }


def run(slot:int,session=None)->dict:
    if type(slot) is not int or slot not in FROZEN_SLOTS:
        return {"source_status":"FAIL_CLOSED_FROZEN_SLOT_INVALID",**SAFETY}
    key=os.getenv("OPENDART_API_KEY","").strip()
    report={
        "purpose":"M20_ORIGINAL_2022_2023_Q3_VS_PRESENT_DAY_2023_CFS_API",
        "source_status":"AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "cohort_slot":slot,
        "credential_present":bool(key),
        "max_approved_official_requests":MAX_CALLS,
        "two_initial_original_Q3_XBRL_financial_facts_found":False,
        "origins_versus_current_2023_CFS_both_values_match":False,
        **SAFETY,
    }
    if not key:
        return report
    if session is None:
        import requests
        session=requests.Session()
    try:
        registry=_official_get(session,"corpCode.xml",{"crtfc_key":key},
                               zip_response=True)
        corp=_registry(registry).get(COHORT[slot])
        if corp is None:
            raise OriginalComparativeGap("FIXED_CORP_NOT_FOUND")
        original={}
        for year in YEARS:
            start,end=_window(year)
            listing=_official_get(session,"list.json",{
                "crtfc_key":key,"corp_code":corp,"bgn_de":start,
                "end_de":end,"pblntf_ty":"A","page_count":"100",
            })
            original[year]=original_first_receipt(listing,year)
        raw22=_official_xbrl_get(session,key,original[2022])
        raw23=_official_xbrl_get(session,key,original[2023])
        api=_official_get(session,"fnlttSinglAcntAll.json",{
            "crtfc_key":key,"corp_code":corp,
            "bsns_year":"2023","reprt_code":"11014","fs_div":"CFS",
        })
        report.update(inspect_original_vs_latest(
            raw22,raw23,api,corp_code=corp,receipt23=original[2023]))
        report["source_status"]="ORIGINAL_2022_2023_TO_CFS_3MONTH_PARITY_DIAGNOSTIC_ONLY"
    except Exception as ex:
        approved={
            "LATEST_CFS_THREE_MONTH_KRW_INVALID","LATEST_CFS_API_NOT_AVAILABLE",
            "LATEST_CFS_API_ROWS_INVALID","LATEST_CFS_API_ROW_INVALID",
            "LATEST_CFS_OPERATING_SEMANTIC_INVALID","LATEST_CFS_RECEIPT_INVALID",
            "LATEST_CFS_OPERATING_ACCOUNT_NOT_UNIQUE","FIXED_CORP_NOT_FOUND",
        }
        msg=str(ex) if type(ex) is OriginalComparativeGap else ""
        report["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        report["failure_code"]=msg if msg in approved else "UNCLASSIFIED"
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cohort-slot",required=True,type=int,choices=FROZEN_SLOTS)
    args=p.parse_args()
    result=run(args.cohort_slot)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/f"slot_{args.cohort_slot}.json").write_text(
        json.dumps(result,sort_keys=True,indent=2),encoding="utf-8")
    print("OPENDART_M20_2022_2023_ORIGINAL_CFS_PARITY="+json.dumps(
        result,sort_keys=True),flush=True)
