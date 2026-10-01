"""Build-bound Android registration and physical-push attestation overlay.

This module is deliberately independent of the market/probability/KRX stack. It
adds only two operational routes to an existing FastAPI app:

* POST /register records the privacy-safe Android client build after the existing
  registration path succeeds.
* GET /push-health binds physical-E2E readiness to the exact registered device,
  its exact build and that same device/build's confirmed handset receipt.

The overlay is idempotent so multiple runtime layers can install it without
creating duplicate routes. Legacy clients remain compatible but fail closed for
current-build physical-E2E attestation because their installed build is unknown.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import monitor
import production
import push_health
import push_self_test

REGISTRATION_BUILD_CONTRACT = "register-client-build-v1"
SELF_TEST_TRIGGER_CONTRACT = "android-register-direct-v1"
PHYSICAL_E2E_BINDING_CONTRACT = "registered-device-build-receipt-v1"
PHYSICAL_E2E_BLOCKER_CONTRACT = "physical-e2e-blocker-v1"
PHYSICAL_E2E_BLOCKERS = frozenset({
    "NO_REGISTERED_BUILD",
    "NO_SELF_TEST",
    "DEVICE_MISMATCH",
    "BUILD_MISMATCH",
    "SELF_TEST_NOT_SENT",
    "RECEIPT_PENDING",
    "CONFIRMED",
})


class RegisterBodyV32(BaseModel):
    token: str
    platform: str = "android"
    enabled_levels: dict[str, list[int]] | None = None
    protocol: int = 1
    client_build: str | None = None


def _clean_client_build(value: str | None) -> str | None:
    if value is None:
        return None
    build = str(value).strip()
    if not build:
        return None
    if len(build) > 80:
        raise HTTPException(400, "invalid client_build")
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-+"
    if any(ch not in allowed for ch in build):
        raise HTTPException(400, "invalid client_build")
    return build


def _init_device_build_db() -> None:
    monitor.init_db()
    with monitor.db() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS device_builds(
                   token TEXT PRIMARY KEY,
                   client_build TEXT NOT NULL,
                   updated_at TEXT NOT NULL
               )"""
        )


def _record_device_build(token: str, build: str | None) -> None:
    _init_device_build_db()
    with monitor.db() as con:
        if build is None:
            # Legacy/rollback clients cannot attest their installed build. Clear
            # any older observation for this token instead of silently reusing it.
            con.execute("DELETE FROM device_builds WHERE token=?", (token,))
            return
        con.execute(
            """INSERT INTO device_builds(token,client_build,updated_at)
               VALUES(?,?,?)
               ON CONFLICT(token) DO UPDATE SET
                 client_build=excluded.client_build,
                 updated_at=excluded.updated_at""",
            (token, build, datetime.now(timezone.utc).isoformat()),
        )


def _latest_registered_device_build() -> tuple[str | None, str | None, str | None]:
    """Return token/build/time for the most recently observed registered device.

    The raw token is server-private and is used only to bind the registration
    record to the exact self-test device. It is never returned by /push-health.
    """
    _init_device_build_db()
    with monitor.db() as con:
        row = con.execute(
            """SELECT b.token,b.client_build,b.updated_at
               FROM device_builds b
               JOIN devices d ON d.token=b.token
               ORDER BY b.updated_at DESC, b.rowid DESC
               LIMIT 1"""
        ).fetchone()
    if not row:
        return None, None, None
    return str(row[0]), str(row[1]), str(row[2])


def _latest_registered_build() -> tuple[str | None, str | None]:
    """Compatibility helper returning only privacy-safe build/time metadata."""
    _token, build, observed_at = _latest_registered_device_build()
    return build, observed_at


def _physical_e2e_blocker(
    *,
    registered_build: str | None,
    self_test_build: str | None,
    same_device: bool,
    same_build: bool,
    sent: bool,
    receipt_confirmed: bool,
) -> str:
    """Return one fail-closed, privacy-safe blocker code for the latest evidence."""
    if not registered_build:
        return "NO_REGISTERED_BUILD"
    if not self_test_build:
        return "NO_SELF_TEST"
    if not same_device:
        return "DEVICE_MISMATCH"
    if not same_build:
        return "BUILD_MISMATCH"
    if not sent:
        return "SELF_TEST_NOT_SENT"
    if not receipt_confirmed:
        return "RECEIPT_PENDING"
    return "CONFIRMED"


def register_v32(body: RegisterBodyV32):
    build = _clean_client_build(body.client_build)
    base_body = monitor.RegisterBody(
        token=body.token,
        platform=body.platform,
        enabled_levels=body.enabled_levels,
        protocol=body.protocol,
    )
    result = dict(production.register(base_body))
    token = body.token.strip()
    if result.get("registered"):
        _record_device_build(token, build)
    result.update(
        client_build=build,
        client_build_observed=bool(build),
        registration_build_contract=REGISTRATION_BUILD_CONTRACT,
        self_test_trigger_contract=SELF_TEST_TRIGGER_CONTRACT if build else None,
        physical_e2e_binding_contract=PHYSICAL_E2E_BINDING_CONTRACT if build else None,
        physical_e2e_blocker_contract=PHYSICAL_E2E_BLOCKER_CONTRACT if build else None,
    )
    return result


def push_health_v32():
    payload = dict(push_health.snapshot())
    registered_token, build, observed_at = _latest_registered_device_build()
    self_test = push_self_test.latest_self_test_binding()
    same_device = bool(
        registered_token
        and self_test.get("token")
        and registered_token == self_test.get("token")
    )
    same_build = bool(build and self_test.get("build") == build)
    sent = bool(self_test.get("sent"))
    receipt_confirmed = bool(self_test.get("receipt_confirmed"))
    blocker = _physical_e2e_blocker(
        registered_build=build,
        self_test_build=self_test.get("build"),
        same_device=same_device,
        same_build=same_build,
        sent=sent,
        receipt_confirmed=receipt_confirmed,
    )

    # Override the aggregate helper's latest-self-test fields from the exact
    # private binding snapshot used for the device/build comparison, avoiding a
    # split-read race between public health and the attestation decision.
    payload.update(
        latest_self_test_build=self_test.get("build"),
        latest_self_test_sent=sent,
        latest_self_test_receipt_confirmed=receipt_confirmed,
        latest_self_test_created_at=self_test.get("created_at"),
        latest_registered_client_build=build,
        latest_registered_client_build_at=observed_at,
        registration_build_observed=bool(build),
        registration_device_matches_self_test=bool(same_device),
        registration_build_matches_self_test=bool(same_build),
        registration_build_contract=REGISTRATION_BUILD_CONTRACT,
        self_test_trigger_contract=SELF_TEST_TRIGGER_CONTRACT,
        physical_e2e_binding_contract=PHYSICAL_E2E_BINDING_CONTRACT,
        physical_e2e_blocker_contract=PHYSICAL_E2E_BLOCKER_CONTRACT,
        physical_e2e_blocker=blocker,
    )
    payload["current_build_physical_e2e_confirmed"] = blocker == "CONFIRMED"
    return payload


def attach(app: FastAPI) -> FastAPI:
    """Install the build-registration contract on `app` idempotently."""
    app.router.routes = [
        route
        for route in app.router.routes
        if getattr(route, "path", None) not in {"/register", "/push-health"}
    ]
    app.post("/register")(register_v32)
    app.get("/push-health")(push_health_v32)
    # Route changes must invalidate any previously built OpenAPI schema.
    app.openapi_schema = None
    return app
