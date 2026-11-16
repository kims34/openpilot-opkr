"""Full daily, all-available-year retrospective 21-session barrier forecasting.

This is a research replay of the currently deployed one_month_calibrated code.
Exact 10-calendar-year rolling data window, per-session next 21 complete
XNYS sessions, strict intraday highs/lows. All future bars are only used for
labels. Daily observed outcomes overlap; never treat observations as IID.

CSV generated locally by GitHub Actions and retained as downloadable artifact.
Yahoo retrospectively backfilled OHLC is NOT an original as-published PIT tape.
Never changes IndexAlert server, broker, credentials, model or Android client.
"""
from __future__ import annotations
import argparse
import bisect
import csv
import hashlib
import json
import math
import os
import statistics
import time
from datetime import date
from pathlib import Path

import numpy as np
import exchange_calendars as xcals

import one_month_calibrated as production
import one_month_probability as barrier
from research_monthly_time_machine_2015 import historical_bars
from research_monthly_time_machine_exact10y import _date_years_earlier

RAW_START = "1999-03-01"
RAW_END_EXCLUSIVE = "2026-11-16"
HORIZON = barrier.HORIZON
MAX_NEIGHBORS = max(barrier.K_CANDIDATES)
FEATURE_START = barrier.MIN_FEATURE_INDEX
PRIOR = barrier.PRIOR_STRENGTH
SCALES = np.array(barrier.FEATURE_SCALES)
WEIGHTS = np.array(barrier.FEATURE_WEIGHTS)
K_VALUES = tuple(barrier.K_CANDIDATES)
BLENDS = tuple(production.BLEND_WEIGHTS)
REQUIRED_PARITY_KEYS = (
    "up_10_probability", "down_10_probability",
    "selected_k_up", "selected_k_down",
    "blend_weight_up", "blend_weight_down",
    "baseline_up_10_probability", "baseline_down_10_probability",
)
COLUMNS = (
    "symbol","as_of","first_future_session","last_future_session",
    "lookback_start","training_sessions","history_full_ten_years","anchor_close",
    "up_threshold","down_threshold",
    "up_10_probability_pct","down_10_probability_pct",
    "baseline_up_pct","baseline_down_pct",
    "selected_k_up","selected_k_down","blend_up","blend_down",
    "up_hit","down_hit","future_high","future_low",
    "max_gain_pct","max_loss_pct",
    "brier_up","brier_down","brier_baseline_up","brier_baseline_down",
)


def get_complete_bars(symbol):
    bars=historical_bars(symbol,start=RAW_START,end=RAW_END_EXCLUSIVE)
    if len(bars) < 3000:
        raise ValueError("insufficient historical source to replay all years")
    cal=xcals.get_calendar("XNYS",start="1999-01-01",end="2027-01-01")
    date_list=[r[0] for r in bars]
    expected=[d.date().isoformat() for d in cal.sessions_in_range(date_list[0],date_list[-1])]
    if expected != date_list:
        missing=sorted(set(expected)-set(date_list))
        extra=sorted(set(date_list)-set(expected))
        raise ValueError("historical XNYS session coverage invalid: "+
                         repr({"missing":missing[:12],"extra":extra[:12]}))
    return bars


def _features_and_labels(bars):
    n=len(bars)
    close=[float(x[3]) for x in bars]
    hi=np.array([float(x[1]) for x in bars])
    lo=np.array([float(x[2]) for x in bars])
    feature=np.full((n,7),np.nan,dtype=float)
    for i in range(FEATURE_START,n):
        feature[i]=barrier._features(close,i)
    y=np.zeros((n,2),dtype=float)
    for i in range(n-HORIZON):
        y[i,0]=float(np.any(hi[i+1:i+HORIZON+1] >= close[i]*1.10))
        y[i,1]=float(np.any(lo[i+1:i+HORIZON+1] <= close[i]*.90))
    psum=np.vstack([np.zeros((1,2)),np.cumsum(y,axis=0)])
    return np.array(close),hi,lo,feature,y,psum


