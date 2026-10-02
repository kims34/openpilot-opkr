"""Fail-closed validator for the frozen KRX historical acquisition plan v2."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.json")


class KRXHistoricalPlanError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXHistoricalPlanError(msg)


def canonical_sha256(value: Any) -> str:
    raw=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_plan(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(data.get("schema_version") == "2", "schema_version drift")
    _require(data.get("plan_id") == "INDEXALERT-KRX-HIST-ACQ-v2", "plan_id drift")
    _require(data.get("supersedes_plan_id") == "INDEXALERT-KRX-HIST-ACQ-v1", "superseded plan drift")
    _require(data.get("superseded_before_any_bulk_network_execution") is True, "v1 supersession timing drift")
    _require(data.get("network_execution_authorized") is False, "plan must not self-authorize execution")

    period=data.get("research_required_period") or {}
    _require(period.get("start") == "2015-06-15", "research start drift")
    _require(period.get("end") == "2026-10-01", "research end drift")
    _require(period.get("market") == "KOSPI", "market scope drift")

    rights=data.get("rights") or {}
    for key in (
        "full_historical_download_rights_authorized",
        "high_frequency_collection_authorized",
        "automated_collection_authorized",
    ):
        _require(rights.get(key) is True, f"{key} missing")
    for key in ("redistribution_authorized","external_sale_authorized","external_leakage_authorized"):
        _require(rights.get(key) is False, f"{key} illegally true")

    phases=data.get("phases") or {}
    identity=phases.get("identity_seed") or {}
    fixed=identity.get("fixed_requests") or []
    _require(len(fixed) == 2, "fixed master request count drift")
    _require(fixed[0].get("basDd") == "20150615", "start master date drift")
    _require(fixed[1].get("basDd") == "20261001", "end master date drift")
    for row in fixed:
        _require(row.get("route") == "KRX_OPENAPI_STK_ISU_BASE_INFO", "identity master route drift")
        _require(row.get("endpoint","").endswith("/stk_isu_base_info"), "identity master endpoint drift")

    windowed=identity.get("windowed_requests") or {}
    for name,bld in (
        ("new_listing_history","dbms/MDC/STAT/issue/MDCSTAT20001"),
        ("delisted_history","dbms/MDC/STAT/issue/MDCSTAT23801"),
    ):
        row=windowed.get(name) or {}
        _require(row.get("bld") == bld, f"{name} BLD drift")
        _require(row.get("request_count") == 12, f"{name} request-count drift")
        windows=row.get("calendar_year_windows") or []
        _require(len(windows) == 12, f"{name} window-count drift")
        _require(windows[0] == ["2015-06-15","2015-12-31"], f"{name} first window drift")
        _require(windows[-1] == ["2026-01-01","2026-10-01"], f"{name} last window drift")

    dynamic=identity.get("dynamic_standard_code_snapshots") or {}
    _require(dynamic.get("route") == "KRX_OPENAPI_STK_ISU_BASE_INFO", "dynamic master route drift")
    _require(dynamic.get("request_count_formula") == "U_new_listing_dates", "dynamic master formula drift")
    _require(dynamic.get("no_fallback_from_later_snapshot") is True, "later-snapshot fallback guard lost")

    rules=identity.get("identity_rules") or {}
    _require(rules.get("market_filter") == "KOSPI only", "identity market drift")
    _require(rules.get("common_stock_filter") == "SECUGRP_NM=주권 and KIND_STKCERT_TP_NM=보통주", "common-stock filter drift")
    _require(rules.get("never_join_by_name_only") is True, "name-only join guard lost")
    _require(rules.get("episode_key") == "market|short_code|listing_date", "episode key drift")
    _require(rules.get("standard_code_required_for_every_episode") is True, "standard-code requirement lost")
    _require(rules.get("standard_code_source_for_preexisting_episode") == "research_start_security_master", "preexisting standard-code source drift")
    _require(rules.get("standard_code_source_for_new_episode") == "listing-date security-master snapshot", "new-episode standard-code source drift")
    _require(rules.get("end_snapshot_is_reconciliation_only") is True, "end snapshot role drift")
    _require(rules.get("unresolved_standard_code_fail_closed") is True, "unresolved standard-code guard lost")
    _require(rules.get("inconsistent_standard_code_across_snapshots_fail_closed") is True, "standard-code consistency guard lost")
    _require(rules.get("per_security_isuCd") == "standard_code", "isuCd identity rule drift")
    _require(rules.get("trading_halt_isuCd2") == "short_code", "halt isuCd2 rule drift")

    status=phases.get("status_history") or {}
    cleanup=status.get("cleanup_trading") or {}
    _require(cleanup.get("request_count") == 12, "cleanup request-count drift")
    halt=status.get("trading_halt") or {}
    _require(halt.get("bld") == "dbms/MDC/STAT/issue/MDCSTAT21301", "halt BLD drift")
    _require(halt.get("route_max_period_days") == 730, "halt max-period drift")
    chunks=halt.get("fixed_calendar_chunks") or []
    _require(len(chunks) == 6, "halt chunk count drift")
    _require(chunks[0] == ["2015-06-15","2017-06-13"], "first halt chunk drift")
    _require(chunks[-1] == ["2025-06-12","2026-10-01"], "last halt chunk drift")

    inv=phases.get("investor_flow_history") or {}
    _require(inv.get("bld") == "dbms/MDC/STAT/standard/MDCSTAT02303", "investor BLD drift")
    _require(len(inv.get("calendar_year_windows") or []) == 12, "investor chunk-count drift")
    _require(inv.get("pit_publication_floor") == "20:00 Asia/Seoul", "PIT floor drift")
    _require("isuCd=standard_code" in str(inv.get("request_formula") or ""), "investor standard-code rule lost")

    counts=data.get("request_count_formula") or {}
    _require(counts.get("fixed_identity_requests") == 26, "fixed identity request-count drift")
    _require(counts.get("dynamic_listing_date_master_requests") == "U_new_listing_dates", "dynamic request formula drift")
    _require(counts.get("cleanup_year_windows") == 12, "cleanup year count drift")

    privacy=data.get("privacy_and_storage") or {}
    for key in (
        "raw_krx_rows_private_research_only",
        "raw_rows_must_not_be_committed_to_git",
        "raw_rows_must_not_be_uploaded_as_public_actions_artifacts",
        "actions_logs_may_emit_metadata_only",
        "every_raw_object_requires_sha256",
        "every_request_requires_receipt",
        "every_batch_requires_manifest",
    ):
        _require(privacy.get(key) is True, f"{key} guard lost")

    safety=data.get("operational_safety") or {}
    _require(safety.get("default_concurrency") == 4, "default concurrency drift")
    _require(safety.get("max_concurrency_without_new_plan_version") == 8, "max concurrency drift")
    _require(safety.get("checkpoint_after_each_request") is True, "checkpoint guard lost")
    _require(safety.get("resume_from_receipts_only") is True, "resume guard lost")

    authority=data.get("authority") or {}
    _require(authority.get("rights_to_acquire") is True, "rights-to-acquire lost")
    for key in (
        "bulk_network_execution_authorized_by_user",
        "source_gate_c_closed",
        "source_gate_d_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid":True,
        "plan_id":"INDEXALERT-KRX-HIST-ACQ-v2",
        "plan_fingerprint_sha256":canonical_sha256(data),
        "rights_to_acquire":True,
        "network_execution_authorized":False,
        "gate_c_closed":False,
        "gate_d_closed":False,
        "sealed_holdout_authorized":False,
        "live_trading_authorized":False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_plan(json.loads(path.read_text(encoding="utf-8")))


if __name__=="__main__":
    print(json.dumps(validate_file(),ensure_ascii=False,indent=2))
