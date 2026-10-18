"""Safe offline KRX source-owner snapshot inspection, with no storage writes.

This reads ONLY the two exact pre-existing PER_SECURITY_HISTORY manifest
and phase-state files. It does not start a network provider request, resume
any original task, change file permissions, write result files, print paths
or emit private issuer/task IDs or raw market rows.

Deploy/run only after the KRX protected-volume owner has *independently*
authorized nonmutating local inspection in their existing protected session.
This script is NOT shipped to, or executed on, the live Railway worker here.
"""
from __future__ import annotations

from contextlib import ExitStack
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

from research_v1_krx_flow_frozen_archive_bytes_gate import (
    audit_frozen_2026_10_03_private_krx_flow_snapshot,
)

MANIFEST_REL = ("task_manifests", "per-security-history-v3.json")
STATE_REL = ("batch_state", "PER_SECURITY_HISTORY.json")
DENIED_PARTS = frozenset({"public", "static", "www", "htdocs"})


class KRXPrivateOwnerReadOnlyError(ValueError):
    """Static errors only; never include private filesystem paths."""


def _need(ok: bool, code: str) -> None:
    if not ok:
        raise KRXPrivateOwnerReadOnlyError(code)


def _protected_root(root: str, worktree: str) -> Path:
    _need(type(root) is str and bool(root) and os.path.isabs(root),
          "PRIVATE_ROOT_NOT_ABSOLUTE")
    _need(type(worktree) is str and bool(worktree)
          and os.path.isabs(worktree), "GIT_WORKTREE_NOT_ABSOLUTE")
    original = Path(root)
    git = Path(worktree).resolve(strict=True)
    _need(not any(part.lower() in DENIED_PARTS for part in original.parts),
          "PRIVATE_ROOT_IN_PUBLIC_TREE")
    # Reject symlinks along the full path, not just at its leaf. A project
    # worktree / public directory never qualifies as a private data root.
    current = Path(original.anchor)
    for part in original.parts[1:]:
        current = current / part
        _need(not current.is_symlink(), "PRIVATE_ROOT_SYMLINK_REJECTED")
    _need(original.is_dir(), "PRIVATE_ROOT_NOT_EXISTING_DIRECTORY")
    resolved = original.resolve(strict=True)
    _need(resolved != git and git not in resolved.parents,
          "PRIVATE_ROOT_INSIDE_GIT_WORKTREE")
    return resolved


