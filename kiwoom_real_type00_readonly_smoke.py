"""One-shot Kiwoom REAL read-only WebSocket authentication smoke.

Safety boundary:
- REAL OAuth token issuance
- read-only ka00001 account identity lookup
- WebSocket LOGIN with the exact freshly issued in-memory token
- type00 REG subscription only
- no order/create/amend/cancel, no funds movement, no permission changes
- output is redacted booleans/counts/codes only

This module is intentionally independent of IndexAlert order-sender code.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import os
import re
import sys
import time
from typing import Any, Mapping

import requests
import websockets


REAL_BASE_URL = "https://api.kiwoom.com"
TOKEN_URL = REAL_BASE_URL + "/oauth2/token"
ACCOUNT_URL = REAL_BASE_URL + "/api/dostk/acnt"
WS_URL = "wss://api.kiwoom.com:10000/api/dostk/websocket"
MAX_JSON_BYTES = 1024 * 1024
FALSE_VALUES = frozenset({"0", "false", "off", "no"})
TYPE00_ALLOWED_FIELDS = frozenset({
    "9201","9203","9205","9001","912","913","302","900","901","902","903",
    "904","905","906","907","908","909","910","911","10","27","28","914",
    "915","938","939","919","920","921","922","923","10010","2134","2135","2136",
})


class ReadOnlySmokeError(RuntimeError):
    def __init__(self, stage: str, return_code: int = -1, detail_code: int | None = None,
                 error_class: str | None = None):
        super().__init__(stage)
        self.stage = stage
        self.return_code = return_code
        self.detail_code = detail_code
        self.error_class = error_class


@dataclass
class SmokeState:
    STAGE: str = "INIT"
    RETURN_CODE: int = -1
    DETAIL_CODE: int | None = None
    ERROR_CLASS: str | None = None
    TOKEN_CANONICAL_NO_EDGE_WHITESPACE: bool = False
    TOKEN_EXPIRY_FIELD_PRESENT: bool = False
    TOKEN_TYPE_FIELD_PRESENT: bool = False
    REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN: bool = False
    WS_LOGIN_USED_ISSUED_TOKEN: bool = False
    TOKEN_AGE_SECONDS_AT_WS_LOGIN: int | None = None
    TOKEN_OK: bool = False
    ACCOUNT_ENDPOINT_OK: bool = False
    WS_CONNECTED: bool = False
    WS_LOGIN_OK: bool = False
    TYPE00_REG_SENT: bool = False
    TYPE00_REG_ACK_OK: bool = False
    TYPE00_EVENT_COUNT: int = 0
    ACCOUNT_MATCHED_TYPE00_EVENT_COUNT: int = 0
    BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED: bool = False
    GENUINE_LIVE_PROVENANCE_VERIFIED: bool = False
    ORDERING: str = "DISABLED"
    REAL_ORDERS_AUTHORIZED: bool = False
    FUNDS_MOVEMENT_AUTHORIZED: bool = False
    PERMISSION_CHANGE_AUTHORIZED: bool = False


def _pairs_no_duplicates(pairs):
    out = {}
    seen = set()
    for key, value in pairs:
        if not isinstance(key, str):
            raise ValueError("invalid JSON key")
        folded = key.casefold()
        if folded in seen:
            raise ValueError("duplicate JSON key")
        seen.add(folded)
        out[key] = value
    return out


def strict_json(raw: bytes | str) -> Mapping[str, Any]:
    if isinstance(raw, str):
        payload = raw.encode("utf-8", "strict")
    elif isinstance(raw, (bytes, bytearray)):
        payload = bytes(raw)
    else:
        raise ValueError("JSON payload type")
    if not payload or len(payload) > MAX_JSON_BYTES:
        raise ValueError("JSON payload size")
    text = payload.decode("utf-8", "strict")
    value = json.loads(
        text,
        object_pairs_hook=_pairs_no_duplicates,
        parse_constant=lambda _x: (_ for _ in ()).throw(ValueError("nonstandard JSON constant")),
    )
    if not isinstance(value, Mapping):
        raise ValueError("top-level object required")
    return value


def return_code(obj: Mapping[str, Any]) -> int:
    if "return_code" not in obj:
        raise ValueError("missing return_code")
    code = obj["return_code"]
    if type(code) is not int or code < 0 or code > 2_147_483_647:
        raise ValueError("invalid return_code")
    return code


def classify_detail(message: Any) -> tuple[int | None, str | None]:
    text = "" if message is None else str(message)
    match = re.search(r"(?:\[|CODE=)(\d{3,5})(?::|\b)", text)
    if not match:
        return None, None
    code = int(match.group(1))
    if code in {8001,8002,8011,8012}:
        kind = "INVALID_CREDENTIALS"
    elif code in {8003,8005,8006,8009,8015,8016}:
        kind = "INVALID_TOKEN"
    elif code in {8030,8031}:
        kind = "MODE_MISMATCH"
    elif code == 8050:
        kind = "TOKEN_OR_LOGIN_AUTH"
    elif code in {8010,8040,8103}:
        kind = "DEVICE_AUTH"
    else:
        kind = "UNCLASSIFIED"
    return code, kind


def _name(obj: Mapping[str, Any]) -> str:
    name = obj.get("trnm")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("invalid message name")
    return name.upper()


def _config() -> tuple[str, str]:
    if os.getenv("KIWOOM_ENV") != "REAL":
        raise ReadOnlySmokeError("CONFIG")
    if os.getenv("KIWOOM_BASE_URL") != REAL_BASE_URL:
        raise ReadOnlySmokeError("CONFIG")
    if str(os.getenv("KIWOOM_ORDERING_ENABLED") or "").strip().lower() not in FALSE_VALUES:
        raise ReadOnlySmokeError("CONFIG")
    app_key = str(os.getenv("KIWOOM_APP_KEY") or "")
    app_secret = str(os.getenv("KIWOOM_APP_SECRET") or "")
    if not app_key.strip() or not app_secret.strip():
        raise ReadOnlySmokeError("CONFIG")
    return app_key, app_secret


def _token_and_account(state: SmokeState) -> tuple[str, str, float]:
    app_key, app_secret = _config()
    try:
        token_response = requests.post(
            TOKEN_URL,
            headers={"Content-Type": "application/json;charset=UTF-8"},
            json={
                "grant_type": "client_credentials",
                "appkey": app_key,
                "secretkey": app_secret,
            },
            timeout=15,
        )
        token_obj = strict_json(token_response.content)
        token_code = return_code(token_obj)
    except ReadOnlySmokeError:
        raise
    except Exception:
        raise ReadOnlySmokeError("TOKEN_PROTOCOL") from None

    token = token_obj.get("token")
    if token_code != 0 or not isinstance(token, str) or not token.strip():
        detail, kind = classify_detail(token_obj.get("return_msg"))
        raise ReadOnlySmokeError("TOKEN", token_code, detail, kind)
    if token != token.strip():
        raise ReadOnlySmokeError("TOKEN_CANONICALITY", token_code)
    issued_monotonic = time.monotonic()
    state.TOKEN_CANONICAL_NO_EDGE_WHITESPACE = True
    state.TOKEN_EXPIRY_FIELD_PRESENT = isinstance(token_obj.get("expires_dt"), str) and bool(token_obj["expires_dt"].strip())
    state.TOKEN_TYPE_FIELD_PRESENT = isinstance(token_obj.get("token_type"), str) and bool(token_obj["token_type"].strip())
    state.TOKEN_OK = True

    try:
        account_response = requests.post(
            ACCOUNT_URL,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "authorization": "Bearer " + token,
                "api-id": "ka00001",
                "cont-yn": "N",
                "next-key": "",
            },
            data=b"{}",
            timeout=15,
        )
        account_obj = strict_json(account_response.content)
        account_code = return_code(account_obj)
    except Exception:
        raise ReadOnlySmokeError("ACCOUNT_PROTOCOL") from None
    account = account_obj.get("acctNo")
    if account_code != 0 or not isinstance(account, str) or not account.strip():
        detail, kind = classify_detail(account_obj.get("return_msg"))
        raise ReadOnlySmokeError("ACCOUNT", account_code, detail, kind)
    state.ACCOUNT_ENDPOINT_OK = True
    state.REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN = True
    return token, account, issued_monotonic


def _type00_observation(obj: Mapping[str, Any], account: str) -> tuple[int, int, bool]:
    if _name(obj) != "REAL":
        raise ValueError("not REAL")
    data = obj.get("data")
    if not isinstance(data, list):
        raise ValueError("REAL data invalid")
    events = matched = 0
    execution = False
    for entry in data:
        if not isinstance(entry, Mapping) or not isinstance(entry.get("type"), str):
            raise ValueError("REAL entry invalid")
        if entry["type"] != "00":
            continue
        values = entry.get("values")
        if not isinstance(values, Mapping):
            raise ValueError("type00 values invalid")
        for key, value in values.items():
            if key not in TYPE00_ALLOWED_FIELDS or not isinstance(value, str) or len(value) > 4096:
                raise ValueError("type00 field invalid")
        events += 1
        if values.get("9201") == account:
            matched += 1
            if (
                values.get("913") == "체결"
                and bool(values.get("909"))
                and bool(values.get("908"))
                and bool(values.get("914"))
                and bool(values.get("915"))
            ):
                execution = True
    return events, matched, execution


async def _recv_text(ws, timeout: float) -> str:
    raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
    if not isinstance(raw, str):
        raise ReadOnlySmokeError("NON_TEXT_WEBSOCKET_FRAME", 0)
    if len(raw.encode("utf-8", "strict")) > MAX_JSON_BYTES:
        raise ReadOnlySmokeError("WEBSOCKET_FRAME_TOO_LARGE", 0)
    return raw


async def _run_ws(token: str, account: str, issued_monotonic: float, state: SmokeState) -> None:
    try:
        async with websockets.connect(
            WS_URL,
            open_timeout=10,
            close_timeout=3,
            max_size=MAX_JSON_BYTES,
            ping_interval=None,
        ) as ws:
            state.WS_CONNECTED = True
            state.TOKEN_AGE_SECONDS_AT_WS_LOGIN = max(0, int(time.monotonic() - issued_monotonic))
            state.WS_LOGIN_USED_ISSUED_TOKEN = True
            await ws.send(json.dumps({"trnm": "LOGIN", "token": token}, separators=(",", ":")))

            login_ok = False
            for _ in range(10):
                raw = await _recv_text(ws, 5)
                if raw.strip().upper() == "PING":
                    await ws.send(raw)
                    continue
                try:
                    obj = strict_json(raw)
                except Exception:
                    raise ReadOnlySmokeError("WS_LOGIN_PROTOCOL", 0) from None
                if _name(obj) == "PING":
                    await ws.send(raw)
                    continue
                if _name(obj) != "LOGIN":
                    raise ReadOnlySmokeError("WS_LOGIN_PROTOCOL", 0)
                try:
                    code = return_code(obj)
                except Exception:
                    raise ReadOnlySmokeError("WS_LOGIN_PROTOCOL", 0) from None
                if code != 0:
                    detail, kind = classify_detail(obj.get("return_msg"))
                    raise ReadOnlySmokeError("WS_LOGIN", code, detail, kind)
                login_ok = True
                break
            if not login_ok:
                raise ReadOnlySmokeError("WS_LOGIN_TIMEOUT", 0)
            state.WS_LOGIN_OK = True

            reg = {
                "trnm": "REG",
                "grp_no": "1",
                "refresh": "1",
                "data": [{"item": [], "type": ["00"]}],
            }
            await ws.send(json.dumps(reg, separators=(",", ":")))
            state.TYPE00_REG_SENT = True

            deadline = time.monotonic() + 8.0
            execution = False
            while time.monotonic() < deadline:
                try:
                    raw = await _recv_text(ws, min(2.0, max(0.25, deadline - time.monotonic())))
                except asyncio.TimeoutError:
                    continue
                if raw.strip().upper() == "PING":
                    await ws.send(raw)
                    continue
                try:
                    obj = strict_json(raw)
                    name = _name(obj)
                except Exception:
                    raise ReadOnlySmokeError("TYPE00_JSON_PROTOCOL", 0) from None
                if name == "PING":
                    await ws.send(raw)
                    continue
                if name == "REG":
                    try:
                        code = return_code(obj)
                    except Exception:
                        raise ReadOnlySmokeError("TYPE00_REG_PROTOCOL", 0) from None
                    if code != 0:
                        detail, kind = classify_detail(obj.get("return_msg"))
                        raise ReadOnlySmokeError("TYPE00_REG", code, detail, kind)
                    state.TYPE00_REG_ACK_OK = True
                    continue
                if name != "REAL":
                    continue
                try:
                    events, matched, seen_execution = _type00_observation(obj, account)
                except Exception:
                    raise ReadOnlySmokeError("TYPE00_FRAME_PROTOCOL", 0) from None
                state.TYPE00_EVENT_COUNT += events
                state.ACCOUNT_MATCHED_TYPE00_EVENT_COUNT += matched
                execution = execution or seen_execution
            state.BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED = execution
            if not state.TYPE00_REG_ACK_OK:
                raise ReadOnlySmokeError("TYPE00_SUBSCRIPTION_UNOBSERVED", 0)
    except ReadOnlySmokeError:
        raise
    except asyncio.TimeoutError:
        raise ReadOnlySmokeError("WS_TIMEOUT", 0) from None
    except Exception:
        raise ReadOnlySmokeError("LOCAL_COMPATIBILITY_OR_NETWORK", -1) from None


def _emit(state: SmokeState, *, exit_code: int) -> None:
    # Never add provider response bodies, credentials, account IDs, tokens,
    # order IDs, symbols, prices, quantities or IP addresses to this object.
    print(json.dumps(asdict(state), sort_keys=True, separators=(",", ":")), flush=True)
    raise SystemExit(exit_code)


def main() -> None:
    state = SmokeState()
    try:
        token, account, issued = _token_and_account(state)
        asyncio.run(_run_ws(token, account, issued, state))
        state.STAGE = "REAL_TYPE00_READ_ONLY_SMOKE"
        state.RETURN_CODE = 0
        _emit(state, exit_code=0)
    except ReadOnlySmokeError as exc:
        state.STAGE = exc.stage
        state.RETURN_CODE = exc.return_code
        state.DETAIL_CODE = exc.detail_code
        state.ERROR_CLASS = exc.error_class
        _emit(state, exit_code=2)


if __name__ == "__main__":
    main()
