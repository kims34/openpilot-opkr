"""Historical same-date comparison: shipped monthly barrier model vs frozen IV paths.

Unmodified legacy application probability (replayed on a prefix) is the reference.
This is a retrospective public-history diagnostic, NOT as-issued or original PIT
evidence. Previously observed market periods are NOT untouched test holdouts.
No model selection, production change, or live order authority.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import time

import numpy as np

import next_day_probability as market
import research_monthly_direct_benchmark as benchmark
import research_monthly_touch_public_pilot as public
import research_monthly_touch_v1 as touch


def _hash(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()


def evaluate(symbol, window, days=126, paths=1024):
    if symbol not in ("SPY", "QQQ") or window not in ("2020", "2022", "2024", "recent"):
        raise ValueError("invalid prespecified study grid")
    rows, metadata = market.fetch_history(symbol, time.time())
    ohlc_map, missing = public.raw_daily(symbol)
    if any(d not in ohlc_map for d, _ in rows):
        raise touch.SourceQualityError("instrument daily OHLC missing: refuse imputation")
    ohlc = [(d, *ohlc_map[d]) for d, _ in rows]
    dates, prices, highs, lows = touch.validate_ohlc(rows, ohlc)
    iv_symbol = touch.EXPECTED_MACRO[symbol]
    iv_map, missing_iv = public.raw_daily("^" + iv_symbol)
    iv = {d: float(bar[2]) for d, bar in iv_map.items()}
    last = len(dates) - touch.HORIZON - 1
    limit = {"2020":"2020-06-30","2022":"2022-12-30","2024":"2024-12-31","recent":dates[last]}[window]
    while last >= 0 and dates[last] > limit:
        last -= 1
    targets = list(range(last - days + 1, last + 1))
    if len(targets) != days or min(targets) < 575:
        raise touch.SourceQualityError("insufficient history for identical comparator model")
    absent_iv = [dates[t] for t in targets if dates[t] not in iv]
    if absent_iv:
        raise touch.SourceQualityError(
            "asof IV missing on " + str(len(absent_iv)) + " required target days")
    replay = benchmark.FastServedReplay(rows, ohlc)
    replay.prep(targets)

    # Parity to the unmodified legacy app code on genuine market OHLC.
    last_fast = replay.estimate(targets[-1])
    last_original = replay.exact_app_estimate(targets[-1])
    parity = {}
    for field in ("up","down","up_selected_k","down_selected_k",
                  "up_blend_weight","down_blend_weight"):
        parity[field] = (last_fast[field] == last_original[field])
    if not all(parity.values()):
        raise touch.SourceQualityError("original production model parity FAILED")

    legacy, mc, half, y = [], [], [], []
    for t in targets:
        old = replay.estimate(t)
        raw = touch.simulate_touch(prices,t,iv[dates[t]],
                                  seed=20261116+t,paths=paths)
        base = np.array([old["up"],old["down"]])
        # Predeclared diagnostic policies: pure frozen Monte Carlo, and 50/50
        # mix with the actually served analogue+blended app probability.
        pure = np.round(raw*1000)/1000
        blend = np.round(((base+raw)/2)*1000)/1000
        legacy.append(base)
        mc.append(pure)
        half.append(blend)
        y.append(touch.touch_label(prices,highs,lows,t))
    legacy, mc, half, y = map(np.asarray,(legacy,mc,half,y))

    models = {}
    for name, predicted in (("pure_vix_vxn_mc",mc),("half_legacy_half_mc",half)):
        total = benchmark.metric(legacy,predicted,y)
        first = benchmark.metric(legacy[:days//2],predicted[:days//2],y[:days//2])
        second = benchmark.metric(legacy[days//2:],predicted[days//2:],y[days//2:])
        passes_research_gate = (
            total["gain_up"]>0 and total["gain_down"]>0
            and total["block_bootstrap_ci95_combined"][0]>0
            and first["gain_combined"]>0 and second["gain_combined"]>0
        )
        models[name] = {
            "total":total,
            "first_half_gain_combined":first["gain_combined"],
            "second_half_gain_combined":second["gain_combined"],
            "research_gate_passed":passes_research_gate,
            "production_admission":"BLOCKED",
        }
    return {
        "symbol":symbol, "window":window,
        "as_of_first":dates[targets[0]],"as_of_last":dates[targets[-1]],
        "latest_completed_source_session":metadata["as_of"],
        "n":len(targets),"horizon_sessions":touch.HORIZON,
        "source_quality":"PUBLIC_HISTORY_BACKFILL_NOT_AS_ISSUED_PIT",
        "macro":iv_symbol,
        "reference":"unmodified one_month_calibrated.estimate_probability per as-of prefix",
        "baseline_replay_verified_at":dates[targets[-1]],
        "baseline_parity":parity,
        "mean_served_legacy_up":float(legacy[:,0].mean()),
        "mean_served_legacy_down":float(legacy[:,1].mean()),
        "legacy_analog_active_up":sum(replay.estimate(t)["up_analog_enabled"] for t in targets),
        "legacy_analog_active_down":sum(replay.estimate(t)["down_analog_enabled"] for t in targets),
        "input_digest_sha256":{
            "instrument":_hash(ohlc),
            "iv_data":_hash(sorted(iv.items())),
        },
        "models":models,"production_admission":"BLOCKED",
        "real_trading_enabled":False,"app_changed":False,
        "holdout_is_unseen":False,
        "original_pit_vintage_verified":False,
        "significance_caution":"21-session events overlap; block bootstrap is not an independent prospective evaluation",
        "policy":"PROSPECTIVE_CONFIRMATION_REQUIRED",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol",choices=("SPY","QQQ"),required=True)
    parser.add_argument("--window",choices=("2020","2022","2024","recent"),required=True)
    parser.add_argument("--days",type=int,default=126)
    parser.add_argument("--paths",type=int,default=1024)
    opt=parser.parse_args()
    try:
        result=evaluate(opt.symbol,opt.window,opt.days,opt.paths)
        print("MONTHLY_DIRECT_RESULT",json.dumps(result,sort_keys=True))
    except Exception as exc:
        # All data issues block a result, never silently fall back to close
        # or to another instrument.
        print("MONTHLY_DIRECT_BLOCKED",json.dumps({
            "symbol":opt.symbol,"window":opt.window,
            "error_type":type(exc).__name__,"reason":str(exc)[:320],
            "production_admission":"BLOCKED","accuracy_claim":False,
        },sort_keys=True))
        raise


if __name__=="__main__":
    main()
