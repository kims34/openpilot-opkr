"""Read-only exact 2021 KRX private-source weekday vs public holiday-candidate set.

No provider/network/broker calls. Only the existing KRX worker's dedicated
private /data volume may be read, after full first-pass raw-byte SHA audit.
Second-pass receipts MUST have the same fingerprint (TOCTOU fail-closed).
No private dates, symbols, rows, source digests or amounts are emitted.
A matching set is NOT independently authenticated official holiday/PIT proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Callable, Mapping

from research_v1_krx_openapi_private_integrity_audit import (
    _bounds, _check_one, _trusted_private_root, audit_private_range,
)
from research_v1_krx_openapi_private_history_batch import PRIVATE_SUBDIR, WORKER

# Pinned from Railway worker's actual 2026-10-12 verified 2021 annual
# integrity log. This digest represents PRIVATE stored source receipts,
# NOT the true historical exchange open/closed calendar.
PINNED_2021_PRIVATE_SNAPSHOT_SHA256 = (
    "362716e7bb5e025a9dcd39207b1ee095d97c633b8ca907722c766edf799ec2a1"
)
# Original KRX-backed public 2020-12-28 2021 market-calendar announcement.
# Publication-vintage evidence is historical text, NOT cryptographic PIT.
EARLY_2021_CLOSURES = frozenset((
    "20210101", "20210211", "20210212", "20210301",
    "20210505", "20210519", "20210920", "20210921",
    "20210922", "20211231",
))
# Subsequent 2021-08-04 public KRX market-closure announcement.
AUGUST_2021_ADDED_CLOSURES = frozenset((
    "20210816", "20211004", "20211011",
))
EXPECTED_HOLIDAYS = EARLY_2021_CLOSURES | AUGUST_2021_ADDED_CLOSURES
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
EMPTY = frozenset((
    "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
    "PROVIDER_BOTH_EMPTY_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
))
OPEN = "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED"
START, END = "2021-01-01", "2021-12-31"
COUNT = 261
UNKNOWN = 13
SAFETY = {
    "actual_original_market_calendar_authenticated": False,
    "original_holiday_publication_pit_verified": False,
    "private_source_retrieved_in_2021": False,
    "individual_security_tradability_verified": False,
    "corporate_actions_verified": False,
    "official_market_status_admitted": False,
    "full_universe_source_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "live_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "network_request_attempted": False,
    "storage_mutated": False,
    "private_source_rows_or_dates_emitted": False,
    "ordering": "DISABLED",
}


class PrivateCalendarEvidenceGap(ValueError):
    """No private evidence in exceptions; constant codes only."""


def compare_verified_2021(rows: Mapping[str, dict], *,
                          prior_snapshot_sha256: str,
                          expected_snapshot_sha256: str = PINNED_2021_PRIVATE_SNAPSHOT_SHA256) -> dict:
    """Compare a complete already SHA-verified private corpus, count-only.

    Caller supplies all 261 **rechecked** receipt summaries, never just
    selected candidate holiday dates. Recompute exact audit snapshot digest,
    ensuring no private checkpoint/source changed between audit passes.
    """
    days = _bounds(START, END)
    if len(days) != COUNT or type(rows) is not dict or set(rows) != set(days):
        raise PrivateCalendarEvidenceGap("2021_COMPLETE_WEEKDAY_PAIR_SET_MISSING")
    if (type(prior_snapshot_sha256) is not str
            or type(expected_snapshot_sha256) is not str
            or not HEX64.fullmatch(prior_snapshot_sha256)
            or not HEX64.fullmatch(expected_snapshot_sha256)
            or prior_snapshot_sha256 != expected_snapshot_sha256):
        raise PrivateCalendarEvidenceGap("2021_PINNED_SNAPSHOT_NOT_VERIFIED")

    receipt_fingerprints = []
    empty_days = set()
    for day in days:
        row = rows[day]
        if (type(row) is not dict or row.get("day") != day
                or type(row.get("pair_sha256")) is not str
                or not HEX64.fullmatch(row["pair_sha256"])
                or type(row.get("daily_rows")) is not int
                or row["daily_rows"] < 0
                or type(row.get("source_day_class")) is not str):
            raise PrivateCalendarEvidenceGap("2021_PRIVATE_DAY_RECEIPT_INVALID")
        if row["daily_rows"] == 0:
            if row["source_day_class"] not in EMPTY:
                raise PrivateCalendarEvidenceGap("2021_EMPTY_DAY_CLASS_CONFLICT")
            empty_days.add(day)
        elif row["source_day_class"] != OPEN:
            raise PrivateCalendarEvidenceGap("2021_NONEMPTY_DAY_CLASS_CONFLICT")
        receipt_fingerprints.append({"day": day, "pair_sha256": row["pair_sha256"]})

    second_fingerprint = hashlib.sha256(json.dumps(
        receipt_fingerprints, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if second_fingerprint != prior_snapshot_sha256:
        raise PrivateCalendarEvidenceGap("2021_SOURCE_CHANGED_BETWEEN_AUDIT_PASSES")
    missing = EXPECTED_HOLIDAYS - empty_days
    unexpected = empty_days - EXPECTED_HOLIDAYS
    equal = not missing and not unexpected
    return {
        "purpose": "KRX_2021_PRIVATE_SOURCE_EMPTY_DAYS_VS_PUBLISHED_CLOSURE_CANDIDATES",
        "status": (
            "PRIVATE_EMPTY_DATE_SET_MATCHES_CANDIDATES_NOT_PIT"
            if equal else "PRIVATE_EMPTY_DATE_SET_MISMATCH_NOT_PIT"
        ),
        "private_2021_complete_sha_verified_pairs": len(rows),
        "private_2021_empty_source_days": len(empty_days),
        "initial_2020_december_public_closure_candidates": len(EARLY_2021_CLOSURES),
        "later_2021_august_public_closure_candidates": len(AUGUST_2021_ADDED_CLOSURES),
        "public_candidate_dates_found_private_empty": len(empty_days & EXPECTED_HOLIDAYS),
        "private_2021_missing_expected_closure_count": len(missing),
        "private_2021_unexpected_empty_date_count": len(unexpected),
        "2021_private_and_public_candidate_sets_exactly_equal": equal,
        "second_pass_snapshot_identity_matches_first_pass": True,
        "private_source_hash_shape_and_content_audited": True,
        "public_2021_candidate_list_is_not_original_official_PIT": True,
        "initial_2021_calendar_announcement_vintage": "2020-12-28",
        "later_2021_calendar_revision_announcement_vintage": "2021-08-04",
        **SAFETY,
    }


def audit_private_2021(*, execute: bool = False,
                       environment: Mapping[str, str] | None = None,
                       integrity: Callable[..., dict] = audit_private_range,
                       check_one: Callable[[Path, str], dict] = _check_one) -> dict:
    result = {
        "purpose": "KRX_2021_PRIVATE_SOURCE_EMPTY_DAYS_VS_PUBLISHED_CLOSURE_CANDIDATES",
        "status": "DRY_RUN_NO_PRIVATE_STORAGE_READ",
        "2021_private_and_public_candidate_sets_exactly_equal": False,
        **SAFETY,
    }
    if not execute:
        return result
    env = os.environ if environment is None else environment
    if env.get("RAILWAY_SERVICE_NAME") != WORKER:
        result["status"] = "FAIL_CLOSED_NOT_APPROVED_DEDICATED_WORKER"
        return result
    data_root = env.get("KRX_PRIVATE_RAW_DIR")
    if (type(data_root) is not str or not data_root.startswith("/data/")
            and data_root != "/data"):
        result["status"] = "FAIL_CLOSED_PRIVATE_VOLUME_ROOT_UNAVAILABLE"
        return result
    root = Path(data_root) / PRIVATE_SUBDIR
    try:
        trusted = _trusted_private_root(root)
        first = integrity(root=trusted, start=START, end=END)
        if (first.get("status") != "ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED"
                or first.get("expected_weekdays") != COUNT
                or first.get("verified_date_pairs") != COUNT
                or first.get("empty_daily_unverified_calendar_or_source_gap_days") != UNKNOWN
                or first.get("invalid_pair_count") != 0
                or first.get("missing_weekday_pair_count") != 0
                or first.get("network_request_attempted") is not False
                or first.get("storage_mutated") is not False
                or first.get("source_admitted") is not False
                or first.get("snapshot_fingerprint_sha256")
                    != PINNED_2021_PRIVATE_SNAPSHOT_SHA256):
            raise PrivateCalendarEvidenceGap("2021_FIRST_PASS_INTEGRITY_OR_COUNT_DRIFT")
        # Second private byte-read: detect TOCTOU/in-flight source mutation.
        # The intermediate date mapping never leaves process memory.
        rows = {day: check_one(trusted, day) for day in _bounds(START, END)}
        return compare_verified_2021(
            rows, prior_snapshot_sha256=first["snapshot_fingerprint_sha256"]
        )
    except Exception:
        result["status"] = "FAIL_CLOSED_2021_PRIVATE_PROOF_UNVERIFIED"
        return result


if __name__ == "__main__":
    args = argparse.ArgumentParser(
        description="Read-only 2021 KRX private market calendar *candidate* day-set audit"
    )
    args.add_argument("--audit", action="store_true")
    cli = args.parse_args()
    out = audit_private_2021(execute=cli.audit)
    print("INDEXALERT_2021_PRIVATE_CALENDAR_CANDIDATE_AUDIT=" +
          json.dumps(out, sort_keys=True))
    if cli.audit and out["status"] != "PRIVATE_EMPTY_DATE_SET_MATCHES_CANDIDATES_NOT_PIT":
        raise SystemExit(1)
