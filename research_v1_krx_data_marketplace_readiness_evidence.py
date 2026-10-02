"""Fail-closed validator for network-free KRX Data Marketplace readiness evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_DATA_MARKETPLACE_READINESS_EVIDENCE.json")


class KRXReadinessEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXReadinessEvidenceError(msg)


def validate_readiness_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "readiness evidence must be an object")
    _require(data.get("schema_version") == "1", "unsupported schema_version")
    _require(data.get("evidence_class") == "NETWORK_FREE_PRE_AUTH_READINESS_ONLY", "unexpected evidence_class")
    _require(data.get("network_request_attempted") is False, "network request must remain false")

    families = data.get("source_families") or {}
    _require(set(families) == {"KRX_SECURITY_STATUS", "KRX_INVESTOR_FLOW"}, "source family set drift")
    for name, row in families.items():
        for key in (
            "credentials_present",
            "route_credentials_complete",
            "authorization_evidence_reference_present",
            "authorization_evidence_valid_for_declared_tiny_probe",
            "automated_collection_authorized",
            "configuration_ready_for_manual_authenticated_probe",
        ):
            _require(row.get(key) is True, f"{name} {key} must remain true")
        _require(row.get("request_attempt_authorized") is False, f"{name} request must remain unauthorized before consent")
        _require(row.get("remaining_requirements_before_manual_probe") == ["EXPLICIT_TINY_REQUEST_CONSENT"], f"{name} remaining requirement drift")

    auth = data.get("authority") or {}
    _require(auth.get("authenticated_probe_completed") is False, "authenticated probe cannot be claimed complete")
    _require(auth.get("gate_a_pass") is False, "Gate A cannot pass on readiness")
    for key in (
        "bulk_historical_acquisition_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(auth.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "ready_for_explicitly_consented_tiny_probe": True,
        "network_request_attempted": False,
        "authenticated_probe_completed": False,
        "gate_a_pass": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_readiness_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
