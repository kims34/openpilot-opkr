"""Offline Kiwoom broker-native execution-event normalization.

This module intentionally contains no network, authentication, account-query or order
submission code. It transforms a caller-supplied copy of an official Kiwoom domestic
real-time order/fill (type ``00``) event into a broker-neutral evidence row while
preserving stable broker order/execution identifiers.

Important: normalization and hashing do NOT authenticate genuine real-account origin.
Independent admission under INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md remains
required before any row can become project LIVE evidence.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping


SOURCE_CONTRACT = "kiwoom-rest-realtime-00-offline-normalizer-v1"
_ACCOUNT_FINGERPRINT = re.compile(r"^sha256:[0-9a-f]{64}$")


class KiwoomNativeExecutionError(ValueError):
    """Raised when a broker-native event cannot be safely normalized."""


def _text(event: Mapping[str, Any], key: str) -> str:
    value = event.get(key, "")
    if value is None:
        return ""
    return str(value).strip()


def _required_text(event: Mapping[str, Any], key: str, label: str) -> str:
    value = _text(event, key)
    if not value:
        raise KiwoomNativeExecutionError(f"missing broker-native {label} ({key})")
    return value


def _decimalish(value: str, *, field: str) -> str:
    """Validate a numeric-looking broker field without changing broker semantics."""
    if value == "":
        return ""
    candidate = value.replace(",", "")
    if candidate[:1] in {"+", "-"}:
        candidate = candidate[1:]
    if not candidate:
        raise KiwoomNativeExecutionError(f"invalid numeric field {field}")
    parts = candidate.split(".")
    if len(parts) > 2 or any(part and not part.isdigit() for part in parts):
        raise KiwoomNativeExecutionError(f"invalid numeric field {field}")
    if all(part == "" for part in parts):
        raise KiwoomNativeExecutionError(f"invalid numeric field {field}")
    return value


def _positive_numeric(value: str) -> bool:
    if not value:
        return False
    try:
        return float(value.replace(",", "")) > 0.0
    except ValueError:
        return False


def canonical_event_sha256(event: Mapping[str, Any]) -> str:
    """Hash canonicalized event bytes; this proves byte identity, not provenance."""
    encoded = json.dumps(
        dict(event),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_realtime_order_fill_event(
    event: Mapping[str, Any],
    *,
    account_fingerprint: str,
) -> dict[str, Any]:
    """Normalize one official Kiwoom domestic order/fill realtime type-00 event.

    The raw account number (field 9201) is required for local binding checks but is
    deliberately omitted from the returned row. ``account_fingerprint`` must be
    produced outside this module in a protected context.

    A positive fill quantity requires the broker-native execution/fill number (909).
    Non-fill order lifecycle messages may legitimately have no execution number.
    """

    if not isinstance(event, Mapping):
        raise KiwoomNativeExecutionError("event must be a mapping")
    if not _ACCOUNT_FINGERPRINT.fullmatch(account_fingerprint):
        raise KiwoomNativeExecutionError(
            "account_fingerprint must be sha256:<64 lowercase hex>"
        )

    # Require a raw account binding locally, but never return or hash it separately.
    _required_text(event, "9201", "account number")
    broker_order_id = _required_text(event, "9203", "order number")
    symbol = _required_text(event, "9001", "symbol")
    lifecycle_time = _required_text(event, "908", "order/fill time")

    broker_execution_id = _text(event, "909")
    fill_qty = _decimalish(_text(event, "911"), field="fill_qty")
    if _positive_numeric(fill_qty) and not broker_execution_id:
        raise KiwoomNativeExecutionError(
            "positive fill quantity requires broker-native execution number (909)"
        )

    numeric_fields = {
        "order_qty": _decimalish(_text(event, "900"), field="order_qty"),
        "order_price": _decimalish(_text(event, "901"), field="order_price"),
        "remaining_qty": _decimalish(_text(event, "902"), field="remaining_qty"),
        "cumulative_fill_amount": _decimalish(
            _text(event, "903"), field="cumulative_fill_amount"
        ),
        "fill_price": _decimalish(_text(event, "910"), field="fill_price"),
        "fill_qty": fill_qty,
        "unit_fill_price": _decimalish(_text(event, "914"), field="unit_fill_price"),
        "unit_fill_qty": _decimalish(_text(event, "915"), field="unit_fill_qty"),
        "fee": _decimalish(_text(event, "938"), field="fee"),
        "tax": _decimalish(_text(event, "939"), field="tax"),
    }

    return {
        "source_contract": SOURCE_CONTRACT,
        "broker": "KIWOOM",
        "source_api": "domestic_realtime_order_fill_00",
        "raw_event_sha256": canonical_event_sha256(event),
        "account_fingerprint": account_fingerprint,
        "broker_order_id": broker_order_id,
        "broker_execution_id": broker_execution_id,
        "original_order_id": _text(event, "904"),
        "symbol": symbol,
        "order_status": _text(event, "913"),
        "order_business_type": _text(event, "912"),
        "order_type": _text(event, "905"),
        "trade_type": _text(event, "906"),
        "side": _text(event, "907"),
        "broker_lifecycle_time": lifecycle_time,
        **numeric_fields,
        "rejection_reason": _text(event, "919"),
        "exchange_code": _text(event, "2134"),
        "exchange_name": _text(event, "2135"),
        "sor_flag": _text(event, "2136"),
        # These fields are deliberately immutable false at this layer. Only an
        # independent provenance admission process may establish genuine LIVE origin.
        "broker_native_structure_normalized": True,
        "genuine_live_provenance_verified": False,
        "project_live_evidence_admitted": False,
    }
