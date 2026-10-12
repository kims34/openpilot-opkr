"""Fixed-issuer, original-filing M20 Q3 financial fact *candidate cardinality*.

This is a network-bounded diagnostic, NOT a backtest or PIT/quarter
comparability/statement CFS admission. Searches first-filed official 2024 and
2025 Q3 XBRL archives for a possible 3-month operating-profit fact whose
context has no explicit dimensions and whose unit is KRW.

Never writes or logs a value, context ID, company ID, filing receipt, unit ID,
source filename, raw ZIP/XML or credential. If multiple candidates exist,
none is selected, averaged or preferred. This module does not infer CFS from
an unsegmented context. No KRX web/API, broker, order, model or holdout.
"""
from __future__ import annotations

from collections import Counter
import io
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping
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

XBRLI = "{http://www.xbrl.org/2003/instance}"
CONCEPTS = {"OperatingIncomeLoss", "ProfitLossFromOperatingActivities"}
NUMBER = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?\Z")
MAX_XML_BYTES = 48 * 1024 * 1024
OUTPUT = Path("research_results/opendart_m20_q3_candidate_cardinality/summary.json")


class CandidateCardinalityError(ValueError):
    pass


def _local(tag: Any) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _value_shape_valid(element: Any) -> bool:
    # Validate text format only; never return, hash, save or print the value.
    nil = element.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}nil")
    txt = element.text
    return (nil not in ("true", "1")
            and type(txt) is str
            and NUMBER.fullmatch(txt.strip()) is not None
            and len(txt) <= 512)


def inspect_m20_q3_original_financial_candidates(archive_raw: bytes, fiscal_year: int) -> dict:
    """Aggregate canonical Q3 period/unit/dimension/candidate counts only."""
    if type(fiscal_year) is not int or fiscal_year not in (2024, 2025):
        raise CandidateCardinalityError("OUTSIDE_FIXED_Q3_SCOPE")
    # Verifies bounded ZIP entry count/sizes/CRC/path traversal first.
    inspect_xbrl_zip(archive_raw)
    exact = (f"{fiscal_year}-07-01", f"{fiscal_year}-09-30")
    sums = Counter()
    try:
        with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
            for info in archive.infolist():
                if info.is_dir() or not info.filename.lower().endswith((".xbrl", ".xml")):
                    continue
                if info.file_size > MAX_XML_BYTES:
                    raise CandidateCardinalityError("XML_DOCUMENT_TOO_LARGE")
                raw = archive.read(info)
                if len(raw) != info.file_size:
                    raise CandidateCardinalityError("XML_DOCUMENT_SIZE_DRIFT")
                try:
                    root = fromstring(raw, forbid_dtd=True,
                                      forbid_entities=True, forbid_external=True)
                except (DefusedXmlException, ParseError, ValueError):
                    raise CandidateCardinalityError("UNSAFE_OR_INVALID_XBRL") from None
                sums["xml_documents_scanned"] += 1
                contexts: dict[str, tuple[str, bool]] = {}
                units: dict[str, bool] = {}
                for e in root.iter():
                    if e.tag == XBRLI + "context":
                        context_id = e.attrib.get("id")
                        if not context_id or context_id in contexts:
                            raise CandidateCardinalityError("CONTEXT_ID_INVALID")
                        dates_start = [z.text for z in e.iter() if z.tag == XBRLI + "startDate"]
                        dates_end = [z.text for z in e.iter() if z.tag == XBRLI + "endDate"]
                        if len(dates_start) == 1 and len(dates_end) == 1:
                            period = (dates_start[0] or "", dates_end[0] or "")
                        else:
                            period = ("", "")
                        dimensioned = any(
                            _local(z.tag) in ("segment", "scenario", "explicitMember", "typedMember")
                            for z in e.iter()
                        )
                        contexts[context_id] = (
                            "Q3" if period == exact else "OTHER", dimensioned
                        )
                        if period == exact:
                            sums["exact_q3_contexts"] += 1
                            if not dimensioned:
                                sums["dimensionless_q3_contexts"] += 1
                    elif e.tag == XBRLI + "unit":
                        unit_id = e.attrib.get("id")
                        if not unit_id or unit_id in units:
                            raise CandidateCardinalityError("UNIT_ID_INVALID")
                        measures = [z.text for z in e.iter() if z.tag == XBRLI + "measure"]
                        divides = any(_local(z.tag) == "divide" for z in e.iter())
                        units[unit_id] = bool(
                            not divides and len(measures) == 1
                            and type(measures[0]) is str
                            and measures[0].strip() in {
                                "iso4217:KRW",
                                "{http://www.xbrl.org/2003/iso4217}KRW",
                            }
                        )
                for e in root.iter():
                    if _local(e.tag) not in CONCEPTS:
                        continue
                    sums["total_operating_concept_facts"] += 1
                    ref = e.attrib.get("contextRef")
                    unit = e.attrib.get("unitRef")
                    if ref not in contexts:
                        sums["unresolved_fact_contexts"] += 1
                        continue
                    period, dimensioned = contexts[ref]
                    if period != "Q3":
                        continue
                    sums["exact_q3_operating_facts"] += 1
                    if dimensioned:
                        sums["dimensioned_q3_operating_facts"] += 1
                        continue
                    sums["dimensionless_q3_operating_facts"] += 1
                    if unit not in units or not units[unit]:
                        sums["non_krw_or_missing_unit_q3_facts"] += 1
                        continue
                    sums["dimensionless_q3_operating_krw_facts"] += 1
                    if not _value_shape_valid(e):
                        sums["invalid_numeric_shape_q3_facts"] += 1
                        continue
                    sums["dimensionless_q3_krw_numeric_candidate_facts"] += 1
    except (zipfile.BadZipFile, UnicodeError, EOFError, OSError):
        raise CandidateCardinalityError("ZIP_OR_XML_READ_INVALID") from None
    if sums["xml_documents_scanned"] == 0:
        raise CandidateCardinalityError("NO_XML_DOCUMENTS")
    # Only numeric format and unit were checked. Whether a fact is *CFS*,
    # whether repeated contexts are equivalent and whether the original
    # report was known at the decision time are NOT verified.
    counts = [
        "xml_documents_scanned", "total_operating_concept_facts",
        "exact_q3_contexts", "dimensionless_q3_contexts",
        "exact_q3_operating_facts", "dimensioned_q3_operating_facts",
        "dimensionless_q3_operating_facts",
        "non_krw_or_missing_unit_q3_facts",
        "dimensionless_q3_operating_krw_facts",
        "invalid_numeric_shape_q3_facts",
        "dimensionless_q3_krw_numeric_candidate_facts",
        "unresolved_fact_contexts",
    ]
    num_candidates = sums["dimensionless_q3_krw_numeric_candidate_facts"]
    return {
        "fiscal_year": fiscal_year,
        **{field: int(sums[field]) for field in counts},
        "strict_single_candidate_shape_only": num_candidates == 1,
        "historical_consolidated_statement_verified": False,
        "quarter_and_q_minus_4_comparability_verified": False,
        "historical_publication_time_verified": False,
        "historic_pit_source_admitted": False,
        "numeric_amounts_or_ids_saved": False,
    }


