"""Transactional structural prospective-session assembly.

This module joins the previously separate prospective boundaries into one
fail-closed session transaction:

official KRX OpenAPI raw bytes -> immutable source receipt -> label-free current
input -> freeze-anchor producer/model binding -> append-only decision -> final
session manifest.

The final manifest is the only structural "session committed" marker. A crash
or validation failure may leave immutable component artifacts, but without the
manifest the session is not considered committed. Nothing here independently
admits source/model/chronology evidence or authorizes a trade.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

import pandas as pd

from research_v1_krx_openapi_prospective_source import (
    build_current_session_openapi_source,
    store_current_session_openapi_source,
)
from research_v1_krx_private_store import validate_private_root
from research_v1_prospective_decision_capture import (
    build_decision_capture,
    store_decision_capture,
)
from research_v1_prospective_frozen_producer import (
    bind_prebuilt_model_for_target,
    fit_frozen_model_for_target,
    store_producer_binding,
)
from research_v1_prospective_inputs import (
    RAW_COLUMNS,
    build_current_session_inputs,
    input_snapshot_sha256,
    store_input_snapshot,
)
from research_v1_prospective_model_bundle import store_model_bundle


CLASSIFICATION = "STRUCTURAL_PROSPECTIVE_SESSION_COMMIT_NOT_ADMITTED"
_MANIFEST_FIELDS = (
    "classification", "session", "source_receipt_sha256",
    "input_snapshot_sha256", "producer_binding_sha256",
    "model_bundle_sha256", "decision_capture_sha256",
    "source_component_stored", "input_component_stored",
    "producer_component_stored", "model_component_stored",
    "decision_component_stored", "structural_session_committed",
    "independent_source_admission_verified",
    "independent_model_admission_verified",
    "independent_chronology_admission_verified",
    "fresh_alpha_observation_admitted", "formal_shadow_s1",
    "fresh_confirmation_s2", "promotion_authority",
    "live_order_authorized",
)


class ProspectiveSessionCommitError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: Any, field: str) -> str:
    if type(value) is not str or len(value) != 64 or any(
        c not in "0123456789abcdef" for c in value
    ):
        raise ProspectiveSessionCommitError(f"{field} must be lowercase SHA-256")
    return value


def _session(value: Any) -> str:
    if type(value) is not str:
        raise ProspectiveSessionCommitError("session must be canonical YYYY-MM-DD")
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ProspectiveSessionCommitError("session is invalid") from exc
    if parsed.tzinfo is not None or parsed.strftime("%Y-%m-%d") != value:
        raise ProspectiveSessionCommitError("session must be canonical YYYY-MM-DD")
    return value


def _history_without_target(history_raw: pd.DataFrame, target_session: str) -> pd.DataFrame:
    if not isinstance(history_raw, pd.DataFrame) or history_raw.empty:
        raise ProspectiveSessionCommitError("nonempty prior-session history is required")
    missing = sorted(set(RAW_COLUMNS) - set(history_raw.columns))
    if missing:
        raise ProspectiveSessionCommitError(f"history missing raw columns: {missing}")
    out = history_raw.loc[:, RAW_COLUMNS].copy()
    dates = pd.to_datetime(out["decision_date"], errors="coerce")
    if dates.isna().any() or dates.dt.tz is not None:
        raise ProspectiveSessionCommitError("history decision_date invalid")
    out["decision_date"] = dates.dt.normalize()
    target = pd.Timestamp(target_session)
    if (out["decision_date"] >= target).any():
        raise ProspectiveSessionCommitError(
            "history_raw must contain only sessions before target_session"
        )
    return out


def validate_session_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise ProspectiveSessionCommitError("session manifest must be an object")
    expected = set(_MANIFEST_FIELDS) | {"session_manifest_sha256"}
    if set(manifest) != expected:
        raise ProspectiveSessionCommitError("session manifest fields mismatch")
    if manifest.get("classification") != CLASSIFICATION:
        raise ProspectiveSessionCommitError("session manifest classification mismatch")
    session = _session(manifest.get("session"))
    for field in (
        "source_receipt_sha256", "input_snapshot_sha256",
        "producer_binding_sha256", "model_bundle_sha256",
        "decision_capture_sha256", "session_manifest_sha256",
    ):
        _digest(manifest.get(field), field)
    for field in (
        "source_component_stored", "input_component_stored",
        "producer_component_stored", "model_component_stored",
        "decision_component_stored", "structural_session_committed",
    ):
        if manifest.get(field) is not True:
            raise ProspectiveSessionCommitError(f"{field} must be exact true")
    for field in (
        "independent_source_admission_verified",
        "independent_model_admission_verified",
        "independent_chronology_admission_verified",
        "fresh_alpha_observation_admitted", "formal_shadow_s1",
        "fresh_confirmation_s2", "promotion_authority",
        "live_order_authorized",
    ):
        if manifest.get(field) is not False:
            raise ProspectiveSessionCommitError(f"{field} must remain exact false")
    body = {field: manifest[field] for field in _MANIFEST_FIELDS}
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if manifest["session_manifest_sha256"] != actual:
        raise ProspectiveSessionCommitError("session manifest fingerprint mismatch")
    return {
        "valid": True,
        "session": session,
        "session_manifest_sha256": actual,
        "structural_session_committed": True,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }


def store_session_manifest(
    manifest: Mapping[str, Any], *, root: str, git_worktree: str
) -> dict[str, Any]:
    validation = validate_session_manifest(manifest)
    payload = _canonical(dict(manifest))
    base = validate_private_root(root, git_worktree=git_worktree)
    target = base / f"session-{manifest['session']}.json"
    fd, name = tempfile.mkstemp(prefix=".session-", dir=base)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o600)
        try:
            os.link(temp, target)
            created = True
        except FileExistsError:
            if target.is_symlink() or target.read_bytes() != payload:
                raise ProspectiveSessionCommitError(
                    "conflicting or tampered same-session commit manifest"
                )
            created = False
        directory = os.open(base, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temp.unlink(missing_ok=True)
    return {
        "session_manifest_sha256": validation["session_manifest_sha256"],
        "created": created,
        "structural_session_committed": True,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }


def commit_structural_prospective_session(
    *,
    daily_raw: bytes,
    master_raw: bytes,
    daily_retrieved_at: str,
    master_retrieved_at: str,
    connectivity_evidence: Mapping[str, Any],
    history_raw: pd.DataFrame,
    supervised_frame: pd.DataFrame | None,
    prebuilt_model_bundle: Mapping[str, Any] | None = None,
    session_calendar: Sequence[Any],
    target_session: str,
    decision_at: str,
    captured_at: str,
    root: str,
    git_worktree: str,
) -> dict[str, Any]:
    """Build and durably commit one structural future session.

    Component artifacts are immutable and may survive a failure. Only the final
    session manifest marks the transaction structurally complete.
    """
    target = _session(target_session)
    history = _history_without_target(history_raw, target)

    source = build_current_session_openapi_source(
        daily_raw=daily_raw,
        master_raw=master_raw,
        expected_session=target,
        daily_retrieved_at=daily_retrieved_at,
        master_retrieved_at=master_retrieved_at,
        connectivity_evidence=connectivity_evidence,
    )
    if source["session"] != target:
        raise ProspectiveSessionCommitError("source session mismatch")
    source_store = store_current_session_openapi_source(
        source,
        daily_raw=daily_raw,
        master_raw=master_raw,
        root=root,
        git_worktree=git_worktree,
    )

    current = source["panel"].loc[:, RAW_COLUMNS].copy()
    raw = pd.concat([history, current], ignore_index=True)
    snapshot = build_current_session_inputs(
        raw,
        decision_at=decision_at,
        source_receipt_sha256=source["source_receipt_sha256"],
    )
    if snapshot["session"] != target:
        raise ProspectiveSessionCommitError("input snapshot session mismatch")
    if snapshot.get("source_receipt_bound") is not True or snapshot.get(
        "source_receipt_sha256"
    ) != source["source_receipt_sha256"]:
        raise ProspectiveSessionCommitError("input/source receipt binding mismatch")
    snapshot_sha = input_snapshot_sha256(snapshot)

    if prebuilt_model_bundle is None:
        if supervised_frame is None:
            raise ProspectiveSessionCommitError(
                "supervised_frame is required when no prebuilt model bundle is supplied"
            )
        producer = fit_frozen_model_for_target(
            supervised_frame,
            session_calendar=session_calendar,
            target_session=target,
        )
    else:
        if supervised_frame is not None:
            raise ProspectiveSessionCommitError(
                "prebuilt model path must not also receive supervised_frame"
            )
        producer = bind_prebuilt_model_for_target(
            prebuilt_model_bundle,
            session_calendar=session_calendar,
            target_session=target,
        )
    binding = producer["producer_binding"]
    bundle = producer["model_bundle"]
    if binding["target_session"] != target:
        raise ProspectiveSessionCommitError("producer target session mismatch")

    model_store = store_model_bundle(
        bundle, root=root, git_worktree=git_worktree
    )
    producer_store = store_producer_binding(
        binding, bundle, root=root, git_worktree=git_worktree
    )
    input_store = store_input_snapshot(
        snapshot, root=root, git_worktree=git_worktree
    )
    if input_store["snapshot_sha256"] != snapshot_sha:
        raise ProspectiveSessionCommitError("stored input fingerprint mismatch")

    decision = build_decision_capture(
        snapshot,
        bundle,
        producer_binding=binding,
        input_snapshot_sha256=snapshot_sha,
        captured_at=captured_at,
    )
    if decision["session"] != target:
        raise ProspectiveSessionCommitError("decision session mismatch")
    decision_store = store_decision_capture(
        decision, root=root, git_worktree=git_worktree
    )

    body = {
        "classification": CLASSIFICATION,
        "session": target,
        "source_receipt_sha256": source_store["source_receipt_sha256"],
        "input_snapshot_sha256": snapshot_sha,
        "producer_binding_sha256": producer_store["producer_binding_sha256"],
        "model_bundle_sha256": model_store["model_bundle_sha256"],
        "decision_capture_sha256": decision_store["decision_capture_sha256"],
        "source_component_stored": True,
        "input_component_stored": True,
        "producer_component_stored": True,
        "model_component_stored": True,
        "decision_component_stored": True,
        "structural_session_committed": True,
        "independent_source_admission_verified": False,
        "independent_model_admission_verified": False,
        "independent_chronology_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "formal_shadow_s1": False,
        "fresh_confirmation_s2": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }
    manifest_sha = hashlib.sha256(_canonical(body)).hexdigest()
    manifest = {**body, "session_manifest_sha256": manifest_sha}
    manifest_store = store_session_manifest(
        manifest, root=root, git_worktree=git_worktree
    )
    return {
        "session": target,
        "source_receipt_sha256": source_store["source_receipt_sha256"],
        "input_snapshot_sha256": snapshot_sha,
        "producer_binding_sha256": producer_store["producer_binding_sha256"],
        "model_bundle_sha256": model_store["model_bundle_sha256"],
        "decision_capture_sha256": decision_store["decision_capture_sha256"],
        "session_manifest_sha256": manifest_store["session_manifest_sha256"],
        "structural_session_committed": True,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }
