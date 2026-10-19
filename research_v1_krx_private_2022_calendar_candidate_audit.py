"""2022 KRX private SOURCE-EMPTY dates versus 14 PUBLIC market holiday CANDIDATES.

Offline ONLY: no KRX requests, orders or network. Production snapshot must be
verified byte-for-byte by preexisting private integrity audit and again before
the in-memory date-set comparison. This never establishes authoritative original
market holidays or stock/day tradability/PIT.
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

# Existing Railway KRX worker's 2022 full original private raw-byte integrity
# log at 2026-10-12T13:08:31Z. Not an authentic historic market calendar!
PINNED_2022_PRIVATE_SNAPSHOT_SHA256 = (
    "0b110aaa452f43788e9880f4bf769981dee5f31c617485ca49cc7e7918306c9e"
)
# Candidate list, not independently authenticated original exchange calendar.
# Ordinary calendar dates need independent as-of/source lineage proof.
REGULAR_2022_CANDIDATES = frozenset((
    "20220131", "20220201", "20220202", "20220301", "20220505",
    "20220606", "20220815", "20220909", "20220912", "20221003",
    "20221010",
))
# The KRX market closure announcement was reported 2022-02-10.
ELECTION_2022_CANDIDATES = frozenset(("20220309", "20220601"))
# The KRX year-end closure was announced 2022-12-15.
YEAR_END_2022_CANDIDATES = frozenset(("20221230",))
PUBLIC_CANDIDATES = (
    REGULAR_2022_CANDIDATES | ELECTION_2022_CANDIDATES |
    YEAR_END_2022_CANDIDATES
)
# Primary issuer/KRX KIND page has actual 2022 election holiday dates, but
# explicitly applies to KOSDAQ. Our private 2022 raw source is KOSPI. Venue
# transposition is NOT allowed. The document path date is not an authenticated
# first-release clock-time or 2022-era independently archived PIT receipt.
KRX_KIND_KOSDAQ_ELECTION_PRIMARY_NOTICE_URL = (
    "https://kind.krx.co.kr/external/2022/02/10/000126/"
    "20220209001809/71985.htm"
)
KRX_KIND_KOSDAQ_ELECTION_DATES = frozenset(("20220309", "20220601"))
PRIVATE_DATA_MARKET = "KOSPI"
PRIMARY_NOTICE_MARKET = "KOSDAQ"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
EMPTY_CLASSES = frozenset((
    "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
    "PROVIDER_BOTH_EMPTY_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
))
NONEMPTY_CLASS = "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED"
START, END = "2022-01-01", "2022-12-31"
EXPECTED_WEEKDAYS = 260
EXPECTED_EMPTY = 14
DENIAL = {
    "official_calendar_original_publication_authenticated": False,
    "regular_2022_calendar_asof_verified": False,
    "election_closure_publication_pit_verified": False,
    "year_end_closure_publication_pit_verified": False,
    "private_original_data_available_in_2022": False,
    "individual_security_tradability_verified": False,
    "historical_corporate_actions_verified": False,
    "official_market_status_admitted": False,
    "full_universe_source_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "network_request_attempted": False,
    "storage_mutated": False,
    "private_day_dates_or_raw_rows_emitted": False,
    "ordering": "DISABLED",
}


class Private2022CalendarGap(ValueError):
    """Constant diagnostics; never embed original raw source or private dates."""


def compare_verified_2022(
    rows: Mapping[str, dict], *, first_pass_snapshot_sha256: str,
    expected_snapshot_sha256: str | None = None,
) -> dict:
    """Count-only set comparison of COMPLETE supplied receipt summaries.

    This helper verifies receipt structure and two-pass identity; the CALLER
    must independently authenticate first-pass original raw bytes via
    audit_private_range. This helper alone is not raw source authentication.
    """
    if expected_snapshot_sha256 is None:
        expected_snapshot_sha256 = PINNED_2022_PRIVATE_SNAPSHOT_SHA256
    days = _bounds(START, END)
    if (len(days) != EXPECTED_WEEKDAYS or type(rows) is not dict
            or set(rows) != set(days)):
        raise Private2022CalendarGap("2022_COMPLETE_WEEKDAY_PAIR_SET_MISSING")
    if (type(first_pass_snapshot_sha256) is not str
            or type(expected_snapshot_sha256) is not str
            or not HEX64.fullmatch(first_pass_snapshot_sha256)
            or not HEX64.fullmatch(expected_snapshot_sha256)
            or first_pass_snapshot_sha256 != expected_snapshot_sha256):
        raise Private2022CalendarGap("2022_ORIGINAL_PINNED_SNAPSHOT_NOT_VERIFIED")

    empty_days = set()
    receipts = []
    for day in days:
        row = rows[day]
        if (type(row) is not dict or row.get("day") != day
                or type(row.get("pair_sha256")) is not str
                or not HEX64.fullmatch(row["pair_sha256"])
                or type(row.get("daily_rows")) is not int
                or row["daily_rows"] < 0
                or type(row.get("source_day_class")) is not str):
            raise Private2022CalendarGap("2022_PRIVATE_RECEIPT_INVALID")
        if row["daily_rows"] == 0:
            if row["source_day_class"] not in EMPTY_CLASSES:
                raise Private2022CalendarGap("2022_EMPTY_SOURCE_CLASS_CONFLICT")
            empty_days.add(day)
        elif row["source_day_class"] != NONEMPTY_CLASS:
            raise Private2022CalendarGap("2022_NONEMPTY_SOURCE_CLASS_CONFLICT")
        receipts.append({"day": day, "pair_sha256": row["pair_sha256"]})

    second_sha = hashlib.sha256(json.dumps(
        receipts, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if second_sha != first_pass_snapshot_sha256:
        raise Private2022CalendarGap("2022_ORIGINAL_SOURCE_CHANGED_BETWEEN_PASSES")

    missing = PUBLIC_CANDIDATES - empty_days
    unexpected = empty_days - PUBLIC_CANDIDATES
    exact = len(empty_days) == EXPECTED_EMPTY and not missing and not unexpected
    return {
        "purpose": "KRX_2022_PRIVATE_EMPTY_DAYS_VS_PUBLIC_HOLIDAY_CANDIDATES",
        "status": (
            "PRIVATE_2022_DATE_SET_MATCHES_CANDIDATES_NOT_PIT" if exact
            else "PRIVATE_2022_DATE_SET_MISMATCH_NOT_PIT"
        ),
        "checked_original_sha_receipt_pairs": len(rows),
        "source_empty_weekdays": len(empty_days),
        "regular_calendar_candidates": len(REGULAR_2022_CANDIDATES),
        "election_candidates": len(ELECTION_2022_CANDIDATES),
        "year_end_candidates": len(YEAR_END_2022_CANDIDATES),
        "public_holiday_candidates": len(PUBLIC_CANDIDATES),
        # Original public notice is market-specific, not a universal trading
        # calendar. These are source-scope hints ONLY, never PIT admission.
        "private_2022_market_scope": PRIVATE_DATA_MARKET,
        "identified_krx_kind_primary_notice_market_scope": PRIMARY_NOTICE_MARKET,
        "identified_krx_kind_primary_notice_election_dates": len(
            KRX_KIND_KOSDAQ_ELECTION_DATES
        ),
        "cross_venue_kosdaq_primary_notice_is_kospi_evidence": False,
        "matched_kospi_first_party_original_kind_election_notice_count": 0,
        "krx_kind_primary_notice_original_publication_instant_verified": False,
        "matched_candidate_empty_dates": len(empty_days & PUBLIC_CANDIDATES),
        "expected_closure_dates_missing_in_private_empty_count": len(missing),
        "unexpected_private_empty_dates_count": len(unexpected),
        "2022_private_candidate_date_sets_equal": exact,
        "first_second_pass_checkpoint_fingerprints_match": True,
        "receipt_structure_checked_not_original_provider_authentication": True,
        "private_first_pass_raw_byte_audit_must_be_independently_run": True,
        "election_2022_announcement_date": "2022-02-10",
        "year_end_2022_announcement_date": "2022-12-15",
        **DENIAL,
    }


def audit_private_2022(
    *, execute: bool = False,
    environment: Mapping[str, str] | None = None,
    integrity: Callable[..., dict] = audit_private_range,
    check_one: Callable[[Path, str], dict] = _check_one,
) -> dict:
    result = {
        "purpose": "KRX_2022_PRIVATE_EMPTY_DAYS_VS_PUBLIC_HOLIDAY_CANDIDATES",
        "status": "DRY_RUN_NO_PRIVATE_STORAGE_READ",
        "2022_private_candidate_date_sets_equal": False,
        **DENIAL,
    }
    if not execute:
        return result
    env = os.environ if environment is None else environment
    if env.get("RAILWAY_SERVICE_NAME") != WORKER:
        result["status"] = "FAIL_CLOSED_NOT_APPROVED_DEDICATED_WORKER"
        return result
    raw_dir = env.get("KRX_PRIVATE_RAW_DIR")
    if (type(raw_dir) is not str
            or (raw_dir != "/data" and not raw_dir.startswith("/data/"))):
        result["status"] = "FAIL_CLOSED_ORIGINAL_PRIVATE_VOLUME_UNAVAILABLE"
        return result
    root = Path(raw_dir) / PRIVATE_SUBDIR
    try:
        trusted = _trusted_private_root(root)
        first = integrity(root=trusted, start=START, end=END)
        if (first.get("status") != "ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED"
                or first.get("expected_weekdays") != EXPECTED_WEEKDAYS
                or first.get("verified_date_pairs") != EXPECTED_WEEKDAYS
                or first.get("empty_daily_unverified_calendar_or_source_gap_days")
                    != EXPECTED_EMPTY
                or first.get("invalid_pair_count") != 0
                or first.get("missing_weekday_pair_count") != 0
                or first.get("network_request_attempted") is not False
                or first.get("storage_mutated") is not False
                or first.get("source_admitted") is not False
                or first.get("snapshot_fingerprint_sha256")
                    != PINNED_2022_PRIVATE_SNAPSHOT_SHA256):
            raise Private2022CalendarGap("2022_FIRST_PASS_ORIGINAL_CHECK_FAILED")
        rows = {day: check_one(trusted, day) for day in _bounds(START, END)}
        out = compare_verified_2022(
            rows, first_pass_snapshot_sha256=first["snapshot_fingerprint_sha256"]
        )
        out["original_raw_byte_integrity_audit_completed_this_invocation"] = True
        return out
    except Exception:
        result["status"] = "FAIL_CLOSED_2022_ORIGINAL_PRIVATE_PROOF_UNVERIFIED"
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="No-provider 2022 private KRX holiday candidate audit"
    )
    parser.add_argument("--audit", action="store_true")
    options = parser.parse_args()
    output = audit_private_2022(execute=options.audit)
    print("INDEXALERT_2022_PRIVATE_CALENDAR_CANDIDATE_AUDIT=" +
          json.dumps(output, sort_keys=True), flush=True)
    if options.audit and output["status"] != (
        "PRIVATE_2022_DATE_SET_MATCHES_CANDIDATES_NOT_PIT"
    ):
        raise SystemExit(1)
