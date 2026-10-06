"""Preregistered rank-aware uncertainty diagnostic for Dynamic 0-N.

Frozen before test outcomes are inspected. Rank bands are structural, not tuned:
1-3 (Champion domain), 4-5 and 6-10 (requested diagnostics), 11+ (open tail).
Each fold estimates residual q25/q50/q75 on calibration-only rows ranked by
predicted mean, then applies that rank-band uncertainty to test rows ranked by
predicted mean. No test outcome enters ranking/calibration/admission.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from research_v1_context import CONTEXT_FEATURES,add_context
from research_v1_distributional_netev import Q_LOW,Q_MED,Q_HIGH,_bucket,_fixed_record_map,_pipe
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_market_eligibility import tag_normal_market_eligibility
from research_v1_ml import stateful_select_records
from research_v1_distributional_long_history import _evaluate_selected
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

BANDS=((1,3,"r1_3"),(4,5,"r4_5"),(6,10,"r6_10"),(11,10**9,"r11_plus"))
def rank_band(r):
    for lo,hi,n in BANDS:
        if lo<=r<=hi:return n
    raise ValueError(r)

def qs(g):
    r=(g.fh_net_return.astype(float)-g.pred_mean.astype(float)).dropna()
    if len(r)<30:return None
    return {"low":float(r.quantile(Q_LOW)),"med":float(r.quantile(Q_MED)),
            "high":float(r.quantile(Q_HIGH)),"n":int(len(r))}

def walk(z,train_days=504,cal_days=126,test_days=126,purge_days=5):
    dates=sorted(pd.Timestamp(x) for x in z.decision_date.drop_duplicates())
    start=train_days+cal_days+2*purge_days; outs=[]; folds=[]
    while start<len(dates):
        td=dates[start:start+test_days]
        ce=start-purge_days; cs=ce-cal_days; te=cs-purge_days
        if not td or te<=0: start+=test_days; continue
        tr=z[z.decision_date.isin(dates[:te])].copy()
        ca=z[z.decision_date.isin(dates[cs:ce])].copy()
        ts=z[z.decision_date.isin(td)].copy()
        tr=tr[tr.fh_label_available.fillna(False).astype(bool)]
        if tr.empty or ca.empty or ts.empty:start+=test_days;continue
        m=_pipe(CONTEXT_FEATURES);m.fit(tr[CONTEXT_FEATURES],tr.fh_net_return.astype(float))
        ca["pred_mean"]=m.predict(ca[CONTEXT_FEATURES]);ts["pred_mean"]=m.predict(ts[CONTEXT_FEATURES])
        for x in (ca,ts):
            x["pred_rank"]=x.groupby("decision_date").pred_mean.rank(method="first",ascending=False).astype(int)
            x["rank_band"]=x.pred_rank.map(rank_band)
            x["vol_bucket"]=_bucket(x.vol20_rank)
        qmap={}; global_by_band={}
        for b,g in ca[ca.fh_label_available.fillna(False).astype(bool)].groupby("rank_band"):
            q=qs(g)
            if q: global_by_band[b]=q
            for vb,h in g.groupby("vol_bucket"):
                zq=qs(h)
                if zq:qmap[(b,str(vb))]=zq
        rows=[]
        for _,r in ts.iterrows():
            q=qmap.get((r.rank_band,str(r.vol_bucket))) or global_by_band.get(r.rank_band)
            if not q: continue
            d=r.to_dict()
            d["netev_low"]=float(r.pred_mean)+q["low"]
            d["netev_med"]=float(r.pred_mean)+q["med"]
            d["netev_high"]=float(r.pred_mean)+q["high"]
            d["rank_cal_n"]=q["n"]; d["score"]=d["netev_low"]; rows.append(d)
        if rows:outs.append(pd.DataFrame(rows))
        folds.append({"test_start":str(td[0].date()),"test_end":str(td[-1].date()),
                      "calibration_rank_bands":[[a,b,n] for a,b,n in BANDS],
                      "available_band_calibration_n":{k:v["n"] for k,v in global_by_band.items()}})
        start+=test_days
    return (pd.concat(outs,ignore_index=True) if outs else pd.DataFrame()),folds

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--cache",default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache",default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir",default="research_results/dynamic_0n_rankaware");a=ap.parse_args()
    raw=load_panel(Path(a.cache))
    frame,legacy,_,_=load_or_build(raw,Path(a.supervised_cache),horizon=5,target_return=.04,stop_return=-.025,participation=.0005,commission_round_trip_bps=3.0)
    frame=frame[frame.adv20_rank>=.20].copy().reset_index(drop=True)
    z=add_fixed_horizon_target(raw,add_context(frame),legacy,5);fm=_fixed_record_map(z,5)
    pred,folds=walk(z)
    eligible=pred[pred.netev_low>0].copy();tag=tag_normal_market_eligibility(eligible)
    gated=tag[tag.normal_market_eligible.astype(bool)].copy()
    maxn=max(1,int(gated.groupby("decision_date").size().max())) if len(gated) else 1
    rec,sel,diag=stateful_select_records(gated,fm,top_k=maxn,threshold=0.0)
    result=_evaluate_selected(raw,pred,rec,sel,diag,5)
    byband={}
    if len(sel):
      for b,g in sel.groupby("rank_band"):
        y=pd.to_numeric(g.fh_net_return,errors="coerce").dropna().to_numpy(float)
        gains=float(y[y>0].sum());loss=float(-y[y<0].sum())
        byband[str(b)]={"trades":len(y),"mean_net_return":float(y.mean()),"pf":float(gains/loss) if loss else None}
      n=sel.groupby("decision_date").size()
      nd={"mean":float(n.mean()),"p50":float(n.quantile(.5)),"p90":float(n.quantile(.9)),"max":int(n.max())}
    else:nd={}
    report={"experiment":"EXP-2026-10-06-DYNAMIC-0N-RANKAWARE-01",
      "stage":"DEVELOPMENTAL_PREREGISTERED_RANK_AWARE_DIAGNOSTIC_NOT_HOLDOUT",
      "protocol":{"rank_bands":[[a,b,n] for a,b,n in BANDS],"rank_variable":"pred_mean_only",
       "calibration":"fold_local_rank_band_x_vol_bucket_q25_with_rank_band_fallback",
       "test_outcome_used_for_threshold":False,"parameter_search":False,"sealed_holdout_touched":False},
      "eligible_rows":int(len(eligible)),"selected_by_rank_band":byband,"selected_n":nd,
      "result":result,"folds":folds,
      "guardrail":"No Champion change. Rank-aware economic gate remains incomplete marginal utility until PIT dependence/sector and capital/execution constraints are available."}
    p=Path(a.result_dir);p.mkdir(parents=True,exist_ok=True)
    (p/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    print("RANKAWARE_0N="+json.dumps(report,ensure_ascii=False,default=str),flush=True)
if __name__=="__main__":main()
