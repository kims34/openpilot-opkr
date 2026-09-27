"""Extended-session probability overlay for SPY, QQQ, SCHD and KOSPI.

This layer never rewrites completed cash history.  It estimates how currently
tradable extended-session instruments are changing the next-session opening
gap, then applies only a bounded fraction of the validated opening-gap signal.
Actual ETF pre/post trades are preferred.  When the ETF itself is closed,
index futures are used only as a clearly-labelled linked estimate.

KOSPI cash does not trade overnight.  Its overnight signal is therefore marked
as an estimate and uses EWY (including US pre/post) adjusted by USD/KRW.  The
KOSPI gap relationship itself is promoted only if a causal 252-session Brier
audit beats the rolling base rate overall and in both chronological halves.
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import requests

import kospi_nextday_probability
import monitor
import next_day_probability as us_base
import open_nowcast_v39
import production_fixed

MODEL_VERSION = "4.1-extended-session"
US_SYMBOLS = {"sp500": "SPY", "ndx": "QQQ", "djdiv": "SCHD"}
US_FUTURES = {"sp500": ("ES=F",), "ndx": ("NQ=F",), "djdiv": ("ES=F", "YM=F")}
NY = ZoneInfo("America/New_York")
SEOUL = ZoneInfo("Asia/Seoul")


def _fresh(ts: int, now: float, limit_minutes: int) -> bool:
    return bool(ts and -300 <= now - float(ts) <= limit_minutes * 60)


def _regular_anchor(symbol: str):
    result = monitor.yahoo_result(symbol, "5d", "5m", False)
    points = monitor.series(result)
    if not points:
        raise ValueError("정규장 기준가 없음")
    return points[-1]


def _future_ratio(proxy: str, anchor_ts: int, now: float):
    ratio, p_now, p_anchor, p_anchor_ts, p_latest_ts = monitor.proxy_ratio_from_cash_close(proxy, anchor_ts)
    if not _fresh(int(p_latest_ts or 0), now, 60):
        raise ValueError("선물 최신 체결 지연")
    if not math.isfinite(ratio) or ratio <= 0 or abs(ratio - 1.0) > 0.15:
        raise ValueError("선물 연동비율 이상")
    return ratio, int(p_latest_ts), p_now


def _us_extended_signal(index_id: str, symbol: str, now: float):
    anchor_ts, anchor_price = _regular_anchor(symbol)
    live, _, state, live_ts = monitor.current(symbol)

    # Prefer the ETF's own actual extended-hours trade whenever it is active.
    if state in {"PRE", "POST"} and _fresh(live_ts, now, 35):
        ratio = live / anchor_price
        if 0.85 <= ratio <= 1.15:
            return {
                "estimated_price": live,
                "move": ratio - 1.0,
                "source": f"{symbol} 실제 {'프리마켓' if state == 'PRE' else '애프터마켓'}",
                "session": state,
                "data_ts": int(live_ts),
                "actual_extended_trade": True,
            }

    ratios = []
    latest_ts = 0
    proxies = []
    for proxy in US_FUTURES[index_id]:
        try:
            ratio, ts, _ = _future_ratio(proxy, anchor_ts, now)
            ratios.append(ratio)
            latest_ts = max(latest_ts, ts)
            proxies.append(proxy)
        except Exception:
            continue
    if not ratios:
        raise ValueError("시간외 연동 시세 없음")
    ratio = float(np.mean(ratios))
    return {
        "estimated_price": anchor_price * ratio,
        "move": ratio - 1.0,
        "source": f"{symbol} 심야 연동 추정 · {'/'.join(proxies)}",
        "session": "OVERNIGHT_PROXY",
        "data_ts": latest_ts,
        "actual_extended_trade": False,
    }


def _us_gap_candidate(symbol: str, item: dict, estimated_open: float):
    rows, meta = us_base.fetch_history(symbol)
    dates = [d for d, _ in rows]
    closes = [p for _, p in rows]
    ohlc = open_nowcast_v39._daily_ohlc(symbol)
    hist_dates = [d for d in dates if d in ohlc and ohlc[d].get("close") is not None]
    if hist_dates != dates:
        raise ValueError("시간외 확률 OHLC 거래일 누락")
    opens = [ohlc[d]["open"] for d in dates]
    raw_closes = [ohlc[d]["close"] for d in dates]
    max_basis_error = max(abs(r / c - 1.0) for r, c in zip(raw_closes, closes))
    if max_basis_error > 0.002:
        raise ValueError("시간외 확률 가격기준 불일치")
    config = open_nowcast_v39.CONFIG_BY_SYMBOL[symbol]
    fitted = open_nowcast_v39._fit_live(
        opens,
        closes,
        dates,
        item["target_date"],
        estimated_open,
        item["probability"],
        config,
    )
    return fitted


def _reliability_weight(signal: dict, item: dict, now: float) -> float:
    target_open = float(item.get("target_open") or 0)
    hours = max(0.0, (target_open - now) / 3600.0) if target_open > now else 0.0
    if signal.get("actual_extended_trade"):
        if signal.get("session") == "PRE":
            if hours <= 1.0:
                return 0.90
            if hours <= 4.0:
                return 0.80
            return 0.65
        return 0.50  # after-market, still far from the next open
    if hours <= 1.0:
        return 0.75
    if hours <= 4.0:
        return 0.65
    return 0.45


def _enrich_us(index_id: str, item: dict, now: float):
    symbol = US_SYMBOLS[index_id]
    target_open = int(item.get("target_open") or 0)
    target_close = int(item.get("target_close") or 0)
    if item.get("error") or item.get("probability") is None or not target_open or not target_close:
        return {"available": False, "status": "기본 확률 확인 중", "model_version": MODEL_VERSION}

    # During the regular target session, the official-open/first-hour models
    # are more informative and should be shown instead of a synthetic gap.
    if target_open <= now < target_close:
        return {
            "available": False,
            "status": "정규장 진행 중 · 개장후/첫 1시간 확률 우선",
            "model_version": MODEL_VERSION,
            "target_date": item.get("target_date"),
        }

    signal = _us_extended_signal(index_id, symbol, now)
    fitted = _us_gap_candidate(symbol, item, signal["estimated_price"])
    baseline = float(item["probability"])
    synthetic = float(fitted["probability"])
    raw_adjustment = synthetic - baseline
    weight = _reliability_weight(signal, item, now)
    adjustment = float(np.clip(raw_adjustment * weight, -7.5, 7.5))
    served = float(np.clip(baseline + adjustment, 5.0, 95.0))
    return {
        "available": True,
        "probability": round(served, 1),
        "baseline_probability": round(baseline, 1),
        "synthetic_open_probability": round(synthetic, 1),
        "adjustment_pp": round(adjustment, 1),
        "extended_move_percent": round(float(signal["move"]) * 100.0, 2),
        "estimated_open_price": round(float(signal["estimated_price"]), 4),
        "source": signal["source"],
        "session": signal["session"],
        "data_ts": signal["data_ts"],
        "actual_extended_trade": bool(signal["actual_extended_trade"]),
        "reliability_weight": weight,
        "estimated": not bool(signal["actual_extended_trade"]),
        "status": "시간외 거래 반영" if signal["actual_extended_trade"] else "시간외 연동 추정 반영",
        "target_date": item.get("target_date"),
        "model_version": MODEL_VERSION,
        "method": "시간외 가격을 다음 시가의 선행 신호로 사용하되 검증된 시가갭 보정의 일부만 반영",
    }


def _kospi_daily_ohlc():
    r = requests.get(
        "https://query1.finance.yahoo.com/v8/finance/chart/%5EKS11",
        params={"range": "10y", "interval": "1d", "includePrePost": "false", "events": "div,splits"},
        headers={"User-Agent": "Mozilla/5.0 IndexAlert/4.1"},
        timeout=20,
    )
    r.raise_for_status()
    result = (r.json().get("chart", {}).get("result") or [None])[0]
    if not result:
        raise ValueError("KOSPI OHLC 없음")
    ts = result.get("timestamp") or []
    q = (result.get("indicators", {}).get("quote") or [{}])[0]
    opens = q.get("open") or []
    closes = q.get("close") or []
    out = []
    for t, op, cl in zip(ts, opens, closes):
        if op is None or cl is None or float(op) <= 0 or float(cl) <= 0:
            continue
        day = datetime.fromtimestamp(int(t), timezone.utc).astimezone(SEOUL).date().isoformat()
        out.append((day, float(op), float(cl)))
    return out


def _analog_probability(gaps, outcomes, live_gap, end, window=756, prior_weight=80.0):
    start = max(0, end - window)
    g = np.asarray(gaps[start:end], float)
    y = np.asarray(outcomes[start:end], float)
    if len(y) < 126:
        raise ValueError("KOSPI 시가갭 학습표본 부족")
    base = float(y.mean())
    scale = max(0.0035, float(np.nanmedian(np.abs(g - np.nanmedian(g)))) * 1.5)
    weights = np.exp(-np.abs(g - live_gap) / scale)
    probability = (float(np.dot(weights, y)) + prior_weight * base) / (float(weights.sum()) + prior_weight)
    return probability, base


def _kospi_gap_model(live_gap: float):
    rows = _kospi_daily_ohlc()
    gaps, outcomes = [], []
    for i in range(1, len(rows)):
        prev_close = rows[i - 1][2]
        op = rows[i][1]
        cl = rows[i][2]
        gaps.append(op / prev_close - 1.0)
        outcomes.append(1.0 if cl > prev_close else 0.0)
    n = len(outcomes)
    if n < 900:
        raise ValueError("KOSPI 시가갭 이력 부족")

    # Causal untouched-style recent audit. Candidate must beat rolling base in
    # the whole audit and both chronological halves before live use.
    audit_start = n - 252
    candidate_losses, base_losses = [], []
    for t in range(audit_start, n):
        p, b = _analog_probability(gaps, outcomes, gaps[t], t)
        y = outcomes[t]
        candidate_losses.append((p - y) ** 2)
        base_losses.append((b - y) ** 2)
    mid = len(candidate_losses) // 2
    cand = float(np.mean(candidate_losses))
    base_brier = float(np.mean(base_losses))
    first_gain = float(np.mean(base_losses[:mid]) - np.mean(candidate_losses[:mid]))
    second_gain = float(np.mean(base_losses[mid:]) - np.mean(candidate_losses[mid:]))
    validated = cand < base_brier and first_gain >= 0.0 and second_gain >= 0.0

    p_live, b_live = _analog_probability(gaps, outcomes, live_gap, n)
    return {
        "candidate": p_live,
        "historical_base": b_live,
        "validated": validated,
        "validation_count": 252,
        "candidate_brier": cand,
        "baseline_brier": base_brier,
        "first_half_gain": first_gain,
        "second_half_gain": second_gain,
    }


def _kospi_proxy_signal(now: float):
    current, previous, _, _, _, _, market_state = production_fixed._naver_kospi_quote()
    if market_state == "REGULAR":
        raise ValueError("KOSPI 정규장 진행 중")

    ewy_now, ewy_prev, ewy_state, ewy_ts = monitor.current("EWY")
    fx_now, fx_prev, _, fx_ts = monitor.current("KRW=X")
    if not _fresh(ewy_ts, now, 45):
        raise ValueError("EWY 야간 프록시 체결 대기")
    if not _fresh(fx_ts, now, 120):
        raise ValueError("환율 연동값 지연")
    if min(ewy_prev, fx_prev, previous, current) <= 0:
        raise ValueError("KOSPI 야간 프록시 기준가 이상")

    # EWY is USD-denominated. Multiplying by USD/KRW approximates KRW equity
    # movement. Subtract today's already-realized KOSPI regular return so the
    # overlay only carries incremental information after the cash close.
    ewy_krw_move = (ewy_now / ewy_prev) * (fx_now / fx_prev) - 1.0
    cash_day_move = current / previous - 1.0
    incremental = float(np.clip(ewy_krw_move - cash_day_move, -0.05, 0.05))
    return {
        "cash_close": current,
        "move": incremental,
        "estimated_price": current * (1.0 + incremental),
        "source": f"KOSPI 야간 연동 추정 · EWY({ewy_state}) + USD/KRW",
        "session": f"EWY_{ewy_state}",
        "data_ts": min(int(ewy_ts), int(fx_ts)),
    }


def _enrich_kospi(item: dict, now: float):
    if item.get("error") or item.get("probability") is None:
        return {"available": False, "status": "KOSPI 기본 확률 확인 중", "model_version": MODEL_VERSION}
    target_open = int(item.get("target_open") or 0)
    target_close = int(item.get("target_close") or 0)
    if target_open <= now < target_close:
        return {
            "available": False,
            "status": "KOSPI 정규장 진행 중 · 현물지수 우선",
            "model_version": MODEL_VERSION,
            "target_date": item.get("target_date"),
        }

    signal = _kospi_proxy_signal(now)
    gap = float(signal["move"])
    model = _kospi_gap_model(gap)
    baseline = float(item["probability"])
    if model["validated"]:
        analog_adjustment = (model["candidate"] - model["historical_base"]) * 100.0
    else:
        analog_adjustment = 0.0
    # EWY+FX is a proxy rather than the actual KOSPI200 night-futures print, so
    # cap its influence more tightly than an actual ETF pre/post trade.
    adjustment = float(np.clip(analog_adjustment * 0.50, -5.0, 5.0))
    served = float(np.clip(baseline + adjustment, 5.0, 95.0))
    return {
        "available": True,
        "probability": round(served, 1),
        "baseline_probability": round(baseline, 1),
        "adjustment_pp": round(adjustment, 1),
        "extended_move_percent": round(gap * 100.0, 2),
        "estimated_open_price": round(float(signal["estimated_price"]), 2),
        "source": signal["source"],
        "session": signal["session"],
        "data_ts": signal["data_ts"],
        "actual_extended_trade": False,
        "estimated": True,
        "status": "KOSPI 시간외 연동 추정 반영",
        "target_date": item.get("target_date"),
        "model_version": MODEL_VERSION,
        "gap_model_validated": bool(model["validated"]),
        "gap_validation_count": model["validation_count"],
        "gap_candidate_brier": model["candidate_brier"],
        "gap_baseline_brier": model["baseline_brier"],
        "method": "완료 KOSPI 종가 확률 + EWY·환율 야간 연동 + KOSPI 자체 시가갭 Brier 게이트",
    }


def enrich(payload: dict, now: float | None = None):
    now = time.time() if now is None else float(now)
    out = dict(payload)
    items = {k: dict(v) for k, v in (payload.get("items") or {}).items()}

    # Add KOSPI as a fourth next-session probability card.
    try:
        items["kospi100"] = kospi_nextday_probability.get_item()
    except Exception as exc:
        items["kospi100"] = {"symbol": "^KS11", "error": "KOSPI 다음 거래일 확률 계산 중"}
        print("kospi probability merge unavailable", type(exc).__name__, flush=True)

    for index_id, item in list(items.items()):
        try:
            if index_id in US_SYMBOLS:
                item["extended_session"] = _enrich_us(index_id, item, now)
            elif index_id == "kospi100":
                item["extended_session"] = _enrich_kospi(item, now)
        except Exception as exc:
            label = "KOSPI" if index_id == "kospi100" else US_SYMBOLS.get(index_id, index_id)
            item["extended_session"] = {
                "available": False,
                "status": "시간외 체결/연동값 대기",
                "model_version": MODEL_VERSION,
                "target_date": item.get("target_date"),
            }
            print("extended session unavailable", label, type(exc).__name__, str(exc), flush=True)
        items[index_id] = item

    out["items"] = items
    out["extended_session_model_version"] = MODEL_VERSION
    return out
