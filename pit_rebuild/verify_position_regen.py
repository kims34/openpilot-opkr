"""Aggregate-only verifier for private abstention-v3 position artifact."""
import json, hashlib
from pathlib import Path
import pandas as pd

P=Path("/pit/private/abstention_v3_positions.parquet")
df=pd.read_parquet(P)
counts={}
for h,g in df.groupby("horizon"):
    counts[str(int(h))]={}
    for cov,cg in g.groupby("coverage"):
        counts[str(int(h))][f"top_{int(round(float(cov)*100))}pct_train_threshold"]=int(len(cg))
canonical=df.sort_values(["horizon","coverage","decision_idx","rank","symbol"]).to_csv(index=False).encode()
print("POSITION_VERIFY="+json.dumps({
 "rows":int(len(df)),"decision_dates":int(df.decision_date.nunique()),
 "counts":counts,"position_fingerprint_sha256":hashlib.sha256(canonical).hexdigest(),
 "network_request_attempted":False,"security_identifiers_emitted":False,
 "sealed_holdout_authorized":False,"live_trading_authorized":False
},sort_keys=True))
