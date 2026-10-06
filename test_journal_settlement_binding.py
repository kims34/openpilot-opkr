"""Synthetic local lifecycle cases; never real account/provenance evidence."""
import os
import json
import tempfile
import unittest
from dataclasses import replace

from account_settlement_binding import (
    SettlementAdmission, SettlementBindingError, bind_journal_settlement_to_early_live,
)
from early_live_admission_gate import EarlyLiveAdmissionEvidence
from kiwoom_account_settlement_evidence import normalize_kt00001_settlement
from order_intent_journal import OrderIntentJournal
from order_snapshot_reconciliation import reconcile_order_snapshot_batch


class JournalSettlementBindingTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.root.name, 'synthetic.sqlite')
        self.journal = OrderIntentJournal(self.path)
        # Only synthetic scope. A stored identity never attests real origin.
        self.journal.db.execute('CREATE TABLE native_journal_scope (id INTEGER PRIMARY KEY, account TEXT, day TEXT)')
        self.journal.db.execute('INSERT INTO native_journal_scope VALUES(1,?,?)', ('sha256:'+'a'*64, '2026-10-06'))
        self.base = EarlyLiveAdmissionEvidence(True,True,True,0,0,True,True,True,True,True,True)
        self.admission = SettlementAdmission(True,True,True,True,0)
        self.snapshot = normalize_kt00001_settlement(
            {'entr':'100000','pymn_alow_amt':'90000','d2_entra':'95000','ord_alow_amt':'50000'},
            account_fingerprint='a'*64, captured_at='2026-10-06T10:00:00+09:00')
        self.rows = []
        self.reconcile()

    def tearDown(self):
        self.journal.close()
        self.root.cleanup()

    def reconcile(self):
        revision = self.journal.db.execute('SELECT revision FROM reconciliation_barrier').fetchone()[0]+1
        result = reconcile_order_snapshot_batch(self.journal, revision=revision, orders=self.rows)
        self.assertTrue(result['matched'])
        self.revision = revision
        self.epoch = self.journal.shadow_control()['epoch']

    def assess(self, **changes):
        args = dict(base=self.base, settlement=self.admission, snapshot=self.snapshot,
                    journal=self.journal, expected_epoch=self.epoch, expected_snapshot_revision=self.revision)
        args.update(changes)
        return bind_journal_settlement_to_early_live(**args)

    def claimed(self):
        self.journal.register('synthetic-intent', symbol='005930', side='BUY', quantity=10)
        enabled = self.journal.enable_shadow(expected_epoch=self.epoch)
        self.journal.claim_submission('synthetic-intent', expected_epoch=enabled['epoch'])

    def acknowledged(self):
        self.claimed()
        self.journal.bind_acknowledgement('synthetic-intent', 'synthetic-order')
        self.rows = [dict(key='synthetic-intent',broker_order_id='synthetic-order',symbol='005930',
                          side='BUY',quantity=10,filled_quantity=0,status='OPEN')]
        self.reconcile()

    def test_reconciled_scope_reaches_structural_boundary_only(self):
        self.acknowledged()
        before = self.journal.db.total_changes
        out = self.assess()
        self.assertTrue(out['account_settlement_admitted'])
        self.assertTrue(out['preconditions_structurally_satisfied'])
        self.assertFalse(out['independent_gate_admission_verified'])
        self.assertFalse(out['ready_for_final_user_authorization'])
        self.assertIn('INDEPENDENT_GATE_ADMISSION_NOT_IMPLEMENTED', out['blockers'])
        self.assertEqual(self.journal.db.total_changes, before)
        for flag in ('real_orders_authorized','early_live_authorized','broker_request_sent',
                     'genuine_live_provenance_verified','funds_movement_authorized'):
            self.assertFalse(out[flag])

    def test_declared_zero_cannot_hide_durable_unknown_submission(self):
        self.claimed()
        out = self.assess()
        self.assertEqual(out['durable_unresolved_reconciliation_count'], 1)
        self.assertFalse(out['ready_for_final_user_authorization'])

    def test_reconnect_invalidates_previously_matched_snapshot(self):
        self.acknowledged()
        self.journal.close()
        self.journal = OrderIntentJournal(self.path)
        self.assertFalse(self.assess()['ready_for_final_user_authorization'])

    def test_late_execution_invalidates_zero_fill_settlement_view(self):
        self.acknowledged()
        self.journal.record_execution('synthetic-intent', broker_order_id='synthetic-order',
                                      execution_id='synthetic-fill', quantity=2)
        out = self.assess()
        self.assertFalse(out['account_settlement_admitted'])
        self.assertTrue(out['local_reconciliation_errors'])

    def test_stored_binding_extra_content_cannot_reach_authorization_boundary(self):
        self.acknowledged()
        before = self.journal.db.total_changes
        payload = json.loads(self.journal.db.execute(
            'SELECT payload FROM reconciled_snapshot_bindings').fetchone()[0])
        payload['unexpected_unreviewed_field'] = 'tampered'
        self.journal.db.execute('UPDATE reconciled_snapshot_bindings SET payload=?',
                                (json.dumps(payload),))
        modified = self.journal.db.total_changes
        out = self.assess()
        self.assertFalse(out['ready_for_final_user_authorization'])
        self.assertFalse(out['account_settlement_admitted'])
        self.assertIn('ORDER_SNAPSHOT_CONTENT_CHANGED',out['local_reconciliation_errors'])
        self.assertEqual(self.journal.db.total_changes,modified)
        self.assertGreater(modified,before)

    def test_stored_intent_extra_content_cannot_reach_authorization_boundary(self):
        self.acknowledged()
        payload = json.loads(self.journal.db.execute(
            'SELECT payload FROM intents WHERE key=?',('synthetic-intent',)).fetchone()[0])
        payload['unexpected_unreviewed_field'] = 'tampered'
        self.journal.db.execute('UPDATE intents SET payload=? WHERE key=?',
                                (json.dumps(payload),'synthetic-intent'))
        modified = self.journal.db.total_changes
        out = self.assess()
        self.assertFalse(out['ready_for_final_user_authorization'])
        self.assertFalse(out['account_settlement_admitted'])
        self.assertIn('ORDER_SNAPSHOT_CONTENT_CHANGED',out['local_reconciliation_errors'])
        self.assertEqual(self.journal.db.total_changes,modified)

    def test_inconsistent_terminal_fact_cannot_reach_authorization_boundary(self):
        self.acknowledged()
        self.journal.db.execute("UPDATE intents SET terminal_status='FILLED' WHERE key=?",
                                ('synthetic-intent',))
        modified = self.journal.db.total_changes
        out = self.assess()
        self.assertFalse(out['ready_for_final_user_authorization'])
        self.assertFalse(out['account_settlement_admitted'])
        self.assertIn('ORDER_SNAPSHOT_CONTENT_CHANGED',out['local_reconciliation_errors'])
        self.assertEqual(self.journal.db.total_changes,modified)

    def test_mismatched_account_or_korean_day_blocks(self):
        for snapshot in (replace(self.snapshot,account_fingerprint='b'*64),
                         replace(self.snapshot,captured_at='2026-10-07T00:00:00+09:00')):
            out = self.assess(snapshot=snapshot)
            self.assertFalse(out['ready_for_final_user_authorization'])
            self.assertIn('ACCOUNT_DATE_SCOPE_UNBOUND', out['local_reconciliation_errors'])

    def test_unattested_source_never_becomes_admitted_from_local_match(self):
        out = self.assess(settlement=SettlementAdmission())
        self.assertFalse(out['account_settlement_admitted'])
        self.assertFalse(out['ready_for_final_user_authorization'])

    def test_inbox_conflict_blocks_even_when_all_external_flags_are_true(self):
        self.journal.db.execute('CREATE TABLE native_inbox_receipts(sequence INTEGER PRIMARY KEY)')
        self.journal.db.execute('CREATE TABLE native_inbox_attempts(receipt_sequence INTEGER,outcome TEXT)')
        self.journal.db.execute('CREATE TABLE native_inbox_conflicts(reason TEXT)')
        self.journal.db.execute("INSERT INTO native_inbox_receipts VALUES(1)")
        self.assertFalse(self.assess()['account_settlement_admitted'])
        self.journal.db.execute("INSERT INTO native_inbox_attempts VALUES(1,'APPLIED')")
        self.journal.db.execute("INSERT INTO native_inbox_conflicts VALUES('SYNTHETIC')")
        self.assertFalse(self.assess()['account_settlement_admitted'])

    def test_kill_latch_cannot_be_hidden_by_fresh_matched_batch(self):
        self.journal.trip_kill_switch()
        self.reconcile()
        out = self.assess()
        self.assertFalse(out['ready_for_final_user_authorization'])
        self.assertIn('KILL_SWITCH_LATCHED', out['local_reconciliation_errors'])

    def test_invalid_scope_inputs_fail_closed(self):
        for snapshot in (replace(self.snapshot,captured_at='not-a-dateZ'),
                         replace(self.snapshot,captured_at='2026-10-06T10:00:00'),
                         replace(self.snapshot,account_fingerprint='arbitrary-identity')):
            with self.assertRaises(SettlementBindingError):
                self.assess(snapshot=snapshot)
        with self.assertRaises(SettlementBindingError):
            self.assess(expected_epoch=True)

    def test_korean_date_overflow_is_blocked_before_journal_transaction(self):
        from unittest.mock import patch
        before = self.journal.shadow_control(),self.journal.db.total_changes
        for timestamp in ('9999-12-31T23:00:00Z','0001-01-01T00:00:00+23:00'):
            with patch.object(self.journal,'_atomic',side_effect=AssertionError('must not transact')):
                with self.assertRaises(SettlementBindingError):
                    self.assess(snapshot=replace(self.snapshot,captured_at=timestamp))
        self.assertEqual(before,(self.journal.shadow_control(),self.journal.db.total_changes))

    def test_cashflow_composition_vetoes_unexplained_balance(self):
        from account_cashflow_reconciliation import (
            reconcile_settled_cashflow, bind_reconciled_cashflow_to_early_live,
        )
        from decimal import Decimal
        opening = replace(self.snapshot, captured_at='2026-10-06T09:00:00+09:00',
                          deposit_cash_krw=Decimal('100001'))
        cashflow = reconcile_settled_cashflow(opening, self.snapshot, [],
            complete_settlement_scope_attested=True, signed_net_mapping_attested=True,
            fees_tax_completeness_attested=True)
        out = bind_reconciled_cashflow_to_early_live(self.base, self.admission,
            self.snapshot, self.journal, cashflow, expected_epoch=self.epoch,
            expected_snapshot_revision=self.revision)
        self.assertFalse(out['ready_for_final_user_authorization'])
        self.assertFalse(out['account_settlement_admitted'])

    def test_cashflow_report_cannot_be_reused_for_another_snapshot(self):
        from account_cashflow_reconciliation import (
            CashflowReconciliationError, reconcile_settled_cashflow,
            bind_reconciled_cashflow_to_early_live,
        )
        opening = replace(self.snapshot, captured_at='2026-10-06T09:00:00+09:00')
        cashflow = reconcile_settled_cashflow(opening, self.snapshot, [],
            complete_settlement_scope_attested=True, signed_net_mapping_attested=True,
            fees_tax_completeness_attested=True)
        other = replace(self.snapshot, captured_at='2026-10-06T10:01:00+09:00')
        with self.assertRaises(CashflowReconciliationError):
            bind_reconciled_cashflow_to_early_live(self.base, self.admission,
                other, self.journal, cashflow, expected_epoch=self.epoch,
                expected_snapshot_revision=self.revision)


if __name__ == '__main__':
    unittest.main()
