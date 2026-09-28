import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from market_basis import regular_close_basis


ET = ZoneInfo("America/New_York")


def ts(day, hour=15, minute=55):
    return int(datetime.fromisoformat(f"{day}T{hour:02d}:{minute:02d}:00").replace(tzinfo=ET).timestamp())


class RegularCloseBasisTests(unittest.TestCase):
    def test_weekend_uses_friday_close(self):
        points = [(ts("2026-09-24"), 767.18), (ts("2026-09-25"), 771.35)]
        basis, day = regular_close_basis(points, ts("2026-09-27", 18, 0), "ETF_CLOSED_PROXY", "America/New_York")
        self.assertEqual(day, "2026-09-25")
        self.assertAlmostEqual(basis, 771.35)

    def test_monday_premarket_uses_friday(self):
        points = [(ts("2026-09-25"), 771.35)]
        basis, day = regular_close_basis(points, ts("2026-09-28", 8, 0), "PRE", "America/New_York")
        self.assertEqual((basis, day), (771.35, "2026-09-25"))

    def test_monday_regular_ignores_incomplete_monday(self):
        points = [(ts("2026-09-25"), 771.35), (ts("2026-09-28", 10, 0), 772.10)]
        basis, day = regular_close_basis(points, ts("2026-09-28", 10, 0), "REGULAR", "America/New_York")
        self.assertEqual((basis, day), (771.35, "2026-09-25"))

    def test_postmarket_uses_same_day_regular_close(self):
        points = [(ts("2026-09-25"), 771.35), (ts("2026-09-28"), 773.20)]
        basis, day = regular_close_basis(points, ts("2026-09-28", 18, 0), "POST", "America/New_York")
        self.assertEqual((basis, day), (773.20, "2026-09-28"))

    def test_holiday_uses_prior_completed_session(self):
        points = [(ts("2026-07-02"), 700.0)]
        basis, day = regular_close_basis(points, ts("2026-07-03", 12, 0), "CLOSED", "America/New_York")
        self.assertEqual((basis, day), (700.0, "2026-07-02"))

    def test_last_sample_of_day_wins(self):
        points = [(ts("2026-09-25", 15, 50), 770.0), (ts("2026-09-25", 15, 55), 771.35)]
        basis, day = regular_close_basis(points, ts("2026-09-26", 12, 0), "CLOSED", "America/New_York")
        self.assertEqual((basis, day), (771.35, "2026-09-25"))

    def test_new_york_date_not_utc_date(self):
        utc_boundary = int(datetime.fromisoformat("2026-09-26T00:30:00+00:00").timestamp())
        points = [(utc_boundary, 771.35)]
        basis, day = regular_close_basis(points, ts("2026-09-26", 10, 0), "CLOSED", "America/New_York")
        self.assertEqual((basis, day), (771.35, "2026-09-25"))

    def test_dst_spring_week_keeps_market_dates(self):
        points = [(ts("2026-03-06"), 500.0), (ts("2026-03-09"), 501.0)]
        basis, day = regular_close_basis(points, ts("2026-03-09", 10, 0), "REGULAR", "America/New_York")
        self.assertEqual((basis, day), (500.0, "2026-03-06"))

    def test_dst_fall_week_keeps_market_dates(self):
        points = [(ts("2026-10-30"), 510.0), (ts("2026-11-02"), 511.0)]
        basis, day = regular_close_basis(points, ts("2026-11-02", 10, 0), "REGULAR", "America/New_York")
        self.assertEqual((basis, day), (510.0, "2026-10-30"))

    def test_invalid_values_are_ignored(self):
        points = [(ts("2026-09-24"), float("nan")), (ts("2026-09-25"), 771.35)]
        basis, day = regular_close_basis(points, ts("2026-09-26", 10, 0), "CLOSED", "America/New_York")
        self.assertEqual((basis, day), (771.35, "2026-09-25"))

    def test_no_prior_regular_day_during_regular_returns_none(self):
        points = [(ts("2026-09-28", 10, 0), 772.10)]
        basis, day = regular_close_basis(points, ts("2026-09-28", 10, 0), "REGULAR", "America/New_York")
        self.assertIsNone(basis)
        self.assertIsNone(day)


if __name__ == "__main__":
    unittest.main()
