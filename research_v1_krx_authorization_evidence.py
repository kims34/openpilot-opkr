"""Structured, secret-free KRX authorization-evidence validation.

This module validates metadata about an external KRX approval/authorization
artifact. It does not prove KRX access by itself and it never authorizes bulk
history, feature testing, holdout use, promotion or live trading.

The purpose is to stop an arbitrary free-form reference string from being the
only authorization metadata attached to a future tiny authenticated probe.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Mapping

from research_v1_krx_auth_preflight import ALLOWED_FAMILIES, ALLOWED_ROUTES


SCHEMA_VERSION = "1"
ALLOWED_APPROVAL_STATES = {"APPROVED", "PENDING", "REVOKED", "UNKNOWN"}
_REQUIRED_FIELDS = {
    "schema_version",
    "evidence_reference",
    "issuer",
    "source_family",
    "access_route",
    "intended_use_scope",
    "approval_state",
    "scope_statement",
    "evidence_document_sha256",
    "captured_at",
}
_OPTIONAL_FIELDS = {"valid_from", "valid_until"}
_ALLOWED_FIELDS = _REQUIRED_FIELDS | _OPTIONAL_FIELDS
_SECRET_MARKERS = (
    "password=", "passwd=", "pwd=", "token=", "cookie=", "secret=",
    "auth_key=", "api_key=", "authorization:", "bearer ",
)


class KRXAuthorizationEvidenceError(ValueError):
    """Raised when non-secret authorization evidence is malformed or unsafe."""


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _nonempty(value: Any, field: str, *, max_len: int = 1000) -> str:
    text = str(value or "").strip()
    if not text:
        raise KRXAuthorizationEvidenceError(f"{field} must be non-empty")
    if len(text) > max_len:
        raise KRXAuthorizationEvidenceError(f"{field} is unexpectedly long")
    lowered = text.lower()
    if any(marker in lowered for marker in _SECRET_MARKERS):
        raise KRXAuthorizationEvidenceError(
            f"{field} must not contain secret-like material"
        )
    return text


def _parse_time(value: Any, field: str) -> datetime:
    text = _nonempty(value, field, max_len=80)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise KRXAuthorizationEvidenceError(f"{field} must be ISO-8601") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise KRXAuthorizationEvidenceError(f"{field} must be timezone-aware")
    return dt.astimezone(timezone.utc)


def validate_authorization_evidence(
    evidence: Mapping[str, Any],
    *,
    expected_source_family: str,
    expected_access_route: str,
    expected_intended_use_scope: str,
    evaluation_time: datetime,
    expected_reference: str | None = None,
) -> dict[str, Any]:
    """Validate one secret-free authorization-evidence metadata record.

    The returned `sufficient_for_tiny_probe_preflight` means only that the
    metadata record is internally consistent, active at `evaluation_time`, and
    matches the declared route/family/use scope. It is never Gate-A PASS and is
    not proof of historical coverage, licensing sufficiency or Alpha.
    """
    if evaluation_time.tzinfo is None or evaluation_time.utcoffset() is None:
        raise KRXAuthorizationEvidenceError("evaluation_time must be timezone-aware")
    now = evaluation_time.astimezone(timezone.utc)

    keys = set(evidence)
    missing = _REQUIRED_FIELDS - keys
    extra = keys - _ALLOWED_FIELDS
    if missing:
        raise KRXAuthorizationEvidenceError(
            f"authorization evidence missing required fields: {sorted(missing)}"
        )
    if extra:
        raise KRXAuthorizationEvidenceError(
            f"authorization evidence contains unsupported fields: {sorted(extra)}"
        )

    schema_version = _nonempty(evidence["schema_version"], "schema_version", max_len=20)
    if schema_version != SCHEMA_VERSION:
        raise KRXAuthorizationEvidenceError(
            f"unsupported authorization evidence schema_version: {schema_version}"
        )

    reference = _nonempty(evidence["evidence_reference"], "evidence_reference", max_len=200)
    issuer = _nonempty(evidence["issuer"], "issuer", max_len=100)
    family = _nonempty(evidence["source_family"], "source_family", max_len=100)
    route = _nonempty(evidence["access_route"], "access_route", max_len=100)
    use_scope = _nonempty(evidence["intended_use_scope"], "intended_use_scope", max_len=200)
    approval_state = _nonempty(evidence["approval_state"], "approval_state", max_len=30).upper()
    scope_statement = _nonempty(evidence["scope_statement"], "scope_statement", max_len=1000)
    document_sha = _nonempty(
        evidence["evidence_document_sha256"], "evidence_document_sha256", max_len=64
    ).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", document_sha):
        raise KRXAuthorizationEvidenceError(
            "evidence_document_sha256 must be a 64-character lowercase/uppercase hex SHA-256"
        )
    captured_at = _parse_time(evidence["captured_at"], "captured_at")
    valid_from = (
        _parse_time(evidence["valid_from"], "valid_from")
        if evidence.get("valid_from") not in (None, "")
        else None
    )
    valid_until = (
        _parse_time(evidence["valid_until"], "valid_until")
        if evidence.get("valid_until") not in (None, "")
        else None
    )

    if family not in ALLOWED_FAMILIES:
        raise KRXAuthorizationEvidenceError(f"unsupported source_family: {family}")
    if route not in ALLOWED_ROUTES:
        raise KRXAuthorizationEvidenceError(f"unsupported access_route: {route}")
    if approval_state not in ALLOWED_APPROVAL_STATES:
        raise KRXAuthorizationEvidenceError(
            f"unsupported approval_state: {approval_state}"
        )
    if captured_at > now:
        raise KRXAuthorizationEvidenceError("captured_at cannot be in the future")
    if valid_from and valid_until and valid_until < valid_from:
        raise KRXAuthorizationEvidenceError("valid_until cannot precede valid_from")

    reasons: list[str] = []
    if issuer.upper() != "KRX":
        reasons.append("ISSUER_NOT_KRX")
    if family != expected_source_family:
        reasons.append("SOURCE_FAMILY_MISMATCH")
    if route != expected_access_route:
        reasons.append("ACCESS_ROUTE_MISMATCH")
    if use_scope != expected_intended_use_scope:
        reasons.append("INTENDED_USE_SCOPE_MISMATCH")
    if expected_reference is not None and reference != str(expected_reference).strip():
        reasons.append("EVIDENCE_REFERENCE_MISMATCH")
    if approval_state != "APPROVED":
        reasons.append(f"APPROVAL_STATE_{approval_state}")
    if valid_from and now < valid_from:
        reasons.append("NOT_YET_VALID")
    if valid_until and now > valid_until:
        reasons.append("EXPIRED")

    sufficient = not reasons
    normalized = {
        "schema_version": schema_version,
        "evidence_reference": reference,
        "issuer": issuer,
        "source_family": family,
        "access_route": route,
        "intended_use_scope": use_scope,
        "approval_state": approval_state,
        "scope_statement": scope_statement,
        "evidence_document_sha256": document_sha,
        "captured_at": captured_at.isoformat(),
        "valid_from": None if valid_from is None else valid_from.isoformat(),
        "valid_until": None if valid_until is None else valid_until.isoformat(),
    }
    return {
        "record": normalized,
        "record_fingerprint_sha256": _canonical_sha256(normalized),
        "sufficient_for_tiny_probe_preflight": sufficient,
        "reason_codes": reasons,
        "gate_a_status_ceiling": "PARTIAL" if sufficient else "BLOCKED",
        "bulk_historical_acquisition_authorized": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "alpha_or_final_judge_promotion_authorized": False,
        "live_trading_authorized": False,
        "guardrail": (
            "A valid authorization-evidence record is only structured metadata for one tiny probe. "
            "It cannot make Gate A PASS and cannot substitute for coverage, PIT, licensing, Alpha, holdout or live evidence."
        ),
    }


def parse_and_validate_authorization_evidence_json(
    raw_json: str | None,
    **kwargs: Any,
) -> dict[str, Any]:
    text = str(raw_json or "").strip()
    if not text:
        raise KRXAuthorizationEvidenceError("authorization evidence JSON is not configured")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise KRXAuthorizationEvidenceError("authorization evidence JSON is invalid") from exc
    if not isinstance(payload, dict):
        raise KRXAuthorizationEvidenceError("authorization evidence JSON must be an object")
    return validate_authorization_evidence(payload, **kwargs)
