"""Offline-only timing and parity of existing deterministic regression tests.

This harness does NOT run a market-data build, model, backtest or holdout.
It compares identical test case outcomes across serial and parallel layouts.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

SUITES = {
    "cost": ("test_research_v1_pit_tax.py", "test_research_v1_core.py"),
    "risk": ("test_research_v1_portfolio.py", "test_research_v1_distributional_netev.py"),
    "gates": ("test_research_v1_medium_swing_prereg.py", "test_research_v1_purged.py"),
    "cache": ("test_research_v1_supervised_cache.py", "test_research_v1_runtime_manifest.py"),
}


# Exact test identity and result hashes from independent, archived 2026-10-13
# successful executions 38381997417 and 38382214223 (34 cases).
# Do not regenerate these from a newly shortened test run: an accidental
# identical omission from both serial and parallel would otherwise pass.
PINNED_CASES = {
    "cost": (9, "0a11d4eca07ce83f32758d8fe8aa62ab5e5450bd9e9bd6413bdb9691e13213c9"),
    "risk": (9, "49185a1d6fcf193c710959d8b07e274114c884158f2d7ffac226bc9df9bd47e6"),
    "gates": (8, "717cd517fb407727db2dee99e1fdcdc39d9033f70dabbb68609dcd4a1ee6cd33"),
    "cache": (8, "2353b8399ba17dc1ec22334bf7be99609ceef05c4342fd3c1e99134a637f59a5"),
    "all": (34, "5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34"),
}


def _expected_files(suite: str) -> list[str]:
    return [name for sub in (SUITES if suite == "all" else (suite,))
            for name in SUITES[sub]]


def _acceptable(report: object, suite: str) -> bool:
    """Reject fabricated/missing/relabelled cases even if all runners agree."""
    if type(report) is not dict or report.get("suite") != suite:
        return False
    cases = report.get("cases")
    if type(cases) is not list or any(
        type(row) is not list or len(row) != 3
        or any(type(v) is not str or not v for v in row)
        for row in cases
    ):
        return False
    pinned_count, pinned_digest = PINNED_CASES[suite]
    if (len(cases) != pinned_count or cases != sorted(cases)
            or len({(row[0], row[1]) for row in cases}) != len(cases)):
        return False
    duration = report.get("duration_seconds")
    if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
        return False
    return (
        type(report.get("exit_code")) is int and report["exit_code"] == 0
        and type(report.get("test_count")) is int and report["test_count"] == pinned_count
        and report.get("test_files") == _expected_files(suite)
        and all(row[2] == "passed" for row in cases)
        and report.get("case_digest_sha256") == pinned_digest
        and case_digest(cases) == pinned_digest
        and report.get("profitability_evaluated") is False
        and report.get("source_admission_modified") is False
        and report.get("holdout_accessed") is False
        and report.get("ordering") is False
    )


def canonical_cases(junit_file: Path) -> list[list[str]]:
    root = ET.parse(junit_file).getroot()
    cases = []
    for test in root.iter("testcase"):
        state = next((k for k in ("failure", "error", "skipped") if test.find(k) is not None), "passed")
        cases.append([test.attrib.get("classname", ""), test.attrib["name"], state])
    return sorted(cases)


def case_digest(cases: list[list[str]]) -> str:
    body = json.dumps(cases, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(body).hexdigest()


def run_suite(suite: str, out: Path) -> None:
    files = _expected_files(suite)
    out.parent.mkdir(parents=True, exist_ok=True)
    junit = out.with_suffix(".xml")
    cmd = [sys.executable, "-m", "pytest", "-q", "--disable-warnings",
           "--junitxml", str(junit), *files]
    start = time.perf_counter()
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    elapsed = time.perf_counter() - start
    cases = canonical_cases(junit) if junit.exists() else []
    result = {
        "suite": suite, "test_files": files, "exit_code": completed.returncode,
        "duration_seconds": round(elapsed, 4), "test_count": len(cases),
        "cases": cases, "case_digest_sha256": case_digest(cases),
        "profitability_evaluated": False, "source_admission_modified": False,
        "holdout_accessed": False, "ordering": False,
    }
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(completed.stdout[-7000:])
    if completed.stderr:
        print(completed.stderr[-1500:], file=sys.stderr)
    print("RUNTIME_OPT_RUN=" + json.dumps({k: v for k, v in result.items() if k != "cases"}))
    if not _acceptable(result, suite):
        raise SystemExit("Offline regression suite failed pinned-case identity / outcome gate")


def compare(serial: Path, parallel_dir: Path, out: Path) -> None:
    base = json.loads(serial.read_text(encoding="utf-8"))
    pieces = [json.loads((parallel_dir / (s + ".json")).read_text(encoding="utf-8"))
              for s in SUITES]
    merged = sorted(case for p in pieces for case in p["cases"])
    parity = (
        _acceptable(base, "all")
        and all(_acceptable(p, suite) for suite, p in zip(SUITES, pieces))
        and len(merged) == len(set(tuple(c) for c in merged))
        and merged == base["cases"]
        and case_digest(merged) == PINNED_CASES["all"][1]
    )
    serial_seconds = base["duration_seconds"]
    max_parallel_seconds = max(p["duration_seconds"] for p in pieces)
    report = {
        "test_outcomes_identical": bool(parity),
        "serial_regression_seconds": serial_seconds,
        "parallel_longest_suite_seconds": max_parallel_seconds,
        "test_phase_speedup_only": round(serial_seconds / max_parallel_seconds, 3)
            if max_parallel_seconds > 0 else None,
        "ci_end_to_end_speedup_measured": False,
        "actual_backtest_speedup_measured": False,
        "case_digest_sha256": base["case_digest_sha256"],
        "cases": len(base["cases"]),
        "admissible_profitability_generated": False,
        "ordering": False,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("RUNTIME_OPT_PARITY=" + json.dumps(report, sort_keys=True))
    if not parity:
        raise SystemExit("Serial / parallel test outcomes differed; optimization rejected")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", choices=["all", *SUITES])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--serial", type=Path)
    ap.add_argument("--parallel-dir", type=Path)
    args = ap.parse_args()
    if args.suite and not args.serial and not args.parallel_dir:
        run_suite(args.suite, args.out)
    elif not args.suite and args.serial and args.parallel_dir:
        compare(args.serial, args.parallel_dir, args.out)
    else:
        ap.error("Choose either --suite OR --serial and --parallel-dir")


if __name__ == "__main__":
    main()
