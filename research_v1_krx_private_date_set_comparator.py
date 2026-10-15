"""Date-by-date KRX KOSPI private audit / reference closure reconciliation.

Read-only. No new provider requests, imports of broker modules, storage writes,
trading, sealed holdout use, or raw KRX issuer/price logs. All date-specific
material stays in the authorized private environment. A reference calendar
claim is NOT proof of original KRX provenance or PIT availability.

Private runner delegates SHA verification to the already-existing
research_v1_krx_openapi_private_integrity_audit._check_one function on the
dedicated /data store. This module itself never authenticates an outside
calendar document: independent source attestation remains a separate gate.
"""
from __future__ import annotations

from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import os
import re
from typing import Callable

SHA = re.compile(r"^[0-9a-f]{64}$")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RAW_DAY = re.compile(r"^\d{8}$")
KNOWN_CLASS = frozenset({
    "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED",
    "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
    "PROVIDER_BOTH_EMPTY_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
})

BLOCK = {
    "classification": "ORIGINAL_KRX_DAY_SET_AGAINST_REFERENCE_CANDIDATES_ONLY",
    "original_official_calendar_attested": False,
    "source_contract_gates_C_D_open": False,
    "historical_pit_available_at_verified": False,
    "original_security_status_verified": False,
    "27_quarantined_securities_released": False,
    "performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "real_orders_authorized": False,
    "ordering": "DISABLED",
    "provider_requests_made": False,
    "raw_security_rows_emitted": False,
    "private_storage_mutated": False,
}


def expected_private_source_root() -> Path | None:
    """Exactly the original worker's /data fallback; no off-mount paths.

    This only computes a candidate root. In production _trusted_private_root
    subsequently resolves it and authenticates the dedicated private store.
    """
    base = Path(os.getenv("KRX_PRIVATE_RAW_DIR") or "/data")
    if (not base.is_absolute() or not base.is_relative_to(Path("/data"))
            or ".." in base.parts or base.is_symlink()):
        return None
    return base / "openapi_kospi_history_v1"


def _parse_day(value: object) -> date:
    if type(value) is not str or not DAY.fullmatch(value):
        raise ValueError("INVALID_ISO_DAY")
    d = date.fromisoformat(value)
    if d.isoformat() != value or d.weekday() >= 5:
        raise ValueError("INVALID_WEEKDAY")
    return d


def reconcile_exact_date_sets(
    *, start: str, end: str, verified_original_days: list[dict],
    reference_closed_iso_days: list[str], expected_empty_count: int | None = None,
    expected_original_audit_snapshot_sha256: str | None = None,
) -> dict:
    """Compare exact dates in memory; return ONLY aggregate counts/digests.

    Verified-original rows must be supplied by the SHA-verifying private
    _check_one; the caller is responsible for actually verifying those bytes.
    Private raw per-date digests and identities are NEVER returned.
    """
    report = {
        "status": "FAIL_CLOSED_INVALID_OR_MISSING_DATE_LEVEL_EVIDENCE",
        "start": start, "end": end,
        "weekday_scope_count": 0,
        "verified_original_pairs": 0,
        "original_empty_day_count": 0,
        "reference_closed_day_count": 0,
        "empty_on_reference_closed": 0,
        "empty_on_reference_open": 0,
        "nonempty_on_reference_closed": 0,
        "original_pair_scope_sha256": None,
        "original_audit_compatible_snapshot_sha256": None,
        "comparison_metadata_sha256": None,
        **BLOCK,
    }
    try:
        lo,hi=date.fromisoformat(start),date.fromisoformat(end)
        if (lo.isoformat()!=start or hi.isoformat()!=end or lo>hi
                or lo.year!=hi.year or lo.year<2015 or hi>date(2026,10,12)
                or (hi-lo).days>=366):
            return report
        expected={lo+timedelta(days=i) for i in range((hi-lo).days+1)
                  if (lo+timedelta(days=i)).weekday()<5}
        if not expected or not isinstance(verified_original_days,list) or not isinstance(reference_closed_iso_days,list):
            return report
        if (len(verified_original_days)!=len(expected) or len(reference_closed_iso_days)>len(expected)
                or len(reference_closed_iso_days)!=len(set(reference_closed_iso_days))
                or (expected_empty_count is not None
                    and (type(expected_empty_count) is not int or expected_empty_count<0))):
            return report
        reference={_parse_day(x) for x in reference_closed_iso_days}
        if not reference.issubset(expected):
            return report
        seen={}
        pair_hashes=[]
        for row in verified_original_days:
            if type(row) is not dict:
                return report
            value=row.get("day")
            if type(value) is not str or not RAW_DAY.fullmatch(value):
                return report
            day=date.fromisoformat(value[:4]+"-"+value[4:6]+"-"+value[6:])
            if day not in expected or day in seen:
                return report
            p=row.get("pair_sha256")
            cls=row.get("source_day_class")
            daily=row.get("daily_rows")
            common=row.get("common_rows")
            if (type(p) is not str or not SHA.fullmatch(p) or cls not in KNOWN_CLASS
                    or type(daily) is not int or type(common) is not int
                    or daily<0 or common<0 or common>daily
                    or (cls=="NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED" and (daily==0 or common==0))
                    or (cls!="NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED" and (daily!=0 or common!=0))):
                return report
            seen[day]=cls
            pair_hashes.append((day.isoformat(),p))
        if set(seen)!=expected:
            return report
        empty={d for d,c in seen.items() if c!="NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED"}
        if expected_empty_count is not None and len(empty)!=expected_empty_count:
            report["status"]="FAIL_CLOSED_AGGREGATE_SOURCE_RECEIPT_DRIFT"
            return report
        # Pair fingerprints are from private _check_one and already bound to raw SHA.
        # Final digest reveals no original provider pair hashes or exact days.
        report["original_audit_compatible_snapshot_sha256"]=hashlib.sha256(json.dumps(
            [{"day":d.replace("-",""),"pair_sha256":p} for d,p in sorted(pair_hashes)],
            sort_keys=True,separators=(",",":")
        ).encode("utf-8")).hexdigest()
        if (expected_original_audit_snapshot_sha256 is not None
                and report["original_audit_compatible_snapshot_sha256"] != expected_original_audit_snapshot_sha256):
            report["status"]="FAIL_CLOSED_ORIGINAL_SNAPSHOT_FINGERPRINT_DRIFT"
            return report
        report["original_pair_scope_sha256"]=hashlib.sha256(json.dumps(
            sorted(pair_hashes),separators=(",",":")
        ).encode("utf-8")).hexdigest()
        comparison={
            "start":start,"end":end,
            "original_empty":len(empty),"reference_closed":len(reference),
            "empty_on_closed":len(empty&reference),
            "empty_on_open":len(empty-reference),
            "nonempty_on_closed":len(reference-empty),
        }
        report["comparison_metadata_sha256"]=hashlib.sha256(
            json.dumps(comparison,sort_keys=True,separators=(",",":")).encode("utf-8")
        ).hexdigest()
        report.update({
            "weekday_scope_count":len(expected),
            "verified_original_pairs":len(seen),
            "original_empty_day_count":len(empty),
            "reference_closed_day_count":len(reference),
            "empty_on_reference_closed":len(empty&reference),
            "empty_on_reference_open":len(empty-reference),
            "nonempty_on_reference_closed":len(reference-empty),
            "status":("EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT"
                      if empty==reference
                      else "EXACT_DATE_SET_MISMATCH_SOURCE_ADMISSION_BLOCKED"),
        })
        return report
    except (ValueError, TypeError, OverflowError):
        return report


