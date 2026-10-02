"""Offline-only staged task builder for the frozen KRX historical job.

This module never imports a network client and never performs KRX requests.
It emits request specifications in the exact shape consumed by
research_v1_krx_historical_request_executor. Endpoint BLD/menu/default resolution
therefore has one canonical implementation: the pinned endpoint resolver.

Security identifiers may exist only in private task rows. Public summaries emit
counts/hashes only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd

from research_v1_krx_historical_acquisition_plan import (
    validate_file as validate_acquisition_plan_file,
)
from research_v1_krx_historical_execution_contract import (
    validate_file as validate_execution_contract_file,
)
from research_v1_krx_historical_request_executor import CLEANUP_CURRENT
from research_v1_krx_historical_request_planner import build_private_request_plan


PLAN_PATH = Path("INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.json")
PLAN_ID = "INDEXALERT-KRX-HIST-ACQ-v3"
EXECUTION_CONTRACT_ID = "INDEXALERT-KRX-HIST-EXEC-v3"

PHASE_ORDER = (
    "IDENTITY_SEED",
    "IDENTITY_STANDARD_CODE_BINDING",
    "PER_SECURITY_HISTORY",
    "STATUS_ECONOMICS",
    "COVERAGE_PIT_AUDIT",
    "SOURCE_ADMISSION",
)


class KRXHistoricalBatchOrchestratorError(ValueError):
    pass


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _task(
    *,
    phase: str,
    source_family: str,
    kind: str,
    params: Mapping[str, Any],
    contains_security_identifier: bool,
) -> dict[str, Any]:
    if phase not in PHASE_ORDER:
        raise KRXHistoricalBatchOrchestratorError(f"unknown phase: {phase}")
    spec = {"kind": str(kind), "params": dict(params)}
    base = {
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": phase,
        "source_family": source_family,
        "request_spec": spec,
        "contains_security_identifier": bool(contains_security_identifier),
    }
    base["task_id"] = _canonical_sha256(base)
    return base


def _load_plan() -> dict[str, Any]:
    validated = validate_acquisition_plan_file(PLAN_PATH)
    if validated["plan_id"] != PLAN_ID:
        raise KRXHistoricalBatchOrchestratorError("acquisition plan binding drift")
    execution = validate_execution_contract_file()
    if execution["contract_id"] != EXECUTION_CONTRACT_ID:
        raise KRXHistoricalBatchOrchestratorError("execution contract binding drift")
    if execution["plan_id"] != PLAN_ID:
        raise KRXHistoricalBatchOrchestratorError("execution-plan binding drift")
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def build_identity_seed_tasks() -> list[dict[str, Any]]:
    """Build the fixed 27-request identity/status seed queue.

    2 approved OpenAPI security-master snapshots
    + 12 new-listing year windows
    + 12 delisted-history year windows
    + 1 current cleanup reconciliation snapshot.

    These specs intentionally omit pinned endpoint defaults; the request executor
    resolves those defaults from the one pinned endpoint catalog at execution.
    """
    plan = _load_plan()
    seed = plan["phases"]["identity_seed"]
    tasks: list[dict[str, Any]] = []

    for row in seed["fixed_requests"]:
        if row["route"] != "KRX_OPENAPI_STK_ISU_BASE_INFO":
            raise KRXHistoricalBatchOrchestratorError("unexpected fixed identity route")
        tasks.append(
            _task(
                phase="IDENTITY_SEED",
                source_family="KRX_SECURITY_STATUS",
                kind="security_master",
                params={"basDd": row["basDd"]},
                contains_security_identifier=False,
            )
        )

    new_cfg = seed["windowed_requests"]["new_listing_history"]
    if new_cfg["bld"] != "dbms/MDC/STAT/issue/MDCSTAT20001":
        raise KRXHistoricalBatchOrchestratorError("new-listing BLD drift")
    for start, end in new_cfg["calendar_year_windows"]:
        tasks.append(
            _task(
                phase="IDENTITY_SEED",
                source_family="KRX_SECURITY_STATUS",
                kind="new_listing",
                params={
                    "strtDd": str(start).replace("-", ""),
                    "endDd": str(end).replace("-", ""),
                },
                contains_security_identifier=False,
            )
        )

    delisted_cfg = seed["windowed_requests"]["delisted_history"]
    if delisted_cfg["bld"] != "dbms/MDC/STAT/issue/MDCSTAT23801":
        raise KRXHistoricalBatchOrchestratorError("delisted-history BLD drift")
    for start, end in delisted_cfg["calendar_year_windows"]:
        tasks.append(
            _task(
                phase="IDENTITY_SEED",
                source_family="KRX_SECURITY_STATUS",
                kind="delisted",
                params={
                    "strtDd": str(start).replace("-", ""),
                    "endDd": str(end).replace("-", ""),
                },
                contains_security_identifier=False,
            )
        )

    cleanup = plan["phases"]["status_history"]["cleanup_trading"][
        "current_cleanup_reconciliation"
    ]
    if cleanup["bld"] != "dbms/MDC/STAT/issue/MDCSTAT23701":
        raise KRXHistoricalBatchOrchestratorError("current cleanup BLD drift")
    tasks.append(
        _task(
            phase="IDENTITY_SEED",
            source_family="KRX_SECURITY_STATUS",
            kind=CLEANUP_CURRENT,
            params=dict(cleanup["request_params"]),
            contains_security_identifier=False,
        )
    )

    if len(tasks) != 27:
        raise KRXHistoricalBatchOrchestratorError(
            f"identity seed task count drift: {len(tasks)}"
        )
    if len({row["task_id"] for row in tasks}) != len(tasks):
        raise KRXHistoricalBatchOrchestratorError("duplicate identity seed task")
    return tasks


def build_listing_date_master_tasks(
    listing_dates: Iterable[Any],
) -> list[dict[str, Any]]:
    """One exact basic-info snapshot per unique new-listing date."""
    dates = pd.to_datetime(pd.Series(list(listing_dates)), errors="coerce").dropna()
    dates = dates.dt.normalize()
    start = pd.Timestamp("2015-06-15")
    end = pd.Timestamp("2026-10-01")
    dates = sorted({d for d in dates if start <= d <= end})
    return [
        _task(
            phase="IDENTITY_STANDARD_CODE_BINDING",
            source_family="KRX_SECURITY_STATUS",
            kind="security_master",
            params={"basDd": date.strftime("%Y%m%d")},
            contains_security_identifier=False,
        )
        for date in dates
    ]


def build_per_security_history_tasks(
    episodes: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Translate the frozen private request plan into executor-compatible specs."""
    private = build_private_request_plan(episodes)
    tasks: list[dict[str, Any]] = []

    for row in private.itertuples(index=False):
        start = pd.Timestamp(row.start).strftime("%Y%m%d")
        end = pd.Timestamp(row.end).strftime("%Y%m%d")
        if row.dataset == "trading_halt":
            tasks.append(
                _task(
                    phase="PER_SECURITY_HISTORY",
                    source_family="KRX_SECURITY_STATUS",
                    kind="trading_halt",
                    params={
                        "isuCd": row.isuCd,
                        "isuCd2": row.isuCd2,
                        "strtDd": start,
                        "endDd": end,
                    },
                    contains_security_identifier=True,
                )
            )
        elif row.dataset == "investor_flow_daily":
            tasks.append(
                _task(
                    phase="PER_SECURITY_HISTORY",
                    source_family="KRX_INVESTOR_FLOW",
                    kind="investor_trading_individual_daily",
                    params={
                        "isuCd": row.isuCd,
                        "strtDd": start,
                        "endDd": end,
                    },
                    contains_security_identifier=True,
                )
            )
        else:
            raise KRXHistoricalBatchOrchestratorError(
                f"unsupported private-plan dataset: {row.dataset}"
            )

    if len(tasks) != len(private):
        raise KRXHistoricalBatchOrchestratorError("per-security task count drift")
    if len({row["task_id"] for row in tasks}) != len(tasks):
        raise KRXHistoricalBatchOrchestratorError("duplicate per-security task")
    return tasks


