import hashlib, json, os
from pathlib import Path
import pandas as pd

ROOT=Path("/pit/marcap_kospi_pit")
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

years={}
total=0
mins=[]; maxs=[]
for y in range(2018,2027):
    p=ROOT/f"kospi-pit-{y}.parquet"
    if not p.exists():
        years[str(y)]={"present":False}; continue
    df=pd.read_parquet(p)
    total += len(df)
    years[str(y)]={"present":True,"rows":int(len(df)),"sha256":sha(p)}
stats=ROOT/"build_stats.json"
payload={
 "mode":"OFFLINE_PIT_VOLUME_VERIFY",
 "network_request_attempted":False,
 "root_exists":ROOT.exists(),
 "years":years,
 "rows_sum":int(total),
 "build_stats_present":stats.exists(),
 "build_stats_sha256":sha(stats) if stats.exists() else None,
 "security_identifiers_emitted":False,
 "sealed_holdout_authorized":False,
 "live_trading_authorized":False,
}
if stats.exists():
    s=json.loads(stats.read_text())
    payload["build_summary"]={k:s.get(k) for k in ["start","end","rows_written","membership_rows_preserved","membership_rows_without_executable_bar","unique_symbols","trading_dates","daily_universe_min","daily_universe_median","daily_universe_max","judge_eligible"]}
print("PIT_VOLUME_VERIFY="+json.dumps(payload,sort_keys=True))
