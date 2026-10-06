import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from order_intent_journal import OrderIntentJournal
from order_snapshot_reconciliation import reconcile_order_snapshot_batch
from indexalert_automation_control import AutomationCapitalState, AutomationUserControls
from shadow_capital_allocator import ShadowCapitalAllocator
from shadow_operational_status import inspect_shadow_operational_status


class OperationalStatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'private-account.sqlite'
        self.journal = OrderIntentJournal(self.path)
        self.capital = ShadowCapitalAllocator(self.journal)
        self.capital.configure(controls=AutomationUserControls(True,100),
            baseline=AutomationCapitalState(0,0),expected_revision=0)
        reconcile_order_snapshot_batch(self.journal,revision=1,orders=[])

    def tearDown(self):
        self.journal.close()
        self.tmp.cleanup()

    def inspect(self):
        return inspect_shadow_operational_status(self.path)

    def claim(self):
        self.journal.register('PRIVATE-INTENT',symbol='PRIVATE-SYMBOL',side='BUY',quantity=10)
        epoch = self.journal.enable_shadow(expected_epoch=self.journal.shadow_control()['epoch'])['epoch']
        self.capital.reserve_and_claim_buy('PRIVATE-INTENT',limit_price_krw=8,fee_buffer_krw=3,
            expected_epoch=epoch,expected_capital_revision=1)

    def test_live_shadow_inspection_never_runs_recovery_or_mutates(self):
        self.claim()
        before = self.journal.shadow_control(),self.journal.get('PRIVATE-INTENT'),self.journal.db.total_changes
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            result = self.inspect()
        after = self.journal.shadow_control(),self.journal.get('PRIVATE-INTENT'),self.journal.db.total_changes
        self.assertEqual(before,after)
        self.assertTrue(result['diagnostics_complete'])
        self.assertEqual(result['shadow_mode'],'SHADOW')
        self.assertEqual(result['unresolved_intent_count'],1)
        self.assertEqual(result['capital']['managed_reserve_krw'],83)
        self.assertFalse(result['real_orders_authorized'])
        self.assertFalse(result['exact_policy_shadow_admitted'])

    def test_missing_database_is_not_created_and_error_is_private(self):
        path = Path(self.tmp.name)/'secret-missing.sqlite'
        result = inspect_shadow_operational_status(path)
        self.assertFalse(path.exists())
        self.assertFalse(result['diagnostics_complete'])
        self.assertNotIn(str(path),json.dumps(result))

    def test_report_omits_private_payloads_identifiers_and_path(self):
        self.claim()
        text = json.dumps(self.inspect())
        for value in ('PRIVATE-INTENT','PRIVATE-SYMBOL',str(self.path)):
            self.assertNotIn(value,text)

    def test_pending_conflicts_and_latch_are_visible(self):
        self.journal.db.executescript('''CREATE TABLE native_inbox_receipts(sequence INTEGER PRIMARY KEY);
            CREATE TABLE native_inbox_attempts(receipt_sequence INTEGER,outcome TEXT);
            CREATE TABLE native_inbox_conflicts(reason TEXT);
            INSERT INTO native_inbox_receipts VALUES(1);
            INSERT INTO native_inbox_conflicts VALUES('PRIVATE');''')
        self.journal.trip_kill_switch()
        result = self.inspect()
        self.assertEqual(result['native_inbox_pending_count'],1)
        self.assertEqual(result['native_inbox_conflict_count'],1)
        self.assertTrue({'KILL_SWITCH_LATCHED','NATIVE_INBOX_PENDING','NATIVE_INBOX_CONFLICTED'} <= set(result['local_blockers']))

    def test_incomplete_schema_is_unavailable_not_zero_pending(self):
        self.journal.db.execute('CREATE TABLE native_inbox_receipts(sequence INTEGER)')
        self.assertFalse(self.inspect()['diagnostics_complete'])

    def test_lowered_ceiling_preserves_and_reports_committed_reserve(self):
        self.claim()
        self.capital.configure(controls=AutomationUserControls(True,20),
            baseline=AutomationCapitalState(10,5),expected_revision=1)
        result = self.inspect()
        self.assertEqual(result['capital']['total_committed_krw'],98)
        self.assertIn('CAPITAL_CEILING_EXCEEDED',result['local_blockers'])

    def test_complete_local_view_does_not_admit_external_shadow_or_live(self):
        result = self.inspect()
        self.assertEqual(result['local_blockers'],[])
        self.assertFalse(result['exact_policy_shadow_admitted'])
        self.assertFalse(result['genuine_live_provenance_verified'])

    def reconcile_claimed(self):
        self.claim()
        self.journal.bind_acknowledgement('PRIVATE-INTENT','PRIVATE-ORDER')
        row = dict(key='PRIVATE-INTENT',broker_order_id='PRIVATE-ORDER',symbol='PRIVATE-SYMBOL',
            side='BUY',quantity=10,filled_quantity=0,status='OPEN')
        reconcile_order_snapshot_batch(self.journal,revision=2,orders=[row])
        return row

    def test_current_epoch_revision_cannot_hide_changed_snapshot_content(self):
        row = self.reconcile_claimed()
        self.assertEqual(self.inspect()['local_blockers'],[])
        for field,value in (('filled_quantity',1),('quantity',True),('symbol','OTHER-PRIVATE'),
                            ('status','FILLED'),('key','OTHER-PRIVATE')):
            self.journal.db.execute('UPDATE reconciled_snapshot_bindings SET payload=?',
                (json.dumps({**row,field:value}),))
            before = self.journal.shadow_control(),self.journal.db.total_changes
            result = self.inspect()
            self.assertTrue(result['diagnostics_complete'])
            self.assertEqual(result['stale_binding_count'],0)
            self.assertEqual(result['changed_binding_count'],1)
            self.assertIn('ORDER_SNAPSHOT_CONTENT_CHANGED',result['local_blockers'])
            self.assertFalse(result['real_orders_authorized'])
            self.assertNotIn('PRIVATE',json.dumps(result))
            self.assertEqual(before,(self.journal.shadow_control(),self.journal.db.total_changes))

    def test_unknown_binding_scope_and_decoder_exhaustion_are_private(self):
        row = self.reconcile_claimed()
        revision,epoch,payload = self.journal.db.execute(
            'SELECT revision,epoch,payload FROM reconciled_snapshot_bindings').fetchone()
        self.journal.db.execute('INSERT INTO reconciled_snapshot_bindings VALUES(?,?,?,?)',
            ('UNKNOWN-PRIVATE',revision,epoch,payload))
        result = self.inspect()
        self.assertIn('ORDER_SNAPSHOT_SCOPE_CHANGED',result['local_blockers'])
        self.assertNotIn('PRIVATE',json.dumps(result))
        self.journal.db.execute('DELETE FROM reconciled_snapshot_bindings WHERE key=?',('UNKNOWN-PRIVATE',))
        for payload in ('invalid private JSON','['*20000+'0'+']'*20000):
            self.journal.db.execute('UPDATE reconciled_snapshot_bindings SET payload=?',(payload,))
            result = self.inspect()
            self.assertIn('ORDER_SNAPSHOT_CONTENT_CHANGED',result['local_blockers'])
            self.assertEqual(result['changed_binding_count'],1)
        self.journal.db.execute('UPDATE reconciled_snapshot_bindings SET payload=?',(json.dumps(row),))
        self.assertEqual(self.inspect()['local_blockers'],[])

    def test_corrupt_identity_is_unavailable_without_recovery_or_private_output(self):
        self.reconcile_claimed()
        for payload in ('{}','['*20000+'0'+']'*20000):
            self.journal.db.execute('UPDATE intents SET payload=?',(payload,))
            before = self.journal.shadow_control(),self.journal.db.total_changes
            result = self.inspect()
            self.assertFalse(result['diagnostics_complete'])
            self.assertEqual(result['local_blockers'],['OPERATIONAL_SNAPSHOT_UNAVAILABLE'])
            self.assertNotIn('PRIVATE',json.dumps(result))
            self.assertEqual(before,(self.journal.shadow_control(),self.journal.db.total_changes))

    def test_inconsistent_terminal_fact_is_unavailable_without_mutation(self):
        self.reconcile_claimed()
        self.journal.db.execute("UPDATE intents SET terminal_status='FILLED' WHERE key=?",
                                ('PRIVATE-INTENT',))
        before = self.journal.shadow_control(),self.journal.db.total_changes
        result = self.inspect()
        self.assertFalse(result['diagnostics_complete'])
        self.assertEqual(result['local_blockers'],['OPERATIONAL_SNAPSHOT_UNAVAILABLE'])
        self.assertNotIn('PRIVATE',json.dumps(result))
        self.assertEqual(before,(self.journal.shadow_control(),self.journal.db.total_changes))

    def test_corrupt_unclaimed_intent_is_not_hidden_from_status(self):
        self.journal.register('PRIVATE-UNCLAIMED',symbol='PRIVATE-SYMBOL',side='BUY',quantity=1)
        self.journal.db.execute("UPDATE intents SET payload=? WHERE key=?",
                                ('{\"symbol\":\"PRIVATE-SYMBOL\",\"side\":\"BUY\",\"quantity\":1,\"extra\":true}',
                                 'PRIVATE-UNCLAIMED'))
        before = self.journal.shadow_control(),self.journal.db.total_changes
        result = self.inspect()
        self.assertFalse(result['diagnostics_complete'])
        self.assertEqual(result['local_blockers'],['OPERATIONAL_SNAPSHOT_UNAVAILABLE'])
        self.assertNotIn('PRIVATE',json.dumps(result))
        self.assertEqual(before,(self.journal.shadow_control(),self.journal.db.total_changes))
