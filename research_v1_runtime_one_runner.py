"""One-runner, one-dependency-install offline regression benchmark.

Measure exact same fixed 34 synthetic/offline testcase identities once serially
and once as four independent child processes on a SINGLE CI runner.
This script never loads market data, fits models, reads holdout or places orders.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from research_v1_runtime_ci import PINNED_CASES, SUITES, _acceptable, compare


def _run(suite: str, out: Path) -> None:
    # Separate child process and JUnit path for every suite. Never force a
    # failed test to success or derive a new pinned baseline from this run.
    command = [
        sys.executable, str(Path(__file__).with_name("research_v1_runtime_ci.py")),
        "--suite", suite, "--out", str(out),
    ]
    proc = subprocess.run(command, capture_output=True, text=True,
                          check=False, timeout=240)
    print("SINGLE_RUNNER_SUITE=" + suite + " EXIT=" + str(proc.returncode))
    if proc.returncode:
        raise RuntimeError(
            "Pinned offline suite " + suite + " failed:\n"
            + proc.stdout[-2400:] + "\n" + proc.stderr[-1200:]
        )
    report = json.loads(out.read_text(encoding="utf-8"))
    if not _acceptable(report, suite):
        raise RuntimeError("suite did not meet immutable testcase contract: " + suite)


def benchmark(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    serial_file = out_dir / "baseline.json"
    start = time.perf_counter()
    _run("all", serial_file)
    serial_wall = time.perf_counter() - start

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=len(SUITES)) as executor:
        futures = {
            suite: executor.submit(_run, suite, out_dir / (suite + ".json"))
            for suite in SUITES
        }
        # Await every worker, including failures, before any acceptance.
        failures = []
        for suite, future in futures.items():
            try:
                future.result()
            except Exception as exc:
                failures.append(suite + ": " + str(exc))
    parallel_wall = time.perf_counter() - start
    if failures:
        raise RuntimeError("fail-closed parallel execution: " + "; ".join(failures))

    parity_path = out_dir / "parity.json"
    compare(serial_file, out_dir, parity_path)
    parity = json.loads(parity_path.read_text(encoding="utf-8"))
    if (parity.get("test_outcomes_identical") is not True
            or parity.get("cases") != PINNED_CASES["all"][0]
            or parity.get("case_digest_sha256") != PINNED_CASES["all"][1]):
        raise RuntimeError("single-runner returned noncanonical testcase parity")
    if not all(math.isfinite(v) and v > 0 for v in (serial_wall, parallel_wall)):
        raise RuntimeError("invalid duration")

    report = {
        "schema": "indexalert-offline-one-runner-benchmark-v1",
        "single_runner_serial_wall_seconds": round(serial_wall, 4),
        "single_runner_parallel_wall_seconds": round(parallel_wall, 4),
        "one_runner_test_phase_speed_ratio": round(serial_wall / parallel_wall, 4),
        "test_case_count": PINNED_CASES["all"][0],
        "test_case_digest_sha256": PINNED_CASES["all"][1],
        "test_outcomes_identical": True,
        "one_runner_dependency_install_count": 1,
        "ci_job_overhead_not_included_in_phase_ratio": True,
        "full_workflow_wall_speedup_measured": False,
        "official_data_pit_admitted": False,
        "economic_backtest_measured": False,
        "holdout_accessed": False,
        "ordering": False,
    }
    (out_dir / "one_runner_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("RUNTIME_OPT_ONE_RUNNER=" + json.dumps(report, sort_keys=True))
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()
    benchmark(args.out_dir)


if __name__ == "__main__":
    main()
