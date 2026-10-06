import tempfile
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from indexalert_automation_control import AutomationCapitalState, AutomationUserControls
from order_intent_journal import OrderIntentJournal, OrderJournalError
from order_snapshot_reconciliation import reconcile_order_snapshot_batch
from shadow_capital_allocator import ShadowCapitalAllocator


class PrincipalReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'synthetic.sqlite'
        self.j=OrderIntentJournal(self.path)
        self.a=ShadowCapitalAllocator(self.j)
        self.a.configure(controls=AutomationUserControls(True,100),
            baseline=AutomationCapitalState(0,0),expected_revision=0)
        self.j.register('d1',symbol='SYNTHETIC',side='BUY',quantity=10)
        epoch=self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])['epoch']
        self.a.reserve_and_claim_buy('d1',limit_price_krw=8,fee_buffer_krw=3,
            expected_epoch=epoch,expected_capital_revision=1)
        self.j.bind_acknowledgement('d1','o1')

    def tearDown(self):
        self.j.close()
        self.tmp.cleanup()

    def batch(self,status='CANCELLED',filled=0,revision=1):
        return reconcile_order_snapshot_batch(self.j,revision=revision,orders=[
            dict(key='d1',broker_order_id='o1',symbol='SYNTHETIC',side='BUY',
                quantity=10,filled_quantity=filled,status=status)])

    def release(self, **overrides):
        args=dict(expected_epoch=self.j.shadow_control()['epoch'],
            expected_capital_revision=self.a.state()['revision'],expected_snapshot_revision=1)
        args.update(overrides)
        return self.a.release_zero_fill_principal('d1',**args)

    def test_whole_batch_zero_fill_cancel_returns_principal_keeps_fee_and_stays_off(self):
        self.assertTrue(self.batch()['matched'])
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            out=self.release()
        self.assertEqual(out['released_principal_krw'],80)
        self.assertEqual(out['retained_fee_buffer_krw'],3)
        self.assertEqual(self.a.state()['managed_reserve_krw'],3)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.assertFalse(out['funds_movement_attempted'])
        self.assertFalse(out['live_ordering_authorized'])
        self.j.register('d2',symbol='OTHER',side='BUY',quantity=12)
        epoch=self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])['epoch']
        self.a.reserve_and_claim_buy('d2',limit_price_krw=8,fee_buffer_krw=0,
            expected_epoch=epoch,expected_capital_revision=self.a.state()['revision'])
        self.assertEqual(self.a.state()['managed_reserve_krw'],99)

    def test_zero_fill_rejection_can_return_only_principal(self):
        self.assertTrue(self.batch(status='REJECTED')['matched'])
        self.assertEqual(self.release()['retained_fee_buffer_krw'],3)

    def test_corrupt_unreleased_reservation_cannot_create_principal_credit(self):
        self.assertTrue(self.batch()['matched'])
        for price, fee, total in ((8,-7,83), (8,84,83), (0,3,83),
                                 (8,3,82), (8,3,84), (8,3,83.5), (8.5,3,88)):
            with self.subTest(price=price, fee=fee, total=total):
                self.j.db.execute('UPDATE shadow_capital_reservations SET limit_price=?,fee_buffer=?,reserve=?',
                    (price,fee,total))
                before = tuple(self.j.db.iterdump())
                with self.assertRaises(OrderJournalError):
                    self.release()
                self.assertEqual(tuple(self.j.db.iterdump()), before)
        self.j.db.execute('UPDATE shadow_capital_reservations SET limit_price=8,fee_buffer=3,reserve=83')
        self.assertEqual(self.release()['released_principal_krw'], 80)

    def test_cancel_request_or_individual_snapshot_cannot_release(self):
        self.j.mark_cancel_requested('d1')
        with self.assertRaises(OrderJournalError): self.release()
        self.j.reconcile_snapshot('d1',broker_order_id='o1',status='CANCELLED',filled_quantity=0)
        with self.assertRaises(OrderJournalError): self.release()
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)

    def test_partial_fill_cancel_retains_entire_reservation(self):
        self.j.record_execution('d1',broker_order_id='o1',execution_id='e1',quantity=4)
        self.assertTrue(self.batch(filled=4)['matched'])
        with self.assertRaises(OrderJournalError): self.release()
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)

    def test_corrupt_matching_zero_fill_view_cannot_release_retained_execution_principal(self):
        self.j.record_execution('d1', broker_order_id='o1', execution_id='e1', quantity=4)
        self.assertTrue(self.batch(filled=4)['matched'])
        self.j.db.execute('UPDATE intents SET filled=0')
        row = json.loads(self.j.db.execute('SELECT payload FROM reconciled_snapshot_bindings').fetchone()[0])
        row['filled_quantity'] = 0
        self.j.db.execute('UPDATE reconciled_snapshot_bindings SET payload=?', (json.dumps(row),))
        with self.assertRaises(OrderJournalError):
            self.release()
        self.assertEqual(self.a.state()['managed_reserve_krw'], 83)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM shadow_capital_releases').fetchone(), (0,))
        self.assertEqual(self.j.db.execute('SELECT quantity FROM executions').fetchone(), (4,))

    def test_malformed_stored_release_snapshot_cannot_credit_principal(self):
        self.assertTrue(self.batch()['matched'])
        snapshot = json.loads(self.j.db.execute('SELECT payload FROM reconciled_snapshot_bindings').fetchone()[0])
        malformed = [json.dumps(dict(snapshot, filled_quantity=False)),
            json.dumps(dict(snapshot, quantity=10.0)), json.dumps(dict(snapshot, key='other')),
            '{"filled_quantity":9,' + json.dumps(snapshot)[1:], '[' * 20000 + '0' + ']' * 20000]
        for payload in malformed:
            with self.subTest(kind='depth' if payload.startswith('[') else 'object'):
                self.j.db.execute('UPDATE reconciled_snapshot_bindings SET payload=?', (payload,))
                with self.assertRaises(OrderJournalError):
                    self.release()
                self.assertEqual(self.a.state()['managed_reserve_krw'], 83)
                self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM shadow_capital_releases').fetchone(), (0,))

    def test_full_fill_cannot_be_treated_as_zero_fill_release(self):
        self.j.record_execution('d1',broker_order_id='o1',execution_id='e1',quantity=10)
        self.assertTrue(self.batch(status='FILLED',filled=10)['matched'])
        with self.assertRaises(OrderJournalError): self.release()
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)

    def test_late_fill_after_snapshot_blocks_principal_release(self):
        self.batch()
        self.j.record_execution('d1',broker_order_id='o1',execution_id='late',quantity=1)
        with self.assertRaises(OrderJournalError): self.release()
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)

    def test_restart_requires_a_new_batch_even_when_terminal_order_unchanged(self):
        self.batch()
        self.j.close()
        self.j=OrderIntentJournal(self.path)
        self.a=ShadowCapitalAllocator(self.j)
        with self.assertRaises(OrderJournalError): self.release()
        self.assertTrue(self.batch(revision=2)['matched'])
        self.release(expected_snapshot_revision=2)
        self.assertEqual(self.a.state()['managed_reserve_krw'],3)

    def test_repeated_release_never_credits_principal_twice(self):
        self.batch()
        self.release()
        self.batch(revision=2)
        with self.assertRaises(OrderJournalError): self.release(expected_snapshot_revision=2)
        self.assertEqual(self.a.state()['managed_reserve_krw'],3)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM shadow_capital_releases').fetchone()[0],1)

    def test_failed_batch_clears_prior_settlement_bindings(self):
        self.batch()
        reconcile_order_snapshot_batch(self.j,revision=2,orders=[])
        with self.assertRaises(OrderJournalError): self.release(expected_snapshot_revision=2)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM reconciled_snapshot_bindings').fetchone()[0],0)
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)

    def test_stale_boolean_or_future_revisions_cannot_release(self):
        self.batch()
        for revision in (True,0,2,'1'):
            with self.assertRaises(OrderJournalError): self.release(expected_snapshot_revision=revision)
        with self.assertRaises(OrderJournalError): self.release(expected_capital_revision=0)
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)

    def test_enabled_or_reconfigured_state_requires_new_off_snapshot(self):
        self.batch()
        self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])
        with self.assertRaises(OrderJournalError): self.release()
        self.a.configure(controls=AutomationUserControls(True,100),
            baseline=AutomationCapitalState(0,0),expected_revision=self.a.state()['revision'])
        with self.assertRaises(OrderJournalError): self.release()
        self.assertTrue(self.batch(revision=2)['matched'])
        self.release(expected_snapshot_revision=2)


if __name__=='__main__': unittest.main()
