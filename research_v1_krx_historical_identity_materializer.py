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
    build_per_security_history_tasks,
    build_status_economics_tasks,
    public_task_summary,
)
from research_v1_krx_historical_batch_state import require_phase_complete
from research_v1_krx_historical_fetchers import (
    parse_data_marketplace_raw,
    parse_openapi_raw,
)
from research_v1_krx_historical_identity import (
    _short_code,
    identity_summary,
    listing_dates_for_standard_code_binding,
    reconstruct_historical_kospi_episodes,
)
from research_v1_krx_official_status import normalise_basic_info
from research_v1_krx_private_store import read_private_json, read_raw_object


SEED_BATCH_REL = "batches/identity-seed-v3.json"
BINDING_BATCH_REL = "batches/identity-standard-code-binding-v3.json"

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


def load_identity_binding_master_snapshots(
    root: str,
    *,
    git_worktree: str | None = None,
) -> pd.DataFrame:
    """Load exact listing-date security-master snapshots from private binding batch."""
    require_phase_complete(
        root=root,
        phase="IDENTITY_STANDARD_CODE_BINDING",
        git_worktree=git_worktree,
    )
    tasks = build_identity_binding_tasks_from_private_seed(
        root,
        git_worktree=git_worktree,
    )
    summary = public_task_summary(tasks)
    batch = read_private_json(
        root,
        BINDING_BATCH_REL,
        git_worktree=git_worktree,
    )["value"]

    _require(batch.get("plan_id") == PLAN_ID, "identity-binding batch plan drift")
    _require(
        batch.get("execution_contract_id") == EXECUTION_CONTRACT_ID,
        "identity-binding batch execution contract drift",
    )
    _require(
        batch.get("phase") == "IDENTITY_STANDARD_CODE_BINDING",
        "identity-binding phase drift",
    )
    _require(
        int(batch.get("task_count", -1)) == len(tasks),
        "identity-binding task count drift",
    )
    _require(
        int(batch.get("completed_task_count", -1)) == len(tasks),
        "identity-binding completion count drift",
    )
    _require(
        batch.get("task_set_fingerprint_sha256")
        == summary["task_set_fingerprint_sha256"],
        "identity-binding task-set fingerprint drift",
    )

    completed = list(batch.get("tasks") or [])
    _require(
        len(completed) == len(tasks),
        "identity-binding completion rows missing",
    )
    by_id = {}
    for row in completed:
        tid = str(row.get("task_id") or "")
        _require(tid and tid not in by_id, "duplicate/missing identity-binding task_id")
        by_id[tid] = dict(row)
    _require(
        set(by_id) == {str(row["task_id"]) for row in tasks},
        "identity-binding completion set does not match frozen task set",
    )

    masters: list[pd.DataFrame] = []
    for task in tasks:
        completion = by_id[str(task["task_id"])]
        raw = read_raw_object(
            root,
            str(completion["raw_object_sha256"]),
            expected_size=int(completion["raw_bytes_size"]),
            git_worktree=git_worktree,
        )
        frame = parse_openapi_raw(raw)
        _require(
            len(frame) == int(completion["response_rows"]),
            "identity-binding parsed row count differs from recorded receipt",
        )
        retrieved_at = _timestamp(completion.get("retrieved_at"), "retrieved_at")
        bas_dd = str(task["request_spec"]["params"]["basDd"])
        masters.append(
            normalise_basic_info(
                frame,
                asof_date=pd.Timestamp(bas_dd),
                available_at=retrieved_at,
            )
        )

    _require(masters, "identity-binding master snapshots are empty")
    return pd.concat(masters, ignore_index=True)


