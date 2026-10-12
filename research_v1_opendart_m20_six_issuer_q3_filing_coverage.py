"""Non-promotable multi-issuer original Q3 *filing-date* coverage probe.

Six preselected KOSPI examples, 2022-2025 Q3, at most 25 approved
official OpenDART requests: corpCode.xml once and list.json <=24.
Cohort is source-feasibility only, not representative/performance-selected.
No XBRL, earnings, market data, raw rows, firm identities, receipts or
historic filing dates stored/logged. Current registry is NOT historical PIT.
Never infer same-day publication time or cross-company historical status.
"""
from __future__ import annotations
from collections import Counter
from datetime import date
import io
import json
import os
from pathlib import Path
import re
import time
import zipfile
from defusedxml.ElementTree import fromstring
from defusedxml.common import DefusedXmlException
from xml.etree.ElementTree import ParseError
from research_v1_opendart_lineage_pilot import _official_get

# Source feasibility cohort frozen before reading any new official results.
COHORT=("000660","005380","005930","035420","051910","105560")
YEARS=(2022,2023,2024,2025)
MAX_CALLS=1+len(COHORT)*len(YEARS)
OUTPUT=Path("research_results/opendart_m20_six_issuer_q3_vintage/summary.json")
RECEIPT=re.compile(r"[0-9]{14}\Z")
CORPORATION=re.compile(r"[0-9]{8}\Z")
BLOCKS={
    "historical_kospi_membership_verified":False,
    "historical_corp_to_security_mapping_verified":False,
    "historical_publication_instant_verified":False,
    "historical_publication_pit_verified":False,
    "original_quarterly_operating_profit_verified":False,
    "original_filing_xbrl_fetched":False,
    "full_cross_section_and_quarter_history_covered":False,
    "m20_signal_pit_admitted":False,
    "m20_performance_run_authorized":False,
    "independent_holdout_authorized":False,
    "champion_change_authorized":False,
    "real_orders_authorized":False,
    "funds_movement_authorized":False,
    "permissions_change_authorized":False,
    "ordering":"DISABLED",
    "raw_provider_values_or_identifiers_saved":False,
}

class CoverageError(ValueError):
    """Fixed, public-safe reason codes only."""

def _window(year:int)->tuple[str,str]:
    if type(year) is not int or year not in YEARS:
        raise CoverageError("REPORT_YEAR_OUT_OF_SCOPE")
    # A bounded original-first-filing search; later amendment-history
    # completeness is NOT claimed.
    return f"{year}1001",f"{year+1}0228"

def _registry(blob:bytes)->dict[str,str]:
    if type(blob) is not bytes or not 4<=len(blob)<=32_000_000:
        raise CoverageError("CORPORATE_REGISTRY_ZIP_INVALID")
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            entries=[x for x in z.infolist()
                     if not x.is_dir() and x.filename.upper()=="CORPCODE.XML"]
            if len(entries)!=1 or entries[0].file_size>40_000_000:
                raise CoverageError("CORPORATE_REGISTRY_XML_INVALID")
            root=fromstring(z.read(entries[0]),forbid_dtd=True,
                            forbid_entities=True,forbid_external=True)
    except (zipfile.BadZipFile,DefusedXmlException,ParseError,
            OSError,ValueError,RuntimeError):
        raise CoverageError("CORPORATE_REGISTRY_UNSAFE") from None
    matches={code:[] for code in COHORT}
    for row in root.iter("list"):
        fields={child.tag:child.text for child in row}
        symbol=(fields.get("stock_code") or "").strip()
        if symbol not in matches:
            continue
        issuer=(fields.get("corp_code") or "").strip()
        if not CORPORATION.fullmatch(issuer):
            raise CoverageError("CORPORATION_IDENTIFIER_INVALID")
        matches[symbol].append(issuer)
    if any(len(items)>1 for items in matches.values()):
        raise CoverageError("CORPORATION_MAPPING_NOT_UNIQUE")
    return {code:items[0] for code,items in matches.items() if items}

def _index_state(data:dict,year:int,begin:str,end:str)->str:
    if type(data) is not dict:
        raise CoverageError("FILING_INDEX_SHAPE_INVALID")
    if data.get("status")=="013":
        return "NO_FILINGS_IN_WINDOW"
    if data.get("status")!="000":
        raise CoverageError("FILING_INDEX_OFFICIAL_STATUS_FAILED")
    pagination=[]
    for key in ("total_count","total_page","page_no"):
        value=data.get(key)
        if type(value) not in (str,int) or not re.fullmatch(r"[0-9]+",str(value)):
            raise CoverageError("FILING_INDEX_PAGINATION_INVALID")
        pagination.append(int(value))
    total,pages,number=pagination
    rows=data.get("list")
    if pages!=1 or number!=1 or total>100 or type(rows) is not list or len(rows)!=total:
        raise CoverageError("FILING_INDEX_PAGES_UNVERIFIED")
    seen=set()
    candidates=[]
    lo=date(int(begin[:4]),int(begin[4:6]),int(begin[6:]))
    hi=date(int(end[:4]),int(end[4:6]),int(end[6:]))
    exact=f"분기보고서 ({year}.09)"
    for row in rows:
        if type(row) is not dict:
            raise CoverageError("FILING_INDEX_ROW_INVALID")
        rid,day,name=(row.get("rcept_no"),row.get("rcept_dt"),row.get("report_nm"))
        if (type(rid) is not str or not RECEIPT.fullmatch(rid) or rid in seen
                or type(day) is not str or not re.fullmatch(r"[0-9]{8}",day)
                or type(name) is not str):
            raise CoverageError("FILING_INDEX_ROW_INVALID")
        seen.add(rid)
        try:
            when=date(int(day[:4]),int(day[4:6]),int(day[6:]))
        except ValueError:
            raise CoverageError("FILING_INDEX_DATE_INVALID") from None
        if rid[:8]!=day or not lo<=when<=hi:
            raise CoverageError("FILING_INDEX_CHRONOLOGY_INVALID")
        if exact in name:
            if when<=date(year,9,30):
                raise CoverageError("QUARTERLY_REPORT_PRECEDES_QUARTER")
            candidates.append((when,name.strip()))
    if not candidates:
        return "Q3_ORIGINAL_NOT_FOUND"
    first=min(d for d,_ in candidates)
    first_day=[name for d,name in candidates if d==first]
    if len(first_day)!=1:
        return "INITIAL_FILING_DATE_MULTIPLE_VERSIONS"
    if first_day[0]!=exact:
        return "INITIAL_VERSION_NOT_ORIGINAL"
    return "ORIGINAL_FIRST_FILING_DATE_ONLY_NOT_PIT"

