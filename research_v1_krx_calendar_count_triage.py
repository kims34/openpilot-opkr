"""Strictly offline annual KRX exchange-closure count *triage*, not PIT.

Reference annual counts from a third-party calendar are diagnostic only.
An annual count equality does not imply equality of the actual closed dates,
provider contents, official original source, security state or availability.

No KRX request, no privileged source reads, no broker imports.
"""
from __future__ import annotations
from datetime import date

# Non-authoritative public news-supported EXCEPTIONS to the secondary
# exchange_calendars/XKRX 4.13.1 calendar for the pinned 2026 private
# Jan01-Oct08 source snapshot. This is NOT a KRX original holiday notice.
NEWS_SUPPORTED_EXTRA_2026_DATES = frozenset({
    date(2026, 6, 3), date(2026, 7, 17),
})

FLAGS = {
    "date_level_original_krx_calendar_attested": False,
    "source_pairs_at_date_level_reconciled": False,
    "security_tradability_verified": False,
    "27_problem_securities_released": False,
    "pit_admitted": False,
    "performance_authorized": False,
    "holdout_authorized": False,
    "orders_authorized": False,
    "ordering": "DISABLED",
}


def _validate_counts(data):
    if not isinstance(data, dict) or set(data) != set(range(2015, 2027)):
        return False
    return all(type(y) is int and type(n) is int and 0 <= n <= 366
               for y, n in data.items())


def check_aggregate_calendar_candidate(observed, secondary, exception_days):
    result = {
        "status": "INVALID_REFERENCE_FAIL_CLOSED",
        "classification": "ANNUAL_COUNT_ONLY_NOT_CALENDAR_PIT_PROOF",
        "exact_secondary_match_years": [],
        "annual_mismatch_years_before_exceptions": [],
        "annual_mismatch_years_after_exceptions": [],
        "observed_unverified_gap_day_total": None,
        "secondary_closed_day_total": None,
        "exception_count": None,
        "net_count_difference_after_exceptions": None,
        **FLAGS,
    }
    if not _validate_counts(observed) or not _validate_counts(secondary):
        return result
    if (not isinstance(exception_days, list) or len(exception_days) > 10
            or any(type(s) is not str for s in exception_days)
            or len(set(exception_days)) != len(exception_days)):
        return result
    parsed = []
    for day in exception_days:
        try:
            d = date.fromisoformat(day)
        except (TypeError, ValueError):
            return result
        if (d.isoformat() != day or d.weekday() >= 5 or d.year != 2026
                or not (date(2026, 1, 1) <= d <= date(2026, 10, 8))):
            return result
        if d not in NEWS_SUPPORTED_EXTRA_2026_DATES:
            # Never make any arbitrary 2026 weekday masquerade as one of
            # the two independently reported extraordinary market closings.
            # Counting is diagnostic only; no public source is admitted.
            return result
        parsed.append(d)
    matches = [y for y in sorted(observed) if observed[y] == secondary[y]]
    mismatches = [y for y in sorted(observed) if observed[y] != secondary[y]]
    adjusted = {y: secondary[y] + (len(parsed) if y == 2026 else 0)
                for y in observed}
    remained = [y for y in sorted(observed) if observed[y] != adjusted[y]]
    result.update({
        "status": ("COUNT_EQUALITY_TRIAGE_ONLY_NOT_DATE_ATTESTED" if not remained
                   else "AGGREGATE_DISCREPANCIES_REMAIN_PIT_BLOCKED"),
        "exact_secondary_match_years": matches,
        "annual_mismatch_years_before_exceptions": mismatches,
        "annual_mismatch_years_after_exceptions": remained,
        "observed_unverified_gap_day_total": sum(observed.values()),
        "secondary_closed_day_total": sum(secondary.values()),
        "exception_count": len(parsed),
        "net_count_difference_after_exceptions": sum(observed.values()) - sum(adjusted.values()),
    })
    return result
