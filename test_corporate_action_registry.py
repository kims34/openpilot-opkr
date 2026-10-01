import unittest
from datetime import datetime, timezone

from corporate_action_registry import active_noncomparable_event


def ts(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


class CorporateActionRegistryTests(unittest.TestCase):
    def test_ctva_spin_off_date_is_non_comparable_in_new_york(self):
        # 2026-10-01 13:00 UTC = 09:00 New York; distribution date.
        event = active_noncomparable_event("CTVA", ts("2026-10-01T13:00:00Z"))
        self.assertIsNotNone(event)
        self.assertEqual(event["kind"], "SPIN_OFF_DISTRIBUTION")
        self.assertEqual(event["basis_status"], "RAW_PREVIOUS_CLOSE_NONCOMPARABLE")
        self.assertGreaterEqual(len(event["sources"]), 2)

    def test_ctva_day_before_is_not_suppressed(self):
        self.assertIsNone(active_noncomparable_event("CTVA", ts("2026-09-30T13:00:00Z")))

    def test_ctva_day_after_is_not_suppressed_by_static_event(self):
        self.assertIsNone(active_noncomparable_event("CTVA", ts("2026-10-02T13:00:00Z")))

    def test_unrelated_symbol_is_not_suppressed(self):
        self.assertIsNone(active_noncomparable_event("AAPL", ts("2026-10-01T13:00:00Z")))

    def test_timezone_boundary_uses_new_york_date(self):
        # 02:00 UTC on Oct 2 is still 22:00 New York on Oct 1.
        self.assertIsNotNone(active_noncomparable_event("ctva", ts("2026-10-02T02:00:00Z")))


if __name__ == "__main__":
    unittest.main()
