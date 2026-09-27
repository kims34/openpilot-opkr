"""IndexAlert production v2.3: validated probability pipeline through v4.0.

Order matters:
  daily close model -> pre-open futures -> v3.9 official-open nowcast
  -> v4.0 completed-first-hour nowcast.
Each later layer is exposed separately and never rewrites the earlier estimate.
Prospective Brier gates keep promoted v3.9/v4.0 models in shadow evaluation and
automatically serve the exact previous-stage probability only when live paired
Brier evidence shows statistically significant degradation.
"""
import firsthour_nowcast_v40
import next_day_probability_v33 as next_day_probability
import open_nowcast_v39
import preopen_futures_v312_live as preopen_futures_v312
import probability_live_gate_patch  # installs safety gates after frozen modules load
import production_v20

app = production_v20.app
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) != "/next-day-probabilities"
]


@app.get("/next-day-probabilities")
def next_day_probabilities():
    safe = next_day_probability.get_all()
    preopen = preopen_futures_v312.enrich(safe)
    after_open = open_nowcast_v39.enrich(preopen)
    return firsthour_nowcast_v40.enrich(after_open)
