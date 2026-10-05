"""Offline adapter from regenerated development positions to affected-scope schema.

Normalized notional=1.0 is used only for overlap/scope matching. It is not
realized economics, broker fill evidence, or a profitability claim.
"""
from __future__ import annotations
import hashlib, math
import pandas as pd

REQ={"decision_date","entry_day","exit_day","symbol","entry_price"}

def regenerated_positions_to_scope(frame: pd.DataFrame, *, notional_per_position: float=1.0) -> pd.DataFrame:
    missing=sorted(REQ-set(frame.columns))
    if missing: raise ValueError(f"missing columns: {missing}")
    n=float(notional_per_position)
    if not math.isfinite(n) or n<=0: raise ValueError("notional_per_position must be finite and positive")
    rows=[]
    for i,r in enumerate(frame.itertuples(index=False)):
        ep=float(r.entry_price)
        if not math.isfinite(ep) or ep<=0: raise ValueError("entry_price must be finite and positive")
        entry=pd.Timestamp(r.entry_day).normalize(); exit_=pd.Timestamp(r.exit_day).normalize()
        if exit_ < entry: raise ValueError("exit_day before entry_day")
        sym=str(r.symbol).strip().upper().zfill(6)
        raw=f"{pd.Timestamp(r.decision_date).date().isoformat()}|{entry.date().isoformat()}|{exit_.date().isoformat()}|{sym}|{i}"
        rows.append({"position_id":hashlib.sha256(raw.encode()).hexdigest(),"symbol":sym,"entry_day":entry,"exit_day":exit_,"affected_qty":n/ep,"entry_cost_basis_total":n})
    return pd.DataFrame(rows,columns=["position_id","symbol","entry_day","exit_day","affected_qty","entry_cost_basis_total"])

def aggregate_summary(scope: pd.DataFrame) -> dict:
    canonical=scope.sort_values(["entry_day","exit_day","position_id"])[["position_id","entry_day","exit_day","affected_qty","entry_cost_basis_total"]].to_csv(index=False).encode()
    return {"rows":int(len(scope)),"entry_days":int(scope.entry_day.nunique()) if len(scope) else 0,"exit_days":int(scope.exit_day.nunique()) if len(scope) else 0,"scope_fingerprint_sha256":hashlib.sha256(canonical).hexdigest(),"normalized_notional_only":True,"realized_economics_proven":False,"network_request_attempted":False,"security_identifiers_emitted":False,"sealed_holdout_authorized":False,"live_trading_authorized":False}
