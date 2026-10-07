"""Online GitHub chronology verifier for prospective IndexAlert sessions.

This is the first path allowed to set independent_chronology_admission_verified
true. It does so only after reading the private immutable session/decision files
and independently querying GitHub for the anchor file, the exact workflow run,
and the anchor-branch commit that added that file.

It does not admit source/model evidence, attach outcomes, promote Alpha, or
authorize any order.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

import requests

from research_v1_krx_private_store import validate_private_root_path
from research_v1_prospective_chronology_anchor import (
    ANCHOR_BRANCH,
    MAX_ANCHOR_LAG_SECONDS,
    REPOSITORY_FULL_NAME,
    WORKFLOW_NAME,
    ProspectiveChronologyAnchorError,
    _aware,
    _canonical,
    _session,
    validate_against_private_components,
    validate_anchor_record,
)
from research_v1_prospective_decision_capture import validate_decision_capture
from research_v1_prospective_session_commit import validate_session_manifest


CLASSIFICATION = "GITHUB_CHRONOLOGY_ADMISSION_VERIFIED"
WORKFLOW_PATH = ".github/workflows/indexalert-prospective-chronology-anchor.yml"
BOT_LOGIN = "github-actions[bot]"
API_BASE = "https://api.github.com"
HTTP_TIMEOUT_SECONDS = 10
HEX40 = set("0123456789abcdef")


class ProspectiveChronologyAdmissionError(ValueError):
    pass


def _strict_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ProspectiveChronologyAdmissionError(
                f"duplicate JSON key: {key}"
            )
        out[key] = value
    return out


def _strict_json_bytes(raw: bytes, field: str) -> Any:
    if not isinstance(raw, (bytes, bytearray)) or not raw:
        raise ProspectiveChronologyAdmissionError(f"{field} is empty")
    try:
        text = bytes(raw).decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ProspectiveChronologyAdmissionError(
                    f"{field} contains non-standard JSON constant: {value}"
                )
            ),
        )
    except UnicodeDecodeError as exc:
        raise ProspectiveChronologyAdmissionError(
            f"{field} is not UTF-8 JSON"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ProspectiveChronologyAdmissionError(
            f"{field} is invalid JSON"
        ) from exc


def _sha40(value: Any, field: str) -> str:
    if (
        type(value) is not str
        or len(value) != 40
        or any(ch not in HEX40 for ch in value)
    ):
        raise ProspectiveChronologyAdmissionError(
            f"{field} must be lowercase 40-char git SHA"
        )
    return value


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "indexalert-prospective-chronology-verifier-v1",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    return headers


def _github_get_json(path: str, *, params: Mapping[str, Any] | None = None) -> Any:
    url = API_BASE + path
    try:
        response = requests.get(
            url,
            headers=_github_headers(),
            params=dict(params or {}),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise ProspectiveChronologyAdmissionError(
            "GitHub verification request failed"
        ) from exc
    if response.status_code != 200:
        raise ProspectiveChronologyAdmissionError(
            f"GitHub verification returned HTTP {response.status_code}"
        )
    try:
        return response.json()
    except ValueError as exc:
        raise ProspectiveChronologyAdmissionError(
            "GitHub verification returned invalid JSON"
        ) from exc


def _read_private_json(path: Path, field: str) -> Mapping[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ProspectiveChronologyAdmissionError(
            f"{field} private artifact is missing or not a regular file"
        )
    value = _strict_json_bytes(path.read_bytes(), field)
    if not isinstance(value, Mapping):
        raise ProspectiveChronologyAdmissionError(f"{field} must be a JSON object")
    return value


def _fetch_anchor_commit_and_record(session: str) -> tuple[str, Mapping[str, Any]]:
    anchor_path = f"prospective_anchors/{session}.json"
    commits = _github_get_json(
        f"/repos/{REPOSITORY_FULL_NAME}/commits",
        params={"sha": ANCHOR_BRANCH, "path": anchor_path, "per_page": 100},
    )
    if not isinstance(commits, list) or len(commits) != 1:
        raise ProspectiveChronologyAdmissionError(
            "anchor path must have exactly one append-only commit"
        )
    commit_sha = _sha40(commits[0].get("sha"), "anchor_commit_sha")
    content = _github_get_json(
        f"/repos/{REPOSITORY_FULL_NAME}/contents/{anchor_path}",
        params={"ref": commit_sha},
    )
    if not isinstance(content, Mapping) or content.get("encoding") != "base64":
        raise ProspectiveChronologyAdmissionError(
            "GitHub anchor content is not canonical base64 content"
        )
    encoded = content.get("content")
    if type(encoded) is not str:
        raise ProspectiveChronologyAdmissionError("GitHub anchor content is missing")
    try:
        raw = base64.b64decode(encoded, validate=False)
    except Exception as exc:
        raise ProspectiveChronologyAdmissionError(
            "GitHub anchor base64 content is invalid"
        ) from exc
    record = _strict_json_bytes(raw, "GitHub anchor record")
    if not isinstance(record, Mapping):
        raise ProspectiveChronologyAdmissionError(
            "GitHub anchor record must be an object"
        )
    validate_anchor_record(record)
    if record["session"] != session:
        raise ProspectiveChronologyAdmissionError("GitHub anchor session mismatch")
    return commit_sha, record


def _verify_workflow_run(record: Mapping[str, Any]) -> dict[str, Any]:
    run_id = record["workflow_run_id"]
    run = _github_get_json(
        f"/repos/{REPOSITORY_FULL_NAME}/actions/runs/{run_id}"
    )
    if not isinstance(run, Mapping):
        raise ProspectiveChronologyAdmissionError("GitHub workflow run is invalid")
    checks = {
        "id": run_id,
        "run_attempt": record["workflow_run_attempt"],
        "name": WORKFLOW_NAME,
        "path": WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "status": "completed",
        "conclusion": "success",
        "head_sha": record["workflow_ref_commit"],
    }
    for field, expected in checks.items():
        if run.get(field) != expected:
            raise ProspectiveChronologyAdmissionError(
                f"GitHub workflow run {field} mismatch"
            )
    decision = _aware(record["decision_at"], "decision_at")
    created = _aware(run.get("created_at"), "workflow_run.created_at")
    lag = float((created - decision).total_seconds())
    if lag < 0:
        raise ProspectiveChronologyAdmissionError(
            "GitHub workflow run predates declared decision"
        )
    if lag > MAX_ANCHOR_LAG_SECONDS:
        raise ProspectiveChronologyAdmissionError(
            "GitHub workflow run exceeds six-hour anchor window"
        )
    return {
        "workflow_run_created_at": created.isoformat(),
        "anchor_lag_seconds": lag,
    }


def _verify_anchor_commit(
    *,
    commit_sha: str,
    record: Mapping[str, Any],
    run_created_at: str,
) -> dict[str, Any]:
    commit = _github_get_json(
        f"/repos/{REPOSITORY_FULL_NAME}/commits/{commit_sha}"
    )
    if not isinstance(commit, Mapping):
        raise ProspectiveChronologyAdmissionError("GitHub anchor commit is invalid")
    expected_message = (
        f"Anchor prospective session {record['session']} "
        f"(run {record['workflow_run_id']})"
    )
    payload = commit.get("commit")
    if not isinstance(payload, Mapping) or payload.get("message") != expected_message:
        raise ProspectiveChronologyAdmissionError(
            "GitHub anchor commit message/run binding mismatch"
        )
    committer = commit.get("committer")
    if not isinstance(committer, Mapping) or committer.get("login") != BOT_LOGIN:
        raise ProspectiveChronologyAdmissionError(
            "GitHub anchor commit was not attributed to github-actions[bot]"
        )
    commit_meta = payload.get("committer")
    if not isinstance(commit_meta, Mapping):
        raise ProspectiveChronologyAdmissionError("GitHub commit metadata missing")
    commit_time = _aware(commit_meta.get("date"), "anchor_commit.committer.date")
    run_time = _aware(run_created_at, "workflow_run.created_at")
    if commit_time < run_time:
        raise ProspectiveChronologyAdmissionError(
            "anchor commit time precedes GitHub workflow run creation"
        )
    # Commit timestamp is only a consistency check. The server-side workflow
    # run creation timestamp above is the chronology trust point.
    return {"github_anchor_commit_created_at": commit_time.isoformat()}


def verify_session_chronology_online(
    *,
    session: str,
    root: str,
    git_worktree: str,
) -> dict[str, Any]:
    """Verify one private session against live GitHub server evidence.

    This function performs public GitHub API reads. It never writes GitHub,
    never reads outcomes, and never changes source/model/trading authority.
    """
    session = _session(session)
    base = validate_private_root_path(root, git_worktree=git_worktree)
    manifest = _read_private_json(
        base / f"session-{session}.json", "session manifest"
    )
    decision = _read_private_json(
        base / f"decision-{session}.json", "decision capture"
    )
    validate_session_manifest(manifest)
    validate_decision_capture(decision)

    commit_sha, record = _fetch_anchor_commit_and_record(session)
    private = validate_against_private_components(
        record,
        session_manifest=manifest,
        decision_capture=decision,
    )
    if private.get("private_components_bound") is not True:
        raise ProspectiveChronologyAdmissionError(
            "private chronology components are not bound"
        )

    run = _verify_workflow_run(record)
    commit = _verify_anchor_commit(
        commit_sha=commit_sha,
        record=record,
        run_created_at=run["workflow_run_created_at"],
    )
    body = {
        "classification": CLASSIFICATION,
        "repository_full_name": REPOSITORY_FULL_NAME,
        "anchor_branch": ANCHOR_BRANCH,
        "session": session,
        "anchor_record_sha256": record["anchor_record_sha256"],
        "session_manifest_sha256": manifest["session_manifest_sha256"],
        "decision_capture_sha256": decision["decision_capture_sha256"],
        "workflow_run_id": record["workflow_run_id"],
        "workflow_run_attempt": record["workflow_run_attempt"],
        "workflow_ref_commit": record["workflow_ref_commit"],
        "github_anchor_commit_sha": commit_sha,
        "github_workflow_run_created_at": run["workflow_run_created_at"],
        "github_anchor_commit_created_at": commit[
            "github_anchor_commit_created_at"
        ],
        "anchor_lag_seconds": run["anchor_lag_seconds"],
        "private_components_bound": True,
        "github_server_chronology_verified": True,
        "independent_chronology_admission_verified": True,
        "independent_source_admission_verified": False,
        "independent_model_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "formal_shadow_s1": False,
        "fresh_confirmation_s2": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }
    digest = hashlib.sha256(_canonical(body)).hexdigest()
    return {**body, "chronology_admission_sha256": digest}
