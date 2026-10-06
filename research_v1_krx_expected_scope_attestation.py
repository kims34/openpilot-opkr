"""Fail-closed validator and offline planner for KRX expected-scope attestation.

No network access is performed here. Calendar dates are enumeration candidates,
not assumed trading sessions. Official trading dates are discovered only later
from authenticated KRX daily-trade responses.
"""
from __future__ import annotations

from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

CONTRACT_PATH = Path("INDEXALERT_KRX_EXPECTED_SCOPE_ATTESTATION_CONTRACT.json")
CONTRACT_ID = "INDEXALERT-KRX-EXPECTED-SCOPE-ATTESTATION-v1"
BOUND_PLAN_ID = "INDEXALERT-KRX-HIST-ACQ-v3"
START = date(2015, 6, 15)
END = date(2026, 10, 1)
EXPECTED_CALENDAR_DATES = 4127


class KRXExpectedScopeAttestationError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXExpectedScopeAttestationError(msg)


def _sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("contract_id") == CONTRACT_ID, "contract_id drift")
    _require(data.get("bound_historical_plan_id") == BOUND_PLAN_ID, "plan binding drift")

    period = data.get("research_period") or {}
    _require(period.get("start") == START.isoformat(), "research start drift")
    _require(period.get("end") == END.isoformat(), "research end drift")
    _require(period.get("calendar_date_count") == EXPECTED_CALENDAR_DATES, "calendar-date count drift")
    _require(period.get("market") == "KOSPI", "market drift")

    sources = data.get("official_attestation_sources") or {}
    daily = sources.get("trading_date_and_trade_scope") or {}
    master = sources.get("same_date_security_identity") or {}
    _require(daily.get("endpoint") == "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd", "daily-trade endpoint drift")
    _require(master.get("endpoint") == "https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info", "basic-info endpoint drift")
    _require(daily.get("method") == "GET" and master.get("method") == "GET", "OpenAPI method drift")
    _require(daily.get("date_parameter") == "basDd", "daily-trade date parameter drift")
    _require(master.get("date_parameter") == "basDd", "basic-info date parameter drift")
    _require("never infer a trading calendar" in str(daily.get("sweep_rule") or ""), "no-invented-calendar guard lost")
    _require("non-empty" in str(daily.get("trading_date_rule") or ""), "non-empty trading-date rule lost")
    _require("ISU_CD" in str(master.get("stable_join_rule") or ""), "stable join rule lost")
    _require("Name-only" not in str(master.get("stable_join_rule") or ""), "unexpected spelling")
    _require("name-only joins are forbidden" in str(master.get("stable_join_rule") or "").lower(), "name-only join guard lost")

    scope = data.get("expected_scope_rules") or {}
    investor = scope.get("investor_flow") or {}
    status = scope.get("security_status") or {}
    _require(investor.get("output_requires_scope_contract_fingerprint") is True, "investor scope fingerprint requirement lost")
    _require(status.get("output_requires_scope_contract_fingerprint") is True, "status scope fingerprint requirement lost")
    _require(investor.get("key") == ["event_date","symbol","isu_cd"], "investor key drift")
    _require(status.get("key") == ["snapshot_date","symbol","isu_cd"], "status key drift")
    _require("Never add a missing security/date" in str(investor.get("rule") or ""), "investor no-fill guard lost")
    _require("Never infer an identity row" in str(status.get("rule") or ""), "status no-fallback guard lost")

    integrity = data.get("integrity") or {}
    for key in (
        "raw_responses_private_only",
        "every_request_requires_receipt",
        "response_payload_sha256_required",
        "response_schema_sha256_required",
        "exact_requested_date_response_date_consistency_required",
        "mixed_contract_fingerprints_forbidden",
        "expected_scope_must_not_be_derived_from_audited_data_marketplace_rows",
    ):
        _require(integrity.get(key) is True, f"{key} guard lost")

    execution = data.get("execution") or {}
    _require(execution.get("rights_to_use_approved_openapi_services") is True, "OpenAPI rights flag lost")
    _require(execution.get("network_execution_authorized_by_user") is False, "expected-scope network execution illegally authorized")
    _require(execution.get("separate_execution_consent_required") is True, "separate consent guard lost")
    _require(execution.get("execution_consent_env") == "KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT", "consent env drift")
    _require(execution.get("execution_consent_exact_value") == "I_AUTHORIZE_INDEXALERT_KRX_EXPECTED_SCOPE_ATTESTATION_v1", "consent sentinel drift")
    _require(execution.get("default_network_request_attempted") is False, "default network guard lost")

    authority = data.get("authority") or {}
    for key in (
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "contract_id": CONTRACT_ID,
        "calendar_date_count": EXPECTED_CALENDAR_DATES,
        "network_execution_authorized_by_user": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


def build_calendar_discovery_plan() -> list[dict[str, Any]]:
    """Enumerate calendar dates without labeling any date a trading session."""
    validate_file()
    rows = []
    current = START
    while current <= END:
        body = {
            "contract_id": CONTRACT_ID,
            "kind": "daily_trade_scope_discovery",
            "requested_date": current.isoformat(),
            "request": {
                "endpoint": "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd",
                "method": "GET",
                "params": {"basDd": current.strftime("%Y%m%d")},
            },
            "trading_day_assumed": False,
            "network_request_attempted": False,
        }
        rows.append({**body, "task_id": _sha256(body)})
        current += timedelta(days=1)

    _require(len(rows) == EXPECTED_CALENDAR_DATES, "calendar enumeration count drift")
    _require(len({r["task_id"] for r in rows}) == len(rows), "duplicate calendar discovery task")
    return rows


def public_plan_summary() -> dict[str, Any]:
    tasks = build_calendar_discovery_plan()
    return {
        "contract_id": CONTRACT_ID,
        "calendar_date_count": len(tasks),
        "first_date": tasks[0]["requested_date"],
        "last_date": tasks[-1]["requested_date"],
        "task_set_fingerprint_sha256": _sha256(sorted(r["task_id"] for r in tasks)),
        "trading_calendar_inferred": False,
        "network_request_attempted": False,
        "raw_rows_emitted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


if __name__ == "__main__":
    print(json.dumps(public_plan_summary(), ensure_ascii=False, indent=2))
