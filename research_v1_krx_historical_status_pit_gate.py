"""KRX historical halt/delist PIT evidence preflight, offline fail closed.

Only synthetic or already authorized metadata may enter. This code neither
fetches original KRX documents nor authenticates their alleged origin. It
NEVER removes the 27-security quarantine, admits backtest data, or orders.
Input contains no original security codes/names or raw market prices.

Times must be explicit Korea local timestamps. Status intervals are
[start, end). Missing end means continuing status, not proof of duration.
A historic tradeable-state assertion is NOT proof of complete positive
tradeability without all other overlapping official events and fills.
"""
from __future__ import annotations
from datetime import datetime, timedelta
import re

_SHA = re.compile(r"^[0-9a-f]{64}$")
_KST_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+09:00$")
_KST_OFFSET = timedelta(hours=9)
_STATUSES = frozenset({"TRADABLE", "HALTED", "CLEANUP", "DELISTED"})
_BAD = frozenset({"HALTED", "CLEANUP", "DELISTED"})


def _sha(s):
    return isinstance(s, str) and bool(_SHA.fullmatch(s))


def _time(v):
    if not isinstance(v, str) or not _KST_TIME.fullmatch(v):
        raise ValueError("NONCANONICAL_KST")
    d = datetime.fromisoformat(v)
    if d.utcoffset() != _KST_OFFSET or d.isoformat(timespec="seconds") != v:
        raise ValueError("NONCANONICAL_KST")
    return d


def assess_historical_status_candidate(events, decision_at_kst):
    """Classify evidence integrity/temporal blockers, never grant trade authority.

    Required claims: episode_sha256, record_sha256, source_document_sha256,
    source_kind, status, effective_start_kst, effective_end_kst (or None),
    originally_published_at_kst, observed_available_at_kst, retrieved_at_kst.

    These are *claims* until verified against original independently dated
    KRX records. A current web snapshot cannot testify to earlier years.
    """
    out = {
        "classification": "HISTORICAL_KRX_STATUS_PIT_CANDIDATE_ONLY",
        "status": "FAIL_CLOSED_INVALID_EVIDENCE",
        "examined_records": 0,
        "time_order_invalid": 0,
        "current_or_unknown_source_rejected": 0,
        "future_publication_or_availability": 0,
        "retrospective_retrieval_not_attested": 0,
        "active_danger_state_count": 0,
        "active_positive_candidate_count": 0,
        "overlapping_conflict_count": 0,
        "independent_source_archive_verified": False,
        "complete_historical_episodes_verified": False,
        "27_quarantined_securities_released": 0,
        "pit_admitted": False,
        "profitability_run_authorized": False,
        "independent_holdout_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "ordering": "DISABLED",
        "network_requests_made": False,
    }
    try:
        decision = _time(decision_at_kst)
    except (TypeError, ValueError):
        return out
    if not isinstance(events, list) or not events or len(events) > 1000:
        return out
    observed = set()
    episode = None
    valid = []
    for row in events:
        if not isinstance(row, dict):
            return out
        if any(not _sha(row.get(k)) for k in (
            "episode_sha256", "record_sha256", "source_document_sha256",
        )):
            return out
        if row["record_sha256"] in observed:
            return out
        observed.add(row["record_sha256"])
        if episode is None:
            episode = row["episode_sha256"]
        if episode != row["episode_sha256"] or row.get("status") not in _STATUSES:
            return out
        try:
            start = _time(row.get("effective_start_kst"))
            end = _time(row["effective_end_kst"]) if row.get("effective_end_kst") is not None else None
            published = _time(row.get("originally_published_at_kst"))
            available = _time(row.get("observed_available_at_kst"))
            retrieved = _time(row.get("retrieved_at_kst"))
        except (ValueError, TypeError):
            return out
        if end is not None and end <= start:
            return out
        if published > available or available > retrieved:
            out["time_order_invalid"] += 1
        if row.get("source_kind") != "KRX_ORIGINAL_HISTORICAL_STATUS_ARCHIVE":
            out["current_or_unknown_source_rejected"] += 1
        if published > decision or available > decision:
            out["future_publication_or_availability"] += 1
        if retrieved > decision:
            out["retrospective_retrieval_not_attested"] += 1
        if start <= decision and (end is None or decision < end):
            valid.append(row["status"])
    out["examined_records"] = len(events)
    out["active_danger_state_count"] = sum(x in _BAD for x in valid)
    out["active_positive_candidate_count"] = valid.count("TRADABLE")
    out["overlapping_conflict_count"] = int(bool(
        out["active_danger_state_count"] and out["active_positive_candidate_count"]
    ))
    out["status"] = (
        "INCONSISTENT_OR_UNTIMELY_STATUS_EVIDENCE_BLOCKED" if (
            out["time_order_invalid"] or out["current_or_unknown_source_rejected"]
            or out["future_publication_or_availability"]
            or out["overlapping_conflict_count"]
        ) else "UNATTESTED_HISTORICAL_STATUS_CANDIDATES_BLOCKED"
    )
    return out
