from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch

import test_native_cashflow_review_manifest as manifest_fixtures
from native_settlement_review_cli import main, review_native_settlement_file
from order_intent_journal import OrderIntentJournal


class NativeReviewCLITests(unittest.TestCase):
    def setUp(self):
        self.fixture = manifest_fixtures.ReviewManifestTests()
        self.fixture.setUp()
        local = self.fixture.local
        self.journal = local.local.journal
        self.path = Path(local.local.path)
        self.input = self.path.parent/'private-input.json'
        page = local.history.page()
        self.payload = dict(account_fingerprint='a'*64,
            opening=dict(body={**local.body,'entr':'10000'},captured_at='2026-10-06T09:00:00+09:00'),
            closing=dict(body=local.body,captured_at='2026-10-06T10:00:00+09:00'),
            history=dict(pages=[dict(page.__dict__)],request=local.history.request(),captured_at=self.fixture.batch.captured_at),
            review_manifest=self.fixture.manifest)
        self.write()

    def tearDown(self): self.fixture.tearDown()

    def write(self): self.input.write_text(json.dumps(self.payload),encoding='utf-8')

    def assess(self): return review_native_settlement_file(self.input,self.path)

    def test_file_path_is_complete_private_read_only_and_not_admitted(self):
        before = self.journal.shadow_control(),self.journal.db.total_changes
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            result = self.assess()
        self.assertTrue(result['assessment_completed'])
        self.assertTrue(result['cashflow_reconciliation']['cash_balance_matched'])
        self.assertFalse(result['cashflow_reconciliation']['settlement_fields_consistent'])
        self.assertFalse(result['ready_for_final_user_authorization'])
        self.assertFalse(result['real_orders_authorized'])
        self.assertEqual(before,(self.journal.shadow_control(),self.journal.db.total_changes))
        for private in ('a'*64,'synthetic-review',str(self.input),str(self.path)):
            self.assertNotIn(private,json.dumps(result))

    def test_active_shadow_is_not_recovered_or_modified_by_review(self):
        self.fixture.local.local.claimed()
        before = self.journal.shadow_control(),self.journal.get('synthetic-intent')
        result = self.assess()
        self.assertEqual(result['durable_unresolved_reconciliation_count'],1)
        self.assertEqual(before,(self.journal.shadow_control(),self.journal.get('synthetic-intent')))

    def test_malformed_cash_groups_cannot_report_matching_balance(self):
        self.payload['closing']['body']['entr'] = '8,9,99'
        self.write()
        before = self.journal.shadow_control(), self.journal.db.total_changes
        result = self.assess()
        self.assertFalse(result['assessment_completed'])
        self.assertNotIn('cashflow_reconciliation', result)
        self.assertFalse(result['real_orders_authorized'])
        self.assertNotIn('8,9,99', json.dumps(result))
        self.assertEqual(before, (self.journal.shadow_control(), self.journal.db.total_changes))

    def test_readonly_journal_refuses_mutation(self):
        readonly = OrderIntentJournal.open_readonly(self.path)
        before = self.journal.shadow_control()
        try:
            with self.assertRaises(sqlite3.OperationalError): readonly.trip_kill_switch()
            with self.assertRaises(sqlite3.OperationalError):
                readonly.register('forbidden',symbol='SYNTHETIC',side='BUY',quantity=1)
        finally: readonly.close()
        self.assertEqual(before,self.journal.shadow_control())

    def test_absent_journal_is_not_created(self):
        missing = self.path.parent/'missing.sqlite'
        self.assertFalse(review_native_settlement_file(self.input,missing)['assessment_completed'])
        self.assertFalse(missing.exists())

    def test_embedded_admissions_and_duplicate_json_keys_reject(self):
        self.payload['source_account_origin_authenticated'] = True
        self.write()
        self.assertFalse(self.assess()['assessment_completed'])
        self.input.write_text('{"account_fingerprint":"a","account_fingerprint":"b"}',encoding='utf-8')
        self.assertFalse(self.assess()['assessment_completed'])

    def test_cli_outputs_json_and_clear_exit_status(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(['--input',str(self.input),'--journal',str(self.path)])
        self.assertEqual(code,0)
        self.assertTrue(json.loads(output.getvalue())['assessment_completed'])
        self.input.write_text('invalid private JSON',encoding='utf-8')
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(['--input',str(self.input),'--journal',str(self.path)]),2)
        self.assertNotIn('invalid private JSON',output.getvalue())
