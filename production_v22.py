"""IndexAlert runtime: safe daily baseline + validated pre/open timing overlays."""
import next_day_probability_v33 as next_day_probability
import open_nowcast_v39
import preopen_futures_v312_live as preopen_futures_v312
import production_v20

app = production_v20.app

# production_v20 already installs the safe probability route. Replace only that
# route so the original daily forecast stays intact and timing-specific models
# are exposed as separate, auditable objects.
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) != "/next-day-probabilities"
]


@app.get("/next-day-probabilities")
def next_day_probabilities_v22():
    safe = next_day_probability.get_all()
    preopen = preopen_futures_v312.enrich(safe)
    return open_nowcast_v39.enrich(preopen)
