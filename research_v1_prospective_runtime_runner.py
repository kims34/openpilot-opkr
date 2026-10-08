"""Tiny-Live critical-path prospective capture runtime.

This service exists to start the genuine-future observation clock without
activating trading.  After a conservative post-close guard it:

1. reconstructs only the missing warm-up market sessions after the verified
   frozen long-history cutoff through the approved KRX OpenAPI services;
2. combines those observations with a short tail of the verified frozen panel;
3. binds the pinned block16 model bundle to the exact supervised-session
   calendar;
4. commits one immutable source/input/producer/decision/session transaction;
5. exposes only a public-safe hash manifest for later GitHub chronology anchoring.

It never imports an order sender, never enables broker permissions, never moves
funds and never turns structural captures into admitted Alpha/Shadow/LIVE
evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from typing import Any, Callable, Mapping

import pandas as pd

from research_v1_krx_historical_fetchers import fetch_openapi_raw, parse_openapi_raw
from research_v1_krx_openapi_prospective_source import (
    _frame_sha256,
    build_current_session_openapi_source,
    store_current_session_openapi_source,
    validate_source_receipt,
)
from research_v1_krx_private_store import (
    validate_private_root,
    verify_raw_object,
    write_raw_object,
)
from research_v1_prospective_inputs import RAW_COLUMNS
from research_v1_prospective_model_bundle import validate_model_bundle
from research_v1_prospective_session_commit import commit_structural_prospective_session
from research_v1_prospective_frozen_producer import (
    FROZEN_CALENDAR_ORIGIN_SESSION,
    FROZEN_TEST_BLOCK_STARTS,
)


KST = timezone(timedelta(hours=9))
MIN_CAPTURE_HOUR_KST = 19
MIN_CAPTURE_MINUTE_KST = 0
RETRY_SECONDS = 15 * 60
SCHEDULER_POLL_SECONDS = 30

PIT_ROOT_DEFAULT = "/pit"
PRIVATE_DIR_NAME = "indexalert_prospective_v1"
LONG_DIR_NAME = "marcap_kospi_pit_long_verified_36643183157"
SUPERVISED_DIR_NAME = "supervised_frozen_verified_36643183157"
SUPERVISED_VERIFICATION_FILE = "frozen_supervised_verification.json"
LONG_VERIFICATION_FILE = "frozen_long_history_verification.json"
MODEL_BUNDLE_FILE = "frozen_block16_model_bundle_36643183157.json"
CONNECTIVITY_EVIDENCE_FILE = "INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json"

DAILY_ENDPOINT = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
MASTER_ENDPOINT = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info"
FROZEN_SOURCE_END = "2026-09-23"
FROZEN_ACTION_ID = 36643183157
FROZEN_LONG_SOURCE_FINGERPRINT = {
    "rows": 2512128,
    "symbols": 1089,
    "date_min": "2015-06-15",
    "date_max": "2026-09-23",
    "columns": [
        "decision_date", "symbol", "open", "high", "low", "close",
        "volume", "value", "krx_change_return",
    ],
    "hash_xor_u64": "17836462952802001740",
    "hash_sum_u64": "17879387804724068608",
}
PINNED_MODEL_SHA256 = "2557663c1055f096be10b5a04890c89a8dfa48a49a7d24faf92ba5276f476531"


class ProspectiveRuntimeError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ProspectiveRuntimeError(f"required runtime artifact missing: {path.name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProspectiveRuntimeError(f"invalid runtime JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise ProspectiveRuntimeError(f"runtime JSON must be an object: {path.name}")
    return value


def _atomic_json(path: Path, value: Mapping[str, Any], *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    payload = _canonical(dict(value)) + b"\n"
    fd, name = tempfile.mkstemp(prefix=".runtime-", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        temp.unlink(missing_ok=True)


def _safe_status(root: Path) -> dict[str, Any]:
    path = root / "public" / "status.json"
    if not path.is_file():
        return {
            "runtime": "INDEXALERT_PROSPECTIVE_CAPTURE_v1",
            "status": "WAITING",
            "ordering": "DISABLED",
            "real_orders_authorized": False,
            "funds_movement_authorized": False,
            "broker_permission_change_authorized": False,
        }
    value = _load_json(path)
    forbidden = {
        "token", "account", "password", "secret", "auth_key", "cookie",
        "order_id", "execution_id", "ip_address",
    }
    for key in value:
        low = key.lower()
        if any(fragment in low for fragment in forbidden):
            raise ProspectiveRuntimeError("public runtime status contains forbidden field")
    return value


def _write_status(root: Path, **values: Any) -> dict[str, Any]:
    out = {
        "runtime": "INDEXALERT_PROSPECTIVE_CAPTURE_v1",
        "ordering": "DISABLED",
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "broker_permission_change_authorized": False,
        "fresh_alpha_observation_admitted": False,
        **values,
    }
    _atomic_json(root / "public" / "status.json", out, mode=0o600)
    return out


def _capture_time_allowed(now_utc: datetime) -> bool:
    if now_utc.tzinfo is None or now_utc.utcoffset() is None:
        raise ProspectiveRuntimeError("runtime clock must be timezone-aware")
    local = now_utc.astimezone(KST)
    return (local.hour, local.minute) >= (MIN_CAPTURE_HOUR_KST, MIN_CAPTURE_MINUTE_KST)


def _locate_verified_pair(pit_root: Path) -> tuple[Path, Path]:
    candidates = [
        pit_root,
        pit_root / "frozen_rerun_20261008",
    ]
    for base in candidates:
        long_dir = base / LONG_DIR_NAME
        sup_dir = base / SUPERVISED_DIR_NAME
        if (
            (long_dir / LONG_VERIFICATION_FILE).is_file()
            and (sup_dir / SUPERVISED_VERIFICATION_FILE).is_file()
            and (sup_dir / "supervised.parquet").is_file()
        ):
            long_ver = _load_json(long_dir / LONG_VERIFICATION_FILE)
            sup_ver = _load_json(sup_dir / SUPERVISED_VERIFICATION_FILE)
            if (
                long_ver.get("classification")
                != "FROZEN_LONG_HISTORY_SOURCE_REHYDRATION_VERIFIED"
                or long_ver.get("frozen_action_id") != FROZEN_ACTION_ID
                or long_ver.get("source_fingerprint") != FROZEN_LONG_SOURCE_FINGERPRINT
                or long_ver.get("fingerprint_exact_match") is not True
            ):
                continue
            if (
                sup_ver.get("classification")
                != "FROZEN_SUPERVISED_CACHE_REHYDRATION_VERIFIED"
                or sup_ver.get("frozen_action_id") != FROZEN_ACTION_ID
                or sup_ver.get("exact_reference_meta_match") is not True
                or sup_ver.get("live_order_authorized") is not False
            ):
                continue
            return long_dir, sup_dir
    raise ProspectiveRuntimeError("verified frozen long-history/supervised pair not found")


def _load_calendar(sup_dir: Path) -> list[str]:
    frame = pd.read_parquet(sup_dir / "supervised.parquet", columns=["decision_date"])
    dates = pd.to_datetime(frame["decision_date"], errors="coerce")
    if dates.isna().any() or dates.dt.tz is not None:
        raise ProspectiveRuntimeError("verified supervised calendar is invalid")
    sessions = sorted(dates.dt.strftime("%Y-%m-%d").drop_duplicates().tolist())
    if not sessions or sessions[0] != FROZEN_CALENDAR_ORIGIN_SESSION:
        raise ProspectiveRuntimeError("verified supervised calendar origin drift")
    for ordinal, expected in FROZEN_TEST_BLOCK_STARTS.items():
        if ordinal < len(sessions) and sessions[ordinal] != expected:
            raise ProspectiveRuntimeError(
                f"verified supervised calendar milestone drift at {ordinal}"
            )
    return sessions


def _load_frozen_history_tail(
    long_dir: Path,
    *,
    observed_at: str,
    minimum_sessions: int = 45,
) -> pd.DataFrame:
    path = long_dir / "kospi-pit-2026.parquet"
    if not path.is_file() or path.is_symlink():
        raise ProspectiveRuntimeError("verified 2026 long-history parquet missing")
    columns = [
        "decision_date", "symbol", "open", "high", "low", "close",
        "volume", "value", "krx_change_return",
    ]
    frame = pd.read_parquet(path, columns=columns)
    dates = pd.to_datetime(frame["decision_date"], errors="coerce")
    if dates.isna().any() or dates.dt.tz is not None:
        raise ProspectiveRuntimeError("frozen history decision_date invalid")
    frame["decision_date"] = dates.dt.normalize()
    frame = frame[frame["decision_date"] <= pd.Timestamp(FROZEN_SOURCE_END)].copy()
    sessions = sorted(frame["decision_date"].drop_duplicates())
    if len(sessions) < minimum_sessions:
        raise ProspectiveRuntimeError("insufficient verified frozen warm-up sessions")
    keep = set(sessions[-minimum_sessions:])
    frame = frame[frame["decision_date"].isin(keep)].copy()
    frame["available_at"] = observed_at
    return frame.loc[:, RAW_COLUMNS].sort_values(
        ["decision_date", "symbol"], kind="mergesort"
    ).reset_index(drop=True)


def _panel_path(cache_root: Path, session: str) -> Path:
    return cache_root / f"panel-{session}.parquet"


def _non_session_path(cache_root: Path, session: str) -> Path:
    return cache_root / f"non-session-{session}.json"


def _load_cached_panel(cache_root: Path, session: str) -> pd.DataFrame | None:
    panel_path = _panel_path(cache_root, session)
    receipt_path = cache_root / f"source-{session}.json"
    if not panel_path.exists():
        return None
    if panel_path.is_symlink() or not receipt_path.is_file() or receipt_path.is_symlink():
        raise ProspectiveRuntimeError("warm-up cache is incomplete or unsafe")
    panel = pd.read_parquet(panel_path)
    receipt = _load_json(receipt_path)
    if receipt.get("session") != session:
        raise ProspectiveRuntimeError("warm-up receipt session mismatch")
    try:
        validate_source_receipt(receipt)
        verify_raw_object(cache_root, receipt["daily_raw_sha256"])
        verify_raw_object(cache_root, receipt["master_raw_sha256"])
    except Exception as exc:
        raise ProspectiveRuntimeError(
            "warm-up source receipt/raw-object integrity failed"
        ) from exc
    if _frame_sha256(panel) != receipt.get("normalized_panel_sha256"):
        raise ProspectiveRuntimeError("warm-up normalized panel fingerprint mismatch")
    return panel


def _store_panel(cache_root: Path, session: str, panel: pd.DataFrame) -> None:
    path = _panel_path(cache_root, session)
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    if path.exists():
        existing = pd.read_parquet(path)
        if _frame_sha256(existing) != _frame_sha256(panel):
            raise ProspectiveRuntimeError("conflicting warm-up panel")
        return
    fd, name = tempfile.mkstemp(prefix=".panel-", suffix=".parquet", dir=path.parent)
    os.close(fd)
    temp = Path(name)
    try:
        panel.to_parquet(temp, index=False)
        os.chmod(temp, 0o600)
        os.link(temp, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        temp.unlink(missing_ok=True)


def _fetch_raw(
    endpoint: str,
    session: str,
    auth_key: str,
    *,
    fetcher: Callable[..., Any] = fetch_openapi_raw,
):
    return fetcher(
        endpoint=endpoint,
        params={"basDd": session.replace("-", "")},
        auth_key=auth_key,
        network_authorized=True,
    )


def _fetch_normalized_session(
    session: str,
    *,
    auth_key: str,
    evidence: Mapping[str, Any],
    storage_root: Path | None,
    git_worktree: str,
    fetcher: Callable[..., Any] = fetch_openapi_raw,
) -> tuple[dict[str, Any] | None, bytes, bytes | None, str]:
    daily = _fetch_raw(DAILY_ENDPOINT, session, auth_key, fetcher=fetcher)
    daily_frame = parse_openapi_raw(daily.raw_bytes)
    if daily_frame.empty:
        return None, daily.raw_bytes, None, daily.retrieved_at
    master = _fetch_raw(MASTER_ENDPOINT, session, auth_key, fetcher=fetcher)
    source = build_current_session_openapi_source(
        daily_raw=daily.raw_bytes,
        master_raw=master.raw_bytes,
        expected_session=session,
        daily_retrieved_at=daily.retrieved_at,
        master_retrieved_at=master.retrieved_at,
        connectivity_evidence=evidence,
    )
    if storage_root is not None:
        store_current_session_openapi_source(
            source,
            daily_raw=daily.raw_bytes,
            master_raw=master.raw_bytes,
            root=str(storage_root),
            git_worktree=git_worktree,
        )
        _store_panel(storage_root, session, source["panel"])
    return source, daily.raw_bytes, master.raw_bytes, master.retrieved_at


def _warmup_after_frozen(
    target_session: str,
    *,
    root: Path,
    auth_key: str,
    evidence: Mapping[str, Any],
    git_worktree: str,
    fetcher: Callable[..., Any] = fetch_openapi_raw,
) -> tuple[list[pd.DataFrame], list[str]]:
    start = pd.Timestamp(FROZEN_SOURCE_END) + pd.Timedelta(days=1)
    end = pd.Timestamp(target_session) - pd.Timedelta(days=1)
    if end < start:
        return [], []
    panels: list[pd.DataFrame] = []
    sessions: list[str] = []
    warmup_root = root / "warmup"
    for day in pd.date_range(start, end, freq="D"):
        session = day.strftime("%Y-%m-%d")
        cached = _load_cached_panel(warmup_root, session)
        if cached is not None:
            panels.append(cached)
            sessions.append(session)
            continue
        marker = _non_session_path(warmup_root, session)
        if marker.is_file() and not marker.is_symlink():
            value = _load_json(marker)
            if (
                value.get("classification")
                != "OBSERVED_EMPTY_KRX_OPENAPI_DAILY_BLOCK_NOT_DECISION"
                or value.get("session") != session
                or value.get("decision_recorded") is not False
                or value.get("fresh_alpha_observation_admitted") is not False
                or value.get("live_order_authorized") is not False
            ):
                raise ProspectiveRuntimeError("invalid non-session warm-up marker")
            try:
                verify_raw_object(
                    warmup_root, value.get("daily_raw_sha256", "")
                )
            except Exception as exc:
                raise ProspectiveRuntimeError(
                    "non-session warm-up raw-object integrity failed"
                ) from exc
            continue
        source, daily_raw, master_raw, retrieved_at = _fetch_normalized_session(
            session,
            auth_key=auth_key,
            evidence=evidence,
            storage_root=warmup_root,
            git_worktree=git_worktree,
            fetcher=fetcher,
        )
        if source is None:
            raw_object = write_raw_object(
                warmup_root, daily_raw, git_worktree=git_worktree
            )
            _atomic_json(
                marker,
                {
                    "classification": "OBSERVED_EMPTY_KRX_OPENAPI_DAILY_BLOCK_NOT_DECISION",
                    "session": session,
                    "observed_at": retrieved_at,
                    "daily_raw_sha256": raw_object["raw_object_sha256"],
                    "decision_recorded": False,
                    "fresh_alpha_observation_admitted": False,
                    "live_order_authorized": False,
                },
            )
            continue
        panels.append(source["panel"])
        sessions.append(session)
    return panels, sessions


def _public_anchor_manifest(result: Mapping[str, Any], decision_at: str) -> dict[str, Any]:
    fields = (
        "session", "source_receipt_sha256", "input_snapshot_sha256",
        "producer_binding_sha256", "model_bundle_sha256",
        "decision_capture_sha256", "session_manifest_sha256",
    )
    out = {field: result[field] for field in fields}
    out.update(
        {
            "decision_at": decision_at,
            "structural_session_committed": True,
            "independent_source_admission_verified": False,
            "independent_model_admission_verified": False,
            "independent_chronology_admission_verified": False,
            "fresh_alpha_observation_admitted": False,
            "live_order_authorized": False,
        }
    )
    return out


def capture_current_session_once(
    *,
    pit_root: str = PIT_ROOT_DEFAULT,
    code_root: str = "/app",
    now_utc: datetime | None = None,
    auth_key: str | None = None,
    fetcher: Callable[..., Any] = fetch_openapi_raw,
    commit_fn: Callable[..., Mapping[str, Any]] = commit_structural_prospective_session,
) -> dict[str, Any]:
    now = now_utc or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ProspectiveRuntimeError("runtime clock must be timezone-aware")
    local = now.astimezone(KST)
    target = local.date().isoformat()
    pit = Path(pit_root).resolve()
    code = Path(code_root).resolve()
    private_root = validate_private_root(
        pit / PRIVATE_DIR_NAME, git_worktree=code
    )

    if not _capture_time_allowed(now):
        return _write_status(
            private_root,
            status="WAITING_FOR_POST_CLOSE_GUARD",
            target_session=target,
            checked_at=now.isoformat(),
        )

    existing_anchor = private_root / "public" / f"anchor-{target}.json"
    if existing_anchor.is_file() and not existing_anchor.is_symlink():
        anchor = _load_json(existing_anchor)
        return _write_status(
            private_root,
            status="SESSION_ALREADY_COMMITTED",
            target_session=target,
            checked_at=now.isoformat(),
            session_manifest_sha256=anchor.get("session_manifest_sha256"),
        )

    key = (auth_key if auth_key is not None else os.getenv("KRX_AUTH_KEY", "")).strip()
    if not key:
        raise ProspectiveRuntimeError("KRX_AUTH_KEY is not configured")

    evidence = _load_json(code / CONNECTIVITY_EVIDENCE_FILE)
    bundle = _load_json(code / MODEL_BUNDLE_FILE)
    checked_bundle = validate_model_bundle(bundle)
    if checked_bundle["model_bundle_sha256"] != PINNED_MODEL_SHA256:
        raise ProspectiveRuntimeError("pinned model bundle identity drift")

    long_dir, sup_dir = _locate_verified_pair(pit)
    calendar = _load_calendar(sup_dir)

    warmup_panels, warmup_sessions = _warmup_after_frozen(
        target,
        root=private_root,
        auth_key=key,
        evidence=evidence,
        git_worktree=str(code),
        fetcher=fetcher,
    )

    current_source, daily_raw, master_raw, _ = _fetch_normalized_session(
        target,
        auth_key=key,
        evidence=evidence,
        storage_root=None,
        git_worktree=str(code),
        fetcher=fetcher,
    )
    if current_source is None:
        return _write_status(
            private_root,
            status="NO_TRADING_SESSION_OR_SOURCE_NOT_YET_PUBLISHED",
            target_session=target,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
    if master_raw is None:
        raise ProspectiveRuntimeError("current master response missing")

    observed = datetime.now(timezone.utc).isoformat()
    frozen_tail = _load_frozen_history_tail(
        long_dir,
        observed_at=observed,
        minimum_sessions=45,
    )
    histories = [frozen_tail]
    for panel in warmup_panels:
        histories.append(panel.loc[:, RAW_COLUMNS].copy())
    history_raw = pd.concat(histories, ignore_index=True)
    history_raw = history_raw.sort_values(
        ["decision_date", "symbol"], kind="mergesort"
    ).drop_duplicates(["decision_date", "symbol"], keep="last")

    extension = sorted(set(warmup_sessions + [target]))
    full_calendar = list(calendar)
    for session in extension:
        if session not in full_calendar:
            full_calendar.append(session)
    full_calendar = sorted(full_calendar)
    if full_calendar[-1] != target:
        raise ProspectiveRuntimeError("target session missing from extended calendar")

    decision_at = datetime.now(timezone.utc).isoformat()
    captured_at = (datetime.now(timezone.utc) + timedelta(milliseconds=1)).isoformat()
    result = dict(
        commit_fn(
            daily_raw=daily_raw,
            master_raw=master_raw,
            daily_retrieved_at=current_source["daily_retrieved_at"],
            master_retrieved_at=current_source["master_retrieved_at"],
            connectivity_evidence=evidence,
            history_raw=history_raw,
            supervised_frame=None,
            prebuilt_model_bundle=bundle,
            session_calendar=full_calendar,
            target_session=target,
            decision_at=decision_at,
            captured_at=captured_at,
            root=str(private_root / "sessions"),
            git_worktree=str(code),
        )
    )
    if result.get("structural_session_committed") is not True:
        raise ProspectiveRuntimeError("structural session did not commit")
    if result.get("live_order_authorized") is not False:
        raise ProspectiveRuntimeError("runtime unexpectedly gained live authority")

    anchor = _public_anchor_manifest(result, decision_at)
    _atomic_json(
        private_root / "public" / f"anchor-{target}.json",
        anchor,
        mode=0o600,
    )
    _atomic_json(private_root / "public" / "anchor-latest.json", anchor, mode=0o600)
    return _write_status(
        private_root,
        status="STRUCTURAL_SESSION_COMMITTED_NOT_ADMITTED",
        target_session=target,
        checked_at=datetime.now(timezone.utc).isoformat(),
        session_manifest_sha256=result["session_manifest_sha256"],
        decision_capture_sha256=result["decision_capture_sha256"],
        model_bundle_sha256=result["model_bundle_sha256"],
    )


class _RuntimeState:
    def __init__(self, *, pit_root: str, code_root: str):
        self.pit_root = pit_root
        self.code_root = code_root
        self.lock = threading.Lock()
        self.last_attempt: datetime | None = None

    @property
    def private_root(self) -> Path:
        return Path(self.pit_root).resolve() / PRIVATE_DIR_NAME

    def maybe_capture(self) -> None:
        now = datetime.now(timezone.utc)
        if not _capture_time_allowed(now):
            return
        with self.lock:
            if self.last_attempt is not None:
                if (now - self.last_attempt).total_seconds() < RETRY_SECONDS:
                    return
            self.last_attempt = now
            try:
                out = capture_current_session_once(
                    pit_root=self.pit_root,
                    code_root=self.code_root,
                    now_utc=now,
                )
                print(
                    "INDEXALERT_PROSPECTIVE_RUNTIME="
                    + json.dumps(out, ensure_ascii=False, sort_keys=True),
                    flush=True,
                )
            except Exception as exc:
                safe = {
                    "status": "CAPTURE_FAILED_CLOSED",
                    "error_class": type(exc).__name__,
                    "error": str(exc)[:500],
                    "ordering": "DISABLED",
                    "real_orders_authorized": False,
                    "funds_movement_authorized": False,
                    "broker_permission_change_authorized": False,
                    "fresh_alpha_observation_admitted": False,
                }
                try:
                    _write_status(self.private_root, **safe)
                except Exception:
                    pass
                print(
                    "INDEXALERT_PROSPECTIVE_RUNTIME="
                    + json.dumps(safe, ensure_ascii=False, sort_keys=True),
                    flush=True,
                )


def _handler(state: _RuntimeState):
    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, status: int, value: Mapping[str, Any]):
            body = _canonical(dict(value)) + b"\n"
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "runtime": "INDEXALERT_PROSPECTIVE_CAPTURE_v1",
                        "ordering": "DISABLED",
                        "real_orders_authorized": False,
                    },
                )
                return
            if self.path == "/status":
                try:
                    self._send_json(200, _safe_status(state.private_root))
                except Exception:
                    self._send_json(
                        503,
                        {
                            "status": "STATUS_UNAVAILABLE",
                            "ordering": "DISABLED",
                            "real_orders_authorized": False,
                        },
                    )
                return
            if self.path == "/anchor/latest":
                path = state.private_root / "public" / "anchor-latest.json"
                if not path.is_file() or path.is_symlink():
                    self._send_json(
                        404,
                        {
                            "status": "NO_ANCHOR",
                            "ordering": "DISABLED",
                            "real_orders_authorized": False,
                        },
                    )
                    return
                self._send_json(200, _load_json(path))
                return
            self._send_json(404, {"status": "NOT_FOUND"})

        def do_POST(self):
            self._send_json(
                405,
                {
                    "status": "MUTATION_FORBIDDEN",
                    "ordering": "DISABLED",
                    "real_orders_authorized": False,
                },
            )

        def log_message(self, format, *args):
            return

    return Handler


def _scheduler(state: _RuntimeState) -> None:
    while True:
        state.maybe_capture()
        time.sleep(SCHEDULER_POLL_SECONDS)


def serve(*, pit_root: str, code_root: str, port: int) -> None:
    state = _RuntimeState(pit_root=pit_root, code_root=code_root)
    thread = threading.Thread(target=_scheduler, args=(state,), daemon=True)
    thread.start()
    server = ThreadingHTTPServer(("0.0.0.0", port), _handler(state))
    server.serve_forever()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pit-root", default=os.getenv("INDEXALERT_PIT_ROOT", PIT_ROOT_DEFAULT))
    parser.add_argument("--code-root", default=os.getenv("INDEXALERT_CODE_ROOT", "/app"))
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")))
    args = parser.parse_args(argv)
    if args.once:
        out = capture_current_session_once(
            pit_root=args.pit_root,
            code_root=args.code_root,
        )
        print(
            "INDEXALERT_PROSPECTIVE_RUNTIME="
            + json.dumps(out, ensure_ascii=False, sort_keys=True),
            flush=True,
        )
        return 0
    serve(pit_root=args.pit_root, code_root=args.code_root, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
