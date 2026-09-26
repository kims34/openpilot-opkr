import history_routes
import monitor
import production_naver

app = production_naver.app
_base_evaluate = monitor.evaluate


def _evaluate(index_id: str):
    # production_naver now owns the KOSPI100 quote/state logic. Keep this layer
    # as a compatibility pass-through for the rest of the production stack.
    return _base_evaluate(index_id)


monitor.evaluate = _evaluate

history_routes.attach(
    app,
    monitor,
    production_naver._naver_kpi100_history_quote,
    production_naver.production_fixed._naver_usdkrw_quote,
)
