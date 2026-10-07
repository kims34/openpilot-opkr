import http.client
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest

from order_intent_journal import OrderIntentJournal, OrderJournalError
from shadow_operational_dashboard import create_dashboard_server


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'private.sqlite'
        self.journal = OrderIntentJournal(self.path)
        self.server = create_dashboard_server(self.path,0)
        self.worker = Thread(target=self.server.serve_forever,daemon=True)
        self.worker.start()

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.worker.join()
        self.journal.close(); self.tmp.cleanup()

    def request(self,path,method='GET',headers=None):
        con = http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        try:
            con.request(method,path,headers=headers or {})
            response = con.getresponse()
            return response.status,dict(response.getheaders()),response.read().decode()
        finally: con.close()

    def test_loopback_api_is_read_only_and_noncacheable(self):
        before = self.journal.shadow_control(),self.journal.db.total_changes
        status,headers,body = self.request('/api/status')
        self.assertEqual(status,200)
        self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertFalse(json.loads(body)['real_orders_authorized'])
        self.assertEqual(before,(self.journal.shadow_control(),self.journal.db.total_changes))
        self.assertEqual(self.server.server_address[0],'127.0.0.1')
        self.assertNotIn(str(self.path),body)

    def test_retained_safety_quarantine_is_specific_private_and_read_only(self):
        self.journal.db.execute('PRAGMA ignore_check_constraints=ON')
        self.journal.db.execute("UPDATE shadow_control SET killed=-1,reason='PRIVATE-FAULT-ARTIFACT'")
        with self.assertRaises(OrderJournalError):
            self.journal.disable_shadow()
        before = self.journal.db.total_changes
        status,_,body = self.request('/api/status')
        report = json.loads(body)
        self.assertEqual(status,200)
        self.assertFalse(report['diagnostics_complete'])
        self.assertEqual(report['local_blockers'], ['SAFETY_METADATA_QUARANTINED'])
        self.assertFalse(report['real_orders_authorized'])
        self.assertNotIn('PRIVATE-FAULT-ARTIFACT',body)
        self.assertNotIn('shadow_control_faults',body)
        self.assertNotIn(str(self.path),body)
        self.assertEqual(self.journal.db.total_changes,before)

    def test_initialized_history_loss_reports_private_blocker_without_recreating(self):
        from shadow_capital_allocator import ShadowCapitalAllocator
        ShadowCapitalAllocator(self.journal)
        self.journal.register('PRIVATE-INTENT',symbol='PRIVATE-SYMBOL',side='BUY',quantity=1)
        self.journal.db.execute('DROP TABLE shadow_capital_releases')
        before = self.journal.db.total_changes
        status,_,body = self.request('/api/status')
        report = json.loads(body)
        self.assertEqual(status,200)
        self.assertFalse(report['diagnostics_complete'])
        self.assertEqual(report['local_blockers'], ['INITIALIZED_HISTORY_MISSING'])
        for field in ('real_orders_authorized','exact_policy_shadow_admitted','genuine_live_provenance_verified','journal_mutation_attempted'):
            self.assertFalse(report[field])
        for private in ('PRIVATE-INTENT','PRIVATE-SYMBOL','shadow_capital_releases',str(self.path)):
            self.assertNotIn(private,body)
        self.assertEqual(self.journal.db.total_changes,before)
        self.assertIsNone(self.journal.db.execute("SELECT 1 FROM sqlite_master WHERE name='shadow_capital_releases'").fetchone())

    def test_foreign_host_and_path_selection_are_rejected(self):
        self.assertEqual(self.request('/api/status',headers={'Host':'external.invalid'})[0],403)
        self.assertEqual(self.request('/api/status?journal=another.sqlite')[0],404)

    def test_mutation_routes_are_not_available(self):
        for method in ('POST','PUT','PATCH','DELETE'):
            self.assertEqual(self.request('/api/status',method)[0],405)

    def test_page_uses_local_script_and_no_order_controls(self):
        status,headers,page = self.request('/')
        self.assertEqual(status,200)
        self.assertIn('script-src',headers['Content-Security-Policy'])
        self.assertIn('실제 주문은 꺼져 있습니다',page)
        self.assertEqual(self.request('/dashboard.js')[0],200)

    def test_unavailable_journal_does_not_create_file(self):
        missing = Path(self.tmp.name)/'missing.sqlite'
        self.server.journal_path = missing
        report = json.loads(self.request('/api/status')[2])
        self.assertFalse(report['diagnostics_complete'])
        self.assertFalse(missing.exists())

    def test_unconfigured_settlement_is_explicit_not_success(self):
        report = json.loads(self.request('/api/settlement')[2])
        self.assertFalse(report['assessment_completed'])
        self.assertEqual(report['review_errors'],['SETTLEMENT_INPUT_NOT_CONFIGURED'])
        self.assertFalse(report['real_orders_authorized'])

    def test_bad_fixed_settlement_input_is_private_and_request_cannot_replace_it(self):
        private = Path(self.tmp.name)/'private-settlement.json'
        private.write_text('PRIVATE INVALID INPUT',encoding='utf-8')
        self.server.settlement_input_path = private
        status,headers,body = self.request('/api/settlement')
        self.assertEqual(status,200)
        self.assertFalse(json.loads(body)['assessment_completed'])
        self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertNotIn('PRIVATE INVALID INPUT',body)
        self.assertNotIn(str(private),body)
        self.assertEqual(self.request('/api/settlement?input=another.json')[0],404)

    def test_valid_artifact_endpoint_keeps_journal_unchanged_and_admissions_false(self):
        import test_native_settlement_review_cli as fixtures
        fixture = fixtures.NativeReviewCLITests()
        fixture.setUp()
        try:
            self.server.journal_path = fixture.path
            self.server.settlement_input_path = fixture.input
            before = fixture.journal.shadow_control(),fixture.journal.db.total_changes
            report = json.loads(self.request('/api/settlement')[2])
            self.assertTrue(report['assessment_completed'])
            self.assertTrue(report['cashflow_reconciliation']['cash_balance_matched'])
            self.assertFalse(report['ready_for_final_user_authorization'])
            self.assertFalse(report['real_orders_authorized'])
            self.assertEqual(before,(fixture.journal.shadow_control(),fixture.journal.db.total_changes))
            self.assertNotIn('a'*64,json.dumps(report))
        finally: fixture.tearDown()

    def test_deep_json_is_blocked_without_request_traceback_and_recovers(self):
        import test_native_settlement_review_cli as fixtures
        fixture = fixtures.NativeReviewCLITests()
        fixture.setUp()
        try:
            self.server.journal_path = fixture.path
            self.server.settlement_input_path = fixture.input
            before = fixture.journal.shadow_control(),fixture.journal.db.total_changes
            fixture.input.write_text('['*20000+'0'+']'*20000,encoding='utf-8')
            errors = io.StringIO()
            with redirect_stderr(errors):
                status,headers,body = self.request('/api/settlement')
                self.assertEqual(status,200)
                self.assertEqual(headers['Cache-Control'],'no-store')
                blocked = json.loads(body)
                self.assertFalse(blocked['assessment_completed'])
                self.assertFalse(blocked['real_orders_authorized'])
                self.assertNotIn(str(fixture.input),body)
                fixture.write()
                recovered = json.loads(self.request('/api/settlement')[2])
                self.assertTrue(recovered['assessment_completed'])
                self.assertFalse(recovered['ready_for_final_user_authorization'])
                self.assertFalse(recovered['real_orders_authorized'])
            self.assertEqual(errors.getvalue(),'')
            self.assertEqual(before,(fixture.journal.shadow_control(),fixture.journal.db.total_changes))
        finally: fixture.tearDown()

    def test_changed_snapshot_is_visible_through_readonly_status_endpoint(self):
        from test_shadow_operational_status import OperationalStatusTests
        fixture = OperationalStatusTests()
        fixture.setUp()
        try:
            row = fixture.reconcile_claimed()
            fixture.journal.db.execute('UPDATE reconciled_snapshot_bindings SET payload=?',
                (json.dumps({**row,'filled_quantity':1}),))
            self.server.journal_path = fixture.path
            before = fixture.journal.shadow_control(),fixture.journal.db.total_changes
            status,headers,body = self.request('/api/status')
            report = json.loads(body)
            self.assertEqual(status,200)
            self.assertTrue(report['diagnostics_complete'])
            self.assertIn('ORDER_SNAPSHOT_CONTENT_CHANGED',report['local_blockers'])
            self.assertEqual(report['changed_binding_count'],1)
            self.assertFalse(report['real_orders_authorized'])
            self.assertNotIn('PRIVATE',body)
            self.assertEqual(before,(fixture.journal.shadow_control(),fixture.journal.db.total_changes))
        finally: fixture.tearDown()
