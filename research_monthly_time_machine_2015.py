"""Time-machine replay: what the shipped IndexAlert 21-day model would
calculate using only daily bars through historical as-of date.

It does NOT assert that an Android application existed in 2015, or that
today's vendor backfilled prices are exact historical as-published vintages.
No production deploy, trading, app-state mutation, or model promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, date, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import numpy as np
import requests
import exchange_calendars as xcals

from research_monthly_direct_benchmark import FastServedReplay
from research_monthly_touch_v1 import validate_ohlc, touch_label

NY = ZoneInfo("America/New_York")
START = "2009-01-01"
END = "2016-03-01"
FIRST_YEAR = 2015
HORIZON = 21
SYMBOLS = ("SPY", "QQQ")


class ReplayError(ValueError):
    pass


def historical_bars(symbol, start=START, end=END):
    if symbol not in SYMBOLS:
        raise ReplayError("unsupported symbol")
    def epoch(ymd):
        return int(datetime.fromisoformat(ymd).replace(tzinfo=timezone.utc).timestamp())
    response = requests.get(
        "https://query1.finance.yahoo.com/v8/finance/chart/" + quote(symbol, safe=""),
        params={"period1":epoch(start),"period2":epoch(end),"interval":"1d",
                "includePrePost":"false","events":"div,splits"},
        headers={"User-Agent":"Mozilla/5.0 IndexAlert-Historical-Research"},
        timeout=35,
    )
    response.raise_for_status()
    chart = response.json().get("chart") or {}
    if chart.get("error"):
        raise ReplayError("provider historical data error")
    result = chart.get("result") or []
    if len(result)!=1 or result[0].get("meta",{}).get("symbol")!=symbol:
        raise ReplayError("missing/mismatched historical symbol")
    node=result[0]
    times=node.get("timestamp") or []
    q=((node.get("indicators") or {}).get("quote") or [{}])[0]
    highs,lows,closes=(q.get("high") or [],q.get("low") or [],q.get("close") or [])
    if not len(times)==len(highs)==len(lows)==len(closes):
        raise ReplayError("mismatched daily OHLC array lengths")
    output=[]
    for ts,h,l,c in zip(times,highs,lows,closes):
        if any(v is None for v in (h,l,c)):
            raise ReplayError("missing daily high/low/close; no close substitution")
        day=datetime.fromtimestamp(int(ts),timezone.utc).astimezone(NY).date().isoformat()
        h,l,c=(float(v) for v in (h,l,c))
        if not all(math.isfinite(v) and v>0 for v in (h,l,c)):
            raise ReplayError("non-finite or nonpositive OHLC")
        if h+1e-7<c or l-1e-7>c or h<l:
            raise ReplayError("malformed OHLC")
        if output and day<=output[-1][0]:
            raise ReplayError("unsorted or duplicated daily bars")
        output.append((day,h,l,c))
    if len(output)<1250:
        raise ReplayError("not enough early years of historical price evidence")
    return output


def exchange_session_guard(bars):
    """Reject missing XNYS sessions for model inputs and 21-session outcomes."""
    cal=xcals.get_calendar("XNYS")
    first, last=bars[0][0],bars[-1][0]
    expected=[d.date().isoformat() for d in cal.sessions_in_range(first,last)]
    observed=[r[0] for r in bars]
    if expected!=observed:
        missing=sorted(set(expected)-set(observed))
        extra=sorted(set(observed)-set(expected))
        raise ReplayError("session coverage mismatch: missing="
                          +str(missing[:8])+", extra="+str(extra[:8]))
    return {"first":first,"last":last,"sessions":len(observed),"missing":0}


def one_date(replay, i, *, verify_app=False):
    dates, p, h, l = replay.dates, replay.p, replay.h, replay.l
    if i+HORIZON>=len(dates):
        raise ReplayError("needs 21 finished future trading sessions")
    model=replay.estimate(i)
    if verify_app:
        original=replay.exact_app_estimate(i)
        keys=("up","down","up_selected_k","down_selected_k",
              "up_blend_weight","down_blend_weight")
        if any(model[k]!=original[k] for k in keys):
            raise ReplayError("historical replay differs from original app model")
    actual=touch_label(p,h,l,i)
    hi=float(max(h[i+1:i+HORIZON+1]))
    lo=float(min(l[i+1:i+HORIZON+1]))
    anchor=float(p[i])
    return {
        "as_of":dates[i],
        "forecast_calculated_after":"regular close of as_of",
        "target_first_session":dates[i+1],
        "target_last_session":dates[i+HORIZON],
        "anchor_close":round(anchor,4),
        "up_10_target":round(anchor*1.10,4),
        "down_10_target":round(anchor*0.90,4),
        "forecast_up_10_pct":round(model["up"]*100,1),
        "forecast_down_10_pct":round(model["down"]*100,1),
        "outcome_up_10_hit":int(actual[0]),
        "outcome_down_10_hit":int(actual[1]),
        "future_21_session_max_high":round(hi,4),
        "future_21_session_min_low":round(lo,4),
        "max_high_pct_change":round((hi/anchor-1)*100,3),
        "min_low_pct_change":round((lo/anchor-1)*100,3),
        "brier_up":round(float((model["up"]-actual[0])**2),6),
        "brier_down":round(float((model["down"]-actual[1])**2),6),
        "app_exact_parity_verified":verify_app,
    }


def simulate(symbol, *, year=FIRST_YEAR, specific="2015-01-02"):
    if year!=FIRST_YEAR:
        raise ReplayError("the tested vintage window is fixed at 2015")
    bars=historical_bars(symbol)
    guard=exchange_session_guard(bars)
    close=[(d,c) for d,h,l,c in bars]
    # No high/low imputation. Same price basis as existing app monthly forecast.
    replay=FastServedReplay(close,bars)
    if specific not in replay.dates:
        raise ReplayError("selected as-of must be a completed exchange session")
    position={d:i for i,d in enumerate(replay.dates)}
    monthly={}
    for i,d in enumerate(replay.dates):
        if not d.startswith(str(year)):
            continue
        k=d[:7]
        if k not in monthly:
            monthly[k]=i
    targets=sorted(set([position[specific],*monthly.values()]))
    replay.prep(targets)
    january=one_date(replay,position[specific],verify_app=True)
    rows=[one_date(replay,i,verify_app=(i==position[specific]))
          for i in monthly.values()]
    p=np.asarray([[x["forecast_up_10_pct"],x["forecast_down_10_pct"]]
                  for x in rows],dtype=float)/100.0
    y=np.asarray([[x["outcome_up_10_hit"],x["outcome_down_10_hit"]]
                  for x in rows],dtype=float)
    scores=np.mean((p-y)**2,axis=0)
    # Both sides can be touched in one interval.
    return {
        "symbol":symbol,"year":year,
        "example":january,
        "month_first_session_replay":rows,
        "annual_monthly_sample":{
            "n":len(rows),"up_events":int(y[:,0].sum()),
            "down_events":int(y[:,1].sum()),
            "brier_up":round(float(scores[0]),6),
            "brier_down":round(float(scores[1]),6),
            "brier_combined":round(float(scores.mean()),6),
        },
        "historical_price_source":"Yahoo chart raw daily high/low/close public retrospective backfill",
        "source_window":{"start":START,"end_exclusive":END,**guard},
        "input_sha256":hashlib.sha256(json.dumps(bars,separators=(",",":")).encode()).hexdigest(),
        "method":"original unmodified one_month_calibrated.estimate_probability replay",
        "source_pit_verified":False,"actual_2015_app_issue_log":False,
        "historical_date_replay_not_current_app_issue":True,
        "research_only":True,"production_admission":"BLOCKED",
        "live_app_modified":False,
        "note":"No model fitting on future 2015 labels; as-of training has only matured 21-session windows.",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol",choices=SYMBOLS,required=True)
    parser.add_argument("--as-of",default="2015-01-02")
    args=parser.parse_args()
    try:
        data=simulate(args.symbol,specific=args.as_of)
        print("HISTORICAL_2015_REPLAY_RESULT",json.dumps(data,ensure_ascii=False,sort_keys=True))
    except Exception as exc:
        print("HISTORICAL_2015_REPLAY_BLOCKED",json.dumps({
            "symbol":args.symbol,"error_type":type(exc).__name__,
            "detail":str(exc)[:300],"research_only":True,
            "source_pit_verified":False},ensure_ascii=False))
        raise


if __name__=="__main__":
    main()
