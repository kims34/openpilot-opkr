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


if __name__=='__main__':
    unittest.main()
