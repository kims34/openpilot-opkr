"""One-shot per-build push self-test for IndexAlert Android clients.

The self-test is operational transport verification only. It is isolated from
market-threshold rules and trading/research decisions. A registered Android
client may request at most one successfully-sent self-test delivery for its own
FCM token and a specific client build identifier. An unsent row is retried using
its original event_id so transient provider failures do not create duplicates.

FCM provider send success is deliberately separate from handset receipt. Every
response reports ``receipt_confirmed`` based only on the privacy-safe /push-ack
ledger. A successfully sent event is never re-sent merely because its receipt is
still pending; the Android worker may poll this same endpoint until the original
event is actually acknowledged.
"""
from __future__ import annotations

import json
import time
import uuid

from fastapi import HTTPException
from pydantic import BaseModel
from firebase_admin import messaging

import monitor
import push_receipts

INDEX_ID = "push_self_test"
THRESHOLD = 0


class PushSelfTestBody(BaseModel):
    token: str
    platform: str = "android"
    protocol: int = 2
    client_build: str


def _clean_build(value: str) -> str:
    build = str(value or "").strip()
    if not build or len(build) > 80:
        raise HTTPException(400, "invalid client_build")
    if any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-+" for ch in build):
        raise HTTPException(400, "invalid client_build")
    return build


def _registered(token: str) -> bool:
    with monitor.db() as con:
        return con.execute("SELECT 1 FROM devices WHERE token=?", (token,)).fetchone() is not None


def _sent_response(*, token: str, event_id: str, build: str, queued: bool) -> dict:
    return {
        "ok": True,
        "queued": bool(queued),
        "already_sent": not bool(queued),
        "client_build": build,
        "event_id": event_id,
        "receipt_confirmed": push_receipts.received_for(token, event_id),
    }


def latest_self_test_binding() -> dict:
    """Return the latest self-test including its private token for server-only binding.

    Callers must not expose ``token`` or ``event_id`` in public API responses.
    This helper exists so the registration overlay can prove that the latest
    registered device and the latest build self-test are the same exact device,
    not merely two devices running the same client build string.
    """
    monitor.init_db()
    with monitor.db() as con:
        row = con.execute(
            """SELECT token,cycle,event_id,sent,created
               FROM deliveries
               WHERE index_id=? AND threshold=?
               ORDER BY created DESC, rowid DESC LIMIT 1""",
            (INDEX_ID, THRESHOLD),
        ).fetchone()
    if not row:
        return {
            "token": None,
            "event_id": None,
            "build": None,
            "sent": False,
            "receipt_confirmed": False,
            "created_at": None,
        }

    token, cycle, event_id, sent, created = row
    cycle_text = str(cycle or "")
    build = cycle_text[len("android-"):] if cycle_text.startswith("android-") else None
    sent_bool = bool(sent)
    token_text = str(token)
    event_text = str(event_id)
    confirmed = bool(sent_bool and push_receipts.received_for(token_text, event_text))
    return {
        "token": token_text,
        "event_id": event_text,
        "build": build,
        "sent": sent_bool,
        "receipt_confirmed": confirmed,
        "created_at": None if created is None else float(created),
    }


def latest_self_test_status() -> dict:
    """Return privacy-safe status for the most recently created build self-test.

    Aggregate push receipt counts cannot prove that the *current* Android build
    received its own self-test: an older build may already have a receipt. This
    helper therefore binds health to the latest self-test delivery row and checks
    that exact token/event pair through the receipt ledger. Raw token/event IDs
    are intentionally omitted from the returned status.
    """
    binding = latest_self_test_binding()
    return {
        "latest_self_test_build": binding["build"],
        "latest_self_test_sent": binding["sent"],
        "latest_self_test_receipt_confirmed": binding["receipt_confirmed"],
        "latest_self_test_created_at": binding["created_at"],
    }


def request_self_test(body: PushSelfTestBody) -> dict:
    token = body.token.strip()
    build = _clean_build(body.client_build)
    if body.platform != "android":
        raise HTTPException(400, "unsupported platform")
    if body.protocol < 2:
        raise HTTPException(400, "unsupported protocol")
    if not (20 <= len(token) <= 4096):
        raise HTTPException(400, "invalid token")

    monitor.init_db()
    if not _registered(token):
        raise HTTPException(404, "device must register before self-test")
    if not monitor.init_firebase():
        raise HTTPException(503, "firebase unavailable")

    cycle = f"android-{build}"
    with monitor.db() as con:
        existing = con.execute(
            """SELECT event_id,sent,payload FROM deliveries
               WHERE token=? AND index_id=? AND cycle=? AND threshold=? LIMIT 1""",
            (token, INDEX_ID, cycle, THRESHOLD),
        ).fetchone()
        if existing and bool(existing[1]):
            return _sent_response(
                token=token,
                event_id=str(existing[0]),
                build=build,
                queued=False,
            )

        if existing:
            # Reuse the exact unsent event so retries remain idempotent.
            event_id = str(existing[0])
            try:
                data = json.loads(existing[2])
            except Exception as exc:
                raise HTTPException(500, "invalid stored self-test payload") from exc
        else:
            event_id = str(uuid.uuid4())
            data = {
                "index_id": INDEX_ID,
                "threshold": str(THRESHOLD),
                "event_id": event_id,
                "cycle": cycle,
                "kind": "push_self_test",
                "title": "IndexAlert 연결 확인",
                "body": "알림 연결이 정상적으로 설정되었습니다.",
            }
            payload = json.dumps(data, ensure_ascii=False, sort_keys=True)
            con.execute(
                """INSERT INTO deliveries(token,index_id,cycle,threshold,event_id,payload,created,sent)
                   VALUES(?,?,?,?,?,?,?,0)""",
                (token, INDEX_ID, cycle, THRESHOLD, event_id, payload, time.time()),
            )

    try:
        messaging.send(
            messaging.Message(
                token=token,
                notification=None,
                data=data,
                android=messaging.AndroidConfig(priority="high", ttl=3600),
            )
        )
    except messaging.UnregisteredError:
        with monitor.db() as con:
            con.execute("DELETE FROM devices WHERE token=?", (token,))
            con.execute("DELETE FROM deliveries WHERE token=?", (token,))
        raise HTTPException(410, "device token is no longer registered")
    except Exception as exc:
        # Leave sent=0 so the same build/event can retry without duplication.
        print("push self-test send failed:", type(exc).__name__, flush=True)
        raise HTTPException(503, "push self-test send failed") from exc

    with monitor.db() as con:
        con.execute(
            "UPDATE deliveries SET sent=1 WHERE token=? AND event_id=?",
            (token, event_id),
        )
    return _sent_response(token=token, event_id=event_id, build=build, queued=True)


def attach(app) -> None:
    existing = {getattr(route, "path", None) for route in app.router.routes}
    if "/push-self-test" not in existing:
        @app.post("/push-self-test")
        def push_self_test(body: PushSelfTestBody):
            return request_self_test(body)
