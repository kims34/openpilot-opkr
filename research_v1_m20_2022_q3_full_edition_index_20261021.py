"""One-pass official index continuity: frozen 2022 Q3 first vs later correction.

Exactly 3 bounded read-only OpenDART requests: corpCode.xml, complete
2022-10-01..2023-02-28 original issuer periodic list, complete
2023-03-01..2026-10-21 later issuer periodic list. Fail closed on any page
truncation, missing or multiple first editions, ambiguous report title,
withdrawal, unexpected company, duplicate receipt, new correction, orphaned
correction or shifted prior 31-row baseline. This proves only an observed
bounded index chronology; NO source financial accounting, publication clock,
historical security PIT, return, holdout, broker or live authorization.
"""
from __future__ import annotations

from datetime import datetime, date, timezone, timedelta
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
from research_v1_opendart_m20_2022_source_proof import _bounded_revision_shape
from research_v1_opendart_m20_2022_later_edition_census import (
    LATER_BEGIN, AS_OF as OLD_LATE_END, REPORT, CATEGORIES,
)
from research_v1_m20_2022_q3_incremental_correction_census import START as DELTA_BEGIN, END as DELTA_END

OUT=Path("research_results/m20_2022_q3_full_contiguous_edition_index/source_counts.json")
SLOT=5
YEAR=2022
END="20261021"  # last fully elapsed Korea-local date when this test was designed
EXPECTED_PRIOR_LATE_PERIODIC_ROWS=31
MAX_ROWS=100
MAX_OFFICIAL_GETS=3
DAY=re.compile(r"[0-9]{8}\Z")
RECEIPT=re.compile(r"[0-9]{14}\Z")
COMPANY=re.compile(r"[0-9]{8}\Z")
SAFETY={
    "index_is_historically_immutable_archive_verified":False,
    "original_2022_q3_cfs_standalone_operating_profit_verified":False,
    "original_2021_q3_cfs_comparative_operating_profit_verified":False,
    "2022_first_publication_instant_verified":False,
    "original_vs_correction_financial_cell_change_verified":False,
    "all_time_revision_history_verified":False,
    "historical_corporation_security_pit_verified":False,
    "official_krx_historical_session_verified":False,
    "m20_feature_pit_admitted":False,
    "m20_performance_run_authorized":False,
    "independent_holdout_authorized":False,
    "champion_change_authorized":False,
    "real_orders_authorized":False,
    "funds_movement_authorized":False,
    "permissions_change_authorized":False,
    "raw_company_receipts_filing_days_titles_source_or_values_persisted":False,
    "ordering":"DISABLED",
}

class ContiguousGap(ValueError):
    """Only fixed public-safe error codes may leave this source gate."""


def _day(value: str) -> date:
    if type(value) is not str or not DAY.fullmatch(value):
        raise ContiguousGap("OFFICIAL_INDEX_DAY_INVALID")
    try:
        return date(int(value[:4]),int(value[4:6]),int(value[6:]))
    except ValueError:
        raise ContiguousGap("OFFICIAL_INDEX_DAY_INVALID") from None


def _validate_window():
    original_start, original_end=_window(YEAR)
    if original_start!="20221001" or original_end!="20230228":
        raise ContiguousGap("ORIGINAL_WINDOW_DRIFT")
    if (_day(original_end)+timedelta(days=1)!=_day(LATER_BEGIN)
        or _day(OLD_LATE_END)+timedelta(days=1)!=_day(DELTA_BEGIN)
        or DELTA_END!=END):
        raise ContiguousGap("PREVIOUS_CENSUS_WINDOW_CONTIGUITY_DRIFT")
    localtoday=datetime.now(timezone(timedelta(hours=9))).date()
    if localtoday <= _day(END):
        raise ContiguousGap("CENSUS_CURRENT_KOREA_DAY_INCOMPLETE")


