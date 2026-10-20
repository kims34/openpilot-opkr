"""Offline original-vs-correction date-only as-of vintage gate for Frozen M20.

Reconciles a privately supplied original-filing receipt day, later corrected
filing receipt day and an independently verified historical session calendar.
The correction's existence is already established by independent official
source-only census. NO actual filing dates, issuer, receipt IDs, financial
values, calendar or current normalized financial API are embedded in code or
persisted in output. Same receipt/correction day is NEVER tradable on its
date-only metadata; post-correction sessions may only consider corrected
edition, not retroactively assign it to original's historical sessions.

This gate returns ONLY a *possible edition-date category*; it cannot certify
the vintage's financial cells, publication, initial tradability or strategy PIT.
"""
from __future__ import annotations

from datetime import timedelta
import json
from pathlib import Path

from research_v1_m20_dart_receipt_date_floor import (
    parse_day, source_date_floor, ReceiptDateGap,
)

OUT = Path("research_results/m20_original_correction_asof_floor/contract.json")
MAX_RELATIVE_CORRECTION_YEARS = 7
BLOCKED = {
    "original_2022_q3_three_month_cfs_value_verified": False,
    "original_2021_comparator_three_month_cfs_value_verified": False,
    "correction_2022_q3_financial_cell_change_verified": False,
    "first_publication_instant_verified": False,
    "historical_original_and_correction_publication_days_verified": False,
    "historical_issuer_security_pit_verified": False,
    "m20_feature_pit_admitted": False,
    "m20_performance_run_authorized": False,
    "independent_holdout_authorized": False,
    "champion_change_authorized": False,
    "real_orders_authorized": False,
    "funds_movement_authorized": False,
    "permissions_change_authorized": False,
    "input_dates_issuer_receipts_calendar_values_or_company_saved": False,
    "ordering": "DISABLED",
}


class EditionFloorGap(ValueError):
    """Non-identifying error category only."""


def edition_date_floor(
    *,
    original_receipt_day: str,
    correction_receipt_day: str,
    trade_session_day: str,
    official_historical_sessions: list[str],
    original_first_filing_verified: bool,
    later_correction_receipt_verified: bool,
    correction_index_complete_for_window: bool,
    calendar_official_historical_pit_verified: bool,
) -> dict:
    """Determine only whether the original or later edition could be dated.

    Acceptance as a historical financial feature is unconditionally false.
    """
    for value in (original_first_filing_verified,
                  later_correction_receipt_verified,
                  correction_index_complete_for_window,
                  calendar_official_historical_pit_verified):
        if type(value) is not bool:
            raise EditionFloorGap("EDITION_ATTESTATION_TYPE_INVALID")
    try:
        orig = parse_day(original_receipt_day)
        corrected = parse_day(correction_receipt_day)
        decision = parse_day(trade_session_day)
    except ReceiptDateGap as e:
        raise EditionFloorGap("EDITION_DAY_SHAPE_INVALID") from None
    if not orig < corrected <= orig + timedelta(days=366*MAX_RELATIVE_CORRECTION_YEARS):
        raise EditionFloorGap("EDITION_DATE_ORDER_OR_SCOPE_INVALID")

    # Same trusted historical-calendar rule is used independently for BOTH
    # filings, preventing accidental use of next-year revised data in an
    # earlier simulated session.
    try:
        first = source_date_floor(
            original_receipt_day, trade_session_day,
            official_historical_sessions,
            first_receipt_verified=original_first_filing_verified,
            calendar_official_historical_pit_verified=calendar_official_historical_pit_verified,
        )
    except ReceiptDateGap as e:
        raise EditionFloorGap("ORIGINAL_DATE_FLOOR_OR_CALENDAR_INVALID") from None

    # A decision before correction or many years before its day is not a
    # corrected-edition candidate. The base floor has a bounded horizon;
    # apply it for an actual later decision, never for pre-correction dates.
    corrected_candidate = False
    if decision > corrected:
        try:
            later = source_date_floor(
                correction_receipt_day, trade_session_day,
                official_historical_sessions,
                first_receipt_verified=later_correction_receipt_verified,
                calendar_official_historical_pit_verified=calendar_official_historical_pit_verified,
            )
        except ReceiptDateGap as e:
            raise EditionFloorGap("CORRECTION_DATE_FLOOR_OR_CALENDAR_INVALID") from None
        corrected_candidate = later["after_receipt_trading_session_candidate"]

    provenance = (original_first_filing_verified
                  and later_correction_receipt_verified
                  and correction_index_complete_for_window
                  and calendar_official_historical_pit_verified)
    orig_candidate = (
        provenance and orig < decision < corrected
        and first["after_receipt_trading_session_candidate"]
    )
    corrected_candidate = provenance and corrected_candidate

    # No reliance on receipt-number decimal ordering or same-day release
    # timing. An unverified correction chain gives no eligible edition.
    if decision <= orig:
        state = "ON_OR_BEFORE_FIRST_RECEIPT_REJECTED"
    elif decision == corrected:
        state = "CORRECTION_RECEIPT_DAY_REJECTED"
    elif not provenance:
        state = "EDITION_CALENDAR_OR_LINEAGE_UNATTESTED"
    elif orig_candidate:
        state = "ORIGINAL_EDITION_DATE_SCOPE_CANDIDATE_ONLY"
    elif corrected_candidate:
        state = "CORRECTED_EDITION_DATE_SCOPE_CANDIDATE_ONLY"
    else:
        state = "NO_ELIGIBLE_ATTESTED_SESSION"

    return {
        "date_only_edition_scope": state,
        "original_edition_date_scope_candidate": bool(orig_candidate),
        "corrected_edition_date_scope_candidate": bool(corrected_candidate),
        "correction_and_original_never_coeligible": not (
            orig_candidate and corrected_candidate
        ),
        "same_day_receipt_or_correction_never_assumed_pretrade_available": True,
        "later_corrected_values_never_assigned_pre_correction": True,
        "original_source_financial_data_not_certified_by_date_scope": True,
        "source_first_public_availability_verified": False,
        "m20_feature_pit_admitted": False,
        "m20_performance_run_authorized": False,
        "real_orders_authorized": False,
        "ordering": "DISABLED",
    }


