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

    def test_duplicate_stored_intent_fields_are_ambiguous_even_if_last_value_matches(self):
        for repeated in ('"quantity":1,', '"quantity":10,', '"side":"SELL",', '"symbol":"OTHER",'):
            with self.subTest(repeated=repeated):
                payload = '{' + repeated + '"symbol":"005930","side":"BUY","quantity":10}'
                self.j.db.execute('UPDATE intents SET payload=? WHERE key=?', (payload, 'decision-1'))
                with self.assertRaises(OrderJournalError):
                    self.j.get('decision-1')

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

    def test_corrupt_execution_total_blocks_both_duplicate_and_new_fill(self):
        self.acknowledged()
        self.fill()
        self.j.db.execute('UPDATE intents SET filled=3')
        for execution, quantity in (('fill-1',4), ('later',1)):
            with self.subTest(execution=execution), self.assertRaises(OrderJournalError):
                self.fill(execution,quantity)
            self.assertEqual(self.j.db.execute('SELECT COUNT(*),SUM(quantity) FROM executions').fetchone(), (1,4))
            self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
            self.assertEqual(self.j.get('decision-1')['state'], 'RECONCILIATION_REQUIRED')

    def test_orphan_execution_blocks_another_fill_without_discarding_existing_records(self):
        self.acknowledged()
        self.fill()
        self.j.db.execute("INSERT INTO executions VALUES('orphan','orphan-fill',1)")
        with self.assertRaises(OrderJournalError):
            self.fill('later',1)
        self.assertEqual(self.j.get('decision-1')['filled_quantity'], 4)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone(), (2,))
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')

    def test_corrupt_execution_totals_block_enable_claim_and_kill_reset(self):
        self.acknowledged()
        self.fill()
        self.j.db.execute('UPDATE intents SET filled=3')
        self.j.register('decision-2',symbol='OTHER',side='BUY',quantity=1)
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('decision-2',expected_epoch=self.j.shadow_control()['epoch'])
        self.assertEqual(self.j.get('decision-2')['state'], 'INTENT_CREATED')
        self.j.disable_shadow()
        with self.assertRaises(OrderJournalError):
            self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])
        self.j.trip_kill_switch()
        with self.assertRaises(OrderJournalError):
            self.j.reset_kill_switch(expected_epoch=self.j.shadow_control()['epoch'])
        self.assertTrue(self.j.shadow_control()['killed'])
        self.assertEqual(self.j.db.execute('SELECT killed FROM shadow_control').fetchone(), (1,))
        self.assertEqual(self.j.db.execute('SELECT quantity FROM executions').fetchone(), (4,))

    def test_malformed_intent_cannot_be_claimed_before_return_validation(self):
        payload = '{"side":"BUY","quantity":10,"quantity":1,"symbol":"005930"}'
        self.j.db.execute('UPDATE intents SET payload=?', (payload,))
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('decision-1',expected_epoch=self.j.shadow_control()['epoch'])
        self.assertEqual(self.j.db.execute('SELECT state,payload FROM intents').fetchone(), ('INTENT_CREATED',payload))

    def test_exhausted_epoch_stops_without_float_nonce_reuse_or_kill_reset(self):
        self.j.db.execute('UPDATE shadow_control SET epoch=?', (2**63-1,))
        out = self.j.disable_shadow()
        self.assertEqual(out['epoch'], 2**63-1)
        self.assertIs(type(out['epoch']), int)
        self.assertEqual(out['mode'], 'MASTER_OFF')
        with self.assertRaises(OrderJournalError):
            self.j.enable_shadow(expected_epoch=2**63-1)
        self.j.trip_kill_switch()
        with self.assertRaises(OrderJournalError):
            self.j.reset_kill_switch(expected_epoch=2**63-1)
        self.assertTrue(self.j.shadow_control()['killed'])

    def test_invalid_float_epoch_can_stop_but_cannot_authorize_claim(self):
        self.j.db.execute('UPDATE shadow_control SET epoch=?', (float(2**63),))
        with self.assertRaises(OrderJournalError):
            self.j.disable_shadow()
        self.assertEqual(self.j.db.execute('SELECT mode FROM shadow_control').fetchone(), ('MASTER_OFF',))
        with self.assertRaises(OrderJournalError):
            self.j.enable_shadow(expected_epoch=2**63)
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('decision-1',expected_epoch=2**63)
        self.assertEqual(self.j.get('decision-1')['state'], 'INTENT_CREATED')

    def test_upgraded_journal_missing_component_registry_is_not_legacy(self):
        self.j.trip_kill_switch()
        self.j.db.execute('DROP TABLE journal_component_history')
        with self.assertRaisesRegex(OrderJournalError, '^startup safety metadata missing$'):
            OrderIntentJournal(self.path)
        self.assertIsNone(self.j.db.execute("SELECT 1 FROM sqlite_master WHERE name='journal_component_history'").fetchone())
        self.assertEqual(self.j.db.execute('PRAGMA user_version').fetchone(), (1,))
        self.assertTrue(self.j.shadow_control()['killed'])

    def test_restart_does_not_recreate_deleted_kill_control(self):
        self.j.trip_kill_switch()
        self.j.db.execute('DELETE FROM shadow_control')
        with self.assertRaisesRegex(OrderJournalError, '^startup safety metadata missing$'):
            OrderIntentJournal(self.path)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM shadow_control').fetchone(), (0,))
        self.assertEqual(self.j.get('decision-1')['state'], 'INTENT_CREATED')

    def test_restart_missing_barrier_stays_off_and_retains_kill_without_new_revision(self):
        self.j.trip_kill_switch()
        self.j.db.execute('DELETE FROM reconciliation_barrier')
        with self.assertRaisesRegex(OrderJournalError, '^startup safety metadata missing$'):
            OrderIntentJournal(self.path)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM reconciliation_barrier').fetchone(), (0,))
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertTrue(self.j.shadow_control()['killed'])

    def test_restart_does_not_recreate_dropped_journal_history_tables(self):
        for tables in (('shadow_control',), ('reconciliation_barrier',),
                       ('intents',), ('executions',), ('reconciled_snapshot_bindings',),
                       ('shadow_control','reconciliation_barrier')):
            with self.subTest(tables=tables):
                path = Path(self.tmp.name) / ('-'.join(tables)+'.sqlite')
                journal = OrderIntentJournal(path)
                try:
                    journal.register('retained', symbol='OFFLINE', side='BUY', quantity=1)
                    journal.trip_kill_switch()
                    for table in tables:
                        journal.db.execute(f'DROP TABLE {table}')
                    with self.assertRaisesRegex(OrderJournalError, '^startup safety metadata missing$'):
                        OrderIntentJournal(path)
                    names = {r[0] for r in journal.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    self.assertTrue(set(tables).isdisjoint(names))
                    if 'intents' not in tables:
                        self.assertEqual(journal.get('retained')['quantity'], 1)
                    if 'shadow_control' not in tables:
                        self.assertTrue(journal.shadow_control()['killed'])
                        self.assertEqual(journal.shadow_control()['mode'], 'MASTER_OFF')
                finally:
                    journal.close()

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
        self.assertEqual(out['state'], 'RECONCILIATION_REQUIRED')
        self.assertEqual(out['terminal_status'], 'FILLED')
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
