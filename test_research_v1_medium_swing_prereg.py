import copy
import unittest

from research_v1_medium_swing_prereg import load_protocol, validate_protocol


class MediumSwingPreregIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = load_protocol()

    def test_prereg_is_valid_but_data_gated(self):
        out = validate_protocol(self.p)
        self.assertTrue(out["valid"], out["blockers"])
        self.assertFalse(out["performance_run_authorized"])
        self.assertFalse(out["holdout_authorized"])
        self.assertFalse(out["champion_change_allowed"])
        self.assertFalse(out["tiny_live_path_change_allowed"])
        self.assertFalse(out["live_order_authorized"])

    def test_horizon_cannot_be_swept_or_changed(self):
        for value in (5, 7, 10, 15):
            p = copy.deepcopy(self.p)
            p["primary_horizon_sessions"] = value
            self.assertFalse(validate_protocol(p)["valid"])
        p = copy.deepcopy(self.p)
        p["horizon_sweep_forbidden"] = False
        self.assertFalse(validate_protocol(p)["valid"])

    def test_h10_cannot_be_rescued(self):
        p = copy.deepcopy(self.p)
        p["rejected_h10_retune_forbidden"] = False
        self.assertFalse(validate_protocol(p)["valid"])

    def test_holdout_core_tiny_live_and_orders_stay_separate(self):
        for key, value in (
            ("consumed_project_v1_holdout_forbidden", False),
            ("tiny_live_path_must_not_be_delayed", False),
            ("champion_core_change_allowed", True),
            ("operating_code_change_allowed", True),
            ("live_order_authorized", True),
        ):
            with self.subTest(key=key):
                p = copy.deepcopy(self.p)
                p[key] = value
                self.assertFalse(validate_protocol(p)["valid"])

    def test_model_and_source_gates_cannot_silently_change(self):
        p = copy.deepcopy(self.p)
        p["model"]["top_k"] = 5
        self.assertFalse(validate_protocol(p)["valid"])

        p = copy.deepcopy(self.p)
        p["required_new_pit_evidence"] = p["required_new_pit_evidence"][:-1]
        self.assertFalse(validate_protocol(p)["valid"])


if __name__ == "__main__":
    unittest.main()
