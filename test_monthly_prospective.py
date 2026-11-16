"""Offline prospective 21-session ledger regression tests; no real orders."""
import os
import sqlite3
import tempfile
import unittest
from datetime import date, timedelta
from unittest.mock import patch

import monthly_prospective as p


def history():
    start = date(2026, 1, 1)
    # Artificial daily "session" IDs only for mocked ledger; NOT market data.
    days = [(start+timedelta(days=i)).isoformat() for i in range(80)]
    rows = [(d, 100.0) for d in days]
    month = {"as_of":days[30], "price_basis":"daily_high_low",
             "up_10_probability":12.3,"down_10_probability":9.8,
             "baseline_up_10_probability":17.1,
             "baseline_down_10_probability":11.1}
    meta = {"as_of":days[30],"target_date":days[31],
            "target_open": 2000.0}
    vendor = {d:(100.0,100.0,100.0) for d in days}
    vendor[days[38]] = (111.0,100.0,100.0)
    vendor[days[44]] = (100.0,89.0,100.0)
    return rows,month,meta,vendor


class ProspectiveMonthlyTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.t.name,"test.db")

    def tearDown(self):
        self.t.cleanup()

    def _record(self, rows, month, meta, now=1000.0):
        with patch.object(p,"_maturity",return_value=rows[51][0]):
            return p.observe("SPY",month,rows[:31],meta,now,db_path=self.db)

    def test_first_issued_is_immutable(self):
        rows,m,meta,vendor=history()
        first=self._record(rows,m,meta)
        self.assertTrue(first["inserted"])
        changed=dict(m,up_10_probability=99.0)
        second=self._record(rows,changed,meta,now=1100.0)
        self.assertFalse(second["inserted"])
        with sqlite3.connect(self.db) as con:
            r=con.execute("SELECT up_p,issued_at,maturity_session FROM monthly_prospective_v1").fetchone()
            self.assertEqual(r,(.123,1000.0,rows[51][0]))

    def test_21_full_sessions_not_20(self):
        rows,m,meta,vendor=history()
        self._record(rows,m,meta)
        x=p.observe("SPY",{},rows[:51],{"as_of":rows[50][0]},2001.0,
                    db_path=self.db,strict_supplier=lambda s:vendor)
        self.assertEqual(x["scored"],0)
        self.assertEqual(p.summary(self.db)["symbols"]["SPY"]["pending_count"],1)

    def test_label_both_independent_events_and_summaries(self):
        rows,m,meta,vendor=history()
        self._record(rows,m,meta)
        z=p.observe("SPY",{},rows[:52],{"as_of":rows[51][0]},3000.0,
                    db_path=self.db,strict_supplier=lambda s:vendor)
        self.assertEqual(z["scored"],1)
        scored=p.summary(self.db)["symbols"]["SPY"]
        self.assertEqual(scored["scored_count"],1)
        self.assertEqual(scored["up_event_count"],1)
        self.assertEqual(scored["down_event_count"],1)
        self.assertAlmostEqual(scored["brier_up"],(.123-1)**2,places=10)
        self.assertAlmostEqual(scored["brier_down"],(.098-1)**2,places=10)
        self.assertEqual(scored["status"],"INSUFFICIENT_PROSPECTIVE_EVIDENCE")
        self.assertEqual(z["inserted"],False)

    def test_missing_vendor_high_does_not_invent_negative_label(self):
        rows,m,meta,vendor=history()
        self._record(rows,m,meta)
        del vendor[rows[37][0]]
        z=p.observe("SPY",{},rows[:52],{},3000.0,db_path=self.db,
                    strict_supplier=lambda s:vendor)
        self.assertEqual(z["scored"],0)
        self.assertEqual(p.summary(self.db)["symbols"]["SPY"]["pending_count"],1)

    def test_unsupported_and_late_forecasts_not_recorded(self):
        rows,m,meta,vendor=history()
        self.assertEqual(p.observe("TQQQ",m,rows,meta,now=1000,db_path=self.db)["status"],
                         "symbol_not_tracked")
        z=self._record(rows,dict(m,price_basis="daily_close"),meta)
        self.assertFalse(z["inserted"])
        z=self._record(rows,m,meta,now=3000)
        self.assertFalse(z["inserted"])
        self.assertEqual(p.summary(self.db)["symbols"]["SPY"]["stored_count"],0)

    def test_revision_of_anchor_blocks_scoring(self):
        rows,m,meta,vendor=history()
        self._record(rows,m,meta)
        modified=rows[:52].copy()
        d,_=modified[30]
        modified[30]=(d,99.0)
        z=p.observe("SPY",{},modified,{},now=3000,db_path=self.db,
                    strict_supplier=lambda s:vendor)
        self.assertEqual(z["scored"],0)

    def test_duplicate_or_unordered_history_rejected(self):
        rows,m,meta,vendor=history()
        bad=rows[:31]
        bad[8]=(bad[7][0],100.0)
        with self.assertRaises(ValueError):
            self._record(bad,m,meta)

    def test_reject_nonfinite_and_unknown_probabilities(self):
        rows,m,meta,vendor=history()
        with self.assertRaises(ValueError):
            self._record(rows,dict(m,up_10_probability=float("nan")),meta)
        with self.assertRaises(ValueError):
            self._record(rows,dict(m,up_10_probability=120.0),meta)

    def test_score_does_not_change_when_later_prices_change(self):
        rows,m,meta,vendor=history()
        self._record(rows,m,meta)
        p.observe("SPY",{},rows[:52],{},3000.0,db_path=self.db,
                  strict_supplier=lambda s:vendor)
        changed=rows[:].copy()
        for i in range(53,len(changed)):
            d,_=changed[i]
            changed[i]=(d,170.0)
        p.observe("SPY",{},changed,{},now=4000.0,db_path=self.db,
                  strict_supplier=lambda s:vendor)
        with sqlite3.connect(self.db) as con:
            self.assertEqual(con.execute("SELECT up_hit,down_hit,scored_at "
                          "FROM monthly_prospective_v1").fetchone(),(1,1,3000.0))

    def test_calendar_21_sessions(self):
        val=p._maturity("2026-11-16", 1794820000.0)
        self.assertTrue(val.startswith("2026-12"))
        self.assertGreater(val,"2026-11-16")

    def test_summary_empty_is_safe(self):
        s=p.summary(self.db)
        self.assertEqual(s["symbols"]["QQQ"]["stored_count"],0)
        self.assertEqual(s["symbols"]["SPY"]["scored_count"],0)
        self.assertFalse(s["orders_enabled"])


if __name__ == "__main__":
    unittest.main()
