"""Original-filing M20 Q3 year-over-year operating fact *format* gate.

Read-only, official OpenDART, preselected fixed issuer, original 2024/2025
Q3 ZIPs only; **not** a source-level alpha, actual statement table binding,
historical publication-time proof, full issuer panel, PIT availability or an
economically admissible comparable net-EV feature.

Never save/log IDs, raw archives, raw financial amounts, delta/sign, accession
numbers, credentials, ticker rows, or security prices. Values are decoded in
memory ONLY to validate that exact two original KRW numbers support finite
arithmetic. All source, profitability, independent holdout and live flags false.
"""
from __future__ import annotations

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

from research_v1_opendart_lineage_pilot import (
    _official_get, corp_from_official_zip, STOCK_CODE,
)
from research_v1_opendart_m20_vintage_pilot import BEGIN, END
from research_v1_opendart_original_xbrl_pilot import (
    _official_xbrl_get, first_q3_original_receipts, inspect_xbrl_zip,
)
from research_v1_opendart_m20_q3_account_cardinality import (
    CONCEPTS, _value_shape_valid,
)
from research_v1_opendart_m20_original_cfs_axis import (
    XBRLI, _local, _statement_axis_kind, inspect_explicit_cfs_axis,
)

MAX_SINGLE_XML = 48*1024*1024
OUTPUT = Path("research_results/opendart_m20_original_quarter_number_compat/summary.json")
DECIMALS = re.compile(r"(?:INF|-?(?:0|[1-9][0-9]{0,2}))\Z")
AUTHORITY = {
    "original_income_statement_table_binding_verified": False,
    "original_period_taxonomy_version_compatibility_verified": False,
    "original_report_restated_earnings_lineage_verified": False,
    "historical_entity_security_mapping_verified": False,
    "historical_publication_instant_verified": False,
    "historical_publication_pit_verified": False,
    "all_issuers_full_history_covered": False,
    "m20_signal_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "live_orders_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "ordering": "DISABLED",
    "source_values_or_identifiers_saved": False,
}


class OriginalQ3NumberCompatibilityError(ValueError):
    """Fixed, public-safe categories only; no source values in exceptions."""


def _numeric_pair_atom(xmlzip: bytes, year: int):
    """Return one transient private (QName, decimals, entity, Decimal) atom.

    The atom is never returned to the public diagnostic. An XBRL fact in a
    filing might originate from income statement or note, so identical QNames
    are NOT enough to claim statement-level economic semantics.
    """
    if type(year) is not int or year not in (2024, 2025):
        raise OriginalQ3NumberCompatibilityError("FIXED_ORIGINAL_YEAR_SCOPE")
    shape=inspect_explicit_cfs_axis(xmlzip,year)
    if not shape["exactly_one_ifrs_explicit_consolidated_candidate_shape_only"]:
        raise OriginalQ3NumberCompatibilityError("CONSOLIDATED_CANDIDATE_NOT_UNIQUE")
    expected=(f"{year}-07-01",f"{year}-09-30")
    found=[]
    with zipfile.ZipFile(io.BytesIO(xmlzip)) as archive:
        for info in archive.infolist():
            if info.is_dir() or not info.filename.lower().endswith((".xbrl",".xml")):
                continue
            if info.file_size>MAX_SINGLE_XML:
                raise OriginalQ3NumberCompatibilityError("STRUCTURED_XML_TOO_LARGE")
            try:
                root=fromstring(archive.read(info),forbid_dtd=True,forbid_entities=True,
                                forbid_external=True)
            except (DefusedXmlException,ParseError,ValueError):
                raise OriginalQ3NumberCompatibilityError("UNSAFE_XBRL_DOCUMENT") from None
            contexts={}
            units={}
            for node in root.iter():
                if node.tag==XBRLI+"context":
                    ident=node.attrib.get("id")
                    if type(ident) is not str or not ident or ident in contexts:
                        raise OriginalQ3NumberCompatibilityError("CONTEXT_ID_AMBIGUOUS")
                    starts=[x.text for x in node.iter() if x.tag==XBRLI+"startDate"]
                    ends=[x.text for x in node.iter() if x.tag==XBRLI+"endDate"]
                    numbers=[x for x in node.iter() if x.tag==XBRLI+"identifier"]
                    if len(starts)!=1 or len(ends)!=1 or len(numbers)!=1:
                        continue
                    entity=(numbers[0].attrib.get("scheme"),numbers[0].text)
                    if not all(type(s) is str and s for s in entity):
                        continue
                    contexts[ident]=((starts[0],ends[0]),_statement_axis_kind(node),entity)
                elif node.tag==XBRLI+"unit":
                    ident=node.attrib.get("id")
                    if type(ident) is not str or not ident or ident in units:
                        raise OriginalQ3NumberCompatibilityError("UNIT_ID_AMBIGUOUS")
                    measures=[x.text for x in node.iter() if x.tag==XBRLI+"measure"]
                    division=any(_local(x.tag)=="divide" for x in node.iter())
                    units[ident]=(not division and measures==["iso4217:KRW"])
            for node in root.iter():
                if _local(node.tag) not in CONCEPTS:
                    continue
                ref=node.attrib.get("contextRef")
                if ref not in contexts:
                    continue
                period,kind,entity=contexts[ref]
                if period!=expected or kind!="CONSOLIDATED":
                    continue
                if not units.get(node.attrib.get("unitRef"),False):
                    continue
                if not _value_shape_valid(node):
                    continue
                decimals=node.attrib.get("decimals")
                if type(decimals) is not str or not DECIMALS.fullmatch(decimals):
                    raise OriginalQ3NumberCompatibilityError("NUMERIC_ACCURACY_UNDECLARED")
                try:
                    val=Decimal(node.text.strip())
                except (InvalidOperation,TypeError,ValueError):
                    raise OriginalQ3NumberCompatibilityError("ORIGINAL_NUMERIC_SHAPE_INVALID") from None
                if not val.is_finite():
                    raise OriginalQ3NumberCompatibilityError("ORIGINAL_NUMERIC_SHAPE_INVALID")
                found.append((node.tag,decimals,entity,val))
    if len(found)!=1:
        raise OriginalQ3NumberCompatibilityError("CONSOLIDATED_VALUE_NOT_UNIQUE")
    return found[0]


