"""IndexAlert runtime with probability model 3.4 feature guardrails."""
import threading
import time

import briefing
import kospi_monthly
import monitor
import next_day_probability_v34 as next_day_probability
import production
import production_kpi100_mobile

app = production_kpi100_mobile.app

app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {
        "/briefings",
        "/next-day-probabilities",
        "/one-month-probabilities",
        "/stock-recommendations",
    }
]


@app.get("/briefings")
def market_briefings():
    return briefing.get_all(production.EXTRA_STATE)


@app.get("/next-day-probabilities")
def next_day_probabilities():
    return next_day_probability.get_all()


@app.get("/one-month-probabilities")
def one_month_probabilities():
    return kospi_monthly.get_all()


@app.on_event("startup")
def warm_market_features_v21():
    def _warm_briefings():
        try:
            expected = {"sp500", "ndx", "djdiv", "kospi100", "usdkrw"}
            for _ in range(30):
                if expected.issubset(set(production.EXTRA_STATE)):
                    break
                time.sleep(1)
            briefing.CACHE["updated"] = 0.0
            briefing.CACHE["items"] = {}
            payload = briefing.get_all(production.EXTRA_STATE)
            print("market briefings ready", len(payload.get("items", [])), flush=True)
        except Exception as exc:
            print("market briefings warmup failed", type(exc).__name__, str(exc), flush=True)

    def _warm_probability():
        try:
            payload = next_day_probability.refresh(True)
            summary = {
                key: {
                    "p": value.get("probability"),
                    "base": value.get("base_rate"),
                    "model": value.get("model_version"),
                    "served_strategy": value.get("current_strategy"),
                    "feature_strategy": value.get("feature_strategy"),
                    "feature_p": value.get("feature_candidate_probability"),
                    "gate": value.get("feature_gate_passed"),
                    "v34_brier": value.get("feature_audit_brier"),
                    "prev_brier": value.get("previous_audit_brier"),
                    "v34_first": value.get("feature_first_half_brier"),
                    "prev_first": value.get("previous_first_half_brier"),
                    "v34_second": value.get("feature_second_half_brier"),
                    "prev_second": value.get("previous_second_half_brier"),
                    "reliability": value.get("reliability"),
                }
                for key, value in payload.get("items", {}).items()
            }
            print("next-day probability 3.4 warmup", summary, flush=True)
        except Exception as exc:
            print("next-day probability 3.4 warmup failed", type(exc).__name__, str(exc), flush=True)

    def _warm_kospi_monthly():
        try:
            payload = kospi_monthly.refresh(True)
            item = payload.get("item") or {}
            print("kospi monthly warmup", {"as_of": item.get("as_of"), "up10": item.get("up_10_probability"), "down10": item.get("down_10_probability")}, flush=True)
        except Exception as exc:
            print("kospi monthly warmup failed", type(exc).__name__, str(exc), flush=True)

    threading.Thread(target=_warm_briefings, daemon=True).start()
    threading.Thread(target=_warm_probability, daemon=True).start()
    threading.Thread(target=_warm_kospi_monthly, daemon=True).start()

    job = monitor.scheduler.get_job("stock-recommendation-refresh")
    if job:
        monitor.scheduler.remove_job("stock-recommendation-refresh")