def run(session=None) -> dict:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    report = {
        "purpose": "FIXED_ISSUER_Q3_ORIGINAL_ACCOUNT_CARDINALITY_ONLY",
        "official_source": "OpenDART",
        "pilot_stock": STOCK_CODE,
        "source_status": "AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "credentials_present": bool(key),
        "original_reports_inspected": 0,
        "two_years_unique_candidate_shapes_only": False,
        "historic_consolidated_statement_verified": False,
        "historical_publication_time_verified": False,
        "historical_pit_source_admitted": False,
        "performance_run_authorized": False,
        "sealed_holdout_authorized": False,
        "champion_change_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permission_change_authorized": False,
        "ordering": "DISABLED",
        "original_numeric_amounts_or_ids_saved": False,
    }
    if not key:
        return report
    if session is None:
        import requests
        session = requests.Session()
    stage = "CORPORATE_MAPPING"
    try:
        corp = corp_from_official_zip(_official_get(
            session, "corpCode.xml", {"crtfc_key": key}, zip_response=True))
        stage = "ORIGINAL_RECEIPTS"
        p = _official_get(session, "list.json", {
            "crtfc_key": key, "corp_code": corp,
            "bgn_de": BEGIN, "end_de": END, "pblntf_ty": "A", "page_count": "100",
        })
        originals = first_q3_original_receipts(p)
        for source_key, year in (("Q_MINUS_4", 2024), ("Q_CURRENT", 2025)):
            stage = "OFFICIAL_XBRL_" + source_key
            raw = _official_xbrl_get(session, key, originals[source_key])
            shape = inspect_m20_q3_original_financial_candidates(raw, year)
            report[source_key.lower() + "_cardinality"] = shape
            report["original_reports_inspected"] += 1
        report["two_years_unique_candidate_shapes_only"] = all(
            report[x + "_cardinality"]["strict_single_candidate_shape_only"]
            for x in ("q_minus_4", "q_current")
        )
        report["source_status"] = "ORIGINAL_CANDIDATE_CARDINALITY_ONLY_NOT_PIT"
    except Exception as exc:
        report["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        report["failure_stage"] = stage
        allowed = {
            "OUTSIDE_FIXED_Q3_SCOPE", "XML_DOCUMENT_TOO_LARGE",
            "XML_DOCUMENT_SIZE_DRIFT", "UNSAFE_OR_INVALID_XBRL",
            "CONTEXT_ID_INVALID", "UNIT_ID_INVALID",
            "ZIP_OR_XML_READ_INVALID", "NO_XML_DOCUMENTS",
        }
        reason = str(exc) if type(exc) is CandidateCardinalityError else ""
        report["failure_reason_code"] = reason if reason in allowed else "UNCLASSIFIED"
    return report


if __name__ == "__main__":
    result = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
    print("OPENDART_M20_CARDINALITY=" + json.dumps(result, sort_keys=True))
