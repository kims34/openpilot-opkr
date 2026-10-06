"""Fail-closed REAL-account read-only configuration boundary.

This module performs configuration admission only. It sends no network request,
does not authenticate, query an account, submit/cancel/amend an order, change a
broker permission, move funds, or grant LIVE evidence/ordering authority.
"""
from kiwoom_readonly_configuration_audit import REAL_BASE_URL


READ_ONLY_API_IDS = frozenset({"ka00001", "kt00007", "ka10076", "kt00018"})
ORDER_API_IDS = frozenset({"kt10000", "kt10001", "kt10002", "kt10003"})


class RealReadOnlyPreparationError(ValueError):
    pass


def _require(condition):
    if not condition:
        raise RealReadOnlyPreparationError("REAL_READ_ONLY_PREPARATION_BLOCKED")


def assess_real_readonly_preparation(configuration):
    _require(type(configuration) is dict)
    env = configuration.get("KIWOOM_ENV")
    base = configuration.get("KIWOOM_BASE_URL")
    ordering = configuration.get("KIWOOM_ORDERING_ENABLED")
    key = configuration.get("KIWOOM_APP_KEY")
    secret = configuration.get("KIWOOM_APP_SECRET")
    _require(type(env) is str and env.strip().upper() == "REAL")
    _require(type(base) is str and base == REAL_BASE_URL)
    _require(type(ordering) is str and ordering.strip().lower() in {"0","false","off","no"})
    _require(type(key) is str and bool(key.strip()))
    _require(type(secret) is str and bool(secret.strip()))
    return {
        "mode": "REAL_READ_ONLY_PREPARATION",
        "configuration_admitted": True,
        "allowed_api_ids": sorted(READ_ONLY_API_IDS),
        "ordering_configuration": "DISABLED",
        "network_request_attempted": False,
        "credentials_validated": False,
        "account_origin_authenticated": False,
        "broker_connectivity_verified": False,
        "account_settlement_admitted": False,
        "genuine_live_provenance_verified": False,
        "early_live_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "broker_permission_change_authorized": False,
    }


def require_readonly_api(api_id):
    _require(type(api_id) is str and api_id in READ_ONLY_API_IDS)
    _require(api_id not in ORDER_API_IDS)
    return api_id
