import threading
import time

import briefing
import next_day_probability_v31 as next_day_probability
import production
import production_v14

# Preserve the full production stack:
# - Naver-backed KOSPI
# - USD/KRW primary/fallback sources
# - history routes
# - constituent mover refresh
# - detailed market briefing
# - validated next-trading-day probability model 3.1
app = production_v14.app

# Replace stale routes on reload.
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {"/briefings", "/next-day-probabilities"}
]


@app.get("/briefings")
def market_briefings():
    return briefing.get_all(production.EXTRA_STATE)


@app.get("/next-day-probabilities")
def next_day_probabilities():
    return next_day_probability.get_all()


@app.on_event("startup")
def warm_market_features():
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
            summary = [(x.get("id"), x.get("category"), x.get("text")) for x in payload.get("items", [])]
            print("market briefings ready", summary, flush=True)
        except Exception as exc:
            print("market briefings warmup failed", type(exc).__name__, str(exc), flush=True)

    def _warm_probability():
        try:
            payload = next_day_probability.refresh(True)
            summary = {
                key: {
                    "p": value.get("probability"),
                    "base": value.get("base_rate"),
                    "strategy": value.get("current_strategy"),
                    "skill": value.get("backtest_skill"),
                    "reliability": value.get("reliability"),
                }
                for key, value in payload.get("items", {}).items()
            }
            print("next-day probability warmup", summary, flush=True)
        except Exception as exc:
            print("next-day probability warmup failed", type(exc).__name__, str(exc), flush=True)

    threading.Thread(target=_warm_briefings, daemon=True).start()
    threading.Thread(target=_warm_probability, daemon=True).start()
