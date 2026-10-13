"""Synthetic-only adversarial checks for archived-case parallel CI gate."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_v1_runtime_ci as ci
import research_v1_runtime_pinned_parallel as pp


class PinnedOnlyTest(unittest.TestCase):
    def setUp(self):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        self.dir = Path(root.name)
        self.rows = {suite: [["fixture.class", "test_" + suite, "passed"]]
                     for suite in ci.SUITES}
        total = sorted(row for group in self.rows.values() for row in group)
        expected = {suite: (len(rows), ci.case_digest(rows))
                    for suite, rows in self.rows.items()}
        expected["all"] = (len(total), ci.case_digest(total))
        frozen = patch.dict(ci.PINNED_CASES, expected, clear=True)
        frozen.start()
        self.addCleanup(frozen.stop)

    def reports(self):
        return {suite: {
            "suite": suite, "test_files": ci._expected_files(suite),
            "exit_code": 0, "duration_seconds": 0.1,
            "test_count": len(rows),
            "cases": copy.deepcopy(rows),
            "case_digest_sha256": ci.case_digest(rows),
            "profitability_evaluated": False,
            "source_admission_modified": False,
            "holdout_accessed": False,
            "ordering": False,
        } for suite, rows in self.rows.items()}

    def test_unchanged_case_identity_passes_without_serial(self):
        data = pp.validate_pinned_parallel(self.reports())
        self.assertEqual(data["pinned_cases"], 4)
        self.assertTrue(data["test_outcomes_match_archived_fixed_baseline"])

    def test_symmetric_missing_case_cannot_be_accepted(self):
        items = self.reports()
        del items["risk"]["cases"][0]
        items["risk"]["test_count"] = 0
        items["risk"]["case_digest_sha256"] = ci.case_digest([])
        with self.assertRaises(ValueError):
            pp.validate_pinned_parallel(items)

    def test_renamed_case_even_with_forged_local_digest_fails(self):
        items = self.reports()
        items["risk"]["cases"][0][1] = "test_changed"
        items["risk"]["case_digest_sha256"] = ci.case_digest(items["risk"]["cases"])
        with self.assertRaises(ValueError):
            pp.validate_pinned_parallel(items)

    def test_bad_permissions_or_failed_test_fails(self):
        for field, value in (("ordering", True), ("holdout_accessed", True),
                             ("source_admission_modified", True),
                             ("profitability_evaluated", True),
                             ("exit_code", 1)):
            items = self.reports()
            items["cost"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                pp.validate_pinned_parallel(items)
        items = self.reports()
        items["cost"]["cases"][0][2] = "failed"
        items["cost"]["case_digest_sha256"] = ci.case_digest(items["cost"]["cases"])
        with self.assertRaises(ValueError):
            pp.validate_pinned_parallel(items)

    def test_unexpected_or_missing_suite_fails(self):
        items = self.reports()
        items.pop("cost")
        with self.assertRaises(ValueError):
            pp.validate_pinned_parallel(items)
        items = self.reports()
        items["extra"] = copy.deepcopy(items["cost"])
        with self.assertRaises(ValueError):
            pp.validate_pinned_parallel(items)

    def test_duplicate_case_across_suites_fails(self):
        items = self.reports()
        items["risk"]["cases"][0] = list(items["cost"]["cases"][0])
        items["risk"]["case_digest_sha256"] = ci.case_digest(items["risk"]["cases"])
        with self.assertRaises(ValueError):
            pp.validate_pinned_parallel(items)

    def test_run_executes_only_four_suites_and_requires_archive_hash(self):
        example = self.reports()
        called = []

        def stub(suite, path):
            self.assertNotEqual(suite, "all")
            called.append(suite)
            path.write_text(json.dumps(example[suite]), encoding="utf-8")
            return {"suite": suite, "subprocess_wall_seconds": 0.01}

        with patch.object(pp, "invoke_suite", side_effect=stub):
            result = pp.run(self.dir)
        self.assertEqual(set(called), set(ci.SUITES))
        self.assertFalse(result["serial_control_executed"])
        self.assertTrue(result["test_outcomes_match_archived_fixed_baseline"])
        self.assertFalse(result["profitability_evaluated"])
        self.assertFalse(result["ordering"])

    def test_unapproved_runner_parallelism_fails_closed(self):
        for n in (0, 1, 3, 5, False):
            with self.subTest(count=n), self.assertRaises(ValueError):
                pp.run(self.dir, workers=n)


if __name__ == "__main__":
    unittest.main()
