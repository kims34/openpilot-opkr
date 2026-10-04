"""Offline adapters for KRX affected-position scope.

Converts existing DecisionRecord outputs and normalized KRX status frames into
the strict schemas consumed by research_v1_krx_affected_position_scope.
No network access, economics inference, holdout access, or authority changes.
"""
from __future__ import annotations
import hashlib, math
from typing import Sequence
import pandas as pd
from research_v1_core import DecisionRecord

def decision_records_to_position_intervals(records: Sequence[DecisionRecord], *, notional_per_position: float = 1.0) -> pd.DataFrame:
    n=float(notional_per_position)
    if not math.isfinite(n) or n <= 0: raise ValueError("notional_per_position must be finite and positive")
    rows=[]
    for i,r in enumerate(records):
        ep=float(r.entry_price)
        if not math.isfinite(ep) or ep <= 0: raise ValueError("entry_price must be finite and positive")
        pid_raw=f"{r.decision_day.isoformat()}|{r.entry_day.isoformat()}|{str(r.symbol).strip().upper()}|{i}"
        pid=hashlib.sha256(pid_raw.encode("utf-8")).hexdigest()
        rows.append({"position_id":pid,"symbol":str(r.symbol).strip().upper().zfill(6),"entry_day":r.entry_day,"exit_day":r.exit_day,"affected_qty":n/ep,"entry_cost_basis_total":n})
    return pd.DataFrame(rows,columns=["position_id","symbol","entry_day","exit_day","affected_qty","entry_cost_basis_total"])

def normalized_status_frames_to_events(*, halts: pd.DataFrame, cleanup: pd.DataFrame, delistings: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for r in halts.itertuples(index=False):
        start=pd.Timestamp(r.halt_date).normalize()
        if pd.isna(r.resume_date):
            raise ValueError("open-ended HALT requires independently attested end/resume information")
        end=pd.Timestamp(r.resume_date).normalize()-pd.Timedelta(days=1)
        if end < start:
            raise ValueError("HALT resume_date must be after halt_date")
        rows.append({"symbol":r.symbol,"event_type":"HALT","event_start":start,"event_end":end,"available_at":r.available_at})
    for r in cleanup.itertuples(index=False):
        rows.append({"symbol":r.symbol,"event_type":"CLEANUP_TRADING","event_start":r.cleanup_start,"event_end":r.cleanup_end,"available_at":r.available_at})
    for r in delistings.itertuples(index=False):
        rows.append({"symbol":r.symbol,"event_type":"DELISTING","event_start":r.delisting_date,"event_end":r.delisting_date,"available_at":r.available_at})
    return pd.DataFrame(rows,columns=["symbol","event_type","event_start","event_end","available_at"])
