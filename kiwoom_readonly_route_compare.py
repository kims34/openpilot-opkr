"""Local-only paired Kiwoom REAL read-only routing diagnosis.

Usage on the *already registered-IP* Windows PC, with local environment keys:
    python kiwoom_readonly_route_compare.py

Do not run on GitHub Actions or Railway. No real orders, positions, trading
authority, public-IP probing, credential/key printing, or provider response
body logging. Calls Kiwoom's token, account identity and WS Type00 endpoints
through the established fail-closed smoke. At most two sequential runs; the
direct comparison is skipped unless the system route hits a WS blocker.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping

SMOKE_FILE = Path(__file__).resolve().with_name("kiwoom_real_type00_readonly_smoke.py")
_ALLOWED_STAGES = frozenset({
    "INIT", "CONFIG", "TOKEN", "TOKEN_PROTOCOL", "TOKEN_CANONICALITY",
    "ACCOUNT", "ACCOUNT_PROTOCOL", "NON_TEXT_WEBSOCKET_FRAME",
    "WEBSOCKET_FRAME_TOO_LARGE", "WS_LOGIN_PROTOCOL", "WS_LOGIN",
    "WS_LOGIN_TIMEOUT", "WS_TIMEOUT", "LOCAL_COMPATIBILITY_OR_NETWORK",
    "TYPE00_JSON_PROTOCOL", "TYPE00_REG_PROTOCOL", "TYPE00_REG",
    "TYPE00_FRAME_PROTOCOL", "TYPE00_FRAME_BEFORE_REG_ACK",
    "TYPE00_SUBSCRIPTION_UNOBSERVED", "TYPE00_ADMISSION_INCOMPLETE",
    "TYPE00_ACK_ONLY_NO_EVENTS", "REAL_TYPE00_READ_ONLY_SMOKE",
})
_ALLOWED_ERRORS = frozenset({
    "INVALID_CREDENTIALS", "INVALID_TOKEN", "MODE_MISMATCH",
    "TOKEN_OR_LOGIN_AUTH", "DEVICE_AUTH", "UNCLASSIFIED",
})
_BOOLEAN_FIELDS = (
    "TOKEN_OK", "ACCOUNT_ENDPOINT_OK", "WS_CONNECTED", "WS_LOGIN_OK",
    "TYPE00_REG_SENT", "TYPE00_REG_ACK_OK",
    "REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN",
    "REST_CONFIGURED_PROXY_PRESENT", "WS_SYSTEM_CONFIGURED_PROXY_PRESENT",
    "REST_WS_CONFIGURED_PROXY_URLS_EQUAL",
)
_SUMMARY_FIELDS = (
    "STAGE", "RETURN_CODE", "DETAIL_CODE", "ERROR_CLASS",
    "WS_PROXY_POLICY", *_BOOLEAN_FIELDS,
)
_FALSE_VALUES = frozenset({"0", "false", "off", "no"})


class DiagnosticError(ValueError):
    """Error without provider payload, credential or secret contents."""


def _preflight(env: Mapping[str, str]) -> None:
    if env.get("KIWOOM_ENV") != "REAL":
        raise DiagnosticError("CONFIG_REAL_REQUIRED")
    if env.get("KIWOOM_BASE_URL") != "https://api.kiwoom.com":
        raise DiagnosticError("CONFIG_REAL_HOST_REQUIRED")
    if str(env.get("KIWOOM_ORDERING_ENABLED") or "").strip().lower() not in _FALSE_VALUES:
        raise DiagnosticError("ORDERING_MUST_BE_DISABLED")
    if not str(env.get("KIWOOM_APP_KEY") or "").strip() or not str(env.get("KIWOOM_APP_SECRET") or "").strip():
        raise DiagnosticError("LOCAL_CREDENTIALS_NOT_FOUND")
    if not SMOKE_FILE.is_file():
        raise DiagnosticError("READONLY_SMOKE_FILE_NOT_FOUND")


def _safe_summary(stdout: str, returncode: int, policy: str) -> dict[str, Any]:
    if returncode not in {0, 2, 3} or len(stdout.encode("utf-8", "ignore")) > 16_384:
        raise DiagnosticError("INVALID_LOCAL_SMOKE_EXIT")
    try:
        obj = json.loads(stdout.strip())
    except Exception:
        raise DiagnosticError("INVALID_LOCAL_SMOKE_JSON") from None
    if not isinstance(obj, dict):
        raise DiagnosticError("INVALID_LOCAL_SMOKE_STRUCTURE")
    stage = obj.get("STAGE")
    if not isinstance(stage, str) or stage not in _ALLOWED_STAGES:
        raise DiagnosticError("INVALID_LOCAL_SMOKE_STAGE")
    error_class = obj.get("ERROR_CLASS")
    if error_class is not None and (
        not isinstance(error_class, str) or error_class not in _ALLOWED_ERRORS
    ):
        raise DiagnosticError("INVALID_LOCAL_SMOKE_ERROR_CLASS")
    for key in _SUMMARY_FIELDS:
        if key not in obj:
            raise DiagnosticError("MISSING_LOCAL_SMOKE_FIELD")
    count = obj.get("TYPE00_EVENT_COUNT")
    if type(count) is not int or count < 0:
        raise DiagnosticError("INVALID_LOCAL_SMOKE_EVENT_COUNT")
    for key in ("RETURN_CODE", "DETAIL_CODE"):
        value = obj.get(key)
        if key == "DETAIL_CODE" and value is None:
            continue
        if type(value) is not int or not -1 <= value <= 2_147_483_647:
            raise DiagnosticError("INVALID_LOCAL_SMOKE_CODE")
    for key in _BOOLEAN_FIELDS:
        if obj.get(key) is not None and type(obj[key]) is not bool:
            raise DiagnosticError("INVALID_LOCAL_SMOKE_BOOLEAN")
    for flag in ("REAL_ORDERS_AUTHORIZED", "FUNDS_MOVEMENT_AUTHORIZED",
                 "PERMISSION_CHANGE_AUTHORIZED", "GENUINE_LIVE_PROVENANCE_VERIFIED"):
        if obj.get(flag) is not False:
            raise DiagnosticError("UNSAFE_OR_INCONSISTENT_LOCAL_SMOKE")
    if obj.get("ORDERING") != "DISABLED" or obj.get("WS_PROXY_POLICY") != policy.upper():
        raise DiagnosticError("UNSAFE_OR_INCONSISTENT_LOCAL_SMOKE")
    if returncode == 0 and (stage != "REAL_TYPE00_READ_ONLY_SMOKE" or not obj.get("WS_LOGIN_OK")
                            or not obj.get("TYPE00_REG_ACK_OK")
                            or not obj.get("TYPE00_EVENT_COUNT", 0) > 0):
        raise DiagnosticError("UNSAFE_OR_INCONSISTENT_LOCAL_SMOKE")
    if returncode == 3 and stage != "TYPE00_ACK_ONLY_NO_EVENTS":
        raise DiagnosticError("INVALID_INCONCLUSIVE_LOCAL_SMOKE")
    return {key: obj[key] for key in _SUMMARY_FIELDS}


def _run_once(policy: str, env: Mapping[str, str]) -> dict[str, Any]:
    child_env = dict(env)
    child_env["KIWOOM_WS_PROXY_POLICY"] = policy
    # Suppress stderr entirely and never forward raw stdout: providers, proxies
    # or local tracebacks may otherwise leak network/credential detail.
    try:
        done = subprocess.run(
            [sys.executable, "-B", str(SMOKE_FILE)],
            cwd=str(SMOKE_FILE.parent),
            env=child_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=100,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise DiagnosticError("LOCAL_SMOKE_EXECUTION_FAILED") from None
    return _safe_summary(done.stdout, done.returncode, policy)


def _interpret(base: Mapping[str, Any], direct: Mapping[str, Any] | None) -> str:
    if not base["TOKEN_OK"] or not base["ACCOUNT_ENDPOINT_OK"]:
        return "REST_PRECONDITION_NOT_MET"
    if base["WS_LOGIN_OK"]:
        return "WS_LOGIN_ALREADY_OK_NO_ROUTE_COMPARISON"
    if direct is None:
        return "WS_BLOCKER_NOT_ROUTE_COMPARABLE"
    if direct["WS_LOGIN_OK"] and not base["WS_LOGIN_OK"]:
        return "ROUTE_DEPENDENT_OUTCOME_POSSIBLE"
    if (base["STAGE"] == "WS_LOGIN" and direct["STAGE"] == "WS_LOGIN"
            and base["DETAIL_CODE"] == 8050 and direct["DETAIL_CODE"] == 8050):
        return "8050_PERSISTS_IN_BOTH_WS_MODES"
    return "DIFFERENCE_INCONCLUSIVE"


def _eligible_for_direct(base: Mapping[str, Any]) -> bool:
    return bool(
        base["TOKEN_OK"] and base["ACCOUNT_ENDPOINT_OK"]
        and not base["WS_LOGIN_OK"]
        and base["STAGE"] in {
            "WS_LOGIN", "WS_LOGIN_TIMEOUT",
            "WS_TIMEOUT", "LOCAL_COMPATIBILITY_OR_NETWORK",
        }
    )


def main() -> None:
    try:
        env = dict(os.environ)
        _preflight(env)
        base = _run_once("system", env)
        direct = _run_once("direct", env) if _eligible_for_direct(base) else None
        print(json.dumps({
            "classification": "KIWOOM_REGISTERED_PC_READONLY_WS_ROUTE_COMPARISON",
            "system": base, "direct": direct,
            "assessment": _interpret(base, direct),
            "broker_connected": bool(base["WS_LOGIN_OK"] or (direct and direct["WS_LOGIN_OK"])),
            "real_orders_authorized": False,
            "funds_movement_authorized": False,
            "trading_readiness_proven": False,
        }, sort_keys=True, separators=(",", ":")))
    except DiagnosticError as exc:
        print(json.dumps({
            "classification": "KIWOOM_REGISTERED_PC_READONLY_WS_ROUTE_COMPARISON",
            "assessment": str(exc),
            "broker_connected": False,
            "real_orders_authorized": False,
            "funds_movement_authorized": False,
            "trading_readiness_proven": False,
        }, sort_keys=True, separators=(",", ":")))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