class DailyExactReplay:
    """Memoizes features, not unseen labels. Tests compare against the app."""
    def __init__(self,bars):
        self.bars=bars
        self.dates=[x[0] for x in bars]
        self.prices,self.highs,self.lows,self.features,self.y,self.ysums=_features_and_labels(bars)
        self.last_sessions_max=len(bars)-HORIZON-1

    def _base(self,first,stop):
        # Training records at forecast timestamp q are start+252 .. q-22,
        # for current t: start+252 .. t-21 (21 completed future bars).
        count=stop-first+1
        if count < 300:
            raise ValueError("insufficient matured analog training")
        return (self.ysums[stop+1]-self.ysums[first])/count

    def _analog_triplet(self,q,first,stop):
        # Freeze exact as-of available history; no future prices, labels or
        # forecasts can enter the sorted candidate pool.
        base=self._base(first,stop)
        indices=np.arange(first,stop+1,dtype=np.int32)
        delta=(self.features[indices]-self.features[q])/SCALES
        distances=np.sqrt(np.sum(WEIGHTS * delta*delta,axis=1))
        if not np.isfinite(distances).all():
            raise ValueError("invalid distance / future-data contamination")
        order=np.lexsort((indices,distances))
        blocked=bytearray(len(self.dates)+4)
        chosen=[]
        ds=[]
        for oi in order:
            p=int(indices[oi])
            if blocked[p]:
                continue
            chosen.append(p)
            ds.append(float(distances[oi]))
            blocked[max(0,p-2):p+3]=b"\x01"*min(5,p+3)
            if len(chosen)>=MAX_NEIGHBORS:
                break
        pairs={}
        for k in K_VALUES:
            length=min(k,len(chosen))
            if length==0:
                pairs[k]=base.copy()
                continue
            band=max(statistics.median(ds[:length]),0.35)
            # Match original production per-neighbor exp and Python summation
            w=[math.exp(-0.5*(d/band)**2) for d in ds[:length]]
            sw=sum(w)
            prior=np.array([sum(weight*self.y[idx,side]
                                for weight,idx in zip(w,chosen[:length]))
                            for side in range(2)])
            prediction=(prior+PRIOR*base)/(sw+PRIOR)
            pairs[k]=np.clip(prediction,0.0,1.0)
        return base,pairs

    def replay_date(self,at):
        window_first=bisect.bisect_left(self.dates,_date_years_earlier(self.dates[at]))
        first=window_first+FEATURE_START
        last_record=at-HORIZON
        if at+HORIZON >=len(self.dates) or last_record-first+1<300:
            raise ValueError("incomplete forecast/future or short 10y training")
        # Equivalent _validation_targets applied to the truncated as-of data.
        validation_first=max(first+300+HORIZON,
                             at+1-barrier.VALIDATION_DAYS-HORIZON)
        validation=list(range(validation_first,last_record+1))
        if len(validation)<120:
            raise ValueError("insufficient validation targets")
        tune_end=max(60,int(len(validation)*barrier.TUNE_FRACTION))
        hist_base=[]
        hist_analog={k:[] for k in K_VALUES}
        observed=[]
        for q in validation:
            # _score_binary_grid: q's training ends at q-HORIZON-1.
            b,a=self._analog_triplet(q,first,q-HORIZON-1)
            hist_base.append(b)
            for k in K_VALUES:
                hist_analog[k].append(a[k])
            observed.append(self.y[q].copy())
        hb=np.asarray(hist_base)
        yy=np.asarray(observed)
        current_base,current_analogs=self._analog_triplet(at,first,last_record)
        result={
            "as_of":self.dates[at],
            "training_sessions":at-window_first+1,
            "history_full_ten_years":self.dates[0]<=_date_years_earlier(self.dates[at]),
            "lookback_start":self.dates[window_first],
        }
        for side,name in ((0,"up"),(1,"down")):
            candidates=[]
            for k in K_VALUES:
                analog=np.asarray(hist_analog[k])[:,side]
                for w in BLENDS:
                    pred=hb[:tune_end,side]+w*(analog[:tune_end]-hb[:tune_end,side])
                    loss=float(np.mean((pred-yy[:tune_end,side])**2))
                    candidates.append((loss,w,k))
            loss,w,k=min(candidates,key=lambda t:(t[0],t[1],t[2]))
            analog=np.asarray(hist_analog[k])[:,side]
            def score(skill_slice):
                t=hb[skill_slice,side]
                a=analog[skill_slice]
                outcome=yy[skill_slice,side]
                pred=t+w*(a-t)
                model=float(np.mean((pred-outcome)**2))
                baseline=float(np.mean((t-outcome)**2))
                return len(outcome), (100.0*(1.0-model/baseline)
                                     if baseline>0 else 0.0)
            n,skill=score(slice(tune_end,None))
            mid=(len(validation)-tune_end)//2
            n1,skill1=score(slice(tune_end,tune_end+mid))
            n2,skill2=score(slice(tune_end+mid,None))
            accepted=(w>0 and n>=production.MIN_TEST_COUNT and skill>0
                      and n1>=production.MIN_HALF_COUNT and skill1>0
                      and n2>=production.MIN_HALF_COUNT and skill2>0)
            chosen_w=float(w if accepted else 0.0)
            output=float(current_base[side]+chosen_w*
                         (current_analogs[k][side]-current_base[side]))
            result[name+"_10_probability_pct"]=round(100.0*output,1)
            result["baseline_"+name+"_pct"]=round(100.0*current_base[side],1)
            result["selected_k_"+name]=k
            result["blend_"+name]=round(chosen_w,2)
        return result

    def original_app_for(self,at):
        lo=bisect.bisect_left(self.dates,_date_years_earlier(self.dates[at]))
        prefix=self.bars[lo:at+1]
        return production.estimate_probability([(d,c) for d,h,l,c in prefix],
                                                prefix)

    def check_parity(self,at,fast):
        original=self.original_app_for(at)
        translated={
            "up_10_probability":fast["up_10_probability_pct"],
            "down_10_probability":fast["down_10_probability_pct"],
            "selected_k_up":fast["selected_k_up"],
            "selected_k_down":fast["selected_k_down"],
            "blend_weight_up":fast["blend_up"],
            "blend_weight_down":fast["blend_down"],
            "baseline_up_10_probability":fast["baseline_up_pct"],
            "baseline_down_10_probability":fast["baseline_down_pct"],
        }
        mismatches={k:(translated[k],original[k])
                    for k in REQUIRED_PARITY_KEYS
                    if translated[k]!=original[k]}
        if mismatches:
            raise ValueError("optimized replay violates ORIGINAL app: " +
                             json.dumps({"asof":self.dates[at],"mismatch":mismatches},
                                        ensure_ascii=False))
        return True

    def score_one(self,symbol,at,result):
        future=self.bars[at+1:at+HORIZON+1]
        high=float(max(r[1] for r in future))
        low=float(min(r[2] for r in future))
        a=self.prices[at]
        y=self.y[at]
        pu=result["up_10_probability_pct"]/100
        pd=result["down_10_probability_pct"]/100
        bu=result["baseline_up_pct"]/100
        bd=result["baseline_down_pct"]/100
        return {
            "symbol":symbol,"as_of":self.dates[at],
            "first_future_session":future[0][0],
            "last_future_session":future[-1][0],
            "lookback_start":result["lookback_start"],
            "training_sessions":result["training_sessions"],
            "history_full_ten_years":result["history_full_ten_years"],
            "anchor_close":round(float(a),4),
            "up_threshold":round(float(a*1.1),4),
            "down_threshold":round(float(a*.9),4),
            **{key:result[key] for key in (
                "up_10_probability_pct","down_10_probability_pct",
                "baseline_up_pct","baseline_down_pct",
                "selected_k_up","selected_k_down","blend_up","blend_down")},
            "up_hit":int(y[0]),"down_hit":int(y[1]),
            "future_high":round(high,4),
            "future_low":round(low,4),
            "max_gain_pct":round(100*(high/a-1),4),
            "max_loss_pct":round(100*(low/a-1),4),
            "brier_up":(pu-y[0])**2,
            "brier_down":(pd-y[1])**2,
            "brier_baseline_up":(bu-y[0])**2,
            "brier_baseline_down":(bd-y[1])**2,
        }


