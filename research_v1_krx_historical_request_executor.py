"""One-request executor for the frozen KRX historical acquisition plan.

This module routes a validated request specification through the historical
worker core. It never self-authorizes network execution: execute_private_request
re-runs the frozen bulk preflight before the injected network fetcher can run.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping

from research_v1_krx_auth_preflight import DATA_MARKETPLACE_ROUTE
from research_v1_krx_historical_fetchers import (
    KRXHistoricalFetchError,
    fetch_data_marketplace_raw,
    fetch_openapi_raw,
    resolve_pinned_endpoint_request,
)
from research_v1_krx_historical_worker_core import (
    OPENAPI_ROUTE,
    execute_private_request,
)


OPENAPI_SECURITY_MASTER_ENDPOINT = (
    "https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info"
)

ALLOWED_DM_ENDPOINTS = {
    "new_listing": ("KRX_SECURITY_STATUS", "MDCSTAT20001"),
    "delisted": ("KRX_SECURITY_STATUS", "MDCSTAT23801"),
    "trading_halt": ("KRX_SECURITY_STATUS", "MDCSTAT21301"),
    "delisted_stock_price": ("KRX_SECURITY_STATUS", "MDCSTAT23902"),
    "investor_trading_individual_daily": ("KRX_INVESTOR_FLOW", "MDCSTAT02303"),
}
CLEANUP_CURRENT = "cleanup_current_reconciliation"


class KRXHistoricalRequestExecutorError(ValueError):
    pass


def _require_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise KRXHistoricalRequestExecutorError(f"{field} is required")
    return text


def _validate_standard_code(value: Any) -> str:
    code = _require_text(value, "isuCd").upper()
    if len(code) != 12 or not code.isalnum():
        raise KRXHistoricalRequestExecutorError("isuCd must be a 12-character standard code")
    return code


def _validate_short_code(value: Any) -> str:
    code = _require_text(value, "isuCd2")
    if len(code) != 6 or not code.isdigit():
        raise KRXHistoricalRequestExecutorError("isuCd2 must be a six-digit short code")
    return code


def _validate_yyyymmdd(value: Any, field: str) -> str:
    text = _require_text(value, field)
    if len(text) != 8 or not text.isdigit():
        raise KRXHistoricalRequestExecutorError(f"{field} must be YYYYMMDD")
    return text


def validate_request_spec(
    spec: Mapping[str, Any],
    *,
    catalog_getter: Any | None = None,
) -> dict[str, Any]:
    if not isinstance(spec, Mapping):
        raise KRXHistoricalRequestExecutorError("request spec must be an object")

    kind = _require_text(spec.get("kind"), "kind")
    params = dict(spec.get("params") or {})

    if kind == "security_master":
        bas_dd = _validate_yyyymmdd(params.get("basDd"), "basDd")
        return {
            "kind": kind,
            "source_family": "KRX_SECURITY_STATUS",
            "dataset_identifier": "stk_isu_base_info",
            "access_route": OPENAPI_ROUTE,
            "endpoint": OPENAPI_SECURITY_MASTER_ENDPOINT,
            "method": "GET",
            "params": {"basDd": bas_dd},
        }

    if kind == CLEANUP_CURRENT:
        if params and params != {"mktId": "ALL"}:
            raise KRXHistoricalRequestExecutorError(
                "cleanup current reconciliation accepts only mktId=ALL"
            )
        return {
            "kind": kind,
            "source_family": "KRX_SECURITY_STATUS",
            "dataset_identifier": "MDCSTAT23701",
            "access_route": DATA_MARKETPLACE_ROUTE,
            "bld": "dbms/MDC/STAT/issue/MDCSTAT23701",
            "method": "json",
            "menu_id": "MDC0202",
            "params": {"mktId": "ALL"},
        }

    if kind not in ALLOWED_DM_ENDPOINTS:
        raise KRXHistoricalRequestExecutorError(f"unsupported historical request kind: {kind}")

    family, dataset_identifier = ALLOWED_DM_ENDPOINTS[kind]
    if kind in {"trading_halt", "delisted_stock_price", "investor_trading_individual_daily"}:
        params["isuCd"] = _validate_standard_code(params.get("isuCd"))
    if kind == "trading_halt":
        params["isuCd2"] = _validate_short_code(params.get("isuCd2"))
    if "strtDd" in params:
        params["strtDd"] = _validate_yyyymmdd(params["strtDd"], "strtDd")
    if "endDd" in params:
        params["endDd"] = _validate_yyyymmdd(params["endDd"], "endDd")

    try:
        resolved = resolve_pinned_endpoint_request(
            kind,
            params,
            catalog_getter=catalog_getter,
        )
    except KRXHistoricalFetchError as exc:
        raise KRXHistoricalRequestExecutorError(str(exc)) from exc

    return {
        "kind": kind,
        "source_family": family,
        "dataset_identifier": dataset_identifier,
        "access_route": DATA_MARKETPLACE_ROUTE,
        "bld": resolved["bld"],
        "method": resolved["method"],
        "menu_id": resolved["menu_id"],
        "params": resolved["params"],
        "pinned_client_commit": resolved["pinned_client_commit"],
    }


def execute_request_spec(
    *,
    spec: Mapping[str, Any],
    environment: Mapping[str, str],
    git_worktree: str,
    client_revision: str,
    catalog_getter: Any | None = None,
    dm_fetch: Callable[..., Any] = fetch_data_marketplace_raw,
    openapi_fetch: Callable[..., Any] = fetch_openapi_raw,
    evaluation_time=None,
) -> dict[str, Any]:
    resolved = validate_request_spec(spec, catalog_getter=catalog_getter)

    if resolved["access_route"] == OPENAPI_ROUTE:
        request_metadata = {
            "endpoint": resolved["endpoint"],
            "method": "GET",
            "params": resolved["params"],
        }

        def fetcher(_canonical_request):
            return openapi_fetch(
                endpoint=resolved["endpoint"],
                params=resolved["params"],
                auth_key=str(environment.get("KRX_AUTH_KEY") or ""),
                network_authorized=True,
            )

    else:
        request_metadata = {
            "bld": resolved["bld"],
            "method": resolved["method"],
            "menu_id": resolved["menu_id"],
            "params": resolved["params"],
            "pinned_client_commit": resolved.get("pinned_client_commit"),
        }

        def fetcher(_canonical_request):
            return dm_fetch(
                method=resolved["method"],
                bld=resolved["bld"],
                params=resolved["params"],
                menu_id=resolved["menu_id"],
                network_authorized=True,
            )

    return execute_private_request(
        environment=environment,
        git_worktree=git_worktree,
        source_family=resolved["source_family"],
        dataset_identifier=resolved["dataset_identifier"],
        access_route=resolved["access_route"],
        request_metadata=request_metadata,
        client_revision=client_revision,
        fetcher=fetcher,
        evaluation_time=evaluation_time,
    )
