"""Read-only original-filing XBRL source-shape probe for pre-registered M20.

Only official OpenDART APIs, fixed issuer and fixed 2024/2025 Q3 reports.
Archive bytes are read transiently, hashed, then discarded. No raw source,
filing IDs, company IDs, financial figures or credentials are saved/logged.

Archive possession is NOT historical PIT admission. No KRX, broker, orders,
holdout, performance evaluation, model-fitting or frozen policy changes.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
from typing import Any, Mapping
import zipfile

import requests

from research_v1_opendart_lineage_pilot import BASE, STOCK_CODE, corp_from_official_zip, _official_get
from research_v1_opendart_m20_vintage_pilot import (
    BEGIN, END, TARGETS, validate_complete_q3_filing_index,
)

REPORT_CODE = "11014"
MAX_ZIP_BYTES = 32 * 1024 * 1024
MAX_FILES = 250
MAX_EXPANDED_BYTES = 120 * 1024 * 1024
MAX_SINGLE_FILE_BYTES = 80 * 1024 * 1024
OUTPUT = Path("research_results/opendart_m20_original_xbrl/summary.json")
RECEIPT_RE = re.compile(r"[0-9]{14}\Z")


class OriginalXbrlProbeError(ValueError):
    """Use fixed reason codes only, without interpolation of provider values."""


def first_q3_original_receipts(payload: Mapping[str, Any]) -> dict[str, str]:
    """Derive exact initial Q3 receipts, rejecting same-day version ambiguity."""
    date_summary = validate_complete_q3_filing_index(payload)
    if date_summary["multiple_versions_on_initial_filing_date"]:
        raise OriginalXbrlProbeError("INITIAL_DAY_VERSION_AMBIGUOUS")
    rows = payload["list"]
    selected: dict[str, str] = {}
    for label, (period, _) in TARGETS.items():
        earliest = date_summary[
            "q_minus_4_initial_filing_date" if label == "Q_MINUS_4"
            else "q_current_initial_filing_date"
        ].replace("-", "")
        candidates = [
            row["rcept_no"] for row in rows
            if f"분기보고서 ({period})" in row["report_nm"]
            and row["rcept_dt"] == earliest
        ]
        original_title = f"분기보고서 ({period})"
        truly_initial = [
            row["rcept_no"] for row in rows
            if row["rcept_dt"] == earliest and row["report_nm"].strip() == original_title
        ]
        if len(candidates) != 1 or len(truly_initial) != 1 or truly_initial != candidates:
            raise OriginalXbrlProbeError("ORIGINAL_EDITION_AMBIGUOUS")
        if not RECEIPT_RE.fullmatch(truly_initial[0]):
            raise OriginalXbrlProbeError("ORIGINAL_RECEIPT_INVALID")
        selected[label] = truly_initial[0]
    if selected["Q_MINUS_4"] == selected["Q_CURRENT"]:
        raise OriginalXbrlProbeError("ORIGINAL_RECEIPT_COLLISION")
    return selected


def inspect_xbrl_zip(source: bytes) -> dict[str, Any]:
    """Read ZIP content with bounded CRC checks; record only aggregate hashes.

    No historical-publication-time, revision or XBRL semantic admission.
    """
    if type(source) is not bytes or not (4 <= len(source) <= MAX_ZIP_BYTES):
        raise OriginalXbrlProbeError("XBRL_ZIP_BYTES_INVALID")
    if not source.startswith(b"PK\x03\x04"):
        raise OriginalXbrlProbeError("OFFICIAL_XBRL_ZIP_ABSENT")
    try:
        with zipfile.ZipFile(io.BytesIO(source), "r") as archive:
            files = [f for f in archive.infolist() if not f.is_dir()]
            if not files or len(files) > MAX_FILES:
                raise OriginalXbrlProbeError("XBRL_ARCHIVE_FILE_COUNT_INVALID")
            if sum(f.file_size for f in files) > MAX_EXPANDED_BYTES:
                raise OriginalXbrlProbeError("XBRL_ARCHIVE_EXPANDED_SIZE_INVALID")
            xml_count = 0
            file_digests = []
            seen = set()
            for f in files:
                if (f.file_size < 1 or f.file_size > MAX_SINGLE_FILE_BYTES
                        or f.flag_bits & 1):
                    raise OriginalXbrlProbeError("XBRL_ENTRY_UNSAFE")
                name = f.filename.replace("\\", "/")
                bits = name.split("/")
                if (name.startswith("/") or any(p in ("", ".", "..") for p in bits)
                        or name.casefold() in seen):
                    raise OriginalXbrlProbeError("XBRL_ENTRY_UNSAFE")
                seen.add(name.casefold())
                unix_type = stat.S_IFMT(f.external_attr >> 16)
                if unix_type not in (0, stat.S_IFREG):
                    raise OriginalXbrlProbeError("XBRL_ENTRY_UNSAFE")
                normalized = name.lower()
                if normalized.endswith((".xml", ".xbrl")):
                    xml_count += 1
                sha = hashlib.sha256()
                seen_size = 0
                with archive.open(f) as fileobj:
                    while True:
                        chunk = fileobj.read(65536)
                        if not chunk:
                            break
                        seen_size += len(chunk)
                        if seen_size > f.file_size or seen_size > MAX_SINGLE_FILE_BYTES:
                            raise OriginalXbrlProbeError("XBRL_ENTRY_SIZE_DRIFT")
                        sha.update(chunk)
                if seen_size != f.file_size:
                    raise OriginalXbrlProbeError("XBRL_ENTRY_SIZE_DRIFT")
                file_digests.append((name.encode("utf-8"), sha.digest()))
            if xml_count == 0:
                raise OriginalXbrlProbeError("XBRL_STRUCTURED_ENTRY_ABSENT")
            digest = hashlib.sha256()
            for name, inner_hash in sorted(file_digests):
                digest.update(len(name).to_bytes(4, "big"))
                digest.update(name)
                digest.update(inner_hash)
            return {
                "xbrl_archive_nonempty": True,
                "xbrl_archive_entries": len(files),
                "xbrl_structured_entries": xml_count,
                "xbrl_decompressed_entry_digest_sha256": digest.hexdigest(),
                "zip_crc_integrity_read_complete": True,
            }
    except (zipfile.BadZipFile, RuntimeError, EOFError, UnicodeError, OSError):
        raise OriginalXbrlProbeError("XBRL_ZIP_INTEGRITY_INVALID") from None


def _official_xbrl_get(session: requests.Session, key: str, receipt: str) -> bytes:
    if not RECEIPT_RE.fullmatch(receipt):
        raise OriginalXbrlProbeError("ORIGINAL_RECEIPT_INVALID")
    response = session.get(
        BASE + "fnlttXbrl.xml",
        params={"crtfc_key": key, "rcept_no": receipt, "reprt_code": REPORT_CODE},
        timeout=30, allow_redirects=False, stream=True,
    )
    try:
        if response.status_code != 200:
            raise OriginalXbrlProbeError("OFFICIAL_XBRL_HTTP_FAILED")
        data = bytearray()
        for part in response.iter_content(chunk_size=65536):
            data.extend(part)
            if len(data) > MAX_ZIP_BYTES:
                raise OriginalXbrlProbeError("XBRL_ZIP_BYTES_INVALID")
        return bytes(data)
    except requests.RequestException:
        raise OriginalXbrlProbeError("OFFICIAL_XBRL_NETWORK_FAILED") from None
    finally:
        response.close()


def run(session: requests.Session | None = None) -> dict[str, Any]:
    key = os.getenv("OPENDART_API_KEY", "").strip()
    report: dict[str, Any] = {
        "purpose": "M20_FIXED_ISSUER_ORIGINAL_XBRL_ZIP_SHAPE_NOT_PIT_ADMISSION",
        "pilot_stock": STOCK_CODE,
        "source": "OpenDART_OFFICIAL_APIS",
        "report_code": REPORT_CODE,
        "source_status": "AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "credential_configured": bool(key),
        "query_window_start": BEGIN,
        "query_window_end": END,
        "original_q3_archives_received": 0,
        "report_filing_date_level_verified": False,
        "raw_bytes_or_financial_amounts_persisted": False,
        "corporation_to_issuer_historical_binding_verified": False,
        "original_document_timestamp_at_publication_verified": False,
        "xbrl_historical_revision_lineage_independently_verified": False,
        "q_and_q_minus_4_economic_comparability_verified": False,
        "decision_time_market_cap_verified": False,
        "krx_tradability_verified": False,
        "pit_source_admitted": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "champion_change_authorized": False,
        "real_orders_authorized": False,
        "live_order_authorized": False,
        "funds_movement_authorized": False,
        "permission_change_authorized": False,
        "ordering": "DISABLED",
    }
    if not key:
        return report
    if session is None:
        session = requests.Session()
    stage = "CURRENT_ISSUER_MAPPING"
    try:
        corp = corp_from_official_zip(_official_get(
            session, "corpCode.xml", {"crtfc_key": key}, zip_response=True))
        stage = "OFFICIAL_PERIODIC_FILING_INDEX"
        index = _official_get(session, "list.json", {
            "crtfc_key": key, "corp_code": corp, "bgn_de": BEGIN,
            "end_de": END, "pblntf_ty": "A", "page_count": "100",
        })
        selected = first_q3_original_receipts(index)
        report["report_filing_date_level_verified"] = True
        for name in ("Q_MINUS_4", "Q_CURRENT"):
            stage = f"OFFICIAL_{name}_XBRL_ZIP"
            zipped = _official_xbrl_get(session, key, selected[name])
            shape = inspect_xbrl_zip(zipped)
            report["original_q3_archives_received"] += 1
            report[name.lower() + "_archive_shape"] = shape
        report["source_status"] = "TWO_OFFICIAL_ORIGINAL_XBRL_ARCHIVES_SHAPE_ONLY"
    except Exception as exc:
        report["source_status"] = "SOURCE_GAP_FAIL_CLOSED"
        report["failure_stage"] = stage
        allowed = {
            "INITIAL_DAY_VERSION_AMBIGUOUS", "ORIGINAL_EDITION_AMBIGUOUS",
            "ORIGINAL_RECEIPT_INVALID", "ORIGINAL_RECEIPT_COLLISION",
            "XBRL_ZIP_BYTES_INVALID", "OFFICIAL_XBRL_ZIP_ABSENT",
            "XBRL_ARCHIVE_FILE_COUNT_INVALID", "XBRL_ARCHIVE_EXPANDED_SIZE_INVALID",
            "XBRL_ENTRY_UNSAFE", "XBRL_ENTRY_SIZE_DRIFT",
            "XBRL_STRUCTURED_ENTRY_ABSENT", "XBRL_ZIP_INTEGRITY_INVALID",
            "OFFICIAL_XBRL_HTTP_FAILED", "OFFICIAL_XBRL_NETWORK_FAILED",
        }
        error = str(exc) if type(exc) is OriginalXbrlProbeError else ""
        report["failure_reason_code"] = error if error in allowed else "UNCLASSIFIED"
    return report


if __name__ == "__main__":
    result = run()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OPENDART_M20_ORIGINAL_XBRL=" + json.dumps(result, ensure_ascii=False), flush=True)