def _execute(session,key:str,sleep=time.sleep)->dict:
    count=0
    def approved(endpoint,params,*,zip_response=False):
        nonlocal count
        if endpoint not in ("corpCode.xml","list.json") or count>=MAX_CALLS:
            raise CoverageError("APPROVED_ENDPOINT_OR_BUDGET_EXCEEDED")
        count+=1
        return _official_get(session,endpoint,params,zip_response=zip_response)
    identities=_registry(approved("corpCode.xml",{"crtfc_key":key},zip_response=True))
    outcomes=Counter()
    for year in YEARS:
        start,end=_window(year)
        for symbol in COHORT:
            corp=identities.get(symbol)
            if not corp:
                outcomes[year,"REGISTRY_ISSUER_ABSENT"]+=1
                continue
            resp=approved("list.json",{
                "crtfc_key":key,"corp_code":corp,
                "bgn_de":start,"end_de":end,
                "pblntf_ty":"A","page_count":"100",
            })
            outcomes[year,_index_state(resp,year,start,end)]+=1
            sleep(0.05)
    group={}
    for year in YEARS:
        group[str(year)]={
            "cohort_size":len(COHORT),
            "unambiguous_original_q3_date_count":outcomes[year,"ORIGINAL_FIRST_FILING_DATE_ONLY_NOT_PIT"],
            "missing_registry_mapping_count":outcomes[year,"REGISTRY_ISSUER_ABSENT"],
            "missing_original_or_periodic_report_count":(
                outcomes[year,"NO_FILINGS_IN_WINDOW"]+outcomes[year,"Q3_ORIGINAL_NOT_FOUND"]),
            "same_day_version_ambiguity_count":outcomes[year,"INITIAL_FILING_DATE_MULTIPLE_VERSIONS"],
            "first_version_not_original_count":outcomes[year,"INITIAL_VERSION_NOT_ORIGINAL"],
        }
    return {
        "official_api_requests":count,
        "fixed_issuer_count":len(COHORT),
        "years_examined":len(YEARS),
        "potential_original_report_cells":len(COHORT)*len(YEARS),
        "date_identified_original_report_cells":sum(
            r["unambiguous_original_q3_date_count"] for r in group.values()),
        "currently_mapped_issuer_count":len(identities),
        "year_coverage_aggregates":group,
        "source_status":"FIXED_COHORT_ORIGINAL_Q3_DATE_COVERAGE_NOT_PIT",
        **BLOCKS,
    }

def run(session=None)->dict:
    key=os.environ.get("OPENDART_API_KEY","").strip()
    result={
        "purpose":"M20_2022_2025_SIX_ISSUER_ORIGINAL_Q3_DATE_COVERAGE",
        "source":"OPENDART_OFFICIAL_APPROVED_ONLY",
        "source_status":"AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "key_configured":bool(key),
        "max_api_requests":MAX_CALLS,
        "official_api_requests":0,
        "potential_original_report_cells":len(COHORT)*len(YEARS),
        "date_identified_original_report_cells":0,
        "issuer_identifiers_filing_dates_or_receipts_saved":False,
        **BLOCKS,
    }
    if not key:
        return result
    if session is None:
        import requests
        session=requests.Session()
    try:
        result.update(_execute(session,key))
    except Exception as ex:
        allow={
            "REPORT_YEAR_OUT_OF_SCOPE","CORPORATE_REGISTRY_ZIP_INVALID",
            "CORPORATE_REGISTRY_XML_INVALID","CORPORATE_REGISTRY_UNSAFE",
            "CORPORATION_IDENTIFIER_INVALID","CORPORATION_MAPPING_NOT_UNIQUE",
            "FILING_INDEX_SHAPE_INVALID","FILING_INDEX_OFFICIAL_STATUS_FAILED",
            "FILING_INDEX_PAGINATION_INVALID","FILING_INDEX_PAGES_UNVERIFIED",
            "FILING_INDEX_ROW_INVALID","FILING_INDEX_DATE_INVALID",
            "FILING_INDEX_CHRONOLOGY_INVALID","QUARTERLY_REPORT_PRECEDES_QUARTER",
            "APPROVED_ENDPOINT_OR_BUDGET_EXCEEDED",
        }
        reason=str(ex) if type(ex) is CoverageError else ""
        result["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        result["failure_reason_code"]=reason if reason in allow else "UNCLASSIFIED"
    return result

if __name__=="__main__":
    report=run()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2),
                      encoding="utf-8")
    print("OPENDART_M20_SIX_ISSUER_Q3_COVERAGE="+json.dumps(report,sort_keys=True),
          flush=True)
