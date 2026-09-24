"""Compatibility entrypoint for the Naver-backed production market feed.

The current KOSPI and USD/KRW implementation lives in production_fixed.py.
This module intentionally does not override monitor.evaluate again; older
versions used KPI100 here and could accidentally replace the newer KOSPI logic.
"""

import production_fixed

app = production_fixed.app

# Re-export these names for production_naver_state.py compatibility.
NAVER_HEADERS = production_fixed.NAVER_HEADERS
NAVER_POLLING = production_fixed.NAVER_KOSPI_URL
