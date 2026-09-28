import unittest
from datetime import date

import fx_basis


class FxBasisTests(unittest.TestCase):
    def test_parse_ecos_close_rows(self):
        payload = {
            "StatisticSearch": {
                "row": [
                    {"TIME": "20260924", "DATA_VALUE": "1,366.0"},
                    {"TIME": "20260925", "DATA_VALUE": "1357.5"},
                    {"TIME": "bad", "DATA_VALUE": "x"},
                ]
            }
        }
        self.assertEqual(
            fx_basis.parse_ecos_close_rows(payload),
            [(date(2026, 9, 24), 1366.0), (date(2026, 9, 25), 1357.5)],
        )

    def test_monday_uses_friday_close_even_if_monday_close_exists(self):
        closes = [
            (date(2026, 9, 25), 1357.5),
            (date(2026, 9, 28), 1365.1),
        ]
        value, basis_day = fx_basis.prior_business_close(closes, date(2026, 9, 28))
        self.assertEqual(value, 1357.5)
        self.assertEqual(basis_day, "2026-09-25")

    def test_weekend_uses_latest_prior_business_day(self):
        closes = [
            (date(2026, 9, 24), 1366.0),
            (date(2026, 9, 25), 1357.5),
        ]
        value, basis_day = fx_basis.prior_business_close(closes, date(2026, 9, 27))
        self.assertEqual(value, 1357.5)
        self.assertEqual(basis_day, "2026-09-25")

    def test_no_prior_day_returns_none(self):
        value, basis_day = fx_basis.prior_business_close(
            [(date(2026, 9, 28), 1365.1)], date(2026, 9, 28)
        )
        self.assertIsNone(value)
        self.assertIsNone(basis_day)


if __name__ == "__main__":
    unittest.main()
