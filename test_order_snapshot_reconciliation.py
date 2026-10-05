import copy
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

from order_intent_journal import OrderIntentJournal, OrderJournalError
from order_snapshot_reconciliation import reconcile_order_snapshot_batch


class SnapshotBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'synthetic.sqlite'
        self.j = OrderIntentJournal(self.path)
        epoch = self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])['epoch']
        for key in ('d1', 'd2'):
            self.j.register(key, symbol='SYNTHETIC-'+key, side='BUY', quantity=10)
            self.j.claim_submission(key, expected_epoch=epoch)
            self.j.bind_acknowledgement(key, 'order-'+key)
        self.j.record_execution('d1', broker_order_id='order-d1', execution_id='fill1', quantity=4)
        self.orders = [dict(key=key, broker_order_id='order-'+key,
            symbol='SYNTHETIC-'+key, side='BUY', quantity=10,
            filled_quantity=4 if key == 'd1' else 0, status='OPEN') for key in ('d1', 'd2')]

    def tearDown(self):
        self.j.close()
        self.tmp.cleanup()

    def apply(self, orders=None, revision=1):
        return reconcile_order_snapshot_batch(self.j, revision=revision,
            orders=self.orders if orders is None else orders)

    def assert_blocked(self):
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        with self.assertRaises(OrderJournalError):
            self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])

    def test_complete_snapshot_stays_off_without_broker_authority_or_network(self):
        self.j.recover()
        with patch('socket.socket', side_effect=AssertionError('network forbidden')):
            result = self.apply()
        self.assertTrue(result['matched'])
        self.assertEqual(self.j.get('d1')['state'], 'PARTIALLY_FILLED')
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        for flag in ('real_broker_origin_verified', 'account_scope_attested',
            'snapshot_freshness_attested', 'genuine_live_evidence', 'live_ordering_authorized'):
            self.assertFalse(result[flag])

    def test_missing_order_quarantines_entire_batch_and_preserves_fills(self):
        result = self.apply(self.orders[:1])
        self.assertIn('ORDER_SCOPE_MISMATCH', result['errors'])
        for key in ('d1', 'd2'):
            self.assertEqual(self.j.get(key)['state'], 'RECONCILIATION_REQUIRED')
        self.assertEqual(self.j.get('d1')['filled_quantity'], 4)
        self.assert_blocked()

    def test_unknown_order_blocks_even_when_all_known_orders_match(self):
        unknown = dict(self.orders[1], key='foreign', broker_order_id='foreign-order')
        result = self.apply(self.orders + [unknown])
        self.assertIn('UNKNOWN_OR_UNCLAIMED_ORDER', result['errors'])
        self.assert_blocked()

    def test_unclaimed_intent_cannot_be_turned_into_submitted_order(self):
        self.j.register('d3', symbol='SYNTHETIC-d3', side='BUY', quantity=10)
        unknown = dict(self.orders[1], key='d3', symbol='SYNTHETIC-d3', broker_order_id='order-d3')
        self.assertFalse(self.apply(self.orders + [unknown])['matched'])
        self.assertEqual(self.j.get('d3')['state'], 'INTENT_CREATED')

    def test_duplicate_key_or_broker_id_fails(self):
        for orders in (self.orders + [self.orders[0]],
            [self.orders[0], dict(self.orders[1], broker_order_id='order-d1')]):
            with self.subTest(orders=orders):
                result = self.apply(orders, revision=self.j.db.execute(
                    'SELECT revision FROM reconciliation_barrier').fetchone()[0]+1)
                self.assertIn('DUPLICATE_ORDER_BINDING', result['errors'])
                self.assert_blocked()

    def test_identity_direction_quantity_and_fill_mismatches_do_not_mutate_ledger(self):
        for i, (field, value) in enumerate((('symbol','OTHER'), ('side','SELL'),
            ('quantity',11), ('filled_quantity',5), ('broker_order_id','OTHER')), 1):
            orders = copy.deepcopy(self.orders)
            orders[0][field] = value
            self.assertFalse(self.apply(orders, revision=i)['matched'])
            self.assertEqual(self.j.get('d1')['filled_quantity'], 4)
            self.assertEqual(self.j.get('d1')['symbol'], 'SYNTHETIC-d1')
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone()[0], 1)

    def test_stale_snapshot_cannot_clear_after_restart(self):
        self.assertTrue(self.apply(revision=2)['matched'])
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        result = self.apply(revision=2)
        self.assertIn('STALE_OR_REPLAYED_SNAPSHOT', result['errors'])
        self.assert_blocked()
        self.assertTrue(self.apply(revision=3)['matched'])
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')

    def test_individual_reconciliation_cannot_bypass_persistent_batch_barrier(self):
        self.apply(self.orders[:1])
        for order in self.orders:
            self.j.reconcile_snapshot(order['key'], broker_order_id=order['broker_order_id'],
                status='OPEN', filled_quantity=order['filled_quantity'])
        self.assert_blocked()
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        self.assert_blocked()
        self.assertTrue(self.apply(revision=2)['matched'])
        self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])

    def test_kill_latch_is_not_cleared_by_successful_batch(self):
        self.j.trip_kill_switch()
        self.assertTrue(self.apply()['matched'])
        self.assertTrue(self.j.shadow_control()['killed'])
        self.assert_blocked()

    def test_terminal_order_cannot_be_resurrected(self):
        self.j.reconcile_snapshot('d2', broker_order_id='order-d2', status='CANCELLED', filled_quantity=0)
        self.assertIn('TERMINAL_STATUS_CONFLICT', self.apply()['errors'])
        self.assertEqual(self.j.get('d2')['terminal_status'], 'CANCELLED')
        orders = copy.deepcopy(self.orders)
        orders[1]['status'] = 'CANCELLED'
        self.assertTrue(self.apply(orders, revision=2)['matched'])

    def test_all_filled_event_does_not_clear_previous_conflict(self):
        self.j.mark_uncertain('d1')
        result = self.j.record_execution('d1', broker_order_id='order-d1', execution_id='fill2', quantity=6)
        self.assertEqual(result['state'], 'RECONCILIATION_REQUIRED')
        self.assertEqual(result['filled_quantity'], 10)
        self.assertEqual(result['terminal_status'], 'FILLED')
        self.assert_blocked()
        orders = copy.deepcopy(self.orders)
        orders[0].update(filled_quantity=10, status='FILLED')
        self.assertTrue(self.apply(orders)['matched'])
        self.assertEqual(self.j.get('d1')['state'], 'FILLED')

    def test_malformed_inputs_persist_off_and_never_raise_raw_type_errors(self):
        for revision in (True, -1, 0, 1.1, '1', None, 2**63):
            self.assertIn('INVALID_SNAPSHOT_REVISION', self.apply(revision=revision)['errors'])
            self.assert_blocked()
        for i, orders in enumerate((None, 'orders', [None], [{}],
            [dict(self.orders[0], filled_quantity=True)],
            [dict(self.orders[0], status=['OPEN'])]), 1):
            result = reconcile_order_snapshot_batch(self.j, revision=i, orders=orders)
            self.assertFalse(result['matched'])
            self.assert_blocked()

    def test_inflight_without_broker_identity_cannot_be_silently_resolved(self):
        self.j.register('d3', symbol='SYNTHETIC', side='SELL', quantity=1)
        self.j.claim_submission('d3', expected_epoch=self.j.shadow_control()['epoch'])
        self.assertFalse(self.apply()['matched'])
        self.assertIsNone(self.j.get('d3')['broker_order_id'])
        self.assert_blocked()

    def test_racing_revisions_preserve_high_watermark_and_never_enable(self):
        ready = Barrier(2)
        def reconcile(revision):
            j = OrderIntentJournal(self.path)
            try:
                ready.wait()
                return reconcile_order_snapshot_batch(j, revision=revision, orders=self.orders)
            finally:
                j.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(reconcile, (1, 2)))
        self.assertEqual(self.j.db.execute('SELECT revision FROM reconciliation_barrier').fetchone()[0], 2)
        self.assertTrue(results[1]['matched'])
        self.assertEqual(self.j.get('d1')['filled_quantity'], 4)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertTrue(self.apply(revision=3)['matched'])

    def test_empty_snapshot_cannot_erase_fills_or_scope(self):
        self.assertFalse(self.apply([])['matched'])
        self.assertEqual(self.j.get('d1')['filled_quantity'], 4)
        self.assert_blocked()


if __name__ == '__main__':
    unittest.main()
