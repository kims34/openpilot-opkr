import unittest, tempfile, json, time
from unittest.mock import patch
import monitor as m

class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        m.DB_PATH=self.tmp.name+'/test.db'
        m.ATH_REFRESH.clear()
        m.init_db()
        self.firebase=patch.object(m,'init_firebase',return_value=True);self.firebase.start()
        self.sender=patch.object(m.messaging,'send',return_value='ok');self.send=self.sender.start()
    def tearDown(self):
        self.sender.stop();self.firebase.stop();self.tmp.cleanup()
    def register(self, token='a'*30, enabled=None, protocol=2):
        return m.register(m.RegisterBody(token=token, enabled_levels=enabled,protocol=protocol))
    def test_partial_failure_retries_only_failed_device_after_rebound(self):
        self.register();self.register('b'*30)
        self.send.side_effect=['ok',RuntimeError('temporary')]
        m.enqueue_crossings('sp500',100,-12,'cash')
        self.assertEqual(self.send.call_count,2)
        self.send.reset_mock();self.send.side_effect=None
        m.enqueue_crossings('sp500',100,-1,'cash')
        self.assertEqual(self.send.call_count,1)
        self.assertEqual(self.send.call_args.args[0].token,'b'*30)
        self.assertIsNone(self.send.call_args.args[0].notification)
        m.enqueue_crossings('sp500',100,-12,'cash')
        self.assertEqual(self.send.call_count,1)
    def test_disabled_levels_and_cancellation(self):
        self.register()
        self.send.side_effect=RuntimeError('temporary')
        m.enqueue_crossings('sp500',100,-12,'cash')
        settings={key:[] for key in m.RULES}
        self.register(enabled=settings)
        self.send.reset_mock();self.send.side_effect=None
        m.enqueue_crossings('sp500',100,-12,'cash')
        self.send.assert_not_called()
    def test_new_ath_resets_ledger(self):
        self.register()
        m.enqueue_crossings('sp500',100,-12,'cash')
        m.enqueue_crossings('sp500',110,-12,'cash')
        self.assertEqual(self.send.call_count,2)
    def test_bar_high_updates_ath_even_after_close(self):
        self.register();m.save_state('sp500',100,98,98,'cash')
        fixture={'timestamp':[int(time.time())], 'meta':{},'indicators':{'quote':[{'close':[99],'high':[105]}]}}
        with patch.object(m,'yahoo_result',return_value=fixture), patch.object(m,'historical_ath',return_value=100), patch.object(m,'proxy_ratio_from_cash_close',return_value=(1,1,1,1,1)):
            result=m.evaluate('sp500')
        self.assertEqual(result['ath'],105)
    def test_legacy_notification_and_idempotent_migration(self):
        self.register(protocol=1)
        m.enqueue_crossings('ndx',100,-15,'cash')
        self.assertIsNotNone(self.send.call_args.args[0].notification)
        m.init_db();m.enqueue_crossings('ndx',100,-15,'cash')
        self.assertEqual(self.send.call_count,1)
    def test_old_global_fired_migration(self):
        self.register();m.save_state('sp500',100,90,90,'cash');m.mark_fired('sp500',[5,10])
        with m.db() as con: con.execute('DELETE FROM migrations')
        m.init_db();m.enqueue_crossings('sp500',100,-12,'cash')
        self.send.assert_not_called()
    def test_invalid_settings_rejected(self):
        with self.assertRaises(m.HTTPException): self.register(enabled={'sp500':[999]})
    def test_pending_expires(self):
        self.register();self.send.side_effect=RuntimeError('temporary')
        m.enqueue_crossings('sp500',100,-12,'cash')
        with m.db() as con: con.execute('UPDATE deliveries SET created=0')
        self.send.reset_mock();self.send.side_effect=None
        m.enqueue_crossings('sp500',100,-1,'cash')
        self.send.assert_not_called()

if __name__=='__main__':unittest.main()
