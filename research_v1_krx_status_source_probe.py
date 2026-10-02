"""Metadata-only feasibility probe for official KRX identity/status sources.

This probe is data-source infrastructure, NOT alpha/performance research. It
never persists KRX numeric market rows. It records only reachability, row
counts, column names, source identifiers and errors needed to decide whether a
future historical PIT ingestion job can be built reproducibly.

Credentials are not authorization, an opaque reference is not validated
evidence, and authorization metadata is not runtime consent. KRX_ID/KRX_PW, a
matching structured non-secret authorization-evidence record, and the exact
explicit-consent sentinel are required before this probe makes an authenticated
Data Marketplace request. KRX OpenAPI AUTH_KEY is a separate route and is never
substituted for the web-session route.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

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
OUT = Path("research_results/krx_status_source_probe")
SOURCE_FAMILY = "KRX_SECURITY_STATUS"
INTENDED_USE_SCOPE = "INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION"


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _frame_meta(df) -> dict[str, Any]:
    return {
        "reachable": True,
        "rows": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "server_current_datetime": df.attrs.get("current_datetime"),
    }


def _try(name: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"name": name, **_frame_meta(fn())}
    except Exception as exc:
        return {
            "name": name,
            "reachable": False,
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:700],
        }


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
    """Map this tiny probe to the frozen A-F source contract conservatively."""
    statuses = {
        "A": "PARTIAL" if request_authorized else "BLOCKED",
        "B": "PARTIAL",
        "C": "BLOCKED",
        "D": "BLOCKED",
        "E": "PARTIAL",
        "F": "PARTIAL",
    }
    evidence = {
        "A": (
            "Route-specific Data Marketplace credentials, a matching validated non-secret authorization-evidence record and exact explicit per-run consent are present, so the tiny authenticated probe may be exercised; the full historical product/access contract remains open."
            if request_authorized
            else "The active runtime has not satisfied credentials, validated authorization-evidence and explicit-consent requirements together, so no authenticated Data Marketplace request is attempted."
        ),
        "B": "MDCSTAT213/237/238/239 screen families are identified, but some low-level mappings remain provisional and exact approved service/schema equivalence for the complete historical family is not closed.",
        "C": "The tiny source probe does not reconstruct or independently audit full requested-period common-stock/status coverage.",
        "D": "Record-level historical event_time/published_at/available_at/ingested_at lineage across all required status families is not established.",
        "E": "The client revision, route metadata, schema metadata and fail-closed diagnostics are reproducible, but end-to-end historical acquisition and coverage reproducibility remain open.",
        "F": "Internal research and external/commercial use are separated by contract, but rights for the final selected historical route remain unverified.",
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
    report["public_contract_evidence_version"] = PUBLIC_EVIDENCE_VERSION
    report["public_contract_evidence_fingerprint_sha256"] = public_evidence_fingerprint
    contract_material = {
        "source_family": SOURCE_FAMILY,
        "intended_use_scope": INTENDED_USE_SCOPE,
        "active_probe_access_route": report["active_probe_access_route"],
        "pinned_krx_data_api_commit": report["pinned_krx_data_api_commit"],
        "official_screen_contracts": report["official_screen_contracts"],
        "candidate_low_level_blds_not_yet_promoted_to_contract": report[
            "candidate_low_level_blds_not_yet_promoted_to_contract"
        ],
        "source_route_policy": report["source_route_policy"],
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


def _write_report(report: dict[str, Any], *, request_authorized: bool) -> None:
    final = _finalise_report(report, request_authorized=request_authorized)
    (OUT / "summary.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("KRX_STATUS_SOURCE_PROBE=" + json.dumps(final, ensure_ascii=False), flush=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
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
        "purpose": "OFFICIAL_KRX_STATUS_SOURCE_FEASIBILITY_ONLY_NOT_PERFORMANCE_RESEARCH",
        "numeric_market_data_persisted": False,
        "credentials_present": session_credentials_present,
        "data_marketplace_session_credentials_present": session_credentials_present,
        "official_openapi_auth_key_present": openapi_key_present,
        "authorization_evidence_reference_present": preflight["authorization_evidence_reference_present"],
        "authorization_evidence": evidence_summary,
        "explicit_probe_consent_present": preflight["explicit_probe_consent_present"],
        "authorization_preflight": preflight,
        "active_probe_access_route": DATA_MARKETPLACE_ROUTE,
        "openapi_route_status": (
            "KEY_PRESENT_BUT_REQUIRED_STATUS_API_MAPPING_NOT_ESTABLISHED"
            if openapi_key_present
            else "AUTH_KEY_NOT_CONFIGURED_AND_REQUIRED_STATUS_API_MAPPING_NOT_ESTABLISHED"
        ),
        "source_route_policy": {
            "data_marketplace_session": "KRX_ID/KRX_PW, a matching validated non-secret authorization-evidence record that explicitly authorizes automated collection, and exact explicit per-run consent are required for the tiny authenticated Data Marketplace source-feasibility check",
            "official_openapi": "AUTH_KEY is a separate KRX OpenAPI credential and may be used only after the exact required API service is identified and approved",
            "no_auth_substitution": True,
            "push_is_dry_run_only": True,
        },
        "pinned_krx_data_api_commit": PINNED_KRX_DATA_API,
        "official_screen_contracts": {
            "trading_halt": "MDCSTAT213 / KRX issue statistics trading-halt history",
            "cleanup_trading": "MDCSTAT237 / KRX cleanup-trading status",
            "delisted": "MDCSTAT238 / KRX delisted-security status",
            "delisted_price": "MDCSTAT239 / KRX delisted-security price trend",
        },
        "candidate_low_level_blds_not_yet_promoted_to_contract": {
            "trading_halt": "dbms/MDC/STAT/issue/MDCSTAT21301",
            "cleanup_trading": "dbms/MDC/STAT/issue/MDCSTAT23701",
        },
        "status": "PENDING" if request_authorized else "AUTHORIZATION_OR_CONSENT_PREFLIGHT_BLOCKED",
        "judge_security_status_ready": False,
        "why_not_judge_ready": [
            "exact official access/product contract for historical halt/cleanup/delisting data is not yet established",
            "historical common-stock identity coverage not yet reconstructed and audited on real data",
            "event_time/published_at/available_at/ingested_at lineage not yet complete",
            "halt/cleanup/delisting event and execution economics not yet joined to decisions",
        ],
    }

    if not request_authorized:
        _write_report(report, request_authorized=False)
        return

    from krx_data_api import fetch, get_krx_auth, transport

    probes: list[dict[str, Any]] = []
    probes.append(_try("listed_stocks_current_identity", lambda: fetch("listed_stocks", auth=True)))
    probes.append(_try(
        "new_listing_history_sample",
        lambda: fetch("new_listing", strtDd="20240101", endDd="20241231", auth=True),
    ))
    probes.append(_try(
        "delisted_history_sample",
        lambda: fetch("delisted", strtDd="20240101", endDd="20241231", auth=True),
    ))

    session = get_krx_auth().session

    def halt_probe():
        payload = transport.json_data(
            "dbms/MDC/STAT/issue/MDCSTAT21301",
            {
                "isuCd": "KR7000300004",
                "isuCd2": "000300",
                "strtDd": "20240101",
                "endDd": "20251231",
            },
            session=session,
            menu_id="MDC0202",
        )
        import pandas as pd
        return pd.DataFrame(payload.get("output") or payload.get("OutBlock_1") or [])

    def cleanup_probe():
        payload = transport.json_data(
            "dbms/MDC/STAT/issue/MDCSTAT23701",
            {"mktId": "ALL"},
            session=session,
            menu_id="MDC0202",
        )
        import pandas as pd
        return pd.DataFrame(payload.get("output") or payload.get("OutBlock_1") or [])

    probes.append(_try("trading_halt_candidate_bld", halt_probe))
    probes.append(_try("cleanup_trading_candidate_bld", cleanup_probe))

    report["probes"] = probes
    catalog_ok = all(
        p.get("reachable") for p in probes
        if p["name"] in {
            "listed_stocks_current_identity",
            "new_listing_history_sample",
            "delisted_history_sample",
        }
    )
    candidate_ok = all(
        p.get("reachable") for p in probes
        if p["name"] in {"trading_halt_candidate_bld", "cleanup_trading_candidate_bld"}
    )
    report["status"] = (
        "SOURCE_FAMILIES_REACHABLE_NEEDS_HISTORICAL_PIT_AUDIT"
        if catalog_ok and candidate_ok
        else "PARTIAL_OR_UNVERIFIED_SOURCE_ACCESS"
    )
    report["candidate_blds_live_validated"] = bool(candidate_ok)
    report["judge_security_status_ready"] = False
    _write_report(report, request_authorized=True)


if __name__ == "__main__":
    main()
