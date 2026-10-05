"""Aggregate-only verifier for private abstention-v3 position artifact."""
import json, hashlib
from pathlib import Path
import pandas as pd
from research_v1_pit_legacy_adapter import load_legacy_compatible_pit
from research_kospi_abstention_v3_position_regen import _legacy_clean

P=Path("/pit/private/abstention_v3_positions_candidate.parquet")
df=pd.read_parquet(P)
required={"fold","horizon","coverage","decision_idx","decision_date","entry_day","exit_day","symbol","rank","score","gross_return","entry_price"}
missing=required-set(df.columns)
if missing: raise ValueError(f"position artifact missing columns: {sorted(missing)}")
if df.empty: raise ValueError("position artifact is empty")
if df[list(required)].isna().any().any(): raise ValueError("position artifact contains null required values")
if (pd.to_datetime(df.entry_day)<=pd.to_datetime(df.decision_date)).any(): raise ValueError("entry_day must be after decision_date")
if (pd.to_datetime(df.exit_day)<pd.to_datetime(df.entry_day)).any(): raise ValueError("exit_day must not precede entry_day")
raw=load_legacy_compatible_pit("/pit/marcap_kospi_pit","2018-01-02","2026-09-25")
clean=_legacy_clean(raw)
calendar=clean[["day_idx","date"]].drop_duplicates().sort_values("day_idx")
if calendar.day_idx.duplicated().any() or calendar.date.duplicated().any(): raise ValueError("PIT session calendar is not unique")
if calendar.day_idx.astype(int).tolist()!=list(range(len(calendar))): raise ValueError("PIT session calendar is not contiguous")
idx_to_date=calendar.set_index("day_idx")["date"]
expected_decision=df["decision_idx"].map(idx_to_date)
expected_entry=df["decision_idx"].add(1).map(idx_to_date)
expected_exit=pd.Series([idx_to_date.get(int(i)+int(h),pd.NaT) for i,h in zip(df["decision_idx"],df["horizon"])],index=df.index)
if expected_decision.isna().any() or expected_entry.isna().any() or expected_exit.isna().any(): raise ValueError("position references missing PIT session")
if not pd.to_datetime(df["decision_date"]).reset_index(drop=True).equals(pd.to_datetime(expected_decision).reset_index(drop=True)): raise ValueError("decision_date failed exact PIT-session invariant")
if not pd.to_datetime(df["entry_day"]).reset_index(drop=True).equals(pd.to_datetime(expected_entry).reset_index(drop=True)): raise ValueError("entry_day failed exact PIT-session invariant")
if not pd.to_datetime(df["exit_day"]).reset_index(drop=True).equals(pd.to_datetime(expected_exit).reset_index(drop=True)): raise ValueError("exit_day failed exact PIT-session invariant")
if (pd.to_numeric(df.entry_price,errors="coerce")<=0).any(): raise ValueError("entry_price must be positive")
if df.duplicated(["horizon","coverage","decision_idx","rank"]).any(): raise ValueError("duplicate selection rank within decision bucket")
rank_ok=df.groupby(["horizon","coverage","decision_idx"])["rank"].apply(lambda x: sorted(x.astype(int).tolist())==list(range(1,len(x)+1)))
if not rank_ok.all(): raise ValueError("selection ranks are not contiguous from 1")
if (df.groupby(["horizon","coverage","decision_idx"]).size()>3).any(): raise ValueError("selection bucket exceeds TOP_K=3")
if not set(pd.to_numeric(df.horizon,errors="coerce").astype(int).unique()).issubset({1,2,3,5}): raise ValueError("unexpected horizon")
if not set(pd.to_numeric(df.coverage,errors="coerce").round(8).unique()).issubset({0.01,0.05,0.1}): raise ValueError("unexpected coverage")
if (pd.to_numeric(df.score,errors="coerce")<0).any() or (pd.to_numeric(df.score,errors="coerce")>1).any(): raise ValueError("score outside probability bounds")
order=df.sort_values(["horizon","coverage","decision_idx","rank"])
score_order_ok=order.groupby(["horizon","coverage","decision_idx"])["score"].apply(lambda x: x.astype(float).is_monotonic_decreasing)
if not score_order_ok.all(): raise ValueError("rank order is inconsistent with descending score")
counts={}
for h,g in df.groupby("horizon"):
    counts[str(int(h))]={}
    for cov,cg in g.groupby("coverage"):
        counts[str(int(h))][f"top_{int(round(float(cov)*100))}pct_train_threshold"]=int(len(cg))
sort_cols=["horizon","coverage","decision_idx","rank","symbol"]
selection_cols=["fold","horizon","coverage","decision_idx","decision_date","symbol","rank","score"]
selection_canonical=df.sort_values(sort_cols)[selection_cols].to_csv(index=False).encode()
position_canonical=df.sort_values(sort_cols).to_csv(index=False).encode()
print("POSITION_VERIFY="+json.dumps({
 "rows":int(len(df)),"decision_dates":int(df.decision_date.nunique()),
 "counts":counts,"selection_fingerprint_sha256":hashlib.sha256(selection_canonical).hexdigest(),
 "position_fingerprint_sha256":hashlib.sha256(position_canonical).hexdigest(),
 "network_request_attempted":False,"security_identifiers_emitted":False,
 "sealed_holdout_authorized":False,"live_trading_authorized":False
},sort_keys=True))
