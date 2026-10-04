"""Offline reconstruction of normalized KRX status events from private store.

Reads only already-acquired raw objects and frozen task/completion metadata.
No network calls. Output is private and may contain identifiers; callers must
use the aggregate scope runner before emitting public evidence.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from research_v1_krx_historical_fetchers import parse_data_marketplace_raw
from research_v1_krx_private_store import read_private_json, read_raw_object


class KRXPrivateStatusMaterializerError(ValueError):
    pass


def _first(frame: pd.DataFrame, names: tuple[str, ...]):
    for name in names:
        if name in frame.columns:
            return name
    raise KRXPrivateStatusMaterializerError(f"missing expected column family: {names}")


def _yyyymmdd(series: pd.Series) -> pd.Series:
    return pd.to_datetime(
        series.astype("string").str.replace(r"[^0-9]", "", regex=True),
        format="%Y%m%d", errors="coerce",
    ).dt.normalize()


def materialize_private_status_events(
    root: str,
    *,
    git_worktree: str | None = None,
) -> pd.DataFrame:
    state = read_private_json(
        root, "batch_state/PER_SECURITY_HISTORY.json", git_worktree=git_worktree
    )["value"]
    if state.get("status") != "COMPLETE" or state.get("phase_complete") is not True:
        raise KRXPrivateStatusMaterializerError("PER_SECURITY_HISTORY is not complete")

    # Task manifest is private because it contains request identifiers/params.
    manifest = read_private_json(
        root, "task_manifests/per-security-history-v3.json", git_worktree=git_worktree
    )["value"]
    tasks = manifest.get("tasks") if isinstance(manifest, dict) else None
    if not isinstance(tasks, list):
        raise KRXPrivateStatusMaterializerError("private task manifest has no task list")
    by_id = {str(t.get("task_id")): t for t in tasks}
    rows: list[dict[str, Any]] = []

    for tid, completion in dict(state.get("completed") or {}).items():
        task = by_id.get(str(tid))
        if not task or task.get("kind") != "trading_halt":
            continue
        raw = read_raw_object(
            root, completion["raw_object_sha256"],
            expected_size=int(completion["raw_bytes_size"]),
            git_worktree=git_worktree,
        )
        # trading_halt is a pinned Data Marketplace endpoint. The manifest
        # records the method used by the frozen request specification.
        method = str(task.get("method") or task.get("request", {}).get("method") or "csv")
        frame = parse_data_marketplace_raw(method, raw)
        if frame.empty:
            continue
        symbol = str(
            task.get("symbol") or task.get("short_code")
            or task.get("params", {}).get("isuCd2") or ""
        ).strip().upper()
        if not symbol:
            raise KRXPrivateStatusMaterializerError("halt task has no private short code")
        start_col = _first(frame, ("거래정지일", "정지일", "HALT_DD", "trading_halt_date"))
        end_col = next((c for c in ("거래재개일", "재개일", "RESUME_DD", "resume_date") if c in frame.columns), None)
        starts = _yyyymmdd(frame[start_col])
        ends = _yyyymmdd(frame[end_col]) if end_col else pd.Series(pd.NaT, index=frame.index)
        for start, resume in zip(starts, ends):
            if pd.isna(start):
                continue
            end = start if pd.isna(resume) else resume - pd.Timedelta(days=1)
            rows.append({
                "symbol": symbol.zfill(6) if symbol.isdigit() else symbol,
                "event_type": "HALT",
                "event_start": start,
                "event_end": end,
                # Retrieval timestamp is intentionally not invented here.
                # PIT availability must be joined from the acquisition receipt
                # before this private frame can be attested for strategy use.
                "available_at": pd.NaT,
            })

    return pd.DataFrame(rows, columns=[
        "symbol","event_type","event_start","event_end","available_at"
    ])
