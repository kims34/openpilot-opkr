"""Rehydrate the exact long-history panel used by frozen H5 evidence.

This is a one-shot source reconstruction, not a strategy experiment.  It rebuilds
the unchanged FinanceData/marcap-derived KOSPI panel into a separate candidate
directory and promotes it only when the exact source fingerprint recovered from
GitHub Actions run 36643183157 matches byte-semantically at the DataFrame hash
boundary used by research_v1_supervised_cache._source_fingerprint.

It never reads the consumed v1 holdout, never overwrites the existing 2018 PIT
tree, never evaluates model performance, and never authorizes trading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

import numpy as np
import pandas as pd

from research_v1_marcap import build as build_marcap


FROZEN_ACTION_ID = 36643183157
FROZEN_ARTIFACT_ID = 11067383547
FROZEN_ARTIFACT_DIGEST = (
    "sha256:c8dd6a016103cf33d9219622f416fda25715c1cac19b371714d9308f2cb2c26f"
)
FROZEN_RUN_HEAD_SHA = "4df26b6f5d2d9e645cd2c0242c9ac8cefb747a9d"
FROZEN_BUILDER_GIT_BLOB_SHA1 = "5b39887733473a6b4aff5a0fc097c0acc5f5d711"
FROZEN_PYTHON_VERSION = "3.12.14"
FROZEN_PANDAS_VERSION = "2.3.3"
FROZEN_NUMPY_VERSION = "2.5.3"
FROZEN_PYARROW_VERSION = "21.0.0"
FROZEN_START = "2015-06-15"
FROZEN_END = "2026-09-23"
FINAL_DIR_NAME = "marcap_kospi_pit_long_verified_36643183157"
RAW_DIR_NAME = "marcap_raw_long_36643183157"
ATTEMPT_PARENT_NAME = "frozen_long_history_rebuild_attempts"
VERIFICATION_FILE = "frozen_long_history_verification.json"

EXPECTED_SOURCE_FINGERPRINT = {
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


class FrozenLongHistoryError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def git_blob_sha1(raw: bytes) -> str:
    if not isinstance(raw, (bytes, bytearray)):
        raise FrozenLongHistoryError("builder bytes required")
    payload = bytes(raw)
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate_builder(builder_path: Path) -> str:
    if not builder_path.is_file() or builder_path.is_symlink():
        raise FrozenLongHistoryError("frozen marcap builder is missing or unsafe")
    digest = git_blob_sha1(builder_path.read_bytes())
    if digest != FROZEN_BUILDER_GIT_BLOB_SHA1:
        raise FrozenLongHistoryError(
            "marcap builder drifted from frozen Action 36643183157"
        )
    return digest


def validate_runtime_versions() -> dict[str, str]:
    try:
        import pyarrow
    except Exception as exc:
        raise FrozenLongHistoryError("pyarrow is required") from exc
    versions = {
        "python": ".".join(map(str, __import__("sys").version_info[:3])),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "pyarrow": pyarrow.__version__,
    }
    expected = {
        "python": FROZEN_PYTHON_VERSION,
        "pandas": FROZEN_PANDAS_VERSION,
        "numpy": FROZEN_NUMPY_VERSION,
        "pyarrow": FROZEN_PYARROW_VERSION,
    }
    if versions != expected:
        raise FrozenLongHistoryError(
            f"frozen reconstruction runtime mismatch: {versions} != {expected}"
        )
    return versions


def load_panel(cache_dir: Path) -> pd.DataFrame:
    files = sorted(
        p for p in cache_dir.glob("kospi-pit-*.parquet")
        if p.is_file() and not p.is_symlink()
    )
    if not files:
        raise FrozenLongHistoryError(f"no yearly PIT parquet files in {cache_dir}")
    frames = [pd.read_parquet(p) for p in files]
    panel = pd.concat(frames, ignore_index=True)
    if "decision_date" not in panel or "symbol" not in panel:
        raise FrozenLongHistoryError("rebuilt panel lacks decision_date/symbol")
    panel["decision_date"] = pd.to_datetime(panel["decision_date"], errors="raise")
    return panel.sort_values(["decision_date", "symbol"]).reset_index(drop=True)


def source_fingerprint(raw: pd.DataFrame) -> dict[str, Any]:
    """Exact semantics of research_v1_supervised_cache._source_fingerprint."""
    required = ["decision_date", "symbol"]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise FrozenLongHistoryError(
            f"raw PIT source missing required columns: {missing}"
        )
    cols = [
        c for c in (
            "decision_date", "symbol", "open", "high", "low", "close",
            "volume", "value", "ChangesRatio", "krx_change_return",
        )
        if c in raw.columns
    ]
    view = raw[cols].copy()
    view["decision_date"] = pd.to_datetime(view["decision_date"], errors="coerce")
    view["symbol"] = view["symbol"].astype(str)
    hashes = pd.util.hash_pandas_object(
        view, index=False
    ).to_numpy(dtype=np.uint64)
    xor_hash = int(np.bitwise_xor.reduce(hashes)) if len(hashes) else 0
    sum_hash = int(hashes.sum(dtype=np.uint64)) if len(hashes) else 0
    dates = view["decision_date"].dropna()
    return {
        "rows": int(len(view)),
        "symbols": int(view["symbol"].nunique()),
        "date_min": str(dates.min().date()) if len(dates) else None,
        "date_max": str(dates.max().date()) if len(dates) else None,
        "columns": cols,
        "hash_xor_u64": str(xor_hash),
        "hash_sum_u64": str(sum_hash),
    }


def require_exact_fingerprint(actual: dict[str, Any]) -> None:
    if actual != EXPECTED_SOURCE_FINGERPRINT:
        differences = {
            key: {
                "expected": EXPECTED_SOURCE_FINGERPRINT.get(key),
                "actual": actual.get(key),
            }
            for key in sorted(set(EXPECTED_SOURCE_FINGERPRINT) | set(actual))
            if actual.get(key) != EXPECTED_SOURCE_FINGERPRINT.get(key)
        }
        raise FrozenLongHistoryError(
            "frozen long-history fingerprint mismatch: "
            + json.dumps(differences, sort_keys=True)
        )


def _verification_body(
    *,
    fingerprint: dict[str, Any],
    builder_blob_sha1: str,
    versions: dict[str, str],
) -> dict[str, Any]:
    return {
        "classification": "FROZEN_LONG_HISTORY_SOURCE_REHYDRATION_VERIFIED",
        "frozen_action_id": FROZEN_ACTION_ID,
        "frozen_artifact_id": FROZEN_ARTIFACT_ID,
        "frozen_artifact_digest": FROZEN_ARTIFACT_DIGEST,
        "frozen_run_head_sha": FROZEN_RUN_HEAD_SHA,
        "frozen_builder_git_blob_sha1": builder_blob_sha1,
        "frozen_start": FROZEN_START,
        "frozen_end": FROZEN_END,
        "runtime_versions": versions,
        "source_fingerprint": fingerprint,
        "fingerprint_exact_match": True,
        "existing_2018_pit_tree_overwritten": False,
        "consumed_v1_holdout_read": False,
        "performance_evaluation_executed": False,
        "model_fit_executed": False,
        "historical_backfill_decisions_created": False,
        "fresh_alpha_observation_admitted": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }


def validate_verification(value: dict[str, Any]) -> dict[str, Any]:
    required_false = (
        "existing_2018_pit_tree_overwritten",
        "consumed_v1_holdout_read",
        "performance_evaluation_executed",
        "model_fit_executed",
        "historical_backfill_decisions_created",
        "fresh_alpha_observation_admitted",
        "promotion_authority",
        "live_order_authorized",
    )
    if value.get("classification") != "FROZEN_LONG_HISTORY_SOURCE_REHYDRATION_VERIFIED":
        raise FrozenLongHistoryError("verification classification mismatch")
    if value.get("frozen_action_id") != FROZEN_ACTION_ID:
        raise FrozenLongHistoryError("frozen action mismatch")
    if value.get("frozen_artifact_id") != FROZEN_ARTIFACT_ID:
        raise FrozenLongHistoryError("frozen artifact mismatch")
    if value.get("frozen_artifact_digest") != FROZEN_ARTIFACT_DIGEST:
        raise FrozenLongHistoryError("frozen artifact digest mismatch")
    if value.get("frozen_run_head_sha") != FROZEN_RUN_HEAD_SHA:
        raise FrozenLongHistoryError("frozen run head mismatch")
    if value.get("frozen_builder_git_blob_sha1") != FROZEN_BUILDER_GIT_BLOB_SHA1:
        raise FrozenLongHistoryError("frozen builder identity mismatch")
    if value.get("source_fingerprint") != EXPECTED_SOURCE_FINGERPRINT:
        raise FrozenLongHistoryError("verification fingerprint mismatch")
    if value.get("fingerprint_exact_match") is not True:
        raise FrozenLongHistoryError("fingerprint_exact_match must be true")
    for field in required_false:
        if value.get(field) is not False:
            raise FrozenLongHistoryError(f"{field} must remain exact false")
    body = dict(value)
    digest = body.pop("verification_sha256", None)
    if not isinstance(digest, str) or len(digest) != 64:
        raise FrozenLongHistoryError("verification_sha256 missing")
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if digest != actual:
        raise FrozenLongHistoryError("verification fingerprint mismatch")
    return {"valid": True, "verification_sha256": actual}


def write_verification(
    directory: Path,
    *,
    fingerprint: dict[str, Any],
    builder_blob_sha1: str,
    versions: dict[str, str],
) -> dict[str, Any]:
    body = _verification_body(
        fingerprint=fingerprint,
        builder_blob_sha1=builder_blob_sha1,
        versions=versions,
    )
    record = {
        **body,
        "verification_sha256": hashlib.sha256(_canonical(body)).hexdigest(),
    }
    validate_verification(record)
    target = directory / VERIFICATION_FILE
    payload = _canonical(record) + b"\n"
    fd, name = tempfile.mkstemp(prefix=".verify-", dir=directory)
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


def verify_existing(directory: Path) -> dict[str, Any]:
    record_path = directory / VERIFICATION_FILE
    if not directory.is_dir() or directory.is_symlink() or not record_path.is_file():
        raise FrozenLongHistoryError("existing verified directory is incomplete")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    validate_verification(record)
    actual = source_fingerprint(load_panel(directory))
    require_exact_fingerprint(actual)
    if actual != record["source_fingerprint"]:
        raise FrozenLongHistoryError("verified directory data drifted from record")
    return {
        "verified": True,
        "created": False,
        "final_dir": str(directory),
        "verification_sha256": record["verification_sha256"],
        "source_fingerprint": actual,
        "model_fit_executed": False,
        "live_order_authorized": False,
    }


def rehydrate(
    *,
    root: Path,
    builder_path: Path,
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_absolute():
        raise FrozenLongHistoryError("PIT root must be absolute")
    root.mkdir(parents=True, exist_ok=True)
    builder_blob = validate_builder(builder_path)
    versions = validate_runtime_versions()

    final = root / FINAL_DIR_NAME
    if final.exists():
        return verify_existing(final)

    attempts = root / ATTEMPT_PARENT_NAME
    attempts.mkdir(parents=True, exist_ok=True)
    raw_dir = root / RAW_DIR_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix="attempt-", dir=attempts))
    try:
        build_marcap(FROZEN_START, FROZEN_END, str(attempt), str(raw_dir))
        actual = source_fingerprint(load_panel(attempt))
        require_exact_fingerprint(actual)
        record = write_verification(
            attempt,
            fingerprint=actual,
            builder_blob_sha1=builder_blob,
            versions=versions,
        )
        # Same-volume directory rename publishes the verified panel in one step.
        try:
            os.rename(attempt, final)
        except FileExistsError:
            # A concurrent identical build may have won. Verify it rather than
            # overwrite anything.
            shutil.rmtree(attempt, ignore_errors=True)
            return verify_existing(final)
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
            "source_fingerprint": actual,
            "model_fit_executed": False,
            "live_order_authorized": False,
        }
    except Exception:
        # Preserve a mismatching/failed candidate for forensic inspection.
        # It remains under ATTEMPT_PARENT_NAME and is never treated as verified.
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/pit")
    parser.add_argument(
        "--builder",
        default=str(Path(__file__).with_name("research_v1_marcap.py")),
    )
    args = parser.parse_args()
    out = rehydrate(
        root=Path(args.root),
        builder_path=Path(args.builder),
    )
    print(
        "INDEXALERT_FROZEN_LONG_HISTORY_REHYDRATION="
        + json.dumps(out, ensure_ascii=False, sort_keys=True),
        flush=True,
    )


if __name__ == "__main__":
    main()
