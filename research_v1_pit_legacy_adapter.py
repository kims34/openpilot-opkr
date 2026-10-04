"""Offline adapter from the rebuilt PIT panel to the legacy clean-v2/v3 schema.

This does not change model policy, access sealed data, or perform network I/O.
It exists only to make the data contract explicit instead of silently pointing
legacy research code at a differently named/differently shaped dataset.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

REQUIRED = {
    "decision_date","symbol","name","market","open","high","low","close",
    "value","krx_change_return","bar_valid_for_execution",
}

def load_legacy_compatible_pit(pit_dir: str, from_date: str, to_date: str) -> pd.DataFrame:
    start=pd.Timestamp(from_date).normalize(); end=pd.Timestamp(to_date).normalize()
    if end < start: raise ValueError("end before start")
    frames=[]
    for year in range(start.year,end.year+1):
        path=Path(pit_dir)/f"kospi-pit-{year}.parquet"
        if not path.exists(): raise FileNotFoundError(path)
        x=pd.read_parquet(path)
        missing=sorted(REQUIRED-set(x.columns))
        if missing: raise ValueError(f"{path.name} missing PIT columns: {missing}")
        frames.append(x)
    x=pd.concat(frames,ignore_index=True)
    x["decision_date"]=pd.to_datetime(x["decision_date"],errors="coerce")
    x=x[(x["decision_date"]>=start)&(x["decision_date"]<=end)].copy()
    if x.empty: raise ValueError("PIT range is empty")
    if not x["bar_valid_for_execution"].fillna(False).astype(bool).all():
        raise ValueError("execution panel unexpectedly contains invalid bars")
    # Preserve the old clean-v2 field meanings exactly. krx_change_return is
    # already decimal return, whereas legacy official_pct was percentage points.
    out=pd.DataFrame({
        "Date":x["decision_date"],
        "Code":x["symbol"].astype(str).str.zfill(6),
        "Name":x["name"].astype(str),
        "Market":x["market"].astype(str),
        "Open":pd.to_numeric(x["open"],errors="coerce"),
        "High":pd.to_numeric(x["high"],errors="coerce"),
        "Low":pd.to_numeric(x["low"],errors="coerce"),
        "Close":pd.to_numeric(x["close"],errors="coerce"),
        "Amount":pd.to_numeric(x["value"],errors="coerce"),
        "ChangesRatio":pd.to_numeric(x["krx_change_return"],errors="coerce")*100.0,
    })
    if out[["Date","Open","High","Low","Close","Amount","ChangesRatio"]].isna().any().any():
        raise ValueError("PIT-to-legacy conversion produced missing required values")
    return out.sort_values(["Code","Date"]).reset_index(drop=True)

def audit_summary(df: pd.DataFrame) -> dict:
    return {
        "rows":int(len(df)),
        "dates":int(df["Date"].nunique()),
        "symbols":int(df["Code"].nunique()),
        "from_date":str(pd.Timestamp(df["Date"].min()).date()),
        "to_date":str(pd.Timestamp(df["Date"].max()).date()),
        "network_request_attempted":False,
        "security_identifiers_emitted":False,
        "sealed_holdout_authorized":False,
        "live_trading_authorized":False,
    }
