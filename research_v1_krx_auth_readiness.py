"""Network-free readiness check for future KRX authenticated source probes.

This module intentionally cannot authorize or perform a KRX request. It checks
only whether route-specific credential presence and a non-secret authorization
evidence reference are configured for a future manually consented tiny probe.

The explicit request-consent environment is forcibly cleared before the shared
preflight is evaluated, even if the caller supplied it. Secret values are never
included in the output.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from research_v1_krx_auth_preflight import (
    DATA_MARKETPLACE_ROUTE,
    EXPLICIT_PROBE_CONSENT_ENV,
    evaluate_auth_preflight,
)
from research_v1_krx_public_evidence import (
    PUBLIC_EVIDENCE_VERSION,
    public_evidence_fingerprint_sha256,
)


OUT = Path("research_results/krx_auth_readiness")


def _sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_readiness_report(
    *,
    environment: Mapping[str, str | None],
    authorization_evidence_reference: str | None,
) -> dict[str, Any]:
    """Return secret-free configuration readiness for the Data Marketplace path."""
    safe_environment = {
        "KRX_ID": environment.get("KRX_ID"),
        "KRX_PW": environment.get("KRX_PW"),
        "KRX_OPENAPI_AUTH_KEY": environment.get("KRX_OPENAPI_AUTH_KEY"),
        # Deliberately ignore any caller-provided consent value. This readiness
        # check must remain non-networking by construction.
        EXPLICIT_PROBE_CONSENT_ENV: "",
    }
    preflight = evaluate_auth_preflight(
        source_family="KRX_INVESTOR_FLOW",
        access_route=DATA_MARKETPLACE_ROUTE,
        environment=safe_environment,
        authorization_evidence_reference=authorization_evidence_reference,
    )
    configured = bool(
        preflight["route_credentials_complete"]
        and preflight["authorization_evidence_reference_present"]
    )
    public_fp = public_evidence_fingerprint_sha256()
    report: dict[str, Any] = {
        "purpose": "KRX_CONFIGURATION_READINESS_ONLY_NO_NETWORK_REQUEST",
        "access_route": DATA_MARKETPLACE_ROUTE,
        "krx_id_present": preflight["krx_id_present"],
        "krx_pw_present": preflight["krx_pw_present"],
        "openapi_auth_key_present": preflight["openapi_auth_key_present"],
        "authorization_evidence_reference_present": preflight[
            "authorization_evidence_reference_present"
        ],
        "explicit_probe_consent_forced_off": True,
        "route_credentials_complete": preflight["route_credentials_complete"],
        "configuration_ready_for_manual_authenticated_probe": configured,
        "request_attempt_authorized": False,
        "authenticated_request_attempted": False,
        "network_request_attempted": False,
        "remaining_requirements_before_manual_probe": (
            ["EXPLICIT_TINY_REQUEST_CONSENT"]
            if configured
            else list(preflight["missing_requirements"])
        ),
        "public_contract_evidence_version": PUBLIC_EVIDENCE_VERSION,
        "public_contract_evidence_fingerprint_sha256": public_fp,
        "bulk_historical_acquisition_authorized": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "alpha_or_final_judge_promotion_authorized": False,
        "live_trading_authorized": False,
    }
    report["readiness_fingerprint_sha256"] = _sha256(report)
    report["guardrail"] = (
        "This report checks configuration presence only. It forcibly disables explicit request consent, "
        "performs no KRX network request and grants no source, research, holdout, promotion or trading authority."
    )
    return report


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_readiness_report(
        environment={
            "KRX_ID": os.getenv("KRX_ID"),
            "KRX_PW": os.getenv("KRX_PW"),
            "KRX_OPENAPI_AUTH_KEY": os.getenv("KRX_OPENAPI_AUTH_KEY"),
            EXPLICIT_PROBE_CONSENT_ENV: os.getenv(EXPLICIT_PROBE_CONSENT_ENV),
        },
        authorization_evidence_reference=os.getenv("KRX_AUTH_EVIDENCE_REF"),
    )
    (OUT / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("KRX_AUTH_READINESS=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
