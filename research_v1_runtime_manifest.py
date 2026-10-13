"""Content-addressed, fail-closed cache eligibility for future ADMITTED PIT inputs.

This module cannot grant admission: a separately audited, pinned source receipt
is required. No network access, strategy evaluation, holdout access or orders.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

SCHEMA = "indexalert-verified-runtime-cache-v1"
REQUIRED_GATES = (
    "original_source_verified",
    "pit_availability_verified",
    "full_universe_coverage_verified",
    "security_identity_verified",
    "official_tradability_verified",
    "corporate_action_economics_verified",
)
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class UnverifiedSourceError(ValueError):
    """Missing, stale or unaudited source; never reuse this cache."""


def _canonical(data: object) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _check_receipt(receipt: Mapping) -> None:
    if type(receipt) is not dict or receipt.get("admission_status") != "PIT_ADMITTED":
        raise UnverifiedSourceError("independent PIT admission receipt required")
    failed = [key for key in REQUIRED_GATES if receipt.get(key) is not True]
    if failed:
        raise UnverifiedSourceError("source admission gates not met: " + ", ".join(failed))
    for key in ("source_evidence_sha256", "coverage_evidence_sha256", "admission_code_sha256"):
        value = receipt.get(key)
        if type(value) is not str or not _HEX64.fullmatch(value):
            raise UnverifiedSourceError("missing pinned evidence SHA256: " + key)
    if receipt.get("holdout_access_authorized") is True or receipt.get("live_orders_authorized") is True:
        raise UnverifiedSourceError("cache preparation cannot authorize holdout or live orders")


def _hash_files(files: Mapping[str, Path]) -> dict[str, str]:
    if not files:
        raise UnverifiedSourceError("empty input set")
    result = {}
    for label, path in sorted(files.items()):
        if type(label) is not str or not label or label in result:
            raise UnverifiedSourceError("invalid input label")
        p = Path(path)
        if not p.is_file() or p.is_symlink():
            raise UnverifiedSourceError("missing or symbolic-link input: " + label)
        h = hashlib.sha256()
        with p.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                h.update(chunk)
        result[label] = h.hexdigest()
    return result


def cache_manifest(*, source_files: Mapping[str, Path], code_files: Mapping[str, Path],
                   receipt: dict, frozen_policy: dict, runtime_lock: dict) -> dict:
    """Generate a cache identity only after separate, explicit PIT admission.

    The caller must independently authenticate the receipt; this function only
    checks the supplied evidence's structure and binds its exact bytes.
    """
    _check_receipt(receipt)
    if type(frozen_policy) is not dict or not frozen_policy:
        raise UnverifiedSourceError("nonempty frozen policy required")
    if type(runtime_lock) is not dict or not runtime_lock:
        raise UnverifiedSourceError("pinned runtime lock required")
    parts = {
        "schema": SCHEMA,
        "source_file_sha256": _hash_files(source_files),
        "code_file_sha256": _hash_files(code_files),
        "receipt_sha256": _sha(_canonical(receipt)),
        "frozen_policy_sha256": _sha(_canonical(frozen_policy)),
        "runtime_lock_sha256": _sha(_canonical(runtime_lock)),
    }
    return {**parts, "cache_key_sha256": _sha(_canonical(parts)),
            "evaluation_authorized": False, "holdout_authorized": False,
            "live_orders_authorized": False}


def cache_matches(stored: dict, **kwargs) -> bool:
    """No restore-key fallback: a single changed byte invalidates reuse."""
    try:
        expected = cache_manifest(**kwargs)
    except (UnverifiedSourceError, TypeError, ValueError, OSError):
        return False
    return type(stored) is dict and stored == expected
