"""Strict offline extractor for Kiwoom REAL type 00 order/fill frames.

Input is an already parsed WebSocket frame. This module opens no network and
authenticates no source. It preserves raw FID strings for protected account and
broker-native execution binding downstream.
"""
from kiwoom_realtime_order_fill_subscription_contract import TYPE00_FIELDS

class KiwoomType00FrameError(ValueError):
    pass

def extract_type00_events(message) -> tuple[dict, ...]:
    if type(message) is not dict or str(message.get("trnm", "")).upper() != "REAL":
        raise KiwoomType00FrameError("TYPE00_FRAME_INVALID")
    data = message.get("data")
    if type(data) is not list:
        raise KiwoomType00FrameError("TYPE00_FRAME_INVALID")
    events = []
    for entry in data:
        if type(entry) is not dict:
            raise KiwoomType00FrameError("TYPE00_FRAME_INVALID")
        if str(entry.get("type", "")).strip() != "00":
            continue
        values = entry.get("values")
        if type(values) is not dict:
            raise KiwoomType00FrameError("TYPE00_FRAME_INVALID")
        if any(type(k) is not str or k not in TYPE00_FIELDS for k in values):
            raise KiwoomType00FrameError("TYPE00_UNKNOWN_FIELD")
        if any(type(v) is not str or len(v) > 4096 for v in values.values()):
            raise KiwoomType00FrameError("TYPE00_VALUE_INVALID")
        events.append(dict(values))
    return tuple(events)

def summarize_type00_frame(message) -> dict:
    events = extract_type00_events(message)
    return {
        "mode": "OFFLINE_KIWOOM_TYPE00_FRAME_EXTRACTION",
        "type00_event_count": len(events),
        "execution_id_present_count": sum(bool(row.get("909")) for row in events),
        "network_request_attempted": False,
        "websocket_opened": False,
        "source_origin_authenticated": False,
        "trading_date_origin_attested": False,
        "broker_native_execution_id_capture_tested": False,
        "genuine_live_provenance_verified": False,
        "real_orders_authorized": False,
    }
