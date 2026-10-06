import json
import hashlib
from decimal import localcontext
import sqlite3
import unittest
from contextlib import contextmanager
from unittest.mock import patch

import test_kiwoom_order_journal_bridge as fixtures
import test_shadow_principal_release as capital_fixtures
from kiwoom_execution_inbox import KiwoomExecutionInbox, ExecutionInboxError
from kiwoom_order_journal_bridge import KiwoomOrderJournalBridge
from order_intent_journal import OrderIntentJournal, OrderJournalError
from order_snapshot_reconciliation import reconcile_order_snapshot_batch


class InboxTests(unittest.TestCase):
    tearDown = fixtures.BridgeTests.tearDown

    def setUp(self):
        fixtures.BridgeTests.setUp(self)
        self.i = KiwoomExecutionInbox(self.b)

    def append(self, receipt='receipt-1', row=None, key='d1'):
        return self.i.append(receipt,key,fixtures.fill() if row is None else row,trading_date=fixtures.DAY)

    def batch(self, filled=4, status='OPEN', revision=1):
        return reconcile_order_snapshot_batch(self.j,revision=revision,orders=[dict(
            key='d1',broker_order_id='native-order',symbol='005930',side='BUY',
            quantity=10,filled_quantity=filled,status=status)])

    def denied_enable(self):
        with self.assertRaises(OrderJournalError):
            self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])

    def test_persist_first_then_apply_without_network_and_no_auto_enable(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            self.append()
            self.assertEqual(self.j.get('d1')['filled_quantity'],0)
            self.assertEqual(self.i.counts()['pending'],1)
            self.denied_enable()
            self.assertTrue(self.i.replay_next()['executions_created'])
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertEqual(self.i.counts()['pending'],0)
        self.denied_enable()
        self.assertTrue(self.batch()['matched'])
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')

    def test_exact_receipt_duplicate_keeps_one_arrival_and_one_execution(self):
        self.append();self.append()
        self.assertEqual(self.i.counts()['receipts'],1)
        self.i.replay_next()
        self.assertFalse(self.i.replay('receipt-1')['executions_created'])
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertEqual(self.i.replay_next()['result'],'NO_PENDING_RECEIPT')

    def test_distinct_delivery_of_same_native_execution_is_still_idempotent(self):
        self.append();self.append('receipt-2')
        self.i.replay_next();self.i.replay_next()
        self.assertEqual(self.i.counts()['receipts'],2)
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)

    def test_distinct_receipt_cannot_hide_changed_price_under_low_precision(self):
        first=fixtures.fill();first.update(fill_price='100001',unit_fill_price='100001')
        changed=fixtures.fill();changed.update(fill_price='100002',unit_fill_price='100002')
        with localcontext() as context:
            context.prec=3
            self.append('first',first);self.i.replay_next()
            self.append('changed',changed)
            with self.assertRaises(ExecutionInboxError):self.i.replay_next()
        self.assertEqual(self.i.counts()['receipts'],2)
        self.assertEqual(self.i.counts()['pending'],1)
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone()[0],1)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.denied_enable()

    def test_reconnect_retains_pending_payload_and_native_id(self):
        self.append()
        self.j.close()
        self.j=OrderIntentJournal(self.path)
        self.b=KiwoomOrderJournalBridge(self.j,account_fingerprint=fixtures.ACCOUNT,trading_date=fixtures.DAY)
        self.i=KiwoomExecutionInbox(self.b)
        self.i.replay_next()
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertEqual(self.j.get('d1')['state'],'RECONCILIATION_REQUIRED')
        self.denied_enable()

    def test_restart_audit_rejects_corrupted_already_processed_receipt(self):
        self.append(); self.i.replay_next(); self.batch()
        self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])
        self.j.close()
        raw=sqlite3.connect(self.path,isolation_level=None)
        try:
            raw.execute('DROP TRIGGER native_inbox_receipts_update_immutable')
            raw.execute("UPDATE native_inbox_receipts SET payload=payload || ' ' WHERE receipt_id='receipt-1'")
        finally:
            raw.close()
        self.j=OrderIntentJournal(self.path)
        self.b=KiwoomOrderJournalBridge(self.j,account_fingerprint=fixtures.ACCOUNT,trading_date=fixtures.DAY)
        with self.assertRaises(ExecutionInboxError):
            KiwoomExecutionInbox(self.b)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(),(1,))
        self.assertEqual(self.j.get('d1')['state'],'RECONCILIATION_REQUIRED')

    def test_restart_audit_rejects_terminal_attempt_without_native_fill_binding(self):
        self.append(); self.i.replay_next(); self.batch()
        self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])
        self.j.close()
        raw=sqlite3.connect(self.path,isolation_level=None)
        try:
            raw.execute('DROP TRIGGER native_fill_bindings_delete_immutable')
            raw.execute("DELETE FROM native_fill_bindings WHERE key='d1'")
        finally:
            raw.close()
        self.j=OrderIntentJournal(self.path)
        self.b=KiwoomOrderJournalBridge(self.j,account_fingerprint=fixtures.ACCOUNT,trading_date=fixtures.DAY)
        with self.assertRaises(ExecutionInboxError):
            KiwoomExecutionInbox(self.b)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(),(1,))
        self.assertEqual(self.j.get('d1')['state'],'RECONCILIATION_REQUIRED')

    def test_restart_rejects_rehashed_processed_receipt_changed_price(self):
        self.append(); self.i.replay_next()
        self.j.close()
        raw = sqlite3.connect(self.path, isolation_level=None)
        try:
            raw.execute('DROP TRIGGER native_inbox_receipts_update_immutable')
            row = fixtures.fill()
            row.update(fill_price='101', unit_fill_price='101')
            payload = json.dumps(row, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
            raw.execute('UPDATE native_inbox_receipts SET payload=?,digest=?',
                (payload, hashlib.sha256(payload.encode()).hexdigest()))
        finally:
            raw.close()
        self.j = OrderIntentJournal(self.path)
        self.b = KiwoomOrderJournalBridge(self.j, account_fingerprint=fixtures.ACCOUNT, trading_date=fixtures.DAY)
        with self.assertRaises(ExecutionInboxError):
            KiwoomExecutionInbox(self.b)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(), (1,))
        self.assertEqual(self.j.get('d1')['filled_quantity'], 4)

    def test_restart_rejects_changed_execution_quantity_under_terminal_marker(self):
        self.append(); self.i.replay_next()
        self.j.close()
        raw = sqlite3.connect(self.path, isolation_level=None)
        try:
            raw.execute('DROP TRIGGER executions_update_immutable')
            raw.execute('UPDATE executions SET quantity=3')
        finally:
            raw.close()
        self.j = OrderIntentJournal(self.path)
        self.b = KiwoomOrderJournalBridge(self.j, account_fingerprint=fixtures.ACCOUNT, trading_date=fixtures.DAY)
        with self.assertRaises(ExecutionInboxError):
            KiwoomExecutionInbox(self.b)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(), (1,))

    def test_restart_rejects_binding_payload_changed_with_digest_untouched(self):
        self.append(); self.i.replay_next()
        self.j.close()
        raw = sqlite3.connect(self.path, isolation_level=None)
        try:
            raw.execute('DROP TRIGGER native_fill_bindings_update_immutable')
            raw.execute("UPDATE native_fill_bindings SET payload=payload || ' '")
        finally:
            raw.close()
        self.j = OrderIntentJournal(self.path)
        self.b = KiwoomOrderJournalBridge(self.j, account_fingerprint=fixtures.ACCOUNT, trading_date=fixtures.DAY)
        with self.assertRaises(ExecutionInboxError):
            KiwoomExecutionInbox(self.b)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(), (1,))

    def test_deep_durable_payload_quarantines_restart_with_private_error(self):
        self.append(); self.i.replay_next(); self.batch()
        self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])
        payload = '[' * 20000 + '0' + ']' * 20000
        self.j.db.execute('DROP TRIGGER native_inbox_receipts_update_immutable')
        self.j.db.execute('UPDATE native_inbox_receipts SET payload=?,digest=?',
            (payload, hashlib.sha256(payload.encode()).hexdigest()))
        with self.assertRaises(ExecutionInboxError) as raised:
            KiwoomExecutionInbox(self.b)
        self.assertEqual(str(raised.exception), 'EXECUTION_INBOX_RECONCILIATION_REQUIRED')
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(), (1,))
        self.assertEqual(self.j.get('d1')['filled_quantity'], 4)

    def test_deep_durable_payload_quarantines_replay_without_fill(self):
        self.append()
        payload = '[' * 20000 + '0' + ']' * 20000
        self.j.db.execute('DROP TRIGGER native_inbox_receipts_update_immutable')
        self.j.db.execute('UPDATE native_inbox_receipts SET payload=?,digest=?',
            (payload, hashlib.sha256(payload.encode()).hexdigest()))
        with self.assertRaises(ExecutionInboxError):
            self.i.replay_next()
        self.assertEqual(self.j.get('d1')['filled_quantity'], 0)
        self.assertEqual(self.i.counts()['pending'], 1)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')

    def test_restart_rejects_intent_fill_total_changed_under_processed_receipt(self):
        self.append(); self.i.replay_next()
        self.j.close()
        raw = sqlite3.connect(self.path, isolation_level=None)
        try:
            raw.execute('UPDATE intents SET filled=3')
        finally:
            raw.close()
        self.j = OrderIntentJournal(self.path)
        self.b = KiwoomOrderJournalBridge(self.j, account_fingerprint=fixtures.ACCOUNT, trading_date=fixtures.DAY)
        with self.assertRaises(ExecutionInboxError):
            KiwoomExecutionInbox(self.b)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(), (1,))
        self.assertEqual(self.j.db.execute('SELECT quantity FROM executions').fetchone(), (4,))

    def test_restart_rejects_duplicate_receipt_fields_even_when_last_value_matches(self):
        self.append(); self.i.replay_next()
        payload = '{"fill_price":"999",' + json.dumps(fixtures.fill())[1:]
        self.j.db.execute('DROP TRIGGER native_inbox_receipts_update_immutable')
        self.j.db.execute('UPDATE native_inbox_receipts SET payload=?,digest=?',
            (payload, hashlib.sha256(payload.encode()).hexdigest()))
        with self.assertRaises(ExecutionInboxError):
            KiwoomExecutionInbox(self.b)
        self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(), (1,))
        self.assertEqual(self.j.get('d1')['filled_quantity'], 4)

    def test_restart_after_later_fill_preserves_processed_receipt_identity(self):
        self.append(); self.i.replay_next()
        self.append('second', fixtures.fill('fill-2', 6, 0, '091502')); self.i.replay_next()
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        self.b = KiwoomOrderJournalBridge(self.j, account_fingerprint=fixtures.ACCOUNT, trading_date=fixtures.DAY)
        self.i = KiwoomExecutionInbox(self.b)
        self.assertEqual(self.i.counts()['pending'], 0)
        self.assertFalse(self.i.replay('receipt-1')['executions_created'])
        self.assertEqual(self.j.get('d1')['filled_quantity'], 10)

    def test_gap_retained_in_arrival_order_requires_explicit_missing_first_replay(self):
        self.append('second',fixtures.fill('fill-2',6,0,'091502'))
        with self.assertRaises(ExecutionInboxError):self.i.replay_next()
        self.append('first')
        with self.assertRaises(ExecutionInboxError):self.i.replay_next()
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)
        self.i.replay('first');self.i.replay_next()
        self.assertEqual(self.j.get('d1')['filled_quantity'],10)
        self.assertEqual(self.i.counts()['pending'],0)
        self.assertEqual(self.j.get('d1')['state'],'RECONCILIATION_REQUIRED')
        self.denied_enable()

    def test_conflicting_receipt_preserves_both_copies_and_never_selects_winner(self):
        self.append()
        row=fixtures.fill();row.update(fill_price='101',unit_fill_price='101')
        with self.assertRaises(ExecutionInboxError):self.append(row=row)
        self.assertEqual(self.i.counts()['receipts'],1)
        self.assertEqual(self.i.counts()['conflicts'],1)
        with self.assertRaises(ExecutionInboxError):self.i.replay_next()
        self.assertTrue(self.batch(filled=0)['matched'])
        self.denied_enable()
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)

    def test_caller_batch_cannot_clear_pending_inbox(self):
        self.append()
        self.assertTrue(self.batch(filled=0)['matched'])
        self.denied_enable()
        self.j.register('d2',symbol='OTHER',side='BUY',quantity=1)
        with self.assertRaises(OrderJournalError):
            self.j.claim_submission('d2',expected_epoch=self.j.shadow_control()['epoch'])

    def test_receipts_attempts_and_conflicts_are_append_only(self):
        self.append();self.i.replay_next()
        row=fixtures.fill();row['fee']='15'
        with self.assertRaises(ExecutionInboxError):self.append(row=row)
        for table in ('receipts','attempts','conflicts'):
            for operation in (f'DELETE FROM native_inbox_{table}',f'UPDATE native_inbox_{table} SET sequence=sequence'):
                with self.assertRaises(sqlite3.IntegrityError):self.j.db.execute(operation)

    def test_raw_account_extras_aggregate_rows_and_self_authority_are_not_persisted(self):
        for row in (dict(fixtures.fill(),account_no='private'),fixtures.rest(),
            dict(fixtures.fill(),genuine_live_provenance_verified=True)):
            with self.assertRaises(ExecutionInboxError):self.append(row=row)
        self.assertEqual(self.i.counts()['receipts'],0)

    def test_replace_cannot_bypass_append_only_receipt_attempt_or_conflict(self):
        self.append();self.i.replay_next()
        row=fixtures.fill();row['fee']='999'
        with self.assertRaises(ExecutionInboxError):self.append(row=row)
        before=self.i.counts()
        for table in ('receipts','attempts','conflicts'):
            with self.assertRaises(sqlite3.IntegrityError):
                self.j.db.execute(f'INSERT OR REPLACE INTO native_inbox_{table} SELECT * FROM native_inbox_{table}')
        self.assertEqual(self.i.counts(),before)

    def test_crash_window_after_native_commit_before_marker_replays_without_double_fill(self):
        self.append()
        self.j.db.execute("CREATE TRIGGER abort_marker BEFORE INSERT ON native_inbox_attempts WHEN NEW.outcome='APPLIED' BEGIN SELECT RAISE(ABORT,'synthetic crash'); END")
        with self.assertRaises(ExecutionInboxError):self.i.replay_next()
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertEqual(self.i.counts()['pending'],1)
        self.j.db.execute('DROP TRIGGER abort_marker')
        self.assertFalse(self.i.replay_next()['executions_created'])
        self.assertEqual(self.i.counts()['pending'],0)
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.denied_enable()

    def test_unknown_receipt_failure_is_sanitized_and_stops(self):
        with self.assertRaises(ExecutionInboxError) as raised:self.i.replay('secret-private-id')
        self.assertNotIn('secret',str(raised.exception))
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')

    def test_conflict_commit_already_quarantines_if_process_stops_before_error(self):
        self.append();self.i.replay_next();self.batch()
        self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])
        original_guard=self.i._guard
        @contextmanager
        def stop_after_commit():
            with original_guard():
                yield
            raise SystemExit('synthetic interruption after commit')
        row=fixtures.fill();row['fee']='999'
        with patch.object(self.i,'_guard',stop_after_commit),self.assertRaises(SystemExit):
            self.append(row=row)
        self.assertEqual(self.i.counts()['conflicts'],1)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.assertEqual(self.j.get('d1')['state'],'RECONCILIATION_REQUIRED')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone(),(1,))
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM reconciled_snapshot_bindings').fetchone(),(0,))

    def test_competing_conflict_writer_cannot_enter_between_receipt_check_and_fill(self):
        self.append()
        competitor=sqlite3.connect(self.path,timeout=0,isolation_level=None)
        original=self.b._apply_execution_locked
        def attempted_interleave(*args,**kwargs):
            self.assertTrue(self.j.db.in_transaction)
            with self.assertRaisesRegex(sqlite3.OperationalError,'locked'):
                competitor.execute("INSERT INTO native_inbox_conflicts(receipt_id,key,day,payload,digest) VALUES('receipt-1','d1','day','conflict','hash')")
            return original(*args,**kwargs)
        try:
            with patch.object(self.b,'_apply_execution_locked',side_effect=attempted_interleave):
                self.i.replay_next()
        finally:
            competitor.close()
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertEqual(self.i.counts()['conflicts'],0)

    def test_fill_binding_failure_rolls_back_inbox_replay_execution(self):
        self.append()
        self.j.db.execute("CREATE TRIGGER abort_native BEFORE INSERT ON native_fill_bindings BEGIN SELECT RAISE(ABORT,'synthetic binding failure'); END")
        with self.assertRaises(ExecutionInboxError):self.i.replay_next()
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)
        self.assertEqual(self.i.counts()['pending'],1)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.j.db.execute('DROP TRIGGER abort_native')
        self.i.replay_next()
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)

    def test_counts_do_not_emit_private_record_or_provenance_claim(self):
        self.append()
        out=self.i.counts();serialized=json.dumps(out)
        for private in ('native-order','receipt-1',fixtures.ACCOUNT,'005930'):
            self.assertNotIn(private,serialized)
        self.assertFalse(out['source_provenance_admitted'])
        self.assertFalse(out['raw_broker_artifact_retained'])
        self.assertFalse(out['live_ordering_authorized'])


