"""Read-only HTTP/scheduler wrapper for the prospective H5 runtime.

This process never imports broker/order code. It periodically calls the already
tested structural run_once() producer after the 18:30 KST finality buffer and
serves only public-safe status plus the latest hash-only chronology payload.
"""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import time
from typing import Any, Mapping

import pandas as pd

from research_v1_prospective_runtime import (
    FINALITY_TIME_KST,
    ProspectiveRuntimeError,
    _canonical,
    _kst_now,
    _read_json,
    load_calendar_prefix,
    load_pinned_model_bundle,
    require_read_only_runtime_authority,
    run_once,
    verify_long_history_root,
)


RUNTIME_ID = "INDEXALERT_PROSPECTIVE_H5_READ_ONLY_HTTP_v1"
RETRY_SECONDS = 15 * 60
POLL_SECONDS = 30
STATUS_FILE = "runtime-status.json"
ANCHOR_RE = re.compile(r"^anchor-payload-(\d{4}-\d{2}-\d{2})\.json$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _canonical(dict(value)) + b"\n"
    fd, name = tempfile.mkstemp(prefix=".runtime-http-", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temp.unlink(missing_ok=True)


def _safe_status(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "runtime": RUNTIME_ID,
        "status": str(result.get("status") or "UNKNOWN"),
        "session": result.get("session"),
        "session_manifest_sha256": result.get("session_manifest_sha256"),
        "chronology_anchor_pending": bool(
            result.get("chronology_anchor_pending", False)
        ),
        "ordering": "DISABLED",
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permission_change_authorized": False,
        "independent_source_admission_verified": False,
        "independent_model_admission_verified": False,
        "independent_chronology_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }


def _read_status(root: Path) -> dict[str, Any]:
    path = root / STATUS_FILE
    if not path.is_file() or path.is_symlink():
        return _safe_status({"status": "WAITING"})
    value = dict(_read_json(path, "public runtime status"))
    forbidden = (
        "token", "password", "secret", "auth_key", "account",
        "order_id", "execution_id",
    )
    for key in value:
        if any(piece in key.lower() for piece in forbidden):
            raise ProspectiveRuntimeError("public status contains forbidden field")
    if value.get("ordering") != "DISABLED":
        raise ProspectiveRuntimeError("public status ordering must remain disabled")
    for field in (
        "real_orders_authorized", "funds_movement_authorized",
        "permission_change_authorized", "independent_source_admission_verified",
        "independent_model_admission_verified",
        "independent_chronology_admission_verified",
        "fresh_alpha_observation_admitted", "live_order_authorized",
    ):
        if value.get(field) is not False:
            raise ProspectiveRuntimeError(f"public status {field} must remain false")
    return value


def validate_anchor_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    expected = {
        "classification", "session", "decision_at",
        "source_receipt_sha256", "input_snapshot_sha256",
        "producer_binding_sha256", "model_bundle_sha256",
        "decision_capture_sha256", "session_manifest_sha256",
        "independent_chronology_admission_verified",
        "fresh_alpha_observation_admitted", "live_order_authorized",
        "anchor_payload_sha256",
    }
    if not isinstance(value, Mapping) or set(value) != expected:
        raise ProspectiveRuntimeError("public anchor fields mismatch")
    if value.get("classification") != "PROSPECTIVE_ANCHOR_PAYLOAD_NOT_ADMISSION":
        raise ProspectiveRuntimeError("public anchor classification mismatch")
    session = value.get("session")
    if type(session) is not str:
        raise ProspectiveRuntimeError("public anchor session missing")
    parsed = pd.Timestamp(session)
    if parsed.tzinfo is not None or parsed.strftime("%Y-%m-%d") != session:
        raise ProspectiveRuntimeError("public anchor session must be YYYY-MM-DD")
    decision = pd.Timestamp(value.get("decision_at"))
    if decision.tzinfo is None or decision.utcoffset() is None:
        raise ProspectiveRuntimeError("public anchor decision_at must be timezone-aware")
    if decision.tz_convert("Asia/Seoul").strftime("%Y-%m-%d") != session:
        raise ProspectiveRuntimeError("public anchor decision/session mismatch")
    for field in (
        "source_receipt_sha256", "input_snapshot_sha256",
        "producer_binding_sha256", "model_bundle_sha256",
        "decision_capture_sha256", "session_manifest_sha256",
        "anchor_payload_sha256",
    ):
        if type(value.get(field)) is not str or not HEX64.fullmatch(value[field]):
            raise ProspectiveRuntimeError(f"{field} must be lowercase SHA-256")
    for field in (
        "independent_chronology_admission_verified",
        "fresh_alpha_observation_admitted", "live_order_authorized",
    ):
        if value.get(field) is not False:
            raise ProspectiveRuntimeError(f"{field} must remain exact false")
    body = {k: value[k] for k in expected if k != "anchor_payload_sha256"}
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if actual != value["anchor_payload_sha256"]:
        raise ProspectiveRuntimeError("public anchor fingerprint mismatch")
    return {
        "valid": True,
        "session": session,
        "anchor_payload_sha256": actual,
        "live_order_authorized": False,
    }


def _latest_anchor(root: Path) -> dict[str, Any] | None:
    found: list[tuple[str, Path]] = []
    if not root.is_dir():
        return None
    for path in root.iterdir():
        if path.is_symlink() or not path.is_file():
            continue
        match = ANCHOR_RE.fullmatch(path.name)
        if match:
            found.append((match.group(1), path))
    if not found:
        return None
    _, latest = max(found)
    value = dict(_read_json(latest, "latest prospective anchor payload"))
    validate_anchor_payload(value)
    return value


class RuntimeState:
    def __init__(
        self,
        *,
        code_root: Path,
        verified_root: Path,
        private_root: Path,
        git_worktree: Path,
        environment: Mapping[str, str],
    ):
        self.code_root = code_root
        self.verified_root = verified_root
        self.private_root = private_root
        self.git_worktree = git_worktree
        self.environment = environment
        self.lock = threading.Lock()
        self.last_attempt_utc: pd.Timestamp | None = None

    def maybe_capture(self) -> None:
        now = _kst_now()
        if now.time() < FINALITY_TIME_KST:
            return
        now_utc = now.tz_convert("UTC")
        with self.lock:
            if self.last_attempt_utc is not None:
                elapsed = (now_utc - self.last_attempt_utc).total_seconds()
                if elapsed < RETRY_SECONDS:
                    return
            self.last_attempt_utc = now_utc
            try:
                result = run_once(
                    code_root=self.code_root,
                    verified_root=self.verified_root,
                    private_root=self.private_root,
                    git_worktree=self.git_worktree,
                    environment=self.environment,
                    now_kst=now,
                )
                _atomic_json(self.private_root / STATUS_FILE, _safe_status(result))
                print(
                    "INDEXALERT_PROSPECTIVE_RUNTIME="
                    + json.dumps(result, sort_keys=True),
                    flush=True,
                )
            except Exception as exc:
                safe = _safe_status(
                    {
                        "status": "FAIL_CLOSED",
                        "session": now.strftime("%Y-%m-%d"),
                    }
                )
                safe["error_class"] = type(exc).__name__
                try:
                    _atomic_json(self.private_root / STATUS_FILE, safe)
                except Exception:
                    pass
                print(
                    "INDEXALERT_PROSPECTIVE_RUNTIME="
                    + json.dumps(safe, sort_keys=True),
                    flush=True,
                )


def _handler(state: RuntimeState):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, value: Mapping[str, Any]) -> None:
            body = _canonical(dict(value)) + b"\n"
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self._send(
                    200,
                    {
                        "ok": True,
                        "runtime": RUNTIME_ID,
                        "ordering": "DISABLED",
                        "real_orders_authorized": False,
                        "live_order_authorized": False,
                    },
                )
                return
            if self.path == "/status":
                try:
                    self._send(200, _read_status(state.private_root))
                except Exception:
                    self._send(
                        503,
                        {
                            "status": "STATUS_UNAVAILABLE",
                            "ordering": "DISABLED",
                            "real_orders_authorized": False,
                            "live_order_authorized": False,
                        },
                    )
                return
            if self.path == "/anchor/latest":
                try:
                    value = _latest_anchor(state.private_root)
                except Exception:
                    self._send(
                        503,
                        {
                            "status": "ANCHOR_UNAVAILABLE",
                            "ordering": "DISABLED",
                            "real_orders_authorized": False,
                            "live_order_authorized": False,
                        },
                    )
                    return
                if value is None:
                    self._send(
                        404,
                        {
                            "status": "NO_ANCHOR",
                            "ordering": "DISABLED",
                            "real_orders_authorized": False,
                            "live_order_authorized": False,
                        },
                    )
                    return
                self._send(200, value)
                return
            self._send(404, {"status": "NOT_FOUND"})

        def do_POST(self):
            self._send(
                405,
                {
                    "status": "MUTATION_FORBIDDEN",
                    "ordering": "DISABLED",
                    "real_orders_authorized": False,
                    "live_order_authorized": False,
                },
            )

        def log_message(self, format, *args):
            return

    return Handler


def _scheduler(state: RuntimeState) -> None:
    while True:
        state.maybe_capture()
        time.sleep(POLL_SECONDS)


def serve(
    *,
    code_root: Path,
    verified_root: Path,
    private_root: Path,
    git_worktree: Path,
    environment: Mapping[str, str],
    port: int,
) -> None:
    # Fail the deployment at startup if authority/model/calendar/PIT identity
    # drifted. This performs no KRX network request.
    require_read_only_runtime_authority(environment)
    load_pinned_model_bundle(code_root)
    load_calendar_prefix(code_root)
    verify_long_history_root(verified_root)
    private_root.mkdir(parents=True, exist_ok=True)
    state = RuntimeState(
        code_root=code_root,
        verified_root=verified_root,
        private_root=private_root,
        git_worktree=git_worktree,
        environment=environment,
    )
    thread = threading.Thread(target=_scheduler, args=(state,), daemon=True)
    thread.start()
    server = ThreadingHTTPServer(("0.0.0.0", port), _handler(state))
    server.serve_forever()


def main() -> None:
    code_root = Path(__file__).resolve().parent
    verified_root = Path(
        os.getenv("INDEXALERT_VERIFIED_PIT_ROOT", "/pit/frozen_rerun_20261008")
    )
    private_root = Path(
        os.getenv("INDEXALERT_PROSPECTIVE_PRIVATE_ROOT", "/pit/prospective_runtime")
    )
    git_worktree = Path(os.getenv("INDEXALERT_GIT_WORKTREE", "/app"))
    port = int(os.getenv("PORT", "8080"))
    serve(
        code_root=code_root,
        verified_root=verified_root,
        private_root=private_root,
        git_worktree=git_worktree,
        environment=os.environ,
        port=port,
    )


if __name__ == "__main__":
    main()
