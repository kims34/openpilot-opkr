"""Compatibility layer for the legacy Android wire id ``kospi100``.

The wire id is kept so installed clients do not break, but it represents the
KOSPI composite (^KS11), not the KOSPI100 sub-index.  Older versions of this
module accidentally remapped the id back to KPI100; production now restores the
composite definition and clears any persisted KPI100 state once.
"""
import history_routes
import monitor
import production_fixed
import production_v14

app = production_v14.app
_base_init_db = monitor.init_db
_base_evaluate = monitor.evaluate

monitor.RULES["kospi100"] = {
    "name": "KOSPI",
    "cash": "^KS11",
    "proxy": None,
    "levels": [],
    "regular_label": "KOSPI · 네이버 증권",
    "proxy_label": "KOSPI · 네이버 증권",
    "extended": False,
    "timezone": "Asia/Seoul",
}


def _init_db():
    _base_init_db()
    with monitor.db() as con:
        if not con.execute("SELECT 1 FROM migrations WHERE name='kospi-composite-restore-v9'").fetchone():
            # A previous release may have persisted KOSPI100 values under this
            # legacy id.  They cannot seed KOSPI composite ATH/state.
            con.execute("DELETE FROM index_state WHERE id='kospi100'")
            con.execute("DELETE FROM fired WHERE index_id='kospi100'")
            con.execute("DELETE FROM deliveries WHERE index_id='kospi100'")
            con.execute("INSERT INTO migrations(name) VALUES('kospi-composite-restore-v9')")


monitor.init_db = _init_db


def _evaluate(index_id: str):
    if index_id == "kospi100":
        return production_fixed._evaluate_kospi(index_id)
    return _base_evaluate(index_id)


monitor.evaluate = _evaluate

# production_naver_state attached an older history route earlier in the import
# chain. Replace it so the legacy id also charts the KOSPI composite.
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) != "/history/{index_id}"
]
history_routes.attach(
    app,
    monitor,
    production_fixed._naver_kospi_quote,
    production_fixed._naver_usdkrw_quote,
)