def _strict_rows(payload: dict, company: str, begin: str, end: str)->list[dict]:
    if type(company) is not str or not COMPANY.fullmatch(company):
        raise ContiguousGap("REGISTRY_COMPANY_INVALID")
    if type(payload) is not dict or payload.get("status")!="000":
        raise ContiguousGap("CONTIGUOUS_OFFICIAL_INDEX_STATUS_UNVERIFIED")
    def natural(k):
        x=payload.get(k)
        if type(x) is int and 0<=x<=MAX_ROWS:
            return x
        if type(x) is str and re.fullmatch(r"0|[1-9][0-9]*",x):
            n=int(x)
            if n<=MAX_ROWS:
                return n
        raise ContiguousGap("CONTIGUOUS_INDEX_PAGINATION_INVALID")
    total=natural("total_count")
    pages=natural("total_page")
    page=natural("page_no")
    rows=payload.get("list")
    if (not (1<=total<=MAX_ROWS) or pages!=1 or page!=1
        or type(rows) is not list or len(rows)!=total):
        raise ContiguousGap("CONTIGUOUS_INDEX_TRUNCATED_OR_MISSING")
    known=set()
    for row in rows:
        if type(row) is not dict:
            raise ContiguousGap("CONTIGUOUS_INDEX_ROW_INVALID")
        receipt=row.get("rcept_no")
        when=row.get("rcept_dt")
        title=row.get("report_nm")
        issuer=row.get("corp_code")
        if (type(receipt) is not str or not RECEIPT.fullmatch(receipt)
            or receipt in known or type(title) is not str
            or issuer!=company or type(when) is not str):
            raise ContiguousGap("CONTIGUOUS_INDEX_ROW_OR_ISSUER_INVALID")
        known.add(receipt)
        if receipt[:8]!=when or not _day(begin)<=_day(when)<=_day(end):
            raise ContiguousGap("CONTIGUOUS_INDEX_DAY_OUTSIDE_WINDOW")
    return rows


def verify_source_indexes(first: dict, later: dict, *, issuer: str) -> dict:
    """Source-only fixed chronology; leaves all source records in memory."""
    _validate_window()
    first_start, first_end=_window(YEAR)
    first_rows=_strict_rows(first,issuer,first_start,first_end)
    later_rows=_strict_rows(later,issuer,LATER_BEGIN,END)
    orig=original_first_receipt(first,YEAR)
    hint=_bounded_revision_shape(first,orig)
    if (not hint["original_index_indicates_possible_later_correction"]
        or hint["same_period_confirmed_corrections_in_initial_window"]!=0
        or hint["same_period_attachment_additions_not_corrections_in_initial_window"]!=0
        or not hint["original_filing_withdrawal_marker_absent"]):
        raise ContiguousGap("FIRST_SUBMISSION_CORRECTION_HINT_DRIFT")
    if len(later_rows)!=EXPECTED_PRIOR_LATE_PERIODIC_ROWS:
        raise ContiguousGap("LATER_INDEX_ROW_BASELINE_DRIFT")
    if orig in {r["rcept_no"] for r in later_rows}:
        raise ContiguousGap("INITIAL_AND_LATER_RECEIPT_DUPLICATE")

    corrections=[]
    attachments=[]
    for row in later_rows:
        title=row["report_nm"].strip()
        if REPORT not in title:
            continue
        kind=CATEGORIES.get(title)
        if kind=="CORRECTION":
            corrections.append(row)
        elif kind=="ATTACHMENT_ADDITION":
            attachments.append(row)
        else:
            raise ContiguousGap("UNRECOGNIZED_LATER_2022_Q3_EDITION")
    if len(corrections)!=1 or attachments:
        raise ContiguousGap("UNEXPECTED_CORRECTION_OR_ATTACHMENTS")
    correction=corrections[0]
    if (correction["rcept_dt"]<=orig[:8]
        or correction["rcept_dt"]>OLD_LATE_END):
        raise ContiguousGap("CORRECTION_OUTSIDE_PREVIOUSLY_PINNED_INDEX")
    if any(REPORT in row["report_nm"]
           for row in later_rows if row["rcept_dt"]>=DELTA_BEGIN):
        raise ContiguousGap("NEW_FROZEN_REPORT_EDITION_IN_INCREMENT")
    return {
        "source_status":"FULL_CONTIGUOUS_OFFICIAL_INDEX_RANGE_VERIFIED_SOURCE_ONLY",
        "first_submission_window_complete_paged":True,
        "later_correction_window_complete_paged":True,
        "initial_to_later_index_windows_adjacent":True,
        "all_scanned_index_rows_same_current_registry_issuer":True,
        "original_first_2022_q3_filing_unique":True,
        "initial_official_first_receipt_correction_marker_seen":True,
        "later_verified_correction_rows":len(corrections),
        "later_verified_attachment_addition_rows":len(attachments),
        "later_periodic_index_rows":len(later_rows),
        "new_correction_after_prior_2026_10_13_boundary":False,
        "observed_correction_index_coverage_end":"20261021",
        "current_day_20261022_index_complete":False,
        "original_to_corrected_data_semantics_bound":False,
    }


