"""Offline Kiwoom domestic-stock order request-envelope contract.

This module mirrors the reviewed official Kiwoom request schema only. It has no
HTTP client, token handling, credentials, broker connection, or send method.
Constructing an envelope is not order authority and never submits anything.
"""
import re

OFFICIAL_SCHEMA_COMMIT = "953e5dbff123f437ab4d11a78a95191a685eb51f"
ORDER_PATH = "/api/dostk/ordr"
EXCHANGES = frozenset(("KRX", "NXT", "SOR"))
TRADE_TYPES = frozenset(("0","3","5","81","61","62","6","7","10","13","16","20","23","26","28","29","30","31"))
API = {
    "BUY": "kt10000",
    "SELL": "kt10001",
    "MODIFY": "kt10002",
    "CANCEL": "kt10003",
}


class KiwoomOrderEnvelopeError(ValueError):
    pass


def _text(value, name):
    if type(value) is not str or not value or value != value.strip() or len(value) > 128:
        raise KiwoomOrderEnvelopeError(f"{name} invalid")
    if any(ord(ch) < 32 for ch in value):
        raise KiwoomOrderEnvelopeError(f"{name} invalid")
    return value


def _digits(value, name, *, zero_allowed):
    _text(value, name)
    if not re.fullmatch(r"[0-9]+", value):
        raise KiwoomOrderEnvelopeError(f"{name} invalid")
    number = int(value)
    if number < 0 or (number == 0 and not zero_allowed):
        raise KiwoomOrderEnvelopeError(f"{name} invalid")
    return value


def _optional_price(value, name):
    if value is None:
        return None
    if value == "":
        return ""
    return _digits(value, name, zero_allowed=True)


def _base(kind, body):
    return {
        "mode": "OFFLINE_KIWOOM_ORDER_REQUEST_ENVELOPE",
        "kind": kind,
        "api_id": API[kind],
        "path": ORDER_PATH,
        "body": body,
        "official_schema_commit": OFFICIAL_SCHEMA_COMMIT,
        "network_request_attempted": False,
        "broker_request_sent": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "broker_permission_change_authorized": False,
        "requires_separate_activation_authorization": True,
    }


def _common(exchange, symbol):
    if exchange not in EXCHANGES:
        raise KiwoomOrderEnvelopeError("dmst_stex_tp invalid")
    return exchange, _text(symbol, "stk_cd")


def build_new_order(*, side, dmst_stex_tp, stk_cd, ord_qty, trde_tp, ord_uv="", cond_uv=""):
    if side not in ("BUY", "SELL"):
        raise KiwoomOrderEnvelopeError("side invalid")
    exchange, symbol = _common(dmst_stex_tp, stk_cd)
    qty = _digits(ord_qty, "ord_qty", zero_allowed=False)
    if trde_tp not in TRADE_TYPES:
        raise KiwoomOrderEnvelopeError("trde_tp invalid")
    body = {
        "dmst_stex_tp": exchange,
        "stk_cd": symbol,
        "ord_qty": qty,
        "trde_tp": trde_tp,
    }
    price = _optional_price(ord_uv, "ord_uv")
    condition = _optional_price(cond_uv, "cond_uv")
    if price is not None:
        body["ord_uv"] = price
    if condition is not None:
        body["cond_uv"] = condition
    return _base(side, body)


def build_cancel_order(*, dmst_stex_tp, orig_ord_no, stk_cd, cncl_qty):
    exchange, symbol = _common(dmst_stex_tp, stk_cd)
    body = {
        "dmst_stex_tp": exchange,
        "orig_ord_no": _text(orig_ord_no, "orig_ord_no"),
        "stk_cd": symbol,
        "cncl_qty": _digits(cncl_qty, "cncl_qty", zero_allowed=True),
    }
    return _base("CANCEL", body)


def build_modify_order(*, dmst_stex_tp, orig_ord_no, stk_cd, mdfy_qty, mdfy_uv, mdfy_cond_uv=""):
    exchange, symbol = _common(dmst_stex_tp, stk_cd)
    price = _digits(mdfy_uv, "mdfy_uv", zero_allowed=True)
    body = {
        "dmst_stex_tp": exchange,
        "orig_ord_no": _text(orig_ord_no, "orig_ord_no"),
        "stk_cd": symbol,
        "mdfy_qty": _digits(mdfy_qty, "mdfy_qty", zero_allowed=True),
        "mdfy_uv": price,
    }
    condition = _optional_price(mdfy_cond_uv, "mdfy_cond_uv")
    if condition is not None:
        body["mdfy_cond_uv"] = condition
    return _base("MODIFY", body)
