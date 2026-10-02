"""Raw-preserving KRX historical network adapters.

These adapters are deliberately low-level. They preserve the exact HTTP response
bytes needed by the historical execution contract and return the common
FetchResult used by research_v1_krx_historical_worker_core.

They do not decide whether a bulk job is authorized. A caller must first pass the
frozen historical acquisition preflight, and the worker core re-checks that
preflight before invoking an injected fetcher.
"""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import json
from typing import Any, Mapping

import pandas as pd

from research_v1_krx_historical_worker_core import FetchResult


PINNED_KRX_DATA_API = "e6ebac9b71482db127348d8a08ebc6743aa3b50e"
DM_BASE = "https://data.krx.co.kr"
OTP_URL = f"{DM_BASE}/comm/fileDn/GenerateOTP/generate.cmd"
CSV_URL = f"{DM_BASE}/comm/fileDn/download_csv/download.cmd"
JSON_URL = f"{DM_BASE}/comm/bldAttendant/getJsonData.cmd"
LOGIN_PAGE = (
    "https://data.krx.co.kr/contents/MDC/COMS/client/view/login.jsp?site=mdc"
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)


class KRXHistoricalFetchError(RuntimeError):
    pass


def _require_network_authorized(value: bool) -> None:
    if value is not True:
        raise KRXHistoricalFetchError(
            "network adapter blocked: historical acquisition preflight authorization required"
        )


def _headers(menu_id: str) -> dict[str, str]:
    return {
        "Referer": f"{DM_BASE}/contents/MDC/MDI/mdiLoader/index.cmd?menuId={menu_id}",
        "User-Agent": USER_AGENT,
    }


def _retrieved_at(value: str | None = None) -> str:
    if value is not None:
        parsed = datetime.fromisoformat(str(value))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise KRXHistoricalFetchError("retrieved_at_override must be timezone-aware")
        return parsed.isoformat()
    return datetime.now(timezone.utc).isoformat()


def _json_frame(raw: bytes) -> pd.DataFrame:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise KRXHistoricalFetchError("KRX JSON response could not be parsed") from exc
    if not isinstance(payload, Mapping):
        raise KRXHistoricalFetchError("KRX JSON response must be an object")
    rows = payload.get("output") or payload.get("OutBlock_1") or []
    if not isinstance(rows, list):
        raise KRXHistoricalFetchError("KRX JSON row block must be a list")
    frame = pd.DataFrame(rows)
    frame.attrs["current_datetime"] = payload.get("CURRENT_DATETIME")
    return frame


