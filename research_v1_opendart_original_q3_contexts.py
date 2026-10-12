"""No-amount original OpenDART XBRL operating-profit Q3 context probe.

Runs only for one preregistered pilot issuer and Q3 2024/2025 first
submissions. Counts tag/context occurrences, never extracts or logs financial
amounts, raw receipts, issuer IDs, credentials or raw XML. Presence of a tag
does not prove consolidated standalone amounts, quarterly comparability,
historical publication/PIT admission, Net EV or trading authority.
"""
from __future__ import annotations

from datetime import date
import io
import json
import os
from pathlib import Path
from typing import Any
import zipfile

from defusedxml.ElementTree import fromstring
from defusedxml.common import DefusedXmlException
from xml.etree.ElementTree import ParseError

from research_v1_opendart_lineage_pilot import BASE, STOCK_CODE, _official_get, corp_from_official_zip
from research_v1_opendart_m20_vintage_pilot import BEGIN, END
from research_v1_opendart_original_xbrl_pilot import (
    _official_xbrl_get, first_q3_original_receipts, inspect_xbrl_zip,
)

OUTPUT = Path("research_results/opendart_m20_original_xbrl_context/summary.json")
CONCEPTS = frozenset({"OperatingIncomeLoss", "ProfitLossFromOperatingActivities"})
MAX_XML_DOCUMENT = 48 * 1024 * 1024


class QuarterContextError(ValueError):
    pass


def _local(tag: Any) -> str:
    return str(tag).rsplit("}", 1)[-1]


def inspect_original_operating_contexts(archive_raw: bytes, fiscal_year: int) -> dict[str, Any]:
    """Report only XBRL concept and period counts, never values or identifiers."""
    inspect_xbrl_zip(archive_raw)  # required ZIP CRC/bounds/path-validation first
    if type(fiscal_year) is not int or fiscal_year not in (2024, 2025):
        raise QuarterContextError("OUTSIDE_FIXED_Q3_SCOPE")
    exact_period = (f"{fiscal_year}-07-01", f"{fiscal_year}-09-30")
    ytd_period = (f"{fiscal_year}-01-01", f"{fiscal_year}-09-30")
    fact_count = exact_fact_count = ytd_fact_count = 0
    q_context_count = ytd_context_count = 0
    files_scanned = 0
    try:
        with zipfile.ZipFile(io.BytesIO(archive_raw)) as archive:
            for item in archive.infolist():
                if item.is_dir() or not item.filename.lower().endswith((".xbrl", ".xml")):
                    continue
                if item.file_size > MAX_XML_DOCUMENT:
                    raise QuarterContextError("XBRL_XML_TOO_LARGE")
                data = archive.read(item)
                if len(data) != item.file_size:
                    raise QuarterContextError("XBRL_XML_SIZE_DRIFT")
                try:
                    # DTD, entities, and external references disabled by parser.
                    root = fromstring(data, forbid_dtd=True, forbid_entities=True, forbid_external=True)
                except (DefusedXmlException, ParseError, ValueError):
                    raise QuarterContextError("XBRL_XML_UNSAFE_OR_INVALID") from None
                files_scanned += 1
                contexts: dict[str, tuple[str, str]] = {}
                for element in root.iter():
                    if _local(element.tag) != "context":
                        continue
                    cid = element.attrib.get("id")
                    if not cid or cid in contexts:
                        raise QuarterContextError("XBRL_CONTEXT_ID_INVALID")
                    starts = [e.text for e in element.iter() if _local(e.tag) == "startDate"]
                    ends = [e.text for e in element.iter() if _local(e.tag) == "endDate"]
                    if len(starts) == 1 and len(ends) == 1:
                        contexts[cid] = (starts[0] or "", ends[0] or "")
                q_context_count += sum(x == exact_period for x in contexts.values())
                ytd_context_count += sum(x == ytd_period for x in contexts.values())
                for element in root.iter():
                    if _local(element.tag) not in CONCEPTS:
                        continue
                    ref = element.attrib.get("contextRef")
                    if not ref:
                        continue
                    fact_count += 1
                    period = contexts.get(ref)
                    if period == exact_period:
                        exact_fact_count += 1
                    if period == ytd_period:
                        ytd_fact_count += 1
    except (zipfile.BadZipFile, UnicodeError, OSError, EOFError):
        raise QuarterContextError("XBRL_ZIP_OR_XML_READ_INVALID") from None

    if files_scanned < 1:
        raise QuarterContextError("STRUCTURED_XML_DOCUMENTS_ABSENT")
    # Numeric values are NOT read or interpreted; no account-semantic admission.
    return {
        "fiscal_year": fiscal_year,
        "xml_files_parsed": files_scanned,
        "operating_profit_tagged_fact_count": fact_count,
        "exact_jul_to_sep_context_count": q_context_count,
        "exact_jul_to_sep_tagged_fact_count": exact_fact_count,
        "jan_to_sep_context_count": ytd_context_count,
        "jan_to_sep_tagged_fact_count": ytd_fact_count,
        "standalone_quarter_operating_profit_semantics_verified": False,
        "operating_amounts_or_context_ids_saved": False,
        "historical_xbrl_pit_verified": False,
    }


