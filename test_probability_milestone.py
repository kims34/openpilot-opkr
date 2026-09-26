import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import probability_milestone as milestone
from probability_shadow import SHADOW_MODELS

MODEL = "3.1-causal-adaptive-close"
SYMBOLS = ("SPY", "QQQ", "SCHD")


class ProbabilityMilestoneTest(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(delete=False)
        self.path = handle.name
        handle.close()
        with sqlite3.connect(self.path) as con:
            con.execute(
                """CREATE TABLE probability_forecasts(
                    model TEXT,symbol TEXT,as_of TEXT,target TEXT,p REAL,base REAL,
                    created REAL,outcome INTEGER,scored_at REAL,
                    PRIMARY KEY(model,symbol,as_of))"""
            )
            con.execute(
                """CREATE TABLE probability_shadow_forecasts(
                    model TEXT NOT NULL,symbol TEXT NOT NULL,as_of TEXT NOT NULL,
                    target TEXT NOT NULL,p REAL NOT NULL,created REAL NOT NULL,
                    outcome INTEGER,scored_at REAL,
                    PRIMARY KEY(model,symbol,as_of))"""
            )
            con.execute(
                """CREATE TABLE devices(
                    token TEXT PRIMARY KEY, platform TEXT, updated_at TEXT,
                    settings TEXT DEFAULT '{}', protocol INTEGER DEFAULT 1)"""
            )

    def tearDown(self):
        try:
            os.unlink(self.path)
        except FileNotFoundError:
            pass

    def seed(self, count):
        with sqlite3.connect(self.path) as con:
            for symbol in SYMBOLS:
                for i in range(count):
                    as_of = f"d{i:03d}"
                    target = f"t{i:03d}"
                    outcome = i % 2
                    base_p = 0.60 if outcome else 0.40
                    con.execute(
                        "INSERT INTO probability_forecasts VALUES(?,?,?,?,?,?,?,?,?)",
                        (MODEL, symbol, as_of, target, base_p, 0.50, i, outcome, i + 1),
                    )
                    for shadow_model in SHADOW_MODELS:
                        if shadow_model == "shadow-fixed75-v1":
                            shadow_p = 0.70 if outcome else 0.30
                        elif shadow_model == "shadow-fixed50-v1":
                            shadow_p = 0.55 if outcome else 0.45
                        else:
                            shadow_p = base_p
                        con.execute(
                            "INSERT INTO probability_shadow_forecasts VALUES(?,?,?,?,?,?,?,?)",
                            (shadow_model, symbol, as_of, target, shadow_p, i, outcome, i + 1),
                        )

    def test_not_ready_before_60_matched_sessions(self):
        self.seed(59)
        report = milestone.build_comparison(self.path, MODEL)
        self.assertFalse(report["ready"])
        self.assertEqual(report["min_count"], 59)

    def test_ready_at_60_and_compares_same_sessions(self):
        self.seed(60)
        report = milestone.build_comparison(self.path, MODEL)
        self.assertTrue(report["ready"])
        self.assertEqual(report["min_count"], 60)
        self.assertEqual(report["best_candidate"], "shadow-fixed75-v1")
        self.assertEqual(report["verdict"], "shadow_improved")
        best = report["models"]["shadow-fixed75-v1"]
        self.assertEqual(best["improved_symbols"], 3)
        self.assertAlmostEqual(best["base_brier"], 0.16, places=10)
        self.assertAlmostEqual(best["shadow_brier"], 0.09, places=10)

    def test_push_is_sent_once_per_registered_device(self):
        self.seed(60)
        token = "test-device-token-abcdefghijklmnopqrstuvwxyz"
        with sqlite3.connect(self.path) as con:
            con.execute(
                "INSERT INTO devices(token,platform,updated_at,settings,protocol) VALUES(?,?,?,?,?)",
                (token, "android", "now", "{}", 2),
            )
        with patch.object(milestone, "_init_firebase", return_value=True), patch.object(
            milestone, "_send_message", return_value="message-id"
        ) as send:
            first = milestone.maybe_notify(self.path, MODEL, now=1000)
            second = milestone.maybe_notify(self.path, MODEL, now=2000)
        self.assertEqual(first["sent"], 1)
        self.assertEqual(first["pending"], 0)
        self.assertEqual(second["sent"], 0)
        self.assertEqual(second["pending"], 0)
        self.assertEqual(send.call_count, 1)
        args = send.call_args.args
        self.assertEqual(args[0], token)
        self.assertEqual(args[1], 2)
        self.assertIn("60회", args[2])
        self.assertEqual(args[4]["event_type"], "probability_milestone")


if __name__ == "__main__":
    unittest.main()
