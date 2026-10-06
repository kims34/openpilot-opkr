import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from kiwoom_execution_inbox import KiwoomExecutionInbox, ExecutionInboxError
from kiwoom_order_journal_bridge import KiwoomOrderJournalBridge
from kiwoom_protected_execution_intake import (
    ProtectedAccountBinding, KiwoomProtectedExecutionIntake, ProtectedIntakeError,
)
from order_intent_journal import OrderIntentJournal, OrderJournalError


class ProtectedIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'synthetic.sqlite'
        self.binding=ProtectedAccountBinding(account='synthetic-protected-account',fingerprint_key=b'a'*32)
        self.j=OrderIntentJournal(self.path)
        self.j.register('intent',symbol='005930',side='BUY',quantity=10)
        epoch=self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])['epoch']
        self.j.claim_submission('intent',expected_epoch=epoch)
        self.j.bind_acknowledgement('intent','order')
        self.bridge=KiwoomOrderJournalBridge(self.j,account_fingerprint=self.binding.fingerprint,trading_date='2026-10-05')
        self.bridge.bind_order('intent',broker_order_id='order',native_side='2')
        self.inbox=KiwoomExecutionInbox(self.bridge)
        self.intake=KiwoomProtectedExecutionIntake(self.inbox,self.binding)
        self.raw=dict(zip(['9201','9203','9001','900','901','902','904','907','908','909','910','911','914','915','913','919'],
            ['synthetic-protected-account','order','005930','10','100','6','','2','091501','execution','100','4','100','4','체결','']))

    def tearDown(self):
        self.j.close();self.tmp.cleanup()

    def append(self, row=None, day='2026-10-05'):
        return self.intake.append('receipt','intent',self.raw if row is None else row,trading_date=day)

    def append_bound(self, row=None, day='2026-10-05'):
        return self.intake.append_for_bound_order('receipt',self.raw if row is None else row,trading_date=day)

    def nonfill(self):
        row=dict(self.raw)
        row.update({'902':'10','909':'','910':'','911':'','914':'','915':'','913':'접수'})
        return row

    def test_known_nonfill_lifecycle_is_ignored_without_poisoning_execution_inbox(self):
        before=self.j.get('intent')['state']
        out=self.append_bound(self.nonfill())
        self.assertEqual(out['result'],'NON_FILL_EVENT_IGNORED')
        self.assertTrue(out['broker_order_binding_resolved'])
        self.assertEqual(self.inbox.counts()['receipts'],0)
        self.assertEqual(self.inbox.counts()['pending'],0)
        self.assertEqual(self.j.get('intent')['state'],before)
        self.assertEqual(self.j.get('intent')['filled_quantity'],0)

    def test_fill_like_event_cannot_be_downgraded_to_nonfill_ignore(self):
        row=self.nonfill()
        row.update({'909':'execution','910':'100','911':'4','914':'100','915':'4'})
        out=self.append_bound(row)
        self.assertEqual(out['result'],'RECEIPT_PERSISTED')
        self.assertEqual(self.inbox.counts()['pending'],1)
        with self.assertRaises(ExecutionInboxError):
            self.inbox.replay_next()
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')

    def test_unknown_nonfill_order_still_fails_closed_before_ignore(self):
        row=self.nonfill(); row['9203']='unbound-order'
        with self.assertRaises(ProtectedIntakeError):
            self.append_bound(row)
        self.assertEqual(self.inbox.counts()['receipts'],0)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')

    def test_bound_order_resolution_routes_without_caller_decision_key(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            out=self.append_bound(); self.inbox.replay_next()
        self.assertTrue(out['broker_order_binding_resolved'])
        self.assertTrue(out['raw_account_equality_checked'])
        self.assertFalse(out['source_provenance_admitted'])
        self.assertFalse(out['live_ordering_authorized'])
        self.assertEqual(self.j.get('intent')['filled_quantity'],4)

    def test_unknown_broker_order_cannot_be_routed_or_retained(self):
        row=dict(self.raw); row['9203']='unbound-order'
        with self.assertRaises(ProtectedIntakeError):
            self.append_bound(row)
        self.assertEqual(self.inbox.counts()['receipts'],0)
        self.assertEqual(self.j.get('intent')['filled_quantity'],0)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')

    def test_equal_protected_account_persists_only_normalized_row_and_keeps_admission_false(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            out=self.append();self.inbox.replay_next()
        self.assertTrue(out['raw_account_equality_checked'])
        self.assertFalse(out['environment_origin_authenticated'])
        self.assertFalse(out['source_provenance_admitted'])
        self.assertFalse(out['trading_date_origin_attested'])
        self.assertFalse(out['live_ordering_authorized'])
        self.assertEqual(self.j.get('intent')['filled_quantity'],4)
        payload=self.j.db.execute('SELECT payload FROM native_inbox_receipts').fetchone()[0]
        self.assertNotIn('synthetic-protected-account',payload)
        self.assertNotIn('9201',json.loads(payload))
        self.assertNotIn('synthetic-protected-account',json.dumps(out))

    def test_wrong_missing_or_nonstring_account_quarantines_before_any_retention(self):
        for value in ('other-account',' synthetic-protected-account',None,123):
            row=dict(self.raw);row['9201']=value
            with self.assertRaises(ProtectedIntakeError):self.append(row)
        self.assertEqual(self.inbox.counts()['receipts'],0)
        self.assertEqual(self.j.get('intent')['filled_quantity'],0)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        with self.assertRaises(OrderJournalError):
            self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])

    def test_extra_raw_sensitive_fields_never_reach_receipt_storage(self):
        for field in ('account_no','token','app_secret','unknown'):
            with self.assertRaises(ProtectedIntakeError):self.append(dict(self.raw,**{field:'synthetic-secret'}))
        self.assertEqual(self.inbox.counts()['receipts'],0)

    def test_binding_and_errors_have_redacted_representations(self):
        self.assertEqual(repr(self.binding),'<ProtectedAccountBinding redacted>')
        row=dict(self.raw);row['9201']='never-emit-private-account'
        with self.assertRaises(ProtectedIntakeError) as raised:self.append(row)
        self.assertEqual(str(raised.exception),'PROTECTED_INTAKE_RECONCILIATION_REQUIRED')

    def test_fingerprint_is_deterministic_keyed_and_account_scoped(self):
        same=ProtectedAccountBinding(account='synthetic-protected-account',fingerprint_key=b'a'*32)
        other=ProtectedAccountBinding(account='other',fingerprint_key=b'a'*32)
        newkey=ProtectedAccountBinding(account='synthetic-protected-account',fingerprint_key=b'b'*32)
        self.assertEqual(same.fingerprint,self.binding.fingerprint)
        self.assertNotEqual(other.fingerprint,self.binding.fingerprint)
        self.assertNotEqual(newkey.fingerprint,self.binding.fingerprint)
        self.assertRegex(same.fingerprint,r'^sha256:[0-9a-f]{64}$')

    def test_rotated_key_cannot_silently_attach_to_old_journal_account_scope(self):
        newkey=ProtectedAccountBinding(account='synthetic-protected-account',fingerprint_key=b'b'*32)
        with self.assertRaises(ProtectedIntakeError):KiwoomProtectedExecutionIntake(self.inbox,newkey)
        self.assertEqual(self.inbox.counts()['receipts'],0)

    def test_restart_with_same_protected_binding_replays_duplicate_only(self):
        self.append();self.inbox.replay_next()
        self.j.close();self.j=OrderIntentJournal(self.path)
        self.bridge=KiwoomOrderJournalBridge(self.j,account_fingerprint=self.binding.fingerprint,trading_date='2026-10-05')
        self.inbox=KiwoomExecutionInbox(self.bridge)
        self.intake=KiwoomProtectedExecutionIntake(self.inbox,self.binding)
        self.append()
        self.assertFalse(self.inbox.replay('receipt')['executions_created'])
        self.assertEqual(self.j.get('intent')['filled_quantity'],4)

    def test_declared_date_mismatch_does_not_manufacture_broker_date(self):
        with self.assertRaises(ProtectedIntakeError):self.append(day='2026-10-06')
        self.assertEqual(self.inbox.counts()['receipts'],0)

    def test_invalid_protected_config_does_not_include_secret_in_errors(self):
        for account,key in (('',b'a'*32),(' secret',b'a'*32),('synthetic',b'short'),('synthetic','private-key'),('\ud800',b'a'*32)):
            with self.assertRaises(ProtectedIntakeError) as raised:
                ProtectedAccountBinding(account=account,fingerprint_key=key)
            self.assertEqual(str(raised.exception),'INVALID_PROTECTED_ACCOUNT_CONTEXT')

    def test_protected_context_cannot_be_mutated_after_fingerprint_binding(self):
        with self.assertRaises(AttributeError):self.binding._account=b'other'
        with self.assertRaises(AttributeError):self.binding._fingerprint='sha256:'+'f'*64
        self.assertTrue(self.binding.matches('synthetic-protected-account'))

    def test_official_extra_fields_are_accepted_and_discarded_before_retention(self):
        row=dict(self.raw,**{'9205':'synthetic-admin','302':'synthetic-name',
            '10':'100','27':'101','28':'99','920':'synthetic-screen',
            '921':'synthetic-terminal','922':'0','923':'','10010':'100'})
        self.append(row)
        payload=self.j.db.execute('SELECT payload FROM native_inbox_receipts').fetchone()[0]
        for value in ('synthetic-admin','synthetic-name','synthetic-screen','synthetic-terminal'):
            self.assertNotIn(value,payload)
        self.inbox.replay_next()
        self.assertEqual(self.j.get('intent')['filled_quantity'],4)

    def test_unused_official_metadata_does_not_change_receipt_identity(self):
        self.append(dict(self.raw,**{'9205':'synthetic-admin-1','10':'100'}))
        out=self.append(dict(self.raw,**{'9205':'synthetic-admin-2','10':'101'}))
        self.assertEqual(out['result'],'DUPLICATE_RECEIPT')
        self.assertEqual(self.inbox.counts()['conflicts'],0)


if __name__=='__main__':unittest.main()
