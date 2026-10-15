"""Synthetic package/version drift negative controls: no network or data."""
import unittest
from unittest.mock import patch

import research_v1_runtime_archived_env_gate as gate


class ArchivedRuntimeVersionsTest(unittest.TestCase):
    def setUp(self):
        self.same = dict(gate.ARCHIVED_PACKAGES)

    def test_identical_archived_environment_passes_for_offline_only(self):
        status = gate.check_versions(self.same, (3, 12))
        self.assertEqual(status["archived_ci_distributions_checked"], 22)
        self.assertTrue(status["offline_package_versions_match"])
        self.assertFalse(status["exact_wheel_hashes_verified"])
        self.assertFalse(status["official_pit_admission_granted"])
        self.assertFalse(status["ordering"])

    def test_single_changed_transitive_dependency_fails(self):
        self.same["urllib3"] = "999.0"
        with self.assertRaises(gate.EnvironmentDriftError):
            gate.check_versions(self.same, (3, 12))

    def test_missing_indirect_dependency_fails(self):
        self.same.pop("joblib")
        with self.assertRaises(gate.EnvironmentDriftError):
            gate.check_versions(self.same, (3, 12))

    def test_wrong_python_minor_version_fails(self):
        with self.assertRaises(gate.EnvironmentDriftError):
            gate.check_versions(self.same, (3, 13))

    def test_ill_typed_version_metadata_fails(self):
        self.same["pytest"] = None
        with self.assertRaises(gate.EnvironmentDriftError):
            gate.check_versions(self.same, (3, 12))

    def test_real_checker_can_be_driven_without_network(self):
        def installed(name):
            return self.same[name]
        with patch.object(gate.metadata, "version", side_effect=installed), \
             patch.object(gate.sys, "version_info", (3, 12, 11)):
            status = gate.actual_environment_check()
        self.assertTrue(status["python_minor_version_match"])

    def test_synthetic_missing_package_in_real_checker_fails(self):
        def installed(name):
            if name == "scipy":
                raise gate.metadata.PackageNotFoundError(name)
            return self.same[name]
        with patch.object(gate.metadata, "version", side_effect=installed), \
             patch.object(gate.sys, "version_info", (3, 12, 11)), \
             self.assertRaises(gate.EnvironmentDriftError):
            gate.actual_environment_check()


if __name__ == "__main__":
    unittest.main()
