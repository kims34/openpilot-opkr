"""Minimal fail-closed KRX investor-flow source probe.

This is NOT a backtest and does not persist KRX numeric market data. It only
checks whether an authenticated KRX Data Marketplace web session is available
and whether the documented individual-investor daily screen route returns a
parseable frame for one security over a tiny historical window.

Authentication routes are deliberately distinct:
- KRX_ID/KRX_PW: Data Marketplace authenticated web-session route used here.
- KRX OpenAPI AUTH_KEY: separate official OpenAPI route requiring key approval
  and approval for each API service. No exact public OpenAPI mapping for this
  required per-security investor-flow dataset is assumed by this probe.

Credentials are never printed or written to artifacts. Source feasibility is
not feature-promotion evidence.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> None:
    out = Path("research_results/krx_investor_flow_probe")
    out.mkdir(parents=True, exist_ok=True)

    session_configured = bool(os.getenv("KRX_ID")) and bool(os.getenv("KRX_PW"))
    openapi_key_present = bool(os.getenv("KRX_OPENAPI_AUTH_KEY"))
    report = {
        "purpose": "DATA_SOURCE_FEASIBILITY_ONLY_NOT_PERFORMANCE_RESEARCH",
        "source": "KRX_Data_Marketplace_MDCSTAT02303_via_authenticated_web_session",
        "numeric_market_data_persisted": False,
        # Backward-compatible field: this refers to the web-session route only.
        "credentials_present": session_configured,
        "data_marketplace_session_credentials_present": session_configured,
        "official_openapi_auth_key_present": openapi_key_present,
        "active_probe_access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "openapi_route_status": (
            "KEY_PRESENT_BUT_REQUIRED_INVESTOR_FLOW_API_MAPPING_NOT_ESTABLISHED"
            if openapi_key_present
            else "AUTH_KEY_NOT_CONFIGURED_AND_REQUIRED_INVESTOR_FLOW_API_MAPPING_NOT_ESTABLISHED"
        ),
        "status": "AUTH_NOT_CONFIGURED" if not session_configured else "PENDING",
        "available_at_policy_if_adopted": (
            "day_D final stock investor trading results must not enter a decision before publication; "
            "the official KRX Data Marketplace investor-trading page states final day-D results are provided after 20:00"
        ),
        "source_route_policy": {
            "data_marketplace_session": (
                "KRX_ID/KRX_PW may be used only for authenticated Data Marketplace source-feasibility checks"
            ),
            "official_openapi": (
                "AUTH_KEY is separate and must not be treated as equivalent unless an exact approved API service covers the required dataset"
            ),
            "no_auth_substitution": True,
        },
        "why_not_feature_ready": [
            "official reproducible historical access contract is not yet frozen",
            "exact public OpenAPI service mapping for required per-security investor flow is not established",
            "historical coverage and stable security mapping are not yet audited",
            "event_time/published_at/available_at/ingested_at lineage is not yet complete",
        ],
    }

    if not session_configured:
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("KRX_INVESTOR_FLOW_PROBE=" + json.dumps(report, ensure_ascii=False), flush=True)
        return

    try:
        from krx_data_api import fetch

        # One security, three already-completed sessions only. No bulk crawl.
        # This uses the authenticated Data Marketplace session route, not the
        # KRX OpenAPI AUTH_KEY route.
        df = fetch(
            "investor_trading_individual_daily",
            isuCd="KR7005930003",
            strtDd="20260921",
            endDd="20260923",
            askBid="3",
            trdVolVal="2",
            auth=True,
        )
        report.update({
            "status": "SOURCE_REACHABLE" if len(df) else "SOURCE_REACHABLE_EMPTY_RESULT",
            "rows": int(len(df)),
            "columns": [str(x) for x in df.columns],
            "index_name": None if df.index.name is None else str(df.index.name),
            "probe_security": "005930",
            "probe_window": ["2026-09-21", "2026-09-23"],
        })
    except Exception as exc:  # fail closed but keep CI diagnostic artifact
        report.update({
            "status": "SOURCE_UNREACHABLE_OR_AUTH_FAILED",
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:500],
        })

    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("KRX_INVESTOR_FLOW_PROBE=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
