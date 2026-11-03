"""Synthetic-only security tests; not a PIT admission or profitability run."""
import copy
import tempfile
import unittest
from pathlib import Path

from research_v1_runtime_manifest import (
    REQUIRED_GATES, UnverifiedSourceError, cache_manifest, cache_matches,
)


class RuntimeManifestTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source = root / "raw.bin"
        self.code = root / "code.py"
        self.source.write_bytes(b"synthetic-fixture-source")
        self.code.write_text("print('fixture')", encoding="utf-8")
        self.inputs = {"source_files": {"source": self.source},
                       "code_files": {"code": self.code},
                       "receipt": {
                           "admission_status": "PIT_ADMITTED",
                           "source_evidence_sha256": "a" * 64,
                           "coverage_evidence_sha256": "b" * 64,
                           "admission_code_sha256": "c" * 64,
                           "holdout_access_authorized": False,
                           "live_orders_authorized": False,
                           **{key: True for key in REQUIRED_GATES},
                       },
                       "frozen_policy": {"fixture": "H5_M20_UNCHANGED"},
                       "runtime_lock": {"python": "3.12", "dependencies": "synthetic"}}

    def test_deterministic_reuse_for_exact_same_bytes(self):
        a = cache_manifest(**self.inputs)
        b = cache_manifest(**self.inputs)
        self.assertEqual(a, b)
        self.assertTrue(cache_matches(a, **self.inputs))
        self.assertFalse(a["evaluation_authorized"])
        self.assertFalse(a["holdout_authorized"])
        self.assertFalse(a["live_orders_authorized"])

    def test_source_tampering_invalidates(self):
        old = cache_manifest(**self.inputs)
        self.source.write_bytes(b"modified")
        self.assertFalse(cache_matches(old, **self.inputs))

    def test_code_policy_and_runtime_changes_invalidate(self):
        original = cache_manifest(**self.inputs)
        for field, patch in (
            ("frozen_policy", {"fixture": "CHANGED"}),
            ("runtime_lock", {"python": "3.13"}),
            ("receipt", {"coverage_evidence_sha256": "d" * 64}),
        ):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.inputs)
                candidate[field].update(patch)
                self.assertFalse(cache_matches(original, **candidate))
        self.code.write_text("print('changed')", encoding="utf-8")
        self.assertFalse(cache_matches(original, **self.inputs))

    def test_every_gate_fails_closed(self):
        for gate in REQUIRED_GATES:
            with self.subTest(gate=gate):
                candidate = copy.deepcopy(self.inputs)
                candidate["receipt"][gate] = False
                with self.assertRaises(UnverifiedSourceError):
                    cache_manifest(**candidate)
        missing = copy.deepcopy(self.inputs)
        missing["receipt"]["admission_status"] = "NOT_EVALUABLE"
        with self.assertRaises(UnverifiedSourceError):
            cache_manifest(**missing)

    def test_bogus_hash_missing_file_or_authorization_rejected(self):
        for key, val in (
            ("source_evidence_sha256", "not-a-sha"),
            ("holdout_access_authorized", True),
            ("live_orders_authorized", True),
        ):
            candidate = copy.deepcopy(self.inputs)
            candidate["receipt"][key] = val
            with self.subTest(key=key), self.assertRaises(UnverifiedSourceError):
                cache_manifest(**candidate)
        candidate = copy.deepcopy(self.inputs)
        candidate["source_files"] = {"missing": Path(self.temp.name) / "missing"}
        with self.assertRaises(UnverifiedSourceError):
            cache_manifest(**candidate)


if __name__ == "__main__":
    unittest.main()
