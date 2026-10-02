import os
from pathlib import Path

import pytest

from research_v1_krx_private_store import (
    KRXPrivateStoreError,
    validate_private_root,
    verify_raw_object,
    write_private_json,
    write_raw_object,
)


def test_private_store_writes_content_addressed_object_atomically(tmp_path):
    root = tmp_path / "private"
    raw = b"KRX_PRIVATE_TEST_PAYLOAD"
    out = write_raw_object(root.resolve(), raw)
    assert out["created"] is True
    assert len(out["raw_object_sha256"]) == 64
    assert out["raw_bytes_size"] == len(raw)

    target = root / out["object_relpath"]
    assert target.read_bytes() == raw
    assert target.stat().st_mode & 0o777 == 0o600
    assert root.stat().st_mode & 0o777 == 0o700

    again = write_raw_object(root.resolve(), raw)
    assert again["created"] is False
    assert again["raw_object_sha256"] == out["raw_object_sha256"]

    checked = verify_raw_object(
        root.resolve(),
        out["raw_object_sha256"],
        expected_size=len(raw),
    )
    assert checked["verified"] is True


def test_private_store_rejects_git_worktree_and_public_dirs(tmp_path):
    git = (tmp_path / "repo").resolve()
    git.mkdir()

    with pytest.raises(KRXPrivateStoreError, match="outside the git worktree"):
        validate_private_root((git / "raw").resolve(), git_worktree=git)

    with pytest.raises(KRXPrivateStoreError, match="public/static"):
        validate_private_root((tmp_path / "public" / "raw").resolve())


def test_private_store_requires_absolute_root(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        with pytest.raises(KRXPrivateStoreError, match="must be absolute"):
            validate_private_root("relative/raw")
    finally:
        os.chdir(cwd)


def test_verify_detects_tampering_and_size_drift(tmp_path):
    root = (tmp_path / "private").resolve()
    out = write_raw_object(root, b"abc")
    target = root / out["object_relpath"]
    target.write_bytes(b"tampered")
    os.chmod(target, 0o600)
    with pytest.raises(KRXPrivateStoreError, match="checksum mismatch"):
        verify_raw_object(root, out["raw_object_sha256"])

    root2 = (tmp_path / "private2").resolve()
    out2 = write_raw_object(root2, b"abc")
    with pytest.raises(KRXPrivateStoreError, match="size mismatch"):
        verify_raw_object(root2, out2["raw_object_sha256"], expected_size=999)


def test_private_json_is_secret_free_and_private(tmp_path):
    root = (tmp_path / "private").resolve()
    out = write_private_json(
        root,
        "receipts/r1.json",
        {"receipt_id": "r1", "row_count": 10},
    )
    target = root / out["metadata_relpath"]
    assert target.is_file()
    assert target.stat().st_mode & 0o777 == 0o600

    with pytest.raises(KRXPrivateStoreError, match="secret-like metadata key"):
        write_private_json(
            root,
            "receipts/bad.json",
            {"headers": {"Authorization": "forbidden"}},
        )


def test_private_json_rejects_path_escape(tmp_path):
    root = (tmp_path / "private").resolve()
    with pytest.raises(KRXPrivateStoreError, match="relpath is unsafe"):
        write_private_json(root, "../escape.json", {"x": 1})
