"""Preregistration validator for future live execution-sufficiency criteria.

This module deliberately does NOT choose the numeric thresholds. Its purpose is
to ensure any future empirical execution-sufficiency protocol is explicit,
secret-free, internally coherent, fingerprinted and frozen before the first
LIVE observation it will judge.

A valid protocol is not evidence that execution sufficiency passes. It only
prevents post-hoc threshold selection after observing live outcomes.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Mapping


SCHEMA_VERSION = "1"
REQUIRED_MARKOUT_HORIZONS = frozenset({"5m", "30m", "close"})
_REQUIRED_FIELDS = {
    "schema_version",
    "protocol_id",
    "frozen_at",
    "protocol_document_sha256",
    "minimum_live_observations",
    "minimum_distinct_decision_dates",
    "minimum_filled_observations",
    "minimum_no_fill_observations",
    "minimum_partial_fill_observations",
    "required_markout_horizons",
    "require_slippage_evidence",
    "require_latency_evidence",
    "require_capacity_evidence",
    "require_tail_evidence",
    "rationale",
}
_ALLOWED_FIELDS = set(_REQUIRED_FIELDS)


class ExecutionSufficiencyProtocolError(ValueError):
    """Raised when a proposed execution-sufficiency preregistration is invalid."""


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _text(value: Any, field: str, max_len: int = 2000) -> str:
    text = str(value or "").strip()
    if not text:
        raise ExecutionSufficiencyProtocolError(f"{field} must be non-empty")
    if len(text) > max_len:
        raise ExecutionSufficiencyProtocolError(f"{field} is unexpectedly long")
    return text


def _aware(value: Any, field: str) -> datetime:
    text = _text(value, field, 80)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ExecutionSufficiencyProtocolError(f"{field} must be ISO-8601") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ExecutionSufficiencyProtocolError(f"{field} must be timezone-aware")
    return dt.astimezone(timezone.utc)


def _int(value: Any, field: str, *, minimum: int) -> int:
    if isinstance(value, bool):
        raise ExecutionSufficiencyProtocolError(f"{field} must be an integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ExecutionSufficiencyProtocolError(f"{field} must be an integer") from exc
    if str(value).strip() not in {str(parsed), f"+{parsed}"} and not isinstance(value, int):
        raise ExecutionSufficiencyProtocolError(f"{field} must be an exact integer")
    if parsed < minimum:
        raise ExecutionSufficiencyProtocolError(
            f"{field} must be >= {minimum}"
        )
    return parsed


def _required_true(value: Any, field: str) -> bool:
    if value is not True:
        raise ExecutionSufficiencyProtocolError(f"{field} must be true")
    return True


def validate_execution_sufficiency_protocol(
    protocol: Mapping[str, Any],
    *,
    first_live_recommendation_at: datetime | None = None,
) -> dict[str, Any]:
    """Validate a future empirical execution-sufficiency preregistration.

    If a first LIVE recommendation timestamp already exists, the protocol must
    have been frozen strictly before that timestamp. A protocol frozen after or
    exactly at the first LIVE observation is rejected as post-hoc.
    """
    keys = set(protocol)
    missing = _REQUIRED_FIELDS - keys
    extra = keys - _ALLOWED_FIELDS
    if missing:
        raise ExecutionSufficiencyProtocolError(
            f"protocol missing required fields: {sorted(missing)}"
        )
    if extra:
        raise ExecutionSufficiencyProtocolError(
            f"protocol contains unsupported fields: {sorted(extra)}"
        )

    schema = _text(protocol["schema_version"], "schema_version", 20)
    if schema != SCHEMA_VERSION:
        raise ExecutionSufficiencyProtocolError(
            f"unsupported schema_version: {schema}"
        )
    protocol_id = _text(protocol["protocol_id"], "protocol_id", 200)
    frozen_at = _aware(protocol["frozen_at"], "frozen_at")
    document_sha = _text(
        protocol["protocol_document_sha256"], "protocol_document_sha256", 64
    ).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", document_sha):
        raise ExecutionSufficiencyProtocolError(
            "protocol_document_sha256 must be a 64-character SHA-256 hex string"
        )

    min_live = _int(
        protocol["minimum_live_observations"],
        "minimum_live_observations",
        minimum=1,
    )
    min_dates = _int(
        protocol["minimum_distinct_decision_dates"],
        "minimum_distinct_decision_dates",
        minimum=1,
    )
    min_filled = _int(
        protocol["minimum_filled_observations"],
        "minimum_filled_observations",
        minimum=1,
    )
    min_no_fill = _int(
        protocol["minimum_no_fill_observations"],
        "minimum_no_fill_observations",
        minimum=0,
    )
    min_partial = _int(
        protocol["minimum_partial_fill_observations"],
        "minimum_partial_fill_observations",
        minimum=0,
    )
    if min_dates > min_live:
        raise ExecutionSufficiencyProtocolError(
            "minimum_distinct_decision_dates cannot exceed minimum_live_observations"
        )
    if min_filled > min_live:
        raise ExecutionSufficiencyProtocolError(
            "minimum_filled_observations cannot exceed minimum_live_observations"
        )
    if min_no_fill > min_live:
        raise ExecutionSufficiencyProtocolError(
            "minimum_no_fill_observations cannot exceed minimum_live_observations"
        )
    if min_partial > min_filled:
        raise ExecutionSufficiencyProtocolError(
            "minimum_partial_fill_observations cannot exceed minimum_filled_observations"
        )

    horizons_raw = protocol["required_markout_horizons"]
    if not isinstance(horizons_raw, (list, tuple)):
        raise ExecutionSufficiencyProtocolError(
            "required_markout_horizons must be a list"
        )
    horizons = tuple(str(x).strip().lower() for x in horizons_raw)
    if not horizons or any(not x for x in horizons):
        raise ExecutionSufficiencyProtocolError(
            "required_markout_horizons must not contain empty values"
        )
    if len(set(horizons)) != len(horizons):
        raise ExecutionSufficiencyProtocolError(
            "required_markout_horizons must not contain duplicates"
        )
    if not REQUIRED_MARKOUT_HORIZONS.issubset(set(horizons)):
        raise ExecutionSufficiencyProtocolError(
            "required_markout_horizons must include 5m, 30m and close"
        )

    require_slippage = _required_true(
        protocol["require_slippage_evidence"], "require_slippage_evidence"
    )
    require_latency = _required_true(
        protocol["require_latency_evidence"], "require_latency_evidence"
    )
    require_capacity = _required_true(
        protocol["require_capacity_evidence"], "require_capacity_evidence"
    )
    require_tail = _required_true(
        protocol["require_tail_evidence"], "require_tail_evidence"
    )
    rationale = _text(protocol["rationale"], "rationale", 4000)

    preregistered_before_live = None
    first_live_iso = None
    if first_live_recommendation_at is not None:
        if (
            first_live_recommendation_at.tzinfo is None
            or first_live_recommendation_at.utcoffset() is None
        ):
            raise ExecutionSufficiencyProtocolError(
                "first_live_recommendation_at must be timezone-aware"
            )
        first_live = first_live_recommendation_at.astimezone(timezone.utc)
        first_live_iso = first_live.isoformat()
        if frozen_at >= first_live:
            raise ExecutionSufficiencyProtocolError(
                "execution sufficiency protocol must be frozen before the first LIVE recommendation it evaluates"
            )
        preregistered_before_live = True

    normalized = {
        "schema_version": schema,
        "protocol_id": protocol_id,
        "frozen_at": frozen_at.isoformat(),
        "protocol_document_sha256": document_sha,
        "minimum_live_observations": min_live,
        "minimum_distinct_decision_dates": min_dates,
        "minimum_filled_observations": min_filled,
        "minimum_no_fill_observations": min_no_fill,
        "minimum_partial_fill_observations": min_partial,
        "required_markout_horizons": list(horizons),
        "require_slippage_evidence": require_slippage,
        "require_latency_evidence": require_latency,
        "require_capacity_evidence": require_capacity,
        "require_tail_evidence": require_tail,
        "rationale": rationale,
    }
    return {
        "protocol": normalized,
        "protocol_fingerprint_sha256": _canonical_sha256(normalized),
        "preregistered_before_first_live_observation": preregistered_before_live,
        "first_live_recommendation_at": first_live_iso,
        "protocol_structurally_valid": True,
        # This validator registers criteria; it never claims those criteria pass.
        "empirical_execution_sufficiency_assessed": False,
        "empirical_execution_blocker_closed": False,
        "promotion_ready": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "guardrail": (
            "Protocol validity prevents post-hoc threshold selection but is not execution evidence. "
            "The numeric criteria must be frozen before the LIVE observations they judge and evaluated separately."
        ),
    }


def parse_and_validate_execution_sufficiency_protocol_json(
    raw_json: str | None,
    **kwargs: Any,
) -> dict[str, Any]:
    text = str(raw_json or "").strip()
    if not text:
        raise ExecutionSufficiencyProtocolError("execution sufficiency protocol JSON is not configured")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ExecutionSufficiencyProtocolError(
            "execution sufficiency protocol JSON is invalid"
        ) from exc
    if not isinstance(payload, dict):
        raise ExecutionSufficiencyProtocolError(
            "execution sufficiency protocol JSON must be an object"
        )
    return validate_execution_sufficiency_protocol(payload, **kwargs)
