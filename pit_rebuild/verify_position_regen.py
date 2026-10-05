"""Aggregate-only verifier for private abstention-v3 position artifact."""
import json, hashlib
from pathlib import Path
import pandas as pd

P=Path("/pit/private/abstention_v3_positions.parquet")
df=pd.read_parquet(P)
required={"fold","horizon","coverage","decision_idx","decision_date","entry_day","exit_day","symbol","rank","score","gross_return","entry_price"}
missing=required-set(df.columns)
if missing: raise ValueError(f"position artifact missing columns: {sorted(missing)}")
if df.empty: raise ValueError("position artifact is empty")
if df[list(required)].isna().any().any(): raise ValueError("position artifact contains null required values")
if (pd.to_datetime(df.entry_day)<=pd.to_datetime(df.decision_date)).any(): raise ValueError("entry_day must be after decision_date")
if (pd.to_datetime(df.exit_day)<pd.to_datetime(df.entry_day)).any(): raise ValueError("exit_day must not precede entry_day")
if (pd.to_numeric(df.entry_price,errors="coerce")<=0).any(): raise ValueError("entry_price must be positive")
if df.duplicated(["horizon","coverage","decision_idx","rank"]).any(): raise ValueError("duplicate selection rank within decision bucket")
rank_ok=df.groupby(["horizon","coverage","decision_idx"])["rank"].apply(lambda x: sorted(x.astype(int).tolist())==list(range(1,len(x)+1)))
if not rank_ok.all(): raise ValueError("selection ranks are not contiguous from 1")
if (df.groupby(["horizon","coverage","decision_idx"]).size()>3).any(): raise ValueError("selection bucket exceeds TOP_K=3")
counts={}
for h,g in df.groupby("horizon"):
    counts[str(int(h))]={}
    for cov,cg in g.groupby("coverage"):
        counts[str(int(h))][f"top_{int(round(float(cov)*100))}pct_train_threshold"]=int(len(cg))
sort_cols=["horizon","coverage","decision_idx","rank","symbol"]
selection_cols=["fold","horizon","coverage","decision_idx","decision_date","symbol","rank","score","gross_return"]
selection_canonical=df.sort_values(sort_cols)[selection_cols].to_csv(index=False).encode()
position_canonical=df.sort_values(sort_cols).to_csv(index=False).encode()
print("POSITION_VERIFY="+json.dumps({
 "rows":int(len(df)),"decision_dates":int(df.decision_date.nunique()),
 "counts":counts,"selection_fingerprint_sha256":hashlib.sha256(selection_canonical).hexdigest(),
 "position_fingerprint_sha256":hashlib.sha256(position_canonical).hexdigest(),
 "network_request_attempted":False,"security_identifiers_emitted":False,
 "sealed_holdout_authorized":False,"live_trading_authorized":False
},sort_keys=True))
