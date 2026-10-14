"""Local-only paired Kiwoom REAL read-only routing diagnosis.

Usage on the *already registered-IP* Windows PC, with local environment keys:
    python kiwoom_readonly_route_compare.py

Do not run on GitHub Actions or Railway. No real orders, positions, trading
authority, public-IP probing, credential/key printing, or provider response
body logging. Calls Kiwoom's token, account identity and WS Type00 endpoints
through the established fail-closed smoke. One OAuth token and REST account
lookup are reused in memory; at most two sequential WebSocket connections,
with the direct comparison skipped unless the system route hits a WS blocker.
"""
from __future__ import annotations

import asyncio
from dataclasses import asdict
import json
import os
from pathlib import Path
from typing import Any, Mapping

import kiwoom_real_type00_readonly_smoke as smoke

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


_REST_PROOF_FIELDS = (
    "TOKEN_OK", "ACCOUNT_ENDPOINT_OK", "REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN",
    "TOKEN_CANONICAL_NO_EDGE_WHITESPACE", "TOKEN_EXPIRY_FIELD_PRESENT",
    "TOKEN_TYPE_FIELD_PRESENT", "REST_CONFIGURED_PROXY_PRESENT",
    "WS_SYSTEM_CONFIGURED_PROXY_PRESENT", "REST_WS_CONFIGURED_PROXY_URLS_EQUAL",
)


def _attempt(policy: str, prepared: tuple | None = None) -> tuple[dict[str, Any], tuple | None]:
    """Use one OAuth token and one REST account lookup across both WS routes.

    All token/account information stays in process memory; only validated,
    redacted state is returned to the report.  No subprocess, stderr, or
    credentials file is used.
    """
    state = smoke.SmokeState()
    state.WS_PROXY_POLICY = policy.upper()
    old_policy = os.environ.get("KIWOOM_WS_PROXY_POLICY")
    os.environ["KIWOOM_WS_PROXY_POLICY"] = policy
    try:
        if prepared is None:
            token, account, issued = smoke._token_and_account(state)
            # Reuse this exact issued token for the alternate WebSocket
            # route, rather than reissuing a new OAuth token and confounding
            # the network-path comparison.
            proof = {name: getattr(state, name) for name in _REST_PROOF_FIELDS}
            prepared = (token, account, issued, proof)
        else:
            token, account, issued, proof = prepared
            for name in _REST_PROOF_FIELDS:
                setattr(state, name, proof[name])
        asyncio.run(smoke._run_ws(token, account, issued, state))
        if not (
            state.TOKEN_OK
            and state.ACCOUNT_ENDPOINT_OK
            and state.REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN
            and state.WS_LOGIN_OK
            and state.TYPE00_REG_SENT
            and state.TYPE00_REG_ACK_OK
        ):
            raise smoke.ReadOnlySmokeError("TYPE00_ADMISSION_INCOMPLETE", 0)
        if state.TYPE00_EVENT_COUNT == 0:
            state.STAGE = "TYPE00_ACK_ONLY_NO_EVENTS"
            state.RETURN_CODE = 0
            exit_code = 3
        else:
            state.STAGE = "REAL_TYPE00_READ_ONLY_SMOKE"
            state.RETURN_CODE = 0
            exit_code = 0
    except smoke.ReadOnlySmokeError as exc:
        state.STAGE = exc.stage
        state.RETURN_CODE = exc.return_code
        state.DETAIL_CODE = exc.detail_code
        state.ERROR_CLASS = exc.error_class
        exit_code = 2
    except Exception:
        # Never emit untrusted errors or tracebacks; they can include
        # credentials, proxy details and original broker response bodies.
        state.STAGE = "LOCAL_COMPATIBILITY_OR_NETWORK"
        state.RETURN_CODE = -1
        exit_code = 2
    finally:
        if old_policy is None:
            os.environ.pop("KIWOOM_WS_PROXY_POLICY", None)
        else:
            os.environ["KIWOOM_WS_PROXY_POLICY"] = old_policy

    # Prevent accidentally promoting malformed provenance or true-order
    # authority. Fail-closed local state never passes the safe report parser.
    summary = _safe_summary(json.dumps(asdict(state)), exit_code, policy)
    return summary, prepared


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
        base, prepared = _attempt("system")
        direct, _ = _attempt("direct", prepared) if _eligible_for_direct(base) else (None, None)
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
