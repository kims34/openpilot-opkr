"""Purged PIT feature-family ablation for Distributional NetEV."""
from pathlib import Path
import json
from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_netev import distributional_walk_forward, freeze_original_topk, _fixed_record_map, _metric, _cost_stress
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_ml import FEATURES, stateful_select_records
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

MARKET=["market_ret1_median","market_ret5_median","market_ret20_median","breadth1","breadth5","dispersion20"]
RESID=["resid_ret1","resid_ret5","resid_ret20"]
FAMILIES={"all_context":CONTEXT_FEATURES,"base_only":FEATURES,"drop_market":[x for x in CONTEXT_FEATURES if x not in MARKET],"drop_residual":[x for x in CONTEXT_FEATURES if x not in RESID],"context_only":MARKET+RESID}

def main():
    raw=load_panel(Path("research_data/marcap_kospi_pit"))
    frame,legacy_map,diag,meta=load_or_build(raw,Path("research_data/pit_supervised_v1"),horizon=5,target_return=0.04,stop_return=-0.025,participation=0.0005,commission_round_trip_bps=3.0)
    frame=frame[frame["adv20_rank"]>=0.20].copy().reset_index(drop=True)
    z=add_fixed_horizon_target(raw,add_context(frame),legacy_map,5)
    fixed=_fixed_record_map(z,5)
    out={"policy":"predeclared_feature_family_ablation_same_purged_walkforward_no_oos_threshold_tuning","models":{}}
    for name,features in FAMILIES.items():
        pred,_=distributional_walk_forward(z,train_days=160,cal_days=40,test_days=40,purge_days=5,features=features)
        eligible=pred[pred["netev_low"]>0].copy()
        frozen=freeze_original_topk(eligible,3)
        records,selected,sd=stateful_select_records(frozen,fixed,top_k=3,threshold=0.0)
        out["models"][name]={"features":features,"selected_records":len(records),"trade_days":int(selected["decision_date"].nunique()) if not selected.empty else 0,"selection_diagnostics":sd,"metrics":_metric(records),"cost_stress":_cost_stress(records)}
    p=Path("research_results/marcap_pit_distributional_ablation"); p.mkdir(parents=True,exist_ok=True)
    (p/"summary.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print("DISTRIBUTIONAL_ABLATION="+json.dumps(out,ensure_ascii=False),flush=True)

if __name__=="__main__": main()
