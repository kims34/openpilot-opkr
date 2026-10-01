"""IndexAlert production v3.2: bind Android registration to the installed build.

This layer closes the remaining physical-push observability gap without changing
market, probability, KRX, recommendation, or execution logic. New Android clients
include a privacy-safe build identifier in /register. The server records that
identifier separately from the raw FCM token and only reports current-build
physical E2E when that exact registered build has a confirmed handset receipt.

The v4.7 Android client performs its self-test immediately on the same confirmed
registration path, before falling back to WorkManager retries. The server therefore
does not launch a second concurrent self-test; the existing /push-self-test route
remains the single idempotent transport endpoint.

Legacy clients that do not send client_build remain fully compatible, but are
fail-closed for current-build physical-E2E attestation because their installed
build cannot be proven remotely.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from pydantic import BaseModel

import monitor
import production
import production_v31
import push_health

app = production_v31.app
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
            # A legacy/rollback client cannot attest its installed build. Remove
            # any older observation for this token so health remains fail-closed.
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


# Replace only the operational registration/health routes. All market and
# research routes remain the exact v31 stack.
app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "path", None) not in {"/register", "/push-health"}
]


@app.post("/register")
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


@app.get("/push-health")
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
    # A receipt for an older build cannot attest the newly registered client.
    payload["current_build_physical_e2e_confirmed"] = bool(
        build
        and payload.get("latest_self_test_build") == build
        and payload.get("latest_self_test_sent")
        and payload.get("latest_self_test_receipt_confirmed")
    )
    return payload
