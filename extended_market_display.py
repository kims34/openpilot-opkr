"""Extended-session display overlay for IndexAlert market cards.

Regular-session ATHs/cash history remain untouched. Off-hours cards prefer
actual ETF pre/post trades and use clearly-labelled linked estimates only when
the cash/ETF market itself is not trading. KOSPI regular cash comes from Naver;
off-hours KOSPI is always explicitly an estimate.
"""
from __future__ import annotations

import math
import time

import extended_session_probability as esp
import monitor
import production

US_SYMBOLS = {"sp500": "SPY", "ndx": "QQQ", "djdiv": "SCHD"}
_INSTALLED = False


def _previous_close(index_id: str, fallback: float) -> float:
    extra = production.EXTRA_STATE.get(index_id) or {}
    try:
        value = float(extra.get("previous_close") or 0)
        if math.isfinite(value) and value > 0:
            return value
    except Exception:
        pass
    return fallback


def _update_extra(index_id: str, value: float, value_ts: int, source: str, ath: float, previous: float, market_state: str):
    extra = dict(production.EXTRA_STATE.get(index_id) or {})
    dd = (value / ath - 1.0) * 100.0 if ath > 0 else None
    day_change = value - previous if previous > 0 else 0.0
    day_change_pct = (value / previous - 1.0) * 100.0 if previous > 0 else 0.0
    extra.update(
        day_change=day_change,
        day_change_percent=day_change_pct,
        drawdown=dd,
        market_state=market_state,
        value_ts=int(value_ts or 0),
        extended_display=True,
        extended_source=source,
    )
    production.EXTRA_STATE[index_id] = extra
    return extra, dd


def install():
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    base_evaluate = monitor.evaluate

    def _evaluate(index_id: str):
        out = base_evaluate(index_id)
        now = time.time()

        if index_id in US_SYMBOLS:
            # Regular session always uses the ETF's actual regular-session price.
            if out.get("market_state") == "REGULAR":
                return out
            try:
                signal = esp._us_extended_signal(index_id, US_SYMBOLS[index_id], now)
                value = float(signal["estimated_price"])
                value_ts = int(signal.get("data_ts") or out.get("value_ts") or out.get("cash_ts") or 0)
                if not math.isfinite(value) or value <= 0:
                    return out
                ath = float(out.get("ath") or 0)
                previous = _previous_close(index_id, float(out.get("cash") or value))
                session = str(signal.get("session") or "OFF_HOURS")
                source = str(signal.get("source") or "시간외 연동")
                extra, dd = _update_extra(index_id, value, value_ts, source, ath, previous, session)
                # The linked estimate can cross a threshold after the last actual
                # ETF trade. Delivery de-duplication in monitor prevents repeats.
                if ath > 0 and dd is not None:
                    monitor.enqueue_crossings(index_id, ath, dd, source)
                monitor.save_state(index_id, ath, float(out.get("cash") or value), value, source)
                return {
                    **out,
                    "value": value,
                    "drawdown": dd,
                    "source": source,
                    "market_state": session,
                    "value_ts": value_ts,
                    "extended_estimate": not bool(signal.get("actual_extended_trade")),
                    "actual_extended_trade": bool(signal.get("actual_extended_trade")),
                    **extra,
                }
            except Exception as exc:
                print("extended card display unavailable", index_id, type(exc).__name__, str(exc), flush=True)
                return out

        if index_id == "kospi100":
            # Naver KOSPI is authoritative while Korea cash is open. Outside the
            # cash session, show a linked estimate but never treat it as a cash ATH.
            if out.get("market_state") == "REGULAR":
                return out
            try:
                signal = esp._kospi_proxy_signal(now)
                value = float(signal["estimated_price"])
                value_ts = int(signal.get("data_ts") or out.get("value_ts") or out.get("cash_ts") or 0)
                if not math.isfinite(value) or value <= 0:
                    return out
                ath = float(out.get("ath") or 0)
                previous = _previous_close(index_id, float(out.get("cash") or value))
                session = str(signal.get("session") or "OFF_HOURS_PROXY")
                source = str(signal.get("source") or "KOSPI 시간외 연동 추정")
                extra, dd = _update_extra(index_id, value, value_ts, source, ath, previous, session)
                monitor.save_state(index_id, ath, float(out.get("cash") or value), value, source)
                return {
                    **out,
                    "value": value,
                    "drawdown": dd,
                    "source": source,
                    "market_state": session,
                    "value_ts": value_ts,
                    "extended_estimate": True,
                    "actual_extended_trade": False,
                    **extra,
                }
            except Exception as exc:
                print("kospi extended card display unavailable", type(exc).__name__, str(exc), flush=True)
                return out

        return out

    monitor.evaluate = _evaluate
    print("extended market-card display overlay active", flush=True)