def check_two_original_q3_numbers(
    *, original24: bytes, original25: bytes,
) -> dict:
    """Compare numeric *representations* only; never emit values or sign."""
    a=_numeric_pair_atom(original24,2024)
    b=_numeric_pair_atom(original25,2025)
    same_qname=a[0]==b[0]
    same_decimals=a[1]==b[1]
    same_entity=a[2]==b[2]
    try:
        delta=b[3]-a[3]
        can_subtract=delta.is_finite()
    except (ArithmeticError,InvalidOperation):
        can_subtract=False
    return {
        "original_q3_pair_count":2,
        "original_q3_exclusive_krw_consolidated_numeric_candidate_shape":True,
        "same_exact_taxonomy_qname_across_years":same_qname,
        "same_declared_decimals_precision":same_decimals,
        "same_xbrl_context_entity_identifier":same_entity,
        "finite_in_memory_numeric_difference_possible":can_subtract,
        "minimal_original_pair_representation_consistent":bool(
            same_qname and same_decimals and same_entity and can_subtract),
        "numeric_amounts_or_delta_or_sign_saved":False,
        **AUTHORITY,
    }


def run(session=None) -> dict:
    key=os.getenv("OPENDART_API_KEY","").strip()
    out={
        "purpose":"FIXED_ISSUER_ORIGINAL_Q3_KRW_CONSOLIDATED_NUMERIC_REPRESENTATION_ONLY",
        "source":"OFFICIAL_OPENDART",
        "pilot_stock":STOCK_CODE,
        "source_status":"AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "credential_present":bool(key),
        "original_q3_reports_examined":0,
        "minimal_original_pair_representation_consistent":False,
        "original_numeric_amounts_or_delta_or_sign_saved":False,
        **AUTHORITY,
    }
    if not key:
        return out
    if session is None:
        import requests
        session=requests.Session()
    stage="FIXED_CORP_MAPPING"
    try:
        corp=corp_from_official_zip(_official_get(
            session,"corpCode.xml",{"crtfc_key":key},zip_response=True))
        stage="ORIGINAL_Q3_INDEX"
        filings=_official_get(session,"list.json",{
            "crtfc_key":key,"corp_code":corp,
            "bgn_de":BEGIN,"end_de":END,"pblntf_ty":"A","page_count":"100",
        })
        original=first_q3_original_receipts(filings)
        stage="READ_ONLY_Q_MINUS_4_ORIGINAL"
        raw24=_official_xbrl_get(session,key,original["Q_MINUS_4"])
        stage="READ_ONLY_Q_CURRENT_ORIGINAL"
        raw25=_official_xbrl_get(session,key,original["Q_CURRENT"])
        stage="ORIGINAL_NUMERIC_REPRESENTATION_PAIR"
        comparability=check_two_original_q3_numbers(original24=raw24,original25=raw25)
        out.update(comparability)
        out["original_q3_reports_examined"]=2
        out["source_status"]="ORIGINAL_NUMERIC_REPRESENTATION_SHAPE_ONLY_NOT_PIT"
    except Exception as exc:
        out["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        out["failure_stage"]=stage
        allowed={
            "FIXED_ORIGINAL_YEAR_SCOPE","CONSOLIDATED_CANDIDATE_NOT_UNIQUE",
            "STRUCTURED_XML_TOO_LARGE","UNSAFE_XBRL_DOCUMENT",
            "CONTEXT_ID_AMBIGUOUS","UNIT_ID_AMBIGUOUS",
            "NUMERIC_ACCURACY_UNDECLARED","ORIGINAL_NUMERIC_SHAPE_INVALID",
            "CONSOLIDATED_VALUE_NOT_UNIQUE",
        }
        reason=str(exc) if type(exc) is OriginalQ3NumberCompatibilityError else ""
        out["failure_reason_code"]=reason if reason in allowed else "UNCLASSIFIED"
    return out


if __name__=="__main__":
    result=run()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,sort_keys=True,indent=2),encoding="utf-8")
    print("OPENDART_M20_ORIGINAL_QUARTER_NUMERIC_COMPAT="+json.dumps(result,sort_keys=True),
          flush=True)