def run(session=None):
    key = os.getenv("OPENDART_API_KEY", "").strip()
    report = {
        "purpose": "M20_FIXED_Q3_ORIGINAL_OPERATING_PROFIT_CONTEXT_COUNTS_ONLY",
        "source_status": "AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "official_source": "OpenDART",
        "pilot_stock": STOCK_CODE,
        "credentials_present": bool(key),
        "original_xbrl_q3_archive_received": 0,
        "original_filing_receipt_chronology_verified": False,
        "original_report_intraday_publication_time_verified": False,
        "standalone_quarter_operating_profit_semantics_verified": False,
        "historical_quarter_amounts_and_comparability_verified": False,
        "original_financial_amounts_saved": False,
        "historical_pit_source_admitted": False,
        "feature_performance_testing_authorized": False,
        "independent_holdout_authorized": False,
        "champion_change_authorized": False,
        "live_order_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permission_change_authorized": False,
        "ordering": "DISABLED",
    }
    if not key:
        return report
    if session is None:
        import requests
        session = requests.Session()
    stage = "FIXED_CORPORATION_MAPPING"
    try:
        corporation = corp_from_official_zip(_official_get(
            session, "corpCode.xml", {"crtfc_key": key}, zip_response=True))
        stage = "FIXED_FILING_INDEX"
        list_data = _official_get(session, "list.json", {
            "crtfc_key": key, "corp_code": corporation, "bgn_de": BEGIN,
            "end_de": END, "pblntf_ty": "A", "page_count": "100",
        })
        selected = first_q3_original_receipts(list_data)
        report["original_filing_receipt_chronology_verified"] = True
        for name, fiscal_year in (("Q_MINUS_4", 2024), ("Q_CURRENT", 2025)):
            stage = "ORIGINAL_XBRL_" + name
            data = _official_xbrl_get(session, key, selected[name])
            shape = inspect_original_operating_contexts(data, fiscal_year)
            report[name.lower() + "_context_counts"] = shape
            report["original_xbrl_q3_archive_received"] += 1
        report["source_status"] = "XBRL_ORIGINAL_Q3_CONTEXT_COUNTS_OBSERVED_NOT_PIT_ADMITTED"
    except Exception as exc:
        report["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        report["failure_stage"] = stage
        allowed = {
            "OUTSIDE_FIXED_Q3_SCOPE", "XBRL_XML_TOO_LARGE",
            "XBRL_XML_SIZE_DRIFT", "XBRL_XML_UNSAFE_OR_INVALID",
            "XBRL_CONTEXT_ID_INVALID", "XBRL_ZIP_OR_XML_READ_INVALID",
            "STRUCTURED_XML_DOCUMENTS_ABSENT",
        }
        reason = str(exc) if type(exc) is QuarterContextError else ""
        report["failure_reason_code"] = reason if reason in allowed else "UNCLASSIFIED"
    return report


if __name__ == "__main__":
    result = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OPENDART_M20_CONTEXTS=" + json.dumps(result, ensure_ascii=False), flush=True)