def _dedupe_master_source_fail_closed(
    frame: pd.DataFrame,
    *,
    label: str,
    key_cols: list[str],
    compare_cols: list[str],
) -> pd.DataFrame:
    """Collapse only identity-equivalent duplicate rows inside one source."""
    if frame.empty:
        return frame.copy()

    keep_indices: list[int] = []
    for _, group in frame.groupby(key_cols, sort=False, dropna=False):
        first_idx = int(group.index[0])
        first = group.iloc[0]
        for pos in range(1, len(group)):
            other = group.iloc[pos]
            for col in compare_cols:
                lv = first[col]
                rv = other[col]
                if pd.isna(lv) and pd.isna(rv):
                    continue
                if col == "common_stock_identity_official":
                    same = bool(lv) == bool(rv)
                elif col == "listing_date_official":
                    same = pd.Timestamp(lv) == pd.Timestamp(rv)
                else:
                    same = str(lv) == str(rv)
                _require(
                    same,
                    f"{label} duplicate identity conflict: {col}",
                )
        keep_indices.append(first_idx)
    return frame.loc[keep_indices].copy().reset_index(drop=True)


def _merge_master_snapshots_fail_closed(
    seed_master: pd.DataFrame,
    binding_master: pd.DataFrame,
) -> pd.DataFrame:
    """Merge seed/binding snapshots without weakening duplicate checks.

    The seed already contains frozen start/end snapshots. If a listing-date
    binding request lands on the same decision date, the same symbol may appear
    once in each source. That overlap is allowed only when the identity fields
    agree exactly; otherwise the merge fails closed. Duplicate keys inside one
    source remain an error.
    """
    key_cols = ["decision_date", "symbol"]
    identity_cols = [
        "standard_code",
        "listing_date_official",
        "market_type_official",
        "common_stock_identity_official",
    ]
    optional_identity_cols = ["security_group_official", "stock_type_official"]

    seed = seed_master.copy()
    binding = binding_master.copy()
    for label, frame in (("seed", seed), ("binding", binding)):
        missing = set(key_cols + identity_cols) - set(frame.columns)
        _require(not missing, f"{label} master missing merge columns: {sorted(missing)}")

    seed["decision_date"] = pd.to_datetime(
        seed["decision_date"], errors="coerce"
    ).dt.normalize()
    binding["decision_date"] = pd.to_datetime(
        binding["decision_date"], errors="coerce"
    ).dt.normalize()
    seed["listing_date_official"] = pd.to_datetime(
        seed["listing_date_official"], errors="coerce"
    ).dt.normalize()
    binding["listing_date_official"] = pd.to_datetime(
        binding["listing_date_official"], errors="coerce"
    ).dt.normalize()
    # Use the exact same short-code canonicalization as the core identity
    # validator before duplicate/overlap checks. This prevents representation
    # differences such as 5930 vs 005930 from surviving until the core layer.
    seed["symbol"] = _short_code(seed["symbol"])
    binding["symbol"] = _short_code(binding["symbol"])
    seed["standard_code"] = seed["standard_code"].astype("string").str.strip().str.upper()
    binding["standard_code"] = binding["standard_code"].astype("string").str.strip().str.upper()
    _require(
        not seed[["decision_date", "listing_date_official"]].isna().any().any(),
        "seed master has invalid merge date",
    )
    _require(
        not binding[["decision_date", "listing_date_official"]].isna().any().any(),
        "binding master has invalid merge date",
    )
    compare_cols = identity_cols + [
        col
        for col in optional_identity_cols
        if col in seed.columns and col in binding.columns
    ]
    seed = _dedupe_master_source_fail_closed(
        seed,
        label="seed",
        key_cols=key_cols,
        compare_cols=compare_cols,
    )
    binding = _dedupe_master_source_fail_closed(
        binding,
        label="binding",
        key_cols=key_cols,
        compare_cols=compare_cols,
    )

    seed_indexed = seed.set_index(key_cols, drop=False)
    binding_indexed = binding.set_index(key_cols, drop=False)
    overlap = seed_indexed.index.intersection(binding_indexed.index)
    for key in overlap:
        left = seed_indexed.loc[key]
        right = binding_indexed.loc[key]
        # Duplicate keys in either input are rejected above, so loc must be a row.
        for col in compare_cols:
            lv = left[col]
            rv = right[col]
            if pd.isna(lv) and pd.isna(rv):
                continue
            if col == "common_stock_identity_official":
                same = bool(lv) == bool(rv)
            elif col == "listing_date_official":
                same = pd.Timestamp(lv) == pd.Timestamp(rv)
            else:
                same = str(lv) == str(rv)
            _require(
                same,
                f"seed/binding security-master overlap conflict: {col}",
            )

    overlap_set = set(overlap.tolist())
    keep_binding = [
        (row.decision_date, row.symbol) not in overlap_set
        for row in binding.itertuples(index=False)
    ]
    merged = pd.concat(
        [seed, binding.loc[keep_binding].copy()],
        ignore_index=True,
        sort=False,
    )
    _require(
        not merged.duplicated(key_cols).any(),
        "duplicate symbol after seed/binding security-master reconciliation",
    )
    return merged


