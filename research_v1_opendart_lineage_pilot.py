"""Read-only OpenDART M20 *source-shape* pilot; never admits PIT or returns.

Fixed one-company, one-report test chosen before looking at returns.
Only official OpenDART APIs are contacted. No KRX collection.
No raw filings, amounts, identifiers or credentials are persisted.
"""
from __future__ import annotations

import io
import json
import os
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

BASE = "https://opendart.fss.or.kr/api/"
STOCK_CODE = "005930"  # fixed representative issuer, not alpha selection
BUSINESS_YEAR = "2025"
REPORT_CODE = "11014"  # Q3
ACCOUNT_ID = "ifrs-full_ProfitLossFromOperatingActivities"
MAX_RESPONSE_BYTES = 32_000_000
MAX_XML_BYTES = 35_000_000
OUTPUT = Path("research_results/opendart_lineage_pilot/summary.json")


def corp_from_official_zip(raw: bytes) -> str:
    if not raw or len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("invalid ZIP payload size")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        candidates = [f for f in archive.infolist()
                      if f.filename.upper() == "CORPCODE.XML" and not f.is_dir()]
        if len(candidates) != 1 or candidates[0].file_size > MAX_XML_BYTES:
            raise ValueError("invalid official XML entry")
        with archive.open(candidates[0]) as src:
            xml_bytes = src.read(MAX_XML_BYTES + 1)
    if len(xml_bytes) > MAX_XML_BYTES:
        raise ValueError("oversize official XML")
    root = ET.fromstring(xml_bytes)
    matches = []
    for row in root.findall(".//list"):
        if (row.findtext("stock_code") or "").strip() == STOCK_CODE:
            code = (row.findtext("corp_code") or "").strip()
            if not re.fullmatch(r"[0-9]{8}", code):
                raise ValueError("invalid corporate identifier")
            matches.append(code)
    if len(matches) != 1:
        raise ValueError("missing or ambiguous current stock mapping")
    return matches[0]


def filing_receipts(payload: dict) -> set[str]:
    if not isinstance(payload, dict) or payload.get("status") != "000":
        raise ValueError("official filing endpoint not admitted")
    if not isinstance(payload.get("list"), list):
        raise ValueError("missing filing list")
    try:
        page_count = int(payload.get("total_page", 0))
    except (TypeError, ValueError):
        raise ValueError("ambiguous filing pagination") from None
    if page_count != 1:
        raise ValueError("filing pagination not exhaustively handled")
    matched = set()
    for row in payload["list"]:
        if not isinstance(row, dict):
            raise ValueError("invalid filing row")
        title = row.get("report_nm")
        receipt = row.get("rcept_no")
        if isinstance(title, str) and "분기보고서" in title and "2025.09" in title:
            if not isinstance(receipt, str) or not re.fullmatch(r"[0-9]{14}", receipt):
                raise ValueError("invalid filing identifier")
            matched.add(receipt)
    if not matched:
        raise ValueError("missing historical period filing")
    return matched


def financial_shape(payload: dict, corp_code: str, receipts: set[str]) -> dict:
    if not isinstance(payload, dict) or payload.get("status") != "000":
        raise ValueError("official financial endpoint not admitted")
    rows = payload.get("list")
    if not isinstance(rows, list):
        raise ValueError("missing financial statement lines")
    standard_lines = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid financial line")
        if (row.get("corp_code") == corp_code
                and row.get("bsns_year") == BUSINESS_YEAR
                and row.get("reprt_code") == REPORT_CODE
                and row.get("sj_div") in {"IS", "CIS"}
                and row.get("account_id") == ACCOUNT_ID):
            receipt = row.get("rcept_no")
            current = row.get("thstrm_amount")
            prior = row.get("frmtrm_q_amount")
            if not isinstance(receipt, str) or not re.fullmatch(r"[0-9]{14}", receipt):
                raise ValueError("bad statement receipt")
            if receipt not in receipts:
                raise ValueError("statement not linked to enumerated filing")
            if not all(isinstance(v, str) and re.fullmatch(r"-?[0-9][0-9,]*", v)
                       for v in (current, prior)):
                raise ValueError("standalone-quarter prior-year line absent")
            standard_lines.append(row)
    if len(standard_lines) != 1:
        raise ValueError("ambiguous standardized operating-profit line")
    return {
        "official_filing_receipt_linked": True,
        "standardized_operating_profit_quarter_shape_found": True,
        "operating_profit_line_count": len(standard_lines),
    }


