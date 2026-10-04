"""PIT-safe affected-position scope builder for KRX status economics.

Pure/offline. Joins strategy position intervals to already-normalized official
status events. It does not infer fills, recovery values, or downstream authority.
"""
from __future__ import annotations

import hashlib
import math
from typing import Iterable

import pandas as pd


class KRXAffectedPositionScopeError(ValueError):
    pass


def _require(df: pd.DataFrame, cols: Iterable[str], label: str) -> None:
    missing = sorted(set(cols) - set(df.columns))
    if missing:
        raise KRXAffectedPositionScopeError(f"{label} missing required columns: {missing}")


def _aware(value, field: str) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if pd.isna(ts) or ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXAffectedPositionScopeError(f"{field} must be timezone-aware")
    return ts


def _day(value, field: str) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        raise KRXAffectedPositionScopeError(f"{field} is invalid")
    return ts.tz_localize(None).normalize() if ts.tzinfo else ts.normalize()


def _symbol(value) -> str:
    s = str(value).strip().upper()
    if not s:
        raise KRXAffectedPositionScopeError("symbol is empty")
    return s.zfill(6) if s.isdigit() else s


def build_affected_position_scope(*, positions: pd.DataFrame, status_events: pd.DataFrame, source_contract_fingerprint: str) -> pd.DataFrame:
    _require(positions, ["position_id","symbol","entry_day","exit_day","affected_qty","entry_cost_basis_total"], "positions")
    _require(status_events, ["symbol","event_type","event_start","event_end","available_at"], "status_events")
    fp = str(source_contract_fingerprint).strip().lower()
    if len(fp) != 64 or any(c not in "0123456789abcdef" for c in fp):
        raise KRXAffectedPositionScopeError("source contract fingerprint must be SHA-256")
    pos = {}
    for row in positions.itertuples(index=False):
        pid = str(row.position_id).strip()
        if not pid or pid in pos:
            raise KRXAffectedPositionScopeError("position_id must be non-empty and unique")
        entry = _day(row.entry_day, f"position[{pid}].entry_day")
        exit_ = _day(row.exit_day, f"position[{pid}].exit_day")
        if exit_ < entry:
            raise KRXAffectedPositionScopeError("position exit precedes entry")
        qty = float(row.affected_qty)
        basis = float(row.entry_cost_basis_total)
        if not math.isfinite(qty) or not math.isfinite(basis) or qty <= 0 or basis <= 0:
            raise KRXAffectedPositionScopeError("position quantity and cost basis must be finite and positive")
        pos[pid] = {"position_id":pid,"symbol":_symbol(row.symbol),"entry_day":entry,"exit_day":exit_,"affected_qty":qty,"entry_cost_basis_total":basis}
    rows=[]; seen=set(); allowed={"HALT","CLEANUP_TRADING","DELISTING"}
    for event in status_events.itertuples(index=False):
        symbol=_symbol(event.symbol); kind=str(event.event_type).strip().upper()
        if kind not in allowed: raise KRXAffectedPositionScopeError(f"unsupported event_type: {kind}")
        start=_day(event.event_start,"event_start"); end=_day(event.event_end,"event_end")
        if end < start: raise KRXAffectedPositionScopeError("event end precedes start")
        available=_aware(event.available_at,"available_at")
        for p in pos.values():
            if p["symbol"] != symbol: continue
            if p["entry_day"] <= end and p["exit_day"] >= start:
                key=(p["position_id"],kind,start.date().isoformat(),end.date().isoformat())
                if key in seen: raise KRXAffectedPositionScopeError("duplicate affected-position event")
                seen.add(key)
                rows.append({"position_id":p["position_id"],"symbol":symbol,"event_type":kind,"affected_qty":p["affected_qty"],"entry_cost_basis_total":p["entry_cost_basis_total"],"event_start":start,"event_end":end,"event_available_at":available,"source_contract_fingerprint":fp})
    columns=["position_id","symbol","event_type","affected_qty","entry_cost_basis_total","event_start","event_end","event_available_at","source_contract_fingerprint"]
    return pd.DataFrame(rows,columns=columns).sort_values(["position_id","event_start","event_end","event_type"]).reset_index(drop=True)


def public_affected_scope_summary(scope: pd.DataFrame) -> dict:
    _require(scope,["position_id","event_type","source_contract_fingerprint"],"affected scope")
    event_keys=sorted(f"{r.position_id}|{r.event_type}|{pd.Timestamp(r.event_start).date().isoformat()}|{pd.Timestamp(r.event_end).date().isoformat()}" for r in scope.itertuples(index=False))
    digest=hashlib.sha256("\n".join(event_keys).encode("utf-8")).hexdigest()
    return {"affected_position_event_count":int(len(scope)),"distinct_affected_positions":int(scope["position_id"].nunique()),"event_type_counts":{str(k):int(v) for k,v in scope["event_type"].value_counts().sort_index().items()},"position_scope_fingerprint_sha256":digest,"security_identifiers_emitted":False,"exact_status_economics_ready":False,"sealed_holdout_authorized":False,"shadow_s1_authorized":False,"fresh_confirmation_s2_authorized":False,"live_trading_authorized":False}
