from pathlib import Path
import hashlib,json
p=Path("/pit/marcap_kospi_pit/build_stats.json")
d=json.loads(p.read_text())
keys=["start","end","rows_written","membership_rows_preserved","membership_rows_without_executable_bar","unique_symbols","trading_dates","daily_universe_min","daily_universe_median","daily_universe_max","membership_daily_universe_min","membership_daily_universe_median","membership_daily_universe_max","schema","judge_eligible","judge_blocker","common_stock_identity_validated"]
out={k:d.get(k) for k in keys}
out["build_stats_sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
out["years"]=[{"year":x.get("year"),"rows":x.get("rows"),"valid_rows":x.get("valid_rows"),"rejected_bar_rows":x.get("rejected_bar_rows"),"dates":x.get("dates"),"symbols":x.get("symbols")} for x in d.get("year_stats",[])]
out.update({"mode":"OFFLINE_BUILD_STATS_SUMMARY","network_request_attempted":False,"security_identifiers_emitted":False,"sealed_holdout_authorized":False,"live_trading_authorized":False})
print("PIT_BUILD_VERIFY="+json.dumps(out,sort_keys=True))
