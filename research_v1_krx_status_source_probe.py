"""Metadata-only feasibility probe for official KRX identity/status sources.

This probe is data-source infrastructure, NOT alpha/performance research. It
never persists KRX numeric market rows. It records only reachability, row
counts, column names, source identifiers and errors needed to decide whether a
future historical PIT ingestion job can be built reproducibly.

Authentication routes are deliberately distinguished:
- KRX_ID/KRX_PW: Data Marketplace authenticated web-session route used by the
  pinned exploratory client below.
- KRX OpenAPI AUTH_KEY: separate official OpenAPI route requiring an
  authentication-key application plus per-API usage approval. This probe does
  not substitute an AUTH_KEY for web-session access and does not claim that the
  required halt/cleanup/delisting datasets are available in the public OpenAPI
  catalog until an exact official API service mapping is documented.

Important: source reachability does not close the Final Judge blocker. Historical
coverage, point-in-time availability, security mapping and exact event/economic
semantics must still be audited before `judge_security_status_ready=True`.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

from research_v1_krx_source_gates import audit_source_gates


PINNED_KRX_DATA_API = "e6ebac9b71482db127348d8a08ebc6743aa3b50e"
OUT = Path("research_results/krx_status_source_probe")
SOURCE_FAMILY = "KRX_SECURITY_STATUS"
INTENDED_USE_SCOPE = "INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION"


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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


def source_gate_audit(*, session_configured: bool) -> dict:
    """Map this tiny probe to the frozen A-F source contract conservatively.

    A successful tiny authenticated request can improve evidence, but this probe
    is structurally incapable of closing historical coverage, PIT lineage or
    licensing. It therefore never returns all PASS.
    """
    statuses = {
        "A": "PARTIAL" if session_configured else "BLOCKED",
        "B": "PARTIAL",
        "C": "BLOCKED",
        "D": "BLOCKED",
        "E": "PARTIAL",
        "F": "PARTIAL",
    }
    evidence = {
        "A": (
            "Data Marketplace session credentials are present and the probe may exercise the authenticated route, "
            "but the exact authorized historical product/access contract for the full status reconstruction is not closed."
            if session_configured
            else "KRX_ID/KRX_PW are absent in the active runtime, so the authenticated Data Marketplace route is not exercised."
        ),
        "B": (
            "MDCSTAT213/237/238/239 screen families are identified, but some low-level mappings remain provisional "
            "and exact approved service/schema equivalence for the complete historical family is not closed."
        ),
        "C": (
            "The tiny source probe does not reconstruct or independently audit full requested-period common-stock/status coverage."
        ),
        "D": (
            "Record-level historical event_time/published_at/available_at/ingested_at lineage across all required status families is not established."
        ),
        "E": (
            "The client revision, route metadata, schema metadata and fail-closed diagnostics are reproducible, "
            "but end-to-end historical acquisition and coverage reproducibility remain open."
        ),
        "F": (
            "Internal research and external/commercial use are separated by contract, but rights for the final selected historical route remain unverified."
        ),
    }
    return audit_source_gates(
        source_family=SOURCE_FAMILY,
        intended_use_scope=INTENDED_USE_SCOPE,
        statuses=statuses,
        evidence=evidence,
    )


def _finalise_report(report: dict[str, Any], *, session_configured: bool) -> dict[str, Any]:
    report["authenticated_request_attempted"] = bool(session_configured)
    report["source_gate_audit"] = source_gate_audit(session_configured=session_configured)
    contract_material = {
        "source_family": SOURCE_FAMILY,
        "intended_use_scope": INTENDED_USE_SCOPE,
        "active_probe_access_route": report["active_probe_access_route"],
        "pinned_krx_data_api_commit": report["pinned_krx_data_api_commit"],
        "official_screen_contracts": report["official_screen_contracts"],
        "candidate_low_level_blds_not_yet_promoted_to_contract": report[
            "candidate_low_level_blds_not_yet_promoted_to_contract"
        ],
        "source_route_policy": report["source_route_policy"],
    }
    report["probe_contract_fingerprint_sha256"] = _canonical_sha256(contract_material)
    result_material = {
        key: value
        for key, value in report.items()
        if key not in {"probe_result_fingerprint_sha256"}
    }
    report["probe_result_fingerprint_sha256"] = _canonical_sha256(result_material)
    return report


def _write_report(report: dict[str, Any], *, session_configured: bool) -> None:
    final = _finalise_report(report, session_configured=session_configured)
    (OUT / "summary.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("KRX_STATUS_SOURCE_PROBE=" + json.dumps(final, ensure_ascii=False), flush=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    session_configured = bool(os.getenv("KRX_ID")) and bool(os.getenv("KRX_PW"))
    openapi_key_present = bool(os.getenv("KRX_OPENAPI_AUTH_KEY"))
    report: dict[str, Any] = {
        "purpose": "OFFICIAL_KRX_STATUS_SOURCE_FEASIBILITY_ONLY_NOT_PERFORMANCE_RESEARCH",
        "numeric_market_data_persisted": False,
        # Backward-compatible field: this means the web-session route only.
        "credentials_present": session_configured,
        "data_marketplace_session_credentials_present": session_configured,
        "official_openapi_auth_key_present": openapi_key_present,
        "active_probe_access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "openapi_route_status": (
            "KEY_PRESENT_BUT_REQUIRED_STATUS_API_MAPPING_NOT_ESTABLISHED"
            if openapi_key_present
            else "AUTH_KEY_NOT_CONFIGURED_AND_REQUIRED_STATUS_API_MAPPING_NOT_ESTABLISHED"
        ),
        "source_route_policy": {
            "data_marketplace_session": (
                "KRX_ID/KRX_PW may be used only for authenticated Data Marketplace source-feasibility checks"
            ),
            "official_openapi": (
                "AUTH_KEY is a separate KRX OpenAPI credential and may be used only after the exact required API service is identified and approved"
            ),
            "no_auth_substitution": True,
        },
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
        "status": "AUTH_NOT_CONFIGURED" if not session_configured else "PENDING",
        "judge_security_status_ready": False,
        "why_not_judge_ready": [
            "exact official access/product contract for historical halt/cleanup/delisting data is not yet established",
            "historical common-stock identity coverage not yet reconstructed and audited",
            "event_time/published_at/available_at/ingested_at lineage not yet complete",
            "halt/cleanup/delisting event and execution economics not yet joined to decisions",
        ],
    }

    if not session_configured:
        _write_report(report, session_configured=False)
        return

    from krx_data_api import fetch, get_krx_auth, transport

    probes: list[dict[str, Any]] = []

    # Catalog-backed Data Marketplace sources already defined by the pinned
    # session client. These are not KRX OpenAPI AUTH_KEY calls.
    probes.append(_try("listed_stocks_current_identity", lambda: fetch("listed_stocks", auth=True)))
    probes.append(_try(
        "new_listing_history_sample",
        lambda: fetch("new_listing", strtDd="20240101", endDd="20241231", auth=True),
    ))
    probes.append(_try(
        "delisted_history_sample",
        lambda: fetch("delisted", strtDd="20240101", endDd="20241231", auth=True),
    ))

    # The pinned session catalog does not expose MDCSTAT213/237. Probe the KRX
    # Data Marketplace low-level transport explicitly, but keep these BLDs as
    # candidates until a live authenticated response validates them. No numeric
    # rows are persisted. This is not equivalent to an approved KRX OpenAPI.
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
    _write_report(report, session_configured=True)


if __name__ == "__main__":
    main()
