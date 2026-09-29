"""Metadata-only feasibility probe for official KRX identity/status sources.

This probe is data-source infrastructure, NOT alpha/performance research. It
never persists KRX numeric market rows. It records only reachability, row
counts, column names, source identifiers and errors needed to decide whether a
future historical PIT ingestion job can be built reproducibly.

Important: source reachability does not close the Final Judge blocker. Historical
coverage, point-in-time availability, security mapping and exact event/economic
semantics must still be audited before `judge_security_status_ready=True`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable


PINNED_KRX_DATA_API = "e6ebac9b71482db127348d8a08ebc6743aa3b50e"
OUT = Path("research_results/krx_status_source_probe")


def _frame_meta(df) -> dict[str, Any]:
    return {
        "reachable": True,
        "rows": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "server_current_datetime": df.attrs.get("current_datetime"),
    }


def _try(name: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"name": name, **_frame_meta(fn())}
    except Exception as exc:  # source probe must retain fail-closed diagnostics
        return {
            "name": name,
            "reachable": False,
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:700],
        }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    configured = bool(os.getenv("KRX_ID")) and bool(os.getenv("KRX_PW"))
    report: dict[str, Any] = {
        "purpose": "OFFICIAL_KRX_STATUS_SOURCE_FEASIBILITY_ONLY_NOT_PERFORMANCE_RESEARCH",
        "numeric_market_data_persisted": False,
        "credentials_present": configured,
        "pinned_krx_data_api_commit": PINNED_KRX_DATA_API,
        "official_screen_contracts": {
            "trading_halt": "MDCSTAT213 / KRX issue statistics trading-halt history",
            "cleanup_trading": "MDCSTAT237 / KRX cleanup-trading status",
            "delisted": "MDCSTAT238 / KRX delisted-security status",
            "delisted_price": "MDCSTAT239 / KRX delisted-security price trend",
        },
        "candidate_low_level_blds_not_yet_promoted_to_contract": {
            "trading_halt": "dbms/MDC/STAT/issue/MDCSTAT21301",
            "cleanup_trading": "dbms/MDC/STAT/issue/MDCSTAT23701",
        },
        "status": "AUTH_NOT_CONFIGURED" if not configured else "PENDING",
        "judge_security_status_ready": False,
        "why_not_judge_ready": [
            "historical common-stock identity coverage not yet reconstructed and audited",
            "event_time/published_at/available_at/ingested_at lineage not yet complete",
            "halt/cleanup/delisting event and execution economics not yet joined to decisions",
        ],
    }

    if not configured:
        (OUT / "summary.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("KRX_STATUS_SOURCE_PROBE=" + json.dumps(report, ensure_ascii=False), flush=True)
        return

    from krx_data_api import fetch, get_krx_auth, transport

    probes: list[dict[str, Any]] = []

    # Catalog-backed sources are already defined by the pinned client.
    probes.append(_try("listed_stocks_current_identity", lambda: fetch("listed_stocks", auth=True)))
    probes.append(_try(
        "new_listing_history_sample",
        lambda: fetch("new_listing", strtDd="20240101", endDd="20241231", auth=True),
    ))
    probes.append(_try(
        "delisted_history_sample",
        lambda: fetch("delisted", strtDd="20240101", endDd="20241231", auth=True),
    ))

    # The pinned catalog does not expose MDCSTAT213/237. Probe the KRX low-level
    # transport explicitly, but treat these BLDs as candidates until a live
    # authenticated response validates them. No numeric rows are persisted.
    session = get_krx_auth().session

    def halt_probe():
        payload = transport.json_data(
            "dbms/MDC/STAT/issue/MDCSTAT21301",
            {
                "isuCd": "KR7000300004",
                "isuCd2": "000300",
                "strtDd": "20240101",
                "endDd": "20251231",
            },
            session=session,
            menu_id="MDC0202",
        )
        import pandas as pd
        return pd.DataFrame(payload.get("output") or payload.get("OutBlock_1") or [])

    def cleanup_probe():
        payload = transport.json_data(
            "dbms/MDC/STAT/issue/MDCSTAT23701",
            {"mktId": "ALL"},
            session=session,
            menu_id="MDC0202",
        )
        import pandas as pd
        return pd.DataFrame(payload.get("output") or payload.get("OutBlock_1") or [])

    probes.append(_try("trading_halt_candidate_bld", halt_probe))
    probes.append(_try("cleanup_trading_candidate_bld", cleanup_probe))

    report["probes"] = probes
    catalog_ok = all(
        p.get("reachable") for p in probes
        if p["name"] in {
            "listed_stocks_current_identity",
            "new_listing_history_sample",
            "delisted_history_sample",
        }
    )
    candidate_ok = all(
        p.get("reachable") for p in probes
        if p["name"] in {"trading_halt_candidate_bld", "cleanup_trading_candidate_bld"}
    )
    report["status"] = (
        "SOURCE_FAMILIES_REACHABLE_NEEDS_HISTORICAL_PIT_AUDIT"
        if catalog_ok and candidate_ok
        else "PARTIAL_OR_UNVERIFIED_SOURCE_ACCESS"
    )
    report["candidate_blds_live_validated"] = bool(candidate_ok)
    report["judge_security_status_ready"] = False

    (OUT / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("KRX_STATUS_SOURCE_PROBE=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