def summarize(rows):
    out={"count":len(rows)}
    for field in ("up","down"):
        y=np.array([r[field+"_hit"] for r in rows],dtype=float)
        p=np.array([r[field+"_10_probability_pct"] for r in rows])/100
        b=np.array([r["baseline_"+field+"_pct"] for r in rows])/100
        loss=(p-y)**2
        bl=(b-y)**2
        out[field]={
            "hits":int(y.sum()),
            "hit_rate":round(float(y.mean()),6),
            "mean_forecast_pct":round(float(p.mean()*100),3),
            "model_brier":round(float(loss.mean()),8),
            "historical_rate_brier":round(float(bl.mean()),8),
            "model_minus_baseline_brier":round(float(loss.mean()-bl.mean()),8),
            "model_brier_skill_pct":round(float(100*(1-loss.mean()/bl.mean())),3)
                if bl.mean()>0 else None,
            "zero_event_brier":round(float(y.mean()),8),
        }
    out["combined_brier"]=round((out["up"]["model_brier"]+
                                  out["down"]["model_brier"])/2,8)
    out["combined_historical_baseline_brier"]=round((
        out["up"]["historical_rate_brier"]+
        out["down"]["historical_rate_brier"])/2,8)
    out["full_ten_years_count"]=sum(int(r["history_full_ten_years"]) for r in rows)
    out["first_as_of"]=rows[0]["as_of"]
    out["last_as_of"]=rows[-1]["as_of"]
    out["mean_annualized_volatility_note"]="not a trading return or directional forecast"
    return out


