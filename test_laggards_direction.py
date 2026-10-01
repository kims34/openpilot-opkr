import unittest
from datetime import datetime, timezone

from laggards import _market_quote, _rank_directional, _regular_session_points


def utc_ts(iso: str) -> int:
    return int(datetime.fromisoformat(iso).replace(tzinfo=timezone.utc).timestamp())


class _FakeMonitor:
    def __init__(self, instrument_type: str):
        self.instrument_type = instrument_type

    def yahoo_result(self, symbol, range_, interval, prepost):
        return {
            "timestamp": [utc_ts("2026-09-25T14:00:00")],
            "indicators": {"quote": [{"close": [100.0]}]},
            "meta": {
                "instrumentType": self.instrument_type,
                "marketState": "REGULAR",
                "longName": symbol,
            },
        }

    @staticmethod
    def series(result):
        return list(zip(result["timestamp"], result["indicators"]["quote"][0]["close"]))


class DirectionalMoverTests(unittest.TestCase):
    def test_down_list_never_contains_gainers(self):
        rows = [
            {"symbol": "A", "day_change_pct": -3.0},
            {"symbol": "B", "day_change_pct": 2.0},
            {"symbol": "C", "day_change_pct": -1.0},
            {"symbol": "D", "day_change_pct": 0.0},
            {"symbol": "E", "day_change_pct": -5.0},
        ]
        ranked = _rank_directional(rows, "down")
        self.assertEqual([r["symbol"] for r in ranked], ["E", "A", "C"])
        self.assertTrue(all(r["day_change_pct"] < 0 for r in ranked))

    def test_up_list_never_contains_decliners(self):
        rows = [
            {"symbol": "A", "day_change_pct": -3.0},
            {"symbol": "B", "day_change_pct": 2.0},
            {"symbol": "C", "day_change_pct": 1.0},
            {"symbol": "D", "day_change_pct": 0.0},
            {"symbol": "E", "day_change_pct": 5.0},
        ]
        ranked = _rank_directional(rows, "up")
        self.assertEqual([r["symbol"] for r in ranked], ["E", "B", "C"])
        self.assertTrue(all(r["day_change_pct"] > 0 for r in ranked))

    def test_regular_filter_excludes_pre_and_post_market(self):
        # 2026-09-25: New York is UTC-4. 13:00 UTC=09:00, 14:00=10:00, 20:30=16:30.
        points = [
            (utc_ts("2026-09-25T13:00:00"), 100.0),
            (utc_ts("2026-09-25T14:00:00"), 101.0),
            (utc_ts("2026-09-25T19:55:00"), 102.0),
            (utc_ts("2026-09-25T20:30:00"), 103.0),
        ]
        filtered = _regular_session_points(points)
        self.assertEqual([v for _, v in filtered], [101.0, 102.0])

    def test_constituent_quote_rejects_etf_instrument_type(self):
        # A holdings-page parser can accidentally return an ETF ticker such as
        # USD (ProShares Ultra Semiconductors). It must never enter a company
        # constituent cache merely because the symbol is syntactically valid.
        with self.assertRaisesRegex(RuntimeError, "non-equity constituent"):
            _market_quote(_FakeMonitor("ETF"), "USD", require_equity=True)

    def test_etf_direction_quote_is_not_subject_to_constituent_equity_gate(self):
        # SPY/QQQ/SCHD themselves are intentionally used only to choose the
        # universe direction. They are not company constituents, so the gate is
        # not applied to those calls.
        with self.assertRaisesRegex(RuntimeError, "invalid quote basis"):
            _market_quote(_FakeMonitor("ETF"), "SCHD", require_equity=False)


if __name__ == "__main__":
    unittest.main()