def reconstruct_private_historical_episodes(
    root: str,
    *,
    git_worktree: str | None = None,
) -> pd.DataFrame:
    """Reconstruct stable historical KOSPI common-stock episodes from private evidence."""
    seed = load_identity_seed_material(root, git_worktree=git_worktree)
    binding = load_identity_binding_master_snapshots(
        root,
        git_worktree=git_worktree,
    )
    masters = _merge_master_snapshots_fail_closed(
        seed["security_master_snapshots"],
        binding,
    )
    return reconstruct_historical_kospi_episodes(
        security_master_snapshots=masters,
        new_listing=seed["new_listing_history"],
        delisted=seed["delisted_history"],
    )


def build_per_security_history_tasks_from_private_identity(
    root: str,
    *,
    git_worktree: str | None = None,
) -> list[dict[str, Any]]:
    """Build the exact private halt/investor request queue from reconstructed episodes."""
    episodes = reconstruct_private_historical_episodes(
        root,
        git_worktree=git_worktree,
    )
    tasks = build_per_security_history_tasks(episodes)
    _require(tasks, "per-security history task set is empty")
    return tasks


def public_historical_identity_summary(
    root: str,
    *,
    git_worktree: str | None = None,
) -> dict[str, Any]:
    """Return counts/fingerprints only after exact identity reconstruction."""
    episodes = reconstruct_private_historical_episodes(
        root,
        git_worktree=git_worktree,
    )
    tasks = build_per_security_history_tasks(episodes)
    ids = identity_summary(episodes)
    req = public_task_summary(tasks)
    return {
        **ids,
        "per_security_request_count": int(req["task_count"]),
        "per_security_task_set_fingerprint_sha256": req[
            "task_set_fingerprint_sha256"
        ],
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "network_request_attempted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def build_status_economics_tasks_from_private_identity(
    root: str,
    *,
    git_worktree: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Build exact cleanup-price tasks from private delisting evidence.

    No network access is performed. Episodes without an official cleanup
    interval intentionally generate no MDCSTAT23902 request and remain
    dependent on separate exact fill/recovery evidence.
    """
    seed = load_identity_seed_material(root, git_worktree=git_worktree)
    episodes = reconstruct_private_historical_episodes(
        root,
        git_worktree=git_worktree,
    )
    tasks, summary = build_status_economics_tasks(
        episodes,
        seed["delisted_history"],
    )
    return tasks, summary


def public_status_economics_task_summary(
    root: str,
    *,
    git_worktree: str | None = None,
) -> dict[str, Any]:
    tasks, event_summary = build_status_economics_tasks_from_private_identity(
        root,
        git_worktree=git_worktree,
    )
    task_summary = public_task_summary(tasks)
    return {
        **event_summary,
        "task_count": int(task_summary["task_count"]),
        "task_set_fingerprint_sha256": task_summary[
            "task_set_fingerprint_sha256"
        ],
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "network_request_attempted": False,
        "exact_status_economics_ready": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
