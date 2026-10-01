"""Fail-closed preregistration validator for empirical LIVE execution sufficiency.

Schema v1 is retained for historical/test-only structural preregistration.
Schema v2 is the project-grade protocol: it freezes policy identity, sample size,
capacity, fill, slippage, latency, markout and integrity acceptance criteria
before the first LIVE recommendation that those criteria may judge.

Protocol validity is never execution evidence and never authorizes holdout,
promotion or live trading.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Mapping


SUPPORTED_SCHEMA_VERSIONS = frozenset({"1", "2"})
REQUIRED_MARKOUT_HORIZONS = frozenset({"5m", "30m", "close"})
_BASE_FIELDS = {
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
_V2_FIELDS = {
    "decision_policy_id",
    "execution_policy_id",
    "maximum_participation_rate",
    "near_capacity_floor_fraction",
    "minimum_near_capacity_observations",
    "minimum_mean_fill_ratio_lcb95",
    "maximum_no_fill_rate_ucb95",
    "maximum_partial_fill_rate_ucb95",
    "maximum_mean_excess_slippage_bps_ucb95",
    "maximum_slippage_budget_ratio_p95",
    "maximum_slippage_budget_ratio_p99",
    "maximum_fee_tax_excess_bps_ucb95",
    "maximum_submit_latency_ttl_fraction_p95",
    "maximum_first_fill_latency_expiry_fraction_p95",
    "minimum_5m_markout_plus_budget_lcb95_bps",
    "minimum_near_capacity_mean_fill_ratio_lcb95",
    "maximum_near_capacity_mean_excess_slippage_bps_ucb95",
    "require_zero_expired_submissions",
    "require_zero_late_fills_after_order_expiry",
    "require_zero_capacity_breaches",
    "require_zero_unknown_outcomes",
    "require_zero_reconciliation_failures",
    "require_zero_risk_limit_breaches",
    "require_complete_markouts",
}


class ExecutionSufficiencyProtocolError(ValueError):
    """Raised when a proposed execution-sufficiency preregistration is invalid."""


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str
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
        raise ExecutionSufficiencyProtocolError(f"{field} must be >= {minimum}")
    return parsed


def _float(
    value: Any,
    field: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    minimum_exclusive: bool = False,
) -> float:
    if isinstance(value, bool):
        raise ExecutionSufficiencyProtocolError(f"{field} must be numeric")
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ExecutionSufficiencyProtocolError(f"{field} must be numeric") from exc
    if not (x == x and abs(x) != float("inf")):
        raise ExecutionSufficiencyProtocolError(f"{field} must be finite")
    if minimum is not None:
        if minimum_exclusive and not x > minimum:
            raise ExecutionSufficiencyProtocolError(f"{field} must be > {minimum}")
        if not minimum_exclusive and x < minimum:
            raise ExecutionSufficiencyProtocolError(f"{field} must be >= {minimum}")
    if maximum is not None and x > maximum:
        raise ExecutionSufficiencyProtocolError(f"{field} must be <= {maximum}")
    return x


def _required_true(value: Any, field: str) -> bool:
    if value is not True:
        raise ExecutionSufficiencyProtocolError(f"{field} must be true")
    return True


def validate_execution_sufficiency_protocol(
    protocol: Mapping[str, Any],
    *,
    first_live_recommendation_at: datetime | None = None,
    protocol_document_text: str | None = None,
) -> dict[str, Any]:
    """Validate a preregistered execution-sufficiency protocol.

    If a first LIVE timestamp exists, ``frozen_at`` must be strictly earlier.
    If exact protocol document text is supplied, its SHA-256 must match the
    preregistered document fingerprint.
    """
    if not isinstance(protocol, Mapping):
        raise ExecutionSufficiencyProtocolError("protocol must be an object")
    schema = _text(protocol.get("schema_version"), "schema_version", 20)
    if schema not in SUPPORTED_SCHEMA_VERSIONS:
        raise ExecutionSufficiencyProtocolError(f"unsupported schema_version: {schema}")

    required = set(_BASE_FIELDS)
    if schema == "2":
        required |= _V2_FIELDS
    keys = set(protocol)
    missing = required - keys
    extra = keys - required
    if missing:
        raise ExecutionSufficiencyProtocolError(
            f"protocol missing required fields: {sorted(missing)}"
        )
    if extra:
        raise ExecutionSufficiencyProtocolError(
            f"protocol contains unsupported fields: {sorted(extra)}"
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
    document_sha_verified = None
    if protocol_document_text is not None:
        actual = hashlib.sha256(protocol_document_text.encode("utf-8")).hexdigest()
        if actual != document_sha:
            raise ExecutionSufficiencyProtocolError(
                "protocol_document_sha256 does not match supplied protocol document"
            )
        document_sha_verified = True

    min_live = _int(protocol["minimum_live_observations"], "minimum_live_observations", minimum=1)
    min_dates = _int(protocol["minimum_distinct_decision_dates"], "minimum_distinct_decision_dates", minimum=1)
    min_filled = _int(protocol["minimum_filled_observations"], "minimum_filled_observations", minimum=1)
    min_no_fill = _int(protocol["minimum_no_fill_observations"], "minimum_no_fill_observations", minimum=0)
    min_partial = _int(protocol["minimum_partial_fill_observations"], "minimum_partial_fill_observations", minimum=0)
    if min_dates > min_live:
        raise ExecutionSufficiencyProtocolError("minimum_distinct_decision_dates cannot exceed minimum_live_observations")
    if min_filled > min_live:
        raise ExecutionSufficiencyProtocolError("minimum_filled_observations cannot exceed minimum_live_observations")
    if min_no_fill > min_live:
        raise ExecutionSufficiencyProtocolError("minimum_no_fill_observations cannot exceed minimum_live_observations")
    if min_partial > min_filled:
        raise ExecutionSufficiencyProtocolError("minimum_partial_fill_observations cannot exceed minimum_filled_observations")

    horizons_raw = protocol["required_markout_horizons"]
    if not isinstance(horizons_raw, (list, tuple)):
        raise ExecutionSufficiencyProtocolError("required_markout_horizons must be a list")
    horizons = tuple(str(x).strip().lower() for x in horizons_raw)
    if not horizons or any(not x for x in horizons):
        raise ExecutionSufficiencyProtocolError("required_markout_horizons must not contain empty values")
    if len(set(horizons)) != len(horizons):
        raise ExecutionSufficiencyProtocolError("required_markout_horizons must not contain duplicates")
    if not REQUIRED_MARKOUT_HORIZONS.issubset(set(horizons)):
        raise ExecutionSufficiencyProtocolError("required_markout_horizons must include 5m, 30m and close")

    normalized: dict[str, Any] = {
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
        "require_slippage_evidence": _required_true(protocol["require_slippage_evidence"], "require_slippage_evidence"),
        "require_latency_evidence": _required_true(protocol["require_latency_evidence"], "require_latency_evidence"),
        "require_capacity_evidence": _required_true(protocol["require_capacity_evidence"], "require_capacity_evidence"),
        "require_tail_evidence": _required_true(protocol["require_tail_evidence"], "require_tail_evidence"),
        "rationale": _text(protocol["rationale"], "rationale", 6000),
    }

    if schema == "2":
        normalized.update({
            "decision_policy_id": _text(protocol["decision_policy_id"], "decision_policy_id", 200),
            "execution_policy_id": _text(protocol["execution_policy_id"], "execution_policy_id", 200),
            "maximum_participation_rate": _float(protocol["maximum_participation_rate"], "maximum_participation_rate", minimum=0.0, maximum=1.0, minimum_exclusive=True),
            "near_capacity_floor_fraction": _float(protocol["near_capacity_floor_fraction"], "near_capacity_floor_fraction", minimum=0.0, maximum=1.0, minimum_exclusive=True),
            "minimum_near_capacity_observations": _int(protocol["minimum_near_capacity_observations"], "minimum_near_capacity_observations", minimum=1),
            "minimum_mean_fill_ratio_lcb95": _float(protocol["minimum_mean_fill_ratio_lcb95"], "minimum_mean_fill_ratio_lcb95", minimum=0.0, maximum=1.0),
            "maximum_no_fill_rate_ucb95": _float(protocol["maximum_no_fill_rate_ucb95"], "maximum_no_fill_rate_ucb95", minimum=0.0, maximum=1.0),
            "maximum_partial_fill_rate_ucb95": _float(protocol["maximum_partial_fill_rate_ucb95"], "maximum_partial_fill_rate_ucb95", minimum=0.0, maximum=1.0),
            "maximum_mean_excess_slippage_bps_ucb95": _float(protocol["maximum_mean_excess_slippage_bps_ucb95"], "maximum_mean_excess_slippage_bps_ucb95"),
            "maximum_slippage_budget_ratio_p95": _float(protocol["maximum_slippage_budget_ratio_p95"], "maximum_slippage_budget_ratio_p95", minimum=1.0),
            "maximum_slippage_budget_ratio_p99": _float(protocol["maximum_slippage_budget_ratio_p99"], "maximum_slippage_budget_ratio_p99", minimum=1.0),
            "maximum_fee_tax_excess_bps_ucb95": _float(protocol["maximum_fee_tax_excess_bps_ucb95"], "maximum_fee_tax_excess_bps_ucb95", minimum=0.0),
            "maximum_submit_latency_ttl_fraction_p95": _float(protocol["maximum_submit_latency_ttl_fraction_p95"], "maximum_submit_latency_ttl_fraction_p95", minimum=0.0, maximum=1.0),
            "maximum_first_fill_latency_expiry_fraction_p95": _float(protocol["maximum_first_fill_latency_expiry_fraction_p95"], "maximum_first_fill_latency_expiry_fraction_p95", minimum=0.0, maximum=1.0),
            "minimum_5m_markout_plus_budget_lcb95_bps": _float(protocol["minimum_5m_markout_plus_budget_lcb95_bps"], "minimum_5m_markout_plus_budget_lcb95_bps"),
            "minimum_near_capacity_mean_fill_ratio_lcb95": _float(protocol["minimum_near_capacity_mean_fill_ratio_lcb95"], "minimum_near_capacity_mean_fill_ratio_lcb95", minimum=0.0, maximum=1.0),
            "maximum_near_capacity_mean_excess_slippage_bps_ucb95": _float(protocol["maximum_near_capacity_mean_excess_slippage_bps_ucb95"], "maximum_near_capacity_mean_excess_slippage_bps_ucb95"),
            "require_zero_expired_submissions": _required_true(protocol["require_zero_expired_submissions"], "require_zero_expired_submissions"),
            "require_zero_late_fills_after_order_expiry": _required_true(protocol["require_zero_late_fills_after_order_expiry"], "require_zero_late_fills_after_order_expiry"),
            "require_zero_capacity_breaches": _required_true(protocol["require_zero_capacity_breaches"], "require_zero_capacity_breaches"),
            "require_zero_unknown_outcomes": _required_true(protocol["require_zero_unknown_outcomes"], "require_zero_unknown_outcomes"),
            "require_zero_reconciliation_failures": _required_true(protocol["require_zero_reconciliation_failures"], "require_zero_reconciliation_failures"),
            "require_zero_risk_limit_breaches": _required_true(protocol["require_zero_risk_limit_breaches"], "require_zero_risk_limit_breaches"),
            "require_complete_markouts": _required_true(protocol["require_complete_markouts"], "require_complete_markouts"),
        })
        if normalized["minimum_near_capacity_observations"] > min_live:
            raise ExecutionSufficiencyProtocolError("minimum_near_capacity_observations cannot exceed minimum_live_observations")
        if normalized["maximum_slippage_budget_ratio_p99"] < normalized["maximum_slippage_budget_ratio_p95"]:
            raise ExecutionSufficiencyProtocolError("p99 slippage budget ratio limit cannot be tighter than p95")

    preregistered_before_live = None
    first_live_iso = None
    if first_live_recommendation_at is not None:
        if first_live_recommendation_at.tzinfo is None or first_live_recommendation_at.utcoffset() is None:
            raise ExecutionSufficiencyProtocolError("first_live_recommendation_at must be timezone-aware")
        first_live = first_live_recommendation_at.astimezone(timezone.utc)
        first_live_iso = first_live.isoformat()
        if frozen_at >= first_live:
            raise ExecutionSufficiencyProtocolError(
                "execution sufficiency protocol must be frozen before the first LIVE recommendation it evaluates"
            )
        preregistered_before_live = True

    return {
        "protocol": normalized,
        "protocol_fingerprint_sha256": _canonical_sha256(normalized),
        "protocol_document_sha256_verified": document_sha_verified,
        "preregistered_before_first_live_observation": preregistered_before_live,
        "first_live_recommendation_at": first_live_iso,
        "protocol_structurally_valid": True,
        "empirical_execution_sufficiency_assessed": False,
        "empirical_execution_blocker_closed": False,
        "promotion_ready": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "guardrail": (
            "Protocol validity prevents post-hoc threshold selection but is not execution evidence. "
            "Any passing assessment remains only one independent Master Spec input."
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
        raise ExecutionSufficiencyProtocolError("execution sufficiency protocol JSON is invalid") from exc
    if not isinstance(payload, dict):
        raise ExecutionSufficiencyProtocolError("execution sufficiency protocol JSON must be an object")
    return validate_execution_sufficiency_protocol(payload, **kwargs)
