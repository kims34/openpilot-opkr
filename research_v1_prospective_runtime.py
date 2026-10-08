"""Read-only prospective H5 session runtime.

Production intent:
- run only after the KRX close/finality buffer (18:30 KST or later);
- use the immutable verified PIT history only as prior-session warmup;
- fetch only official KRX OpenAPI daily-trade/security-master reads;
- bind the pinned block16 model bundle without refitting;
- append one immutable structural session record under a private Railway volume;
- never access broker APIs, submit orders, move funds, or grant Alpha authority.

A committed structural session is still NOT independently source/model/chronology
admitted and is NOT Fresh Alpha evidence.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd

from research_v1_krx_historical_fetchers import fetch_openapi_raw
from research_v1_krx_official_status import (
    KRX_OPENAPI_BASIC_SOURCE,
    normalise_basic_info,
)
from research_v1_krx_openapi_connectivity_evidence import validate_evidence
from research_v1_krx_openapi_prospective_source import _number, _short_code
from research_v1_prospective_frozen_producer import _session_calendar
from research_v1_prospective_model_bundle import validate_model_bundle
from research_v1_prospective_session_commit import (
    ProspectiveSessionCommitError,
    commit_structural_prospective_session,
    validate_session_manifest,
)


DAILY_ENDPOINT = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
MASTER_ENDPOINT = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info"
MODEL_BUNDLE_FILE = "frozen_block16_model_bundle_36643183157.json"
CALENDAR_PREFIX_FILE = "frozen_supervised_session_calendar_36643183157.json"
CONNECTIVITY_EVIDENCE_FILE = "INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json"

EXPECTED_MODEL_SHA256 = "2557663c1055f096be10b5a04890c89a8dfa48a49a7d24faf92ba5276f476531"
EXPECTED_CALENDAR_PAYLOAD_SHA256 = "852f25e6f43e3c1df6dd201604eab5fea9ec1bd7b7468b9dea30eac3fe334ee3"
EXPECTED_CALENDAR_ORIGIN = "2015-07-10"
EXPECTED_CALENDAR_END = "2026-09-16"
EXPECTED_CALENDAR_COUNT = 2745
EXPECTED_LONG_SOURCE_END = "2026-09-23"
EXPECTED_LONG_SOURCE_FINGERPRINT = {
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
LONG_DIR_NAME = "marcap_kospi_pit_long_verified_36643183157"
LONG_VERIFICATION_FILE = "frozen_long_history_verification.json"
NETWORK_AUTH_VALUE = "READ_ONLY_KRX_PROSPECTIVE_V1"
FINALITY_TIME_KST = time(18, 30)
HISTORY_LOOKBACK_DAYS = 70
MIN_HISTORY_SESSIONS = 25

RAW_COLUMNS = (
    "decision_date", "symbol", "open", "high", "low", "close",
    "volume", "value", "krx_change_return", "available_at",
)


class ProspectiveRuntimeError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _read_json(path: Path, field: str) -> Mapping[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ProspectiveRuntimeError(f"{field} is missing or unsafe")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProspectiveRuntimeError(f"{field} is invalid JSON") from exc
    if not isinstance(value, Mapping):
        raise ProspectiveRuntimeError(f"{field} must be a JSON object")
    return value


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on", "enabled"}


def require_read_only_runtime_authority(environment: Mapping[str, str]) -> str:
    """Return KRX key only when this process is strictly data-read-only."""
    if environment.get("INDEXALERT_PROSPECTIVE_NETWORK_AUTHORIZED") != NETWORK_AUTH_VALUE:
        raise ProspectiveRuntimeError("read-only KRX prospective network authority is absent")
    for field in (
        "REAL_ORDERS_AUTHORIZED", "FUNDS_MOVEMENT_AUTHORIZED",
        "PERMISSION_CHANGE_AUTHORIZED",
    ):
        if _truthy(environment.get(field)):
            raise ProspectiveRuntimeError(f"{field} must remain false")
    ordering = str(environment.get("ORDERING") or "DISABLED").strip().upper()
    if ordering != "DISABLED":
        raise ProspectiveRuntimeError("ORDERING must remain DISABLED")
    key = str(environment.get("KRX_AUTH_KEY") or "").strip()
    if not key:
        raise ProspectiveRuntimeError("KRX_AUTH_KEY is absent")
    return key


def load_pinned_model_bundle(code_root: Path) -> dict[str, Any]:
    bundle = dict(_read_json(code_root / MODEL_BUNDLE_FILE, "pinned model bundle"))
    checked = validate_model_bundle(bundle)
    if checked["model_bundle_sha256"] != EXPECTED_MODEL_SHA256:
        raise ProspectiveRuntimeError("pinned model bundle identity mismatch")
    if bundle.get("independent_model_admission_verified") is not False:
        raise ProspectiveRuntimeError("pinned model must remain unadmitted")
    if bundle.get("live_order_authorized") is not False:
        raise ProspectiveRuntimeError("pinned model cannot authorize live orders")
    return bundle


def load_calendar_prefix(code_root: Path) -> list[str]:
    wrapper = _read_json(code_root / CALENDAR_PREFIX_FILE, "calendar prefix")
    if wrapper.get("classification") != "FROZEN_SUPERVISED_SESSION_CALENDAR_RUNTIME_PREFIX":
        raise ProspectiveRuntimeError("calendar wrapper classification mismatch")
    if wrapper.get("payload_sha256") != EXPECTED_CALENDAR_PAYLOAD_SHA256:
        raise ProspectiveRuntimeError("calendar wrapper expected hash mismatch")
    calendar = wrapper.get("calendar")
    if not isinstance(calendar, Mapping):
        raise ProspectiveRuntimeError("calendar payload missing")
    actual = hashlib.sha256(_canonical(calendar)).hexdigest()
    if actual != EXPECTED_CALENDAR_PAYLOAD_SHA256:
        raise ProspectiveRuntimeError("calendar payload fingerprint mismatch")
    sessions = calendar.get("sessions")
    if (
        calendar.get("reference_action_id") != 36643183157
        or calendar.get("origin_session") != EXPECTED_CALENDAR_ORIGIN
        or calendar.get("end_session") != EXPECTED_CALENDAR_END
        or calendar.get("session_count") != EXPECTED_CALENDAR_COUNT
        or not isinstance(sessions, list)
        or len(sessions) != EXPECTED_CALENDAR_COUNT
    ):
        raise ProspectiveRuntimeError("calendar prefix metadata mismatch")
    _session_calendar(sessions)
    return list(sessions)


def verify_long_history_root(verified_root: Path) -> tuple[Path, pd.Timestamp]:
    long_dir = verified_root / LONG_DIR_NAME
    record = _read_json(long_dir / LONG_VERIFICATION_FILE, "long-history verification")
    if record.get("classification") != "FROZEN_LONG_HISTORY_SOURCE_REHYDRATION_VERIFIED":
        raise ProspectiveRuntimeError("long-history verification classification mismatch")
    if record.get("fingerprint_exact_match") is not True:
        raise ProspectiveRuntimeError("long-history source is not exact-match verified")
    if record.get("source_fingerprint") != EXPECTED_LONG_SOURCE_FINGERPRINT:
        raise ProspectiveRuntimeError("long-history source fingerprint mismatch")
    for field in (
        "consumed_v1_holdout_read", "performance_evaluation_executed",
        "model_fit_executed", "historical_backfill_decisions_created",
        "fresh_alpha_observation_admitted", "promotion_authority",
        "live_order_authorized",
    ):
        if record.get(field) is not False:
            raise ProspectiveRuntimeError(f"unsafe long-history verification field: {field}")
    if not long_dir.is_dir() or long_dir.is_symlink():
        raise ProspectiveRuntimeError("verified long-history directory missing")
    return long_dir, pd.Timestamp(EXPECTED_LONG_SOURCE_END)


def _kst_now() -> pd.Timestamp:
    return pd.Timestamp.now(tz="Asia/Seoul")


def resolve_target_session(now_kst: pd.Timestamp) -> str:
    if now_kst.tzinfo is None:
        raise ProspectiveRuntimeError("runtime clock must be timezone-aware")
    local = now_kst.tz_convert("Asia/Seoul")
    if local.time() < FINALITY_TIME_KST:
        raise ProspectiveRuntimeError("current session is before 18:30 KST finality buffer")
    return local.strftime("%Y-%m-%d")


def _weekday_dates(start: pd.Timestamp, end: pd.Timestamp) -> list[pd.Timestamp]:
    if start > end:
        return []
    days = pd.date_range(start.normalize(), end.normalize(), freq="D")
    return [d for d in days if d.weekday() < 5]


def _fetch_daily(day: pd.Timestamp, *, auth_key: str):
    return fetch_openapi_raw(
        endpoint=DAILY_ENDPOINT,
        params={"basDd": day.strftime("%Y%m%d")},
        auth_key=auth_key,
        network_authorized=True,
    )


def _fetch_master(day: pd.Timestamp, *, auth_key: str):
    return fetch_openapi_raw(
        endpoint=MASTER_ENDPOINT,
        params={"basDd": day.strftime("%Y%m%d")},
        auth_key=auth_key,
        network_authorized=True,
    )


def _current_common_master(master_frame: pd.DataFrame, *, target: pd.Timestamp, available_at: str) -> pd.DataFrame:
    identity = normalise_basic_info(
        master_frame,
        asof_date=target,
        available_at=available_at,
        source=KRX_OPENAPI_BASIC_SOURCE,
    )
    market = identity["market_type_official"].astype(str)
    common = identity[
        identity["common_stock_identity_official"].eq(True)
        & (market.str.upper().str.contains("KOSPI", na=False) | market.str.contains("유가증권", na=False))
    ].copy()
    if common.empty or common["symbol"].duplicated().any():
        raise ProspectiveRuntimeError("current common-stock master is empty or duplicated")
    return common.sort_values("symbol").reset_index(drop=True)


def _normalise_extension_day(
    frame: pd.DataFrame,
    *,
    session: pd.Timestamp,
    retrieved_at: str,
    current_common: pd.DataFrame,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=RAW_COLUMNS)
    required = {
        "BAS_DD", "ISU_CD", "TDD_OPNPRC", "TDD_HGPRC", "TDD_LWPRC",
        "TDD_CLSPRC", "ACC_TRDVOL", "ACC_TRDVAL", "FLUC_RT",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ProspectiveRuntimeError(f"daily extension missing fields: {missing}")
    bas = session.strftime("%Y%m%d")
    if not frame["BAS_DD"].astype("string").str.strip().eq(bas).all():
        raise ProspectiveRuntimeError("daily extension session mismatch")
    daily = pd.DataFrame({
        "decision_date": session.normalize(),
        "symbol": _short_code(frame["ISU_CD"], "daily.ISU_CD"),
        "open": _number(frame["TDD_OPNPRC"], "TDD_OPNPRC"),
        "high": _number(frame["TDD_HGPRC"], "TDD_HGPRC"),
        "low": _number(frame["TDD_LWPRC"], "TDD_LWPRC"),
        "close": _number(frame["TDD_CLSPRC"], "TDD_CLSPRC"),
        "volume": _number(frame["ACC_TRDVOL"], "ACC_TRDVOL"),
        "value": _number(frame["ACC_TRDVAL"], "ACC_TRDVAL"),
        "krx_change_return": _number(frame["FLUC_RT"], "FLUC_RT") / 100.0,
    })
    if daily["symbol"].duplicated().any():
        raise ProspectiveRuntimeError("daily extension has duplicate symbols")
    scope = current_common[
        current_common["listing_date_official"].le(session.normalize())
    ][["symbol", "listing_date_official"]].copy()
    expected = set(scope["symbol"].astype(str))
    merged = daily.merge(scope, on="symbol", how="inner", validate="one_to_one")
    actual = set(merged["symbol"].astype(str))
    missing_current = sorted(expected - actual)
    if missing_current:
        raise ProspectiveRuntimeError(
            "current common-stock warmup history is incomplete; "
            f"missing {len(missing_current)} eligible symbols"
        )
    if (merged[["open", "high", "low", "close"]] <= 0).any().any():
        raise ProspectiveRuntimeError("warmup daily data contains nonpositive OHLC")
    if (merged[["volume", "value"]] < 0).any().any():
        raise ProspectiveRuntimeError("warmup daily data contains negative volume/value")
    if (
        (merged["low"] > merged[["open", "close"]].min(axis=1))
        | (merged["high"] < merged[["open", "close"]].max(axis=1))
        | (merged["low"] > merged["high"])
    ).any():
        raise ProspectiveRuntimeError("warmup daily data has inconsistent OHLC")
    if (merged["krx_change_return"] <= -1.0).any():
        raise ProspectiveRuntimeError("warmup daily return is invalid")
    merged["available_at"] = pd.Timestamp(retrieved_at).isoformat()
    return merged[list(RAW_COLUMNS)].sort_values("symbol").reset_index(drop=True)


def _load_verified_history(
    long_dir: Path,
    *,
    target: pd.Timestamp,
    current_common: pd.DataFrame,
    availability_at: str,
) -> tuple[pd.DataFrame, list[str]]:
    parquet = long_dir / f"kospi-pit-{target.year}.parquet"
    if not parquet.is_file():
        # Current target can be after the frozen source year only after a future
        # refit; for block16 in 2026 this file must exist.
        parquet = long_dir / "kospi-pit-2026.parquet"
    if not parquet.is_file() or parquet.is_symlink():
        raise ProspectiveRuntimeError("verified warmup parquet is missing")
    frame = pd.read_parquet(parquet)
    required = set(RAW_COLUMNS[:-1])
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ProspectiveRuntimeError(f"verified history missing columns: {missing}")
    frame["decision_date"] = pd.to_datetime(frame["decision_date"], errors="raise").dt.normalize()
    source_end = pd.Timestamp(EXPECTED_LONG_SOURCE_END)
    cutoff = target - pd.Timedelta(days=HISTORY_LOOKBACK_DAYS)
    frame = frame[
        frame["decision_date"].between(cutoff, min(target - pd.Timedelta(days=1), source_end))
    ].copy()
    common_symbols = set(current_common["symbol"].astype(str))
    frame = frame[frame["symbol"].astype(str).isin(common_symbols)].copy()
    if frame.empty:
        raise ProspectiveRuntimeError("verified warmup history is empty")
    frame["symbol"] = frame["symbol"].astype(str)
    frame["available_at"] = pd.Timestamp(availability_at).isoformat()
    dates = sorted(frame["decision_date"].drop_duplicates())
    return frame[list(RAW_COLUMNS)].sort_values(["decision_date", "symbol"]).reset_index(drop=True), [
        pd.Timestamp(d).strftime("%Y-%m-%d") for d in dates
    ]


def _atomic_anchor_payload(root: Path, *, session: str, result: Mapping[str, Any], decision_at: str) -> Path:
    body = {
        "classification": "PROSPECTIVE_ANCHOR_PAYLOAD_NOT_ADMISSION",
        "session": session,
        "decision_at": decision_at,
        "source_receipt_sha256": result["source_receipt_sha256"],
        "input_snapshot_sha256": result["input_snapshot_sha256"],
        "producer_binding_sha256": result["producer_binding_sha256"],
        "model_bundle_sha256": result["model_bundle_sha256"],
        "decision_capture_sha256": result["decision_capture_sha256"],
        "session_manifest_sha256": result["session_manifest_sha256"],
        "independent_chronology_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }
    body["anchor_payload_sha256"] = hashlib.sha256(_canonical(body)).hexdigest()
    payload = _canonical(body) + b"\n"
    target = root / f"anchor-payload-{session}.json"
    fd, name = tempfile.mkstemp(prefix=".anchor-payload-", dir=root)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o600)
        try:
            os.link(temp, target)
        except FileExistsError:
            if target.is_symlink() or target.read_bytes() != payload:
                raise ProspectiveRuntimeError("conflicting same-session anchor payload")
        directory = os.open(root, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temp.unlink(missing_ok=True)
    return target


def run_once(
    *,
    code_root: Path,
    verified_root: Path,
    private_root: Path,
    git_worktree: Path,
    environment: Mapping[str, str],
    now_kst: pd.Timestamp | None = None,
) -> dict[str, Any]:
    auth_key = require_read_only_runtime_authority(environment)
    now_kst = _kst_now() if now_kst is None else now_kst
    target_text = resolve_target_session(now_kst)
    target = pd.Timestamp(target_text)

    private_root.mkdir(parents=True, exist_ok=True)
    existing_manifest = private_root / f"session-{target_text}.json"
    if existing_manifest.exists():
        existing = _read_json(existing_manifest, "existing session manifest")
        checked = validate_session_manifest(existing)
        return {
            "status": "ALREADY_COMMITTED",
            "session": target_text,
            "session_manifest_sha256": checked["session_manifest_sha256"],
            "fresh_alpha_observation_admitted": False,
            "live_order_authorized": False,
        }

    bundle = load_pinned_model_bundle(code_root)
    prefix = load_calendar_prefix(code_root)
    long_dir, source_end = verify_long_history_root(verified_root)
    evidence = dict(_read_json(code_root / CONNECTIVITY_EVIDENCE_FILE, "KRX connectivity evidence"))
    validate_evidence(evidence)

    master_fetch = _fetch_master(target, auth_key=auth_key)
    current_common = _current_common_master(
        master_fetch.response_frame,
        target=target,
        available_at=master_fetch.retrieved_at,
    )

    fetch_start = min(
        source_end + pd.Timedelta(days=1),
        target - pd.Timedelta(days=HISTORY_LOOKBACK_DAYS),
    )
    daily_results: dict[str, Any] = {}
    for day in _weekday_dates(fetch_start, target):
        fetched = _fetch_daily(day, auth_key=auth_key)
        if fetched.response_frame.empty:
            continue
        daily_results[day.strftime("%Y-%m-%d")] = fetched

    current = daily_results.get(target_text)
    if current is None:
        return {
            "status": "NO_MARKET_SESSION",
            "session": target_text,
            "fresh_alpha_observation_admitted": False,
            "live_order_authorized": False,
        }

    observed_at = max(
        pd.Timestamp(master_fetch.retrieved_at),
        *(pd.Timestamp(v.retrieved_at) for v in daily_results.values()),
    ).tz_convert("UTC")
    verified_history, verified_dates = _load_verified_history(
        long_dir,
        target=target,
        current_common=current_common,
        availability_at=observed_at.isoformat(),
    )

    extension_frames = []
    extension_dates = []
    for session_text, fetched in sorted(daily_results.items()):
        day = pd.Timestamp(session_text)
        if day > source_end and day < target:
            extension_frames.append(
                _normalise_extension_day(
                    fetched.response_frame,
                    session=day,
                    retrieved_at=fetched.retrieved_at,
                    current_common=current_common,
                )
            )
            extension_dates.append(session_text)
    history = verified_history
    if extension_frames:
        history = pd.concat([history, *extension_frames], ignore_index=True)
    history = history.sort_values(["decision_date", "symbol"]).reset_index(drop=True)
    history_session_count = int(pd.to_datetime(history["decision_date"]).nunique())
    if history_session_count < MIN_HISTORY_SESSIONS:
        raise ProspectiveRuntimeError(
            f"insufficient warmup sessions: {history_session_count} < {MIN_HISTORY_SESSIONS}"
        )

    # Prefix is independently pinned through 2026-09-16. Extend it first with
    # exact verified long-history sessions through 2026-09-23, then with official
    # OpenAPI non-empty sessions through the target.
    verified_extension = [
        d for d in verified_dates
        if d > EXPECTED_CALENDAR_END and d <= EXPECTED_LONG_SOURCE_END
    ]
    online_extension = sorted(
        d for d in daily_results
        if d > EXPECTED_LONG_SOURCE_END and d <= target_text
    )
    session_calendar = list(dict.fromkeys(prefix + verified_extension + online_extension))
    _session_calendar(session_calendar)
    if session_calendar[-1] != target_text:
        raise ProspectiveRuntimeError("target is not the latest validated market session")

    decision_at = pd.Timestamp.now(tz="UTC").isoformat()
    result = commit_structural_prospective_session(
        daily_raw=current.raw_bytes,
        master_raw=master_fetch.raw_bytes,
        daily_retrieved_at=current.retrieved_at,
        master_retrieved_at=master_fetch.retrieved_at,
        connectivity_evidence=evidence,
        history_raw=history,
        supervised_frame=None,
        prebuilt_model_bundle=bundle,
        session_calendar=session_calendar,
        target_session=target_text,
        decision_at=decision_at,
        captured_at=decision_at,
        root=str(private_root),
        git_worktree=str(git_worktree),
    )
    _atomic_anchor_payload(
        private_root,
        session=target_text,
        result=result,
        decision_at=decision_at,
    )
    return {
        "status": "STRUCTURAL_SESSION_COMMITTED",
        "session": target_text,
        "history_sessions": history_session_count,
        "session_calendar_count": len(session_calendar),
        "source_receipt_sha256": result["source_receipt_sha256"],
        "input_snapshot_sha256": result["input_snapshot_sha256"],
        "producer_binding_sha256": result["producer_binding_sha256"],
        "model_bundle_sha256": result["model_bundle_sha256"],
        "decision_capture_sha256": result["decision_capture_sha256"],
        "session_manifest_sha256": result["session_manifest_sha256"],
        "chronology_anchor_pending": True,
        "independent_source_admission_verified": False,
        "independent_model_admission_verified": False,
        "independent_chronology_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verified-root",
        default=os.getenv(
            "INDEXALERT_VERIFIED_PIT_ROOT", "/pit/frozen_rerun_20261008"
        ),
    )
    parser.add_argument(
        "--private-root",
        default=os.getenv(
            "INDEXALERT_PROSPECTIVE_PRIVATE_ROOT", "/pit/prospective_runtime"
        ),
    )
    parser.add_argument(
        "--git-worktree",
        default=os.getenv("INDEXALERT_GIT_WORKTREE", "/app"),
    )
    args = parser.parse_args()
    try:
        result = run_once(
            code_root=Path(__file__).resolve().parent,
            verified_root=Path(args.verified_root),
            private_root=Path(args.private_root),
            git_worktree=Path(args.git_worktree),
            environment=os.environ,
        )
    except (ProspectiveRuntimeError, ProspectiveSessionCommitError) as exc:
        print(
            "INDEXALERT_PROSPECTIVE_RUNTIME="
            + json.dumps(
                {
                    "status": "FAIL_CLOSED",
                    "error_class": type(exc).__name__,
                    "detail": str(exc),
                    "ORDERING": "DISABLED",
                    "REAL_ORDERS_AUTHORIZED": False,
                    "FUNDS_MOVEMENT_AUTHORIZED": False,
                    "PERMISSION_CHANGE_AUTHORIZED": False,
                    "fresh_alpha_observation_admitted": False,
                    "live_order_authorized": False,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        raise
    print(
        "INDEXALERT_PROSPECTIVE_RUNTIME="
        + json.dumps(result, sort_keys=True),
        flush=True,
    )


if __name__ == "__main__":
    main()
