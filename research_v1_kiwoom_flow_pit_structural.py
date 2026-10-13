"""Strict *structural* PIT audit for Kiwoom ka10059 candidate records.

This never authenticates an historical release or admits the dataset. In
particular, KRX's 20:00 KST final-publication floor is NOT transferable to an
undocumented broker release. A source-provided timestamp or hash by itself
cannot prove what was published in the past.
"""
from __future__ import annotations

from datetime import datetime, date, time, timezone
from zoneinfo import ZoneInfo
from typing import Any, Mapping, Sequence
import re

KST = ZoneInfo("Asia/Seoul")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ISIN = re.compile(r"^KR[0-9A-Z]{10}$")
SYMBOL = re.compile(r"^[0-9]{6}$")
VENUES = frozenset(("KRX", "NXT", "SOR"))
SOURCE = "KIWOOM_REST_KA10059"
REQUIRED = (
    "source", "isin", "symbol", "venue", "event_date",
    "published_at", "available_at", "ingested_at", "decision_at",
    "response_sha256",
)


class KiwoomFlowPITError(ValueError):
    """Reject structurally invalid timestamps or ambiguous identities."""


def _timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise KiwoomFlowPITError(f"{label}: timestamp string required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise KiwoomFlowPITError(f"{label}: invalid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise KiwoomFlowPITError(f"{label}: explicit UTC offset required")
    return parsed.astimezone(timezone.utc)


def _date(value: Any) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise KiwoomFlowPITError("event_date must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise KiwoomFlowPITError("invalid event_date") from exc


def audit_candidate_pit(rows: Sequence[Mapping[str, Any]] | None) -> dict[str, Any]:
    """Audit *only* supplied structural assertions; never authorize PIT usage.

    Requires one record per known (ISIN, venue, date). Does not invent
    delisted/zero-flow observations, a market calendar, a missing timestamp or
    backdated provenance. Exact historical release verification remains
    external and independently required.
    """
    if not isinstance(rows, (tuple, list)) or not rows:
        raise KiwoomFlowPITError("nonempty candidate records required")
    seen = set()
    earliest, latest = None, None
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise KiwoomFlowPITError(f"record {index}: mapping required")
        missing = [key for key in REQUIRED if key not in row]
        if missing:
            raise KiwoomFlowPITError(f"record {index}: missing required fields {missing}")
        if row["source"] != SOURCE:
            raise KiwoomFlowPITError(f"record {index}: source mismatch")
        if not isinstance(row["isin"], str) or not ISIN.fullmatch(row["isin"]):
            raise KiwoomFlowPITError(f"record {index}: official issue-id format missing")
        if not isinstance(row["symbol"], str) or not SYMBOL.fullmatch(row["symbol"]):
            raise KiwoomFlowPITError(f"record {index}: symbol format invalid")
        if not isinstance(row["venue"], str) or row["venue"] not in VENUES:
            raise KiwoomFlowPITError(f"record {index}: exchange/venue unknown")
        digest = row["response_sha256"]
        if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
            raise KiwoomFlowPITError(f"record {index}: response digest missing")
        event = _date(row["event_date"])
        observed = tuple(_timestamp(row[key], key) for key in
            ("published_at", "available_at", "ingested_at", "decision_at"))
        published, available, ingested, decision = observed
        event_open = datetime.combine(event, time.min, tzinfo=KST).astimezone(timezone.utc)
        if not (event_open <= published <= available <= ingested):
            raise KiwoomFlowPITError(
                f"record {index}: event/publication/availability/ingestion chronology invalid"
            )
        if available > decision:
            raise KiwoomFlowPITError(f"record {index}: lookahead: data not available at decision")
        key = (row["isin"], row["venue"], event)
        if key in seen:
            raise KiwoomFlowPITError(f"record {index}: duplicated issue/venue/day")
        seen.add(key)
        earliest = min(earliest, event) if earliest else event
        latest = max(latest, event) if latest else event
    return {
        "source": SOURCE,
        "candidate_rows": len(rows),
        "earliest_event_date": earliest.isoformat(),
        "latest_event_date": latest.isoformat(),
        "structural_asof_timeline_valid": True,
        "published_original_vintage_independently_verified": False,
        "full_universe_historical_coverage_verified": False,
        "broker_publication_time_contract_verified": False,
        "source_admitted": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "interpretation": (
            "Structural as-of alignment is necessary, NOT historical PIT evidence. "
            "Independently archived source vintages, official identities/coverage, "
            "venue, exact unit semantics, licence and availability proof are absent."
        ),
    }
