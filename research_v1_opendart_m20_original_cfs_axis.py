"""M20 one-issuer ORIGINAL 2024/2025 Q3 consolidated-axis feasibility.

A *diagnostic* of explicit IFRS consolidated/separate XBRL axis and candidate
cardinality only. This is not a full original consolidated income-statement
validation, a financial amount, PIT admissibility, or an alpha/performance run.
Uses previously approved OpenDART 2-report official read-only route only.

Any ambiguous, missing, non-KRW, malformed, or multi-dimension statement
candidate stays missing. Never save financial amounts, context/receipt/issuer
IDs, original XML, ZIPs or access keys; never emit them to public logs.
"""
from __future__ import annotations

from collections import Counter
import io
import json
import os
from pathlib import Path
import zipfile
from defusedxml.ElementTree import fromstring
from defusedxml.common import DefusedXmlException
from xml.etree.ElementTree import ParseError

from research_v1_opendart_lineage_pilot import _official_get, corp_from_official_zip, STOCK_CODE
from research_v1_opendart_m20_vintage_pilot import BEGIN, END
from research_v1_opendart_original_xbrl_pilot import (
    _official_xbrl_get, first_q3_original_receipts, inspect_xbrl_zip,
)
from research_v1_opendart_m20_q3_account_cardinality import (
    _value_shape_valid, inspect_m20_q3_original_financial_candidates, CONCEPTS,
)

XBRLI = "{http://www.xbrl.org/2003/instance}"
IFRS_AXIS = "ifrs-full:ConsolidatedAndSeparateFinancialStatementsAxis"
CFS = "ifrs-full:ConsolidatedMember"
SFS = "ifrs-full:SeparateMember"
MAX_DOCUMENT = 48 * 1024 * 1024
OUTPUT = Path("research_results/opendart_m20_cfs_axis/summary.json")


class CFSAxisError(ValueError):
    pass


def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _statement_axis_kind(context) -> str:
    """Only one exact explicit IFRS axis/member is a recognized shape.

    Other dimensional combinations stay OTHER, including typed members,
    extra axes, a dimensionless context and custom prefixed members.
    """
    explicit = [e for e in context.iter() if _local(e.tag) == "explicitMember"]
    typed = [e for e in context.iter() if _local(e.tag) == "typedMember"]
    if typed or len(explicit) != 1:
        return "OTHER"
    member = explicit[0]
    if member.attrib.get("dimension") != IFRS_AXIS:
        return "OTHER"
    label = (member.text or "").strip()
    if label == CFS:
        return "CONSOLIDATED"
    if label == SFS:
        return "SEPARATE"
    return "OTHER"


def inspect_explicit_cfs_axis(archive_raw: bytes, fiscal_year: int) -> dict:
    """Counts original quarter facts; no values, names, IDs or receipt numbers."""
    if type(fiscal_year) is not int or fiscal_year not in (2024, 2025):
        raise CFSAxisError("OUTSIDE_FIXED_Q3_SCOPE")
    inspect_xbrl_zip(archive_raw)
    exact = (f"{fiscal_year}-07-01", f"{fiscal_year}-09-30")
    counts = Counter()
    try:
        with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
            for member in archive.infolist():
                if member.is_dir() or not member.filename.lower().endswith((".xml", ".xbrl")):
                    continue
                if member.file_size > MAX_DOCUMENT:
                    raise CFSAxisError("XML_OVERSIZE")
                raw = archive.read(member)
                if len(raw) != member.file_size:
                    raise CFSAxisError("XML_LENGTH_INVALID")
                try:
                    root = fromstring(raw, forbid_dtd=True, forbid_entities=True, forbid_external=True)
                except (DefusedXmlException, ParseError, ValueError):
                    raise CFSAxisError("XML_UNSAFE_OR_INVALID") from None
                counts["xml_documents_checked"] += 1
                contexts = {}
                units = {}
                for node in root.iter():
                    if node.tag == XBRLI + "context":
                        key = node.attrib.get("id")
                        if not key or key in contexts:
                            raise CFSAxisError("CONTEXT_ID_INVALID")
                        starts = [e.text for e in node.iter() if e.tag == XBRLI + "startDate"]
                        ends = [e.text for e in node.iter() if e.tag == XBRLI + "endDate"]
                        period = (starts[0] or "", ends[0] or "") if len(starts)==1 and len(ends)==1 else ("","")
                        contexts[key] = (period, _statement_axis_kind(node))
                    elif node.tag == XBRLI + "unit":
                        key = node.attrib.get("id")
                        if not key or key in units:
                            raise CFSAxisError("UNIT_ID_INVALID")
                        measures = [e.text for e in node.iter() if e.tag == XBRLI + "measure"]
                        divide = any(_local(e.tag) == "divide" for e in node.iter())
                        units[key] = (not divide and len(measures) == 1
                                      and measures[0] == "iso4217:KRW")
                for node in root.iter():
                    if _local(node.tag) not in CONCEPTS:
                        continue
                    reference = node.attrib.get("contextRef")
                    if reference not in contexts:
                        counts["unresolved_fact_context"] += 1
                        continue
                    period, kind = contexts[reference]
                    if period != exact:
                        continue
                    counts["original_q3_operating_facts"] += 1
                    if kind == "CONSOLIDATED":
                        counts["exact_axis_consolidated_facts"] += 1
                        if units.get(node.attrib.get("unitRef"), False) and _value_shape_valid(node):
                            counts["exact_axis_consolidated_krw_numeric_candidates"] += 1
                        else:
                            counts["consolidated_currency_or_numeric_invalid"] += 1
                    elif kind == "SEPARATE":
                        counts["exact_axis_separate_facts"] += 1
                        if units.get(node.attrib.get("unitRef"), False) and _value_shape_valid(node):
                            counts["exact_axis_separate_krw_numeric_candidates"] += 1
                    else:
                        counts["unknown_axis_or_extra_dimension_facts"] += 1
    except (zipfile.BadZipFile, UnicodeError, OSError, EOFError):
        raise CFSAxisError("XBRL_RETRIEVAL_INTEGRITY_FAILURE") from None
    if not counts["xml_documents_checked"]:
        raise CFSAxisError("NO_XBRL_DOCUMENTS")

    parent = inspect_m20_q3_original_financial_candidates(archive_raw, fiscal_year)
    if (counts["original_q3_operating_facts"] != parent["exact_q3_operating_facts"]
            or counts["xml_documents_checked"] != parent["xml_documents_scanned"]):
        raise CFSAxisError("SOURCE_COUNT_ATTESTATION_MISMATCH")
    out_keys = (
        "xml_documents_checked", "original_q3_operating_facts",
        "exact_axis_consolidated_facts", "exact_axis_separate_facts",
        "unknown_axis_or_extra_dimension_facts",
        "exact_axis_consolidated_krw_numeric_candidates",
        "exact_axis_separate_krw_numeric_candidates",
        "consolidated_currency_or_numeric_invalid", "unresolved_fact_context",
    )
    return {
        "fiscal_year": fiscal_year,
        **{key:int(counts[key]) for key in out_keys},
        "exactly_one_ifrs_explicit_consolidated_candidate_shape_only": (
            counts["exact_axis_consolidated_krw_numeric_candidates"] == 1
        ),
        "historical_consolidated_income_statement_table_bound": False,
        "same_filing_duplicate_equivalence_verified": False,
        "quarter_and_q_minus_4_comparability_verified": False,
        "original_publication_pit_verified": False,
        "numeric_values_or_identifiers_saved": False,
    }


