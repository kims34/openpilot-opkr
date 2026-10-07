"""Strict offline extractor for Kiwoom REAL type 00 order/fill frames.

Input is a parsed frame or bounded serialized UTF-8 JSON. This module opens no network and
authenticates no source. It preserves raw FID strings for protected account and
broker-native execution binding downstream.
"""
import json
from kiwoom_realtime_order_fill_subscription_contract import TYPE00_FIELDS

MAX_FRAME_BYTES = 1024 * 1024
MAX_FRAME_DEPTH = 64

class KiwoomType00FrameError(ValueError):
    pass

def extract_type00_events_json(payload) -> tuple[dict, ...]:
    """Bounded serialized UTF-8 input; parsing never authenticates its origin."""
    def unique_fields(pairs):
        fields = {}
        for key, value in pairs:
            if key in fields:
                raise KiwoomType00FrameError('TYPE00_JSON_INVALID')
            fields[key] = value
        return fields
    def reject_constant(value):
        raise KiwoomType00FrameError('TYPE00_JSON_INVALID')
    try:
        if type(payload) not in (str, bytes) or len(payload) > MAX_FRAME_BYTES:
            raise KiwoomType00FrameError('TYPE00_JSON_INVALID')
        encoded = payload.encode('utf-8') if type(payload) is str else payload
        if len(encoded) > MAX_FRAME_BYTES:
            raise KiwoomType00FrameError('TYPE00_JSON_INVALID')
        message = json.loads(encoded.decode('utf-8'), object_pairs_hook=unique_fields,
                             parse_constant=reject_constant)
        pending = [(message,0)]
        while pending:
            value, depth = pending.pop()
            if type(value) in (dict,list):
                if depth >= MAX_FRAME_DEPTH:
                    raise KiwoomType00FrameError('TYPE00_JSON_INVALID')
                children = value.values() if type(value) is dict else value
                pending.extend((child,depth+1) for child in children)
    except (ValueError, UnicodeError, RecursionError):
        raise KiwoomType00FrameError('TYPE00_JSON_INVALID') from None
    return extract_type00_events(message)

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
