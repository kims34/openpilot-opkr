"""Hash-only GitHub chronology anchor for prospective structural sessions.

A local/Railway file timestamp is not independent proof that a decision existed
before later outcomes. This module creates and validates a secret-free anchor
record containing only session/timestamp claims and SHA-256 identities.

The GitHub workflow commits that record to a dedicated evidence branch. The
record itself does not self-admit chronology; a later trusted verifier must
fetch the actual GitHub commit metadata and bind it back to the private decision
capture before independent chronology admission can become true.
"""
from __future__ import annotations

from datetime import datetime
import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

import pandas as pd

from research_v1_prospective_decision_capture import validate_decision_capture
from research_v1_prospective_session_commit import validate_session_manifest


CLASSIFICATION = "HASH_ONLY_GITHUB_CHRONOLOGY_ANCHOR_NOT_ADMITTED"
ANCHOR_BRANCH = "index-alert-prospective-anchors-v1"
REPOSITORY_FULL_NAME = "kims34/openpilot-opkr"
WORKFLOW_NAME = "IndexAlert Prospective Chronology Anchor"
MAX_ANCHOR_LAG_SECONDS = 6 * 60 * 60
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
_BODY_FIELDS = (
    "classification", "repository_full_name", "anchor_branch",
    "workflow_name", "workflow_ref_commit", "session", "decision_at",
    "source_receipt_sha256", "input_snapshot_sha256",
    "producer_binding_sha256", "model_bundle_sha256",
    "decision_capture_sha256", "session_manifest_sha256",
    "security_identifiers_disclosed", "ranked_scores_disclosed",
    "selected_candidates_disclosed", "outcomes_attached",
    "independent_chronology_admission_verified",
    "fresh_alpha_observation_admitted", "promotion_authority",
    "live_order_authorized",
)


class ProspectiveChronologyAnchorError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha(value: Any, field: str, pattern=HEX64) -> str:
    if type(value) is not str or not pattern.fullmatch(value):
        raise ProspectiveChronologyAnchorError(f"{field} must be canonical lowercase hex")
    return value


def _session(value: Any) -> str:
    if type(value) is not str:
        raise ProspectiveChronologyAnchorError("session must be YYYY-MM-DD")
    try:
        day = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ProspectiveChronologyAnchorError("session is invalid") from exc
    if day.tzinfo is not None or day.strftime("%Y-%m-%d") != value:
        raise ProspectiveChronologyAnchorError("session must be canonical YYYY-MM-DD")
    return value


def _aware(value: Any, field: str) -> pd.Timestamp:
    if not isinstance(value, (str, datetime, pd.Timestamp)) or pd.isna(value):
        raise ProspectiveChronologyAnchorError(f"{field} must be timezone-aware")
    try:
        ts = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ProspectiveChronologyAnchorError(f"{field} invalid") from exc
    if ts.tzinfo is None or ts.utcoffset() is None:
        raise ProspectiveChronologyAnchorError(f"{field} must be timezone-aware")
    return ts.tz_convert("UTC")


