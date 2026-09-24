import requests

import history_routes
import monitor
import production
import production_fixed
import production_naver

app = production_naver.app
_base_evaluate = monitor.evaluate


def _naver_market_state():
    try:
        r = requests.get(
            production_naver.NAVER_POLLING,
            headers={**production_naver.NAVER_HEADERS, "Accept": "application/json,*/*;q=0.8"},
            timeout=5,
        )
        r.raise_for_status()
        root = r.json()
        for area in ((root.get("result") or {}).get("areas") or []):
            for item in (area.get("datas") or []):
                if str(item.get("cd") or "").upper() == "KPI100":
                    ms = str(item.get("ms") or "").upper()
                    if ms == "OPEN":
                        return "REGULAR"
                    if ms:
                        return "CLOSED"
    except Exception as exc:
        print("kospi100 Naver market-state failed", type(exc).__name__, flush=True)
    return None


def _evaluate(index_id: str):
    result = _base_evaluate(index_id)
    if index_id == "kospi100" and "네이버 증권" in str(result.get("source") or ""):
        state = _naver_market_state()
        if state:
            result["market_state"] = state
            if index_id in production.EXTRA_STATE:
                production.EXTRA_STATE[index_id]["market_state"] = state
            print("kospi100 Naver market_state", state, flush=True)
    return result


monitor.evaluate = _evaluate

history_routes.attach(
    app,
    monitor,
    production_fixed._naver_kospi_quote,
    production_fixed._naver_usdkrw_quote,
)
