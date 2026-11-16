import tempfile
import unittest
from unittest.mock import patch
import monthly_touch_shadow as shadow
import monthly_touch_backtested_display as display


class HistoricalAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.con=shadow.connect(self.temp.name+'/ledger.db')
        self.con.execute('INSERT INTO monthly_touch_shadow_v1 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,NULL,NULL)',
            ('SPY',display.MODEL,'down','2026-11-13','2026-12-15',100,.23,.25,100,
             'source',display.MODEL_SHA256,'2026-10-14',8000))
    def tearDown(self):self.con.close();self.temp.cleanup()
    def forecast(self, symbol='SPY', digest=display.MODEL_SHA256, now=150):
        with patch.object(display,'validity',return_value=(200,'2026-12-15')):
            return display.admitted_forecast(self.con,symbol,digest,now)
    def test_bound_model_displays_only_historical_status(self):
        f=self.forecast();self.assertEqual(f['probability'],23)
        self.assertFalse(f['independent_confirmed'])
        self.assertEqual(f['verification_status'],'historical_backtest_passed')
    def test_expired_future_issued_missing_and_changed_model_are_hidden(self):
        self.assertIsNone(self.forecast(now=200));self.assertIsNone(self.forecast(now=99))
        self.assertIsNone(self.forecast('QQQ'));self.assertIsNone(self.forecast('SCHD'))
        self.assertIsNone(self.forecast(digest='changed'))
    def test_wrong_direction_target_or_digest_cannot_reuse_evidence(self):
        for field,value in [('direction','up'),('maturity','2026-12-16'),('model_digest','changed')]:
            self.con.execute('SAVEPOINT change')
            self.con.execute(f'UPDATE monthly_touch_shadow_v1 SET {field}=?',(value,))
            self.assertIsNone(self.forecast())
            self.con.execute('ROLLBACK TO change')
    def test_calendar_accounts_for_thanksgiving(self):
        expires,maturity=display.validity('2026-11-13')
        self.assertEqual(maturity,'2026-12-15')
        self.assertEqual(expires,1794862800)


if __name__=='__main__':unittest.main()
