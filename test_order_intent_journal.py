import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

from order_intent_journal import OrderIntentJournal, OrderJournalError


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'orders.sqlite'
        self.j = OrderIntentJournal(self.path)
        self.j.register('decision-1', symbol='005930', side='BUY', quantity=10)
        self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])

    def tearDown(self):
        self.j.close()
        self.tmp.cleanup()

    def acknowledged(self):
        self.j.claim_submission('decision-1', expected_epoch=self.j.shadow_control()['epoch'])
        self.j.bind_acknowledgement('decision-1', 'broker-1')

    def fill(self, execution_id='fill-1', quantity=4):
        return self.j.record_execution('decision-1', broker_order_id='broker-1', execution_id=execution_id, quantity=quantity)

    def test_idempotency_and_conflicting_payload(self):
        self.assertEqual(self.j.register('decision-1', symbol='005930', side='BUY', quantity=10)['quantity'], 10)
        with self.assertRaisesRegex(OrderJournalError, 'collision'):
            self.j.register('decision-1', symbol='005930', side='BUY', quantity=11)
        self.assertEqual(self.j.get('decision-1')['quantity'], 10)

    def test_concurrent_connections_have_one_claimant(self):
        ready = Barrier(8)
        armed = Barrier(8)
        shared = {}
        def claim(_):
            journal = OrderIntentJournal(self.path)
            try:
                leader = ready.wait()
                if leader == 0:
                    shared['epoch'] = journal.enable_shadow(expected_epoch=journal.shadow_control()['epoch'])['epoch']
                armed.wait()
                journal.claim_submission('decision-1', expected_epoch=shared['epoch'])
                return True
            except OrderJournalError:
                return False
            finally:
                journal.close()
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(claim, range(8))), 1)

    def test_timeout_survives_restart_and_cannot_resubmit(self):
        self.j.claim_submission('decision-1', expected_epoch=self.j.shadow_control()['epoch'])
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        self.assertEqual(self.j.get('decision-1')['state'], 'RECONCILIATION_REQUIRED')
        self.assertEqual(self.j.recover()[0]['state'], 'RECONCILIATION_REQUIRED')
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('decision-1', expected_epoch=self.j.shadow_control()['epoch'])

    def test_uncertain_acknowledgement_alone_does_not_clear_block(self):
        self.j.claim_submission('decision-1', expected_epoch=self.j.shadow_control()['epoch'])
        self.j.mark_uncertain('decision-1')
        self.assertEqual(self.j.bind_acknowledgement('decision-1', 'broker-1')['state'], 'RECONCILIATION_REQUIRED')

    def test_duplicate_fill_is_idempotent_and_full_fill_has_zero_remaining(self):
        self.acknowledged()
        self.fill()
        self.assertEqual(self.fill()['filled_quantity'], 4)
        out = self.fill('fill-2', 6)
        self.assertEqual(out['state'], 'FILLED')
        self.assertEqual(out['remaining_quantity'], 0)
        self.assertFalse(out['live_ordering_authorized'])
        self.assertFalse(out['genuine_live_evidence'])

    def test_conflicting_duplicate_is_durably_quarantined(self):
        self.acknowledged()
        self.fill()
        with self.assertRaisesRegex(OrderJournalError, 'duplicate'):
            self.fill(quantity=5)
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        self.assertEqual(self.j.get('decision-1')['state'], 'RECONCILIATION_REQUIRED')
        self.assertEqual(self.j.get('decision-1')['filled_quantity'], 4)

    def test_overfill_rolls_back_quantity_and_quarantines(self):
        self.acknowledged()
        self.fill()
        with self.assertRaisesRegex(OrderJournalError, 'exceeds'):
            self.fill('fill-2', 7)
        self.assertEqual(self.j.get('decision-1')['filled_quantity'], 4)
        self.assertEqual(self.j.get('decision-1')['state'], 'RECONCILIATION_REQUIRED')

    def test_cancel_request_does_not_release_unknown_remaining(self):
        self.acknowledged()
        self.fill()
        out = self.j.mark_cancel_requested('decision-1')
        self.assertEqual(out['state'], 'RECONCILIATION_REQUIRED')
        self.assertEqual(out['remaining_quantity'], 6)
        self.assertEqual(self.fill('fill-2', 2)['state'], 'RECONCILIATION_REQUIRED')

    def test_cancel_fill_race_preserves_authoritative_quantity(self):
        self.acknowledged()
        self.fill()
        out = self.j.reconcile_snapshot('decision-1', broker_order_id='broker-1', status='CANCELLED', filled_quantity=4)
        self.assertEqual(out['state'], 'CANCELLED')
        out = self.fill('late-fill', 6)
        self.assertEqual(out['state'], 'FILLED')
        self.assertEqual(out['filled_quantity'], 10)

    def test_snapshot_mismatch_does_not_invent_missing_executions(self):
        self.acknowledged()
        self.fill()
        out = self.j.reconcile_snapshot('decision-1', broker_order_id='broker-1', status='OPEN', filled_quantity=5)
        self.assertEqual(out['state'], 'RECONCILIATION_REQUIRED')
        self.assertEqual(out['filled_quantity'], 4)

    def test_stale_snapshot_cannot_resurrect_terminal_order(self):
        self.acknowledged()
        self.j.reconcile_snapshot('decision-1', broker_order_id='broker-1', status='CANCELLED', filled_quantity=0)
        self.assertEqual(self.j.reconcile_snapshot('decision-1', broker_order_id='broker-1', status='OPEN', filled_quantity=0)['state'], 'RECONCILIATION_REQUIRED')
        self.assertEqual(self.j.reconcile_snapshot('decision-1', broker_order_id='broker-1', status='OPEN', filled_quantity=0)['state'], 'RECONCILIATION_REQUIRED')

    def test_unresolved_order_blocks_a_different_new_intent(self):
        self.acknowledged()
        self.j.mark_uncertain('decision-1')
        self.j.register('decision-2', symbol='000660', side='BUY', quantity=1)
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('decision-2', expected_epoch=self.j.shadow_control()['epoch'])
        self.assertEqual(self.j.get('decision-2')['state'], 'INTENT_CREATED')

    def test_wrong_broker_order_identity_is_quarantined(self):
        self.acknowledged()
        with self.assertRaises(OrderJournalError):
            self.j.bind_acknowledgement('decision-1', 'other-order')
        self.assertEqual(self.j.get('decision-1')['broker_order_id'], 'broker-1')
        self.assertEqual(self.j.get('decision-1')['state'], 'RECONCILIATION_REQUIRED')

    def test_rejected_order_cannot_acquire_fills(self):
        self.acknowledged()
        self.j.reconcile_snapshot('decision-1', broker_order_id='broker-1', status='REJECTED', filled_quantity=0)
        with self.assertRaises(OrderJournalError):
            self.fill()
        self.assertEqual(self.j.get('decision-1')['filled_quantity'], 0)
        self.assertEqual(self.j.get('decision-1')['state'], 'RECONCILIATION_REQUIRED')

    def test_restart_of_open_partial_fill_requires_reconciliation(self):
        self.acknowledged()
        self.fill()
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        rows = self.j.recover()
        self.assertEqual(rows[0]['filled_quantity'], 4)
        self.assertEqual(rows[0]['remaining_quantity'], 6)
        self.assertEqual(rows[0]['state'], 'RECONCILIATION_REQUIRED')

    def test_malformed_payloads_and_quantities_are_rejected(self):
        for quantity in (True, 0, -1, 1.5, '1'):
            with self.assertRaises(OrderJournalError):
                self.j.register('bad', symbol='005930', side='BUY', quantity=quantity)
        for symbol in (None, '', ' '):
            with self.assertRaises(OrderJournalError):
                self.j.register('bad', symbol=symbol, side='BUY', quantity=1)


if __name__ == '__main__':
    unittest.main()
