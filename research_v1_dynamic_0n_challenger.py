"""Preregistered Dynamic 0-N diagnostic challenger.

Does not modify Champion/Core/holdout. Reuses the frozen H5 selection-conditioned
OOF predictions, labels, costs, PIT universe and market-state gate. Fixed 0-5/0-10
are diagnostics only. Dynamic 0-N has no tuned N cap: every decision-time row with
conservative netev_low > 0 and the same normal-market gate may proceed to the
existing stateful execution selector. Capital per daily cohort remains frozen at
1/H, equal-weighted across admitted names.

This is intentionally an economic-gate upper-bound diagnostic, not a claim that
sector/factor/correlation or live execution uncertainty are solved. Those missing
inputs are reported as blockers for a full marginal-portfolio-utility challenger.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_netev import _fixed_record_map, freeze_original_topk
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_market_eligibility import veto_frozen_topk_nonstandard_market, tag_normal_market_eligibility
from research_v1_ml import stateful_select_records
from research_v1_selected_calibration import selected_calibration_walk_forward
from research_v1_distributional_long_history import _evaluate_selected
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

def rank_diagnostics(pred):
    x=pred[pred["fh_label_available"].fillna(False).astype(bool)].copy()
    x=x.sort_values(["decision_date","netev_low"],ascending=[True,False])
    x["rank_all"]=x.groupby("decision_date").cumcount()+1
    x["candidate_count"]=x.groupby("decision_date")["symbol"].transform("size")
    bands={"r1_3":(1,3),"r4_5":(4,5),"r6_10":(6,10),"r11_plus":(11,10**9)}
    out={}
    for name,(lo,hi) in bands.items():
        g=x[(x.rank_all>=lo)&(x.rank_all<=hi)].copy()
        y=pd.to_numeric(g["fh_net_return"],errors="coerce").dropna().to_numpy(float)
        gains=float(y[y>0].sum()) if len(y) else 0.0
        losses=float(-y[y<0].sum()) if len(y) else 0.0
        out[name]={"rows":int(len(y)),"mean_net_return":float(y.mean()) if len(y) else None,
                   "profit_factor":float(gains/losses) if losses>0 else None,
                   "positive_rate":float((y>0).mean()) if len(y) else None,
                   "mean_netev_low":float(pd.to_numeric(g["netev_low"],errors="coerce").mean()) if len(g) else None}
    # same diagnostics restricted to conservative-positive candidates
    pos=x[x.netev_low>0].copy()
    pos["rank_positive"]=pos.groupby("decision_date").cumcount()+1
    out["positive_candidate_count_by_day"]={
      "days_with_any":int(pos.decision_date.nunique()),
      "mean":float(pos.groupby("decision_date").size().mean()) if len(pos) else 0.0,
      "p50":float(pos.groupby("decision_date").size().quantile(.5)) if len(pos) else 0.0,
      "p90":float(pos.groupby("decision_date").size().quantile(.9)) if len(pos) else 0.0,
      "max":int(pos.groupby("decision_date").size().max()) if len(pos) else 0,
      "days_gt3":int((pos.groupby("decision_date").size()>3).sum()) if len(pos) else 0,
      "days_gt5":int((pos.groupby("decision_date").size()>5).sum()) if len(pos) else 0,
      "days_gt10":int((pos.groupby("decision_date").size()>10).sum()) if len(pos) else 0}
    return out

def evaluate_policy(raw,pred,fixed_map,horizon,name,kind,k=None):
    eligible=pred[pred.netev_low>0].copy()
    if kind=="fixed":
        frozen=freeze_original_topk(eligible,int(k))
        gated, vetoed, gate=veto_frozen_topk_nonstandard_market(frozen)
        technical_topk=int(k)
    else:
        tagged=tag_normal_market_eligibility(eligible)
        gated=tagged[tagged.normal_market_eligible.astype(bool)].copy()
        vetoed=tagged[~tagged.normal_market_eligible.astype(bool)].copy()
        gate={"policy":"PER_CANDIDATE_DYNAMIC_GATE_NO_FIXED_N","rows_before":int(len(tagged)),
              "rows_after":int(len(gated)),"vetoed_rows":int(len(vetoed)),
              "backfill_allowed":"NOT_APPLICABLE_DYNAMIC_SEQUENCE","official_status_validated":False}
        technical_topk=max(1,int(gated.groupby("decision_date").size().max())) if len(gated) else 1
    records,selected,diag=stateful_select_records(gated,fixed_map,top_k=technical_topk,threshold=0.0)
    result=_evaluate_selected(raw,pred,records,selected,diag,horizon)
    result["policy"]=name; result["market_gate"]=gate
    if len(selected):
        counts=selected.groupby("decision_date").size()
        result["selected_n_by_trade_day"]={"mean":float(counts.mean()),"p50":float(counts.quantile(.5)),
          "p90":float(counts.quantile(.9)),"max":int(counts.max()),"days_gt3":int((counts>3).sum()),
          "days_gt5":int((counts>5).sum()),"days_gt10":int((counts>10).sum())}
        result["turnover_proxy_entries_per_oos_session"]=float(len(selected)/pred.decision_date.nunique())
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cache",default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache",default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir",default="research_results/dynamic_0n_challenger")
    args=ap.parse_args()
    raw=load_panel(Path(args.cache))
    frame,legacy,diag,meta=load_or_build(raw,Path(args.supervised_cache),horizon=5,target_return=.04,stop_return=-.025,participation=.0005,commission_round_trip_bps=3.0)
    frame=frame[frame.adv20_rank>=.20].copy().reset_index(drop=True)
    z=add_fixed_horizon_target(raw,add_context(frame),legacy,5)
    fixed_map=_fixed_record_map(z,5)
    pred,folds=selected_calibration_walk_forward(z,train_days=504,cal_days=126,test_days=126,purge_days=5,features=CONTEXT_FEATURES,top_k=3)
    if pred.empty: raise RuntimeError("no predictions")
    policies={
      "A_frozen_dynamic_0_3_champion_reference":evaluate_policy(raw,pred,fixed_map,5,"A_frozen_dynamic_0_3_champion_reference","fixed",3),
      "B_fixed_0_5_diagnostic":evaluate_policy(raw,pred,fixed_map,5,"B_fixed_0_5_diagnostic","fixed",5),
      "C_fixed_0_10_diagnostic":evaluate_policy(raw,pred,fixed_map,5,"C_fixed_0_10_diagnostic","fixed",10),
      "D_economic_gate_dynamic_0_N_challenger":evaluate_policy(raw,pred,fixed_map,5,"D_economic_gate_dynamic_0_N_challenger","dynamic")}
    report={"experiment":"EXP-2026-10-06-DYNAMIC-0N-01",
      "stage":"DEVELOPMENTAL_PREREGISTERED_DIAGNOSTIC_NOT_HOLDOUT_NOT_PROMOTION",
      "frozen":{"horizon":5,"train_days":504,"cal_days":126,"test_days":126,"purge_days":5,
        "q25":.25,"admission":"netev_low_gt_0","participation":.0005,"commission_round_trip_bps":3.0,
        "same_model_features_labels_costs_pit":True,"sealed_holdout_touched":False},
      "rank_diagnostics":rank_diagnostics(pred),"policies":policies,
      "full_marginal_utility_blockers":["official sector/factor exposure mapping","candidate-to-portfolio PIT dependence/correlation contract",
        "capital-in-KRW and minimum-order/round-lot policy","empirical partial-fill/slippage/impact uncertainty","empirical capacity and live execution evidence"],
      "interpretation_guardrail":"D is an economic-gate dynamic-N upper-bound diagnostic. It cannot be promoted as the final marginal-utility policy until the listed PIT/execution inputs exist. B/C are N-effect diagnostics only. No result changes Champion."}
    out=Path(args.result_dir); out.mkdir(parents=True,exist_ok=True)
    (out/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    print("DYNAMIC_0N="+json.dumps(report,ensure_ascii=False,default=str),flush=True)
if __name__=="__main__": main()