def dry_run() -> dict:
    """Entirely synthetic dates; no actual source or official calendar."""
    original = edition_date_floor(
        original_receipt_day="20221014",
        correction_receipt_day="20231214",
        trade_session_day="20221017",
        official_historical_sessions=["20221013", "20221014", "20221017"],
        original_first_filing_verified=True,
        later_correction_receipt_verified=True,
        correction_index_complete_for_window=True,
        calendar_official_historical_pit_verified=True,
    )
    corrected = edition_date_floor(
        original_receipt_day="20221014",
        correction_receipt_day="20231214",
        trade_session_day="20231215",
        official_historical_sessions=["20231214", "20231215"],
        original_first_filing_verified=True,
        later_correction_receipt_verified=True,
        correction_index_complete_for_window=True,
        calendar_official_historical_pit_verified=True,
    )
    if (not original["original_edition_date_scope_candidate"]
        or original["corrected_edition_date_scope_candidate"]
        or corrected["original_edition_date_scope_candidate"]
        or not corrected["corrected_edition_date_scope_candidate"]):
        raise EditionFloorGap("SYNTHETIC_EDITION_SCOPE_RULE_INVALID")
    result = {
        "purpose": "FIXED_M20_ORIGINAL_CORRECTED_DATE_ONLY_ASOF_VINTAGE_GATE",
        "source_status": "SYNTHETIC_TWO_EDITION_DATE_SCOPE_ONLY_NOT_SOURCE",
        "synthetic_original_window_test_passed": True,
        "synthetic_correction_window_test_passed": True,
        "same_day_original_and_correction_trading_is_disallowed": True,
        "separately_attested_calendar_required": True,
        "separately_attested_full_correction_history_required": True,
        "feature_value_from_current_corrected_api_never_backfilled": True,
        **BLOCKED,
    }
    return result


if __name__ == "__main__":
    report = dry_run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
    print("M20_ORIGINAL_CORRECTION_ASOF_FLOOR=" + json.dumps(report, sort_keys=True))
