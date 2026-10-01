"""Privacy-safe Android client-build registration metadata.

The production /register endpoint historically stored only the FCM token,
platform, settings and protocol. That made it impossible to distinguish an old
APK from a WorkManager/self-test failure by server logs alone. This module
extends the request with an optional client_build marker while keeping the raw
FCM token private and preserving backward compatibility for older clients.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException

import monitor


class RegisterBody(monitor.RegisterBody):
    client_build: str | None = None


def _clean_build(value: str | None) -> str | None:
    if value is None:
        return None
    build = str(value).strip()
    if not build or len(build) > 80:
        raise HTTPException(400, "invalid client_build")
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-+"
    if any(ch not in allowed for ch in build):
        raise HTTPException(400, "invalid client_build")
    return build


def _init_db() -> None:
    monitor.init_db()
    with monitor.db() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS device_client_builds(
                   token TEXT PRIMARY KEY,
                   client_build TEXT NOT NULL,
                   updated_at TEXT NOT NULL
               )"""
        )


def register(body: RegisterBody) -> dict:
    build = _clean_build(body.client_build)
    token = body.token.strip()
    if not (20 <= len(token) <= 4096):
        raise HTTPException(400, "invalid token")
    if body.platform != "android":
        raise HTTPException(400, "unsupported platform")
    if body.protocol not in (1, 2):
        raise HTTPException(400, "unsupported protocol")

    settings = body.enabled_levels
    if settings is not None:
        settings = dict(settings)
        settings.setdefault("kospi100", [])

    base = monitor.RegisterBody(
        token=body.token,
        platform=body.platform,
        enabled_levels=settings,
        protocol=body.protocol,
    )
    result = monitor.register(base)
    if build and bool(result.get("ok")) and bool(result.get("registered")):
        _init_db()
        now = datetime.now(timezone.utc).isoformat()
        with monitor.db() as con:
            con.execute(
                """INSERT INTO device_client_builds(token,client_build,updated_at)
                   VALUES(?,?,?)
                   ON CONFLICT(token) DO UPDATE SET
                       client_build=excluded.client_build,
                       updated_at=excluded.updated_at""",
                (token, build, now),
            )
        result = dict(result)
        result["client_build"] = build
    return result


def latest_registered_build_status() -> dict:
    _init_db()
    with monitor.db() as con:
        row = con.execute(
            """SELECT b.client_build,b.updated_at
               FROM device_client_builds b
               JOIN devices d ON d.token=b.token
               ORDER BY b.updated_at DESC LIMIT 1"""
        ).fetchone()
    return {
        "latest_registered_client_build": None if not row else str(row[0]),
        "latest_registered_client_build_at": None if not row else str(row[1]),
        "client_build_registration_supported": True,
    }


def attach(app) -> None:
    # Replace the legacy route only after the full production stack has loaded.
    # Older clients remain valid because client_build is optional.
    app.router.routes = [
        route for route in app.router.routes
        if getattr(route, "path", None) != "/register"
    ]

    @app.post("/register")
    def register_client(body: RegisterBody):
        return register(body)
