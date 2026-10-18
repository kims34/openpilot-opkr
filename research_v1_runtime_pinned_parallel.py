"""Offline-only pinned regression parallel runner (no duplicate serial phase).

Archival 34-case expected outcomes and per-suite SHA-256 are fixed in
research_v1_runtime_ci.PINNED_CASES. This only reduces redundant CI execution:
it is NOT a research PIT source validator or a strategy performance engine.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import time

import research_v1_runtime_ci as ci
from research_v1_runtime_single_runner import invoke_suite


def validate_pinned_parallel(reports: dict[str, dict]) -> dict:
    """Reject any suite omission, extra suite, symmetric case loss, or drift."""
    if type(reports) is not dict or set(reports) != set(ci.SUITES):
        raise ValueError("missing or unexpected pinned test suite")
    merged = []
    for suite in ci.SUITES:
        report = reports[suite]
        if not ci._acceptable(report, suite):
            raise ValueError("pinned testcase integrity failed: " + suite)
        merged.extend(report["cases"])
    merged.sort()
    identities = [(case[0], case[1]) for case in merged]
    expected_count, expected_hash = ci.PINNED_CASES["all"]
    if (len(merged) != expected_count
            or len(set(identities)) != expected_count
            or ci.case_digest(merged) != expected_hash):
        raise ValueError("fixed 34-case union digest or identity mismatch")
    return {"pinned_cases": expected_count,
            "pinned_case_digest_sha256": expected_hash,
            "test_outcomes_match_archived_fixed_baseline": True}


def run(out_dir: Path, *, workers: int = 4) -> dict:
    if type(workers) is not int or workers != len(ci.SUITES):
        raise ValueError("only fixed 4-worker offline suite layout approved")
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {
            pool.submit(invoke_suite, suite, out_dir / (suite + ".json")): suite
            for suite in ci.SUITES
        }
        completed = {pending[f]: f.result() for f in as_completed(pending)}
    parallel_seconds = time.perf_counter() - started
    if set(completed) != set(ci.SUITES):
        raise RuntimeError("not all pinned suites completed")
    evidence = {}
    for suite in ci.SUITES:
        evidence[suite] = json.loads((out_dir / (suite + ".json")).read_text(encoding="utf-8"))
    pinned = validate_pinned_parallel(evidence)
    report = {
        "schema": "indexalert-parallel-only-pinned-offline-v1",
        **pinned,
        "runner_layout": "four parallel subprocess suites; archived SHA256 baseline gate",
        "runner_regression_wall_seconds": round(time.perf_counter() - started, 4),
        "parallel_group_wall_seconds": round(parallel_seconds, 4),
        "serial_control_executed": False,
        "actual_backtest_speedup_measured": False,
        "ci_end_to_end_speedup_measured": False,
        "source_admission_modified": False,
        "holdout_accessed": False,
        "profitability_evaluated": False,
        "ordering": False,
    }
    (out_dir / "pinned_only_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PINNED_PARALLEL_ONLY=" + json.dumps(report, sort_keys=True), flush=True)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Strict offline archived-case CI gate")
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    run(args.out_dir)


if __name__ == "__main__":
    main()