def _csv_frame(raw: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(BytesIO(raw), encoding="EUC-KR")
    except Exception as exc:
        raise KRXHistoricalFetchError("KRX CSV response could not be parsed") from exc


def _response_ok(resp: Any) -> bool:
    ok = getattr(resp, "ok", None)
    if ok is not None:
        return bool(ok)
    status = int(getattr(resp, "status_code", 0) or 0)
    return 200 <= status < 300


def _status_code(resp: Any) -> int:
    return int(getattr(resp, "status_code", 0) or 0)


def _content(resp: Any) -> bytes:
    raw = getattr(resp, "content", b"")
    if isinstance(raw, bytearray):
        raw = bytes(raw)
    if not isinstance(raw, bytes):
        raise KRXHistoricalFetchError("HTTP response content must be bytes")
    return raw


def _text(resp: Any) -> str:
    value = getattr(resp, "text", None)
    if isinstance(value, str):
        return value
    raw = _content(resp)
    try:
        return raw.decode("utf-8")
    except Exception:
        return raw.decode("utf-8", errors="replace")


def fetch_data_marketplace_raw(
    *,
    method: str,
    bld: str,
    params: Mapping[str, Any],
    menu_id: str,
    network_authorized: bool,
    session: Any | None = None,
    retrieved_at_override: str | None = None,
) -> FetchResult:
    """Fetch one authenticated Data Marketplace object while preserving raw bytes.

    When session is omitted, the pinned krx-data-api authentication singleton is
    used. A premature LOGOUT invalidates that singleton and is retried exactly
    once. When a session is injected (tests/custom caller), no hidden relogin is
    attempted.
    """
    _require_network_authorized(network_authorized)
    method = str(method).lower().strip()
    if method not in {"csv", "json"}:
        raise KRXHistoricalFetchError("method must be csv or json")
    if not str(bld).strip():
        raise KRXHistoricalFetchError("bld is required")
    if not str(menu_id).strip():
        raise KRXHistoricalFetchError("menu_id is required")

    auth = None
    if session is None:
        try:
            from krx_data_api import get_krx_auth
        except Exception as exc:
            raise KRXHistoricalFetchError(
                "pinned krx-data-api client is unavailable"
            ) from exc
        auth = get_krx_auth()
        session = auth.session

    def _csv_once(active_session: Any) -> tuple[bytes, int]:
        otp_payload = {
            "locale": "ko_KR",
            "share": "1",
            "csvxls_isNo": "false",
            "name": "fileDown",
            **dict(params),
            "url": bld,
        }
        otp_resp = active_session.post(
            OTP_URL,
            data=otp_payload,
            headers=_headers(menu_id),
        )
        otp_text = _text(otp_resp).strip()
        if otp_text == "LOGOUT":
            raise KRXHistoricalFetchError("KRX_AUTH_SESSION_LOGOUT")
        if not _response_ok(otp_resp) or not otp_text:
            raise KRXHistoricalFetchError(
                f"KRX OTP request failed: status={_status_code(otp_resp)}"
            )
        resp = active_session.post(
            CSV_URL,
            data={"code": otp_text},
            headers=_headers(menu_id),
        )
        raw = _content(resp)
        if not _response_ok(resp) or not raw:
            raise KRXHistoricalFetchError(
                f"KRX CSV download failed: status={_status_code(resp)} bytes={len(raw)}"
            )
        return raw, _status_code(resp)

    def _json_once(active_session: Any) -> tuple[bytes, int]:
        payload = {"bld": bld, "locale": "ko_KR", **dict(params)}
        resp = active_session.post(
            JSON_URL,
            data=payload,
            headers=_headers(menu_id),
        )
        if _text(resp).strip() == "LOGOUT":
            raise KRXHistoricalFetchError("KRX_AUTH_SESSION_LOGOUT")
        raw = _content(resp)
        if not _response_ok(resp):
            raise KRXHistoricalFetchError(
                f"KRX JSON request failed: status={_status_code(resp)}"
            )
        if not raw:
            raise KRXHistoricalFetchError("KRX JSON response was empty")
        return raw, _status_code(resp)

    call = _csv_once if method == "csv" else _json_once
    try:
        raw, status = call(session)
    except KRXHistoricalFetchError as exc:
        if str(exc) != "KRX_AUTH_SESSION_LOGOUT" or auth is None:
            raise
        auth.invalidate()
        session = auth.session
        raw, status = call(session)

    frame = _csv_frame(raw) if method == "csv" else _json_frame(raw)
    return FetchResult(
        raw_bytes=raw,
        response_frame=frame,
        retrieved_at=_retrieved_at(retrieved_at_override),
        transport_status=f"HTTP_{status}_{method.upper()}",
        network_request_attempted=True,
    )


def fetch_openapi_raw(
    *,
    endpoint: str,
    params: Mapping[str, Any],
    auth_key: str,
    network_authorized: bool,
    session: Any | None = None,
    retrieved_at_override: str | None = None,
) -> FetchResult:
    """Fetch one approved KRX OpenAPI object while preserving exact response bytes."""
    _require_network_authorized(network_authorized)
    key = str(auth_key or "").strip()
    if not key:
        raise KRXHistoricalFetchError("KRX OpenAPI auth key is required")
    if not str(endpoint).startswith("https://data-dbg.krx.co.kr/svc/apis/"):
        raise KRXHistoricalFetchError("unexpected KRX OpenAPI endpoint")

    if session is None:
        try:
            import requests
        except Exception as exc:
            raise KRXHistoricalFetchError("requests is unavailable") from exc
        session = requests.Session()

    resp = session.get(
        endpoint,
        params=dict(params),
        headers={"AUTH_KEY": key},
        timeout=30,
    )
    raw = _content(resp)
    if not _response_ok(resp):
        raise KRXHistoricalFetchError(
            f"KRX OpenAPI request failed: status={_status_code(resp)}"
        )
    if not raw:
        raise KRXHistoricalFetchError("KRX OpenAPI response was empty")
    frame = _json_frame(raw)
    return FetchResult(
        raw_bytes=raw,
        response_frame=frame,
        retrieved_at=_retrieved_at(retrieved_at_override),
        transport_status=f"HTTP_{_status_code(resp)}_OPENAPI",
        network_request_attempted=True,
    )