class InboxSettlementTests(unittest.TestCase):
    tearDown = capital_fixtures.PrincipalReleaseTests.tearDown
    batch = capital_fixtures.PrincipalReleaseTests.batch
    release = capital_fixtures.PrincipalReleaseTests.release

    def setUp(self):
        capital_fixtures.PrincipalReleaseTests.setUp(self)
        b=KiwoomOrderJournalBridge(self.j,account_fingerprint=fixtures.ACCOUNT,trading_date=fixtures.DAY)
        b.bind_order('d1',broker_order_id='o1',native_side='2')
        self.i=KiwoomExecutionInbox(b)
        self.row=fixtures.fill(qty=1,remaining=9)
        self.row.update(symbol='SYNTHETIC',broker_order_id='o1')

    def append(self):
        self.i.append('receipt','d1',self.row,trading_date=fixtures.DAY)

    def test_zero_fill_snapshot_cannot_release_capital_with_unprocessed_fill(self):
        self.append()
        self.assertTrue(self.batch()['matched'])
        with self.assertRaises(OrderJournalError):self.release()
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)
        self.i.replay_next()
        self.assertEqual(self.j.get('d1')['filled_quantity'],1)
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)

    def test_zero_fill_snapshot_cannot_release_capital_with_conflicted_delivery(self):
        self.append()
        self.row['fee']='999'
        with self.assertRaises(ExecutionInboxError):self.append()
        self.assertTrue(self.batch()['matched'])
        with self.assertRaises(OrderJournalError):self.release()
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)


if __name__=='__main__':unittest.main()
