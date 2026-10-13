"""Byte-level integrity only for read-only post-selection fan-out artifacts.

Does NOT authenticate a source receipt, grant PIT admission, authorize evaluation,
replay model fitting, read the sealed holdout, or place orders. A separately
authenticated frozen upstream cache identity is mandatory for actual use.
"""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

SCHEMA = "indexalert-readonly-handoff-v1"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class UnsafeHandoff(ValueError):
    """Missing or changed input: reject reuse rather than silently restore."""


def _canonical(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _identity(info: os.stat_result) -> tuple[int, ...]:
    """Detect replacement/mutation by device, inode, size, mtime and ctime."""
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _digest_files(root: Path, filenames: list[str]) -> dict[str, str]:
    """Hash regular files opened relative to no-follow directory descriptors.

    No check-then-open Path.is_symlink/open race: the kernel rejects symlink
    resolution at each opened path component. This still is NOT an immutable
    multi-file snapshot or an authenticated source/PIT admission certificate.
    """
    if type(filenames) is not list or not filenames or any(
        type(name) is not str or not name for name in filenames
    ):
        raise UnsafeHandoff("nonempty list of explicit file names required")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise UnsafeHandoff("no-follow directory descriptors unavailable: fail closed")
    root = Path(root)
    seen: set[str] = set()
    digests: dict[str, str] = {}
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0)

    try:
        with ExitStack() as root_stack:
            root_fd = os.open(root, directory_flags)
            root_stack.callback(os.close, root_fd)
            if not stat.S_ISDIR(os.fstat(root_fd).st_mode):
                raise UnsafeHandoff("artifact root is not a directory")
            for name in sorted(filenames):
                if "\\" in name or "\x00" in name:
                    raise UnsafeHandoff("invalid artifact path separator or NUL")
                parts = PurePosixPath(name)
                if (parts.is_absolute()
                        or any(p in (".", "..", "") for p in name.split("/"))
                        or name in seen):
                    raise UnsafeHandoff("duplicate, absolute or traversing artifact name")
                seen.add(name)

                # A dirfd-based walk prevents symlink traversal even if a path
                # is swapped between a pre-check and open; no path pre-check.
                with ExitStack() as component_stack:
                    parent_fd = root_fd
                    for component in parts.parts[:-1]:
                        next_fd = os.open(component, directory_flags, dir_fd=parent_fd)
                        component_stack.callback(os.close, next_fd)
                        parent_fd = next_fd
                    fd = os.open(parts.parts[-1], file_flags, dir_fd=parent_fd)
                    with os.fdopen(fd, "rb") as source:
                        before = os.fstat(source.fileno())
                        if not stat.S_ISREG(before.st_mode):
                            raise UnsafeHandoff("non-regular artifact forbidden: " + name)
                        h = hashlib.sha256()
                        for chunk in iter(lambda: source.read(1024 * 1024), b""):
                            h.update(chunk)
                        after = os.fstat(source.fileno())
                        current = os.stat(parts.parts[-1], dir_fd=parent_fd,
                                          follow_symlinks=False)
                        if _identity(before) != _identity(after) or _identity(before) != _identity(current):
                            raise UnsafeHandoff("artifact replaced or mutated while hashing: " + name)
                        digests[name] = h.hexdigest()
    except OSError as exc:
        raise UnsafeHandoff("missing, unsafe or changed artifact directory/file") from exc
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
