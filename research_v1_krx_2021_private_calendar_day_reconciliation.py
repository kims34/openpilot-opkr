"""KRX 2021 date-by-date *private* history vs retrospectively published holidays.

No provider or brokerage calls, no network, no private source mutation. When
deployed separately by an authorized operator on the existing dedicated
Railway KRX Historical Worker, checks each of the 261 SHA-audited original
weekday pairs against the full contemporaneous 2021 KRX market holiday list.
The public result never contains original dates/rows/security IDs/hashes.
A successful retrospective market-wide date match is never security
tradability, market-data available-at PIT, economics or real-order authority.

No private volume is available in GitHub Actions; tests only mock receipts.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Callable, Mapping

from research_v1_krx_openapi_private_integrity_audit import (
    OfflinePrivateAuditError, _bounds, _check_one, _trusted_private_root,
)
from research_v1_krx_openapi_private_history_batch import PRIVATE_SUBDIR, WORKER

# Original KRX 2021 calendar published December 2020, pre-vintage revision.
KRX_INITIAL_2021_CLOSED = frozenset((
    "20210101", "20210211", "20210212", "20210301", "20210505",
    "20210519", "20210920", "20210921", "20210922", "20211231",
))
# Announced by KRX 2021-08-04; none is a previously published original
# holiday. Do not retrospectively impute availability before the notice.
KRX_REVISED_2021_CLOSED = frozenset((
    "20210816", "20211004", "20211011",
))
EXPECTED_CLOSED = KRX_INITIAL_2021_CLOSED | KRX_REVISED_2021_CLOSED
SOURCE_SNAPSHOT_SHA256 = (
    "362716e7bb5e025a9dcd39207b1ee095d97c633b8ca907722c766edf799ec2a1"
)
EXPECTED_WEEKDAYS = 261
EXPECTED_UNKNOWN = 13
NONEMPTY = "NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED"
SHA = re.compile("[0-9a-f]{64}\\Z")
SAFE = {
    "source_original_publication_pit_verified": False,
    "2021_exchange_calendar_pit_admitted": False,
    "individual_security_tradability_verified": False,
    "halt_delist_corporate_actions_verified": False,
    "full_universe_source_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "network_request_attempted": False,
    "storage_mutated": False,
    "raw_security_rows_or_private_dates_emitted": False,
    "ordering": "DISABLED",
}


# The KRX confirmation of extra market-wide closures was publicly reported
# on 2021-08-04 *after market open*. The exact first exchange publication
# instant has NOT been cryptographically verified. Conservatively, a
# pre-open model must wait until 2021-08-05 to use that confirmation.
KRX_REVISION_FIRST_SAFE_PREOPEN_DAY = date(2021, 8, 5)


def strict_krx_2021_calendar_preopen_reference(decision_day: str) -> dict:
    """Historical exchange ANNOUNCEMENT knowledge only; never trading PIT.

    A final revised 2021 market holiday table is NOT a point-in-time safe
    reference for a strategy decision before the 2021-08-04 KRX notice.
    The initial 10-day schedule remains the safe announcement reference
    at and before the 2021-08-04 market open. Public reporting of the
    KRX market notice happened that afternoon, so on the following day
    the post-revision 13-day reference is conservatively usable.
    """
    if type(decision_day) is not str or not re.fullmatch(
        r"2021-\d{2}-\d{2}", decision_day
    ):
        raise OfflinePrivateAuditError("KRX_2021_PREOPEN_DATE_INVALID")
    try:
        on = date.fromisoformat(decision_day)
    except ValueError:
        raise OfflinePrivateAuditError("KRX_2021_PREOPEN_DATE_INVALID") from None
    if on.year != 2021:
        raise OfflinePrivateAuditError("KRX_2021_PREOPEN_DATE_INVALID")
    after_announcement = on >= KRX_REVISION_FIRST_SAFE_PREOPEN_DAY
    return {
        "reference_vintage": (
            "KRX_2021_REVISED_NOTICE_CONSERVATIVE_NEXT_DAY"
            if after_announcement else "KRX_2021_INITIAL_MARKET_CALENDAR"
        ),
        "reference_market_closure_count": (
            len(EXPECTED_CLOSED) if after_announcement
            else len(KRX_INITIAL_2021_CLOSED)
        ),
        "extra_2021_exchange_closures_from_later_notice_usable_preopen":
            3 if after_announcement else 0,
        "krx_notice_day": "2021-08-04",
        "first_conservative_preopen_for_revised_reference": "2021-08-05",
        "official_exchange_publication_instant_verified": False,
        "official_asof_market_calendar_source_admitted": False,
        "individual_security_tradability_verified": False,
        "historical_source_publication_pit_verified": False,
        "m20_performance_run_authorized": False,
        "independent_holdout_authorized": False,
        "live_orders_authorized": False,
        "network_request_attempted": False,
        "ordering": "DISABLED",
    }


def _base() -> dict:
    return {
        "purpose": "2021_KRX_DATED_CALENDAR_PRIVATE_ORIGINAL_SOURCE_READONLY_NOT_PIT",
        "status": "DRY_RUN_PRIVATE_STORAGE_UNTOUCHED",
        "baseline_historical_2021_weekday_pairs": EXPECTED_WEEKDAYS,
        "baseline_historical_2021_unknown_calendar_days": EXPECTED_UNKNOWN,
        "initial_announced_2021_exchange_closed_dates": 10,
        "later_announced_2021_exchange_closed_dates": 3,
        "2021_later_announcement_publication_date": "2021-08-04",
        "expected_final_2021_exchange_closed_dates": len(EXPECTED_CLOSED),
        "original_pair_fingerprint_matched": False,
        "private_original_2021_weekday_pairs_verified": 0,
        "original_source_empty_days_count": 0,
        "expected_closures_missing_from_source_empty_days_count": 0,
        "unexpected_source_empty_days_count": 0,
        "source_date_by_date_retrospective_calendar_match": False,
        **SAFE,
    }


def _source_rows_match_expected_calendar(rows: list[dict]) -> dict:
    """Fail closed on any 261-day / SHA / daily-empty contradiction.

    Input is *only* validated per-day digest and source-row metadata from
    existing _check_one; neither original issuer codes nor prices are accepted.
    A lexical SHA is never accepted as authentication without a separately
    independently audited, fixed 2021 aggregate snapshot fingerprint.
    """
    out = _base()
    expected_days = _bounds("2021-01-01", "2021-12-31")
    if (type(rows) is not list or len(rows) != EXPECTED_WEEKDAYS
            or len(expected_days) != EXPECTED_WEEKDAYS
            or len(EXPECTED_CLOSED) != EXPECTED_UNKNOWN):
        out["status"] = "FAIL_CLOSED_2021_EXPECTED_SCOPE"
        return out
    fingerprints = []
    empty_days = set()
    for day, x in zip(expected_days, rows):
        if type(x) is not dict or set(x) != {
            "day", "pair_sha256", "daily_rows", "source_day_class"
        }:
            out["status"] = "FAIL_CLOSED_2021_SOURCE_ROW_SHAPE"
            return out
        if (x["day"] != day or type(x["pair_sha256"]) is not str
                or not SHA.fullmatch(x["pair_sha256"])
                or type(x["daily_rows"]) is not int or x["daily_rows"] < 0):
            out["status"] = "FAIL_CLOSED_2021_SOURCE_ROW_BINDING"
            return out
        empty = x["source_day_class"] != NONEMPTY
        if empty and x["source_day_class"] not in (
            "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
            "PROVIDER_BOTH_EMPTY_UNVERIFIED_CALENDAR_OR_SOURCE_GAP",
        ):
            out["status"] = "FAIL_CLOSED_2021_SOURCE_DAY_CLASS"
            return out
        if empty != (x["daily_rows"] == 0):
            out["status"] = "FAIL_CLOSED_2021_EMPTY_ROW_CONTRADICTION"
            return out
        fingerprints.append({"day": day, "pair_sha256": x["pair_sha256"]})
        if empty:
            empty_days.add(day)
    digest = hashlib.sha256(json.dumps(
        fingerprints, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if digest != SOURCE_SNAPSHOT_SHA256:
        out["status"] = "FAIL_CLOSED_2021_IMMUTABLE_SOURCE_FINGERPRINT_DRIFT"
        return out
    out["original_pair_fingerprint_matched"] = True
    out["private_original_2021_weekday_pairs_verified"] = len(rows)
    out["original_source_empty_days_count"] = len(empty_days)
    # Only public aggregate counts are emitted. Even a failing comparison
    # never logs or returns the private observed dates or source SHA hashes.
    out["expected_closures_missing_from_source_empty_days_count"] = len(
        EXPECTED_CLOSED - empty_days
    )
    out["unexpected_source_empty_days_count"] = len(empty_days - EXPECTED_CLOSED)
    if (len(empty_days) != EXPECTED_UNKNOWN
            or empty_days != EXPECTED_CLOSED):
        out["status"] = "FAIL_CLOSED_2021_DAY_BY_DAY_CALENDAR_MISMATCH"
        return out
    out["status"] = "2021_RETROSPECTIVE_EXCHANGE_CALENDAR_DATES_MATCH_SOURCE_EMPTY_NOT_PIT"
    out["source_date_by_date_retrospective_calendar_match"] = True
    return out


def run(*, audit: bool = False, environment: Mapping[str, str] | None = None,
        check_day: Callable[..., dict] = _check_one,
        verify_root: Callable[[Path], Path] = _trusted_private_root) -> dict:
    out = _base()
    if not audit:
        return out
    env = os.environ if environment is None else environment
    raw_root = env.get("KRX_PRIVATE_RAW_DIR")
    if env.get("RAILWAY_SERVICE_NAME") != WORKER:
        out["status"] = "FAIL_CLOSED_NOT_DEDICATED_KRX_PRIVATE_WORKER"
        return out
    if type(raw_root) is not str or not Path(raw_root).is_relative_to(Path("/data")):
        out["status"] = "FAIL_CLOSED_NOT_ON_PRIVATE_DATA_VOLUME"
        return out
    try:
        root = verify_root(Path(raw_root) / PRIVATE_SUBDIR)
    except Exception:
        # Private store mount verification is not a public data surface.
        # Even unexpected store/helper exceptions (e.g. KeyError,
        # RuntimeError, AttributeError) must never leak private volume paths,
        # original per-day identifiers or underlying exception messages.
        # Match the independent 2021 private reviewer fail-closed behavior.
        out["status"] = "FAIL_CLOSED_PRIVATE_ROOT_NOT_VERIFIED"
        return out
    checked = []
    for day in _bounds("2021-01-01", "2021-12-31"):
        try:
            x = check_day(root, day)
            checked.append({
                "day": x["day"],
                "pair_sha256": x["pair_sha256"],
                "daily_rows": x["daily_rows"],
                "source_day_class": x["source_day_class"],
            })
        except Exception:
            out["status"] = "FAIL_CLOSED_PRIVATE_SOURCE_DAY_INVALID"
            return out
    try:
        return _source_rows_match_expected_calendar(checked)
    except Exception:
        # The reconciler runs only AFTER all 261 original private
        # source pairs have been read. Any unexpected comparison/helper
        # exception can carry private date, path, digest or source-data
        # details: never allow it to escape into Railway public logs.
        out = _base()
        out["status"] = "FAIL_CLOSED_PRIVATE_CALENDAR_COMPARISON_UNVERIFIED"
        return out


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--audit", action="store_true")
    args = p.parse_args()
    report = run(audit=args.audit)
    print("INDEXALERT_KRX_2021_PRIVATE_CALENDAR_VINTAGE=" +
          json.dumps(report, sort_keys=True), flush=True)
    if args.audit and not report["source_date_by_date_retrospective_calendar_match"]:
        raise SystemExit(1)
