"""Offline Kiwoom REAL ka10001 quote contract; never opens broker connections.

Official example: Kiwoom-Securities/Kiwoom-REST-API
examples/국내주식/종목정보/get_domestic_stock_info.py
This is only source/response-shape preflight for future owner-authorized read-only
broker verification; it cannot prove a live quote, PIT suitability or order safety.
"""
from __future__ import annotations

import json
import re
from typing import Any, Mapping

QUOTE_API_ID = "ka10001"
QUOTE_PATH = "/api/dostk/stkinfo"
QUOTE_METHOD = "POST"
_MAX_BYTES = 65_536


class QuoteContractError(ValueError):
    """Fixed non-sensitive quote contract failure."""


def _stock_code(value: Any) -> str:
    # Conservative KRX numeric-only subset: no suffix, wildcard, query string,
    # relative path, market expansion or implied symbol universe.
    if type(value) is not str or re.fullmatch(r"[0-9]{6}", value) is None:
        raise QuoteContractError("INVALID_KRX_STOCK_CODE")
    return value


def offline_quote_envelope(stk_cd: str) -> dict[str, Any]:
    """Exact offline request shape; excludes credentials and HTTP clients.

    Never interpret this serialized shape as authority to open a connection.
    """
    symbol = _stock_code(stk_cd)
    return {
        "method": QUOTE_METHOD,
        "path": QUOTE_PATH,
        "api_id": QUOTE_API_ID,
        "body": {"stk_cd": symbol},
        "network_request_sent": False,
        "real_quote_verified": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
    }


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in pairs:
        if key.casefold() in folded:
            raise QuoteContractError("DUPLICATE_PROVIDER_FIELD")
        result[key] = value
        folded.add(key.casefold())
    return result


def offline_quote_structure(*, stock_code: str, http_status: int,
                            response_body: bytes | str) -> dict[str, Any]:
    """Validate a synthetic or externally supplied read-only response shape.

    Does NOT fetch a quote, authorize or report that genuine broker evidence
    exists. Never returns price, account, token or original broker content.
    """
    symbol = _stock_code(stock_code)
    if type(http_status) is not int or http_status != 200:
        raise QuoteContractError("HTTP_NOT_SUCCESSFUL")
    if isinstance(response_body, str):
        try:
            raw = response_body.encode("utf-8", "strict")
        except UnicodeError:
            raise QuoteContractError("INVALID_QUOTE_PAYLOAD") from None
    elif isinstance(response_body, bytes):
        raw = response_body
    else:
        raise QuoteContractError("INVALID_QUOTE_PAYLOAD")
    if not raw or len(raw) > _MAX_BYTES:
        raise QuoteContractError("INVALID_QUOTE_PAYLOAD")
    try:
        obj = json.loads(
            raw.decode("utf-8", "strict"),
            object_pairs_hook=_no_duplicate_keys,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonstandard")),
        )
    except Exception:
        raise QuoteContractError("INVALID_QUOTE_PAYLOAD") from None
    if not isinstance(obj, Mapping):
        raise QuoteContractError("INVALID_QUOTE_PAYLOAD")
    code = obj.get("return_code")
    if type(code) is not int or code != 0:
        raise QuoteContractError("BROKER_QUOTE_NOT_ACCEPTED")
    if obj.get("stk_cd") != symbol:
        raise QuoteContractError("STOCK_IDENTITY_MISMATCH")
    price = obj.get("cur_prc")
    if type(price) is not str or not price.strip() or len(price) > 64:
        raise QuoteContractError("QUOTE_FIELD_UNVERIFIED")
    if re.fullmatch(r"[+-]?[0-9]+", price.strip()) is None:
        raise QuoteContractError("QUOTE_FIELD_UNVERIFIED")
    return {
        "structural_contract_passed": True,
        "requested_symbol_matched": True,
        "synthetic_quote_field_shape_passed": True,
        "live_broker_connection_verified": False,
        "real_quote_verified": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
    }
