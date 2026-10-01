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

    def test_public_basis_fields_rejects_startup_provider_fallback(self):
        # Startup can briefly inherit a mathematically valid provider previous
        # close from an older layer. Without explicit ECOS verification that
        # comparison must not escape through /status or /history.
        out = fx_basis.public_basis_fields({
            "previous_close": 1356.54,
            "previous_close_date": None,
            "day_change": 6.05,
            "day_change_percent": 0.446,
            "basis_verified": None,
            "basis_provider": None,
        })
        self.assertEqual(out, {
            "previous_close": None,
            "previous_close_date": None,
            "day_change": None,
            "day_change_percent": None,
            "basis_verified": False,
            "basis_provider": None,
        })

    def test_public_basis_fields_accepts_only_complete_ecos_basis(self):
        out = fx_basis.public_basis_fields({
            "previous_close": 1352.8,
            "previous_close_date": "2026-09-30",
            "day_change": 9.4,
            "day_change_percent": 0.695,
            "basis_verified": True,
            "basis_provider": "Bank of Korea ECOS 731Y003/0000003 15:30 close",
        })
        self.assertEqual(out["previous_close"], 1352.8)
        self.assertEqual(out["previous_close_date"], "2026-09-30")
        self.assertEqual(out["day_change"], 9.4)
        self.assertEqual(out["day_change_percent"], 0.695)
        self.assertIs(out["basis_verified"], True)
        self.assertIn("ECOS", out["basis_provider"])

    def test_public_basis_fields_rejects_false_verified_shape(self):
        out = fx_basis.public_basis_fields({
            "previous_close": 1352.8,
            "previous_close_date": "2026-09-30",
            "day_change": 9.4,
            "day_change_percent": 0.695,
            "basis_verified": True,
            "basis_provider": "Yahoo Finance fallback",
        })
        self.assertIs(out["basis_verified"], False)
        self.assertIsNone(out["previous_close"])
        self.assertIsNone(out["day_change_percent"])


if __name__ == "__main__":
    unittest.main()
