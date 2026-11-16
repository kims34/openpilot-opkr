"""IndexAlert 21-session barrier risk-regime calibration, research ONLY.

Input: the 12,468 immutable historical replay rows, with all daily as-of
probabilities and *later* 21-session touch labels. No future labels enter a
forecast. No live production/Android/broker action or automatic promotion.

Pre-declared challengers:
  rolling_logit_offset: trailing 1260 matured historical probabilities,
    intercept regularized by 25 log-odds pseudo-observations.
  regime_logit_offset: same but condition on causal 21-day vol >=25%
    OR 21-day close-to-close return <=-5%; fallback to global.
  quarter_base: 75% existing model plus 25% as-of causal base rate.

Evaluation: 2018-01-02 to latest 21-session matured forecast, with 2010-17
used for initial calibration. Not an unseen PIT holdout (years previously
inspected). 21-session overlapping labels require block uncertainty.
"""
from __future__ import annotations

import bisect
import csv
import json
import math
import statistics
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np

HORIZON=21
SEED=20261116
STRESS_VOL=0.25
STRESS_21_RETURN=-0.05
EXTREME_VOL=0.35
EXTREME_RETURN=-0.10
BACK=1260
MIN_GLOBAL=252
MIN_REGIME=160
MIN_EVENTS=8
PENALTY=25.0
START_DATE="2018-01-01"
SYMBOLS=("SPY","QQQ")
SIDES=("up","down")
CANDIDATES=("original","rolling_logit_offset","regime_logit_offset","quarter_base")
COLS=("symbol","as_of","last_future_session","year","vol21","ret21","stress","extreme",
      "original_up","original_down","base_up","base_down","true_up","true_down",
      "rolling_logit_offset_up","rolling_logit_offset_down",
      "regime_logit_offset_up","regime_logit_offset_down",
      "quarter_base_up","quarter_base_down",
      "eligible_global_n","eligible_stress_n","past_21session_label_guard")
SOURCE_FILE="all_daily_spy_qqq_2002_2026.csv"


def read_rows(path):
    with open(path,newline="",encoding="utf-8") as f:
        result=list(csv.DictReader(f))
    if len(result) != 12468:
        raise ValueError(f"expected immutable 12468-row source; got {len(result)}")
    grouped=defaultdict(list)
    for r in result:
        symbol=r["symbol"]
        if symbol not in SYMBOLS:
            raise ValueError("unknown symbol")
        data={
            "as_of":r["as_of"],"maturity":r["last_future_session"],
            "close":float(r["anchor_close"]),
            "p":{s:float(r[f"{s}_10_probability_pct"])/100 for s in SIDES},
            "base":{s:float(r[f"baseline_{s}_pct"])/100 for s in SIDES},
            "hit":{s:int(r[f"{s}_hit"]) for s in SIDES},
            "full10":r.get("history_full_ten_years","False")=="True",
        }
        if data["maturity"]<=data["as_of"] or data["close"]<=0:
            raise ValueError("bad event timeline / close")
        if any(not (0<=data["p"][s]<=1 and 0<=data["base"][s]<=1)
               or data["hit"][s] not in (0,1) for s in SIDES):
            raise ValueError("bad probabilities or outcomes")
        grouped[symbol].append(data)
    for symbol in SYMBOLS:
        rows=grouped[symbol]
        if [r["as_of"] for r in rows]!=sorted(set(r["as_of"] for r in rows)):
            raise ValueError("prediction days not unique and ordered")
        for i,r in enumerate(rows):
            if i>=HORIZON:
                # Market state uses only closes at or prior to as_of.
                old=rows[i-HORIZON]["close"]
                r["ret21"]=r["close"]/old-1
                x=np.diff(np.log([t["close"] for t in rows[i-HORIZON:i+1]]))
                r["vol21"]=float(np.std(x,ddof=1)*math.sqrt(252))
                r["stress"]=bool(r["vol21"]>=STRESS_VOL or r["ret21"]<=STRESS_21_RETURN)
                r["extreme"]=bool(r["vol21"]>=EXTREME_VOL or r["ret21"]<=EXTREME_RETURN)
            else:
                r.update(vol21=None,ret21=None,stress=False,extreme=False)
    return grouped


def clipped_logit(p):
    value=min(max(float(p),0.0005),0.9995)
    return math.log(value/(1-value))


def expit(x):
    if x>=0:
        z=math.exp(-x)
        return 1/(1+z)
    z=math.exp(x)
    return z/(1+z)


def fitted_offset(probs, labels, *, min_n=MIN_GLOBAL):
    """Fit only intercept, leave production relative ranking intact."""
    n=len(probs)
    if n<min_n or sum(labels)<MIN_EVENTS or n-sum(labels)<MIN_EVENTS:
        return 0.0
    logits=np.array([clipped_logit(p) for p in probs])
    labels=np.asarray(labels,dtype=float)
    # L2 penalty discourages noisy shifts during rare-event intervals.
    left,right=-3.0,3.0
    for _ in range(54):
        mid=(left+right)/2
        prediction=np.reciprocal(1.0+np.exp(-np.clip(logits+mid,-35.0,35.0)))
        grad=float(np.sum(prediction-labels)+PENALTY*mid)
        if grad>0:
            right=mid
        else:
            left=mid
    return (left+right)/2


