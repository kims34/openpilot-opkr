"""No-network adversarial proof that runtime parity cannot silently lose cases.

These fixtures are synthetic pytest report metadata, NOT source data, labels,
performance, a fresh holdout, official source authorization or trading.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import research_v1_runtime_ci as ci


class ImmutableCaseParityTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.parts = {}
        expected = {}
        for suite in ci.SUITES:
            case = [[Path(ci.SUITES[suite][0]).stem, "test_synthetic_identity_" + suite, "passed"]]
            self.parts[suite] = self._report(suite, case)
            expected[suite] = (1, ci.case_digest(case))
        all_cases = sorted(case for p in self.parts.values() for case in p["cases"])
        self.baseline = self._report("all", all_cases)
        expected["all"] = (len(all_cases), ci.case_digest(all_cases))
        pinned_patch = patch.dict(ci.PINNED_CASES, expected, clear=True)
        pinned_patch.start()
        self.addCleanup(pinned_patch.stop)

    def _report(self, suite, cases):
        cases = sorted(cases)
        return {
            "suite": suite,
            "test_files": ci._expected_files(suite),
            "exit_code": 0,
            "duration_seconds": 1.0,
            "test_count": len(cases),
            "cases": cases,
            "case_digest_sha256": ci.case_digest(cases),
            "profitability_evaluated": False,
            "source_admission_modified": False,
            "holdout_accessed": False,
            "ordering": False,
        }

    def _check(self, expected_ok):
        serial = self.root / "baseline.json"
        serial.write_text(json.dumps(self.baseline), encoding="utf-8")
        for suite, obj in self.parts.items():
            (self.root / (suite + ".json")).write_text(json.dumps(obj), encoding="utf-8")
        result = self.root / "parity.json"
        if expected_ok:
            ci.compare(serial, self.root, result)
        else:
            with self.assertRaises(SystemExit):
                ci.compare(serial, self.root, result)
        self.assertIs(json.loads(result.read_text())["test_outcomes_identical"], expected_ok)

    def _rewrite_digests(self):
        for p in [self.baseline, *self.parts.values()]:
            p["cases"].sort()
            p["test_count"] = len(p["cases"])
            p["case_digest_sha256"] = ci.case_digest(p["cases"])

    def test_fixture_exact_case_set_and_outcomes_pass(self):
        self._check(True)

    def test_same_case_deleted_from_serial_and_parallel_fails(self):
        removed = self.parts["cache"]["cases"].pop()
        self.baseline["cases"].remove(removed)
        self._rewrite_digests()
        self._check(False)

    def test_same_case_renamed_on_both_sides_fails(self):
        self.parts["cost"]["cases"][0][1] = "test_changed_both_sides"
        for row in self.baseline["cases"]:
            if row[1] == "test_synthetic_identity_cost":
                row[1] = "test_changed_both_sides"
        self._rewrite_digests()
        self._check(False)

    def test_changed_suite_membership_fails(self):
        self.parts["risk"]["test_files"] = ci._expected_files("cost")
        self._check(False)

    def test_misreported_frozen_authority_fails(self):
        for key in ("ordering", "holdout_accessed", "source_admission_modified",
                    "profitability_evaluated"):
            with self.subTest(key=key):
                self.baseline[key] = True
                self._check(False)
                self.baseline[key] = False

    def test_bad_test_count_duration_and_digest_fail(self):
        original = copy.deepcopy(self.parts["gates"])
        for key, value in (("test_count", 2), ("duration_seconds", 0),
                           ("duration_seconds", float("nan")),
                           ("case_digest_sha256", "0" * 64)):
            with self.subTest(key=key, value=str(value)):
                self.parts["gates"] = copy.deepcopy(original)
                self.parts["gates"][key] = value
                self._check(False)

    def test_duplicate_identity_across_suites_fails(self):
        self.parts["risk"]["cases"] = copy.deepcopy(self.parts["cost"]["cases"])
        self._rewrite_digests()
        self._check(False)

    def test_run_suite_short_collection_fails_before_pass(self):
        junit = self.root / "collect.xml"
        junit.write_text("<testsuite/>", encoding="utf-8")
        class Finished:
            returncode = 0
            stdout = ""
            stderr = ""
        with patch.object(ci.subprocess, "run", return_value=Finished()), \
             patch.object(ci, "canonical_cases", return_value=[]), \
             self.assertRaises(SystemExit):
            ci.run_suite("cost", self.root / "collect.json")



class OneRunnerFailClosedTest(unittest.TestCase):
    """Offline-only mock subprocesses; no data, holdout or trade orders."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_failed_child_process_fails_closed(self):
        import research_v1_runtime_one_runner as runner
        class Finished:
            returncode = 1
            stdout = "offline fixture failed"
            stderr = ""
        with patch.object(runner.subprocess, "run", return_value=Finished()), \
             self.assertRaises(RuntimeError):
            runner._run("risk", self.root / "risk.json")

    def test_missing_case_report_fails_closed(self):
        import research_v1_runtime_one_runner as runner
        class Finished:
            returncode = 0
            stdout = ""
            stderr = ""
        with patch.object(runner.subprocess, "run", return_value=Finished()), \
             self.assertRaises(FileNotFoundError):
            runner._run("cost", self.root / "cost.json")

    def test_one_failed_parallel_child_rejects_combined_run(self):
        import research_v1_runtime_one_runner as runner
        def fake_child(suite, out):
            if suite == "risk":
                raise RuntimeError("synthetic risk worker failure")
        with patch.object(runner, "_run", side_effect=fake_child), \
             self.assertRaisesRegex(RuntimeError, "fail-closed parallel execution"):
            runner.benchmark(self.root)
        self.assertFalse((self.root / "one_runner_report.json").exists())

    def test_missing_parity_file_rejected(self):
        import research_v1_runtime_one_runner as runner
        with patch.object(runner, "_run", return_value=None), \
             patch.object(runner, "compare", return_value=None), \
             self.assertRaises(FileNotFoundError):
            runner.benchmark(self.root)
        self.assertFalse((self.root / "one_runner_report.json").exists())

    def test_synthetic_exact_parity_preserves_disabled_flags(self):
        import research_v1_runtime_one_runner as runner
        records = {}
        expected = {}
        for suite in ci.SUITES:
            cases = [[Path(ci.SUITES[suite][0]).stem, "test_synthetic_" + suite, "passed"]]
            records[suite] = cases
            expected[suite] = (1, ci.case_digest(cases))
        all_cases = sorted(case for cases in records.values() for case in cases)
        records["all"] = all_cases
        expected["all"] = (len(all_cases), ci.case_digest(all_cases))
        def fake_child(suite, out):
            cases = records[suite]
            payload = {
                "suite": suite, "test_files": ci._expected_files(suite),
                "exit_code": 0, "duration_seconds": 1.0,
                "test_count": len(cases), "cases": cases,
                "case_digest_sha256": ci.case_digest(cases),
                "profitability_evaluated": False,
                "source_admission_modified": False,
                "holdout_accessed": False, "ordering": False,
            }
            out.write_text(json.dumps(payload), encoding="utf-8")
        with patch.dict(ci.PINNED_CASES, expected, clear=True), \
             patch.object(runner, "_run", side_effect=fake_child):
            report = runner.benchmark(self.root)
        self.assertIs(report["test_outcomes_identical"], True)
        for key in ("economic_backtest_measured", "official_data_pit_admitted",
                    "full_workflow_wall_speedup_measured", "holdout_accessed", "ordering"):
            self.assertIs(report[key], False)

if __name__ == "__main__":
    unittest.main()
