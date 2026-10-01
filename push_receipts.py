"""Privacy-safe client receipt acknowledgements for IndexAlert push delivery.

The Android client never sends its raw FCM token back through this endpoint.
Instead it submits SHA-256(token) plus the server-issued event_id. The server
accepts a receipt only when that hash belongs to a currently registered device
and the same event_id was already marked sent for that device.
"""
from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone

from fastapi import HTTPException
from pydantic import BaseModel

import monitor


class PushAckBody(BaseModel):
    event_id: str
    token_hash: str
    notifications_enabled: bool
    protocol: int = 2


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def init_db() -> None:
    monitor.init_db()
    with monitor.db() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS push_receipts(
                token_hash TEXT NOT NULL,
                event_id TEXT NOT NULL,
                received_at TEXT NOT NULL,
                notifications_enabled INTEGER NOT NULL,
                protocol INTEGER NOT NULL DEFAULT 2,
                PRIMARY KEY(token_hash,event_id)
            )"""
        )


def _resolve_registered_token(token_hash: str) -> str | None:
    if len(token_hash) != 64 or any(ch not in "0123456789abcdef" for ch in token_hash.lower()):
        return None
    with monitor.db() as con:
        tokens = [row[0] for row in con.execute("SELECT token FROM devices").fetchall()]
    for token in tokens:
        if hmac.compare_digest(_token_hash(token), token_hash.lower()):
            return token
    return None


def received_for(token: str, event_id: str) -> bool:
    """Return whether this exact registered-token/event pair has a real client ACK.

    This is an internal server check for transport self-tests. It never exposes
    the token and never infers receipt from FCM send success.
    """
    clean_token = str(token or "").strip()
    clean_event = str(event_id or "").strip()
    if not clean_token or not clean_event:
        return False
    init_db()
    token_hash = _token_hash(clean_token)
    with monitor.db() as con:
        return con.execute(
            "SELECT 1 FROM push_receipts WHERE token_hash=? AND event_id=? LIMIT 1",
            (token_hash, clean_event),
        ).fetchone() is not None


def record(body: PushAckBody) -> dict:
    event_id = body.event_id.strip()
    token_hash = body.token_hash.strip().lower()
    if not event_id or len(event_id) > 200:
        raise HTTPException(400, "invalid event_id")
    if body.protocol < 2:
        raise HTTPException(400, "unsupported protocol")

    init_db()
    token = _resolve_registered_token(token_hash)
    if token is None:
        raise HTTPException(404, "unknown device")

    with monitor.db() as con:
        sent = con.execute(
            "SELECT 1 FROM deliveries WHERE token=? AND event_id=? AND sent=1 LIMIT 1",
            (token, event_id),
        ).fetchone()
        if not sent:
            raise HTTPException(404, "unknown sent event")
        existed = con.execute(
            "SELECT 1 FROM push_receipts WHERE token_hash=? AND event_id=?",
            (token_hash, event_id),
        ).fetchone() is not None
        con.execute(
            """INSERT OR IGNORE INTO push_receipts(
                token_hash,event_id,received_at,notifications_enabled,protocol
            ) VALUES(?,?,?,?,?)""",
            (
                token_hash,
                event_id,
                datetime.now(timezone.utc).isoformat(),
                1 if body.notifications_enabled else 0,
                int(body.protocol),
            ),
        )
    return {"ok": True, "acknowledged": True, "duplicate": existed}


def stats() -> dict:
    init_db()
    with monitor.db() as con:
        row = con.execute(
            "SELECT COUNT(*), MAX(received_at) FROM push_receipts"
        ).fetchone()
        latest_enabled = con.execute(
            "SELECT notifications_enabled FROM push_receipts ORDER BY received_at DESC LIMIT 1"
        ).fetchone()
    return {
        "received_deliveries": int((row or [0])[0] or 0),
        "last_client_receipt_at": None if not row else row[1],
        "latest_receipt_notifications_enabled": None if not latest_enabled else bool(latest_enabled[0]),
    }


def attach(app) -> None:
    existing = {getattr(route, "path", None) for route in app.router.routes}
    if "/push-ack" not in existing:
        @app.post("/push-ack")
        def push_ack(body: PushAckBody):
            return record(body)
