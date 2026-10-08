"""Read-only Kiwoom credential-mode probe.

Attempts OAuth client-credentials issuance against Kiwoom REAL and DEMO hosts
using the same in-memory credentials. Emits only booleans and numeric codes.
Never prints credentials, tokens, return messages, account data, IPs or orders.
"""
from __future__ import annotations
import json
import os
import re
from typing import Any, Mapping
import requests

HOSTS = {
    "REAL": "https://api.kiwoom.com",
    "DEMO": "https://mockapi.kiwoom.com",
}
FALSE_VALUES = frozenset({"0","false","off","no"})


def _strict_object(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("object required")
    return value


def _detail_code(message: Any) -> int | None:
    text = "" if message is None else str(message)
    match = re.search(r"(?:\[|CODE=)(\d{3,5})(?::|\b)", text)
    return int(match.group(1)) if match else None


def attempt(base: str, app_key: str, app_secret: str) -> dict[str, Any]:
    try:
        response = requests.post(
            base + "/oauth2/token",
            headers={"Content-Type":"application/json;charset=UTF-8"},
            json={
                "grant_type":"client_credentials",
                "appkey":app_key,
                "secretkey":app_secret,
            },
            timeout=15,
        )
        obj = _strict_object(response.json())
        code = obj.get("return_code")
        code = code if type(code) is int else None
        token = obj.get("token")
        expiry = obj.get("expires_dt")
        token_type = obj.get("token_type")
        return {
            "http_status": int(response.status_code),
            "return_code": code,
            "detail_code": _detail_code(obj.get("return_msg")),
            "token_present": isinstance(token, str) and bool(token.strip()),
            "expiry_present": isinstance(expiry, str) and bool(expiry.strip()),
            "token_type_present": isinstance(token_type, str) and bool(token_type.strip()),
        }
    except Exception:
        return {
            "http_status": None,
            "return_code": None,
            "detail_code": None,
            "token_present": False,
            "expiry_present": False,
            "token_type_present": False,
        }


def main() -> None:
    if str(os.getenv("KIWOOM_ORDERING_ENABLED") or "").strip().lower() not in FALSE_VALUES:
        raise SystemExit("ordering must remain disabled")
    key = str(os.getenv("KIWOOM_APP_KEY") or "")
    secret = str(os.getenv("KIWOOM_APP_SECRET") or "")
    if not key.strip() or not secret.strip():
        raise SystemExit("credentials are not configured")
    result = {
        "classification":"KIWOOM_TOKEN_MODE_READONLY_DIAGNOSTIC",
        "REAL":attempt(HOSTS["REAL"], key, secret),
        "DEMO":attempt(HOSTS["DEMO"], key, secret),
        "ORDERING":"DISABLED",
        "REAL_ORDERS_AUTHORIZED":False,
        "FUNDS_MOVEMENT_AUTHORIZED":False,
        "PERMISSION_CHANGE_AUTHORIZED":False,
    }
    print(json.dumps(result,sort_keys=True,separators=(",",":")),flush=True)


if __name__ == "__main__":
    main()
