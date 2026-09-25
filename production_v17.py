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
