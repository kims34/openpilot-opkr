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

import json
import os
from pathlib import Path
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


def _read_exact_private_metadata(root: Path, rel: tuple[str, str]) -> bytes:
    parent = root / rel[0]
    _need(not parent.is_symlink() and parent.is_dir(),
          "PRIVATE_METADATA_PARENT_INVALID")
    item = parent / rel[1]
    _need(not item.is_symlink(), "PRIVATE_METADATA_SYMLINK_REJECTED")
    # An O_NOFOLLOW fd is used to avoid following final-component symlinks
    # even if the file changed after the preceding stat check.
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(item, flags)
    except OSError:
        raise KRXPrivateOwnerReadOnlyError(
            "PRIVATE_METADATA_READ_DENIED_OR_MISSING"
        ) from None
    try:
        st = os.fstat(fd)
        _need(stat.S_ISREG(st.st_mode), "PRIVATE_METADATA_NOT_REGULAR_FILE")
        _need(stat.S_IMODE(st.st_mode) == 0o600,
              "PRIVATE_METADATA_PERMISSION_DRIFT")
        _need(st.st_size >= 2, "PRIVATE_METADATA_EMPTY")
        # Bound memory use without exposing a source path or file size.
        _need(st.st_size <= 32 * 1024 * 1024,
              "PRIVATE_METADATA_EXCEEDS_SAFETY_LIMIT")
        with os.fdopen(fd, "rb", closefd=False) as f:
            payload = f.read(st.st_size + 1)
        _need(len(payload) == st.st_size,
              "PRIVATE_METADATA_CHANGED_DURING_READ")
        return payload
    finally:
        os.close(fd)


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
