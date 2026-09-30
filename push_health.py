"""Sanitized push-delivery health for IndexAlert production.

This endpoint intentionally exposes no FCM registration token or device payload.
It only reports aggregate registration/delivery state so current Android-to-server
wiring can be verified without leaking credentials.
"""
from __future__ import annotations

import os

import firebase_admin

import monitor
import push_receipts


def snapshot() -> dict:
    monitor.init_db()
    with monitor.db() as con:
        device_row = con.execute(
            "SELECT COUNT(*), MAX(updated_at) FROM devices"
        ).fetchone()
        pending_row = con.execute(
            "SELECT COUNT(*) FROM deliveries WHERE sent=0"
        ).fetchone()
        sent_row = con.execute(
            "SELECT COUNT(*) FROM deliveries WHERE sent=1"
        ).fetchone()
    receipt = push_receipts.stats()
    sent = int((sent_row or [0])[0] or 0)
    received = int(receipt.get("received_deliveries") or 0)
    return {
        "ok": True,
        "firebase": bool(firebase_admin._apps),
        "registered_devices": int((device_row or [0])[0] or 0),
        "last_device_registration_at": None if not device_row else device_row[1],
        "pending_deliveries": int((pending_row or [0])[0] or 0),
        "sent_deliveries": sent,
        "received_deliveries": received,
        "unconfirmed_sent_deliveries": max(0, sent - received),
        "last_client_receipt_at": receipt.get("last_client_receipt_at"),
        "latest_receipt_notifications_enabled": receipt.get("latest_receipt_notifications_enabled"),
        "client_receipts_supported": True,
        "execution_logging_configured": bool(os.getenv("INDEXALERT_EXECUTION_LOG_TOKEN", "").strip()),
        "tokens_exposed": False,
    }


def attach(app) -> None:
    existing = {getattr(route, "path", None) for route in app.router.routes}
    if "/push-health" not in existing:
        @app.get("/push-health")
        def push_health():
            return snapshot()
