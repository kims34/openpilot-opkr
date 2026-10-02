"""Fail-closed validator for authenticated KRX security/status tiny-probe evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_STATUS_TINY_PROBE_EVIDENCE.json")


class KRXStatusTinyProbeEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXStatusTinyProbeEvidenceError(msg)


def validate_status_tiny_probe_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "unsupported schema_version")
    _require(data.get("evidence_class") == "AUTHENTICATED_METADATA_ONLY_TINY_PROBE", "unexpected evidence_class")
    _require(data.get("source_family") == "KRX_SECURITY_STATUS", "source family drift")
    _require(data.get("access_route") == "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION", "route drift")
    _require(data.get("authenticated_request_attempted") is True, "authenticated request evidence missing")
    _require(data.get("numeric_market_data_persisted") is False, "numeric market data must not be persisted")

    auth = data.get("authorization") or {}
    _require(auth.get("permission_state") == "PERMITTED_NO_SEPARATE_APPROVAL", "permission state drift")
    _require(auth.get("automated_collection_authorized") is True, "automation permission missing")
    _require(auth.get("explicit_probe_consent_present") is True, "explicit consent evidence missing")
    _require(auth.get("request_attempt_authorized") is True, "request authorization evidence missing")

    probes = {row.get("name"): row for row in (data.get("probes") or [])}
    for name in (
        "listed_stocks_current_identity",
        "new_listing_history_sample",
        "delisted_history_sample",
        "trading_halt_candidate_bld",
        "cleanup_trading_candidate_bld",
    ):
        _require(name in probes, f"{name} missing")
        _require(probes[name].get("reachable") is True, f"{name} not reachable")
        _require(isinstance(probes[name].get("rows"), int) and probes[name]["rows"] > 0, f"{name} rows invalid")

    _require(probes["trading_halt_candidate_bld"].get("bld") == "dbms/MDC/STAT/issue/MDCSTAT21301", "trading halt BLD drift")
    _require(probes["cleanup_trading_candidate_bld"].get("bld") == "dbms/MDC/STAT/issue/MDCSTAT23701", "cleanup BLD drift")
    _require(data.get("candidate_blds_live_validated") is True, "candidate BLD validation missing")

    gates = data.get("gate_state_after_probe") or {}
    _require(gates == {
        "A": "PARTIAL",
        "B": "PARTIAL",
        "C": "BLOCKED",
        "D": "BLOCKED",
        "E": "PARTIAL",
        "F": "PARTIAL",
    }, "gate state drift")

    authority = data.get("authority") or {}
    for key in (
        "judge_security_status_ready",
        "source_contract_closed_for_declared_scope",
        "alpha_or_final_judge_promotion_authorized",
        "bulk_historical_acquisition_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    fps = data.get("fingerprints") or {}
    for key in ("public_contract_evidence_sha256", "probe_contract_sha256", "probe_result_sha256"):
        v = str(fps.get(key) or "")
        _require(len(v) == 64 and all(ch in "0123456789abcdef" for ch in v), f"{key} invalid")

    return {
        "valid": True,
        "gate_a": "PARTIAL",
        "gate_b": "PARTIAL",
        "gate_c": "BLOCKED",
        "gate_d": "BLOCKED",
        "judge_security_status_ready": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_status_tiny_probe_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