def run(symbol,year,out_dir="daily_monthly_artifacts"):
    if symbol not in ("SPY","QQQ") or not (2002<=year<=2009):
        raise ValueError("outside supported full 10y window")
    bars=get_complete_bars(symbol)
    replay=DailyExactReplay(bars)
    indices=[i for i,d in enumerate(replay.dates)
             if d.startswith(str(year)) and i<=replay.last_sessions_max
             and i-bisect.bisect_left(replay.dates,_date_years_earlier(d))>=714]
    if not indices:
        raise ValueError("no finished 21-session forecasts for year")
    results=[]
    parity=[]
    for number,i in enumerate(indices):
        probability=replay.replay_date(i)
        if i in (indices[0], indices[len(indices)//2], indices[-1]):
            replay.check_parity(i,probability)
            parity.append(replay.dates[i])
        results.append(replay.score_one(symbol,i,probability))
        if (number+1)%50==0:
            print("DAILY_REPLAY_PROGRESS",symbol,year,number+1,
                  "of",len(indices),flush=True)
    directory=Path(out_dir)
    directory.mkdir(parents=True,exist_ok=True)
    name=f"{symbol}_daily_21session_{year}"
    with open(directory/(name+".csv"),"w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(results)
    result={
        "symbol":symbol,"year":year,
        "metrics":summarize(results),
        "parity_dates":parity,"parity_original_app_8_fields_verified":True,
        "source_first":replay.dates[0],"source_last":replay.dates[-1],
        "price_source":"Yahoo public historical daily backfill",
        "price_vintage_pit_verified":False,
        "overlapping_horizon":HORIZON,
        "future_used_only_for_outcomes":True,
        "production_changed":False,
        "production_promotable":False,
        "csv_file":name+".csv",
        "input_sha256":hashlib.sha256(json.dumps(bars,separators=(",",":")).encode()).hexdigest(),
    }
    with open(directory/(name+".json"),"w",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2)
    print("DAILY_REPLAY_SUMMARY",json.dumps(result,ensure_ascii=False,sort_keys=True),flush=True)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol",required=True,choices=["SPY","QQQ"])
    ap.add_argument("--year",required=True,type=int)
    ap.add_argument("--out-dir",default="daily_monthly_artifacts")
    args=ap.parse_args()
    run(args.symbol,args.year,args.out_dir)


if __name__=="__main__":
    main()
