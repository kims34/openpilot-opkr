"""IndexAlert runtime: safe 3.3/3.2 pre-open forecast + separate v3.9 after-open nowcast."""
import next_day_probability_v33 as next_day_probability
import open_nowcast_v39
import production_v20

app = production_v20.app

# production_v20 already installs the safe probability route. Replace only that
# route so the existing payload remains intact and gains a separate after_open
# object. No other market/alert routes are changed.
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) != "/next-day-probabilities"
]


@app.get("/next-day-probabilities")
def next_day_probabilities_v22():
    safe = next_day_probability.get_all()
    return open_nowcast_v39.enrich(safe)