def _official_get(session: requests.Session, endpoint: str, params: dict,
                  *, zip_response: bool = False):
    response = session.get(BASE + endpoint, params=params, timeout=20,
                           allow_redirects=False)
    if response.status_code != 200 or len(response.content) > MAX_RESPONSE_BYTES:
        raise ValueError("official API HTTP or payload failure")
    if zip_response:
        return response.content
    parsed = response.json()
    if not isinstance(parsed, dict):
        raise ValueError("official JSON not an object")
    return parsed


def run(session: requests.Session | None = None) -> dict:
    key = os.environ.get("OPENDART_API_KEY", "").strip()
    report = {
        "purpose": "FIXED_ISSUER_SOURCE_FEASIBILITY_ONLY",
        "pilot_stock": STOCK_CODE,
        "pilot_business_year": BUSINESS_YEAR,
        "pilot_report_code": REPORT_CODE,
        "official_source": "OpenDART",
        "source_status": "AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "credential_configured": bool(key),
        "current_mapping_only_not_historical_pit": True,
        "historical_filing_version_pit_verified": False,
        "exact_publication_time_verified": False,
        "quarterly_amounts_saved": False,
        "raw_documents_saved": False,
        "krx_status_verified": False,
        "pit_source_admitted": False,
        "performance_run_authorized": False,
        "holdout_authorized": False,
        "champion_change_allowed": False,
        "live_order_authorized": False,
        "ordering": "DISABLED",
    }
    if not key:
        return report
    if session is None:
        session = requests.Session()
    stage = "CORPORATE_MAPPING"
    try:
        corp_code = corp_from_official_zip(_official_get(
            session, "corpCode.xml", {"crtfc_key": key}, zip_response=True))
        stage = "FILING_RECEIPT"
        receipts = filing_receipts(_official_get(
            session, "list.json", {
                "crtfc_key": key, "corp_code": corp_code,
                "bgn_de": "20251001", "end_de": "20260131",
                "pblntf_ty": "A", "page_count": "100",
            }))
        stage = "FINANCIAL_LINE"
        shape = financial_shape(_official_get(
            session, "fnlttSinglAcntAll.json", {
                "crtfc_key": key, "corp_code": corp_code,
                "bsns_year": BUSINESS_YEAR, "reprt_code": REPORT_CODE,
                "fs_div": "CFS",
            }), corp_code, receipts)
        report.update(shape)
        report["source_status"] = "PILOT_SOURCE_SHAPE_PRESENT_NOT_PIT_ADMITTED"
    except Exception as exc:
        # Never log exception messages: HTTP exceptions may contain credential URLs.
        report["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        report["error_type"] = type(exc).__name__
        report["failure_stage"] = stage
        safe_codes = {
            "invalid ZIP payload size", "invalid official XML entry",
            "oversize official XML", "invalid corporate identifier",
            "missing or ambiguous current stock mapping",
            "official filing endpoint not admitted", "missing filing list",
            "ambiguous filing pagination", "filing pagination not exhaustively handled",
            "invalid filing row", "invalid filing identifier",
            "missing historical period filing",
            "official financial endpoint not admitted",
            "missing financial statement lines", "invalid financial line",
            "bad statement receipt", "statement not linked to enumerated filing",
            "standalone-quarter prior-year line absent",
            "ambiguous standardized operating-profit line",
            "official API HTTP or payload failure", "official JSON not an object",
        }
        code = str(exc) if type(exc) is ValueError else ""
        report["failure_reason_code"] = code if code in safe_codes else "UNCLASSIFIED"
    return report


if __name__ == "__main__":
    result = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OPENDART_LINEAGE_PILOT=" + json.dumps(result, ensure_ascii=False), flush=True)
