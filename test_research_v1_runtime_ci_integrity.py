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


class CacheManifestNoFollowTest(unittest.TestCase):
    """Synthetic-only local filesystem race controls (not PIT authorization)."""

    def setUp(self):
        from research_v1_runtime_manifest import REQUIRED_GATES
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.source = self.root / "original.bin"
        self.code = self.root / "frozen.py"
        self.source.write_bytes(b"synthetic original")
        self.code.write_bytes(b"synthetic code")
        self.args = {
            "source_files": {"data": self.source},
            "code_files": {"code": self.code},
            "receipt": {
                "admission_status": "PIT_ADMITTED",
                "source_evidence_sha256": "a" * 64,
                "coverage_evidence_sha256": "b" * 64,
                "admission_code_sha256": "c" * 64,
                "holdout_access_authorized": False,
                "live_orders_authorized": False,
                **{k: True for k in REQUIRED_GATES},
            },
            "frozen_policy": {"synthetic_fixture": "unchanged"},
            "runtime_lock": {"python": "synthetic 3.12"},
        }

    def test_exact_synthetic_input_still_matches(self):
        import research_v1_runtime_manifest as m
        receipt = m.cache_manifest(**self.args)
        self.assertTrue(m.cache_matches(receipt, **self.args))
        self.assertFalse(receipt["evaluation_authorized"])
        self.assertFalse(receipt["holdout_authorized"])
        self.assertFalse(receipt["live_orders_authorized"])

    def test_source_leaf_swapped_to_symlink_at_open_rejected(self):
        import research_v1_runtime_manifest as m
        original_open = m.os.open
        swapped = [False]
        def swap_at_open(path, flags, *a, **kw):
            if path == "original.bin" and not swapped[0]:
                swapped[0] = True
                self.source.rename(self.root / "retired.bin")
                self.source.symlink_to(self.root / "retired.bin")
            return original_open(path, flags, *a, **kw)
        with patch.object(m.os, "open", side_effect=swap_at_open), \
             self.assertRaises(m.UnverifiedSourceError):
            m.cache_manifest(**self.args)
        self.assertTrue(swapped[0])

    def test_intermediate_directory_symlink_rejected(self):
        import research_v1_runtime_manifest as m
        directory = self.root / "source_dir"
        directory.mkdir()
        (directory / "data.bin").write_bytes(b"synthetic")
        (self.root / "shortcut").symlink_to(directory, target_is_directory=True)
        args = dict(self.args)
        args["source_files"] = {"source": self.root / "shortcut" / "data.bin"}
        with self.assertRaises(m.UnverifiedSourceError):
            m.cache_manifest(**args)

    def test_source_mutation_during_later_code_read_rejected(self):
        import research_v1_runtime_manifest as m
        original_open = m.os.open
        changed = [False]
        def mutate_previous(path, flags, *a, **kw):
            if path == "frozen.py" and not changed[0]:
                changed[0] = True
                self.source.write_bytes(b"altered during code read")
            return original_open(path, flags, *a, **kw)
        with patch.object(m.os, "open", side_effect=mutate_previous), \
             self.assertRaises(m.UnverifiedSourceError):
            m.cache_manifest(**self.args)
        self.assertTrue(changed[0])

    def test_same_byte_inode_replacement_during_later_read_rejected(self):
        import research_v1_runtime_manifest as m
        original_open = m.os.open
        moved = [False]
        def replace_previous(path, flags, *a, **kw):
            if path == "frozen.py" and not moved[0]:
                moved[0] = True
                raw = self.source.read_bytes()
                self.source.rename(self.root / "retired_original.bin")
                self.source.write_bytes(raw)
            return original_open(path, flags, *a, **kw)
        with patch.object(m.os, "open", side_effect=replace_previous), \
             self.assertRaises(m.UnverifiedSourceError):
            m.cache_manifest(**self.args)
        self.assertTrue(moved[0])

    def test_fifo_cache_input_rejected_nonblocking(self):
        import os
        import research_v1_runtime_manifest as m
        fifo = self.root / "pipe"
        os.mkfifo(fifo)
        args = dict(self.args)
        args["source_files"] = {"fifo": fifo}
        with self.assertRaises(m.UnverifiedSourceError):
            m.cache_manifest(**args)


    def test_cache_receipt_permission_flags_must_be_literal_false(self):
        import research_v1_runtime_manifest as m
        for key in ("holdout_access_authorized", "live_orders_authorized"):
            for bad in (True, 1, "true", "false", None, [], {}):
                with self.subTest(key=key, bad=repr(bad)):
                    inputs = copy.deepcopy(self.args)
                    inputs["receipt"][key] = bad
                    with self.assertRaises(m.UnverifiedSourceError):
                        m.cache_manifest(**inputs)
            with self.subTest(key=key, bad="missing"):
                inputs = copy.deepcopy(self.args)
                del inputs["receipt"][key]
                with self.assertRaises(m.UnverifiedSourceError):
                    m.cache_manifest(**inputs)

    def test_ambiguous_receipt_cannot_match_cached_manifest(self):
        import research_v1_runtime_manifest as m
        stored = m.cache_manifest(**self.args)
        for key in ("holdout_access_authorized", "live_orders_authorized"):
            inputs = copy.deepcopy(self.args)
            inputs["receipt"][key] = "false"
            with self.subTest(key=key):
                self.assertFalse(m.cache_matches(stored, **inputs))


    def test_alias_elevated_receipt_permissions_rejected(self):
        """A contradictory real-order/holdout/funds flag cannot slip through
        because its name differs from the local receipt guard."""
        import research_v1_runtime_manifest as m
        clean = m.cache_manifest(**self.args)
        self.assertFalse(clean["live_orders_authorized"])
        for flag in m.FORBIDDEN_ELEVATED_RECEIPT_FLAGS:
            for value in (True, 1, "true", "false", None, [], {}):
                with self.subTest(flag=flag, value=repr(value)):
                    inputs = copy.deepcopy(self.args)
                    inputs["receipt"][flag] = value
                    with self.assertRaises(m.UnverifiedSourceError):
                        m.cache_manifest(**inputs)
                    self.assertFalse(m.cache_matches(clean, **inputs))

    def test_explicit_false_receipt_alias_does_not_grant_authority(self):
        import research_v1_runtime_manifest as m
        inputs = copy.deepcopy(self.args)
        for flag in m.FORBIDDEN_ELEVATED_RECEIPT_FLAGS:
            inputs["receipt"][flag] = False
        record = m.cache_manifest(**inputs)
        for key in ("evaluation_authorized", "holdout_authorized", "live_orders_authorized"):
            self.assertIs(record[key], False)
        self.assertTrue(m.cache_matches(record, **inputs))
        # Absence is allowed: these source-specific aliases are optional,
        # unlike local holdout and order rights which require explicit false.

if __name__ == "__main__":
    unittest.main()
