"""Independent evidence gate for a *new* PR-merged offline candidate lineage.

Archived regression identity remains immutable and independently checked by
research_v1_runtime_archived_source_gate.py. The archived source gate still
intentionally FAILS on the changed upstream manifest; DO NOT reinterpret this
candidate-mode proof as the old archived code replay or as merge authorization.

This gate binds to exact reviewed upstream #413 HEAD and precisely four
reviewed changed-from-archive implementation/control blobs, all fetched from GitHub. It rejects
any other changes to archived test definitions / direct implementations.
No PIT market data, official OpenDART, holdout, profitability, or trades.
"""
from __future__ import annotations

import json
from pathlib import Path
import stat

import research_v1_runtime_ci as ci
import research_v1_runtime_archived_source_gate as original

APPROVED_SCOPE_BASE_REF = "index-alert-backtest-runtime-opt-v1-20261013"
APPROVED_SCOPE_HEAD_REF = "index-alert-backtest-single-runner-opt-v1-20261013"
# Explicit candidate comparison target, NOT a frozen-strategy promotion.
EXACT_UPSTREAM_HEAD = "f003ef6247e16fcc71bd3b1b20cd4904c4d984c0"

# Only code change allowed relative to the archived direct implementations:
# original research_v1_runtime_manifest.py
# 108f66714602a1bd3ae42c34dcca7c16e38f460b
# becomes e0055c66... after no-follow/TOCTOU, literal-false holdout/live\n# permission and six auxiliary privilege-alias guards in green #413.
EXACT_UPSTREAM_CHANGED_BLOBS = {
    "research_v1_runtime_manifest.py": "e0055c66c59398fd4a1158077446d886b54c4e37",
    "research_v1_runtime_one_runner.py": "0c792b66daa46bdc7725fdcfde17ced975fb2c55",
    "research_v1_runtime_ci.py": "7306e4f57e0056960452f1991b5c95ba7413f11e",
    "test_research_v1_runtime_ci_integrity.py": "bb2e5d8f81d9052a16005d1b5642598268dd17d8",
}
# The independent environment-version attestor is now also bound, so a
# modified attestor cannot silently declare a different dependency baseline.
EXACT_LOCAL_ENV_GUARD_BLOBS = {
    "research_v1_runtime_archived_env_gate.py": "9a7af4ec2f3742448962f76ab4e8fadf8521c9ff",
}
EXPECTED_CURRENT_ARCHIVED_MANIFEST = "108f66714602a1bd3ae42c34dcca7c16e38f460b"


class CandidateLineageError(ValueError):
    """No silent re-pin, changed merge-base or unexpected code mutation."""


def strict_candidate_files() -> dict[str, str]:
    if (original.ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS.get(
            "research_v1_runtime_manifest.py") != EXPECTED_CURRENT_ARCHIVED_MANIFEST):
        raise CandidateLineageError("archived manifest baseline changed")
    if ci.SUITES != original.ARCHIVED_SUITES or ci.PINNED_CASES != original.ARCHIVED_PINNED_CASES:
        raise CandidateLineageError("frozen case/suite baseline altered")
    base = dict(original.ARCHIVED_GIT_BLOBS)
    base.update({
        k: v for k, v in original.ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS.items()
        if k != "research_v1_runtime_manifest.py"
    })
    if (set(base).intersection(EXACT_LOCAL_ENV_GUARD_BLOBS)
            or set(EXACT_UPSTREAM_CHANGED_BLOBS).intersection(EXACT_LOCAL_ENV_GUARD_BLOBS)):
        raise CandidateLineageError("local archived environment attestor collides with originals")
    if set(base).intersection(EXACT_UPSTREAM_CHANGED_BLOBS):
        raise CandidateLineageError("candidate blobs collide with immutable originals")
    return {**base, **EXACT_UPSTREAM_CHANGED_BLOBS, **EXACT_LOCAL_ENV_GUARD_BLOBS}


def check_candidate(root: Path, *, base_ref: str, head_ref: str,
                    base_head_sha: str, event_name: str) -> dict:
    if (base_ref != APPROVED_SCOPE_BASE_REF
            or head_ref != APPROVED_SCOPE_HEAD_REF
            or base_head_sha != EXACT_UPSTREAM_HEAD
            or event_name != "pull_request"):
        raise CandidateLineageError("not the exact reviewed PR synthetic merge scope")
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise CandidateLineageError("candidate checkout root missing or symlinked")
    files = strict_candidate_files()
    if len(files) != 22:
        raise CandidateLineageError("candidate checked source set altered")
    for filename, expected in sorted(files.items()):
        path = root / filename
        if (path.is_symlink() or not path.is_file()
                or not stat.S_ISREG(path.stat().st_mode)):
            raise CandidateLineageError("candidate source missing/unsafe: " + filename)
        digest = original.git_blob_sha1(path.read_bytes())
        if digest != expected:
            raise CandidateLineageError(
                "candidate merge source drift: " + filename
            )
    return {
        "schema": "indexalert-isolated-candidate-merge-source-v1",
        "checked_files": len(files),
        "original_eight_test_blobs_kept": True,
        "original_eight_other_direct_implementation_blobs_kept": True,
        "exact_four_reviewed_candidate_code_blobs_verified": True,
        "exact_upstream_head": EXACT_UPSTREAM_HEAD,
        "original_archived_manifest_replayed_without_change": False,
        "archived_case_sha256": original.ARCHIVED_CASE_DIGEST,
        "candidate_source_lineage_consistent": True,
        "candidate_approved_for_merge": False,
        "all_transitive_imports_pinned": False,
        "official_pit_admitted": False,
        "actual_backtest_performance_measured": False,
        "profitability_evaluated": False,
        "holdout_accessed": False,
        "ordering": False,
    }


def main() -> None:
    import os
    report = check_candidate(
        Path("."),
        base_ref=os.environ.get("GITHUB_BASE_REF", ""),
        head_ref=os.environ.get("GITHUB_HEAD_REF", ""),
        base_head_sha=os.environ.get("INDEXALERT_BASE_HEAD_SHA", ""),
        event_name=os.environ.get("GITHUB_EVENT_NAME", ""),
    )
    print("CANDIDATE_MERGED_SOURCE_PROOF=" + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
