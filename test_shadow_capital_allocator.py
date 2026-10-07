import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

from indexalert_automation_control import AutomationCapitalState, AutomationUserControls, AutomationControlError
from order_intent_journal import OrderIntentJournal, OrderJournalError
from order_snapshot_reconciliation import reconcile_order_snapshot_batch
from shadow_capital_allocator import ShadowCapitalAllocator


class ShadowCapitalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'synthetic.sqlite'
        self.j = OrderIntentJournal(self.path)
        self.a = ShadowCapitalAllocator(self.j)
        self.j.register('d1', symbol='SYNTHETIC', side='BUY', quantity=10)
        self.configure()

    def tearDown(self):
        self.j.close()
        self.tmp.cleanup()

    def configure(self, enabled=True, maximum=100, baseline=None):
        self.a.configure(controls=AutomationUserControls(enabled, maximum),
            baseline=baseline or AutomationCapitalState(0, 0),
            expected_revision=self.a.state()['revision'])
        self.epoch = self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])['epoch']

    def claim(self, key='d1', price=8, fee=0, epoch=None, revision=None):
        return self.a.reserve_and_claim_buy(key, limit_price_krw=price, fee_buffer_krw=fee,
            expected_epoch=self.epoch if epoch is None else epoch,
            expected_capital_revision=self.a.state()['revision'] if revision is None else revision)

    def ack(self):
        self.j.bind_acknowledgement('d1','o1')

    def test_complete_capital_schema_loss_cannot_become_fresh_or_skip_reservation(self):
        for table in ('shadow_capital_config','shadow_capital_reservations','shadow_capital_releases'):
            self.j.db.execute(f'DROP TABLE {table}')
        with self.assertRaisesRegex(OrderJournalError, 'component history missing'):
            self.j.claim_submission('d1',expected_epoch=self.epoch)
        with self.assertRaisesRegex(OrderJournalError, 'component history missing'):
            self.j.enable_shadow(expected_epoch=self.epoch)
        with self.assertRaisesRegex(OrderJournalError, '^startup capital history missing$'):
            ShadowCapitalAllocator(self.j)
        with self.assertRaisesRegex(OrderJournalError, '^startup safety metadata missing$'):
            OrderIntentJournal(self.path)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.get('d1')['state'], 'INTENT_CREATED')
        self.assertEqual(self.j.db.execute('SELECT component FROM journal_component_history').fetchall(), [('capital',)])
        self.assertIsNone(self.j.db.execute("SELECT 1 FROM sqlite_master WHERE name='shadow_capital_config'").fetchone())

    def test_legacy_complete_capital_schema_backfills_component_history(self):
        self.claim(fee=3)
        self.j.db.execute('DROP TABLE journal_component_history')
        self.j.db.execute('PRAGMA user_version=0')  # Actual pre-registry schema.
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        self.a = ShadowCapitalAllocator(self.j)
        self.assertEqual(self.a.state()['managed_reserve_krw'], 83)
        self.assertEqual(self.a.state()['revision'], 1)
        self.assertEqual(self.j.db.execute('SELECT component FROM journal_component_history').fetchall(), [('capital',)])

    def test_reinitialization_does_not_reset_deleted_capital_configuration(self):
        self.claim(fee=3)
        self.j.db.execute('DELETE FROM shadow_capital_config')
        with self.assertRaisesRegex(OrderJournalError, '^startup capital history missing$'):
            ShadowCapitalAllocator(self.j)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM shadow_capital_config').fetchone(), (0,))
        self.assertEqual(self.j.db.execute('SELECT reserve FROM shadow_capital_reservations').fetchone(), (83,))
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')

    def test_reinitialization_does_not_recreate_dropped_capital_history(self):
        self.claim(fee=3)
        self.j.trip_kill_switch()
        self.j.db.execute('DROP TABLE shadow_capital_releases')
        with self.assertRaisesRegex(OrderJournalError, '^startup capital history missing$'):
            ShadowCapitalAllocator(self.j)
        self.assertIsNone(self.j.db.execute("SELECT 1 FROM sqlite_master WHERE name='shadow_capital_releases'").fetchone())
        self.assertEqual(self.j.db.execute('SELECT reserve FROM shadow_capital_reservations').fetchone(), (83,))
        self.assertTrue(self.j.shadow_control()['killed'])

    def test_reservation_includes_quantity_price_fee_and_no_broker_request(self):
        with patch('socket.socket', side_effect=AssertionError('network forbidden')):
            out = self.claim(fee=3)
        self.assertEqual(out['reservation_krw'], 83)
        self.assertEqual(self.a.state()['managed_reserve_krw'], 83)
        self.assertEqual(out['intent']['state'], 'SUBMITTING')
        self.assertFalse(out['live_ordering_authorized'])
        self.assertFalse(out['account_capital_provenance_verified'])

    def test_existing_positions_external_orders_uncertainty_and_fees_count(self):
        self.configure(baseline=AutomationCapitalState(10, 5, 5, 1))
        with self.assertRaises(AutomationControlError):
            self.claim()
        self.assertEqual(self.a.state()['managed_reserve_krw'], 0)
        self.assertEqual(self.j.get('d1')['state'], 'INTENT_CREATED')

    def test_pending_reservations_prevent_overlapping_capital_allocation(self):
        self.claim()
        self.ack()
        self.j.register('d2', symbol='OTHER', side='BUY', quantity=10)
        with self.assertRaises(AutomationControlError):
            self.claim('d2')
        self.assertEqual(self.j.get('d2')['state'], 'INTENT_CREATED')
        self.assertEqual(self.a.state()['managed_reserve_krw'], 80)

    def test_corrupt_existing_reservation_cannot_free_capacity_for_another_buy(self):
        self.claim()
        self.ack()
        self.j.register('d2', symbol='OTHER', side='BUY', quantity=10)
        for amount in (1, -80, 80.5):
            with self.subTest(amount=amount):
                self.j.db.execute('UPDATE shadow_capital_reservations SET reserve=?', (amount,))
                before = tuple(self.j.db.iterdump())
                with self.assertRaises(OrderJournalError):
                    self.a.reserve_and_claim_buy('d2',limit_price_krw=8,fee_buffer_krw=0,
                        expected_epoch=self.epoch,expected_capital_revision=1)
                self.assertEqual(tuple(self.j.db.iterdump()), before)
                self.assertEqual(self.j.get('d2')['state'], 'INTENT_CREATED')
        self.j.db.execute('UPDATE shadow_capital_reservations SET reserve=80')
        self.assertEqual(self.a.state()['managed_reserve_krw'], 80)

    def test_failed_claim_rolls_back_its_reservation(self):
        self.j.trip_kill_switch()
        with self.assertRaises(OrderJournalError):
            self.claim()
        self.assertEqual(self.a.state()['managed_reserve_krw'], 0)
        self.assertEqual(self.j.get('d1')['state'], 'INTENT_CREATED')

    def test_stale_capital_revision_or_safety_epoch_cannot_claim(self):
        old_revision, old_epoch = self.a.state()['revision'], self.epoch
        self.configure(maximum=50)
        for kwargs in ({'revision':old_revision}, {'epoch':old_epoch}):
            with self.assertRaises((OrderJournalError, AutomationControlError)):
                self.claim(price=4, **kwargs)
        self.assertEqual(self.a.state()['managed_reserve_krw'], 0)

    def test_lowering_limit_or_disabled_control_does_not_release_reservations(self):
        self.claim()
        self.ack()
        self.configure(enabled=False, maximum=20)
        self.assertEqual(self.a.state()['managed_reserve_krw'], 80)
        self.j.register('d2',symbol='OTHER',side='BUY',quantity=1)
        with self.assertRaises(AutomationControlError):
            self.claim('d2', price=1)

    def test_legacy_claim_entry_cannot_skip_reservation_after_allocator_initialization(self):
        with self.assertRaisesRegex(OrderJournalError, 'reservation'):
            self.j.claim_submission('d1', expected_epoch=self.epoch)
        self.assertEqual(self.j.get('d1')['state'], 'INTENT_CREATED')

    def test_duplicate_claim_cannot_retry_or_reprice_existing_reservation(self):
        self.claim()
        self.ack()
        with self.assertRaises(OrderJournalError):
            self.claim(price=1)
        self.assertEqual(self.a.state()['managed_reserve_krw'],80)

    def test_ack_cancel_partial_and_terminal_fill_never_implicitly_release_cash(self):
        self.claim()
        self.ack()
        self.j.record_execution('d1',broker_order_id='o1',execution_id='e1',quantity=4)
        self.j.mark_cancel_requested('d1')
        self.assertEqual(self.a.state()['managed_reserve_krw'],80)
        self.j.reconcile_snapshot('d1',broker_order_id='o1',status='CANCELLED',filled_quantity=4)
        self.j.record_execution('d1',broker_order_id='o1',execution_id='e2',quantity=6)
        self.assertEqual(self.a.state()['managed_reserve_krw'],80)
        self.assertEqual(self.j.get('d1')['filled_quantity'],10)

    def test_timeout_restart_preserves_reservation_without_auto_enable(self):
        self.claim()
        self.j.mark_uncertain('d1')
        self.j.close()
        self.j=OrderIntentJournal(self.path)
        self.a=ShadowCapitalAllocator(self.j)
        self.assertEqual(self.a.state()['managed_reserve_krw'],80)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        with self.assertRaises(OrderJournalError):
            self.claim()

    def test_batch_barrier_blocks_reservation_and_claim_as_one_transaction(self):
        reconcile_order_snapshot_batch(self.j,revision=1,orders=[{}])
        with self.assertRaises(OrderJournalError):
            self.claim()
        self.assertEqual(self.a.state()['managed_reserve_krw'],0)

    def test_invalid_values_and_overflow_cannot_mutate(self):
        for price,fee in ((True,0),(0,0),(-1,0),(1,-1),(1,True),(2**63,0)):
            with self.assertRaises(OrderJournalError):
                self.claim(price=price,fee=fee)
        self.assertEqual(self.a.state()['managed_reserve_krw'],0)

    def test_racing_workers_can_reserve_only_one_claim(self):
        self.j.register('d2',symbol='OTHER',side='BUY',quantity=10)
        ready, armed = Barrier(2), Barrier(2)
        shared={}
        def claim(key):
            j=OrderIntentJournal(self.path)
            a=ShadowCapitalAllocator(j)
            try:
                if ready.wait()==0:
                    shared['epoch']=j.enable_shadow(expected_epoch=j.shadow_control()['epoch'])['epoch']
                armed.wait()
                a.reserve_and_claim_buy(key,limit_price_krw=8,fee_buffer_krw=0,
                    expected_epoch=shared['epoch'],expected_capital_revision=a.state()['revision'])
                return True
            except (OrderJournalError,AutomationControlError):
                return False
            finally:
                j.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(claim,('d1','d2'))),1)
        self.assertEqual(self.a.state()['managed_reserve_krw'],80)

    def test_unreserved_legacy_open_buy_cannot_be_ignored(self):
        j=OrderIntentJournal(Path(self.tmp.name)/'legacy.sqlite')
        try:
            j.register('legacy',symbol='OLD',side='BUY',quantity=10)
            epoch=j.enable_shadow(expected_epoch=j.shadow_control()['epoch'])['epoch']
            j.claim_submission('legacy',expected_epoch=epoch)
            j.bind_acknowledgement('legacy','old-order')
            a=ShadowCapitalAllocator(j)
            a.configure(controls=AutomationUserControls(True,100),
                baseline=AutomationCapitalState(0,0),expected_revision=0)
            epoch=j.enable_shadow(expected_epoch=j.shadow_control()['epoch'])['epoch']
            j.register('new',symbol='NEW',side='BUY',quantity=1)
            with self.assertRaisesRegex(OrderJournalError,'legacy'):
                a.reserve_and_claim_buy('new',limit_price_krw=1,fee_buffer_krw=0,
                    expected_epoch=epoch,expected_capital_revision=1)
            self.assertEqual(a.state()['managed_reserve_krw'],0)
        finally:
            j.close()

    def test_allocator_default_is_disabled_and_configuration_does_not_auto_enable(self):
        j=OrderIntentJournal(Path(self.tmp.name)/'default.sqlite')
        try:
            a=ShadowCapitalAllocator(j)
            self.assertFalse(a.state()['controls'].automation_enabled)
            self.assertEqual(a.state()['controls'].max_automation_capital_krw,0)
            a.configure(controls=AutomationUserControls(True,100),
                baseline=AutomationCapitalState(0,0),expected_revision=0)
            self.assertEqual(j.shadow_control()['mode'],'MASTER_OFF')
        finally:
            j.close()

    def test_corrupt_stored_capital_configuration_blocks_claim_without_private_traceback(self):
        baseline_faults = ('[]', 'null', '[0,0,0,0,0]', '[false,0,0,0]',
            '[-1,0,0,0]', '[0.5,0,0,0]', '[NaN,0,0,0]',
            '[18446744073709551616,0,0,0]', '[' * 20000 + '0' + ']' * 20000)
        for baseline in baseline_faults:
            with self.subTest(kind='deep' if len(baseline)>100 else baseline):
                self.j.db.execute('UPDATE shadow_capital_config SET baseline=?', (baseline,))
                before = tuple(self.j.db.iterdump())
                with self.assertRaisesRegex(OrderJournalError, '^invalid shadow capital configuration$'):
                    self.a.reserve_and_claim_buy('d1',limit_price_krw=8,fee_buffer_krw=0,
                        expected_epoch=self.epoch,expected_capital_revision=1)
                self.assertEqual(tuple(self.j.db.iterdump()), before)
                self.assertEqual(self.j.get('d1')['state'], 'INTENT_CREATED')
        self.j.db.execute("UPDATE shadow_capital_config SET baseline='[0,0,0,0]'")
        for revision, maximum in ((-1,100), (1.5,100), (1,0), (1,-1), (1,99.5)):
            with self.subTest(revision=revision, maximum=maximum):
                self.j.db.execute('UPDATE shadow_capital_config SET revision=?,maximum=?', (revision,maximum))
                before = tuple(self.j.db.iterdump())
                with self.assertRaisesRegex(OrderJournalError, '^invalid shadow capital configuration$'):
                    self.a.reserve_and_claim_buy('d1',limit_price_krw=8,fee_buffer_krw=0,
                        expected_epoch=self.epoch,expected_capital_revision=1)
                self.assertEqual(tuple(self.j.db.iterdump()), before)
        self.j.db.execute('UPDATE shadow_capital_config SET revision=1,maximum=100')
        self.assertEqual(self.claim()['reservation_krw'], 80)


if __name__=='__main__':
    unittest.main()
