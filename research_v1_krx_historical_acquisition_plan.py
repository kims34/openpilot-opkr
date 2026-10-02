"""Fail-closed validator for the frozen KRX historical acquisition plan."""
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
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("plan_id") == "INDEXALERT-KRX-HIST-ACQ-v1", "plan_id drift")
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
    rules=identity.get("identity_rules") or {}
    _require(rules.get("market_filter") == "KOSPI only", "identity market drift")
    _require(rules.get("never_join_by_name_only") is True, "name-only join guard lost")
    _require(rules.get("episode_key") == "market|short_code|listing_date", "episode key drift")
    _require(rules.get("overlapping_same_short_code_episodes_fail_closed") is True, "episode overlap guard lost")

    status=phases.get("status_history") or {}
    halt=status.get("trading_halt") or {}
    _require(halt.get("bld") == "dbms/MDC/STAT/issue/MDCSTAT21301", "halt BLD drift")
    _require(halt.get("route_max_period_days") == 730, "halt max-period drift")
    chunks=halt.get("fixed_calendar_chunks") or []
    _require(len(chunks) == 6, "halt chunk count drift")
    _require(chunks[0] == ["2015-06-15","2017-06-13"], "first halt chunk drift")
    _require(chunks[-1] == ["2025-06-12","2026-10-01"], "last halt chunk drift")

    inv=phases.get("investor_flow_history") or {}
    _require(inv.get("bld") == "dbms/MDC/STAT/standard/MDCSTAT02303", "investor BLD drift")
    _require(inv.get("pit_publication_floor") == "20:00 Asia/Seoul", "PIT floor drift")
    _require(inv.get("expected_calendar_windows_if_active_full_period") == 12, "investor chunking drift")

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
        "plan_id":"INDEXALERT-KRX-HIST-ACQ-v1",
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
