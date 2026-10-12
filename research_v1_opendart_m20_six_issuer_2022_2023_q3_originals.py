"""2022/2023 original Q3 earnings pair evidence for six *fixed* source cohort issuers.

Only the already-used official OpenDART corpCode.xml, list.json and
fnlttXbrl.xml endpoints, five calls maximum per fixed cohort slot.
Original first-submitted quarterly XBRL facts stay in ephemeral memory,
without saving amounts, issuer IDs, receipt IDs, filing dates, ZIPs,
differences, signs or returns. Six slots are ex-ante; no performance
selection or future-company substitutions.

This is source *shape* feasibility only. Historic publication time, actual
historic issuer membership/security mapping, true statement binding,
revisions/corporate actions, KRX tradability, M20 performance and sealed
holdout are NOT verified. No real orders, funds or permissions authorized.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import io
import json
import os
from pathlib import Path
import re
import zipfile

from defusedxml.ElementTree import fromstring
from defusedxml.common import DefusedXmlException
from xml.etree.ElementTree import ParseError

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_original_xbrl_pilot import (
    _official_xbrl_get, inspect_xbrl_zip,
)
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import (
    _registry, _index_state, _window, COHORT,
)
from research_v1_opendart_m20_original_cfs_axis import (
    XBRLI, _local, _statement_axis_kind,
)
from research_v1_opendart_m20_q3_account_cardinality import (
    CONCEPTS, _value_shape_valid,
)
from research_v1_opendart_m20_q3_original_numeric_compat import DECIMALS

YEARS=(2022,2023)
FROZEN_SLOTS=tuple(range(len(COHORT)))
MAX_CALLS_PER_SLOT=5
MAX_XML_SIZE=48*1024*1024
RESULTS=Path("research_results/opendart_m20_2022_23_six_issuer_original_q3")
REC=re.compile(r"[0-9]{14}\Z")
SAFETY={
    "historical_issuer_security_mapping_verified":False,
    "original_statement_table_binding_verified":False,
    "intraday_publication_time_verified":False,
    "historical_filing_pit_verified":False,
    "revision_chain_completed":False,
    "complete_original_quarterly_history_verified":False,
    "all_historical_issuers_verified":False,
    "historical_mcap_and_tradability_verified":False,
    "m20_signal_pit_admitted":False,
    "m20_performance_run_authorized":False,
    "independent_holdout_authorized":False,
    "champion_change_authorized":False,
    "real_orders_authorized":False,
    "funds_movement_authorized":False,
    "permissions_change_authorized":False,
    "financial_amounts_or_issuer_ids_saved":False,
    "ordering":"DISABLED",
}


class HistoricalOriginalGap(ValueError):
    """Use only fixed codes, never provider strings."""


def original_first_receipt(payload:dict,year:int)->str:
    """Select only exact first-submission edition after full-page validation."""
    if type(year) is not int or year not in YEARS:
        raise HistoricalOriginalGap("UNAPPROVED_ORIGINAL_YEAR")
    start,end=_window(year)
    if _index_state(payload,year,start,end)!="ORIGINAL_FIRST_FILING_DATE_ONLY_NOT_PIT":
        raise HistoricalOriginalGap("INITIAL_FILING_AMBIGUOUS_OR_MISSING")
    candidates=[]
    exact=f"분기보고서 ({year}.09)"
    for row in payload["list"]:
        if exact in row["report_nm"]:
            candidates.append(row)
    # _index_state has validated each receipt's shape/day and entire
    # single-page index. Earliest first submission, never a later correction.
    first=min(row["rcept_dt"] for row in candidates)
    earliest=[row for row in candidates if row["rcept_dt"]==first]
    if (len(earliest)!=1 or earliest[0]["report_nm"].strip()!=exact
            or not REC.fullmatch(earliest[0]["rcept_no"])):
        raise HistoricalOriginalGap("INITIAL_FILING_AMBIGUOUS_OR_MISSING")
    return earliest[0]["rcept_no"]


def original_quarter_fact(zip_bytes:bytes,year:int):
    """Bounded ZIP+defused XML to unique CFS/KRW Q3 operating-profit atom.

    Returns one private in-memory tuple only; callers MUST discard it and
    publish boolean compatibility results, never values or identities.
    """
    if type(year) is not int or year not in YEARS:
        raise HistoricalOriginalGap("UNAPPROVED_ORIGINAL_YEAR")
    inspect_xbrl_zip(zip_bytes)
    selected=[]
    period=(f"{year}-07-01",f"{year}-09-30")
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            for info in archive.infolist():
                if info.is_dir() or not info.filename.lower().endswith((".xml",".xbrl")):
                    continue
                if not (0<info.file_size<=MAX_XML_SIZE):
                    raise HistoricalOriginalGap("ORIGINAL_XML_SIZE_INVALID")
                contents=archive.read(info)
                if len(contents)!=info.file_size:
                    raise HistoricalOriginalGap("ORIGINAL_XML_SIZE_INVALID")
                try:
                    root=fromstring(contents,forbid_dtd=True,
                                    forbid_entities=True,forbid_external=True)
                except (DefusedXmlException,ParseError,ValueError):
                    raise HistoricalOriginalGap("ORIGINAL_XML_UNSAFE") from None
                contexts={}
                units={}
                for node in root.iter():
                    if node.tag==XBRLI+"context":
                        context_id=node.attrib.get("id")
                        if not context_id or context_id in contexts:
                            raise HistoricalOriginalGap("ORIGINAL_CONTEXT_AMBIGUOUS")
                        starts=[x.text for x in node.iter() if x.tag==XBRLI+"startDate"]
                        ends=[x.text for x in node.iter() if x.tag==XBRLI+"endDate"]
                        identities=[x for x in node.iter()
                                    if x.tag==XBRLI+"identifier"]
                        if len(starts)!=1 or len(ends)!=1 or len(identities)!=1:
                            continue
                        identity=(identities[0].attrib.get("scheme"),identities[0].text)
                        if not all(type(x) is str and x for x in identity):
                            continue
                        contexts[context_id]=((starts[0],ends[0]),
                                              _statement_axis_kind(node),identity)
                    if node.tag==XBRLI+"unit":
                        unit_id=node.attrib.get("id")
                        if not unit_id or unit_id in units:
                            raise HistoricalOriginalGap("ORIGINAL_UNIT_AMBIGUOUS")
                        measures=[x.text for x in node.iter()
                                  if x.tag==XBRLI+"measure"]
                        is_divided=any(_local(x.tag)=="divide" for x in node.iter())
                        units[unit_id]=not is_divided and measures==["iso4217:KRW"]
                for node in root.iter():
                    if _local(node.tag) not in CONCEPTS:
                        continue
                    ctx=contexts.get(node.attrib.get("contextRef"))
                    if ctx is None:
                        continue
                    dates,axis,identity=ctx
                    if dates!=period or axis!="CONSOLIDATED":
                        continue
                    if not units.get(node.attrib.get("unitRef"),False):
                        continue
                    if not _value_shape_valid(node):
                        continue
                    decimals=node.attrib.get("decimals")
                    if type(decimals) is not str or not DECIMALS.fullmatch(decimals):
                        raise HistoricalOriginalGap("ORIGINAL_NUMERIC_PRECISION_INVALID")
                    try:
                        value=Decimal(node.text.strip())
                    except (TypeError,ValueError,InvalidOperation):
                        raise HistoricalOriginalGap("ORIGINAL_NUMERIC_TEXT_INVALID") from None
                    if not value.is_finite():
                        raise HistoricalOriginalGap("ORIGINAL_NUMERIC_TEXT_INVALID")
                    selected.append((node.tag,decimals,identity,value))
    except (zipfile.BadZipFile,RuntimeError,EOFError,UnicodeError,OSError):
        raise HistoricalOriginalGap("ORIGINAL_ARCHIVE_UNREADABLE") from None
    if len(selected)!=1:
        raise HistoricalOriginalGap("EXACT_CONSOLIDATED_Q3_KRW_OPERATING_FACT_NOT_UNIQUE")
    return selected[0]


def compare_pair(archive22:bytes,archive23:bytes)->dict:
    a=original_quarter_fact(archive22,2022)
    b=original_quarter_fact(archive23,2023)
    same_qname=a[0]==b[0]
    same_precision=a[1]==b[1]
    same_reporter=a[2]==b[2]
    try:
        finite_delta=(b[3]-a[3]).is_finite()
    except (InvalidOperation,ArithmeticError):
        finite_delta=False
    return {
        "original_first_submission_Q3_archives_examined":2,
        "same_exact_qname":same_qname,
        "same_declared_decimals":same_precision,
        "same_original_filing_reporter_context":same_reporter,
        "arithmetic_possible_in_memory":finite_delta,
        "two_original_q3_numeric_representations_consistent":bool(
            same_qname and same_precision and same_reporter and finite_delta),
        "amounts_delta_and_sign_retained":False,
    }


def run(slot:int,session=None)->dict:
    if type(slot) is not int or slot not in FROZEN_SLOTS:
        return {"source_status":"FAIL_CLOSED_FROZEN_SLOT_INVALID",**SAFETY}
    key=os.getenv("OPENDART_API_KEY","").strip()
    report={
        "purpose":"M20_FROZEN_SIX_ISSUER_ORIGINAL_2022Q3_2023Q3_NUMERIC_SOURCE_ONLY",
        "cohort_slot":slot,
        "source_status":"AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "api_credential_present":bool(key),
        "max_approved_source_requests":MAX_CALLS_PER_SLOT,
        "original_first_submission_Q3_archives_examined":0,
        "two_original_q3_numeric_representations_consistent":False,
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
        company=_registry(registry).get(COHORT[slot])
        if company is None:
            raise HistoricalOriginalGap("FIXED_ISSUER_ABSENT_FROM_REGISTRY")
        originals={}
        for year in YEARS:
            begin,end=_window(year)
            index=_official_get(session,"list.json",{
                "crtfc_key":key,"corp_code":company,
                "bgn_de":begin,"end_de":end,"pblntf_ty":"A","page_count":"100",
            })
            originals[year]=original_first_receipt(index,year)
        a=_official_xbrl_get(session,key,originals[2022])
        b=_official_xbrl_get(session,key,originals[2023])
        report.update(compare_pair(a,b))
        report["source_status"]="ORIGINAL_2022_2023_Q3_NUMERIC_PAIR_SHAPE_ONLY_NOT_PIT"
    except Exception as exc:
        fixed={
            "UNAPPROVED_ORIGINAL_YEAR",
            "INITIAL_FILING_AMBIGUOUS_OR_MISSING",
            "ORIGINAL_XML_SIZE_INVALID","ORIGINAL_XML_UNSAFE",
            "ORIGINAL_CONTEXT_AMBIGUOUS","ORIGINAL_UNIT_AMBIGUOUS",
            "ORIGINAL_NUMERIC_PRECISION_INVALID",
            "ORIGINAL_NUMERIC_TEXT_INVALID","ORIGINAL_ARCHIVE_UNREADABLE",
            "EXACT_CONSOLIDATED_Q3_KRW_OPERATING_FACT_NOT_UNIQUE",
            "FIXED_ISSUER_ABSENT_FROM_REGISTRY",
        }
        reason=str(exc) if type(exc) is HistoricalOriginalGap else ""
        report["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        report["failure_code"]=reason if reason in fixed else "UNCLASSIFIED"
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--cohort-slot",required=True,type=int,choices=FROZEN_SLOTS)
    args=parser.parse_args()
    out=run(args.cohort_slot)
    RESULTS.mkdir(parents=True,exist_ok=True)
    (RESULTS/f"slot_{args.cohort_slot}.json").write_text(
        json.dumps(out,sort_keys=True,indent=2),encoding="utf-8")
    print("OPENDART_M20_2022_2023_ORIGINAL_Q3_PAIR="+json.dumps(
        out,sort_keys=True),flush=True)
