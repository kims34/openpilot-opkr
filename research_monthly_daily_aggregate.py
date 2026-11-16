"""Aggregate 2002-2026 historical daily SPY/QQQ probability audit artifacts.

Research only: downloaded from two successful GitHub Action runs. No market
fetch, no order permission, no model fitting, no production changes.
Calculates Brier versus each as-of's matured historical-rate baseline.
Confidence intervals account for 21-session overlapping touch outcomes
(block and year resampling); not independent PIT-vintage proof.
"""
from __future__ import annotations
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

FIRST=2002
LAST=2026
SYMBOLS=("SPY","QQQ")
SEED=20261116
BLOCK=21
MODEL_SOURCE="Original one_month_calibrated, exact as-of 10-year prefix (shorter before 2009)"
CSV_FIELDS=(
    "symbol","as_of","first_future_session","last_future_session",
    "lookback_start","training_sessions","history_full_ten_years",
    "anchor_close","up_threshold","down_threshold",
    "up_10_probability_pct","down_10_probability_pct",
    "baseline_up_pct","baseline_down_pct",
    "selected_k_up","selected_k_down","blend_up","blend_down",
    "up_hit","down_hit","future_high","future_low",
    "max_gain_pct","max_loss_pct",
    "brier_up","brier_down","brier_baseline_up","brier_baseline_down",
)
YEAR_FIELDS=("year","symbol","n","up_hits","down_hits",
             "up_brier","down_brier","combined_brier",
             "up_baseline_brier","down_baseline_brier","combined_baseline_brier",
             "combined_baseline_gain","full_ten_years_count")


def _from_csv(path):
    with path.open(newline="",encoding="utf-8") as handle:
        rows=list(csv.DictReader(handle))
    if not rows:
        raise ValueError("empty original daily predictions "+str(path))
    for r in rows:
        if any(not r.get(k) for k in (
                "symbol","as_of","up_10_probability_pct",
                "down_10_probability_pct","up_hit","down_hit")):
            raise ValueError("missing forecast/result field")
        for p in ("up_10_probability_pct","down_10_probability_pct",
                  "baseline_up_pct","baseline_down_pct"):
            v=float(r[p])
            if not math.isfinite(v) or not (0<=v<=100):
                raise ValueError("invalid probability")
        for s in ("up_hit","down_hit"):
            if r[s] not in ("0","1"):
                raise ValueError("invalid 21-session outcome")
        for p in ("brier_up","brier_down","brier_baseline_up",
                  "brier_baseline_down"):
            if not math.isfinite(float(r[p])):
                raise ValueError("nonfinite Brier")
        for side in ("up","down"):
            expected=(float(r[side+"_10_probability_pct"])/100-
                      int(r[side+"_hit"]))**2
            if abs(float(r["brier_"+side])-expected)>1e-9:
                raise ValueError("Brier record integrity mismatch")
        if r["last_future_session"]<r["as_of"]:
            raise ValueError("future outcome preceding prediction")
    return rows


def _stats(rows):
    n=len(rows)
    result={"n":n, "first":rows[0]["as_of"],"last":rows[-1]["as_of"]}
    for side in ("up","down"):
        actual=np.array([int(r[side+"_hit"]) for r in rows],dtype=float)
        p=np.array([float(r[side+"_10_probability_pct"])/100 for r in rows])
        b=np.array([float(r["baseline_"+side+"_pct"])/100 for r in rows])
        model=(p-actual)**2
        base=(b-actual)**2
        result[side]={
            "hit_count":int(sum(actual)),
            "hit_rate":float(np.mean(actual)),
            "mean_forecast":float(np.mean(p)),
            "brier":float(np.mean(model)),
            "baseline_brier":float(np.mean(base)),
            "gain":float(np.mean(base-model)),
            "row_gain":base-model,
        }
    result["combined_brier"]=(result["up"]["brier"]+
                              result["down"]["brier"])/2
    result["combined_baseline_brier"]=(result["up"]["baseline_brier"]+
                                      result["down"]["baseline_brier"])/2
    result["combined_gain"]=result["combined_baseline_brier"]-result["combined_brier"]
    return result


def _moving_block_ci(series,seed=SEED):
    values=np.asarray(series,dtype=float)
    n=len(values)
    if n<42:
        return None
    rng=np.random.default_rng(seed)
    reps=[]
    for _ in range(1000):
        begins=rng.integers(0,n-BLOCK+1,size=math.ceil(n/BLOCK))
        indices=(begins[:,None]+np.arange(BLOCK)).ravel()[:n]
        reps.append(float(values[indices].mean()))
    return [float(x) for x in np.quantile(reps,(.025,.975))]


