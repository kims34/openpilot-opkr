"""Offline adapter for output shape of KRX private SHA-bound original audit.

Only accepts the metadata dicts returned after the independent private
checkpoint/raw-byte verification. Does not itself verify source bytes,
calendar, security PIT status, source provenance, broker permissions.
Never export full private date-level rows outside the authorized environment.
"""
from __future__ import annotations

from research_v1_krx_calendar_gap_boundary import _day, _sha

NONEMPTY = "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED"
EMPTY_WITH_MASTER = "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
BOTH_EMPTY = "PROVIDER_BOTH_EMPTY_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
KNOWN = frozenset({NONEMPTY, EMPTY_WITH_MASTER, BOTH_EMPTY})


def normalize_preverified_source_days(audit_metadata: list[dict]) -> dict:
    """Validate reported per-day classifications; never create trust.

    Input must come from upstream private SHA-backed _check_one after its
    actual execution. The pair_sha256 is the whole per-day source-pair
    fingerprint, NOT one raw source object's SHA.
    """
    out = {
        "status": "FAIL_CLOSED_INVALID_SOURCE_DAY_METADATA",
        "provenance": "UNTRUSTED_UNLESS_UPSTREAM_PRIVATE_SHA_AUDIT_ACTUALLY_EXECUTED",
        "observations": [],
        "calendar_attested": False,
        "PIT_admitted": False,
        "security_status_attested": False,
        "performance_authorized": False,
        "real_orders_authorized": False,
        "original_source_bytes_verified_by_this_adapter": False,
        "network_requests_attempted": False,
        "storage_mutated": False,
    }
    if not isinstance(audit_metadata, list) or not audit_metadata or len(audit_metadata) > 4000:
        return out
    normalized = []
    seen = set()
    for row in audit_metadata:
        if not isinstance(row, dict):
            return out
        day = row.get("day")
        cls = row.get("source_day_class")
        if not _day(day) or day in seen or cls not in KNOWN:
            return out
        if not _sha(row.get("pair_sha256")):
            return out
        daily = row.get("daily_rows")
        common = row.get("common_rows")
        if type(daily) is not int or type(common) is not int or daily < 0 or common < 0:
            return out
        if cls == NONEMPTY:
            if daily < 1 or common < 1 or common > daily:
                return out
            state = "NONEMPTY"
        else:
            if daily != 0 or common != 0:
                return out
            state = "EMPTY"
        seen.add(day)
        normalized.append({
            "date": day,
            "response_state": state,
            # Pair-level checksum, not an individual raw object checksum.
            "raw_receipt_sha256": row["pair_sha256"],
        })
    out["status"] = "DECLARED_SOURCE_METADATA_NORMALIZED_NOT_PIT"
    out["observations"] = sorted(normalized, key=lambda x: x["date"])
    return out
