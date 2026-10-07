import copy
import hashlib
import json
from decimal import localcontext
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

from order_intent_journal import OrderIntentJournal
from kiwoom_order_journal_bridge import KiwoomOrderJournalBridge, NativeBridgeError
from research_v1_kiwoom_native_execution import (
    normalize_realtime_order_fill_event,normalize_kt00007_order_fill_detail,
    normalize_ka10076_filled_order,
)

ACCOUNT='sha256:'+'a'*64
DAY='2026-10-05'


def fill(execution='native-fill-1',qty=4,remaining=6,time='091501'):
    raw={'9201':'synthetic-account','9203':'native-order','9001':'005930',
        '900':'10','901':'100','902':str(remaining),'904':'','907':'2',
        '908':time,'909':execution,'910':'100','911':str(qty),
        '914':'100','915':str(qty),'913':'체결','919':'','938':'12','939':'0'}
    return normalize_realtime_order_fill_event(raw,account_fingerprint=ACCOUNT)


def rest(api='kt00007',filled=4,remaining=6):
    raw=dict(ord_no='native-order',stk_cd='005930',ord_qty='10',
        ord_uv='100',cntr_qty=str(filled),cntr_uv='100',ord_remnq=str(remaining),
        ori_ord='',ord_tm='091501',trde_tp='2')
    if api=='kt00007':
        return normalize_kt00007_order_fill_detail(raw,account_fingerprint=ACCOUNT)
    raw.update(ord_pric='100',cntr_pric='100',oso_qty=str(remaining),orig_ord_no='',tdy_trde_cmsn='12',tdy_trde_tax='0')
    return normalize_ka10076_filled_order(raw,account_fingerprint=ACCOUNT)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'synthetic.sqlite'
        self.j=OrderIntentJournal(self.path)
        self.j.register('d1',symbol='005930',side='BUY',quantity=10)
        epoch=self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])['epoch']
        self.j.claim_submission('d1',expected_epoch=epoch)
        self.j.bind_acknowledgement('d1','native-order')
        self.b=KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.b.bind_order('d1',broker_order_id='native-order',native_side='2')

    def tearDown(self):
        self.j.close()
        self.tmp.cleanup()

    def apply(self,row=None,day=DAY):
        return self.b.apply_execution('d1',fill() if row is None else row,trading_date=day)

    def assert_blocked(self):
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone()[0],1)

    def test_normalized_unit_fill_and_native_id_commit_together_without_network(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            out=self.apply()
        self.assertTrue(out['executions_created'])
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertEqual(self.j.db.execute('SELECT execution_id FROM executions').fetchone()[0],'native-fill-1')
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone()[0],1)
        for name in ('live_ordering_authorized','genuine_live_evidence','real_account_origin_verified',
            'trading_date_origin_attested','native_side_semantics_attested','fees_settled'):
            self.assertFalse(out[name])

    def test_native_exact_duplicate_never_counts_quantity_twice(self):
        self.apply()
        self.assertFalse(self.apply()['executions_created'])
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)

    def test_changed_price_under_low_decimal_precision_is_conflict(self):
        first=fill();first.update(fill_price='100001',unit_fill_price='100001')
        changed=fill();changed.update(fill_price='100002',unit_fill_price='100002')
        with localcontext() as context:
            context.prec=3
            self.apply(first)
            with self.assertRaises(NativeBridgeError):self.apply(changed)
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assert_blocked()

    def test_same_price_across_decimal_contexts_and_restart_remains_duplicate(self):
        first=fill();first.update(fill_price='100001.00',unit_fill_price='100001')
        self.apply(first)
        self.j.close();self.j=OrderIntentJournal(self.path)
        self.b=KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        equivalent=fill();equivalent.update(fill_price='1.00001E5',unit_fill_price='100001.000')
        with localcontext() as context:
            context.prec=3
            self.assertFalse(self.apply(equivalent)['executions_created'])
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)

    def test_changed_price_beyond_default_precision_is_conflict(self):
        first=fill();first.update(fill_price='12345678901234567890123456789',
            unit_fill_price='12345678901234567890123456789')
        self.apply(first)
        changed=fill();changed.update(fill_price='12345678901234567890123456788',
            unit_fill_price='12345678901234567890123456788')
        with self.assertRaises(NativeBridgeError):self.apply(changed)
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assert_blocked()

    def test_native_scope_order_fill_and_execution_rows_reject_mutation_and_replace(self):
        self.apply()
        for table,column in (('native_journal_scope','id'),('native_order_bindings','key'),
            ('native_fill_bindings','key'),('executions','key')):
            for statement in (f'DELETE FROM {table}',f'UPDATE {table} SET {column}={column}',
                f'INSERT OR REPLACE INTO {table} SELECT * FROM {table}'):
                with self.assertRaises(sqlite3.IntegrityError):self.j.db.execute(statement)
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertFalse(self.apply()['executions_created'])

    def test_reconnect_restores_recursive_replace_safeguards(self):
        self.apply();self.j.close();self.j=OrderIntentJournal(self.path)
        self.b=KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.assertEqual(self.j.db.execute('PRAGMA recursive_triggers').fetchone(),(1,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.j.db.execute('INSERT OR REPLACE INTO native_fill_bindings SELECT * FROM native_fill_bindings')
        self.assertFalse(self.apply()['executions_created'])

    def test_duplicate_is_idempotent_after_later_fills_and_restart(self):
        self.apply()
        self.apply(fill('native-fill-2',6,0,'091502'))
        self.j.close()
        self.j=OrderIntentJournal(self.path)
        self.b=KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.assertFalse(self.apply()['executions_created'])
        self.assertEqual(self.j.get('d1')['filled_quantity'],10)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')

    def test_same_id_conflicting_price_quantity_or_time_quarantines_without_rewrite(self):
        self.apply()
        for change in ({'fill_price':'101','unit_fill_price':'101'},
            {'fill_qty':'5','unit_fill_qty':'5'},{'broker_lifecycle_time':'091600'}):
            row=fill();row.update(change)
            with self.assertRaises(NativeBridgeError):self.apply(row)
            self.assertEqual(self.j.get('d1')['filled_quantity'],4)
            self.assert_blocked()

    def test_account_day_order_symbol_and_native_side_must_match(self):
        for field,value in (('account_fingerprint','sha256:'+'b'*64),
            ('broker_order_id','different'),('symbol','000660'),('side','1'),('order_qty','11')):
            row=fill();row[field]=value
            with self.assertRaises(NativeBridgeError):self.apply(row)
        with self.assertRaises(NativeBridgeError):self.apply(day='2026-10-06')
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)
        self.assert_blocked()

    def test_restart_rejects_orphan_native_order_binding_without_discarding_it(self):
        self.j.db.execute("INSERT INTO native_order_bindings VALUES('orphan','orphan-order','2')")
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        with self.assertRaises(NativeBridgeError):
            KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_order_bindings').fetchone(), (2,))
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone(), (0,))
        self.assert_blocked()

    def test_restart_rejects_incomplete_native_side_binding(self):
        self.j.register('d2',symbol='OTHER',side='BUY',quantity=1)
        self.j.claim_submission('d2',expected_epoch=self.j.shadow_control()['epoch'])
        self.j.bind_acknowledgement('d2','other-order')
        self.j.db.execute("INSERT INTO native_order_bindings VALUES('d2','other-order','')")
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        with self.assertRaises(NativeBridgeError):
            KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.assertEqual(self.j.db.execute("SELECT native_side FROM native_order_bindings WHERE key='d2'").fetchone(), ('',))
        self.assert_blocked()

    def test_restart_rejects_orphan_fill_binding_without_receipt_reference(self):
        self.j.db.execute("INSERT INTO native_fill_bindings VALUES('d1','orphan-fill','bad','{}')")
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        with self.assertRaises(NativeBridgeError):
            KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone(), (1,))
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone(), (0,))
        self.assert_blocked()

    def test_restart_rejects_changed_fill_binding_digest_without_receipt_reference(self):
        self.apply()
        self.j.db.execute('DROP TRIGGER native_fill_bindings_update_immutable')
        self.j.db.execute("UPDATE native_fill_bindings SET digest='bad'")
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        with self.assertRaises(NativeBridgeError):
            KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.assertEqual(self.j.db.execute('SELECT quantity FROM executions').fetchone(), (4,))
        self.assertEqual(self.j.db.execute('SELECT digest FROM native_fill_bindings').fetchone(), ('bad',))
        self.assert_blocked()

    def test_restart_rejects_rehashed_malformed_fill_binding_without_receipt(self):
        self.apply()
        material = json.loads(self.j.db.execute('SELECT payload FROM native_fill_bindings').fetchone()[0])
        malformed = [json.dumps(dict(material,quantity=3),sort_keys=True,separators=(',',':')),
            json.dumps(dict(material,remaining=9),sort_keys=True,separators=(',',':')),
            '{"price":"999",' + json.dumps(material,sort_keys=True,separators=(',',':'))[1:],
            '[' * 20000 + '0' + ']' * 20000]
        self.j.db.execute('DROP TRIGGER native_fill_bindings_update_immutable')
        for payload in malformed:
            with self.subTest(kind='deep' if len(payload)>1000 else 'object'):
                self.j.db.execute('UPDATE native_fill_bindings SET payload=?,digest=?',
                    (payload,hashlib.sha256(payload.encode()).hexdigest()))
                with self.assertRaises(NativeBridgeError) as raised:
                    KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
                self.assertEqual(str(raised.exception), 'NATIVE_BRIDGE_RECONCILIATION_REQUIRED')
                self.assertEqual(self.j.db.execute('SELECT quantity FROM executions').fetchone(), (4,))
                self.assert_blocked()

    def test_startup_rejects_corrupt_unbound_execution_total_without_inventing_native_binding(self):
        self.j.record_execution('d1',broker_order_id='native-order',execution_id='offline',quantity=4)
        self.j.db.execute('UPDATE intents SET filled=3')
        with self.assertRaises(NativeBridgeError):
            KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.assertEqual(self.j.db.execute('SELECT quantity FROM executions').fetchone(), (4,))
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone(), (0,))
        self.assert_blocked()

    def test_startup_rejects_orphan_execution_without_native_binding(self):
        self.j.db.execute("INSERT INTO executions VALUES('orphan','orphan-fill',1)")
        with self.assertRaises(NativeBridgeError):
            KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone(), (1,))
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone(), (0,))
        self.assert_blocked()

    def test_session_cannot_switch_account_or_trading_day_after_restart(self):
        for account,day in (('sha256:'+'b'*64,DAY),(ACCOUNT,'2026-10-06')):
            with self.assertRaises(NativeBridgeError):
                KiwoomOrderJournalBridge(self.j,account_fingerprint=account,trading_date=day)
            self.assert_blocked()

    def test_unbound_order_cannot_receive_native_fill(self):
        self.j.register('d2',symbol='005930',side='BUY',quantity=10)
        with self.assertRaises(NativeBridgeError):self.b.apply_execution('d2',fill(),trading_date=DAY)
        self.assertEqual(self.j.get('d2')['state'],'INTENT_CREATED')
        self.assertEqual(self.j.get('d2')['filled_quantity'],0)

    def test_rest_aggregate_cannot_be_recast_as_execution(self):
        for api in ('kt00007','ka10076'):
            with self.assertRaises(NativeBridgeError):self.apply(rest(api))
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone()[0],0)

    def test_matching_rest_quantities_compare_only_without_creating_or_clearing_state(self):
        self.apply()
        self.j.mark_uncertain('d1')
        for api in ('kt00007','ka10076'):
            out=self.b.verify_rest_snapshot('d1',rest(api),trading_date=DAY)
            self.assertFalse(out['executions_created'])
            self.assertFalse(out['order_state_reconciled'])
        self.assertEqual(self.j.get('d1')['state'],'RECONCILIATION_REQUIRED')
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone()[0],1)

    def test_rest_missing_fills_or_remaining_mismatch_does_not_invent_executions(self):
        for row in (rest(),rest(filled=0,remaining=9)):
            with self.assertRaises(NativeBridgeError):self.b.verify_rest_snapshot('d1',row,trading_date=DAY)
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)
        self.assert_blocked()

    def test_rest_matching_corrupt_total_cannot_override_retained_executions(self):
        self.apply()
        self.j.db.execute('UPDATE intents SET filled=3')
        for api in ('kt00007', 'ka10076'):
            with self.subTest(api=api), self.assertRaises(NativeBridgeError):
                self.b.verify_rest_snapshot('d1', rest(api,filled=3,remaining=7), trading_date=DAY)
        self.assertEqual(self.j.db.execute('SELECT quantity FROM executions').fetchone(), (4,))
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone(), (1,))
        self.assert_blocked()

    def test_rest_matching_order_cannot_ignore_orphan_execution(self):
        self.apply()
        self.j.db.execute("INSERT INTO executions VALUES('orphan','orphan-fill',1)")
        for api in ('kt00007', 'ka10076'):
            with self.subTest(api=api), self.assertRaises(NativeBridgeError):
                self.b.verify_rest_snapshot('d1', rest(api), trading_date=DAY)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone(), (2,))
        self.assert_blocked()

    def test_cumulative_unit_ambiguity_or_missing_unit_fields_fail_closed(self):
        for change in ({'unit_fill_qty':'2'},{'unit_fill_qty':''},{'unit_fill_price':''},
            {'unit_fill_price':'101'}):
            row=fill();row.update(change)
            with self.assertRaises(NativeBridgeError):self.apply(row)
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)

    def test_native_number_validation_rejects_fractional_negative_nonfinite_and_boolean(self):
        for value in ('4.1','-4','NaN','Infinity',True,''):
            row=fill();row.update(fill_qty=value,unit_fill_qty=value)
            with self.assertRaises(NativeBridgeError):self.apply(row)
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)

    def test_gap_or_out_of_order_new_execution_waits_for_missing_native_fill(self):
        second=fill('native-fill-2',6,0,'091502')
        with self.assertRaises(NativeBridgeError):self.apply(second)
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)
        self.apply()
        self.apply(second)
        self.assertEqual(self.j.get('d1')['filled_quantity'],10)
        self.assertEqual(self.j.get('d1')['state'],'RECONCILIATION_REQUIRED')

    def test_invalid_time_amendment_status_or_rejection_cannot_create_fill(self):
        for change in ({'broker_lifecycle_time':'256199'},{'broker_lifecycle_time':'0915'},
            {'original_order_id':'amend-parent'},{'order_status':'접수'},{'rejection_reason':'rejected'}):
            row=fill();row.update(change)
            with self.assertRaises(NativeBridgeError):self.apply(row)

    def test_source_or_schema_drift_and_self_live_claim_rejected(self):
        for field,value in (('source_contract','forged'),('official_schema_commit','other'),
            ('genuine_live_provenance_verified',True),('project_live_evidence_admitted',True),
            ('broker_execution_id_available_in_source',False),('broker_execution_id','')):
            row=fill();row[field]=value
            with self.assertRaises(NativeBridgeError):self.apply(row)
        self.assert_blocked()

    def test_existing_unbound_local_execution_cannot_acquire_fabricated_native_proof(self):
        self.j.record_execution('d1',broker_order_id='native-order',execution_id='native-fill-1',quantity=4)
        with self.assertRaises(NativeBridgeError):self.apply()
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone()[0],0)

    def test_daily_fee_totals_are_not_settled_or_added_as_per_fill_cost(self):
        self.apply()
        row=fill();row.update(fee='999999',tax='999999')
        self.assertFalse(self.apply(row)['fees_settled'])
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)

    def test_conflict_errors_do_not_expose_private_identifiers(self):
        row=fill();row['broker_order_id']='private-order-do-not-emit'
        with self.assertRaises(NativeBridgeError) as raised:self.apply(row)
        self.assertEqual(str(raised.exception),'NATIVE_BRIDGE_RECONCILIATION_REQUIRED')

    def test_source_binding_failure_rolls_back_execution_and_quantity_together(self):
        self.j.db.execute("CREATE TRIGGER synthetic_abort BEFORE INSERT ON native_fill_bindings BEGIN SELECT RAISE(ABORT,'synthetic failure'); END")
        with self.assertRaises(NativeBridgeError):self.apply()
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone()[0],0)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone()[0],0)
        self.assert_blocked()

    def test_concurrent_exact_duplicates_create_one_native_execution(self):
        ready=Barrier(6)
        def apply(_):
            j=OrderIntentJournal(self.path)
            try:
                b=KiwoomOrderJournalBridge(j,account_fingerprint=ACCOUNT,trading_date=DAY)
                ready.wait()
                return b.apply_execution('d1',fill(),trading_date=DAY)['executions_created']
            finally:
                j.close()
        with ThreadPoolExecutor(max_workers=6) as pool:
            self.assertEqual(sum(pool.map(apply,range(6))),1)
        self.assertEqual(self.j.get('d1')['filled_quantity'],4)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM native_fill_bindings').fetchone()[0],1)


if __name__=='__main__':unittest.main()