def _year_resample_ci(per_year,seed=SEED):
    rng=np.random.default_rng(seed)
    n=len(per_year)
    sampled=[]
    for _ in range(2000):
        ids=rng.integers(0,n,size=n)
        weight=sum(per_year[i][0] for i in ids)
        gain=sum(per_year[i][0]*per_year[i][1] for i in ids)/weight
        sampled.append(gain)
    return [float(x) for x in np.quantile(sampled,(.025,.975))]


def _bins(rows,symbol,side):
    bins=((0,.01),(.01,.03),(.03,.05),(.05,.10),(.10,.20),(.20,.40),(.40,1.00001))
    output=[]
    for start,end in bins:
        selected=[r for r in rows if
                  start<=float(r[side+"_10_probability_pct"])/100<end]
        if not selected:
            continue
        predicted=np.array([float(r[side+"_10_probability_pct"])/100
                            for r in selected])
        outcome=np.array([int(r[side+"_hit"]) for r in selected])
        output.append({
            "symbol":symbol,"side":side,
            "bin":f"{start:.2f}–{min(1,end):.2f}",
            "observations":len(selected),
            "forecast_mean_pct":float(np.mean(predicted)*100),
            "actual_touch_percent":float(np.mean(outcome)*100),
            "actual_events":int(np.sum(outcome)),
        })
    return output


