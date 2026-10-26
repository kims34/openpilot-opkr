"""Incremental official OpenDART 2022-Q3 correction-index evidence, source only.

A new, strictly bounded window immediately following the previous successful
historical amendment census (through 2026-10-13) is queried through the last
*fully elapsed* Korea-local day, 2026-10-21. Two read-only authenticated
requests maximum: corpCode.xml registry and list.json for one frozen cohort
slot 5 issuer. Status 013 means no queried data PER OFFICIAL DOCUMENTATION,
not missing original historical financial statement. Never store/print
issuer, receipt, actual event date, raw report name, provider message,
source JSON/ZIP, amounts, tokens or market/broker data. This is not an
original CFS cell, correction-to-cell binding or historical PIT admission.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import COHORT, _registry
from research_v1_opendart_m20_2022_later_edition_census import (
    AS_OF as PRIOR_CENSUS_END, CATEGORIES, REPORT
)

START="20261014"
END="20261021"
SLOT=5
MAX_API_CALLS=2
MAX_ROWS=100
OUT=Path("research_results/m20_2022_q3_incremental_correction_census/source_only.json")
YMD=re.compile(r"[0-9]{8}\Z")
REC=re.compile(r"[0-9]{14}\Z")
STATIC={
    "first_original_2022_q3_cfs_3month_profit_verified":False,
    "first_original_2021_q3_comparator_verified":False,
    "original_to_amended_profit_cell_binding_verified":False,
    "full_correction_lineage_all_time_verified":False,
    "first_filing_publication_instant_verified":False,
    "historical_issuer_security_pit_verified":False,
    "official_historical_market_calendar_verified":False,
    "m20_feature_pit_admitted":False,
    "m20_performance_run_authorized":False,
    "independent_holdout_authorized":False,
    "champion_change_authorized":False,
    "real_orders_authorized":False,
    "funds_movement_authorized":False,
    "permissions_change_authorized":False,
    "raw_identifiers_dates_names_amounts_or_provider_contents_saved":False,
    "ordering":"DISABLED",
}

class IncrementalGap(ValueError):
    """Fixed public-safe failure reason, never user/provider strings."""


def _day(raw: str)->date:
    if type(raw) is not str or not YMD.fullmatch(raw):
        raise IncrementalGap("OFFICIAL_DAY_SHAPE_INVALID")
    try:
        return date(int(raw[:4]),int(raw[4:6]),int(raw[6:]))
    except ValueError:
        raise IncrementalGap("OFFICIAL_CALENDAR_DAY_INVALID") from None


def _scope()->None:
    if len(COHORT)<=SLOT or _day(START)!=_day(PRIOR_CENSUS_END)+timedelta(days=1):
        raise IncrementalGap("CONTIGUOUS_PREVIOUS_INDEX_SCOPE_DRIFT")
    if _day(END)!=date(2026,10,21) or _day(START)>_day(END):
        raise IncrementalGap("BOUNDED_CENSUS_WINDOW_DRIFT")
    # Current day is not complete: no later session completeness from intraday data.
    korea=datetime.now(timezone(timedelta(hours=9))).date()
    if korea<=_day(END):
        raise IncrementalGap("BOUNDED_WINDOW_DAY_NOT_FULLY_ELAPSED")


def inspect_index(body: dict, *, expected_company: str)->dict:
    """Validate single scoped official page, including 013 absent-data case."""
    if type(expected_company) is not str or not re.fullmatch(r"[0-9]{8}",expected_company):
        raise IncrementalGap("COMPANY_MAPPING_SHAPE_INVALID")
    if type(body) is not dict:
        raise IncrementalGap("OFFICIAL_INDEX_NOT_AN_OBJECT")
    state=body.get("status")
    if state=="013":
        # Official list API 013 = "조회된 데이터가 없습니다".
        # Any attached substantive rows/pagination invalidate absent-data assertion.
        if (body.get("list") not in (None,[])
                or any(body.get(k) not in (None,0,"0") for k in
                       ("total_count","total_page","page_no"))):
            raise IncrementalGap("NO_DATA_STATUS_WITH_ROWS_OR_PAGINATION")
        return {
            "source_status":"OFFICIAL_INDEX_013_NO_ROWS_IN_INCREMENTAL_WINDOW",
            "official_013_no_query_results":True,
            "official_scoped_index_metadata_retrieved":True,
            "bounded_index_rows_examined":0,
            "new_2022_q3_correction_rows_in_window":0,
            "new_2022_q3_attachment_rows_in_window":0,
            "new_target_edition_found_stop":False,
            "incremental_window_has_no_matching_target_report":True,
        }
    if state!="000":
        raise IncrementalGap("OFFICIAL_INDEX_UNVERIFIED_PROVIDER_STATUS")
    def num(name: str)->int:
        v=body.get(name)
        if type(v) is int and v>=0:
            return v
        if type(v) is str and re.fullmatch(r"0|[1-9][0-9]*",v):
            return int(v)
        raise IncrementalGap("OFFICIAL_INDEX_PAGINATION_INVALID")
    total=num("total_count")
    pages=num("total_page")
    pageno=num("page_no")
    rows=body.get("list")
    if not (pages==1 and pageno==1 and 1<=total<=MAX_ROWS
            and type(rows) is list and len(rows)==total):
        raise IncrementalGap("OFFICIAL_INDEX_PAGINATION_INCOMPLETE")
    unique=set()
    corrections=0
    attachments=0
    for item in rows:
        if type(item) is not dict:
            raise IncrementalGap("OFFICIAL_ROW_SHAPE_INVALID")
        receipt=item.get("rcept_no")
        day=item.get("rcept_dt")
        company=item.get("corp_code")
        name=item.get("report_nm")
        if (type(receipt) is not str or not REC.fullmatch(receipt)
                or receipt in unique or type(name) is not str
                or company!=expected_company or type(day) is not str):
            raise IncrementalGap("OFFICIAL_ROW_IDENTITY_INVALID")
        if not _day(START)<=_day(day)<=_day(END) or receipt[:8]!=day:
            raise IncrementalGap("OFFICIAL_ROW_DATE_OR_WINDOW_INVALID")
        unique.add(receipt)
        if REPORT not in name:
            continue
        category=CATEGORIES.get(name.strip())
        if category=="CORRECTION":
            corrections+=1
        elif category=="ATTACHMENT_ADDITION":
            attachments+=1
        else:
            raise IncrementalGap("TARGET_2022_Q3_UNRECOGNIZED_EDITION")
    detected=(corrections+attachments)>0
    return {
        "source_status":(
            "ADDITIONAL_TARGET_EDITION_FOUND_QUARANTINE"
            if detected else "OFFICIAL_INDEX_000_NO_TARGET_EDITION_IN_INCREMENTAL_WINDOW"
        ),
        "official_013_no_query_results":False,
        "official_scoped_index_metadata_retrieved":True,
        "bounded_index_rows_examined":total,
        "new_2022_q3_correction_rows_in_window":corrections,
        "new_2022_q3_attachment_rows_in_window":attachments,
        "new_target_edition_found_stop":detected,
        "incremental_window_has_no_matching_target_report":not detected,
    }


def execute(session, key: str)->dict:
    _scope()
    raw=_official_get(session,"corpCode.xml",{"crtfc_key":key},zip_response=True)
    company=_registry(raw).get(COHORT[SLOT])
    if company is None:
        raise IncrementalGap("FROZEN_ISSUER_CURRENT_REGISTRY_MISSING")
    result=_official_get(session,"list.json",{
        "crtfc_key":key,"corp_code":company,"bgn_de":START,"end_de":END,
        "pblntf_ty":"A","last_reprt_at":"N","page_no":"1",
        "page_count":"100",
    })
    return inspect_index(result,expected_company=company)


def run(session=None)->dict:
    key=os.getenv("OPENDART_API_KEY","").strip()
    answer={
        "purpose":"FROZEN_SLOT5_2022_Q3_INCREMENTAL_20261014_20261021_AMENDMENT_CENSUS",
        "fixed_cohort_slot":SLOT,
        "max_official_requests":MAX_API_CALLS,
        "credential_present":bool(key),
        "source_status":"PENDING" if key else "AUTH_NOT_CONFIGURED",
        **STATIC,
    }
    if not key:
        return answer
    if session is None:
        import requests
        session=requests.Session()
    try:
        answer.update(execute(session,key))
    except Exception as exc:
        public={
            "OFFICIAL_DAY_SHAPE_INVALID","OFFICIAL_CALENDAR_DAY_INVALID",
            "CONTIGUOUS_PREVIOUS_INDEX_SCOPE_DRIFT","BOUNDED_CENSUS_WINDOW_DRIFT",
            "BOUNDED_WINDOW_DAY_NOT_FULLY_ELAPSED","COMPANY_MAPPING_SHAPE_INVALID",
            "OFFICIAL_INDEX_NOT_AN_OBJECT","NO_DATA_STATUS_WITH_ROWS_OR_PAGINATION",
            "OFFICIAL_INDEX_UNVERIFIED_PROVIDER_STATUS",
            "OFFICIAL_INDEX_PAGINATION_INVALID",
            "OFFICIAL_INDEX_PAGINATION_INCOMPLETE","OFFICIAL_ROW_SHAPE_INVALID",
            "OFFICIAL_ROW_IDENTITY_INVALID","OFFICIAL_ROW_DATE_OR_WINDOW_INVALID",
            "TARGET_2022_Q3_UNRECOGNIZED_EDITION",
            "FROZEN_ISSUER_CURRENT_REGISTRY_MISSING",
        }
        code=str(exc) if type(exc) is IncrementalGap else ""
        answer["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        answer["source_gap_reason"]=code if code in public else "OFFICIAL_INCREMENTAL_CORRECTION_INDEX_UNVERIFIED"
    return answer


if __name__=="__main__":
    result=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2),encoding="utf-8")
    print("M20_INCREMENTAL_2022_Q3_CORRECTION_INDEX="+json.dumps(result,sort_keys=True),flush=True)
