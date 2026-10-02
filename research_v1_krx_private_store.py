"""Private content-addressed storage for KRX historical raw responses.

Offline/storage infrastructure only. This module never performs network access.
It enforces the historical execution contract: raw KRX bytes stay outside the
Git worktree/public directories, are written atomically, chmod 0600, and are
addressed by SHA-256. Public callers may expose only metadata.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping


class KRXPrivateStoreError(ValueError):
    pass


PUBLIC_DIR_NAMES = {"public", "static", "www", "htdocs"}
SECRET_KEY_FRAGMENTS = (
    "password", "passwd", "pwd", "secret", "token", "auth_key",
    "api_key", "apikey", "authorization", "cookie", "session",
)


def sha256_bytes(data: bytes) -> str:
    if not isinstance(data, (bytes, bytearray)):
        raise KRXPrivateStoreError("raw object must be bytes")
    return hashlib.sha256(bytes(data)).hexdigest()


def _resolved(path: str | os.PathLike[str]) -> Path:
    p = Path(path)
    if not p.is_absolute():
        raise KRXPrivateStoreError("private raw root must be absolute")
    return p.resolve()


def validate_private_root_path(
    root: str | os.PathLike[str],
    *,
    git_worktree: str | os.PathLike[str] | None = None,
) -> Path:
    """Validate a candidate private root without creating or modifying it."""
    p = _resolved(root)

    parts = {part.lower() for part in p.parts}
    if parts & PUBLIC_DIR_NAMES:
        raise KRXPrivateStoreError("private raw root must not be under public/static directories")

    if git_worktree is not None:
        git = Path(git_worktree).resolve()
        try:
            p.relative_to(git)
        except ValueError:
            pass
        else:
            raise KRXPrivateStoreError("private raw root must be outside the git worktree")
    return p


def validate_private_root(
    root: str | os.PathLike[str],
    *,
    git_worktree: str | os.PathLike[str] | None = None,
) -> Path:
    p = validate_private_root_path(root, git_worktree=git_worktree)
    p.mkdir(parents=True, exist_ok=True)
    os.chmod(p, 0o700)
    return p


def _object_path(root: Path, digest: str) -> Path:
    return root / "objects" / "sha256" / digest[:2] / f"{digest}.bin"


def write_raw_object(
    root: str | os.PathLike[str],
    raw_bytes: bytes,
    *,
    git_worktree: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    base = validate_private_root(root, git_worktree=git_worktree)
    payload = bytes(raw_bytes)
    digest = sha256_bytes(payload)
    target = _object_path(base, digest)
    target.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(target.parent, 0o700)

    if target.exists():
        existing = target.read_bytes()
        if sha256_bytes(existing) != digest or existing != payload:
            raise KRXPrivateStoreError("existing content-addressed object does not match digest")
        os.chmod(target, 0o600)
        return {
            "raw_object_sha256": digest,
            "raw_bytes_size": len(payload),
            "object_relpath": str(target.relative_to(base)),
            "created": False,
        }

    fd, tmp_name = tempfile.mkstemp(prefix=".tmp-", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, target)
        # fsync directory so the rename is durable.
        dir_fd = os.open(str(target.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

    os.chmod(target, 0o600)
    return {
        "raw_object_sha256": digest,
        "raw_bytes_size": len(payload),
        "object_relpath": str(target.relative_to(base)),
        "created": True,
    }


def verify_raw_object(
    root: str | os.PathLike[str],
    digest: str,
    *,
    expected_size: int | None = None,
    git_worktree: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    base = validate_private_root(root, git_worktree=git_worktree)
    d = str(digest).strip().lower()
    if len(d) != 64 or any(ch not in "0123456789abcdef" for ch in d):
        raise KRXPrivateStoreError("invalid raw object SHA-256")
    target = _object_path(base, d)
    if not target.is_file():
        raise KRXPrivateStoreError("raw object missing")
    payload = target.read_bytes()
    actual = sha256_bytes(payload)
    if actual != d:
        raise KRXPrivateStoreError("raw object checksum mismatch")
    if expected_size is not None and len(payload) != int(expected_size):
        raise KRXPrivateStoreError("raw object size mismatch")
    mode = target.stat().st_mode & 0o777
    if mode != 0o600:
        raise KRXPrivateStoreError("raw object file mode drift")
    return {
        "raw_object_sha256": actual,
        "raw_bytes_size": len(payload),
        "object_relpath": str(target.relative_to(base)),
        "verified": True,
    }


def _secret_like_key(key: Any) -> bool:
    normal = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(key))
    return any(fragment in normal for fragment in SECRET_KEY_FRAGMENTS)


def validate_secret_free_metadata(value: Any, path: str = "metadata") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if _secret_like_key(key):
                raise KRXPrivateStoreError(f"secret-like metadata key forbidden: {path}.{key}")
            validate_secret_free_metadata(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for idx, child in enumerate(value):
            validate_secret_free_metadata(child, f"{path}[{idx}]")


def write_private_json(
    root: str | os.PathLike[str],
    relpath: str,
    value: Mapping[str, Any],
    *,
    git_worktree: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    base = validate_private_root(root, git_worktree=git_worktree)
    validate_secret_free_metadata(value)
    rel = Path(relpath)
    if rel.is_absolute() or ".." in rel.parts:
        raise KRXPrivateStoreError("private metadata relpath is unsafe")
    target = base / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(target.parent, 0o700)
    payload = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str)
        + "\n"
    ).encode("utf-8")

    fd, tmp_name = tempfile.mkstemp(prefix=".tmp-", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, target)
        dir_fd = os.open(str(target.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
    os.chmod(target, 0o600)
    return {
        "metadata_sha256": sha256_bytes(payload),
        "metadata_bytes_size": len(payload),
        "metadata_relpath": str(rel),
    }
