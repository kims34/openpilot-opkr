"""Minimal fail-closed KRX investor-flow source probe.

This is NOT a backtest and does not persist KRX numeric market data.  It only
checks whether an authenticated KRX Data Marketplace session is available and
whether the documented individual-investor daily endpoint returns a parseable
frame for one security over a tiny historical window.

Credentials are read from KRX_ID/KRX_PW by the pinned external client.  They are
never printed or written to artifacts.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> None:
    out = Path("research_results/krx_investor_flow_probe")
    out.mkdir(parents=True, exist_ok=True)

    configured = bool(os.getenv("KRX_ID")) and bool(os.getenv("KRX_PW"))
    report = {
        "purpose": "DATA_SOURCE_FEASIBILITY_ONLY_NOT_PERFORMANCE_RESEARCH",
        "source": "KRX_Data_Marketplace_MDCSTAT02303_via_authenticated_web_session",
        "numeric_market_data_persisted": False,
        "credentials_present": configured,
        "status": "AUTH_NOT_CONFIGURED" if not configured else "PENDING",
        "available_at_policy_if_adopted": (
            "day_D_final_investor_results_must_not_enter_a_decision_before_KRX_publication; "
            "current official page states final daily trading results are provided after 20:00"
        ),
    }

    if not configured:
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("KRX_INVESTOR_FLOW_PROBE=" + json.dumps(report, ensure_ascii=False), flush=True)
        return

    try:
        from krx_data_api import fetch

        # One security, three already-completed sessions only.  No bulk crawl.
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
