"""Rehydrate the exact frozen supervised cache from the verified long history.

This is deterministic source/label/feature reconstruction only. It does not run
the frozen model, compute performance, inspect the consumed holdout artifact, or
admit/promote any Alpha result.

The source panel must already be the exact long-history reconstruction verified
against Action 36643183157. The supervised cache is built with vendored copies
of the exact modules from Action head 4df26b6f... and is published only if its
metadata/diagnostics exactly equal the supervised_cache object recovered from
that Action artifact.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Mapping

import numpy as np
import pandas as pd

from rehydrate_frozen_long_history import (
    FINAL_DIR_NAME as LONG_HISTORY_DIR_NAME,
    VERIFICATION_FILE as LONG_HISTORY_VERIFICATION_FILE,
    EXPECTED_SOURCE_FINGERPRINT,
    load_panel as load_long_history_panel,
    source_fingerprint as long_history_fingerprint,
    validate_verification as validate_long_history_verification,
)


FROZEN_ACTION_ID = 36643183157
FROZEN_ARTIFACT_ID = 11067383547
FROZEN_ARTIFACT_DIGEST = (
    "sha256:c8dd6a016103cf33d9219622f416fda25715c1cac19b371714d9308f2cb2c26f"
)
FROZEN_RUN_HEAD_SHA = "4df26b6f5d2d9e645cd2c0242c9ac8cefb747a9d"
FROZEN_MODULE_DIR_NAME = "frozen_supervised_v1"
REFERENCE_FILE_NAME = "frozen_supervised_reference_36643183157.json"
FINAL_DIR_NAME = "supervised_frozen_verified_36643183157"
ATTEMPT_PARENT_NAME = "frozen_supervised_rehydration_attempts"
VERIFICATION_FILE = "frozen_supervised_verification.json"

FROZEN_MODULE_BLOBS = {
    "research_v1_supervised_cache.py": "799d5b424c4055289f3d7b54fa03ecbb467dbb1f",
    "research_v1_core.py": "7aaa01338b11c119497050282b53fcf7d13a2b8d",
    "research_v1_pit_labels.py": "91ef828617ea77713f1ddca0c427fadaf1114f0a",
    "research_v1_pit_features.py": "421e243ae8cea7c1bc02bc4564d13f76974c660e",
    "research_v1_data_policy.py": "51105bca61ef9f7479a0b61ec08a43d01f147940",
}
FROZEN_RUNTIME = {
    "python": "3.12.14",
    "pandas": "2.3.3",
    "numpy": "2.5.3",
    "pyarrow": "21.0.0",
}


class FrozenSupervisedRehydrationError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def validate_frozen_modules(base: Path) -> dict[str, str]:
    module_dir = base / FROZEN_MODULE_DIR_NAME
    if not module_dir.is_dir() or module_dir.is_symlink():
        raise FrozenSupervisedRehydrationError("frozen module directory missing")
    actual: dict[str, str] = {}
    for name, expected in FROZEN_MODULE_BLOBS.items():
        path = module_dir / name
        if not path.is_file() or path.is_symlink():
            raise FrozenSupervisedRehydrationError(f"frozen module missing: {name}")
        digest = _git_blob_sha1(path.read_bytes())
        if digest != expected:
            raise FrozenSupervisedRehydrationError(
                f"frozen module drift: {name} {digest} != {expected}"
            )
        actual[name] = digest
    return actual


def validate_runtime() -> dict[str, str]:
    import pyarrow

    versions = {
        "python": ".".join(map(str, sys.version_info[:3])),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "pyarrow": pyarrow.__version__,
    }
    if versions != FROZEN_RUNTIME:
        raise FrozenSupervisedRehydrationError(
            f"frozen runtime mismatch: {versions} != {FROZEN_RUNTIME}"
        )
    return versions


def load_reference(base: Path) -> tuple[dict[str, Any], str]:
    path = base / REFERENCE_FILE_NAME
    if not path.is_file() or path.is_symlink():
        raise FrozenSupervisedRehydrationError("frozen supervised reference missing")
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise FrozenSupervisedRehydrationError(
            "frozen supervised reference is invalid"
        ) from exc
    if not isinstance(value, dict):
        raise FrozenSupervisedRehydrationError(
            "frozen supervised reference must be an object"
        )
    expected_top = {
        "version": "pit-supervised-cache-v3-ca-safe-source-fingerprint",
        "feature_return_policy": "KRX_FLUC_RT_BASE_PRICE_ADJUSTED_FOR_CORPORATE_ACTIONS",
        "source_fingerprint": EXPECTED_SOURCE_FINGERPRINT,
        "horizon": 5,
        "target_return": 0.04,
        "stop_return": -0.025,
        "participation": 0.0005,
        "commission_round_trip_bps": 3.0,
        "rows": 2486909,
        "records": 2484241,
    }
    for key, expected in expected_top.items():
        if value.get(key) != expected:
            raise FrozenSupervisedRehydrationError(
                f"frozen supervised reference drift: {key}"
            )
    diagnostics = value.get("diagnostics")
    if not isinstance(diagnostics, dict):
        raise FrozenSupervisedRehydrationError("reference diagnostics missing")
    exact_diag = {
        "ambiguous_same_bar": 55604,
        "entry_no_fill": 2668,
        "entry_no_fill_retained_in_decision_universe": 2668,
        "post_entry_missing_future_bar_conservative_stop": 7274,
        "insufficient_global_future_horizon": 4561,
        "eligible_rows_with_labels": 2484241,
        "eligible_rows_without_label_no_fill": 2668,
        "feature_return_policy": "KRX_FLUC_RT_BASE_PRICE_ADJUSTED_FOR_CORPORATE_ACTIONS",
        "ambiguity_policy": "stop_first_conservative",
        "entry_no_fill_policy": "retain_for_ranking_leave_slot_empty_no_retroactive_backfill",
        "post_entry_gap_policy": "planned_stop_on_first_missing_market_session_preliminary",
        "cost_policy": "historical_KOSPI_statutory_sell_tax_by_exact_entry_date_plus_round_trip_commission",
        "half_spread_bps_one_way": 4.0,
        "commission_round_trip_bps": 3.0,
        "fixed_explicit_bps_override": None,
    }
    for key, expected in exact_diag.items():
        if diagnostics.get(key) != expected:
            raise FrozenSupervisedRehydrationError(
                f"frozen diagnostic reference drift: {key}"
            )
    return value, hashlib.sha256(raw).hexdigest()


def require_exact_meta(meta: Mapping[str, Any], reference: Mapping[str, Any]) -> None:
    if not isinstance(meta, Mapping):
        raise FrozenSupervisedRehydrationError("supervised meta must be an object")
    if dict(meta) != dict(reference):
        differences = {}
        for key in sorted(set(meta) | set(reference)):
            if meta.get(key) != reference.get(key):
                differences[key] = {
                    "expected": reference.get(key),
                    "actual": meta.get(key),
                }
        raise FrozenSupervisedRehydrationError(
            "frozen supervised metadata mismatch: "
            + json.dumps(differences, ensure_ascii=False, sort_keys=True)[:12000]
        )


def supervised_logical_fingerprint(frame: pd.DataFrame) -> dict[str, Any]:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise FrozenSupervisedRehydrationError("nonempty supervised frame required")
    if "decision_date" not in frame or "symbol" not in frame:
        raise FrozenSupervisedRehydrationError(
            "supervised frame lacks decision_date/symbol"
        )
    work = frame.copy()
    dates = pd.to_datetime(work["decision_date"], errors="coerce")
    if dates.isna().any() or dates.dt.tz is not None:
        raise FrozenSupervisedRehydrationError("invalid supervised decision_date")
    work["decision_date"] = dates
    work["symbol"] = work["symbol"].astype(str)
    work = work.sort_values(["decision_date", "symbol"], kind="mergesort").reset_index(drop=True)
    hashes = pd.util.hash_pandas_object(work, index=False).to_numpy(dtype=np.uint64)
    xor_hash = int(np.bitwise_xor.reduce(hashes)) if len(hashes) else 0
    sum_hash = int(hashes.sum(dtype=np.uint64)) if len(hashes) else 0
    rec_rows = (
        int(work["rec_outcome"].notna().sum())
        if "rec_outcome" in work.columns
        else 0
    )
    return {
        "rows": int(len(work)),
        "columns": list(work.columns),
        "dtypes": [str(work[c].dtype) for c in work.columns],
        "date_min": str(work["decision_date"].min().date()),
        "date_max": str(work["decision_date"].max().date()),
        "symbols": int(work["symbol"].nunique()),
        "record_rows": rec_rows,
        "hash_xor_u64": str(xor_hash),
        "hash_sum_u64": str(sum_hash),
    }


def _attach_record_columns_low_memory(
    frame: pd.DataFrame,
    record_map: Mapping[Any, Any],
) -> pd.DataFrame:
    """Attach frozen DecisionRecord fields without a multi-million dict-list.

    The frozen cache wrapper built a rec_rows list and merged it back into the
    already-sorted feature frame.  That duplicates millions of Python dicts.
    Here we allocate typed output columns once and perform exact key lookups.
    The resulting cache schema/values are checked against the recovered Action
    metadata before publication.
    """
    n = len(frame)
    entry_day = np.full(n, np.datetime64("NaT"), dtype="datetime64[ns]")
    entry_price = np.full(n, np.nan, dtype=np.float64)
    horizon = np.full(n, np.nan, dtype=np.float64)
    target_return = np.full(n, np.nan, dtype=np.float64)
    stop_return = np.full(n, np.nan, dtype=np.float64)
    cost_return = np.full(n, np.nan, dtype=np.float64)
    outcome = np.empty(n, dtype=object)
    outcome[:] = None
    gross_return = np.full(n, np.nan, dtype=np.float64)
    net_return = np.full(n, np.nan, dtype=np.float64)
    exit_day = np.full(n, np.datetime64("NaT"), dtype="datetime64[ns]")
    exit_price = np.full(n, np.nan, dtype=np.float64)

    matched = 0
    for i, (decision_day, symbol) in enumerate(
        frame[["decision_date", "symbol"]].itertuples(index=False, name=None)
    ):
        rec = record_map.get((pd.Timestamp(decision_day).date(), str(symbol)))
        if rec is None:
            continue
        matched += 1
        entry_day[i] = np.datetime64(pd.Timestamp(rec.entry_day), "ns")
        entry_price[i] = float(rec.entry_price)
        horizon[i] = float(rec.horizon)
        target_return[i] = float(rec.target_return)
        stop_return[i] = float(rec.stop_return)
        cost_return[i] = float(rec.cost_return)
        outcome[i] = str(rec.outcome)
        gross_return[i] = float(rec.gross_return)
        net_return[i] = float(rec.net_return)
        exit_day[i] = np.datetime64(pd.Timestamp(rec.exit_day), "ns")
        exit_price[i] = float(rec.exit_price)

    if matched != len(record_map):
        raise FrozenSupervisedRehydrationError(
            f"record-map attachment mismatch: matched={matched} records={len(record_map)}"
        )

    frame["rec_entry_day"] = entry_day
    frame["rec_entry_price"] = entry_price
    frame["rec_horizon"] = horizon
    frame["rec_target_return"] = target_return
    frame["rec_stop_return"] = stop_return
    frame["rec_cost_return"] = cost_return
    frame["rec_outcome"] = outcome
    frame["rec_gross_return"] = gross_return
    frame["rec_net_return"] = net_return
    frame["rec_exit_day"] = exit_day
    frame["rec_exit_price"] = exit_price
    return frame


def _build_cache_low_memory(
    raw: pd.DataFrame,
    cache_dir: Path,
    *,
    reference: Mapping[str, Any],
):
    """Execute exact frozen feature/label semantics with bounded cache assembly."""
    from research_v1_pit_labels import make_pit_supervised
    from research_v1_supervised_cache import (
        CACHE_VERSION,
        _source_fingerprint,
    )

    source_fingerprint = _source_fingerprint(raw)
    if source_fingerprint != reference["source_fingerprint"]:
        raise FrozenSupervisedRehydrationError(
            "source fingerprint changed before frozen supervised build"
        )

    frame, record_map, diagnostics = make_pit_supervised(
        raw,
        horizon=5,
        target_return=0.04,
        stop_return=-0.025,
        participation=0.0005,
        commission_round_trip_bps=3.0,
    )
    record_count = len(record_map)
    if record_count != reference["records"]:
        raise FrozenSupervisedRehydrationError(
            f"record_map count drift: {record_count} != {reference['records']}"
        )
    if diagnostics != reference["diagnostics"]:
        raise FrozenSupervisedRehydrationError("diagnostics object drift")

    frame = _attach_record_columns_low_memory(frame, record_map)
    del record_map
    gc.collect()

    cache_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = cache_dir / "supervised.parquet"
    frame.to_parquet(parquet_path, index=False)
    meta = {
        "version": CACHE_VERSION,
        "feature_return_policy": diagnostics.get("feature_return_policy"),
        "source_fingerprint": source_fingerprint,
        "horizon": 5,
        "target_return": 0.04,
        "stop_return": -0.025,
        "participation": 0.0005,
        "commission_round_trip_bps": 3.0,
        "rows": int(len(frame)),
        "records": int(record_count),
        "diagnostics": diagnostics,
    }
    require_exact_meta(meta, reference)
    (cache_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return frame, diagnostics, record_count


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_long_history(root: Path) -> tuple[pd.DataFrame, str]:
    directory = root / LONG_HISTORY_DIR_NAME
    verification_path = directory / LONG_HISTORY_VERIFICATION_FILE
    if (
        not directory.is_dir()
        or directory.is_symlink()
        or not verification_path.is_file()
        or verification_path.is_symlink()
    ):
        raise FrozenSupervisedRehydrationError(
            "verified frozen long-history directory is missing"
        )
    try:
        verification = json.loads(verification_path.read_text(encoding="utf-8"))
        validated = validate_long_history_verification(verification)
    except Exception as exc:
        raise FrozenSupervisedRehydrationError(
            "long-history verification is invalid"
        ) from exc
    panel = load_long_history_panel(directory)
    actual = long_history_fingerprint(panel)
    if actual != EXPECTED_SOURCE_FINGERPRINT:
        raise FrozenSupervisedRehydrationError(
            "long-history source fingerprint drift"
        )
    return panel, validated["verification_sha256"]


def _verification_body(
    *,
    long_history_verification_sha256: str,
    reference_sha256: str,
    module_blobs: Mapping[str, str],
    runtime_versions: Mapping[str, str],
    supervised_fingerprint: Mapping[str, Any],
    supervised_parquet_sha256: str,
    meta_sha256: str,
) -> dict[str, Any]:
    return {
        "classification": "FROZEN_SUPERVISED_CACHE_REHYDRATION_VERIFIED",
        "frozen_action_id": FROZEN_ACTION_ID,
        "frozen_artifact_id": FROZEN_ARTIFACT_ID,
        "frozen_artifact_digest": FROZEN_ARTIFACT_DIGEST,
        "frozen_run_head_sha": FROZEN_RUN_HEAD_SHA,
        "long_history_verification_sha256": long_history_verification_sha256,
        "reference_sha256": reference_sha256,
        "frozen_module_git_blobs": dict(module_blobs),
        "runtime_versions": dict(runtime_versions),
        "supervised_logical_fingerprint": dict(supervised_fingerprint),
        "supervised_parquet_sha256": supervised_parquet_sha256,
        "meta_sha256": meta_sha256,
        "exact_reference_meta_match": True,
        "consumed_holdout_artifact_read": False,
        "performance_evaluation_executed": False,
        "model_fit_executed": False,
        "historical_decision_backfill_created": False,
        "fresh_alpha_observation_admitted": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }


def validate_supervised_verification(record: Mapping[str, Any]) -> dict[str, Any]:
    if record.get("classification") != "FROZEN_SUPERVISED_CACHE_REHYDRATION_VERIFIED":
        raise FrozenSupervisedRehydrationError("verification classification mismatch")
    if record.get("frozen_action_id") != FROZEN_ACTION_ID:
        raise FrozenSupervisedRehydrationError("frozen action mismatch")
    if record.get("frozen_artifact_id") != FROZEN_ARTIFACT_ID:
        raise FrozenSupervisedRehydrationError("frozen artifact mismatch")
    if record.get("frozen_artifact_digest") != FROZEN_ARTIFACT_DIGEST:
        raise FrozenSupervisedRehydrationError("frozen artifact digest mismatch")
    if record.get("frozen_run_head_sha") != FROZEN_RUN_HEAD_SHA:
        raise FrozenSupervisedRehydrationError("frozen run head mismatch")
    if record.get("frozen_module_git_blobs") != FROZEN_MODULE_BLOBS:
        raise FrozenSupervisedRehydrationError("frozen module identity mismatch")
    if record.get("runtime_versions") != FROZEN_RUNTIME:
        raise FrozenSupervisedRehydrationError("frozen runtime mismatch")
    if record.get("exact_reference_meta_match") is not True:
        raise FrozenSupervisedRehydrationError("reference match must be exact true")
    for field in (
        "consumed_holdout_artifact_read",
        "performance_evaluation_executed",
        "model_fit_executed",
        "historical_decision_backfill_created",
        "fresh_alpha_observation_admitted",
        "promotion_authority",
        "live_order_authorized",
    ):
        if record.get(field) is not False:
            raise FrozenSupervisedRehydrationError(f"{field} must remain exact false")
    body = dict(record)
    digest = body.pop("verification_sha256", None)
    if type(digest) is not str or len(digest) != 64:
        raise FrozenSupervisedRehydrationError("verification_sha256 missing")
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if digest != actual:
        raise FrozenSupervisedRehydrationError("verification fingerprint mismatch")
    return {
        "valid": True,
        "verification_sha256": actual,
        "supervised_logical_fingerprint": record["supervised_logical_fingerprint"],
    }


def _write_verification(directory: Path, body: Mapping[str, Any]) -> dict[str, Any]:
    record = {
        **dict(body),
        "verification_sha256": hashlib.sha256(_canonical(body)).hexdigest(),
    }
    validate_supervised_verification(record)
    target = directory / VERIFICATION_FILE
    payload = _canonical(record) + b"\n"
    fd, name = tempfile.mkstemp(prefix=".supervised-verify-", dir=directory)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, target)
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temp.unlink(missing_ok=True)
    return record


def _verify_existing(
    final: Path,
    *,
    reference: Mapping[str, Any],
    reference_sha256: str,
    module_blobs: Mapping[str, str],
    runtime_versions: Mapping[str, str],
    long_history_verification_sha256: str,
) -> dict[str, Any]:
    verification_path = final / VERIFICATION_FILE
    meta_path = final / "meta.json"
    parquet_path = final / "supervised.parquet"
    if any(
        not p.is_file() or p.is_symlink()
        for p in (verification_path, meta_path, parquet_path)
    ):
        raise FrozenSupervisedRehydrationError(
            "existing supervised verified directory is incomplete"
        )
    record = json.loads(verification_path.read_text(encoding="utf-8"))
    validate_supervised_verification(record)
    if record["reference_sha256"] != reference_sha256:
        raise FrozenSupervisedRehydrationError("reference identity drift")
    if record["frozen_module_git_blobs"] != dict(module_blobs):
        raise FrozenSupervisedRehydrationError("module identity drift")
    if record["runtime_versions"] != dict(runtime_versions):
        raise FrozenSupervisedRehydrationError("runtime identity drift")
    if record["long_history_verification_sha256"] != long_history_verification_sha256:
        raise FrozenSupervisedRehydrationError("long-history parent identity drift")
    meta_raw = meta_path.read_bytes()
    meta = json.loads(meta_raw.decode("utf-8"))
    require_exact_meta(meta, reference)
    frame = pd.read_parquet(parquet_path)
    actual = supervised_logical_fingerprint(frame)
    if actual != record["supervised_logical_fingerprint"]:
        raise FrozenSupervisedRehydrationError("supervised logical fingerprint drift")
    if _sha256_file(parquet_path) != record["supervised_parquet_sha256"]:
        raise FrozenSupervisedRehydrationError("supervised parquet byte drift")
    if hashlib.sha256(meta_raw).hexdigest() != record["meta_sha256"]:
        raise FrozenSupervisedRehydrationError("supervised meta byte drift")
    return {
        "verified": True,
        "created": False,
        "final_dir": str(final),
        "verification_sha256": record["verification_sha256"],
        "supervised_logical_fingerprint": actual,
        "model_fit_executed": False,
        "live_order_authorized": False,
    }


def rehydrate(*, root: Path, code_root: Path) -> dict[str, Any]:
    root = root.resolve()
    code_root = code_root.resolve()
    if not root.is_absolute() or not code_root.is_dir():
        raise FrozenSupervisedRehydrationError("absolute PIT root and code root required")
    root.mkdir(parents=True, exist_ok=True)
    module_blobs = validate_frozen_modules(code_root)
    runtime_versions = validate_runtime()
    reference, reference_sha256 = load_reference(code_root)
    raw, long_history_verification_sha256 = _load_long_history(root)

    frozen_module_dir = code_root / FROZEN_MODULE_DIR_NAME
    sys.path.insert(0, str(frozen_module_dir))
    try:
        # Import exact frozen modules into the isolated dependency closure.
        import research_v1_supervised_cache  # noqa: F401
        import research_v1_pit_labels  # noqa: F401
    finally:
        # Keep imported modules loaded, but avoid changing later import resolution.
        if sys.path and sys.path[0] == str(frozen_module_dir):
            sys.path.pop(0)

    final = root / FINAL_DIR_NAME
    if final.exists():
        del raw
        gc.collect()
        return _verify_existing(
            final,
            reference=reference,
            reference_sha256=reference_sha256,
            module_blobs=module_blobs,
            runtime_versions=runtime_versions,
            long_history_verification_sha256=long_history_verification_sha256,
        )

    attempts = root / ATTEMPT_PARENT_NAME
    attempts.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix="attempt-", dir=attempts))
    try:
        frame, diagnostics, record_count = _build_cache_low_memory(
            raw,
            attempt,
            reference=reference,
        )
        del raw
        gc.collect()
        meta_path = attempt / "meta.json"
        parquet_path = attempt / "supervised.parquet"
        meta_raw = meta_path.read_bytes()
        meta = json.loads(meta_raw.decode("utf-8"))
        require_exact_meta(meta, reference)
        if record_count != reference["records"]:
            raise FrozenSupervisedRehydrationError("record count drift")
        if diagnostics != reference["diagnostics"]:
            raise FrozenSupervisedRehydrationError("diagnostics object drift")

        logical = supervised_logical_fingerprint(frame)
        if logical["rows"] != reference["rows"]:
            raise FrozenSupervisedRehydrationError("supervised row count drift")
        if logical["record_rows"] != reference["records"]:
            raise FrozenSupervisedRehydrationError("record row count drift")
        parquet_sha = _sha256_file(parquet_path)
        meta_sha = hashlib.sha256(meta_raw).hexdigest()
        body = _verification_body(
            long_history_verification_sha256=long_history_verification_sha256,
            reference_sha256=reference_sha256,
            module_blobs=module_blobs,
            runtime_versions=runtime_versions,
            supervised_fingerprint=logical,
            supervised_parquet_sha256=parquet_sha,
            meta_sha256=meta_sha,
        )
        record = _write_verification(attempt, body)
        del frame, diagnostics
        gc.collect()
        try:
            os.rename(attempt, final)
        except FileExistsError:
            shutil.rmtree(attempt, ignore_errors=True)
            return _verify_existing(
                final,
                reference=reference,
                reference_sha256=reference_sha256,
                module_blobs=module_blobs,
                runtime_versions=runtime_versions,
                long_history_verification_sha256=long_history_verification_sha256,
            )
        parent_fd = os.open(root, os.O_RDONLY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
        return {
            "verified": True,
            "created": True,
            "final_dir": str(final),
            "verification_sha256": record["verification_sha256"],
            "supervised_logical_fingerprint": logical,
            "model_fit_executed": False,
            "live_order_authorized": False,
        }
    except Exception:
        # Failed attempts remain unpromoted for forensic inspection.
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/pit")
    parser.add_argument("--code-root", default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()
    out = rehydrate(root=Path(args.root), code_root=Path(args.code_root))
    print(
        "INDEXALERT_FROZEN_SUPERVISED_REHYDRATION="
        + json.dumps(out, ensure_ascii=False, sort_keys=True),
        flush=True,
    )


if __name__ == "__main__":
    main()
