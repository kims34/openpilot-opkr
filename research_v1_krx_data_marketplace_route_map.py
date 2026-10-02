"""Fail-closed validator for pinned KRX Data Marketplace route mapping.

This validates only the project's pinned third-party transport map. It never
contacts KRX, never reads credentials, and never grants source or trading
authority.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


PATH = Path("INDEXALERT_KRX_DATA_MARKETPLACE_ROUTE_MAP.json")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

EXPECTED = {
    "trading_halt": ("dbms/MDC/STAT/issue/MDCSTAT21301", "KRX_SECURITY_STATUS"),
    "cleanup_trading": ("dbms/MDC/STAT/issue/MDCSTAT23701", "KRX_SECURITY_STATUS"),
    "delisted_status": ("dbms/MDC/STAT/issue/MDCSTAT23801", "KRX_SECURITY_STATUS"),
    "delisted_price": ("dbms/MDC/STAT/issue/MDCSTAT23902", "KRX_SECURITY_STATUS"),
    "investor_flow_daily": ("dbms/MDC/STAT/standard/MDCSTAT02303", "KRX_INVESTOR_FLOW"),
}

FALSE_AUTHORITY = {
    "official_krx_route_authorized",
    "gate_a_pass",
    "gate_b_pass",
    "bulk_historical_acquisition_authorized",
    "feature_performance_testing_authorized",
    "sealed_holdout_authorized",
    "live_trading_authorized",
}


class KRXRouteMapError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXRouteMapError(msg)


def validate_route_map(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "route map must be an object")
    _require(data.get("schema_version") == "1", "unsupported schema_version")
    _require(
        data.get("evidence_class") == "PINNED_THIRD_PARTY_ROUTE_MAPPING_ONLY",
        "unexpected evidence_class",
    )

    pinned=data.get("pinned_client") or {}
    _require(pinned.get("repository") == "beaten-by-the-market/krx-data-api", "pinned repository drift")
    commit=str(pinned.get("commit") or "")
    _require(bool(COMMIT_RE.fullmatch(commit)), "pinned client commit must be 40-hex")
    _require(commit == "e6ebac9b71482db127348d8a08ebc6743aa3b50e", "pinned client commit drift")
    _require(set(pinned.get("credential_env_names") or []) == {"KRX_ID","KRX_PW"}, "credential env drift")
    _require(pinned.get("session_ttl_seconds") == 1500, "session TTL drift")

    routes=data.get("routes") or {}
    _require(set(routes) == set(EXPECTED), "route set drift")
    for name,(bld,family) in EXPECTED.items():
        row=routes[name]
        _require(row.get("bld") == bld, f"{name} bld drift")
        _require(row.get("source_family") == family, f"{name} source_family drift")
        _require(row.get("mapping_state"), f"{name} mapping_state missing")
        _require(isinstance(row.get("required"), list), f"{name} required fields missing")
    _require(routes["trading_halt"].get("max_period_days") == 730, "trading_halt period limit drift")
    cleanup = routes["cleanup_trading"]
    _require(
        cleanup.get("mapping_state")
        == "PROJECT_AUTHENTICATED_CURRENT_SNAPSHOT_REACHABLE_SCHEMA_OBSERVED_HISTORICAL_WINDOW_NOT_VERIFIED",
        "cleanup route snapshot/historical boundary drift",
    )
    _require(cleanup.get("required") == ["mktId"], "cleanup request contract drift")
    _require(cleanup.get("observed_authenticated_request") == {"mktId": "ALL"}, "cleanup authenticated request drift")
    _require(cleanup.get("historical_date_filter_verified") is False, "cleanup historical-window semantics illegally promoted")
    _require(routes["investor_flow_daily"].get("pit_publication_floor") == "20:00 Asia/Seoul", "investor PIT floor drift")

    auth=data.get("authority") or {}
    _require(set(auth) == FALSE_AUTHORITY, "authority field set drift")
    for key in FALSE_AUTHORITY:
        _require(auth.get(key) is False, f"{key} illegally true")

    guardrails=" ".join(str(x) for x in (data.get("guardrails") or []))
    _require("cannot prove KRX authorization" in guardrails, "authorization guardrail missing")
    _require(
        "historical strtDd/endDd window semantics are not verified" in guardrails,
        "cleanup historical-window guardrail missing",
    )

    return {
        "valid": True,
        "pinned_client_commit": commit,
        "route_count": len(routes),
        "gate_a_pass": False,
        "gate_b_pass": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_route_map(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
