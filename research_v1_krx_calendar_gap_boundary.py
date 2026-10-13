"""Offline candidate reconciliation of KRX calendar-vs-source gaps.

Inputs are *already collected metadata receipts*, NEVER new provider requests.
This module does not attest third-party calendar authenticity and never grants
PIT/backtest/holdout/trading authority, even for apparently matched dates.
No raw prices, securities, credentials, network, filesystem or broker imports.
"""
from __future__ import annotations

from datetime import date
import re

SHA_RE = re.compile(r"^[a-f0-9]{64}$")
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
OBSERVATION_STATES = frozenset({"EMPTY", "NONEMPTY"})
SESSION_STATES = frozenset({"OPEN", "CLOSED"})

SAFETY = {
    "official_calendar_independently_attested": False,
    "original_pit_available_at_verified": False,
    "official_halt_delist_status_verified": False,
    "all_historical_security_identifiers_verified": False,
    "source_admitted_for_backtest": False,
    "m20_performance_testing_authorized": False,
    "independent_holdout_authorized": False,
    "real_orders_authorized": False,
    "ordering": "DISABLED",
    "network_requests_attempted": False,
    "private_storage_mutated": False,
    "raw_rows_emitted": False,
}


def _day(value: object) -> bool:
    if not isinstance(value, str) or not DAY_RE.fullmatch(value):
        return False
    try:
        parsed = date.fromisoformat(value)
        return parsed.isoformat() == value and parsed.weekday() < 5
    except ValueError:
        return False


def _sha(value: object) -> bool:
    return isinstance(value, str) and bool(SHA_RE.fullmatch(value))


def reconcile_candidates(observations: list[dict], calendar: list[dict]) -> dict:
    """Compute ONLY provisional date-level consistency counts.

    Each observation: date, response_state, raw_receipt_sha256.
    Each calendar entry: date, session_state, source_kind,
    source_document_sha256. The last two are provenance *claims*, not
    independently checked source documents.

    Missing/contradictory/duplicated evidence is fail-closed, never inferred
    from weekends/holidays or from a provider's empty response.
    """
    output = {
        "classification": "OFFLINE_DECLARATION_CONSISTENCY_ONLY_NOT_ATTESTATION",
        "status": "FAIL_CLOSED_INVALID_OR_INCOMPLETE_INPUT",
        "observed_weekday_receipts": 0,
        "official_calendar_matches_attested": 0,
        "closure_candidates_only": 0,
        "open_response_consistent_candidates_only": 0,
        "possible_open_day_source_gaps": 0,
        "closed_day_response_contradictions": 0,
        "unmatched_or_untrusted_calendar_dates": 0,
        "source_admitted_dates": [],
        **SAFETY,
    }
    if not isinstance(observations, list) or not isinstance(calendar, list):
        return output
    if not observations or len(observations) > 4000 or len(calendar) > 4000:
        return output

    by_observation = {}
    for item in observations:
        if not isinstance(item, dict) or not _day(item.get("date")):
            return output
        if item.get("response_state") not in OBSERVATION_STATES or not _sha(item.get("raw_receipt_sha256")):
            return output
        key = item["date"]
        if key in by_observation:
            return output
        by_observation[key] = item

    by_calendar = {}
    for item in calendar:
        if not isinstance(item, dict) or not _day(item.get("date")):
            return output
        key = item["date"]
        if key in by_calendar or key not in by_observation:
            return output
        # Even a well-formed claim cannot authenticate the document behind it.
        by_calendar[key] = item

    counts = {
        "closure_candidates_only": 0,
        "open_response_consistent_candidates_only": 0,
        "possible_open_day_source_gaps": 0,
        "closed_day_response_contradictions": 0,
        "unmatched_or_untrusted_calendar_dates": 0,
    }
    for key, observed in by_observation.items():
        claimed = by_calendar.get(key)
        if (claimed is None or claimed.get("source_kind") != "KRX_OFFICIAL_EXCHANGE_CALENDAR"
                or claimed.get("session_state") not in SESSION_STATES
                or not _sha(claimed.get("source_document_sha256"))):
            counts["unmatched_or_untrusted_calendar_dates"] += 1
            continue
        status = claimed["session_state"]
        state = observed["response_state"]
        if status == "CLOSED" and state == "EMPTY":
            counts["closure_candidates_only"] += 1
        elif status == "OPEN" and state == "NONEMPTY":
            counts["open_response_consistent_candidates_only"] += 1
        elif status == "OPEN" and state == "EMPTY":
            counts["possible_open_day_source_gaps"] += 1
        else:
            counts["closed_day_response_contradictions"] += 1

    output.update(counts)
    output["observed_weekday_receipts"] = len(by_observation)
    output["status"] = (
        "CANDIDATES_RECORDED_SOURCE_ADMISSION_BLOCKED"
        if not (counts["possible_open_day_source_gaps"]
                or counts["closed_day_response_contradictions"]
                or counts["unmatched_or_untrusted_calendar_dates"])
        else "OPEN_DISCREPANCIES_SOURCE_ADMISSION_BLOCKED"
    )
    return output
