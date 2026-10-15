"""Offline synthetic-only checks for single-runner regression harness."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_v1_runtime_ci as ci
import research_v1_runtime_single_runner as one


class SingleRunnerHarnessTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.examples = {
            suite: [["offline.synthetic", "test_" + suite, "passed"]]
            for suite in ci.SUITES
        }
        self.pinned = {
            suite: (len(cases), ci.case_digest(cases))
            for suite, cases in self.examples.items()
        }
        all_cases = sorted(case for cases in self.examples.values() for case in cases)
        self.pinned["all"] = (len(all_cases), ci.case_digest(all_cases))
        p = patch.dict(ci.PINNED_CASES, self.pinned, clear=True)
        p.start()
        self.addCleanup(p.stop)

    def fake_invocation(self, altered=None, status=None):
        def invoke(suite, path):
            rows = (
                sorted(case for group in self.examples.values() for case in group)
                if suite == "all" else [row[:] for row in self.examples[suite]]
            )
            if suite == altered:
                rows[0][1] = "test_unexpected"
            if suite == status:
                rows[0][2] = "failure"
            rows = sorted(rows)
            record = {
                "suite": suite, "test_files": ci._expected_files(suite),
                "exit_code": 0, "duration_seconds": 0.02,
                "test_count": len(rows), "cases": rows,
                "case_digest_sha256": ci.case_digest(rows),
                "profitability_evaluated": False,
                "source_admission_modified": False,
                "holdout_accessed": False, "ordering": False,
            }
            path.write_text(json.dumps(record), encoding="utf-8")
            return {"suite": suite, "subprocess_wall_seconds": 0.02}
        return invoke

    def test_synthetic_identical_results_pass(self):
        with patch.object(one, "invoke_suite", side_effect=self.fake_invocation()):
            result = one.run(self.root, workers=2)
        self.assertTrue(result["test_outcomes_identical"])
        self.assertEqual(result["pinned_cases"], 4)
        self.assertFalse(result["profitability_evaluated"])
        self.assertFalse(result["ordering"])

    def test_synthetic_parallel_case_rename_fails(self):
        with patch.object(one, "invoke_suite", side_effect=self.fake_invocation(altered="risk")):
            with self.assertRaises(SystemExit):
                one.run(self.root)
        parity = json.loads((self.root / "parity.json").read_text())
        self.assertFalse(parity["test_outcomes_identical"])

    def test_synthetic_test_failure_fails(self):
        with patch.object(one, "invoke_suite", side_effect=self.fake_invocation(status="cache")):
            with self.assertRaises(SystemExit):
                one.run(self.root)

    def test_invalid_workers_fail(self):
        for value in (0, -1, 5, True, 2.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                one.run(self.root, workers=value)


if __name__ == "__main__":
    unittest.main()
