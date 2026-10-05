"""One-shot offline promotion of verified candidate to official baseline."""
from pathlib import Path
import hashlib, json, os, shutil, time
import pandas as pd

candidate=Path("/pit/private/abstention_v3_positions_candidate.parquet")
official=Path("/pit/private/abstention_v3_positions.parquet")
backup=Path("/pit/private/abstention_v3_positions.pre_candidate_backup.parquet")
if not candidate.exists(): raise FileNotFoundError(candidate)

def sha256(p):
    h=hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

candidate_file_sha=sha256(candidate)
if official.exists():
    if not backup.exists():
        tmp=backup.with_suffix(backup.suffix+".tmp")
        shutil.copy2(official,tmp); os.replace(tmp,backup)
    backup_sha=sha256(backup)
else:
    backup_sha=None

tmp=official.with_suffix(official.suffix+".promotion_tmp")
shutil.copy2(candidate,tmp)
if sha256(tmp)!=candidate_file_sha: raise ValueError("promotion temp checksum mismatch")
os.replace(tmp,official)
official_sha=sha256(official)
if official_sha!=candidate_file_sha: raise ValueError("official checksum mismatch after atomic replace")

df=pd.read_parquet(official)
sort_cols=["horizon","coverage","decision_idx","rank","symbol"]
selection_cols=["fold","horizon","coverage","decision_idx","decision_date","symbol","rank","score"]
selection_fp=hashlib.sha256(df.sort_values(sort_cols)[selection_cols].to_csv(index=False).encode()).hexdigest()
position_fp=hashlib.sha256(df.sort_values(sort_cols).to_csv(index=False).encode()).hexdigest()
expected_selection="8a442cbf42ff8449e9d7d6a28e9ac7e4215e2997d45aa6e17e109318598a6156"
expected_position="53c6e32d18fb75f61825da07423f0f6e21b839ea234069e69e3d1c153a81387f"
if selection_fp!=expected_selection or position_fp!=expected_position: raise ValueError("promoted baseline fingerprint mismatch")
print("BASELINE_PROMOTION="+json.dumps({"rows":int(len(df)),"candidate_file_sha256":candidate_file_sha,"official_file_sha256":official_sha,"backup_file_sha256":backup_sha,"selection_fingerprint_sha256":selection_fp,"position_fingerprint_sha256":position_fp,"network_request_attempted":False,"sealed_holdout_authorized":False,"live_trading_authorized":False},sort_keys=True),flush=True)
