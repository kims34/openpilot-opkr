"""IndexAlert production v3.1: clarify U.S. closed-session proxy labels.

No pricing logic changes.  Regular session remains actual ETF trades; pre/post
remain actual ETF extended-hours trades when fresh.  Futures-linked values are
used only when the ETF itself is closed, and are labeled accordingly.
"""
from __future__ import annotations

import extended_session_probability as esp
import production_v28

app = production_v28.app
_original_us_extended_signal = esp._us_extended_signal


def _us_extended_signal_clear_label(index_id: str, symbol: str, now: float):
    signal = dict(_original_us_extended_signal(index_id, symbol, now))
    if not bool(signal.get("actual_extended_trade")):
        source = str(signal.get("source") or "")
        if "심야 연동 추정" in source:
            source = source.replace("심야 연동 추정", "ETF 휴장시간 선물연동 추정")
        elif "선물연동" not in source:
            source = f"{symbol} ETF 휴장시간 선물연동 추정"
        signal["source"] = source
        signal["session"] = "ETF_CLOSED_PROXY"
    return signal


esp._us_extended_signal = _us_extended_signal_clear_label
