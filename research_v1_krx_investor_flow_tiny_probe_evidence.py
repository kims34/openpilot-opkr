"""Fail-closed validator for authenticated KRX investor-flow tiny-probe evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_INVESTOR_FLOW_TINY_PROBE_EVIDENCE.json")


class KRXInvestorFlowTinyProbeEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXInvestorFlowTinyProbeEvidenceError(msg)


def validate_investor_flow_tiny_probe_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "unsupported schema_version")
    _require(data.get("evidence_class") == "AUTHENTICATED_METADATA_ONLY_TINY_PROBE", "unexpected evidence_class")
    _require(data.get("source_family") == "KRX_INVESTOR_FLOW", "source family drift")
    _require(data.get("access_route") == "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION", "route drift")
    _require(data.get("authenticated_request_attempted") is True, "authenticated request evidence missing")
    _require(data.get("numeric_market_data_persisted") is False, "numeric market data must not be persisted")

    auth = data.get("authorization") or {}
    _require(auth.get("permission_state") == "PERMITTED_NO_SEPARATE_APPROVAL", "permission state drift")
    _require(auth.get("automated_collection_authorized") is True, "automation permission missing")
    _require(auth.get("explicit_probe_consent_present") is True, "explicit consent evidence missing")
    _require(auth.get("request_attempt_authorized") is True, "request authorization evidence missing")

    probe = data.get("probe") or {}
    _require(probe.get("bld") == "dbms/MDC/STAT/standard/MDCSTAT02303", "BLD drift")
    _require(probe.get("security") == "005930", "probe security drift")
    _require(probe.get("window") == ["2026-09-21","2026-09-23"], "probe window drift")
    _require(probe.get("rows") == 3, "row count drift")
    expected = {"일자","금융투자","보험","투신","사모","은행","기타금융","연기금 등","기타법인","개인","외국인","기타외국인","전체"}
    _require(expected.issubset(set(probe.get("columns") or [])), "observed columns drift")

    pit = data.get("pit_policy") or {}
    _require(pit.get("official_publication_floor") == "20:00 Asia/Seoul", "PIT publication floor drift")

    gates = data.get("gate_state_after_probe") or {}
    _require(gates == {
        "A": "PARTIAL",
        "B": "PARTIAL",
        "C": "BLOCKED",
        "D": "PARTIAL",
        "E": "PARTIAL",
        "F": "PARTIAL",
    }, "gate state drift")

    authority = data.get("authority") or {}
    for key in (
        "source_contract_closed_for_declared_scope",
        "feature_performance_testing_authorized",
        "alpha_or_final_judge_promotion_authorized",
        "bulk_historical_acquisition_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    fps = data.get("fingerprints") or {}
    for key in (
        "authorization_record_sha256",
        "public_contract_evidence_sha256",
        "probe_contract_sha256",
        "probe_result_sha256",
    ):
        v = str(fps.get(key) or "")
        _require(len(v) == 64 and all(ch in "0123456789abcdef" for ch in v), f"{key} invalid")

    return {
        "valid": True,
        "gate_a": "PARTIAL",
        "gate_b": "PARTIAL",
        "gate_c": "BLOCKED",
        "gate_d": "PARTIAL",
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_investor_flow_tiny_probe_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
