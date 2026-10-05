import tempfile
import unittest
from pathlib import Path

from order_intent_journal import OrderIntentJournal, OrderJournalError


class ShadowSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'journal.sqlite'
        self.j = OrderIntentJournal(self.path)
        self.j.register('d1', symbol='005930', side='BUY', quantity=2)

    def tearDown(self):
        self.j.close()
        self.tmp.cleanup()

    def enable(self):
        return self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])['epoch']

    def test_default_off_and_missing_epoch_cannot_claim(self):
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        for epoch in (None, self.j.shadow_control()['epoch']):
            with self.assertRaises(OrderJournalError):
                self.j.claim_submission('d1', expected_epoch=epoch)
        self.assertEqual(self.j.get('d1')['state'], 'INTENT_CREATED')

    def test_disable_invalidates_previous_epoch(self):
        epoch = self.enable()
        self.j.disable_shadow()
        with self.assertRaisesRegex(OrderJournalError, 'stale'):
            self.j.claim_submission('d1', expected_epoch=epoch)

    def test_enable_after_disable_does_not_revive_old_epoch(self):
        old = self.enable()
        self.j.disable_shadow()
        new = self.enable()
        self.assertGreater(new, old)
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('d1', expected_epoch=old)
        self.assertEqual(self.j.claim_submission('d1', expected_epoch=new)['state'], 'SUBMITTING')

    def test_kill_persists_on_reconnect_and_blocks_enable(self):
        old = self.enable()
        self.j.trip_kill_switch()
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        self.assertTrue(self.j.shadow_control()['killed'])
        with self.assertRaisesRegex(OrderJournalError, 'latched'):
            self.enable()
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('d1', expected_epoch=old)

    def test_kill_reset_stays_off_and_requires_fresh_enable(self):
        self.j.trip_kill_switch()
        out = self.j.reset_kill_switch(expected_epoch=self.j.shadow_control()['epoch'])
        self.assertFalse(out['killed'])
        self.assertEqual(out['mode'], 'MASTER_OFF')
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('d1', expected_epoch=out['epoch'])
        epoch = self.enable()
        self.j.claim_submission('d1', expected_epoch=epoch)

    def test_restart_without_kill_still_disables_shadow(self):
        old = self.enable()
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertGreater(self.j.shadow_control()['epoch'], old)
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('d1', expected_epoch=old)

    def test_uncertain_outcome_blocks_enable_and_kill_reset(self):
        epoch = self.enable()
        self.j.claim_submission('d1', expected_epoch=epoch)
        self.j.mark_uncertain('d1')
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        with self.assertRaisesRegex(OrderJournalError, 'unresolved'):
            self.enable()
        self.j.trip_kill_switch()
        with self.assertRaisesRegex(OrderJournalError, 'unresolved'):
            self.j.reset_kill_switch(expected_epoch=self.j.shadow_control()['epoch'])

    def test_conflict_disables_claims_without_erasing_fills(self):
        epoch = self.enable()
        self.j.claim_submission('d1', expected_epoch=epoch)
        self.j.bind_acknowledgement('d1', 'o1')
        self.j.record_execution('d1', broker_order_id='o1', execution_id='e1', quantity=1)
        with self.assertRaises(OrderJournalError):
            self.j.record_execution('d1', broker_order_id='o1', execution_id='e1', quantity=2)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.get('d1')['filled_quantity'], 1)

    def test_boolean_float_or_string_epoch_rejected(self):
        for epoch in (True, 1.0, '1', -1):
            with self.assertRaises(OrderJournalError):
                self.j.enable_shadow(expected_epoch=epoch)
            self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')

    def test_successful_reconciliation_does_not_auto_enable(self):
        epoch = self.enable()
        self.j.claim_submission('d1', expected_epoch=epoch)
        self.j.mark_uncertain('d1')
        self.j.bind_acknowledgement('d1', 'o1')
        self.j.reconcile_snapshot('d1', broker_order_id='o1', status='OPEN', filled_quantity=0)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertFalse(self.j.shadow_control()['live_ordering_authorized'])

    def test_broker_order_cannot_bind_to_two_decisions(self):
        epoch = self.enable()
        self.j.claim_submission('d1', expected_epoch=epoch)
        self.j.bind_acknowledgement('d1', 'o1')
        self.j.register('d2', symbol='000660', side='BUY', quantity=2)
        self.j.claim_submission('d2', expected_epoch=epoch)
        with self.assertRaisesRegex(OrderJournalError, 'another intent'):
            self.j.bind_acknowledgement('d2', 'o1')
        self.assertEqual(self.j.get('d1')['broker_order_id'], 'o1')
        self.assertIsNone(self.j.get('d2')['broker_order_id'])
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')

    def test_payload_collision_disables_even_before_submission(self):
        self.enable()
        with self.assertRaisesRegex(OrderJournalError, 'collision'):
            self.j.register('d1', symbol='000660', side='BUY', quantity=2)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.get('d1')['symbol'], '005930')

    def test_repeated_fill_attempt_does_not_override_rejection(self):
        epoch = self.enable()
        self.j.claim_submission('d1', expected_epoch=epoch)
        self.j.bind_acknowledgement('d1', 'o1')
        self.j.reconcile_snapshot('d1', broker_order_id='o1', status='REJECTED', filled_quantity=0)
        for _ in range(2):
            with self.assertRaises(OrderJournalError):
                self.j.record_execution('d1', broker_order_id='o1', execution_id='e1', quantity=1)
        self.assertEqual(self.j.get('d1')['filled_quantity'], 0)
        self.assertEqual(self.j.get('d1')['terminal_status'], 'REJECTED')


if __name__ == '__main__':
    unittest.main()
