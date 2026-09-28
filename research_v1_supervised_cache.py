"""Reusable PIT supervised-label cache for IndexAlert research.

The expensive daily path labelling step is deterministic for a fixed raw panel,
horizon/barriers and cost policy.  Persist both model rows and the exact economic
DecisionRecord fields so feature/model challengers can reuse the same labels
without rebuilding ~600k paths every run.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_core import DecisionRecord
from research_v1_pit_labels import make_pit_supervised

RECORD_COLUMNS = [
    "rec_entry_day", "rec_entry_price", "rec_horizon", "rec_target_return",
    "rec_stop_return", "rec_cost_return", "rec_outcome", "rec_gross_return",
    "rec_net_return", "rec_exit_day", "rec_exit_price",
]


def build_cache(
    raw: pd.DataFrame,
    cache_dir: Path,
    *,
    horizon: int = 5,
    target_return: float = 0.04,
    stop_return: float = -0.025,
    participation: float = 0.0005,
    commission_round_trip_bps: float = 3.0,
):
    frame, record_map, diagnostics = make_pit_supervised(
        raw,
        horizon=horizon,
        target_return=target_return,
        stop_return=stop_return,
        participation=participation,
        commission_round_trip_bps=commission_round_trip_bps,
    )
    rec_rows = []
    for (decision_day, symbol), rec in record_map.items():
        rec_rows.append({
            "decision_date": pd.Timestamp(decision_day),
            "symbol": str(symbol),
            "rec_entry_day": pd.Timestamp(rec.entry_day),
            "rec_entry_price": float(rec.entry_price),
            "rec_horizon": int(rec.horizon),
            "rec_target_return": float(rec.target_return),
            "rec_stop_return": float(rec.stop_return),
            "rec_cost_return": float(rec.cost_return),
            "rec_outcome": str(rec.outcome),
            "rec_gross_return": float(rec.gross_return),
            "rec_net_return": float(rec.net_return),
            "rec_exit_day": pd.Timestamp(rec.exit_day),
            "rec_exit_price": float(rec.exit_price),
        })
    rec_df = pd.DataFrame(rec_rows)
    merged = frame.merge(rec_df, on=["decision_date", "symbol"], how="left", validate="one_to_one")
    cache_dir.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(cache_dir / "supervised.parquet", index=False)
    meta = {
        "version": "pit-supervised-cache-v1",
        "horizon": int(horizon),
        "target_return": float(target_return),
        "stop_return": float(stop_return),
        "participation": float(participation),
        "commission_round_trip_bps": float(commission_round_trip_bps),
        "rows": int(len(merged)),
        "records": int(len(record_map)),
        "diagnostics": diagnostics,
    }
    (cache_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return merged, record_map, diagnostics


def load_cache(cache_dir: Path):
    p = cache_dir / "supervised.parquet"
    m = cache_dir / "meta.json"
    if not p.exists() or not m.exists():
        raise FileNotFoundError(cache_dir)
    frame = pd.read_parquet(p)
    frame["decision_date"] = pd.to_datetime(frame["decision_date"])
    record_map = {}
    rec_mask = frame["rec_outcome"].notna() if "rec_outcome" in frame.columns else pd.Series(False, index=frame.index)
    for row in frame.loc[rec_mask].itertuples(index=False):
        rec = DecisionRecord(
            decision_day=pd.Timestamp(row.decision_date).date(),
            entry_day=pd.Timestamp(row.rec_entry_day).date(),
            symbol=str(row.symbol),
            score=0.0,
            entry_price=float(row.rec_entry_price),
            horizon=int(row.rec_horizon),
            target_return=float(row.rec_target_return),
            stop_return=float(row.rec_stop_return),
            cost_return=float(row.rec_cost_return),
            outcome=str(row.rec_outcome),
            gross_return=float(row.rec_gross_return),
            net_return=float(row.rec_net_return),
            exit_day=pd.Timestamp(row.rec_exit_day).date(),
            exit_price=float(row.rec_exit_price),
        )
        record_map[(rec.decision_day, rec.symbol)] = rec
    meta = json.loads(m.read_text(encoding="utf-8"))
    return frame, record_map, meta.get("diagnostics", {}), meta


def load_or_build(raw: pd.DataFrame, cache_dir: Path, **kwargs):
    try:
        return load_cache(cache_dir)
    except FileNotFoundError:
        frame, record_map, diag = build_cache(raw, cache_dir, **kwargs)
        meta = json.loads((cache_dir / "meta.json").read_text(encoding="utf-8"))
        return frame, record_map, diag, meta
