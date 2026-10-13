"""Version-level runtime provenance for 2026-10-13 archived OFFLINE CI.

The 22 versions below were independently read from 'Successfully installed'
lines of archived GitHub job 115245168834 (run 38382214223) and the latest
isolated CI job 115594738030 (run 38484481047), and matched exactly.
This DOES NOT guarantee exact wheel file bytes, native BLAS/OS identities,
Python patch-level identity, historical PIT, or trading authorization.
"""
from __future__ import annotations

import json
from importlib import metadata
import sys

EXPECTED_PYTHON = (3, 12)
ARCHIVED_PACKAGES = {
    "certifi": "2026.7.22",
    "charset-normalizer": "3.5.2",
    "cloudpickle": "3.1.2",
    "idna": "3.20",
    "iniconfig": "2.3.1",
    "joblib": "1.6.0",
    "numpy": "2.5.3",
    "packaging": "26.3",
    "pandas": "2.3.3",
    "pluggy": "1.6.0",
    "pyarrow": "21.0.0",
    "pygments": "2.21.0",
    "pytest": "9.1.1",
    "python-dateutil": "2.9.0.post0",
    "pytz": "2026.5",
    "requests": "2.32.3",
    "scikit-learn": "1.7.2",
    "scipy": "1.18.1",
    "six": "1.17.0",
    "threadpoolctl": "3.7.0",
    "tzdata": "2026.5",
    "urllib3": "2.8.0",
}


class EnvironmentDriftError(ValueError):
    """Archived regression environment requirements are no longer met."""


def check_versions(installed: dict[str, str], python_version: tuple[int, int]) -> dict:
    if type(installed) is not dict or python_version != EXPECTED_PYTHON:
        raise EnvironmentDriftError("archived Python version drift")
    if not all(
        type(k) is str and type(v) is str and v
        for k, v in installed.items()
    ):
        raise EnvironmentDriftError("invalid distribution-version metadata")
    mismatches = [
        name for name, expected in ARCHIVED_PACKAGES.items()
        if installed.get(name) != expected
    ]
    if mismatches:
        raise EnvironmentDriftError(
            "offline regression dependency version mismatch: " + ", ".join(mismatches)
        )
    return {
        "offline_package_versions_match": True,
        "archived_ci_distributions_checked": len(ARCHIVED_PACKAGES),
        "python_minor_version_match": True,
        "archived_ci_run": 38382214223,
        "crosschecked_ci_run": 38484481047,
        "exact_wheel_hashes_verified": False,
        "os_native_dependency_identity_verified": False,
        "official_pit_admission_granted": False,
        "profitability_evaluated": False,
        "holdout_accessed": False,
        "ordering": False,
    }


def actual_environment_check() -> dict:
    names = ARCHIVED_PACKAGES.keys()
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "<MISSING>"
    return check_versions(versions, sys.version_info[:2])


def main() -> None:
    print("ARCHIVED_OFFLINE_ENVIRONMENT=" + json.dumps(
        actual_environment_check(), sort_keys=True
    ))


if __name__ == "__main__":
    main()
