import unittest

from research_v1_pit_labels import kospi_statutory_sell_tax_bps


class KospiHistoricalTaxTest(unittest.TestCase):
    def test_modern_regime_boundaries(self):
        cases = {
            "2015-06-15": 30.0,
            "2019-06-02": 30.0,
            "2019-06-03": 25.0,
            "2020-12-31": 25.0,
            "2021-01-01": 23.0,
            "2022-12-31": 23.0,
            "2023-01-01": 20.0,
            "2024-01-01": 18.0,
            "2025-01-01": 15.0,
            "2026-01-01": 20.0,
        }
        for day, expected in cases.items():
            with self.subTest(day=day):
                self.assertEqual(kospi_statutory_sell_tax_bps(day), expected)

    def test_pre_modern_regime_rejected(self):
        with self.assertRaises(ValueError):
            kospi_statutory_sell_tax_bps("2015-06-14")


if __name__ == "__main__":
    unittest.main()
