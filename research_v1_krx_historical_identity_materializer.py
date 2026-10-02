"""Private offline materializer for the KRX historical identity seed.

This module performs no network access. It consumes the completed private
IDENTITY_SEED batch, re-parses verified raw objects, normalizes the two security
master snapshots, and derives the exact listing-date master request set required
for stable historical standard-code binding.

Returned DataFrames contain private KRX rows and identifiers and therefore must
never be printed, committed, or emitted to public Actions artifacts.
"""
from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from research_v1_krx_historical_batch_orchestrator import (
    EXECUTION_CONTRACT_ID,
    PLAN_ID,
    build_identity_seed_tasks,
    build_listing_date_master_tasks,
    public_task_summary,
)
from research_v1_krx_historical_batch_state import require_phase_complete
from research_v1_krx_historical_fetchers import (
    parse_data_marketplace_raw,
    parse_openapi_raw,
)
from research_v1_krx_historical_identity import (
    listing_dates_for_standard_code_binding,
)
from research_v1_krx_official_status import normalise_basic_info
from research_v1_krx_private_store import read_private_json, read_raw_object


SEED_BATCH_REL = "batches/identity-seed-v3.json"

KIND_META = {
    "security_master": {
        "parser": "openapi",
    },
    "new_listing": {
        "parser": "csv",
    },
    "delisted": {
        "parser": "csv",
    },
    "cleanup_current_reconciliation": {
        "parser": "json",
    },
}


class KRXHistoricalIdentityMaterializerError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXHistoricalIdentityMaterializerError(msg)


def _timestamp(value: Any, field: str) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if pd.isna(ts) or ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXHistoricalIdentityMaterializerError(
            f"{field} must be timezone-aware"
        )
    return ts


def _load_seed_batch(
    root: str,
    *,
    git_worktree: str | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require_phase_complete(
        root=root,
        phase="IDENTITY_SEED",
        git_worktree=git_worktree,
    )
    batch = read_private_json(
        root,
        SEED_BATCH_REL,
        git_worktree=git_worktree,
    )["value"]

    _require(batch.get("plan_id") == PLAN_ID, "identity-seed batch plan drift")
    _require(
        batch.get("execution_contract_id") == EXECUTION_CONTRACT_ID,
        "identity-seed batch execution contract drift",
    )
    _require(batch.get("phase") == "IDENTITY_SEED", "identity-seed phase drift")
    _require(int(batch.get("task_count", -1)) == 27, "identity-seed task count drift")
    _require(
        int(batch.get("completed_task_count", -1)) == 27,
        "identity-seed completion count drift",
    )

    expected = build_identity_seed_tasks()
    expected_summary = public_task_summary(expected)
    _require(
        batch.get("task_set_fingerprint_sha256")
        == expected_summary["task_set_fingerprint_sha256"],
        "identity-seed task-set fingerprint drift",
    )

    completed = list(batch.get("tasks") or [])
    _require(len(completed) == 27, "identity-seed completion rows missing")
    by_id = {}
    for row in completed:
        tid = str(row.get("task_id") or "")
        _require(tid and tid not in by_id, "duplicate/missing identity-seed task_id")
        by_id[tid] = dict(row)
    _require(
        set(by_id) == {str(row["task_id"]) for row in expected},
        "identity-seed completion set does not match frozen task set",
    )
    return batch, expected


def _parse_raw(kind: str, raw: bytes) -> pd.DataFrame:
    if kind not in KIND_META:
        raise KRXHistoricalIdentityMaterializerError(
            f"unsupported identity-seed kind: {kind}"
        )
    parser = KIND_META[kind]["parser"]
    if parser == "openapi":
        return parse_openapi_raw(raw)
    return parse_data_marketplace_raw(parser, raw)


def load_identity_seed_material(
    root: str,
    *,
    git_worktree: str | None = None,
) -> dict[str, pd.DataFrame]:
    """Load completed private seed material without network access."""
    batch, expected = _load_seed_batch(root, git_worktree=git_worktree)
    by_id = {str(row["task_id"]): dict(row) for row in batch["tasks"]}

    masters: list[pd.DataFrame] = []
    new_rows: list[pd.DataFrame] = []
    delisted_rows: list[pd.DataFrame] = []
    cleanup_rows: list[pd.DataFrame] = []

    for task in expected:
        completion = by_id[str(task["task_id"])]
        raw = read_raw_object(
            root,
            str(completion["raw_object_sha256"]),
            expected_size=int(completion["raw_bytes_size"]),
            git_worktree=git_worktree,
        )
        kind = str(task["request_spec"]["kind"])
        frame = _parse_raw(kind, raw)
        _require(
            len(frame) == int(completion["response_rows"]),
            f"{kind} parsed row count differs from recorded receipt",
        )
        retrieved_at = _timestamp(completion.get("retrieved_at"), "retrieved_at")

        if kind == "security_master":
            bas_dd = str(task["request_spec"]["params"]["basDd"])
            masters.append(
                normalise_basic_info(
                    frame,
                    asof_date=pd.Timestamp(bas_dd),
                    available_at=retrieved_at,
                )
            )
        elif kind == "new_listing":
            new_rows.append(frame.copy())
        elif kind == "delisted":
            delisted_rows.append(frame.copy())
        elif kind == "cleanup_current_reconciliation":
            cleanup_rows.append(frame.copy())
        else:  # pragma: no cover - guarded by KIND_META
            raise KRXHistoricalIdentityMaterializerError(
                f"unsupported identity-seed kind: {kind}"
            )

    _require(len(masters) == 2, "expected exactly two fixed security-master snapshots")
    _require(len(new_rows) == 12, "expected twelve new-listing windows")
    _require(len(delisted_rows) == 12, "expected twelve delisted-history windows")
    _require(len(cleanup_rows) == 1, "expected one cleanup reconciliation snapshot")

    return {
        "security_master_snapshots": pd.concat(masters, ignore_index=True),
        "new_listing_history": pd.concat(new_rows, ignore_index=True, sort=False),
        "delisted_history": pd.concat(delisted_rows, ignore_index=True, sort=False),
        "cleanup_current": cleanup_rows[0].reset_index(drop=True),
    }


def build_identity_binding_tasks_from_private_seed(
    root: str,
    *,
    git_worktree: str | None = None,
) -> list[dict[str, Any]]:
    """Derive one exact security-master request per historical listing date."""
    material = load_identity_seed_material(root, git_worktree=git_worktree)
    dates = listing_dates_for_standard_code_binding(
        material["new_listing_history"]
    )
    tasks = build_listing_date_master_tasks(dates)
    _require(tasks, "identity binding task set is empty")
    _require(len(tasks) == len(dates), "identity binding task count drift")
    return tasks


def public_identity_seed_material_summary(
    root: str,
    *,
    git_worktree: str | None = None,
) -> dict[str, Any]:
    """Return only counts and task fingerprints; never identifiers/raw rows."""
    material = load_identity_seed_material(root, git_worktree=git_worktree)
    dates = listing_dates_for_standard_code_binding(
        material["new_listing_history"]
    )
    tasks = build_listing_date_master_tasks(dates)
    summary = public_task_summary(tasks)
    return {
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "seed_security_master_rows": int(len(material["security_master_snapshots"])),
        "seed_new_listing_rows": int(len(material["new_listing_history"])),
        "seed_delisted_rows": int(len(material["delisted_history"])),
        "seed_cleanup_current_rows": int(len(material["cleanup_current"])),
        "listing_date_master_request_count": int(len(tasks)),
        "listing_date_task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "identifiers_emitted": False,
        "raw_rows_emitted": False,
        "network_request_attempted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
