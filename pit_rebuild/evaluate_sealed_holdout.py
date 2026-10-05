"""One-shot sealed holdout evaluator for the frozen IndexAlert v3 policy.

History is used only for fitting/warm-up. Rows after the immutable cutoff are
the only scored holdout. Results are written privately and not printed.
"""
from __future__ import annotations
import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import numpy as np,pandas as pd
import research_kospi_clean_v2 as v2
import research_kospi_abstention_v3 as v3

CUTOFF=pd.Timestamp("2026-09-25")
HIST=Path("/pit/marcap_kospi_pit")
SEALED=Path("/pit/private/sealed_holdout")
RESULT=Path("/pit/private/sealed_holdout_result.json")
BASE_SEL="8a442cbf42ff8449e9d7d6a28e9ac7e4215e2997d45aa6e17e109318598a6156"
BASE_POS="53c6e32d18fb75f61825da07423f0f6e21b839ea234069e69e3d1c153a81387f"

def hfile(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()

def raw_to_v2(df):
 def col(*n):
  for x in n:
   if x in df.columns:return x
  raise RuntimeError("missing "+str(n))
 d=pd.DataFrame({"date":pd.to_datetime(df[col("Date","date")]),"code":df[col("Code","symbol","code")].astype(str).str.replace(r"\.0$","",regex=True).str.zfill(6),"name":df[col("Name","name")].astype(str),"market":df[col("Market","market")].astype(str).str.upper(),"open":pd.to_numeric(df[col("Open","open")],errors="coerce"),"high":pd.to_numeric(df[col("High","high")],errors="coerce"),"low":pd.to_numeric(df[col("Low","low")],errors="coerce"),"close":pd.to_numeric(df[col("Close","close")],errors="coerce"),"amount":pd.to_numeric(df[col("Amount","value","amount")],errors="coerce"),"official_pct":pd.to_numeric(df[col("ChangesRatio","ChagesRatio","ChangeRatio","krx_change_return")],errors="coerce")})
 if "krx_change_return" in df.columns and not any(x in df.columns for x in ("ChangesRatio","ChagesRatio","ChangeRatio")): d["official_pct"]*=100.0
 d=d[d.market.eq("KOSPI") & d.code.str.match(r"^\d{5}0$")]
 pat="|".join(v2.EXCLUDE_NAME_PARTS); d=d[~d.name.str.contains(pat,case=False,na=False,regex=True)]
 d=d.dropna(); d=d[(d.open>0)&(d.close>0)&(d.amount>0)&(d.low<=d.open)&(d.open<=d.high)&(d.low<=d.close)&(d.close<=d.high)]
 d["r1"]=d.official_pct/100.; d=d[(d.r1>-.36)&(d.r1<.36)]
 return d.sort_values(["code","date"]).drop_duplicates(["code","date"],keep="last")

def main():
 if RESULT.exists(): raise SystemExit("EVAL_BLOCKED: result already exists")
 freshp=SEALED/"eligible_raw.parquet"
 if not freshp.exists(): raise SystemExit("EVAL_BLOCKED: sealed data missing")
 fs=raw_to_v2(pd.read_parquet(freshp)); fs=fs[fs.date>CUTOFF]
 if fs.empty or (fs.date<=CUTOFF).any(): raise SystemExit("EVAL_BLOCKED: invalid fresh range")
 # History files are normalized PIT outputs; use enough history for frozen 5y training and feature warmup.
 hp=sorted(HIST.glob("kospi-pit-*.parquet"))
 if not hp: raise SystemExit("EVAL_BLOCKED: frozen history missing")
 hs=raw_to_v2(pd.concat([pd.read_parquet(p) for p in hp],ignore_index=True)); hs=hs[hs.date<=CUTOFF]
 allx=pd.concat([hs,fs],ignore_index=True).sort_values(["code","date"]).drop_duplicates(["code","date"],keep="last")
 dates=sorted(allx.date.unique()); mp={pd.Timestamp(d):i for i,d in enumerate(dates)}; allx["day_idx"]=allx.date.map(lambda x:mp[pd.Timestamp(x)]).astype(int)
 obs=v2.engineer(allx); test=obs[obs.date>CUTOFF].copy()
 if test.empty: raise SystemExit("EVAL_BLOCKED: no engineered holdout rows")
 train=obs[obs.date<=CUTOFF].copy()
 metrics={}; thresholds={}
 for h in v2.HORIZONS:
  tr=train.dropna(subset=v2.FEATURES+[f"ret{h}"]); te=test.dropna(subset=v2.FEATURES+[f"ret{h}"]).copy()
  if len(tr)<5000 or te.empty: continue
  y=(tr[f"ret{h}"]-v2.LABEL_COST>0).astype(int); m=v3.model(); m.fit(tr[v2.FEATURES],y)
  tp=m.predict_proba(tr[v2.FEATURES])[:,1]; te["p"]=m.predict_proba(te[v2.FEATURES])[:,1]
  metrics[str(h)]={}; thresholds[str(h)]={}
  for cov in v3.COVERAGES:
   th=float(np.quantile(tp,1-cov)); thresholds[str(h)][str(cov)]=th
   ch=te[te.p>=th].groupby("decision_idx",sort=True).apply(lambda z:z.nlargest(v2.TOP_K,"p"),include_groups=False)
   vals=(ch[f"ret{h}"].astype(float)-v2.LABEL_COST).tolist() if len(ch) else []
   metrics[str(h)][str(cov)]={"trades":len(vals),"mean_net_25bp":float(np.mean(vals)) if vals else None,"positive_fraction":float(np.mean(np.array(vals)>0)) if vals else None}
 payload={"version":"sealed-holdout-v1","cutoff":"2026-09-25","baseline_selection_fingerprint":BASE_SEL,"baseline_position_fingerprint":BASE_POS,"fresh_source_sha256":hfile(freshp),"fresh_first":str(fs.date.min().date()),"fresh_last":str(fs.date.max().date()),"fresh_dates":int(fs.date.nunique()),"thresholds_from_frozen_history_only":thresholds,"metrics":metrics,"policy_changed_after_unseal":False,"passed":False,"pass_rule_status":"NOT_YET_PREDECLARED","created_at":datetime.now(timezone.utc).isoformat()}
 tmp=RESULT.with_suffix(".json.tmp"); tmp.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n"); os.replace(tmp,RESULT)
 print(json.dumps({"sealed_evaluation":"COMPLETE","result_written":str(RESULT),"metrics_emitted":False,"passed":False,"pass_rule_status":"NOT_YET_PREDECLARED"},sort_keys=True))
if __name__=="__main__":main()
