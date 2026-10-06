"""Validate redacted REAL account-scope smoke summaries without granting admission.

This module consumes only the public/redacted summary shape emitted by the
read-only smoke script. It cannot authenticate an account, bind a journal,
establish execution provenance, or authorize orders.
"""

REQUIRED_TRUE = (
    "TOKEN_OK",
    "ACCOUNT_ENDPOINT_OK",
    "SETTLEMENT_ENDPOINT_OK",
    "SETTLEMENT_FIELDS_VALID",
    "BROKER_TODAY_ENDPOINT_OK",
    "TRADING_DATE_ORIGIN_ATTESTED",
    "ORDER_HISTORY_ENDPOINT_OK",
    "ORDER_HISTORY_COMPLETE",
    "OPEN_ORDER_ENDPOINT_OK",
    "OPEN_ORDER_COMPLETE",
    "FILLED_ORDER_ENDPOINT_OK",
    "FILLED_ORDER_COMPLETE",
    "HOLDINGS_KRX_ENDPOINT_OK",
    "HOLDINGS_KRX_COMPLETE",
    "HOLDINGS_NXT_ENDPOINT_OK",
    "HOLDINGS_NXT_COMPLETE",
    "ACCOUNT_SCOPE_BASELINE_COMPLETE",
    "BROKER_NATIVE_ORDER_SNAPSHOT_CAPTURE_TESTED",
)
COUNT_FIELDS = (
    "ORDER_HISTORY_ROWS",
    "OPEN_ORDER_ROWS",
    "FILLED_ORDER_ROWS",
    "HOLDING_ROWS_KRX",
    "HOLDING_ROWS_NXT",
)

def assess_redacted_account_scope(summary: dict) -> dict:
    if type(summary) is not dict:
        raise ValueError("ACCOUNT_SCOPE_SUMMARY_INVALID")
    if summary.get("STAGE") != "REAL_ACCOUNT_SCOPE_READ_ONLY_SMOKE":
        raise ValueError("ACCOUNT_SCOPE_SUMMARY_INVALID")
    if type(summary.get("RETURN_CODE")) is not int or summary["RETURN_CODE"] != 0:
        raise ValueError("ACCOUNT_SCOPE_SUMMARY_INVALID")
    for name in REQUIRED_TRUE:
        if summary.get(name) is not True:
            raise ValueError("ACCOUNT_SCOPE_SUMMARY_INVALID")
    for name in COUNT_FIELDS:
        value = summary.get(name)
        if type(value) is not int or value < 0:
            raise ValueError("ACCOUNT_SCOPE_SUMMARY_INVALID")
    forbidden_true = (
        "BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED",
        "DURABLE_JOURNAL_BOUND",
        "ACCOUNT_SETTLEMENT_ADMITTED",
        "GENUINE_LIVE_PROVENANCE_VERIFIED",
        "REAL_ORDERS_AUTHORIZED",
        "FUNDS_MOVEMENT_AUTHORIZED",
        "PERMISSION_CHANGE_AUTHORIZED",
    )
    if any(summary.get(name) is True for name in forbidden_true):
        raise ValueError("ACCOUNT_SCOPE_SUMMARY_OVERCLAIM")
    if summary.get("ORDERING") != "DISABLED":
        raise ValueError("ACCOUNT_SCOPE_SUMMARY_OVERCLAIM")
    day = summary.get("TRADING_DATE")
    if type(day) is not str or len(day) != 10:
        raise ValueError("ACCOUNT_SCOPE_SUMMARY_INVALID")
    return {
        "mode": "REDACTED_REAL_ACCOUNT_SCOPE_SUMMARY",
        "trading_date": day,
        "account_scope_baseline_complete": True,
        "order_snapshot_capture_tested": True,
        "row_counts": {name: summary[name] for name in COUNT_FIELDS},
        "broker_native_execution_id_capture_tested": False,
        "durable_journal_bound": False,
        "account_settlement_admitted": False,
        "genuine_live_provenance_verified": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "broker_permission_change_authorized": False,
    }