def build_anchor_record(
    *,
    session: str,
    decision_at: str,
    source_receipt_sha256: str,
    input_snapshot_sha256: str,
    producer_binding_sha256: str,
    model_bundle_sha256: str,
    decision_capture_sha256: str,
    session_manifest_sha256: str,
    workflow_ref_commit: str,
) -> dict[str, Any]:
    session = _session(session)
    decision = _aware(decision_at, "decision_at")
    if decision.tz_convert("Asia/Seoul").strftime("%Y-%m-%d") != session:
        raise ProspectiveChronologyAnchorError("decision_at/session mismatch")
    body = {
        "classification": CLASSIFICATION,
        "repository_full_name": REPOSITORY_FULL_NAME,
        "anchor_branch": ANCHOR_BRANCH,
        "workflow_name": WORKFLOW_NAME,
        "workflow_ref_commit": _sha(
            workflow_ref_commit, "workflow_ref_commit", pattern=HEX40
        ),
        "session": session,
        "decision_at": decision.isoformat(),
        "source_receipt_sha256": _sha(
            source_receipt_sha256, "source_receipt_sha256"
        ),
        "input_snapshot_sha256": _sha(
            input_snapshot_sha256, "input_snapshot_sha256"
        ),
        "producer_binding_sha256": _sha(
            producer_binding_sha256, "producer_binding_sha256"
        ),
        "model_bundle_sha256": _sha(
            model_bundle_sha256, "model_bundle_sha256"
        ),
        "decision_capture_sha256": _sha(
            decision_capture_sha256, "decision_capture_sha256"
        ),
        "session_manifest_sha256": _sha(
            session_manifest_sha256, "session_manifest_sha256"
        ),
        "security_identifiers_disclosed": False,
        "ranked_scores_disclosed": False,
        "selected_candidates_disclosed": False,
        "outcomes_attached": False,
        "independent_chronology_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }
    digest = hashlib.sha256(_canonical(body)).hexdigest()
    return {**body, "anchor_record_sha256": digest}


def validate_anchor_record(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise ProspectiveChronologyAnchorError("anchor record must be an object")
    expected = set(_BODY_FIELDS) | {"anchor_record_sha256"}
    if set(record) != expected:
        raise ProspectiveChronologyAnchorError("anchor fields mismatch")
    if record.get("classification") != CLASSIFICATION:
        raise ProspectiveChronologyAnchorError("anchor classification mismatch")
    if record.get("repository_full_name") != REPOSITORY_FULL_NAME:
        raise ProspectiveChronologyAnchorError("repository identity mismatch")
    if record.get("anchor_branch") != ANCHOR_BRANCH:
        raise ProspectiveChronologyAnchorError("anchor branch mismatch")
    if record.get("workflow_name") != WORKFLOW_NAME:
        raise ProspectiveChronologyAnchorError("workflow identity mismatch")
    _sha(record.get("workflow_ref_commit"), "workflow_ref_commit", pattern=HEX40)
    session = _session(record.get("session"))
    decision = _aware(record.get("decision_at"), "decision_at")
    if decision.tz_convert("Asia/Seoul").strftime("%Y-%m-%d") != session:
        raise ProspectiveChronologyAnchorError("decision/session mismatch")
    for field in (
        "source_receipt_sha256", "input_snapshot_sha256",
        "producer_binding_sha256", "model_bundle_sha256",
        "decision_capture_sha256", "session_manifest_sha256",
        "anchor_record_sha256",
    ):
        _sha(record.get(field), field)
    for field in (
        "security_identifiers_disclosed", "ranked_scores_disclosed",
        "selected_candidates_disclosed", "outcomes_attached",
        "independent_chronology_admission_verified",
        "fresh_alpha_observation_admitted", "promotion_authority",
        "live_order_authorized",
    ):
        if record.get(field) is not False:
            raise ProspectiveChronologyAnchorError(f"{field} must remain exact false")
    body = {field: record[field] for field in _BODY_FIELDS}
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if record["anchor_record_sha256"] != actual:
        raise ProspectiveChronologyAnchorError("anchor fingerprint mismatch")
    return {
        "valid": True,
        "session": session,
        "anchor_record_sha256": actual,
        "independent_chronology_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }


def validate_against_private_components(
    record: Mapping[str, Any],
    *,
    session_manifest: Mapping[str, Any],
    decision_capture: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind the hash-only public record back to the private session components."""
    anchor = validate_anchor_record(record)
    manifest = validate_session_manifest(session_manifest)
    decision = validate_decision_capture(decision_capture)
    pairs = (
        ("session_manifest_sha256", manifest["session_manifest_sha256"]),
        ("decision_capture_sha256", decision["decision_capture_sha256"]),
        ("source_receipt_sha256", session_manifest["source_receipt_sha256"]),
        ("input_snapshot_sha256", session_manifest["input_snapshot_sha256"]),
        ("producer_binding_sha256", session_manifest["producer_binding_sha256"]),
        ("model_bundle_sha256", session_manifest["model_bundle_sha256"]),
    )
    for field, expected in pairs:
        if record[field] != expected:
            raise ProspectiveChronologyAnchorError(f"{field} private binding mismatch")
    if record["session"] != session_manifest["session"] or record["session"] != decision_capture["session"]:
        raise ProspectiveChronologyAnchorError("session private binding mismatch")
    if _aware(record["decision_at"], "decision_at") != _aware(
        decision_capture["decision_at"], "decision_capture.decision_at"
    ):
        raise ProspectiveChronologyAnchorError("decision_at private binding mismatch")
    return {
        "valid": True,
        "session": anchor["session"],
        "private_components_bound": True,
        "independent_chronology_admission_verified": False,
        "blocker": "TRUSTED_GITHUB_COMMIT_METADATA_NOT_YET_VERIFIED",
    }


def assess_external_github_commit(
    record: Mapping[str, Any],
    *,
    commit_sha: str,
    commit_created_at: str,
) -> dict[str, Any]:
    """Assess externally fetched GitHub commit metadata without self-admission.

    Callers must obtain commit metadata from GitHub, not from the producer
    runtime. Even then this function reports structural conditions; the
    canonical admission path must also bind the private components.
    """
    validate_anchor_record(record)
    commit = _sha(commit_sha, "commit_sha", pattern=HEX40)
    created = _aware(commit_created_at, "commit_created_at")
    decision = _aware(record["decision_at"], "decision_at")
    lag = float((created - decision).total_seconds())
    blockers = []
    if lag < 0:
        blockers.append("GITHUB_COMMIT_PRECEDES_DECLARED_DECISION")
    if lag > MAX_ANCHOR_LAG_SECONDS:
        blockers.append("GITHUB_ANCHOR_LAG_EXCEEDS_6H")
    return {
        "github_commit_sha": commit,
        "github_commit_created_at": created.isoformat(),
        "anchor_lag_seconds": lag,
        "chronology_conditions_structurally_satisfied": not blockers,
        "blockers": blockers,
        "independent_chronology_admission_verified": False,
        "admission_blocker": "TRUSTED_ADAPTER_MUST_BIND_GITHUB_COMMIT_AND_PRIVATE_COMPONENTS",
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    parser.add_argument("--decision-at", required=True)
    parser.add_argument("--source-receipt-sha256", required=True)
    parser.add_argument("--input-snapshot-sha256", required=True)
    parser.add_argument("--producer-binding-sha256", required=True)
    parser.add_argument("--model-bundle-sha256", required=True)
    parser.add_argument("--decision-capture-sha256", required=True)
    parser.add_argument("--session-manifest-sha256", required=True)
    parser.add_argument("--workflow-ref-commit", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    record = build_anchor_record(
        session=args.session,
        decision_at=args.decision_at,
        source_receipt_sha256=args.source_receipt_sha256,
        input_snapshot_sha256=args.input_snapshot_sha256,
        producer_binding_sha256=args.producer_binding_sha256,
        model_bundle_sha256=args.model_bundle_sha256,
        decision_capture_sha256=args.decision_capture_sha256,
        session_manifest_sha256=args.session_manifest_sha256,
        workflow_ref_commit=args.workflow_ref_commit,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(_canonical(record) + b"\n")
    print(json.dumps({
        "session": record["session"],
        "anchor_record_sha256": record["anchor_record_sha256"],
        "security_identifiers_disclosed": False,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
