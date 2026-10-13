"""Byte-level integrity only for read-only post-selection fan-out artifacts.

Does NOT authenticate a source receipt, grant PIT admission, authorize evaluation,
replay model fitting, read the sealed holdout, or place orders. A separately
authenticated frozen upstream cache identity is mandatory for actual use.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re

SCHEMA = "indexalert-readonly-handoff-v1"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class UnsafeHandoff(ValueError):
    """Missing or changed input: reject reuse rather than silently restore."""


def _canonical(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _digest_files(root: Path, filenames: list[str]) -> dict[str, str]:
    if type(filenames) is not list or not filenames:
        raise UnsafeHandoff("nonempty explicit file list required")
    if type(root) is not Path:
        root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise UnsafeHandoff("missing or symlinked artifact directory")

    base = root.resolve(strict=True)
    seen: set[str] = set()
    digests: dict[str, str] = {}
    for name in sorted(filenames):
        if type(name) is not str or not name or "\\" in name:
            raise UnsafeHandoff("invalid artifact name")
        parts = PurePosixPath(name)
        if (parts.is_absolute() or any(x in (".", "..", "") for x in name.split("/"))
                or name.startswith("/") or name in seen):
            raise UnsafeHandoff("duplicate, absolute or traversing artifact name")
        seen.add(name)
        current = root
        for part in parts.parts:
            current = current / part
            if current.is_symlink():
                raise UnsafeHandoff("symbolic-link artifact path not allowed: " + name)
        if not current.is_file() or not current.resolve(strict=True).is_relative_to(base):
            raise UnsafeHandoff("missing or outside-root artifact: " + name)
        before = current.stat()
        h = hashlib.sha256()
        with current.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        after = current.stat()
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise UnsafeHandoff("artifact mutated during read: " + name)
        digests[name] = h.hexdigest()
    return digests


def make_handoff(*, root: Path, filenames: list[str],
                 upstream_cache_key_sha256: str) -> dict:
    """Bind exact artifact bytes to a caller-authenticated upstream cache key.

    This is content integrity, NOT an admission certificate or digital signature.
    The caller must independently verify upstream receipt, policy and origin.
    """
    if type(upstream_cache_key_sha256) is not str or not _HEX64.fullmatch(upstream_cache_key_sha256):
        raise UnsafeHandoff("authenticated upstream cache key SHA256 required")
    fields = {
        "schema": SCHEMA,
        "upstream_cache_key_sha256": upstream_cache_key_sha256,
        "artifact_sha256": _digest_files(root, filenames),
    }
    return {
        **fields,
        "handoff_sha256": _sha256(_canonical(fields)),
        "pit_admission_granted": False,
        "profitability_evaluation_authorized": False,
        "holdout_access_authorized": False,
        "live_orders_authorized": False,
    }


def handoff_matches(stored: object, *, root: Path, filenames: list[str],
                    upstream_cache_key_sha256: str) -> bool:
    """No name/date cache fallback; reject even one changed file or input key."""
    try:
        expected = make_handoff(
            root=root, filenames=filenames,
            upstream_cache_key_sha256=upstream_cache_key_sha256,
        )
    except (UnsafeHandoff, TypeError, ValueError, OSError):
        return False
    return type(stored) is dict and stored == expected