def audit_private_scope(
    *, private_root: Path, start: str, end: str,
    reference_closed_iso_days: list[str], expected_empty_count: int,
    expected_original_audit_snapshot_sha256: str | None = None,
    existing_audit: Callable | None = None,
) -> dict:
    """Dedicated Railway private-volume execution only; no extra KRX requests.

    An injected audit callback is FOR TRUSTED OFFLINE TESTS ONLY. In normal
    service usage we always execute real _check_one SHA and file checks.
    """
    fail={"status":"FAIL_CLOSED_NOT_AUTHORIZED_PRIVATE_AUDIT_ENV",**BLOCK}
    if existing_audit is None:
        # Fail before importing the production-only provider dependencies.
        # No GitHub CI runner, laptop or arbitrary root may pretend to be
        # the dedicated original KRX historical worker and mounted volume.
        # Share the exact /data fallback and scope check with the one-year
        # runner, then defer to the deployed original store's path verifier.
        required=expected_private_source_root()
        actual=Path(private_root)
        if (os.getenv("RAILWAY_SERVICE_NAME")!="indexalert-krx-historical-worker"
                or required is None or actual!=required
                or not actual.is_relative_to(Path("/data"))):
            return fail
        # Check source provenance pins only after verifying worker identity
        # and mount scope; prior environment refusal semantics remain stable.
        # Every REAL Railway original source audit must be pinned to the
        # historical annual SHA receipt. Only synthetic callbacks can omit
        # the SHA, and those ALWAYS return SYNTHETIC status.
        if (type(expected_original_audit_snapshot_sha256) is not str
                or not SHA.fullmatch(expected_original_audit_snapshot_sha256)
                or type(expected_empty_count) is not int or expected_empty_count < 0
                or not isinstance(reference_closed_iso_days, list)
                or not reference_closed_iso_days):
            return {"status": "FAIL_CLOSED_UNPINNED_PRIVATE_ORIGINAL_RECEIPTS", **BLOCK}
        from research_v1_krx_openapi_private_integrity_audit import (
            _check_one, _trusted_private_root,
        )
        try:
            root=_trusted_private_root(actual)
        except Exception:
            return fail
        verify=_check_one
    else:
        # This mode is only for synthetic tests, NOT proof of actual SHA audit.
        root=Path(private_root)
        verify=existing_audit
    try:
        lo,hi=date.fromisoformat(start),date.fromisoformat(end)
        if lo.year!=hi.year or (hi-lo).days>=366 or hi>date(2026,10,12):
            return fail
        days=[(lo+timedelta(days=i)).strftime("%Y%m%d")
              for i in range((hi-lo).days+1)
              if (lo+timedelta(days=i)).weekday()<5]
        if not days:
            return fail
        receipts=[verify(root,d) for d in days]
    except Exception:
        return fail
    report=reconcile_exact_date_sets(
        start=start,end=end,verified_original_days=receipts,
        reference_closed_iso_days=reference_closed_iso_days,
        expected_empty_count=expected_empty_count,
        expected_original_audit_snapshot_sha256=expected_original_audit_snapshot_sha256,
    )
    if existing_audit is not None:
        report["status"]="SYNTHETIC_CALLBACK_NOT_ORIGINAL_SOURCE_PROOF"
    return report
