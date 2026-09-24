import production_naver

app = production_naver.app

_original_api = production_naver._naver_api_quote
_original_legacy = production_naver._naver_legacy_quote


def _legacy_first_quote():
    try:
        return _original_legacy()
    except Exception as exc:
        print("kospi100 Naver legacy failed", type(exc).__name__, flush=True)
    return _original_api()


# production_naver._evaluate resolves this global dynamically, so replacing the
# module helper switches only KOSPI100 quote priority without touching alerts.
production_naver._naver_quote = _legacy_first_quote