def run(session=None):
    key = os.getenv("OPENDART_API_KEY","").strip()
    report = {
        "purpose":"ORIGINAL_IFRS_CONSOLIDATED_VS_SEPARATE_Q3_AXIS_SHAPE_ONLY",
        "official_source":"OpenDART",
        "pilot_stock":STOCK_CODE,
        "source_status":"AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "credential_present": bool(key),
        "original_reports_checked":0,
        "original_two_report_ifrs_consolidated_axis_cardinality_verified":False,
        "historical_statement_table_pit_verified":False,
        "quarter_and_q_minus_4_values_comparable_verified":False,
        "full_universe_historical_source_admitted":False,
        "historical_pit_source_admitted":False,
        "performance_run_authorized":False,
        "independent_holdout_authorized":False,
        "champion_change_authorized":False,
        "live_order_authorized":False,
        "real_orders_authorized":False,
        "funds_movement_authorized":False,
        "permission_change_authorized":False,
        "ordering":"DISABLED",
        "numerical_values_or_identifiers_saved":False,
    }
    if not key:
        return report
    if session is None:
        import requests
        session = requests.Session()
    stage = "ISSUER_MAPPING"
    try:
        corp = corp_from_official_zip(_official_get(
            session,"corpCode.xml",{"crtfc_key":key},zip_response=True))
        stage="FIRST_FILING_IDENTITIES"
        filings = _official_get(session,"list.json",{
            "crtfc_key":key,"corp_code":corp,
            "bgn_de":BEGIN,"end_de":END,"pblntf_ty":"A","page_count":"100"
        })
        originals = first_q3_original_receipts(filings)
        for name,year in (("Q_MINUS_4",2024),("Q_CURRENT",2025)):
            stage="EXACT_FIRST_XBRL_"+name
            data = _official_xbrl_get(session,key,originals[name])
            counts = inspect_explicit_cfs_axis(data,year)
            report[name.lower()+"_axis_counts"] = counts
            report["original_reports_checked"] += 1
        report["original_two_report_ifrs_consolidated_axis_cardinality_verified"] = all(
            report[x+"_axis_counts"]["exactly_one_ifrs_explicit_consolidated_candidate_shape_only"]
            for x in ("q_minus_4","q_current")
        )
        report["source_status"]="CONSOLIDATED_AXIS_METADATA_ONLY_NOT_PIT_ADMITTED"
    except Exception as e:
        report["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        report["failure_stage"]=stage
        allowed={"OUTSIDE_FIXED_Q3_SCOPE","XML_OVERSIZE","XML_LENGTH_INVALID",
                 "XML_UNSAFE_OR_INVALID","CONTEXT_ID_INVALID","UNIT_ID_INVALID",
                 "XBRL_RETRIEVAL_INTEGRITY_FAILURE","NO_XBRL_DOCUMENTS",
                 "SOURCE_COUNT_ATTESTATION_MISMATCH"}
        code = str(e) if type(e) is CFSAxisError else ""
        report["failure_reason_code"]=code if code in allowed else "UNCLASSIFIED"
    return report


if __name__=="__main__":
    data=run()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(data,sort_keys=True),encoding="utf-8")
    print("OPENDART_M20_CFS_AXIS="+json.dumps(data,sort_keys=True),flush=True)