def _read_exact_private_metadata(root: Path, rel: tuple[str, ...]) -> bytes:
    """Anchor every existing directory and file to O_NOFOLLOW descriptors.

    The former Path.is_symlink checks were vulnerable to the parent being
    exchanged for a symlink between check and opening a full absolute file
    path. Use openat-style dir_fd lookups for every ancestor, the metadata
    directory, and finally the file; never navigate via mutable full paths
    once traversal begins. Linux private worker is required to support both
    O_DIRECTORY and O_NOFOLLOW. All descriptors are closed in ExitStack.
    """
    _need(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"),
          "PRIVATE_SECURE_OPEN_FLAGS_UNAVAILABLE")
    _need(type(rel) is tuple and 2 <= len(rel) <= 7
          and all(type(p) is str and p not in {".", ".."}
                  and re.fullmatch(r"[A-Za-z0-9._-]+", p) is not None
                  for p in rel), "PRIVATE_RELATIVE_PATH_UNSAFE")
    parent = root.joinpath(*rel[:-1])
    _need(not parent.is_symlink() and parent.is_dir(),
          "PRIVATE_METADATA_PARENT_INVALID")
    item = parent / rel[-1]
    _need(not item.is_symlink(), "PRIVATE_METADATA_SYMLINK_REJECTED")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    # O_NONBLOCK makes an attacker-swapped FIFO fail fast at fstat rather than\n    # hanging forever in open(). On regular metadata/blob files it has no effect.\n    file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        with ExitStack() as stack:
            directory_fd = os.open(root.anchor, directory_flags)
            stack.callback(os.close, directory_fd)
            # A relative, fd-anchored lookup of each path component rejects
            # directory-symlink replacements even when a race occurs.
            for part in root.parts[1:]:
                child_fd = os.open(part, directory_flags, dir_fd=directory_fd)
                stack.callback(os.close, child_fd)
                directory_fd = child_fd
            for part in rel[:-1]:
                parent_fd = os.open(part, directory_flags, dir_fd=directory_fd)
                stack.callback(os.close, parent_fd)
                directory_fd = parent_fd
            fd = os.open(rel[-1], file_flags, dir_fd=directory_fd)
            stack.callback(os.close, fd)
            st = os.fstat(fd)
            _need(stat.S_ISREG(st.st_mode), "PRIVATE_METADATA_NOT_REGULAR_FILE")
            _need(stat.S_IMODE(st.st_mode) == 0o600,
                  "PRIVATE_METADATA_PERMISSION_DRIFT")
            _need(st.st_size >= 2, "PRIVATE_METADATA_EMPTY")
            _need(st.st_size <= 32 * 1024 * 1024,
                  "PRIVATE_METADATA_EXCEEDS_SAFETY_LIMIT")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                payload = stream.read(st.st_size + 1)
            _need(len(payload) == st.st_size,
                  "PRIVATE_METADATA_CHANGED_DURING_READ")
            after = os.fstat(fd)
            _need(after.st_dev == st.st_dev
                  and after.st_ino == st.st_ino
                  and after.st_size == st.st_size
                  and after.st_mtime_ns == st.st_mtime_ns,
                  "PRIVATE_METADATA_CHANGED_DURING_READ")
            return payload
    except OSError:
        raise KRXPrivateOwnerReadOnlyError(
            "PRIVATE_METADATA_READ_DENIED_OR_MISSING"
        ) from None


def read_protected_krx_original_manifest_and_phase_state(
    *,
    private_root: str,
    git_worktree: str,
) -> tuple[bytes, bytes]:
    """Owner-only read-only access; never modifies mounted source or metadata."""
    base = _protected_root(private_root, git_worktree)
    return (
        _read_exact_private_metadata(base, MANIFEST_REL),
        _read_exact_private_metadata(base, STATE_REL),
    )


def audit_owner_frozen_2026_10_03_private_snapshot(
    *,
    private_root: str,
    git_worktree: str,
) -> dict[str, Any]:
    manifest_raw, state_raw = read_protected_krx_original_manifest_and_phase_state(
        private_root=private_root, git_worktree=git_worktree
    )
    # Mandatory immutable SHA/14,296/11,750 original-prefix validation;
    # this wrapper deliberately has NO supplied override for the pinned
    # expected provenance values or source/performance/trading authority.
    result = audit_frozen_2026_10_03_private_krx_flow_snapshot(
        private_manifest_bytes=manifest_raw,
        private_phase_state_bytes=state_raw,
    )
    # Result contains only counts and static yes/no safety/provenance gates.
    return {"snapshot_audit_status": "PASSED_INTERNAL_ARCHIVE_CHECKS", **result}


def main() -> int:
    try:
        root = os.environ.get("KRX_PRIVATE_RAW_DIR", "")
        result = audit_owner_frozen_2026_10_03_private_snapshot(
            private_root=root,
            git_worktree=str(Path.cwd().resolve()),
        )
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:
        # Never include OSError, private path, issuer IDs, credential or
        # raw response data in any console/log or GitHub issue.
        reason = (
            str(exc) if isinstance(exc, KRXPrivateOwnerReadOnlyError)
            else "ORIGINAL_PRIVATE_SNAPSHOT_UNVERIFIED"
        )
        print(json.dumps({
            "snapshot_audit_status": "BLOCKED",
            "reason_code": reason,
            "source_admitted": False,
            "performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "ordering_enabled": False,
            "network_request_attempted": False,
            "source_numeric_rows_or_identifiers_emitted": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
