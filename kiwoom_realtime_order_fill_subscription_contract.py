"""Offline contract for Kiwoom domestic order/fill realtime registration.

Mirrors the reviewed official type 00 WebSocket registration packet only.
No socket/client/token/account/order code is present and no subscription is sent.
"""
OFFICIAL_SCHEMA_COMMIT = "953e5dbff123f437ab4d11a78a95191a685eb51f"
WEBSOCKET_PATH = "/api/dostk/websocket"
REALTIME_TYPE = "00"

TYPE00_FIELDS = frozenset((
    "9201","9203","9205","9001","912","913","302","900","901","902","903",
    "904","905","906","907","908","909","910","911","10","27","28","914",
    "915","938","939","919","920","921","922","923","10010","2134","2135","2136",
))

class KiwoomRealtimeEnvelopeError(ValueError):
    pass

def build_order_fill_registration(*, group_no="1", refresh="1") -> dict:
    if type(group_no) is not str or not group_no or len(group_no) > 16 or not group_no.isdigit():
        raise KiwoomRealtimeEnvelopeError("grp_no invalid")
    if refresh not in ("0","1"):
        raise KiwoomRealtimeEnvelopeError("refresh invalid")
    body = {
        "trnm": "REG",
        "grp_no": group_no,
        "refresh": refresh,
        "data": [{"item": [], "type": [REALTIME_TYPE]}],
    }
    return {
        "mode": "OFFLINE_KIWOOM_REALTIME_REGISTRATION_ENVELOPE",
        "path": WEBSOCKET_PATH,
        "body": body,
        "official_schema_commit": OFFICIAL_SCHEMA_COMMIT,
        "network_request_attempted": False,
        "websocket_opened": False,
        "subscription_sent": False,
        "broker_request_sent": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "broker_permission_change_authorized": False,
        "genuine_live_provenance_verified": False,
    }

def validate_type00_field_allowlist(raw_event: dict) -> dict:
    if type(raw_event) is not dict:
        raise KiwoomRealtimeEnvelopeError("type00 event invalid")
    if any(type(k) is not str or k not in TYPE00_FIELDS for k in raw_event):
        raise KiwoomRealtimeEnvelopeError("unknown type00 field")
    if any(type(v) is not str or len(v) > 4096 for v in raw_event.values()):
        raise KiwoomRealtimeEnvelopeError("type00 value invalid")
    return {
        "mode": "OFFLINE_KIWOOM_TYPE00_FIELD_ALLOWLIST",
        "recognized_field_count": len(raw_event),
        "broker_execution_id_present": bool(raw_event.get("909")),
        "network_request_attempted": False,
        "websocket_opened": False,
        "genuine_live_provenance_verified": False,
        "broker_native_execution_id_capture_tested": False,
        "real_orders_authorized": False,
    }
