"""Fail-closed validator for frozen KRX OpenAPI connectivity evidence.

This validates only the metadata evidence file committed by the project.
It never calls KRX, never reads a credential, and never grants source,
performance, holdout, promotion or live-trading authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


EVIDENCE_PATH = Path("INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

EXPECTED_SERVICES = {
    "security_master": {
        "krx_service_name": "유가증권 종목기본정보",
        "endpoint_suffix": "/stk_isu_base_info",
        "required_fields": {
            "ISU_ABBRV","ISU_CD","ISU_ENG_NM","ISU_NM","ISU_SRT_CD",
            "KIND_STKCERT_TP_NM","LIST_DD","LIST_SHRS","MKT_TP_NM",
            "PARVAL","SECT_TP_NM","SECUGRP_NM",
        },
    },
    "daily_trade": {
        "krx_service_name": "유가증권 일별매매정보",
        "endpoint_suffix": "/stk_bydd_trd",
        "required_fields": {
            "ACC_TRDVAL","ACC_TRDVOL","BAS_DD","CMPPREVDD_PRC","FLUC_RT",
            "ISU_CD","ISU_NM","LIST_SHRS","MKTCAP","MKT_NM","SECT_TP_NM",
            "TDD_CLSPRC","TDD_HGPRC","TDD_LWPRC","TDD_OPNPRC",
        },
    },
}

AUTHORITY_FALSE_FIELDS = {
    "krx_source_contract_closed",
    "judge_security_status_ready",
    "investor_flow_feature_testing_authorized",
    "alpha_or_final_judge_promotion_authorized",
    "sealed_holdout_authorized",
    "live_trading_authorized",
}

REQUIRED_NOT_PROVEN = {
    "complete historical coverage",
    "record-level point-in-time availability lineage",
    "trading-halt history",
    "cleanup-trading history",
    "actual delisting history",
    "exact delisting or forced-liquidation economics",
    "investor-by-security flow access",
    "research-grade immutable acquisition receipts for full history",
    "intended-use rights beyond the separately audited OpenAPI terms and exact approved service scope",
}

SECRET_MARKERS = (
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "cookie",
    "bearer",
)


class KRXOpenAPIEvidenceError(ValueError):
    pass


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise KRXOpenAPIEvidenceError(message)


def validate_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(str(data.get("schema_version")) in {"1","2"}, "unsupported evidence schema_version")
    _require(
        str(data.get("evidence_class")) == "AUTHENTICATED_CONNECTIVITY_AND_SCHEMA_ONLY",
        "unexpected evidence_class",
    )

    commit = str(data.get("production_server_commit") or "")
    _require(bool(COMMIT_RE.fullmatch(commit)), "production_server_commit must be a 40-hex SHA")
    _require(isinstance(data.get("github_action_run_id"), int), "github_action_run_id must be integer")
    _require(isinstance(data.get("github_action_job_id"), int), "github_action_job_id must be integer")
    request_date = str(data.get("request_date") or "")
    _require(len(request_date) == 8 and request_date.isdigit(), "request_date must be YYYYMMDD")

    auth = data.get("authentication") or {}
    _require(auth.get("route") == "KRX_OPENAPI", "authentication route mismatch")
    _require(auth.get("header_name") == "AUTH_KEY", "authentication header mismatch")
    _require(auth.get("secret_value_recorded") is False, "secret value must never be recorded")
    _require(auth.get("production_environment_secret_present") is True, "production key presence evidence missing")

    services = data.get("services") or {}
    _require(set(services) == set(EXPECTED_SERVICES), "unexpected or missing services")
    for name, expected in EXPECTED_SERVICES.items():
        row = services[name]
        _require(row.get("krx_service_name") == expected["krx_service_name"], f"{name} service name mismatch")
        _require(str(row.get("endpoint") or "").endswith(expected["endpoint_suffix"]), f"{name} endpoint mismatch")
        _require(row.get("method") == "GET", f"{name} method must be GET")
        _require(row.get("http_status") == 200, f"{name} http_status must be 200")
        _require(row.get("json_parsed") is True, f"{name} JSON parse evidence missing")
        _require(isinstance(row.get("row_count"), int) and row["row_count"] > 0, f"{name} row_count invalid")
        _require(row.get("schema_ok") is True, f"{name} schema_ok must be true")
        fields = set(row.get("fields") or [])
        _require(expected["required_fields"].issubset(fields), f"{name} required fields missing")

        if str(data.get("schema_version")) == "2":
            for key in ("response_schema_sha256","response_payload_sha256"):
                value = str(row.get(key) or "").lower()
                _require(bool(SHA256_RE.fullmatch(value)), f"{name} {key} invalid")
            _require(isinstance(row.get("observed_at"), str) and row["observed_at"], f"{name} observed_at missing")

    authority = data.get("authority") or {}
    _require(set(authority) == AUTHORITY_FALSE_FIELDS, "authority field set drifted")
    for field in AUTHORITY_FALSE_FIELDS:
        _require(authority.get(field) is False, f"{field} illegally true")

    not_proven = set(data.get("not_proven") or [])
    _require(REQUIRED_NOT_PROVEN.issubset(not_proven), "not_proven boundary weakened")

    serialized = json.dumps(data, ensure_ascii=False).lower()
    for marker in SECRET_MARKERS:
        _require(f"{marker}=" not in serialized, f"secret-like material found: {marker}")

    return {
        "valid": True,
        "schema_version": str(data["schema_version"]),
        "evidence_id": str(data.get("evidence_id") or ""),
        "evidence_fingerprint_sha256": _canonical_sha256(data),
        "source_contract_closed": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = EVIDENCE_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return validate_evidence(data)


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
