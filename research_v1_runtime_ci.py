"""Offline-only timing and parity of existing deterministic regression tests.

This harness does NOT run a market-data build, model, backtest or holdout.
It compares identical test case outcomes across serial and parallel layouts.
"""
from __future__ import annotations

import argparse
import hashlib
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
    files = [x for s in (SUITES if suite == "all" else (suite,)) for x in SUITES[s]]
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
    if completed.returncode or not cases or any(x[2] != "passed" for x in cases):
        raise SystemExit("Offline regression suite failed (or collected no tests)")


def compare(serial: Path, parallel_dir: Path, out: Path) -> None:
    base = json.loads(serial.read_text(encoding="utf-8"))
    pieces = [json.loads((parallel_dir / (s + ".json")).read_text(encoding="utf-8"))
              for s in SUITES]
    def acceptable(x):
        return (x.get("exit_code") == 0 and x.get("test_count", 0) > 0
                and all(case[2] == "passed" for case in x.get("cases", []))
                and x.get("profitability_evaluated") is False
                and x.get("source_admission_modified") is False
                and x.get("holdout_accessed") is False
                and x.get("ordering") is False
                and x.get("case_digest_sha256") == case_digest(x.get("cases", [])))
    merged = sorted(case for p in pieces for case in p["cases"])
    parity = (acceptable(base) and all(acceptable(p) for p in pieces)
              and len(merged) == len(set(tuple(c) for c in merged))
              and merged == base["cases"]
              and case_digest(merged) == base["case_digest_sha256"])
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