def audit(main_dir,early_dir,out_dir):
    main=Path(main_dir)
    early=Path(early_dir)
    dest=Path(out_dir)
    dest.mkdir(parents=True,exist_ok=True)
    all_rows=[]
    annual=[]
    integrity={}
    annual_stats={}
    for symbol in SYMBOLS:
        digests=set()
        prev_date=""
        annual_stats[symbol]=[]
        for year in range(FIRST,LAST+1):
            root=early if year<=2009 else main
            name=f"{symbol}_daily_21session_{year}"
            file=root/(name+".csv")
            score=root/(name+".json")
            if not file.exists() or not score.exists():
                raise ValueError("missing annual original forecast artifact "+name)
            rows=_from_csv(file)
            with score.open(encoding="utf-8") as f:
                metadata=json.load(f)
            if metadata.get("year")!=year or metadata.get("symbol")!=symbol:
                raise ValueError("cross-symbol/year artifact contamination")
            if len(rows)!=metadata.get("metrics",{}).get("count"):
                raise ValueError("year count mismatch from immutable CI result")
            if len(metadata.get("parity_dates",[]))<3 or not metadata.get(
                    "parity_original_app_8_fields_verified"):
                raise ValueError("insufficient original-app parity evidence")
            digests.add(metadata["input_sha256"])
            asofs=[r["as_of"] for r in rows]
            if (any(not d.startswith(str(year)) for d in asofs)
                    or asofs!=sorted(set(asofs)) or asofs[0]<=prev_date):
                raise ValueError("year/year-date ordering or duplication")
            prev_date=asofs[-1]
            if year>=2010:
                for r in rows:
                    r["history_full_ten_years"]="True"
            # The early-history runner emits an explicit full-10y flag.
            for r in rows:
                r["history_full_ten_years"]=r["history_full_ten_years"]=="True"
            s=_stats(rows)
            annual_stats[symbol].append((len(rows),s["combined_gain"]))
            num_full=sum(int(r["history_full_ten_years"]) for r in rows)
            annual.append({
                "year":year,"symbol":symbol,
                "n":s["n"],
                "up_hits":s["up"]["hit_count"],
                "down_hits":s["down"]["hit_count"],
                "up_brier":s["up"]["brier"],
                "down_brier":s["down"]["brier"],
                "combined_brier":s["combined_brier"],
                "up_baseline_brier":s["up"]["baseline_brier"],
                "down_baseline_brier":s["down"]["baseline_brier"],
                "combined_baseline_brier":s["combined_baseline_brier"],
                "combined_baseline_gain":s["combined_gain"],
                "full_ten_years_count":num_full,
            })
            all_rows.extend(rows)
        integrity[symbol]={"source_sha256_count":len(digests),
                            "source_sha256_values":sorted(digests)}
        if len(digests)!=1:
            # Intra-run vendor revisions can invalidate cross-year comparisons.
            raise ValueError("different historical vendor OHLC source digests")
    if len(annual)!=50 or len(all_rows)<12000:
        raise ValueError("missing yearly source data")
    counts_by_symbol={symbol:sum(r["symbol"]==symbol for r in all_rows)
                      for symbol in SYMBOLS}
    result={
        "source":"Yahoo retrospective public daily OHLC - NOT original vintage PIT",
        "first_year":FIRST,"last_year":LAST,
        "asset_year_jobs":len(annual),
        "rows_total":len(all_rows),
        "rows_by_symbol":counts_by_symbol,
        "daily_forecast_runs_vs_independent_events":"21-session outcome windows overlap",
        "no_live_deployment":True,
        "no_model_promotion":True,
        "all_input_sha_consistent_by_asset":True,
        "data_integrity":integrity,
        "model":MODEL_SOURCE,
        "by_symbol":{},
        "calibration":[],
    }
    for symbol in SYMBOLS:
        rows=sorted((r for r in all_rows if r["symbol"]==symbol),
                    key=lambda x:x["as_of"])
        s=_stats(rows)
        scores=[]
        for side in ("up","down"):
            d=s[side]
            gain=d.pop("row_gain")
            d["moving_21_session_block_ci95_gain"]=_moving_block_ci(
                gain,seed=SEED+(1 if symbol=="QQQ" else 0)+(1 if side=="down" else 0))
            scores.append(gain)
            result["calibration"].extend(_bins(rows,symbol,side))
        average=(scores[0]+scores[1])/2
        cohort_stats={}
        for label,subset in (
            ("full_10y",[r for r in rows if r["history_full_ten_years"]]),
            ("partial_10y",[r for r in rows if not r["history_full_ten_years"]]),
            ("calendar_2010_2026",[r for r in rows if r["as_of"]>="2010-01-01"]),
        ):
            if not subset:
                continue
            sc=_stats(subset)
            for side in ("up","down"):
                sc[side].pop("row_gain",None)
            cohort_stats[label]={
                "n":len(subset),"start":subset[0]["as_of"],
                "end":subset[-1]["as_of"],
                "events_up":sc["up"]["hit_count"],
                "events_down":sc["down"]["hit_count"],
                "brier_model":sc["combined_brier"],
                "brier_baseline":sc["combined_baseline_brier"],
                "baseline_minus_model_gain":sc["combined_gain"],
            }
        result["by_symbol"][symbol]={
            "n":len(rows),"as_of_start":rows[0]["as_of"],
            "as_of_end":rows[-1]["as_of"],
            "cohorts":cohort_stats,
            "up":s["up"],"down":s["down"],
            "combined_brier":s["combined_brier"],
            "combined_baseline_brier":s["combined_baseline_brier"],
            "combined_baseline_gain":s["combined_gain"],
            "combined_gain_block_ci95":_moving_block_ci(average),
            "combined_gain_year_resample_ci95":_year_resample_ci(
                annual_stats[symbol]),
            "full_ten_year_forecasts":sum(
                int(r["history_full_ten_years"]) for r in rows),
        }

    with (dest/"all_daily_spy_qqq_2002_2026.csv").open(
            "w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)
    with (dest/"annual_brier_2002_2026.csv").open(
            "w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=YEAR_FIELDS)
        writer.writeheader()
        writer.writerows(sorted(annual,key=lambda r:(r["year"],r["symbol"])))
    with (dest/"calibration_2002_2026.csv").open(
            "w",newline="",encoding="utf-8") as f:
        cols=("symbol","side","bin","observations","forecast_mean_pct",
              "actual_touch_percent","actual_events")
        writer=csv.DictWriter(f,fieldnames=cols)
        writer.writeheader()
        writer.writerows(result["calibration"])
    with (dest/"summary_2002_2026.json").open(
            "w",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2,sort_keys=True)
    print("ALL_YEARS_FINAL_SCORECARD",json.dumps({
        "year_count":LAST-FIRST+1,"asset_year_jobs":len(annual),
        "rows_total":result["rows_total"],
        "by_symbol":result["by_symbol"],
        "research_only":True,
    },ensure_ascii=False,sort_keys=True),flush=True)
    return result


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--main",default="downloaded/main")
    p.add_argument("--early",default="downloaded/early")
    p.add_argument("--out",default="full_daily_results")
    args=p.parse_args()
    audit(args.main,args.early,args.out)


if __name__=="__main__":
    main()
