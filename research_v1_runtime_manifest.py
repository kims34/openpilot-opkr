"""Content-addressed, fail-closed cache eligibility for future ADMITTED PIT inputs.

This module cannot grant admission: a separately audited, pinned source receipt
is required. No network access, strategy evaluation, holdout access or orders.
"""
from __future__ import annotations

import hashlib
import os
import stat
from contextlib import ExitStack
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
    # Fail closed on absent, ambiguous or non-boolean authorization flags.
    # Testing only the literal True would mistakenly admit "true", 1, None,
    # or a missing flag as safe cache metadata. This grants no privileges.
    if (receipt.get("holdout_access_authorized") is not False
            or receipt.get("live_orders_authorized") is not False):
        raise UnverifiedSourceError("cache receipt must explicitly deny holdout and live orders")


def _identity(info: os.stat_result) -> tuple[int, ...]:
    """Filesystem identity used to fail closed on mutation or replacement."""
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _read_fingerprint_no_follow(path: Path, *, hash_bytes: bool
                                ) -> tuple[str | None, tuple[int, ...]]:
    """Open every path component without following links; reject concurrent drift.

    This is local file integrity, NOT publisher authentication or a multi-file
    atomic snapshot. Caller must independently authenticate PIT admission.
    """
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise UnverifiedSourceError("no-follow filesystem opening unsupported")
    try:
        p = Path(path)
        components = p.parts[1:] if p.is_absolute() else p.parts
        if not components or any(component in ("", ".", "..") for component in components):
            raise UnverifiedSourceError("invalid or traversing cache input path")
        dirs = (os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                | getattr(os, "O_CLOEXEC", 0))
        leaf_flags = (os.O_RDONLY | os.O_NOFOLLOW
                      | getattr(os, "O_NONBLOCK", 0)
                      | getattr(os, "O_CLOEXEC", 0))
        with ExitStack() as stack:
            parent = os.open("/" if p.is_absolute() else ".", dirs)
            stack.callback(os.close, parent)
            for component in components[:-1]:
                child = os.open(component, dirs, dir_fd=parent)
                stack.callback(os.close, child)
                parent = child
            fd = os.open(components[-1], leaf_flags, dir_fd=parent)
            stack.callback(os.close, fd)
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise UnverifiedSourceError("nonregular cache input forbidden")
            digest = None
            if hash_bytes:
                h = hashlib.sha256()
                with os.fdopen(os.dup(fd), "rb") as source:
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        h.update(chunk)
                digest = h.hexdigest()
            after = os.fstat(fd)
            current = os.stat(components[-1], dir_fd=parent,
                              follow_symlinks=False)
            if _identity(before) != _identity(after) or _identity(before) != _identity(current):
                raise UnverifiedSourceError("cache input changed while fingerprinting")
            return digest, _identity(before)
    except (OSError, TypeError) as exc:
        raise UnverifiedSourceError("missing, unsafe or changed cache input") from exc


def _hash_files(files: Mapping[str, Path]
                ) -> tuple[dict[str, str], list[tuple[Path, tuple[int, ...]]]]:
    if not isinstance(files, Mapping) or not files:
        raise UnverifiedSourceError("nonempty explicit cache input map required")
    if any(type(label) is not str or not label for label in files):
        raise UnverifiedSourceError("invalid input label")
    result: dict[str, str] = {}
    identities: list[tuple[Path, tuple[int, ...]]] = []
    for label, path in sorted(files.items()):
        digest, identity = _read_fingerprint_no_follow(Path(path), hash_bytes=True)
        if digest is None:
            raise UnverifiedSourceError("missing cache input digest")
        result[label] = digest
        identities.append((Path(path), identity))
    return result, identities


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
    source_digests, source_identities = _hash_files(source_files)
    code_digests, code_identities = _hash_files(code_files)
    # Recheck earlier inputs after hashing later ones; an unchanged digest
    # alone cannot detect same-byte inode substitution during the scan.
    for path, original_identity in (*source_identities, *code_identities):
        _, current_identity = _read_fingerprint_no_follow(path, hash_bytes=False)
        if original_identity != current_identity:
            raise UnverifiedSourceError("cache input replaced during batch hashing")
    parts = {
        "schema": SCHEMA,
        "source_file_sha256": source_digests,
        "code_file_sha256": code_digests,
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
