"""Minimal fail-closed KRX investor-flow source probe.

This is NOT a backtest and does not persist KRX numeric market data. It only
checks whether an explicitly authorized and explicitly consented KRX Data
Marketplace web-session probe may be attempted and whether the documented
individual-investor daily screen route returns a parseable frame for one
security over a tiny historical window.

Credentials are not authorization, an opaque reference is not validated
evidence, and authorization metadata is not runtime consent. KRX_ID/KRX_PW, a
matching structured non-secret authorization-evidence record, and the exact
explicit-consent sentinel are required before this probe makes an authenticated
request. KRX OpenAPI AUTH_KEY is a separate route and is never substituted.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from research_v1_krx_auth_preflight import (
    DATA_MARKETPLACE_ROUTE,
    EXPLICIT_PROBE_CONSENT_ENV,
    evaluate_auth_preflight,
)
from research_v1_krx_authorization_evidence import (
    KRXAuthorizationEvidenceError,
    parse_and_validate_authorization_evidence_json,
)
from research_v1_krx_public_evidence import (
    PUBLIC_EVIDENCE_VERSION,
    public_evidence_fingerprint_sha256,
)
from research_v1_krx_source_gates import audit_source_gates


PINNED_KRX_DATA_API = "e6ebac9b71482db127348d8a08ebc6743aa3b50e"
SOURCE_FAMILY = "KRX_INVESTOR_FLOW"
INTENDED_USE_SCOPE = "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION"
SOURCE_NAME = "KRX_Data_Marketplace_MDCSTAT02303_via_authenticated_web_session"


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_authorization_evidence(
    *, authorization_evidence_reference: str | None, raw_json: str | None
) -> tuple[bool, dict[str, Any]]:
    try:
        validated = parse_and_validate_authorization_evidence_json(
            raw_json,
            expected_source_family=SOURCE_FAMILY,
            expected_access_route=DATA_MARKETPLACE_ROUTE,
            expected_intended_use_scope=INTENDED_USE_SCOPE,
            evaluation_time=datetime.now(timezone.utc),
            expected_reference=authorization_evidence_reference,
        )
        sufficient = bool(validated["sufficient_for_tiny_probe_preflight"])
        automated_collection_authorized = bool(
            validated["record"].get("automated_collection_authorized") is True
        )
        return sufficient, {
            "configured": True,
            "valid_for_declared_tiny_probe": sufficient,
            "reason_codes": list(validated["reason_codes"]),
            "record_fingerprint_sha256": validated["record_fingerprint_sha256"],
            "evidence_reference": validated["record"]["evidence_reference"],
            "approval_state": validated["record"]["approval_state"],
            "automated_collection_authorized": automated_collection_authorized,
        }
    except KRXAuthorizationEvidenceError as exc:
        return False, {
            "configured": bool(str(raw_json or "").strip()),
            "valid_for_declared_tiny_probe": False,
            "reason_codes": [type(exc).__name__, str(exc)],
            "record_fingerprint_sha256": None,
            "evidence_reference": None,
            "approval_state": None,
            "automated_collection_authorized": False,
        }


def source_gate_audit(*, request_authorized: bool) -> dict:
    """Map this tiny probe to the frozen A-F contract conservatively."""
    statuses = {
        "A": "PARTIAL" if request_authorized else "BLOCKED",
        "B": "PARTIAL",
        "C": "BLOCKED",
        "D": "PARTIAL",
        "E": "PARTIAL",
        "F": "PARTIAL",
    }
    evidence = {
        "A": (
            "Route-specific Data Marketplace credentials, a matching validated non-secret authorization-evidence record and exact explicit per-run consent are present, so the tiny authenticated probe may be exercised; the full historical access contract is still not closed."
            if request_authorized
            else "The active runtime has not satisfied credentials, validated authorization-evidence and explicit-consent requirements together, so no authenticated Data Marketplace request is attempted."
        ),
        "B": "The MDCSTAT02303 individual-investor daily source family is identified, but exact approved historical service/schema equivalence is not closed.",
        "C": "The tiny three-session probe cannot establish full research-period coverage or stable security mapping.",
        "D": "The after-20:00 publication rule is frozen, but complete record-level event_time/published_at/available_at/ingested_at lineage has not yet been demonstrated on real historical research data.",
        "E": "The client revision, probe window, route metadata and fail-closed diagnostics are reproducible, but bulk historical acquisition and coverage integrity remain unverified.",
        "F": "Internal research and external/commercial use are separated by contract, but rights for the ultimately selected investor-flow route remain unverified.",
    }
    return audit_source_gates(
        source_family=SOURCE_FAMILY,
        intended_use_scope=INTENDED_USE_SCOPE,
        statuses=statuses,
        evidence=evidence,
    )


def _finalise_report(report: dict[str, Any], *, request_authorized: bool) -> dict[str, Any]:
    public_evidence_fingerprint = public_evidence_fingerprint_sha256()
    report["authenticated_request_attempted"] = bool(request_authorized)
    report["source_gate_audit"] = source_gate_audit(request_authorized=request_authorized)
    report["feature_performance_testing_authorized"] = False
    report["public_contract_evidence_version"] = PUBLIC_EVIDENCE_VERSION
    report["public_contract_evidence_fingerprint_sha256"] = public_evidence_fingerprint
    contract_material = {
        "source_family": SOURCE_FAMILY,
        "intended_use_scope": INTENDED_USE_SCOPE,
        "source": SOURCE_NAME,
        "active_probe_access_route": report["active_probe_access_route"],
        "pinned_krx_data_api_commit": PINNED_KRX_DATA_API,
        "available_at_policy_if_adopted": report["available_at_policy_if_adopted"],
        "source_route_policy": report["source_route_policy"],
        "probe_security": "005930",
        "probe_window": ["2026-09-21", "2026-09-23"],
        "public_contract_evidence_version": PUBLIC_EVIDENCE_VERSION,
        "public_contract_evidence_fingerprint_sha256": public_evidence_fingerprint,
        "authorization_preflight_required": True,
        "structured_authorization_evidence_required": True,
        "explicit_per_run_probe_consent_required": True,
    }
    report["probe_contract_fingerprint_sha256"] = _canonical_sha256(contract_material)
    result_material = {
        key: value for key, value in report.items()
        if key not in {"probe_result_fingerprint_sha256"}
    }
    report["probe_result_fingerprint_sha256"] = _canonical_sha256(result_material)
    return report


def _write_report(out: Path, report: dict[str, Any], *, request_authorized: bool) -> None:
    final = _finalise_report(report, request_authorized=request_authorized)
    (out / "summary.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("KRX_INVESTOR_FLOW_PROBE=" + json.dumps(final, ensure_ascii=False), flush=True)


def main() -> None:
    out = Path("research_results/krx_investor_flow_probe")
    out.mkdir(parents=True, exist_ok=True)

    environment = {
        "KRX_ID": os.getenv("KRX_ID"),
        "KRX_PW": os.getenv("KRX_PW"),
        "KRX_OPENAPI_AUTH_KEY": os.getenv("KRX_OPENAPI_AUTH_KEY"),
        EXPLICIT_PROBE_CONSENT_ENV: os.getenv(EXPLICIT_PROBE_CONSENT_ENV),
    }
    session_credentials_present = bool(environment["KRX_ID"]) and bool(environment["KRX_PW"])
    openapi_key_present = bool(environment["KRX_OPENAPI_AUTH_KEY"])
    auth_ref = os.getenv("KRX_AUTH_EVIDENCE_REF")
    evidence_valid, evidence_summary = _validate_authorization_evidence(
        authorization_evidence_reference=auth_ref,
        raw_json=os.getenv("KRX_AUTH_EVIDENCE_JSON"),
    )
    preflight = evaluate_auth_preflight(
        source_family=SOURCE_FAMILY,
        access_route=DATA_MARKETPLACE_ROUTE,
        environment=environment,
        authorization_evidence_reference=auth_ref,
        authorization_evidence_record_validated=evidence_valid,
        automated_collection_authorized=bool(
            evidence_summary.get("automated_collection_authorized") is True
        ),
    )
    request_authorized = bool(preflight["request_attempt_authorized"])

    report: dict[str, Any] = {
        "purpose": "DATA_SOURCE_FEASIBILITY_ONLY_NOT_PERFORMANCE_RESEARCH",
        "source": SOURCE_NAME,
        "numeric_market_data_persisted": False,
        "credentials_present": session_credentials_present,
        "data_marketplace_session_credentials_present": session_credentials_present,
        "official_openapi_auth_key_present": openapi_key_present,
        "authorization_evidence_reference_present": preflight["authorization_evidence_reference_present"],
        "authorization_evidence": evidence_summary,
        "explicit_probe_consent_present": preflight["explicit_probe_consent_present"],
        "authorization_preflight": preflight,
        "active_probe_access_route": DATA_MARKETPLACE_ROUTE,
        "pinned_krx_data_api_commit": PINNED_KRX_DATA_API,
        "openapi_route_status": (
            "KEY_PRESENT_BUT_REQUIRED_INVESTOR_FLOW_API_MAPPING_NOT_ESTABLISHED"
            if openapi_key_present
            else "AUTH_KEY_NOT_CONFIGURED_AND_REQUIRED_INVESTOR_FLOW_API_MAPPING_NOT_ESTABLISHED"
        ),
        "status": "PENDING" if request_authorized else "AUTHORIZATION_OR_CONSENT_PREFLIGHT_BLOCKED",
        "available_at_policy_if_adopted": (
            "day_D final stock investor trading results must not enter a decision before publication; "
            "the official KRX Data Marketplace investor-trading page states final day-D results are provided after 20:00"
        ),
        "source_route_policy": {
            "data_marketplace_session": "KRX_ID/KRX_PW, a matching validated non-secret authorization-evidence record that explicitly authorizes automated collection, and exact explicit per-run consent are required for the tiny authenticated Data Marketplace source-feasibility check",
            "official_openapi": "AUTH_KEY is separate and must not be treated as equivalent unless an exact approved API service covers the required dataset",
            "no_auth_substitution": True,
            "push_is_dry_run_only": True,
        },
        "why_not_feature_ready": [
            "official reproducible historical access contract is not yet frozen",
            "exact public OpenAPI service mapping for required per-security investor flow is not established",
            "historical coverage and stable security mapping are not yet audited on real data",
            "full historical event_time/published_at/available_at/ingested_at lineage is not yet demonstrated",
        ],
    }

    if not request_authorized:
        _write_report(out, report, request_authorized=False)
        return

    try:
        from krx_data_api import fetch

        df = fetch(
            "investor_trading_individual_daily",
            isuCd="KR7005930003",
            strtDd="20260921",
            endDd="20260923",
            askBid="3",
            trdVolVal="2",
            auth=True,
        )
        report.update({
            "status": "SOURCE_REACHABLE" if len(df) else "SOURCE_REACHABLE_EMPTY_RESULT",
            "rows": int(len(df)),
            "columns": [str(x) for x in df.columns],
            "index_name": None if df.index.name is None else str(df.index.name),
            "probe_security": "005930",
            "probe_window": ["2026-09-21", "2026-09-23"],
        })
    except Exception as exc:
        report.update({
            "status": "SOURCE_UNREACHABLE_OR_AUTH_FAILED",
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:500],
        })

    _write_report(out, report, request_authorized=True)


if __name__ == "__main__":
    main()
