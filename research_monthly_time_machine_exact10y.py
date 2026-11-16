"""Exact 10y-as-of 2015 IndexAlert one-month replay, calling original app code.

Historical public Yahoo bars are backfilled, NOT authenticated as-issued PIT.
At each as-of date, the model receives *only* that date's preceding ten years
of daily price data. The next 21 complete exchange sessions are labels only.
No model deployment, trading, price-provider fallback, or data imputation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, timedelta

import numpy as np
import one_month_calibrated as existing_app
from research_monthly_time_machine_2015 import historical_bars,exchange_session_guard

START = "2004-12-01"
END = "2016-03-01"
HORIZON = 21


def _date_years_earlier(value, years=10):
    d=date.fromisoformat(value)
    try:
        return d.replace(year=d.year-years).isoformat()
    except ValueError:
        return d.replace(year=d.year-years,day=28).isoformat()


def one_asof(bars, t):
    if t+HORIZON>=len(bars):
        raise ValueError("future 21 sessions not completed")
    d=bars[t][0]
    window_start=_date_years_earlier(d)
    # Preserves rolling 10-year lookback: as-of never sees a later close.
    prefix=[r for r in bars[:t+1] if r[0]>=window_start]
    if len(prefix)<900:
        raise ValueError("not enough 10-year past data")
    close_rows=[(day,c) for day,h,l,c in prefix]
    value=existing_app.estimate_probability(close_rows,prefix)
    if value.get("price_basis")!="daily_high_low" or value.get("as_of")!=d:
        raise ValueError("existing app model input contract violated")
    anchor=prefix[-1][3]
    future=bars[t+1:t+1+HORIZON]
    high=max(float(r[1]) for r in future)
    low=min(float(r[2]) for r in future)
    up=int(high>=anchor*1.10)
    down=int(low<=anchor*.90)
    up_prob=value["up_10_probability"]/100.0
    down_prob=value["down_10_probability"]/100.0
    return {
        "as_of":d,"ten_year_lookback_from":window_start,
        "actual_input_sessions":len(prefix),
        "target_first_session":future[0][0],
        "target_last_session":future[-1][0],
        "anchor":round(float(anchor),4),
        "up_10_target":round(float(anchor*1.10),4),
        "down_10_target":round(float(anchor*.90),4),
        "forecast_up_10_pct":value["up_10_probability"],
        "forecast_down_10_pct":value["down_10_probability"],
        "actual_21_session_high":round(high,4),
        "actual_21_session_low":round(low,4),
        "max_gain_pct":round((high/anchor-1)*100,3),
        "max_loss_pct":round((low/anchor-1)*100,3),
        "up_hit":up,"down_hit":down,
        "brier_up":round((up_prob-up)**2,6),
        "brier_down":round((down_prob-down)**2,6),
        "legacy_model_method":value["method"],
        "legacy_analog_blend_up":value["blend_weight_up"],
        "legacy_analog_blend_down":value["blend_weight_down"],
    }


def replay(symbol, example="2015-01-02", monthly=True):
    bars=historical_bars(symbol,start=START,end=END)
    guard=exchange_session_guard(bars)
    datepos={r[0]:i for i,r in enumerate(bars)}
    if example not in datepos:
        raise ValueError("exact forecast as-of date not found")
    first_of_month={}
    for i,bar in enumerate(bars):
        d=bar[0]
        if d.startswith("2015"):
            first_of_month.setdefault(d[:7],i)
    if len(first_of_month)!=12:
        raise ValueError("2015 monthly sessions missing")
    example_result=one_asof(bars,datepos[example])
    rows=[one_asof(bars,i) for i in first_of_month.values()] if monthly else []
    metric=None
    if rows:
        outcomes=np.array([[r["up_hit"],r["down_hit"]] for r in rows])
        forecast=np.array([[r["forecast_up_10_pct"],r["forecast_down_10_pct"]]
                           for r in rows])/100
        errors=np.mean((forecast-outcomes)**2,axis=0)
        metric={"count":len(rows),"up_event_count":int(outcomes[:,0].sum()),
                "down_event_count":int(outcomes[:,1].sum()),
                "brier_up":round(float(errors[0]),6),
                "brier_down":round(float(errors[1]),6),
                "brier_average":round(float(np.mean(errors)),6)}
    return {
        "symbol":symbol,
        "example":example_result,
        "monthly_first_session_2015":rows,
        "annual_monthly_metrics":metric,
        "source_session_coverage":guard,
        "full_source_sha256":hashlib.sha256(json.dumps(
            bars,separators=(",",":")).encode()).hexdigest(),
        "source":"Yahoo historical unadjusted OHLC backfill, no original PIT vintage",
        "model":"unaltered one_month_calibrated.estimate_probability, rolling 10-year as-of input",
        "model_source":"IndexAlert app restore branch; no real 2015-issued record",
        "as_issued_historical_source_verified":False,
        "historical_forward_data_used_in_prediction":False,
        "future_used_only_for_21_session_label":True,
        "production_admission":"BLOCKED","production_app_untouched":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--symbol",choices=("SPY","QQQ"),required=True)
    p.add_argument("--example",default="2015-01-02")
    p.add_argument("--only-example",action="store_true")
    a=p.parse_args()
    result=replay(a.symbol,a.example,monthly=not a.only_example)
    print("HISTORICAL_2015_EXACT10Y_RESULT",json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
