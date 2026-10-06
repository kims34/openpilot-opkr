"""Synthetic review artifacts are never authenticated broker evidence."""
import copy
import unittest
from dataclasses import replace
import test_native_settlement_readiness as readiness_fixtures
from account_cashflow_reconciliation import CashflowReconciliationError
from native_cashflow_review_manifest import load_native_cashflow_review_manifest, native_row_digest


class ReviewManifestTests(unittest.TestCase):
    def setUp(self):
        self.local = readiness_fixtures.NativeReadinessTests()
        self.local.setUp()
        self.batch = self.local.history.normalize()
        movement = self.local.reviews[0].movement
        self.manifest = dict(version=1,account_fingerprint='a'*64,
            history_captured_at=self.batch.captured_at,history_request=dict(self.batch.request_fields),
            rows=[dict(native_row_sha256=native_row_digest(self.batch.records[0]),
                disposition='SETTLED_KRW_NET',movement=dict(transaction_id=movement.transaction_id,
                    account_fingerprint=movement.account_fingerprint,settled_at=movement.settled_at,
                    net_cash_delta_krw=str(movement.net_cash_delta_krw),fees_tax_krw=str(movement.fees_tax_krw)))])

    def tearDown(self):
        self.local.tearDown()

    def test_artifact_flows_through_entire_journal_boundary(self):
        result = self.local.assess(reviews=None,review_manifest=self.manifest)
        self.assertTrue(result['preconditions_structurally_satisfied'])
        self.assertFalse(result['independent_gate_admission_verified'])
        self.assertFalse(result['ready_for_final_user_authorization'])
        self.assertIn('INDEPENDENT_GATE_ADMISSION_NOT_IMPLEMENTED', result['blockers'])
        self.assertFalse(result['real_orders_authorized'])
        self.assertFalse(result['genuine_live_provenance_verified'])

    def test_scope_capture_query_and_native_bytes_must_match(self):
        for field,value in (('account_fingerprint','b'*64),
                            ('history_captured_at','2026-10-06T10:01:00+09:00'),
                            ('history_request',{**dict(self.batch.request_fields),'stk_cd':'005930'})):
            with self.assertRaises(CashflowReconciliationError):
                load_native_cashflow_review_manifest({**self.manifest,field:value},self.batch)
        record = self.batch.records[0]
        changed = replace(record,native_fields=tuple(sorted({**dict(record.native_fields),'io_tp':'CHANGED'}.items())))
        with self.assertRaises(CashflowReconciliationError):
            load_native_cashflow_review_manifest(self.manifest,replace(self.batch,records=(changed,)))

    def test_missing_duplicate_and_unknown_rows_reject(self):
        row = self.manifest['rows'][0]
        for rows in ([],[row,row],[{**row,'native_row_sha256':'f'*64}]):
            with self.assertRaises(CashflowReconciliationError):
                load_native_cashflow_review_manifest({**self.manifest,'rows':rows},self.batch)

    def test_amounts_require_exact_decimal_text_and_account_scope(self):
        for field,value in (('net_cash_delta_krw',-1001),('net_cash_delta_krw','NaN'),
                            ('fees_tax_krw','-1'),('account_fingerprint','b'*64),
                            ('settled_at','2026-10-06T09:30:00')):
            manifest = copy.deepcopy(self.manifest)
            manifest['rows'][0]['movement'][field] = value
            with self.assertRaises(CashflowReconciliationError):
                load_native_cashflow_review_manifest(manifest,self.batch)

    def test_manifest_cannot_import_admission_flags_or_unknown_classification(self):
        with self.assertRaises(CashflowReconciliationError):
            load_native_cashflow_review_manifest({**self.manifest,'source_account_origin_authenticated':True},self.batch)
        manifest = copy.deepcopy(self.manifest)
        manifest['rows'][0]['disposition'] = 'UNREVIEWED'
        with self.assertRaises(CashflowReconciliationError):
            load_native_cashflow_review_manifest(manifest,self.batch)

    def test_exclusion_requires_null_and_inputs_cannot_be_combined(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['rows'][0]['disposition'] = 'NON_CASH'
        with self.assertRaises(CashflowReconciliationError):
            load_native_cashflow_review_manifest(manifest,self.batch)
        manifest['rows'][0]['movement'] = None
        self.assertIsNone(load_native_cashflow_review_manifest(manifest,self.batch)[0].movement)
        with self.assertRaises(CashflowReconciliationError):
            self.local.assess(review_manifest=self.manifest)
