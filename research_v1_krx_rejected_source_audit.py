"""Offline, read-only KRX rejected-OpenAPI receipt audit.

Uses already retrieved private daily/master response bytes. It never fetches
new data, writes source, emits security identifiers/prices or grants admission.
Its only public output is a bounded aggregate describing a rejected source.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping

import pandas as pd

from research_v1_krx_openapi_prospective_source import (
    KRXProspectiveOpenAPISourceError,
    build_current_session_openapi_source,
)
from research_v1_krx_private_store import validate_private_root_path

_RECEIPT_RE = re.compile(r"^rejected-(\d{4}-\d{2}-\d{2})-([0-9a-f]{64})\.json$")
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_MAX_RECEIPTS = 512
_MAX_RECEIPT_BYTES = 16 * 1024
_MAX_RAW_BYTES = 16 * 1024 * 1024
_RECEIPT_KEYS = frozenset({
    "classification", "requested_source_session", "daily_endpoint_suffix",
    "master_endpoint_suffix", "daily_raw_sha256", "master_raw_sha256",
    "daily_retrieved_at", "master_retrieved_at", "observed_available_by",
    "availability_semantics", "independent_source_admission_verified",
    "decision_recorded", "fresh_alpha_observation_admitted",
    "live_order_authorized",
})
_COUNTS = frozenset({
    "common_stock_rows", "nonpositive_ohlc_rows", "zero_volume_value_rows",
    "other_activity_rows", "all_zero_ohlc_rows",
})


class KRXRejectedAuditError(ValueError):
    """Fixed message ONLY; never insert raw provider/receipt data."""


def _read_protected(path: Path, *, max_bytes: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise KRXRejectedAuditError("PRIVATE_FILE_NOT_REGULAR")
    st = path.stat()
    if (st.st_mode & 0o777) != 0o600 or st.st_size <= 0 or st.st_size > max_bytes:
        raise KRXRejectedAuditError("PRIVATE_FILE_MODE_OR_SIZE_INVALID")
    data = path.read_bytes()
    if len(data) != st.st_size:
        raise KRXRejectedAuditError("PRIVATE_FILE_SIZE_DRIFT")
    return data


def _aware(value: Any) -> pd.Timestamp:
    if type(value) is not str:
        raise KRXRejectedAuditError("RECEIPT_TIME_INVALID")
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError, OverflowError):
        raise KRXRejectedAuditError("RECEIPT_TIME_INVALID") from None
    if pd.isna(timestamp) or timestamp.tzinfo is None:
        raise KRXRejectedAuditError("RECEIPT_TIME_INVALID")
    return timestamp.tz_convert("UTC")


def _validated_receipt(path: Path) -> tuple[dict[str, Any], pd.Timestamp]:
    match = _RECEIPT_RE.fullmatch(path.name)
    if match is None:
        raise KRXRejectedAuditError("RECEIPT_NAME_INVALID")
    data = _read_protected(path, max_bytes=_MAX_RECEIPT_BYTES)
    if hashlib.sha256(data).hexdigest() != match.group(2):
        raise KRXRejectedAuditError("RECEIPT_SHA_MISMATCH")
    try:
        doc = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise KRXRejectedAuditError("RECEIPT_JSON_INVALID") from None
    if type(doc) is not dict or set(doc) != _RECEIPT_KEYS:
        raise KRXRejectedAuditError("RECEIPT_SCHEMA_INVALID")
    day = match.group(1)
    try:
        valid_day = pd.Timestamp(day).strftime("%Y-%m-%d") == day
    except (ValueError, TypeError):
        valid_day = False
    if not valid_day or doc["requested_source_session"] != day:
        raise KRXRejectedAuditError("RECEIPT_SESSION_INVALID")
    if (
        doc["classification"] != "REJECTED_OPENAPI_SOURCE_DIAGNOSTIC_NOT_ADMISSION"
        or doc["daily_endpoint_suffix"] != "/stk_bydd_trd"
        or doc["master_endpoint_suffix"] != "/stk_isu_base_info"
        or doc["availability_semantics"] != "OBSERVED_RETRIEVAL_ONLY_NOT_HISTORICAL_PUBLICATION"
        or any(doc[field] is not False for field in (
            "independent_source_admission_verified", "decision_recorded",
            "fresh_alpha_observation_admitted", "live_order_authorized",
        ))
        or any(type(doc[field]) is not str or _SHA_RE.fullmatch(doc[field]) is None
               for field in ("daily_raw_sha256", "master_raw_sha256"))
    ):
        raise KRXRejectedAuditError("RECEIPT_AUTHORITY_OR_ROUTE_INVALID")
    daily_at = _aware(doc["daily_retrieved_at"])
    master_at = _aware(doc["master_retrieved_at"])
    seen = _aware(doc["observed_available_by"])
    if seen != max(daily_at, master_at):
        raise KRXRejectedAuditError("RECEIPT_TIME_DRIFT")
    if min(daily_at, master_at).tz_convert("Asia/Seoul").date() < pd.Timestamp(day).date():
        raise KRXRejectedAuditError("RECEIPT_BEFORE_SOURCE_SESSION")
    return doc, seen


def _raw_from_digest(root: Path, digest: str) -> bytes:
    target = root / "objects" / "sha256" / digest[:2] / (digest + ".bin")
    data = _read_protected(target, max_bytes=_MAX_RAW_BYTES)
    if hashlib.sha256(data).hexdigest() != digest:
        raise KRXRejectedAuditError("RAW_SHA_MISMATCH")
    return data


def audit_latest_rejected_source(
    *, private_root: Path, git_worktree: Path,
    connectivity_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify a recent private rejection without creating an admitted source.

    Return safe bounded counts only, no raw bytes, issue identifiers, receipt
    names/hashes, provider text or original pricing. Any inconsistency raises.
    """
    base = Path(private_root) / "rejected-openapi"
    checked = validate_private_root_path(base, git_worktree=git_worktree)
    if base.is_symlink() or checked != base.resolve():
        raise KRXRejectedAuditError("PRIVATE_ROOT_INVALID")
    if not base.exists():
        return {"status": "NO_SAVED_RECEIPT", "admission_verified": False}
    if not base.is_dir() or (base.stat().st_mode & 0o777) != 0o700:
        raise KRXRejectedAuditError("PRIVATE_ROOT_INVALID")
    receipts = sorted(base.glob("rejected-*.json"))
    if not receipts:
        return {"status": "NO_SAVED_RECEIPT", "admission_verified": False}
    if len(receipts) > _MAX_RECEIPTS:
        raise KRXRejectedAuditError("RECEIPT_COUNT_LIMIT")
    chosen: dict[str, Any] | None = None
    chosen_at: pd.Timestamp | None = None
    # Verify all receipt headers; audit raw objects only for newest observation.
    for path in receipts:
        doc, seen = _validated_receipt(path)
        if chosen_at is None or (seen, path.name) > (chosen_at, chosen["_name"]):
            chosen = dict(doc, _name=path.name)
            chosen_at = seen
    assert chosen is not None
    daily = _raw_from_digest(base, chosen["daily_raw_sha256"])
    master = _raw_from_digest(base, chosen["master_raw_sha256"])
    try:
        build_current_session_openapi_source(
            daily_raw=daily, master_raw=master,
            expected_session=chosen["requested_source_session"],
            daily_retrieved_at=chosen["daily_retrieved_at"],
            master_retrieved_at=chosen["master_retrieved_at"],
            connectivity_evidence=connectivity_evidence,
        )
    except KRXProspectiveOpenAPISourceError as exc:
        if not str(exc).startswith(
            "common-stock current-session OHLC contains nonpositive value;"
        ):
            raise KRXRejectedAuditError("SOURCE_REJECTION_REASON_CHANGED") from None
        counts = getattr(exc, "safe_ohlc_counts", None)
        if type(counts) is not dict or set(counts) != _COUNTS:
            raise KRXRejectedAuditError("SOURCE_REJECTION_COUNTS_INVALID")
        if any(type(n) is not int or n < 0 or n > 1000000 for n in counts.values()):
            raise KRXRejectedAuditError("SOURCE_REJECTION_COUNTS_INVALID")
        if (
            counts["nonpositive_ohlc_rows"] <= 0
            or counts["nonpositive_ohlc_rows"] > counts["common_stock_rows"]
            or counts["nonpositive_ohlc_rows"] != (
                counts["zero_volume_value_rows"] + counts["other_activity_rows"]
            )
            or counts["all_zero_ohlc_rows"] > counts["nonpositive_ohlc_rows"]
        ):
            raise KRXRejectedAuditError("SOURCE_REJECTION_COUNTS_INVALID")
        return {
            "status": "REJECTED_SOURCE_RAW_VERIFIED",
            "requested_source_session": chosen["requested_source_session"],
            "receipts_seen": len(receipts),
            "latest_raw_hashes_verified": True,
            "common_stock_rows": counts["common_stock_rows"],
            "nonpositive_ohlc_rows": counts["nonpositive_ohlc_rows"],
            "zero_volume_value_rows": counts["zero_volume_value_rows"],
            "other_activity_rows": counts["other_activity_rows"],
            "all_zero_ohlc_rows": counts["all_zero_ohlc_rows"],
            "official_halt_status_verified": False,
            "admission_verified": False,
            "live_order_authorized": False,
        }
    except Exception:
        raise KRXRejectedAuditError("SOURCE_DIAGNOSTIC_FAILED") from None
    raise KRXRejectedAuditError("SOURCE_NO_LONGER_REJECTED")
