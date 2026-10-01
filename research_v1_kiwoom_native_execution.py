"""Offline Kiwoom broker-native execution normalization and REST snapshot reconciliation.

This module intentionally contains no network, authentication, account-query or order
submission code. It transforms caller-supplied copies of official Kiwoom domestic
order/fill responses into broker-neutral evidence rows while preserving broker-native
identifiers.

Important: normalization, hashing and reconciliation do NOT authenticate genuine
real-account origin. Independent admission under
INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md remains required before any row can
become project LIVE evidence.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from typing import Any, Mapping, Sequence


OFFICIAL_SCHEMA_COMMIT = "953e5dbff123f437ab4d11a78a95191a685eb51f"
SOURCE_CONTRACT = "kiwoom-rest-realtime-00-offline-normalizer-v1"
KT00007_SOURCE_CONTRACT = "kiwoom-rest-kt00007-offline-normalizer-v1"
KA10076_SOURCE_CONTRACT = "kiwoom-rest-ka10076-offline-normalizer-v1"
REST_RECONCILIATION_CONTRACT = "kiwoom-rest-order-snapshot-reconciliation-v1"

_ACCOUNT_FINGERPRINT = re.compile(r"^sha256:[0-9a-f]{64}$")
_RAW_ACCOUNT_FIELD = "9201"
_SENSITIVE_RECORD_KEYS = frozenset(
    {
        _RAW_ACCOUNT_FIELD,
        "account_no",
        "account_number",
        "acct_no",
        "acctNo",
        "acnt_no",
    }
)


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


def _validate_account_fingerprint(account_fingerprint: str) -> None:
    if not _ACCOUNT_FINGERPRINT.fullmatch(account_fingerprint):
        raise KiwoomNativeExecutionError(
            "account_fingerprint must be sha256:<64 lowercase hex>"
        )


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
        return Decimal(value.replace(",", "")) > 0
    except InvalidOperation:
        return False


def _as_decimal(value: str, *, field: str) -> Decimal:
    try:
        return Decimal(value.replace(",", ""))
    except InvalidOperation as exc:
        raise KiwoomNativeExecutionError(f"invalid numeric field {field}") from exc


def _privacy_safe_mapping_sha256(record: Mapping[str, Any]) -> str:
    """Hash a canonical mapping after removing known account-number fields.

    This is a privacy-safe local identity aid, not a raw broker-artifact hash and not
    broker provenance.
    """
    safe_record = {
        key: value
        for key, value in dict(record).items()
        if key not in _SENSITIVE_RECORD_KEYS
    }
    encoded = json.dumps(
        safe_record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def privacy_safe_event_sha256(event: Mapping[str, Any]) -> str:
    """Hash a canonical event view after removing the raw account number.

    This value is only a privacy-safe local identity aid. It is deliberately *not* a
    hash of the immutable raw broker artifact and proves neither raw-artifact identity
    nor genuine broker provenance. A protected provenance bundle must retain/hash the
    raw source separately when later allowed by the provenance contract.
    """

    return _privacy_safe_mapping_sha256(event)


def _project_fail_closed_markers() -> dict[str, bool]:
    return {
        "broker_native_structure_normalized": True,
        "genuine_live_provenance_verified": False,
        "project_live_evidence_admitted": False,
    }


def normalize_realtime_order_fill_event(
    event: Mapping[str, Any],
    *,
    account_fingerprint: str,
) -> dict[str, Any]:
    """Normalize one official Kiwoom domestic order/fill realtime type-00 event.

    The raw account number (field 9201) is required for local binding checks but is
    deliberately omitted from the returned row and from the public-safe event hash.
    ``account_fingerprint`` must be produced outside this module in a protected context.

    A positive fill quantity requires the broker-native execution/fill number (909).
    Non-fill order lifecycle messages may legitimately have no execution number.
    """

    if not isinstance(event, Mapping):
        raise KiwoomNativeExecutionError("event must be a mapping")
    _validate_account_fingerprint(account_fingerprint)

    # Require a raw account binding locally, but never return or publicly hash it.
    _required_text(event, _RAW_ACCOUNT_FIELD, "account number")
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
        "official_schema_commit": OFFICIAL_SCHEMA_COMMIT,
        "broker": "KIWOOM",
        "source_api": "domestic_realtime_order_fill_00",
        "record_granularity": "broker_execution_event",
        "privacy_safe_event_sha256": privacy_safe_event_sha256(event),
        "account_fingerprint": account_fingerprint,
        "broker_order_id": broker_order_id,
        "broker_execution_id": broker_execution_id,
        "broker_execution_id_available_in_source": True,
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
        **_project_fail_closed_markers(),
    }


def normalize_kt00007_order_fill_detail(
    record: Mapping[str, Any],
    *,
    account_fingerprint: str,
) -> dict[str, Any]:
    """Normalize one ``kt00007`` order/fill-detail REST record.

    ``kt00007`` is an order-level snapshot and does not expose the realtime execution
    number (909). Therefore a positive aggregate ``cntr_qty`` must *not* be promoted
    into a fabricated broker execution ID.
    """
    if not isinstance(record, Mapping):
        raise KiwoomNativeExecutionError("record must be a mapping")
    _validate_account_fingerprint(account_fingerprint)

    broker_order_id = _required_text(record, "ord_no", "order number")
    symbol = _required_text(record, "stk_cd", "symbol")

    numeric_fields = {
        "order_qty": _decimalish(_text(record, "ord_qty"), field="order_qty"),
        "order_price": _decimalish(_text(record, "ord_uv"), field="order_price"),
        "confirmed_qty": _decimalish(
            _text(record, "cnfm_qty"), field="confirmed_qty"
        ),
        "fill_qty": _decimalish(_text(record, "cntr_qty"), field="fill_qty"),
        "fill_price": _decimalish(_text(record, "cntr_uv"), field="fill_price"),
        "remaining_qty": _decimalish(
            _text(record, "ord_remnq"), field="remaining_qty"
        ),
        "stop_price": _decimalish(_text(record, "cond_uv"), field="stop_price"),
        "fee": "",
        "tax": "",
    }
    order_time = _text(record, "ord_tm")
    confirm_time = _text(record, "cnfm_tm")

    return {
        "source_contract": KT00007_SOURCE_CONTRACT,
        "official_schema_commit": OFFICIAL_SCHEMA_COMMIT,
        "broker": "KIWOOM",
        "source_api": "kt00007",
        "record_granularity": "order_aggregate_snapshot",
        "privacy_safe_record_sha256": _privacy_safe_mapping_sha256(record),
        "account_fingerprint": account_fingerprint,
        "broker_order_id": broker_order_id,
        "broker_execution_id": "",
        "broker_execution_id_available_in_source": False,
        "original_order_id": _text(record, "ori_ord"),
        "symbol": symbol,
        "order_status": "",
        "acceptance_type": _text(record, "acpt_tp"),
        "order_type": _text(record, "io_tp_nm"),
        "trade_type": _text(record, "trde_tp"),
        "amend_cancel_type": _text(record, "mdfy_cncl"),
        "broker_order_time": order_time,
        "broker_confirm_time": confirm_time,
        "broker_lifecycle_time": confirm_time or order_time,
        **numeric_fields,
        "exchange_code": _text(record, "dmst_stex_tp"),
        "exchange_name": "",
        "sor_flag": "",
        **_project_fail_closed_markers(),
    }


def normalize_ka10076_filled_order(
    record: Mapping[str, Any],
    *,
    account_fingerprint: str,
) -> dict[str, Any]:
    """Normalize one ``ka10076`` filled-order REST record.

    This endpoint carries fee/tax/status/SOR fields but still does not expose the
    realtime execution number (909). The row therefore remains an order-aggregate
    snapshot, never an independently identified fill event.
    """
    if not isinstance(record, Mapping):
        raise KiwoomNativeExecutionError("record must be a mapping")
    _validate_account_fingerprint(account_fingerprint)

    broker_order_id = _required_text(record, "ord_no", "order number")
    symbol = _required_text(record, "stk_cd", "symbol")

    numeric_fields = {
        "order_qty": _decimalish(_text(record, "ord_qty"), field="order_qty"),
        "order_price": _decimalish(_text(record, "ord_pric"), field="order_price"),
        "confirmed_qty": "",
        "fill_qty": _decimalish(_text(record, "cntr_qty"), field="fill_qty"),
        "fill_price": _decimalish(_text(record, "cntr_pric"), field="fill_price"),
        "remaining_qty": _decimalish(
            _text(record, "oso_qty"), field="remaining_qty"
        ),
        "stop_price": _decimalish(_text(record, "stop_pric"), field="stop_price"),
        "fee": _decimalish(_text(record, "tdy_trde_cmsn"), field="fee"),
        "tax": _decimalish(_text(record, "tdy_trde_tax"), field="tax"),
    }
    order_time = _text(record, "ord_tm")

    return {
        "source_contract": KA10076_SOURCE_CONTRACT,
        "official_schema_commit": OFFICIAL_SCHEMA_COMMIT,
        "broker": "KIWOOM",
        "source_api": "ka10076",
        "record_granularity": "order_aggregate_snapshot",
        "privacy_safe_record_sha256": _privacy_safe_mapping_sha256(record),
        "account_fingerprint": account_fingerprint,
        "broker_order_id": broker_order_id,
        "broker_execution_id": "",
        "broker_execution_id_available_in_source": False,
        "original_order_id": _text(record, "orig_ord_no"),
        "symbol": symbol,
        "order_status": _text(record, "ord_stt"),
        "order_type": _text(record, "io_tp_nm"),
        "trade_type": _text(record, "trde_tp"),
        "broker_order_time": order_time,
        "broker_confirm_time": "",
        "broker_lifecycle_time": order_time,
        **numeric_fields,
        "exchange_code": _text(record, "stex_tp"),
        "exchange_name": _text(record, "stex_tp_txt"),
        "sor_flag": _text(record, "sor_yn"),
        **_project_fail_closed_markers(),
    }


def _assert_same_text(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    field: str,
) -> None:
    a = str(left.get(field, "") or "").strip()
    b = str(right.get(field, "") or "").strip()
    if a and b and a != b:
        raise KiwoomNativeExecutionError(
            f"REST snapshot reconciliation mismatch for {field}: {a!r} != {b!r}"
        )


def _assert_same_numeric(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    field: str,
) -> None:
    a = str(left.get(field, "") or "").strip()
    b = str(right.get(field, "") or "").strip()
    if not a or not b:
        return
    if _as_decimal(a, field=field) != _as_decimal(b, field=field):
        raise KiwoomNativeExecutionError(
            f"REST snapshot reconciliation mismatch for {field}: {a!r} != {b!r}"
        )


def reconcile_kiwoom_rest_order_snapshots(
    snapshots: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Fail-closed reconciliation for same-order ``kt00007``/``ka10076`` snapshots.

    Callers should pass snapshots captured for the same logical order and sufficiently
    close in time that quantity state is intended to match. This helper proves only
    internal structural consistency. It never establishes real-account provenance.
    """
    rows = list(snapshots)
    if len(rows) < 2:
        raise KiwoomNativeExecutionError(
            "REST snapshot reconciliation requires at least two normalized rows"
        )

    allowed_sources = {"kt00007", "ka10076"}
    for row in rows:
        if not isinstance(row, Mapping):
            raise KiwoomNativeExecutionError("normalized snapshot must be a mapping")
        if row.get("source_api") not in allowed_sources:
            raise KiwoomNativeExecutionError(
                "REST snapshot reconciliation accepts only kt00007/ka10076 rows"
            )
        if row.get("broker") != "KIWOOM":
            raise KiwoomNativeExecutionError("snapshot broker must be KIWOOM")
        if row.get("genuine_live_provenance_verified") is not False:
            raise KiwoomNativeExecutionError(
                "normalized snapshot must remain provenance fail-closed"
            )
        _validate_account_fingerprint(str(row.get("account_fingerprint", "")))

    first = rows[0]
    for other in rows[1:]:
        for field in (
            "account_fingerprint",
            "broker_order_id",
            "symbol",
            "original_order_id",
        ):
            _assert_same_text(first, other, field)
        for field in (
            "order_qty",
            "order_price",
            "fill_qty",
            "fill_price",
            "remaining_qty",
        ):
            _assert_same_numeric(first, other, field)

    source_apis = sorted({str(row["source_api"]) for row in rows})
    return {
        "reconciliation_contract": REST_RECONCILIATION_CONTRACT,
        "official_schema_commit": OFFICIAL_SCHEMA_COMMIT,
        "broker": "KIWOOM",
        "source_apis": source_apis,
        "account_fingerprint": first["account_fingerprint"],
        "broker_order_id": first["broker_order_id"],
        "symbol": first["symbol"],
        "rest_snapshot_count": len(rows),
        "rest_snapshot_structure_reconciled": True,
        "genuine_live_provenance_verified": False,
        "project_live_evidence_admitted": False,
    }