def _history_short_code(value: Any) -> str:
    """Canonicalize KRX history short codes without deleting letters."""
    text = str(value or "").strip().upper()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    if text.isdigit() and 1 <= len(text) <= 6:
        text = text.zfill(6)
    if (
        len(text) != 6
        or not text.isascii()
        or not text.isalnum()
    ):
        raise KRXHistoricalBatchOrchestratorError("invalid delisted-history short code")
    return text


def _history_date(value: Any) -> pd.Timestamp | None:
    text = str(value or "").strip()
    if text in {"", "-", "nan", "None", "NaT"}:
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) != 8:
        raise KRXHistoricalBatchOrchestratorError(
            f"invalid delisted-history date: {value!r}"
        )
    ts = pd.to_datetime(digits, format="%Y%m%d", errors="coerce")
    if pd.isna(ts):
        raise KRXHistoricalBatchOrchestratorError(
            f"invalid delisted-history date: {value!r}"
        )
    return pd.Timestamp(ts).normalize()


def build_status_economics_tasks(
    episodes: pd.DataFrame,
    delisted_history: pd.DataFrame,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Build cleanup-price requests only where official cleanup intervals exist.

    Delisted episodes with no cleanup interval produce no MDCSTAT23902 request;
    they remain dependent on separate exact fill/recovery evidence. A partial
    cleanup interval (start without end or vice versa) is ambiguous and fails
    closed.
    """
    required_episode = {
        "episode_key", "short_code", "standard_code",
        "listing_date", "delisting_date", "source_delisted",
    }
    missing = required_episode - set(episodes.columns)
    if missing:
        raise KRXHistoricalBatchOrchestratorError(
            f"episodes missing status-economics columns: {sorted(missing)}"
        )
    required_history = {
        "종목코드", "상장일", "폐지일",
        "정리매매기간_시작일", "정리매매기간_종료일",
    }
    missing = required_history - set(delisted_history.columns)
    if missing:
        raise KRXHistoricalBatchOrchestratorError(
            f"delisted history missing cleanup columns: {sorted(missing)}"
        )

    history: dict[tuple[str, pd.Timestamp], dict[str, Any]] = {}
    for row in delisted_history.to_dict("records"):
        code = _history_short_code(row["종목코드"])
        listing = _history_date(row["상장일"])
        delisting = _history_date(row["폐지일"])
        if listing is None or delisting is None:
            raise KRXHistoricalBatchOrchestratorError(
                "delisted history requires listing and delisting dates"
            )
        key = (code, listing)
        if key in history:
            raise KRXHistoricalBatchOrchestratorError(
                f"duplicate delisted-history episode: {code} {listing.date()}"
            )
        history[key] = {
            "delisting_date": delisting,
            "cleanup_start": _history_date(row["정리매매기간_시작일"]),
            "cleanup_end": _history_date(row["정리매매기간_종료일"]),
        }

    tasks: list[dict[str, Any]] = []
    delisted_episode_count = 0
    no_cleanup_count = 0

    for ep in episodes.itertuples(index=False):
        if not bool(ep.source_delisted):
            continue
        delisted_episode_count += 1
        listing = pd.Timestamp(ep.listing_date).normalize()
        code = _history_short_code(ep.short_code)
        key = (code, listing)
        if key not in history:
            raise KRXHistoricalBatchOrchestratorError(
                f"delisted episode lacks exact history row: {ep.episode_key}"
            )
        row = history[key]
        episode_delist = pd.Timestamp(ep.delisting_date).normalize()
        if row["delisting_date"] != episode_delist:
            raise KRXHistoricalBatchOrchestratorError(
                f"delisting date mismatch: {ep.episode_key}"
            )

        start = row["cleanup_start"]
        end = row["cleanup_end"]
        if (start is None) != (end is None):
            raise KRXHistoricalBatchOrchestratorError(
                f"partial cleanup interval: {ep.episode_key}"
            )
        if start is None and end is None:
            no_cleanup_count += 1
            continue
        if end < start:
            raise KRXHistoricalBatchOrchestratorError(
                f"cleanup interval reversed: {ep.episode_key}"
            )
        if end > episode_delist:
            raise KRXHistoricalBatchOrchestratorError(
                f"cleanup interval extends beyond delisting: {ep.episode_key}"
            )

        standard = str(ep.standard_code).strip().upper()
        if len(standard) != 12 or not standard.isalnum():
            raise KRXHistoricalBatchOrchestratorError(
                f"invalid standard code for status economics: {ep.episode_key}"
            )
        tasks.append(
            _task(
                phase="STATUS_ECONOMICS",
                source_family="KRX_SECURITY_STATUS",
                kind="delisted_stock_price",
                params={
                    "isuCd": standard,
                    "strtDd": start.strftime("%Y%m%d"),
                    "endDd": end.strftime("%Y%m%d"),
                },
                contains_security_identifier=True,
            )
        )

    if len({row["task_id"] for row in tasks}) != len(tasks):
        raise KRXHistoricalBatchOrchestratorError(
            "duplicate status-economics task"
        )
    return tasks, {
        "delisted_episode_count": int(delisted_episode_count),
        "cleanup_price_task_count": int(len(tasks)),
        "delisted_without_cleanup_interval_count": int(no_cleanup_count),
    }


def public_task_summary(tasks: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Metadata-only summary safe for public CI logs."""
    rows = list(tasks)
    by_phase: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    for row in rows:
        phase = str(row["phase"])
        kind = str(row["request_spec"]["kind"])
        by_phase[phase] = by_phase.get(phase, 0) + 1
        by_kind[kind] = by_kind.get(kind, 0) + 1
    return {
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "task_count": len(rows),
        "task_count_by_phase": dict(sorted(by_phase.items())),
        "task_count_by_kind": dict(sorted(by_kind.items())),
        "task_set_fingerprint_sha256": _canonical_sha256(
            sorted(str(row["task_id"]) for row in rows)
        ),
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "network_request_attempted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
