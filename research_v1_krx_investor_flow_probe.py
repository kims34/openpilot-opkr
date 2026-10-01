"""Minimal fail-closed KRX investor-flow source probe.

This is NOT a backtest and does not persist KRX numeric market data. It only
checks whether an authenticated KRX Data Marketplace web session is available
and whether the documented individual-investor daily screen route returns a
parseable frame for one security over a tiny historical window.

Authentication routes are deliberately distinct:
- KRX_ID/KRX_PW: Data Marketplace authenticated web-session route used here.
- KRX OpenAPI AUTH_KEY: separate official OpenAPI route requiring key approval
  and approval for each API service. No exact public OpenAPI mapping for this
  required per-security investor-flow dataset is assumed by this probe.

Credentials are never printed or written to artifacts. Source feasibility is
not feature-promotion evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

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


def source_gate_audit(*, session_configured: bool) -> dict:
    """Map this tiny probe to the frozen A-F contract conservatively."""
    statuses = {
        "A": "PARTIAL" if session_configured else "BLOCKED",
        "B": "PARTIAL",
        "C": "BLOCKED",
        "D": "PARTIAL",
        "E": "PARTIAL",
        "F": "PARTIAL",
    }
    evidence = {
        "A": (
            "Data Marketplace session credentials are present and the probe may exercise the authenticated route, "
            "but the reproducible authorized historical access contract for the required per-security history is not frozen."
            if session_configured
            else "KRX_ID/KRX_PW are absent in the active runtime, so the authenticated Data Marketplace route is not exercised."
        ),
        "B": (
            "The MDCSTAT02303 individual-investor daily source family is identified, but exact approved historical service/schema equivalence is not closed."
        ),
        "C": (
            "The tiny three-session probe cannot establish full research-period coverage or stable security mapping."
        ),
        "D": (
            "The after-20:00 publication rule is frozen, but record-level event_time/published_at/available_at/ingested_at lineage is not implemented for historical research data."
        ),
        "E": (
            "The client revision, probe window, route metadata and fail-closed diagnostics are reproducible, "
            "but bulk historical acquisition and coverage integrity remain unverified."
        ),
        "F": (
            "Internal research and external/commercial use are separated by contract, but rights for the ultimately selected investor-flow route remain unverified."
        ),
    }
    return audit_source_gates(
        source_family=SOURCE_FAMILY,
        intended_use_scope=INTENDED_USE_SCOPE,
        statuses=statuses,
        evidence=evidence,
    )


def _finalise_report(report: dict[str, Any], *, session_configured: bool) -> dict[str, Any]:
    public_evidence_fingerprint = public_evidence_fingerprint_sha256()
    report["authenticated_request_attempted"] = bool(session_configured)
    report["source_gate_audit"] = source_gate_audit(session_configured=session_configured)
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
    }
    report["probe_contract_fingerprint_sha256"] = _canonical_sha256(contract_material)
    result_material = {
        key: value
        for key, value in report.items()
        if key not in {"probe_result_fingerprint_sha256"}
    }
    report["probe_result_fingerprint_sha256"] = _canonical_sha256(result_material)
    return report


def _write_report(out: Path, report: dict[str, Any], *, session_configured: bool) -> None:
    final = _finalise_report(report, session_configured=session_configured)
    (out / "summary.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("KRX_INVESTOR_FLOW_PROBE=" + json.dumps(final, ensure_ascii=False), flush=True)


def main() -> None:
    out = Path("research_results/krx_investor_flow_probe")
    out.mkdir(parents=True, exist_ok=True)

    session_configured = bool(os.getenv("KRX_ID")) and bool(os.getenv("KRX_PW"))
    openapi_key_present = bool(os.getenv("KRX_OPENAPI_AUTH_KEY"))
    report: dict[str, Any] = {
        "purpose": "DATA_SOURCE_FEASIBILITY_ONLY_NOT_PERFORMANCE_RESEARCH",
        "source": SOURCE_NAME,
        "numeric_market_data_persisted": False,
        # Backward-compatible field: this refers to the web-session route only.
        "credentials_present": session_configured,
        "data_marketplace_session_credentials_present": session_configured,
        "official_openapi_auth_key_present": openapi_key_present,
        "active_probe_access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "pinned_krx_data_api_commit": PINNED_KRX_DATA_API,
        "openapi_route_status": (
            "KEY_PRESENT_BUT_REQUIRED_INVESTOR_FLOW_API_MAPPING_NOT_ESTABLISHED"
            if openapi_key_present
            else "AUTH_KEY_NOT_CONFIGURED_AND_REQUIRED_INVESTOR_FLOW_API_MAPPING_NOT_ESTABLISHED"
        ),
        "status": "AUTH_NOT_CONFIGURED" if not session_configured else "PENDING",
        "available_at_policy_if_adopted": (
            "day_D final stock investor trading results must not enter a decision before publication; "
            "the official KRX Data Marketplace investor-trading page states final day-D results are provided after 20:00"
        ),
        "source_route_policy": {
            "data_marketplace_session": (
                "KRX_ID/KRX_PW may be used only for authenticated Data Marketplace source-feasibility checks"
            ),
            "official_openapi": (
                "AUTH_KEY is separate and must not be treated as equivalent unless an exact approved API service covers the required dataset"
            ),
            "no_auth_substitution": True,
        },
        "why_not_feature_ready": [
            "official reproducible historical access contract is not yet frozen",
            "exact public OpenAPI service mapping for required per-security investor flow is not established",
            "historical coverage and stable security mapping are not yet audited",
            "event_time/published_at/available_at/ingested_at lineage is not yet complete",
        ],
    }

    if not session_configured:
        _write_report(out, report, session_configured=False)
        return

    try:
        from krx_data_api import fetch

        # One security, three already-completed sessions only. No bulk crawl.
        # This uses the authenticated Data Marketplace session route, not the
        # KRX OpenAPI AUTH_KEY route.
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
    except Exception as exc:  # fail closed but keep CI diagnostic artifact
        report.update({
            "status": "SOURCE_UNREACHABLE_OR_AUTH_FAILED",
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:500],
        })

    _write_report(out, report, session_configured=True)


if __name__ == "__main__":
    main()
