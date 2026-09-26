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

        # The current Naver endpoint returns the KOSPI composite directly as
        # datas[0] (itemCode/symbolCode = KOSPI). Keep compatibility with any
        # older nested polling response as well, but never use KPI100 here.
        direct = root.get("datas") or []
        items = list(direct)
        for area in ((root.get("result") or {}).get("areas") or []):
            items.extend(area.get("datas") or [])

        for item in items:
            code = str(item.get("itemCode") or item.get("symbolCode") or item.get("cd") or "").upper()
            if code == "KOSPI":
                ms = str(item.get("marketStatus") or item.get("ms") or "").upper()
                if ms in {"OPEN", "REGULAR"}:
                    return "REGULAR"
                if ms:
                    return "CLOSED"
    except Exception as exc:
        print("kospi Naver market-state failed", type(exc).__name__, flush=True)
    return None


def _evaluate(index_id: str):
    result = _base_evaluate(index_id)
    # The historical internal id is retained for installed-client compatibility,
    # but it now represents KOSPI only. No KOSPI100 quote is used.
    if index_id == "kospi100" and str(result.get("name") or "").upper() == "KOSPI":
        state = _naver_market_state()
        if state:
            result["market_state"] = state
            if index_id in production.EXTRA_STATE:
                production.EXTRA_STATE[index_id]["market_state"] = state
            print("kospi Naver market_state", state, flush=True)
    return result


monitor.evaluate = _evaluate

history_routes.attach(
    app,
    monitor,
    production_fixed._naver_kospi_quote,
    production_fixed._naver_usdkrw_quote,
)
