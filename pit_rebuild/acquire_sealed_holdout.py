"""Acquire future-only KOSPI evidence for the sealed holdout.

The development cutoff is immutable. This module downloads a fresh source file
without reusing the development cache, filters strictly after the cutoff, writes
only into the sealed area, and does not run models or print market outcomes.
"""
from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import requests
import research_v1_marcap as marcap

ROOT=Path("/pit/private/sealed_holdout")
MANIFEST=Path("/pit/private/sealed_holdout_manifest.json")
CUTOFF=pd.Timestamp("2026-09-25")
YEAR=2026
URL=marcap.RAW_URL.format(year=YEAR)

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def main():
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if m.get("development_cutoff")!="2026-09-25" or not m.get("sealed"):
        raise SystemExit("ACQ_BLOCKED: invalid or unsealed manifest")
    if m.get("data_acquired"):
        raise SystemExit("ACQ_BLOCKED: manifest already marks data acquired")
    ROOT.mkdir(parents=True,exist_ok=True)
    raw_path=ROOT/"marcap-2026-fresh.parquet"
    if raw_path.exists():
        raise SystemExit("ACQ_BLOCKED: fresh raw file already exists; refusing overwrite")
    r=requests.get(URL,timeout=120)
    r.raise_for_status()
    raw=r.content
    tmp=ROOT/"marcap-2026-fresh.parquet.tmp"
    tmp.write_bytes(raw); os.replace(tmp,raw_path)
    df=pd.read_parquet(raw_path)
    if "Date" not in df.columns and df.index.name=="Date": df=df.reset_index()
    if "Date" not in df.columns: raise SystemExit("ACQ_BLOCKED: Date missing")
    dates=pd.to_datetime(df["Date"]).dt.normalize()
    eligible=df.loc[dates>CUTOFF].copy()
    if eligible.empty: raise SystemExit("ACQ_BLOCKED: source contains no sessions after development cutoff")
    edates=pd.to_datetime(eligible["Date"]).dt.normalize()
    if (edates<=CUTOFF).any(): raise SystemExit("ACQ_BLOCKED: cutoff leakage")
    sealed_raw=ROOT/"eligible_raw.parquet"
    eligible.to_parquet(sealed_raw,index=False)
    receipt={
      "acquisition_version":"indexalert-fresh-acq-v1",
      "source":"FinanceData/marcap (KRX-derived daily all-security data)",
      "source_url_template":"FinanceData/marcap raw GitHub yearly parquet",
      "source_sha256":sha256_bytes(raw),
      "cutoff":"2026-09-25",
      "first_eligible_date":str(edates.min().date()),
      "last_eligible_date":str(edates.max().date()),
      "eligible_rows":int(len(eligible)),
      "eligible_dates":int(edates.nunique()),
      "acquired_at":datetime.now(timezone.utc).isoformat(),
      "model_executed":False,
      "outcomes_unsealed":False,
    }
    (ROOT/"acquisition_receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    # Update only state flags; do not expose data/results to development output.
    m["data_acquired"]=True
    m["acquisition_receipt"]="sealed_holdout/acquisition_receipt.json"
    m["outcomes_unsealed"]=False
    tmpm=MANIFEST.with_suffix(".json.tmp")
    tmpm.write_text(json.dumps(m,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    os.replace(tmpm,MANIFEST)
    print(json.dumps({"fresh_acquisition":"SUCCESS","data_acquired":True,"outcomes_unsealed":False,"receipt":str(ROOT/"acquisition_receipt.json")},sort_keys=True))

if __name__=="__main__": main()
