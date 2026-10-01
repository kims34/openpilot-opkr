"""Sanitized push-delivery health for IndexAlert production.

This endpoint intentionally exposes no FCM registration token or device payload.
It only reports aggregate registration/delivery state plus privacy-safe status of
the most recently created build self-test, so current Android-to-server wiring
can be verified without confusing an old-build receipt with the current build.
"""
from __future__ import annotations

import os

import firebase_admin

import monitor
import push_receipts
import push_self_test


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
    latest_self_test = push_self_test.latest_self_test_status()
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
        **latest_self_test,
        "current_build_physical_e2e_confirmed": bool(
            latest_self_test.get("latest_self_test_build")
            and latest_self_test.get("latest_self_test_sent")
            and latest_self_test.get("latest_self_test_receipt_confirmed")
        ),
        "execution_logging_configured": bool(os.getenv("INDEXALERT_EXECUTION_LOG_TOKEN", "").strip()),
        "tokens_exposed": False,
    }


def attach(app) -> None:
    existing = {getattr(route, "path", None) for route in app.router.routes}
    if "/push-health" not in existing:
        @app.get("/push-health")
        def push_health():
            return snapshot()
