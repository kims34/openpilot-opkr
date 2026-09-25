import threading
import time

import briefing
import production
import production_v14

# Preserve the full v1.6 production stack:
# - Naver-backed KOSPI
# - USD/KRW primary/fallback sources
# - history routes
# - 30-minute constituent mover refresh
app = production_v14.app

# Replace any stale briefing route on reload.
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) != "/briefings"
]


@app.get("/briefings")
def market_briefings():
    return briefing.get_all(production.EXTRA_STATE)


@app.on_event("startup")
def warm_market_briefings():
    def _warm():
        try:
            # The market monitor populates EXTRA_STATE immediately after startup.
            # Wait for all dashboard rows so the first 30-minute cache uses the
            # real previous-day movement rather than a temporary zero value.
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
    threading.Thread(target=_warm, daemon=True).start()
