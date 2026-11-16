import unittest
from unittest.mock import patch
import test_quarterly_touch as fixtures
import historical_touch as history
import historical_touch_model as model


class HistoricalLedgerTests(unittest.TestCase):
    def setUp(self):fixtures.QuarterlyLedgerTests.setUp(self)
    def tearDown(self):self.temp.cleanup()
    def issue(self,symbol='SPY',clock=None):
        history.observe(symbol,[(d,c) for d,h,l,c in self.rows[:self.t+1]],self.meta,self.db,
            lambda symbol,closes:self.rows[:len(closes)],clock or (lambda:self.opening-100))
    def test_all_24_targets_display_without_performance_gate(self):
        for symbol in ('SPY','QQQ','SCHD'):self.issue(symbol)
        rows=history.summary(self.db,self.opening-50)
        self.assertEqual(len(rows),24)
        self.assertEqual({r['horizon_sessions'] for r in rows},{21,63})
        self.assertEqual({r['threshold_percent'] for r in rows},{5,10})
        self.assertTrue(all(r['verification_status']=='historical_estimate' and not r['independent_confirmed'] for r in rows))
        # Previously rejected targets are present, rather than labelled as passed.
        self.assertTrue(any(r['symbol']=='SCHD' and r['event']=='63:down10_touch' for r in rows))
        self.issue()
        self.assertTrue(all(r['stored_count']==1 for r in history.summary(self.db,self.opening-50)))
    def test_expiry_changed_model_and_late_issue_remain_blocked(self):
        self.issue();self.assertEqual(history.summary(self.db,self.expires),[])
        with patch.object(history,'DIGEST','changed'):
            self.assertEqual(history.summary(self.db,self.opening-50),[])
        self.issue('QQQ',lambda:self.opening+1)
        self.assertFalse(any(r['symbol']=='QQQ' for r in history.summary(self.db,self.opening+2)))
    def test_maturities_score_separately(self):
        self.issue()
        for offset,expected in [(20,0),(21,4),(62,4),(63,8)]:
            cut=self.t+offset;closes=[(d,c) for d,h,l,c in self.rows[:cut+1]]
            history.observe('SPY',closes,{'as_of':closes[-1][0],'target_open':0},self.db,
                lambda symbol,closes:self.rows[:len(closes)],lambda:self.opening+10000000)
            with history.connect(self.db) as con:
                self.assertEqual(con.execute('SELECT COUNT(outcome) FROM historical_touch_v1').fetchone()[0],expected)
    def test_model_rejects_invalid_bars_and_excludes_future(self):
        prefix=self.rows[:self.t+1]
        first=model.estimate_all(prefix)
        changed=self.rows.copy();changed[self.t+1]=(changed[self.t+1][0],10000.,1.,100.)
        self.assertEqual(first,model.estimate_all(changed[:self.t+1]))
        broken=prefix.copy();d,h,l,c=broken[-1];broken[-1]=(d,l,h,c)
        with self.assertRaises(ValueError):model.estimate_all(broken)


if __name__=='__main__':unittest.main()
