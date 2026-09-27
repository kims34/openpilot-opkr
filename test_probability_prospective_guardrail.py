import sqlite3
import tempfile
import unittest

import probability_prospective_guardrail as guard


class ProspectiveGuardrailTests(unittest.TestCase):
    def _db(self, rows):
        tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        tmp.close()
        with sqlite3.connect(tmp.name) as con:
            con.execute('''CREATE TABLE probability_forecasts(
                model TEXT,symbol TEXT,as_of TEXT,target TEXT,p REAL,base REAL,
                created REAL,outcome INTEGER,scored_at REAL,
                PRIMARY KEY(model,symbol,as_of))''')
            con.executemany(
                'INSERT INTO probability_forecasts VALUES(?,?,?,?,?,?,?, ?,?)',
                [
                    ('3.3-calibration-gated','SPY',f'a{i:03d}',f't{i:03d}',p,b,float(i),y,float(i))
                    for i,(p,b,y) in enumerate(rows)
                ]
            )
        return tmp.name

    def test_collecting_before_twenty_scores(self):
        path = self._db([(0.5,0.5,0)] * 19)
        report = guard.summarize(path,'3.3-calibration-gated','SPY')
        self.assertEqual(report['state'],'collecting')
        self.assertEqual(report['scored_count'],19)
        self.assertEqual(report['windows'],{})
        self.assertTrue(report['served_probability_unchanged'])

    def test_review_requires_all_20_40_60_windows_to_trail_baseline(self):
        path = self._db([(0.9,0.5,0)] * 60)
        report = guard.summarize(path,'3.3-calibration-gated','SPY')
        self.assertEqual(report['state'],'review')
        self.assertEqual(set(report['windows']),{'20','40','60'})
        for size in ('20','40','60'):
            self.assertFalse(report['windows'][size]['beats_baseline'])
            self.assertLess(report['windows'][size]['skill'],0)

    def test_watch_when_recent_20_and_40_trail_but_60_still_beats(self):
        rows = [(0.0,0.5,0)] * 20 + [(0.55,0.5,0)] * 40
        path = self._db(rows)
        report = guard.summarize(path,'3.3-calibration-gated','SPY')
        self.assertEqual(report['state'],'watch')
        self.assertFalse(report['windows']['20']['beats_baseline'])
        self.assertFalse(report['windows']['40']['beats_baseline'])
        self.assertTrue(report['windows']['60']['beats_baseline'])

    def test_normal_when_recent_model_beats_baseline(self):
        path = self._db([(0.1,0.5,0)] * 60)
        report = guard.summarize(path,'3.3-calibration-gated','SPY')
        self.assertEqual(report['state'],'normal')
        self.assertTrue(report['windows']['20']['beats_baseline'])
        self.assertAlmostEqual(report['windows']['20']['direction_accuracy'],100.0)
        self.assertAlmostEqual(report['windows']['20']['calibration_gap_pp'],10.0)

    def test_other_model_rows_are_not_mixed(self):
        path = self._db([(0.1,0.5,0)] * 20)
        with sqlite3.connect(path) as con:
            con.executemany(
                'INSERT INTO probability_forecasts VALUES(?,?,?,?,?,?,?, ?,?)',
                [('other','SPY',f'x{i}',f'x{i}',0.9,0.5,0.0,0,0.0) for i in range(60)]
            )
        report = guard.summarize(path,'3.3-calibration-gated','SPY')
        self.assertEqual(report['scored_count'],20)
        self.assertEqual(report['state'],'normal')


if __name__ == '__main__':
    unittest.main()