def eligible_indices(rows,t,window=BACK):
    """Only matured event labels strictly before date t can train."""
    days=[r["as_of"] for r in rows]
    stop=bisect.bisect_left(days,rows[t]["as_of"])
    # Only last window prior to the prediction, not entire 2018+ labels.
    begin=max(0,stop-window)
    return [j for j in range(begin,stop)
            if rows[j]["maturity"] < rows[t]["as_of"]]


def apply_on_date(rows,t,*,history_override=None):
    current=rows[t]
    if current["vol21"] is None:
        raise ValueError("insufficient volatility lookback")
    previous=history_override if history_override is not None else eligible_indices(rows,t)
    # Guard against future-label leakage and same-day unseen maturity.
    if any(rows[j]["maturity"]>=current["as_of"] or j>=t for j in previous):
        raise ValueError("future or unmatured label in calibration history")
    past=[rows[j] for j in previous]
    conditions=[r for r in past if r["stress"] == current["stress"]
                and r["vol21"] is not None]
    n_stress=len(conditions)
    n_global=len(past)
    outputs={"original":{},"rolling_logit_offset":{},
             "regime_logit_offset":{},"quarter_base":{}}
    for side in SIDES:
        original=current["p"][side]
        outputs["original"][side]=original
        global_delta=fitted_offset([r["p"][side] for r in past],
                                   [r["hit"][side] for r in past])
        local_delta=fitted_offset([r["p"][side] for r in conditions],
                                  [r["hit"][side] for r in conditions],
                                  min_n=MIN_REGIME)
        eligible_local=(n_stress>=MIN_REGIME and
                        sum(r["hit"][side] for r in conditions)>=MIN_EVENTS and
                        n_stress-sum(r["hit"][side] for r in conditions)>=MIN_EVENTS)
        outputs["rolling_logit_offset"][side]=expit(clipped_logit(original)+global_delta)
        outputs["regime_logit_offset"][side]=expit(
            clipped_logit(original)+(local_delta if eligible_local else global_delta))
        outputs["quarter_base"][side]=0.75*original+0.25*current["base"][side]
    return outputs, {"eligible_global_n":n_global,
                     "eligible_stress_n":n_stress,
                     "past_21session_label_guard":True}


def _metric(rows):
    if not rows:
        return {"n":0}
    scores={}
    for name in CANDIDATES:
        for side in SIDES:
            y=np.array([r["true_"+side] for r in rows],dtype=float)
            p=np.array([r[name+"_"+side] for r in rows],dtype=float)
            scores[name+"_"+side]=float(np.mean((p-y)**2))
        scores[name+"_combined"]=(scores[name+"_up"]+scores[name+"_down"])/2
    def gain(name,side):
        return scores["original_"+side]-scores[name+"_"+side]
    result={"n":len(rows),"events_up":int(sum(r["true_up"] for r in rows)),
            "events_down":int(sum(r["true_down"] for r in rows)),
            "mean_original_up":float(np.mean([r["original_up"] for r in rows])),
            "mean_original_down":float(np.mean([r["original_down"] for r in rows])),
            "original_up":scores["original_up"],
            "original_down":scores["original_down"],
            "original_combined":scores["original_combined"]}
    for name in CANDIDATES[1:]:
        result[name]={
            "brier_combined":scores[name+"_combined"],
            "gain_up":gain(name,"up"),
            "gain_down":gain(name,"down"),
            "gain_combined":scores["original_combined"]-scores[name+"_combined"],
        }
    return result


def bootstrap_gain(rows,name,seed=SEED):
    y=np.array([[r["true_up"],r["true_down"]] for r in rows],dtype=float)
    p=np.array([[r["original_up"],r["original_down"]] for r in rows],dtype=float)
    q=np.array([[r[name+"_up"],r[name+"_down"]] for r in rows],dtype=float)
    diff=np.mean((p-y)**2-(q-y)**2,axis=1)
    n=len(diff)
    rng=np.random.default_rng(seed)
    boot=[]
    for _ in range(1000):
        starts=rng.integers(0,n-HORIZON+1,size=math.ceil(n/HORIZON))
        ids=(starts[:,None]+np.arange(HORIZON)).ravel()[:n]
        boot.append(float(diff[ids].mean()))
    return [float(x) for x in np.quantile(boot,[.025,.975])]


