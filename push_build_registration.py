"""Build-bound Android registration and physical-push attestation overlay.

This module is deliberately independent of the market/probability/KRX stack. It
adds only two operational routes to an existing FastAPI app:

* POST /register records the privacy-safe Android client build after the existing
  registration path succeeds.
* GET /push-health binds physical-E2E readiness to that exact registered build.

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

REGISTRATION_BUILD_CONTRACT = "register-client-build-v1"
SELF_TEST_TRIGGER_CONTRACT = "android-register-direct-v1"


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


def _latest_registered_build() -> tuple[str | None, str | None]:
    _init_device_build_db()
    with monitor.db() as con:
        row = con.execute(
            """SELECT b.client_build,b.updated_at
               FROM device_builds b
               JOIN devices d ON d.token=b.token
               ORDER BY b.updated_at DESC, b.rowid DESC
               LIMIT 1"""
        ).fetchone()
    if not row:
        return None, None
    return str(row[0]), str(row[1])


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
    )
    return result


def push_health_v32():
    payload = dict(push_health.snapshot())
    build, observed_at = _latest_registered_build()
    payload.update(
        latest_registered_client_build=build,
        latest_registered_client_build_at=observed_at,
        registration_build_observed=bool(build),
        registration_build_contract=REGISTRATION_BUILD_CONTRACT,
        self_test_trigger_contract=SELF_TEST_TRIGGER_CONTRACT,
    )
    payload["current_build_physical_e2e_confirmed"] = bool(
        build
        and payload.get("latest_self_test_build") == build
        and payload.get("latest_self_test_sent")
        and payload.get("latest_self_test_receipt_confirmed")
    )
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
