"""Private read-only 2021 KRX market-holiday date-set reconciliation, NOT PIT.

Run only on the existing authorized dedicated KRX private-history worker
volume, with --audit. Re-verify the full 261 weekday original source pairs
and their existing preverified 2021 fingerprint; compare exact *dates*
of empty daily-trade responses with historically published exchange holidays.
No private per-day dates, receipts, identifiers, price rows, amounts, network
calls, provider credentials or file writes are emitted. Zero rows alone
can never establish authoritative historic exchange trading status or PIT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re

from research_v1_krx_openapi_private_integrity_audit import (
    _bounds, _check_one, _trusted_private_root, OfflinePrivateAuditError,
)
from research_v1_krx_openapi_private_history_batch import PRIVATE_SUBDIR, WORKER

# KRX's 2020-12-28 prospective calendar, updated by its 2021-08-04
# exchange-market announcement. Weekdays only: 10 initial + 3 later.
# Contemporaneous published KRX announcement reporting:
# https://www.yna.co.kr/view/AKR20201225031900002
# https://www.yna.co.kr/view/AKR20210804093200002
INITIAL_2021 = frozenset((
    "20210101", "20210211", "20210212", "20210301", "20210505",
    "20210519", "20210920", "20210921", "20210922", "20211231",
))
ADDED_2021 = frozenset(("20210816", "20211004", "20211011"))
OFFICIAL_FINAL_2021 = INITIAL_2021 | ADDED_2021
HOLIDAY_NOTICE_ASOF = "2021-08-04"
EXPECTED_WEEKDAY_PAIRS = 261
# Existing deployed read-only six-year Railway audit / 2021 year_receipts:
# verified_date_pairs=261, empty_daily_unverified...=13.
# Pin this cryptographic private-pair PANEL digest, not today's data.
EXISTING_2021_PANEL_SHA256 = (
    "362716e7bb5e025a9dcd39207b1ee095d97c633b8ca907722c766edf799ec2a1"
)
SHA = re.compile(r"[0-9a-f]{64}\Z")


def _base() -> dict:
    return {
        "purpose": "PRIVATE_2021_EXACT_MARKET_HOLIDAY_DATE_SET_AUDIT_NOT_PIT",
        "status": "DRY_RUN_PRIVATE_ORIGINAL_NOT_READ",
        "market_year": 2021,
        "initial_2020_announced_weekday_holidays": len(INITIAL_2021),
        "later_added_weekday_holidays": len(ADDED_2021),
        "revised_market_notice_asof": HOLIDAY_NOTICE_ASOF,
        "expected_final_official_weekday_holidays": len(OFFICIAL_FINAL_2021),
        "expected_weekday_original_pairs": EXPECTED_WEEKDAY_PAIRS,
        "original_pairs_reverified": 0,
        "original_panel_sha256_matches_prior_audit": False,
        "empty_daily_original_pairs_total": 0,
        "empty_daily_original_pairs_at_expected_holidays": 0,
        "empty_daily_original_pairs_on_other_weekdays": 0,
        "expected_holidays_with_nonempty_daily_rows": 0,
        "private_2021_original_date_set_independently_reconciled": False,
        "official_exchange_date_source_cryptographically_attested": False,
        "original_publication_pit_verified": False,
        "per_security_historical_tradability_verified": False,
        "corporate_actions_pit_verified": False,
        "full_universe_admitted": False,
        "m20_performance_run_authorized": False,
        "holdout_access_authorized": False,
        "champion_change_authorized": False,
        "live_orders_authorized": False,
        "funds_movement_authorized": False,
        "permissions_change_authorized": False,
        "raw_security_rows_or_identifiers_disclosed": False,
        "private_source_day_identifiers_disclosed": False,
        "network_request_attempted": False,
        "storage_mutated": False,
        "ordering": "DISABLED",
    }


def review_private_2021(*, execute: bool = False, environment=None) -> dict:
    """Verify private source pairs, but keep historical public PIT always false."""
    out = _base()
    if not execute:
        return out
    env = os.environ if environment is None else environment
    if env.get("RAILWAY_SERVICE_NAME") != WORKER:
        out["status"] = "FAIL_CLOSED_NOT_DEDICATED_KRX_WORKER"
        return out
    raw_root = env.get("KRX_PRIVATE_RAW_DIR")
    if (type(raw_root) is not str or
            not Path(raw_root).is_relative_to(Path("/data"))):
        out["status"] = "FAIL_CLOSED_PRIVATE_VOLUME_NOT_MOUNTED"
        return out
    root = Path(raw_root) / PRIVATE_SUBDIR
    try:
        root = _trusted_private_root(root)
        days = _bounds("2021-01-01", "2021-12-31")
        if len(days) != EXPECTED_WEEKDAY_PAIRS or len(OFFICIAL_FINAL_2021) != 13:
            raise OfflinePrivateAuditError("2021_CALENDAR_SCOPE_DRIFT")
        fingerprints = []
        empty = set()
        for day in days:
            observed = _check_one(root, day)
            digest = observed.get("pair_sha256")
            count = observed.get("daily_rows")
            cls = observed.get("source_day_class")
            if (observed.get("day") != day or type(digest) is not str
                    or not SHA.fullmatch(digest) or type(count) is not int
                    or count < 0):
                raise OfflinePrivateAuditError("PRIVATE_DATE_RECEIPT_INTEGRITY_INVALID")
            if (count == 0 and cls not in (
                    "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
                    "PROVIDER_BOTH_EMPTY_UNVERIFIED_CALENDAR_OR_SOURCE_GAP")):
                raise OfflinePrivateAuditError("PRIVATE_EMPTY_DAY_SHAPE_INVALID")
            if count > 0 and cls != "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED":
                raise OfflinePrivateAuditError("PRIVATE_ACTIVE_DAY_SHAPE_INVALID")
            fingerprints.append({"day": day, "pair_sha256": digest})
            if count == 0:
                empty.add(day)
        panel_sha = hashlib.sha256(json.dumps(
            fingerprints, sort_keys=True, separators=(",",":")
        ).encode("utf-8")).hexdigest()
        if panel_sha != EXISTING_2021_PANEL_SHA256:
            raise OfflinePrivateAuditError("PRIVATE_2021_PANEL_SHA_DRIFT")
        out["original_pairs_reverified"] = len(fingerprints)
        out["original_panel_sha256_matches_prior_audit"] = True
        out["empty_daily_original_pairs_total"] = len(empty)
        out["empty_daily_original_pairs_at_expected_holidays"] = len(
            empty & OFFICIAL_FINAL_2021)
        out["empty_daily_original_pairs_on_other_weekdays"] = len(
            empty - OFFICIAL_FINAL_2021)
        out["expected_holidays_with_nonempty_daily_rows"] = len(
            OFFICIAL_FINAL_2021 - empty)
        # Critical: a date-set match is a *private provider response check*.
        # It is NOT independently authenticated KRX calendar / public-as-of
        # publication, and cannot promote PIT or executable stock prices.
        if empty == OFFICIAL_FINAL_2021:
            out["status"] = "PRIVATE_2021_DATE_SET_SHAPE_MATCH_NOT_PIT"
        else:
            out["status"] = "PRIVATE_2021_DATE_SET_DISCREPANCY_NOT_PIT"
    except (OfflinePrivateAuditError, OSError, ValueError, TypeError):
        # Do not disclose private filenames, hashes, failed dates or provider
        # exception messages. A failure never makes an admissible result.
        out = _base()
        out["status"] = "FAIL_CLOSED_PRIVATE_2021_SOURCE_UNVERIFIED"
    return out


if __name__ == "__main__":
    cmd = argparse.ArgumentParser()
    cmd.add_argument("--audit", action="store_true")
    opts = cmd.parse_args()
    report = review_private_2021(execute=opts.audit)
    print("INDEXALERT_KRX_2021_DATE_SET_REVIEW=" +
          json.dumps(report, sort_keys=True), flush=True)
    if opts.audit and report["status"] != "PRIVATE_2021_DATE_SET_SHAPE_MATCH_NOT_PIT":
        raise SystemExit(1)
