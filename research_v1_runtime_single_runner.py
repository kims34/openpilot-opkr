"""Measure single-runner serial vs subprocess-parallel OFFLINE regression work.

This is engineering-only. It invokes the pre-existing pinned regression suites,
never data acquisition, model fitting, performance backtests, holdout or orders.
All results must match the immutable 34-case identities and suite SHA-256 hashes
already enforced by research_v1_runtime_ci.compare.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
import time

from research_v1_runtime_ci import SUITES, compare


def invoke_suite(suite: str, path: Path) -> dict:
    """Each suite runs in its own process; JUnit/JSON paths never overlap."""
    start = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, "research_v1_runtime_ci.py", "--suite", suite,
         "--out", str(path)],
        capture_output=True, text=True, timeout=300, check=False,
    )
    elapsed = time.perf_counter() - start
    if completed.returncode:
        raise RuntimeError(
            "Pinned offline regression failed: " + suite + "\n"
            + completed.stdout[-2200:] + "\n" + completed.stderr[-1200:]
        )
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("suite") != suite or result.get("exit_code") != 0:
        raise RuntimeError("Invalid suite output: " + suite)
    return {"suite": suite, "subprocess_wall_seconds": round(elapsed, 4)}


def run(out_dir: Path, *, workers: int = 4) -> dict:
    if type(workers) is not int or not 1 <= workers <= len(SUITES):
        raise ValueError("Only 1..4 offline test processes are supported")
    out_dir.mkdir(parents=True, exist_ok=True)
    validation_started = time.perf_counter()

    # Same GitHub runner + venv + filesystem: compare test process time, not
    # separate runner environment preparation or hypothetical market speed.
    serial = invoke_suite("all", out_dir / "baseline.json")
    parallel_started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        submitted = {
            pool.submit(invoke_suite, suite, out_dir / (suite + ".json")): suite
            for suite in SUITES
        }
        parallel_results = {
            submitted[future]: future.result() for future in as_completed(submitted)
        }
    parallel_wall = time.perf_counter() - parallel_started

    # Existing compare rejects symmetric omissions, wrong suite membership,
    # mismatched outcome status, bad digests, and all authority flag changes.
    compare(out_dir / "baseline.json", out_dir, out_dir / "parity.json")
    parity = json.loads((out_dir / "parity.json").read_text(encoding="utf-8"))
    if parity.get("test_outcomes_identical") is not True or set(parallel_results) != set(SUITES):
        raise RuntimeError("Fail-closed pinned testcase parity did not pass")

    full_wall = time.perf_counter() - validation_started
    serial_wall = serial["subprocess_wall_seconds"]
    report = {
        "schema": "indexalert-one-runner-offline-regression-v1",
        "runner_model": "one ubuntu-latest job: serial then 4 isolated test processes",
        "workers": workers,
        "serial_test_subprocess_wall_seconds": serial_wall,
        "parallel_test_group_wall_seconds": round(parallel_wall, 4),
        "one_runner_both_modes_validation_wall_seconds": round(full_wall, 4),
        "test_subprocess_speed_ratio": round(serial_wall / parallel_wall, 4)
            if parallel_wall > 0 else None,
        "test_outcomes_identical": True,
        "pinned_cases": parity["cases"],
        "pinned_case_digest_sha256": parity["case_digest_sha256"],
        "ci_end_to_end_speedup_measured": False,
        "actual_profitability_backtest_speedup_measured": False,
        "source_admission_modified": False,
        "profitability_evaluated": False,
        "holdout_accessed": False,
        "ordering": False,
    }
    (out_dir / "one_runner_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ONE_RUNNER_OFFLINE=" + json.dumps(report, sort_keys=True), flush=True)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline-only single-runner probe")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.out_dir)


if __name__ == "__main__":
    main()