def calibration_table(rows):
    bins=((0,.02),(.02,.05),(.05,.10),(.10,.20),(.20,.40),(.40,1.000001))
    out=[]
    for symbol in SYMBOLS:
        for side in SIDES:
            for regime in ("normal","stress","extreme"):
                pool=[r for r in rows if r["symbol"]==symbol and (
                    (regime=="normal" and not r["stress"])
                    or (regime=="stress" and r["stress"])
                    or (regime=="extreme" and r["extreme"]))]
                for a,b in bins:
                    group=[r for r in pool if a<=r["original_"+side]<b]
                    if group:
                        out.append({
                            "symbol":symbol,"side":side,"regime":regime,
                            "bin":f"{a:.2f}-{min(1,b):.2f}","n":len(group),
                            "forecast_mean_pct":100*float(np.mean([r["original_"+side] for r in group])),
                            "actual_rate_pct":100*float(np.mean([r["true_"+side] for r in group])),
                            "events":sum(r["true_"+side] for r in group)})
    return out


def run(source_dir,out_dir):
    grouped=read_rows(Path(source_dir)/SOURCE_FILE)
    out=Path(out_dir)
    out.mkdir(parents=True,exist_ok=True)
    daily=[]
    by_symbol={}
    for symbol in SYMBOLS:
        rows=grouped[symbol]
        for t,row in enumerate(rows):
            if row["as_of"]<START_DATE:
                continue
            if not row["full10"]:
                raise ValueError("post-2018 as-of without complete 10-year history")
            p,info=apply_on_date(rows,t)
            result={
                "symbol":symbol,"as_of":row["as_of"],"year":row["as_of"][:4],
                "last_future_session":row["maturity"],
                "vol21":row["vol21"],"ret21":row["ret21"],
                "stress":row["stress"],"extreme":row["extreme"],
                **info,
            }
            for side in SIDES:
                result["true_"+side]=row["hit"][side]
                result["base_"+side]=row["base"][side]
                for name in CANDIDATES:
                    result[name+"_"+side]=p[name][side]
            daily.append(result)
        output=[r for r in daily if r["symbol"]==symbol]
        by_symbol[symbol]={
            "all":_metric(output),
            "stress":_metric([r for r in output if r["stress"]]),
            "normal":_metric([r for r in output if not r["stress"]]),
            "extreme":_metric([r for r in output if r["extreme"]]),
            "first_half_2018_2021":_metric([r for r in output if r["year"]<="2021"]),
            "second_half_2022_2026":_metric([r for r in output if r["year"]>="2022"]),
        }
        for name in CANDIDATES[1:]:
            by_symbol[symbol]["all"][name]["block_bootstrap_gain_95"] = bootstrap_gain(
                output,name,seed=SEED+len(symbol)+len(name))
            # Strict research gate: both signs, both periods, and block CI lower>0
            allm=by_symbol[symbol]["all"][name]
            one=by_symbol[symbol]["first_half_2018_2021"][name]
            two=by_symbol[symbol]["second_half_2022_2026"][name]
            stress=by_symbol[symbol]["stress"][name]
            by_symbol[symbol]["all"][name]["research_gate_passed"]=bool(
                allm["gain_up"]>0 and allm["gain_down"]>0
                and one["gain_combined"]>0 and two["gain_combined"]>0
                and stress["gain_combined"]>0
                and allm["block_bootstrap_gain_95"][0]>0)
    annual=[]
    for symbol in SYMBOLS:
        for year in sorted(set(r["year"] for r in daily if r["symbol"]==symbol)):
            sample=[r for r in daily if r["symbol"]==symbol and r["year"]==year]
            annual.append({"symbol":symbol,"year":year,"n":len(sample),
                           "stress_n":sum(r["stress"] for r in sample),
                           **_metric(sample)})
    diagnostic=calibration_table(daily)
    with open(out/"daily_risk_recalibration_2018_2026.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=COLS)
        w.writeheader()
        w.writerows(daily)
    with open(out/"calibration_by_stress_probability_bins.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=("symbol","side","regime","bin","n",
                                      "forecast_mean_pct","actual_rate_pct","events"))
        w.writeheader()
        w.writerows(diagnostic)
    with open(out/"annual_risk_recalibration_2018_2026.json","w",encoding="utf-8") as f:
        json.dump(annual,f,ensure_ascii=False,indent=2,sort_keys=True)
    report={
        "n_total":len(daily),"by_symbol":by_symbol,
        "source":"2026 retrospective Yahoo OHLC as-of daily app replay; NOT original PIT",
        "asof_fit":"only labels whose 21-session maturity < forecast date",
        "comparison":"original app / regularized rolling-logit / risk-regime logit / quarter baseline",
        "predeclared_regime":"past 21-session annualized close volatility >=25% OR past 21-session close return <=-5%",
        "no_model_promotion":True,
        "research_holdout_unseen":False,
        "production_changed":False,
        "independence_note":"21-session outcomes overlap; confidence bands are exploratory",
        "missing_pit_vintage":True,
    }
    with open(out/"risk_calibration_summary.json","w",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,indent=2,sort_keys=True)
    print("RISK_CALIBRATION_FINAL",json.dumps({
        "n":len(daily),"by_symbol":by_symbol,
        "production_changed":False,"source_pit_verified":False,
    },ensure_ascii=False,sort_keys=True),flush=True)
    return report


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",default="downloaded")
    p.add_argument("--out-dir",default="risk_calibration_result")
    args=p.parse_args()
    run(args.input_dir,args.out_dir)