def execute(session, key: str)->dict:
    _validate_window()
    raw=_official_get(session,"corpCode.xml",{"crtfc_key":key},zip_response=True)
    issuer=_registry(raw).get(COHORT[SLOT])
    if issuer is None:
        raise ContiguousGap("FIXED_CURRENT_REGISTRY_ISSUER_MISSING")
    first_begin,first_end=_window(YEAR)
    base={"crtfc_key":key,"corp_code":issuer,"pblntf_ty":"A",
          "last_reprt_at":"N","page_no":"1","page_count":"100"}
    first=_official_get(session,"list.json",{**base,"bgn_de":first_begin,"end_de":first_end})
    later=_official_get(session,"list.json",{**base,"bgn_de":LATER_BEGIN,"end_de":END})
    return verify_source_indexes(first,later,issuer=issuer)


def run(session=None)->dict:
    key=os.environ.get("OPENDART_API_KEY","").strip()
    z={
        "purpose":"FROZEN_SLOT5_2022_Q3_FIRST_TO_20261021_CONTIGUOUS_OFFICIAL_EDITION_CENSUS",
        "fixed_cohort_slot":SLOT,
        "max_official_requests":MAX_OFFICIAL_GETS,
        "credential_present":bool(key),
        "source_status":"PENDING" if key else "AUTH_NOT_CONFIGURED",
        **SAFETY,
    }
    if not key:
        return z
    if session is None:
        import requests
        session=requests.Session()
    try:
        z.update(execute(session,key))
    except Exception as exc:
        allow={
            "OFFICIAL_INDEX_DAY_INVALID","ORIGINAL_WINDOW_DRIFT",
            "PREVIOUS_CENSUS_WINDOW_CONTIGUITY_DRIFT",
            "CENSUS_CURRENT_KOREA_DAY_INCOMPLETE","REGISTRY_COMPANY_INVALID",
            "CONTIGUOUS_OFFICIAL_INDEX_STATUS_UNVERIFIED",
            "CONTIGUOUS_INDEX_PAGINATION_INVALID",
            "CONTIGUOUS_INDEX_TRUNCATED_OR_MISSING",
            "CONTIGUOUS_INDEX_ROW_INVALID",
            "CONTIGUOUS_INDEX_ROW_OR_ISSUER_INVALID",
            "CONTIGUOUS_INDEX_DAY_OUTSIDE_WINDOW",
            "FIRST_SUBMISSION_CORRECTION_HINT_DRIFT",
            "LATER_INDEX_ROW_BASELINE_DRIFT",
            "INITIAL_AND_LATER_RECEIPT_DUPLICATE",
            "UNRECOGNIZED_LATER_2022_Q3_EDITION",
            "UNEXPECTED_CORRECTION_OR_ATTACHMENTS",
            "CORRECTION_OUTSIDE_PREVIOUSLY_PINNED_INDEX",
            "NEW_FROZEN_REPORT_EDITION_IN_INCREMENT",
            "FIXED_CURRENT_REGISTRY_ISSUER_MISSING",
        }
        code=str(exc) if type(exc) is ContiguousGap else ""
        z["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        z["source_gap_reason"]=code if code in allow else "UNVERIFIED_ORIGINAL_TO_LATER_SOURCE"
    return z


if __name__=="__main__":
    report=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,sort_keys=True,indent=2),encoding="utf-8")
    print("M20_FULL_OFFICIAL_EDITION_CENSUS="+json.dumps(report,sort_keys=True),flush=True)
