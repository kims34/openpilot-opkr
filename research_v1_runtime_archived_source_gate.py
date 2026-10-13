"""Fail-closed provenance gate for archived *test definitions*, not market data.

Testcase names/outcomes alone cannot detect changing tested code while
keeping public test names and outcomes. Direct test import implementations are
pinned separately; not the entire transitive dependency closure. These pinned Git blob identities were
cross-checked against successful archived GitHub run #38382214223, at commit
05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56, and the isolated PR #418 tree.
This does NOT authenticate official KRX/OpenDART, prove end-to-end reproducibility
of Python transitive dependencies, or authorize any economic analysis/trading.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat

import research_v1_runtime_ci as ci

BASELINE_COMMIT = "05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56"
BASELINE_RUN_ID = 38382214223
ARCHIVED_CASE_DIGEST = "5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34"

# Git's exact content-addressed blob SHA-1 values: verified against independent
# archived successful run's checkout, rather than regenerated on latest HEAD.
ARCHIVED_GIT_BLOBS = {
    "test_research_v1_pit_tax.py": "eaf38d7c861263dc13e409044cd28df975f6716d",
    "test_research_v1_core.py": "e84f1eaa42ba7e739346874c4f58bc4a12a2f489",
    "test_research_v1_portfolio.py": "479224b6f893aaca57abdb49f1c3f5664cb83800",
    "test_research_v1_distributional_netev.py": "bb2ed75f115fd1251d64b2041f1755145fb51161",
    "test_research_v1_medium_swing_prereg.py": "fa01d38402ac37801be1cfb2c1696ba566b4d425",
    "test_research_v1_purged.py": "e6ce669385bac40f1d6493b44163405d721742ac",
    "test_research_v1_supervised_cache.py": "ea096c6e7e51ff323a253db4f4f570d19834954e",
    "test_research_v1_runtime_manifest.py": "c633132550f0f7ff670f650e84609e3d32ffc557",
    "requirements-indexalert-runtime-ci.txt": "30a965e1899d761158ecce0c0d05172b895d2ae5",
}
# Direct local implementations imported by the archived eight tests.
# Cross-checked against commit 05d73661... by separate historic/current
# GitHub fetch_file requests (9 of 9 exact blob SHA identities). This is
# intentionally a DIRECT import manifest; it does not assert a complete
# transitive import closure or whole-runtime reproducibility.
ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS = {
    "research_v1_pit_labels.py": "91ef828617ea77713f1ddca0c427fadaf1114f0a",
    "research_v1_core.py": "7aaa01338b11c119497050282b53fcf7d13a2b8d",
    "research_v1_portfolio.py": "9233c6699a01b35f63167a002d16c0114a430d2c",
    "research_v1_distributional_netev.py": "4019f01a58c1378edeec7ace55215a62b4ad6fd4",
    "research_v1_medium_swing_prereg.py": "a7f0c40c5dbb7f9daf2959857d0f683b543a0c6f",
    "research_v1_ml.py": "614b6624ca145fd711462f5d8fb528740643ce9",
    "research_v1_pit_run_purged.py": "cb610bec52168d24a394a5fc145691038d4666a4",
    "research_v1_supervised_cache.py": "6a9273f987699c0b9d6053f33bf2ecdc0bda75ce",
    "research_v1_runtime_manifest.py": "108f66714602a1bd3ae42c34dcca7c16e38f460b",
}

ARCHIVED_SUITES = {
    "cost": ("test_research_v1_pit_tax.py", "test_research_v1_core.py"),
    "risk": ("test_research_v1_portfolio.py", "test_research_v1_distributional_netev.py"),
    "gates": ("test_research_v1_medium_swing_prereg.py", "test_research_v1_purged.py"),
    "cache": ("test_research_v1_supervised_cache.py", "test_research_v1_runtime_manifest.py"),
}
ARCHIVED_PINNED_CASES = {
    "cost": (9, "0a11d4eca07ce83f32758d8fe8aa62ab5e5450bd9e9bd6413bdb9691e13213c9"),
    "risk": (9, "49185a1d6fcf193c710959d8b07e274114c884158f2d7ffac226bc9df9bd47e6"),
    "gates": (8, "717cd517fb407727db2dee99e1fdcdc39d9033f70dabbb68609dcd4a1ee6cd33"),
    "cache": (8, "2353b8399ba17dc1ec22334bf7be99609ceef05c4342fd3c1e99134a637f59a5"),
    "all": (34, ARCHIVED_CASE_DIGEST),
}


class SourceDriftError(ValueError):
    """Unexpected test definition, dependency manifest or pinned policy."""


def git_blob_sha1(contents: bytes) -> str:
    """Git object identity; not a collision-resistant authenticated signature."""
    return hashlib.sha1(
        b"blob " + str(len(contents)).encode("ascii") + b"\0" + contents
    ).hexdigest()


def validate_source_definitions(root: Path) -> dict:
    """Reject silent test rewriting even if result names/hash appear unchanged."""
    if ci.SUITES != ARCHIVED_SUITES or ci.PINNED_CASES != ARCHIVED_PINNED_CASES:
        raise SourceDriftError("archived test-split or expected-result policy drift")
    if set(ci._expected_files("all")) != (set(ARCHIVED_GIT_BLOBS)
                                            - {"requirements-indexalert-runtime-ci.txt"}):
        raise SourceDriftError("archived test file coverage changed")
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise SourceDriftError("source tree root missing or symlinked")
    actual = {}
    for name, expected in {
        **ARCHIVED_GIT_BLOBS, **ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS
    }.items():
        path = root / name
        if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise SourceDriftError("archived source missing or nonregular: " + name)
        digest = git_blob_sha1(path.read_bytes())
        if digest != expected:
            raise SourceDriftError("archived blob mismatch: " + name + " expected=" + expected + " observed=" + digest)
        actual[name] = digest
    return {
        "source_definition_drift_detected": False,
        "archived_regression_source_files": 8,
        "archived_direct_implementation_files": len(ARCHIVED_DIRECT_IMPLEMENTATION_BLOBS),
        "all_transitive_imports_pinned": False,
        "archived_environment_manifest_files": 1,
        "original_archived_checkout_commit": BASELINE_COMMIT,
        "original_archived_actions_run_id": BASELINE_RUN_ID,
        "fixed_test_case_digest_sha256": ARCHIVED_CASE_DIGEST,
        "git_blob_shas_verified": True,
        "source_pit_admitted": False,
        "profitability_evaluated": False,
        "holdout_accessed": False,
        "ordering": False,
    }


def main() -> None:
    result = validate_source_definitions(Path("."))
    print("ARCHIVED_REGRESSION_SOURCE_PROOF=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
