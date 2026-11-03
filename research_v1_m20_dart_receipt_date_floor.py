"""Offline-only DART rcept_dt source-date PIT floor contract for Frozen M20.

OpenDART's documented rcept_dt is an 8-digit receipt DAY, not a verified
intraday public-release timestamp or a verified original CFS numeric fact.

This intentionally does NOT use a weekend/holiday guess or fetch any market,
DART, original report, broker, account or holdout data. An independently
attested ordered *official market session calendar* must be supplied and
verified elsewhere. The earliest AFTER-receipt session is ONLY a conservative
candidate, not a sufficient PIT proof, especially if original publication
availability or amendment-specific version timing is unknown.

All output is non-identifying categorical evidence. This function cannot
admit M20 features, authorize performance, open holdout or enable orders.
"""
from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path
import re

OUT = Path("research_results/m20_dart_receipt_date_floor/contract.json")
MAX_SESSIONS = 600
MAX_LOOKAHEAD_DAYS = 366
DAY = re.compile(r"[0-9]{8}\Z")

FROZEN = {
    "source_accounting_cfs_original_values_pit_verified": False,
    "source_first_public_release_instant_verified": False,
    "source_first_public_release_day_verified": False,
    "source_correction_vintage_complete": False,
    "historical_security_issuer_pit_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "source_dates_times_calendar_or_identifiers_persisted": False,
    "ordering": "DISABLED",
}

class ReceiptDateGap(ValueError):
    """Only known non-source-revealing error codes are returned."""


def parse_day(value: str) -> date:
    """Never silently accept timestamps as dates or synthesize filing time."""
    if type(value) is not str or not DAY.fullmatch(value):
        raise ReceiptDateGap("DATE_ONLY_YYYYMMDD_REQUIRED")
    try:
        actual = date(int(value[:4]), int(value[4:6]), int(value[6:8]))
    except ValueError:
        raise ReceiptDateGap("INVALID_CALENDAR_DATE") from None
    if not 2000 <= actual.year <= 2100:
        raise ReceiptDateGap("RECEIPT_YEAR_OUTSIDE_CONTRACT")
    return actual


def source_date_floor(receipt_date: str, observed_trade_day: str,
                      official_session_days: list[str],
                      *,
                      first_receipt_verified: bool,
                      calendar_official_historical_pit_verified: bool) -> dict:
    """Check ONLY candidate session timing; NO archival or financial admission.

    When genuine official calendar and first-filing metadata have been
    independently attested, days STRICTLY after the reported receipt date
    can be considered further for a separate full publication/source gate.
    The result never certifies disclosure publication or usable financial data.
    """
    receipt = parse_day(receipt_date)
    day = parse_day(observed_trade_day)
    if (type(first_receipt_verified) is not bool
        or type(calendar_official_historical_pit_verified) is not bool):
        raise ReceiptDateGap("SOURCE_ATTESTATIONS_MUST_BE_BOOLEAN")
    if (type(official_session_days) is not list
            or len(official_session_days) == 0
            or len(official_session_days) > MAX_SESSIONS):
        raise ReceiptDateGap("TRADING_CALENDAR_MISSING_OR_UNBOUNDED")
    sessions = [parse_day(x) for x in official_session_days]
    if (len(set(sessions)) != len(sessions)
            or any(x >= y for x,y in zip(sessions,sessions[1:]))):
        raise ReceiptDateGap("TRADING_CALENDAR_NOT_STRICTLY_ORDERED")
    if not (receipt - timedelta(days=MAX_LOOKAHEAD_DAYS) <= day
            <= receipt + timedelta(days=MAX_LOOKAHEAD_DAYS)):
        raise ReceiptDateGap("TRADE_DAY_OUTSIDE_SOURCE_TEST_HORIZON")
    if not first_receipt_verified:
        return {
            "source_date_gate_status": "FIRST_ORIGINAL_FILING_RECEIPT_NOT_ATTESTED",
            "trade_day_on_official_calendar": False,
            "receipt_day_or_earlier_rejected": day <= receipt,
            "after_receipt_trading_session_candidate": False,
            "source_public_availability_verified": False,
            "date_floor_does_not_admit_accounting_or_pit": True,
        }
    if not calendar_official_historical_pit_verified:
        return {
            "source_date_gate_status": "HISTORICAL_OFFICIAL_TRADING_CALENDAR_NOT_ATTESTED",
            "trade_day_on_official_calendar": False,
            "receipt_day_or_earlier_rejected": day <= receipt,
            "after_receipt_trading_session_candidate": False,
            "source_public_availability_verified": False,
            "date_floor_does_not_admit_accounting_or_pit": True,
        }
    # An explicit trusted source is required: never infer business days
    # from weekdays, holidays, today, nearest session or timezone offsets.
    on_calendar = day in sessions
    after = day > receipt and on_calendar
    return {
        "source_date_gate_status": (
            "AFTER_RECEIPT_TRADING_SESSION_CANDIDATE_ONLY" if after
            else "NO_ELIGIBLE_AFTER_RECEIPT_TRADING_SESSION"
        ),
        "trade_day_on_official_calendar": on_calendar,
        "receipt_day_or_earlier_rejected": day <= receipt,
        "after_receipt_trading_session_candidate": after,
        "source_public_availability_verified": False,
        "date_floor_does_not_admit_accounting_or_pit": True,
    }


def dry_run() -> dict:
    """Synthetic fixture only; none of the dates below is an actual filing."""
    tested = source_date_floor(
        "20221014", "20221017", ["20221013","20221014","20221017"],
        first_receipt_verified=True,
        calendar_official_historical_pit_verified=True,
    )
    if (tested["source_date_gate_status"]
            != "AFTER_RECEIPT_TRADING_SESSION_CANDIDATE_ONLY"
            or not tested["after_receipt_trading_session_candidate"]):
        raise ReceiptDateGap("SYNTHETIC_EXAMPLE_GATE_CHANGED")
    # No invented official attestation, dates or issuer details saved to output.
    return {
        "purpose": "DART_DATE_ONLY_RECEIPT_CONSERVATIVE_TRADING_DAY_CANDIDATE_CONTRACT",
        "source_status": "SYNTHETIC_OFFLINE_RULES_ONLY_NO_SOURCE_OR_PIT",
        "official_opendart_rcept_dt_is_date_only": True,
        "same_day_trading_from_rcept_dt_is_prohibited": True,
        "no_calendar_weekday_or_holiday_inference": True,
        "original_financial_fact_or_publication_availability_from_date_only": False,
        "synthetic_rule_self_test_success": True,
        **FROZEN,
    }


if __name__ == "__main__":
    report = dry_run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_DART_RCEPT_DT_FLOOR=" + json.dumps(report, sort_keys=True))
