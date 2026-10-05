"""Regenerate development-only abstention-v3 selections from rebuilt PIT.

Offline only. Writes private position rows to a caller-supplied path and prints
only aggregate counts/fingerprints. This is NOT sealed validation and cannot
promote a strategy.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import research_kospi_clean_v2 as v2
import research_kospi_abstention_v3 as v3
from research_v1_pit_legacy_adapter import load_legacy_compatible_pit

def _legacy_clean(raw: pd.DataFrame) -> pd.DataFrame:
    # Mirror v2.load_data after file loading so feature/universe semantics stay fixed.
    out=pd.DataFrame({
        "date":pd.to_datetime(raw["Date"],errors="coerce"),
        "code":raw["Code"].astype(str).str.replace(r"\.0$","",regex=True).str.zfill(6),
        "name":raw["Name"].astype(str),
        "market":raw["Market"].astype(str).str.upper(),
        "open":pd.to_numeric(raw["Open"],errors="coerce"),
        "high":pd.to_numeric(raw["High"],errors="coerce"),
        "low":pd.to_numeric(raw["Low"],errors="coerce"),
        "close":pd.to_numeric(raw["Close"],errors="coerce"),
        "amount":pd.to_numeric(raw["Amount"],errors="coerce"),
        "official_pct":pd.to_numeric(raw["ChangesRatio"],errors="coerce"),
    })
    out=out[out.market.eq("KOSPI")]
    out=out[out.code.str.match(r"^\d{5}0$")]
    pat="|".join(v2.EXCLUDE_NAME_PARTS)
    out=out[~out.name.str.contains(pat,case=False,na=False,regex=True)]
    out=out.dropna(subset=["date","open","high","low","close","amount","official_pct"])
    out=out[(out.open>0)&(out.close>0)&(out.amount>0)]
    out=out[(out.low<=out.open)&(out.open<=out.high)&(out.low<=out.close)&(out.close<=out.high)]
    out["r1"]=out.official_pct/100.0
    out=out[(out.r1>-0.36)&(out.r1<0.36)]
    out=out.sort_values(["code","date"]).drop_duplicates(["code","date"],keep="last")
    dates=sorted(out.date.unique()); date_to_idx={pd.Timestamp(d):i for i,d in enumerate(dates)}
    out["day_idx"]=out.date.map(lambda x:date_to_idx[pd.Timestamp(x)]).astype(int)
    return out.reset_index(drop=True)

def regenerate(obs: pd.DataFrame, n_days: int) -> pd.DataFrame:
    rows=[]; first_test=v2.TRAIN_DAYS+v2.PURGE_DAYS
    # Exact market-session calendar used by v2 day_idx semantics.
    idx_to_date={int(i):pd.Timestamp(d) for i,d in obs[["decision_idx","date"]].drop_duplicates().groupby("decision_idx")["date"].first().items()}
    for fold_no,test_start in enumerate(range(first_test,n_days-1,v2.TEST_DAYS),1):
        test_end=min(test_start+v2.TEST_DAYS,n_days-1)
        train_end=test_start-v2.PURGE_DAYS; train_start=max(0,train_end-v2.TRAIN_DAYS)
        if train_end-train_start<int(v2.TRAIN_DAYS*0.9): continue
        train_all=obs[(obs.decision_idx>=train_start)&(obs.decision_idx<train_end)]
        test_all=obs[(obs.decision_idx>=test_start)&(obs.decision_idx<test_end)]
        for h in v2.HORIZONS:
            ret_col=f"ret{h}"; train=train_all.dropna(subset=v2.FEATURES+[ret_col]).copy(); test=test_all.dropna(subset=v2.FEATURES+[ret_col]).copy()
            if len(train)<5000 or test.empty: continue
            y=(train[ret_col]-v2.LABEL_COST>0).astype(int)
            if y.nunique()<2: continue
            m=v3.model(); m.fit(train[v2.FEATURES],y)
            train_p=m.predict_proba(train[v2.FEATURES])[:,1]; test["score"]=m.predict_proba(test[v2.FEATURES])[:,1]
            for cov in v3.COVERAGES:
                threshold=float(np.quantile(train_p,1.0-cov))
                for decision_idx,day in test.groupby("decision_idx",sort=True):
                    chosen=day[day.score>=threshold].nlargest(v2.TOP_K,"score")
                    for rank,r in enumerate(chosen.itertuples(index=False),1):
                        entry_idx=int(decision_idx)+1; exit_idx=int(decision_idx)+h\n                        if entry_idx not in idx_to_date or exit_idx not in idx_to_date: raise ValueError("exact session date mapping missing")\n                        # v2 entry is next-session open. Recover it from gross return is unsafe; join clean data in main below.\n                        rows.append({"fold":fold_no,"horizon":h,"coverage":cov,"decision_idx":int(decision_idx),"decision_date":pd.Timestamp(r.date),"entry_day":idx_to_date[entry_idx],"exit_day":idx_to_date[exit_idx],"symbol":str(r.code).zfill(6),"rank":rank,"score":float(r.score),"gross_return":float(getattr(r,ret_col))})
    return pd.DataFrame(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--pit-dir",required=True); ap.add_argument("--private-output",required=True); ap.add_argument("--from-date",default="2018-01-02"); ap.add_argument("--to-date",default="2026-09-25"); args=ap.parse_args()
    raw=load_legacy_compatible_pit(args.pit_dir,args.from_date,args.to_date); clean=_legacy_clean(raw); dates=sorted(clean.date.unique()); obs=v2.engineer(clean); selected=regenerate(obs,len(dates))\n    entry_px=clean[["code","day_idx","open"]].rename(columns={"code":"symbol","day_idx":"entry_idx","open":"entry_price"})\n    selected["entry_idx"]=selected["decision_idx"]+1\n    selected=selected.merge(entry_px,on=["symbol","entry_idx"],how="left",validate="many_to_one")\n    if selected["entry_price"].isna().any() or (selected["entry_price"]<=0).any(): raise ValueError("selected position missing exact next-session entry price")\n    selected=selected.drop(columns=["entry_idx"])
    out=Path(args.private_output); out.parent.mkdir(parents=True,exist_ok=True); selected.to_parquet(out,index=False)
    # Fingerprint includes private identifiers but emits only the digest.
    canonical=selected.sort_values(["horizon","coverage","decision_idx","rank","symbol"]).to_csv(index=False).encode()
    counts={str(int(h)):{f"top_{int(round(float(cov)*100))}pct_train_threshold":int(len(cg)) for cov,cg in hg.groupby("coverage")} for h,hg in selected.groupby("horizon")}
    summary={"mode":"DEVELOPMENT_CONTAMINATED_POSITION_REGEN","rows":int(len(selected)),"decision_dates":int(selected.decision_date.nunique()) if len(selected) else 0,"counts":counts,"position_fingerprint_sha256":hashlib.sha256(canonical).hexdigest(),"research_status":"DEVELOPMENT_CONTAMINATED_NOT_SEALED","profitability_validated":False,"network_request_attempted":False,"security_identifiers_emitted":False,"sealed_holdout_authorized":False,"live_trading_authorized":False}
    print("POSITION_REGEN="+json.dumps(summary,sort_keys=True))
if __name__=="__main__": main()
