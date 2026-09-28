"""IndexAlert production v2.4: validated probability pipeline + extended sessions.

Order matters:
  daily close model -> pre-open futures -> extended-session overlay
  -> v3.9 official-open nowcast -> v4.0 completed-first-hour nowcast.
Each layer is exposed separately.  Extended-session values are explicitly
labelled as actual ETF pre/post trades or linked estimates and never rewrite
completed cash history.
"""
import extended_session_probability
import extended_session_kospi_fallback  # patches KOSPI off-hours continuity
import firsthour_nowcast_v40
import next_day_probability_v33 as next_day_probability
import open_nowcast_v39
import preopen_futures_v312_live as preopen_futures_v312
import probability_live_gate_patch  # installs prospective safety gates
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
    extended = extended_session_probability.enrich(preopen)
    after_open = open_nowcast_v39.enrich(extended)
    return firsthour_nowcast_v40.enrich(after_open)
