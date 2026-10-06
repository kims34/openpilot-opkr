"""Synthetic end-to-end offline lifecycle; no real account/LIVE evidence."""
import unittest
from dataclasses import replace
from decimal import Decimal
import test_journal_settlement_binding as journal_fixtures
import test_kiwoom_settlement_history as history_fixtures
from native_cashflow_binding import ReviewedNativeCashflow
from account_cashflow_reconciliation import SettledCashMovement, CashflowReconciliationError
from kiwoom_settlement_history import SettlementHistoryError
from account_settlement_binding import SettlementAdmission
from native_settlement_readiness import assess_native_settlement_readiness
from kiwoom_account_settlement_evidence import SettlementEvidenceError


class NativeReadinessTests(unittest.TestCase):
    def setUp(self):
        self.local = journal_fixtures.JournalSettlementBindingTests()
        self.local.setUp()
        self.history = history_fixtures.HistoryTests()
        self.body = dict(entr='8999', pymn_alow_amt='0', d2_entra='99999', ord_alow_amt='0')
        movement = SettledCashMovement('synthetic-review', 'a'*64,
            '2026-10-06T09:30:00+09:00', Decimal('-1001'), Decimal('1'))
        self.reviews = [ReviewedNativeCashflow(self.history.normalize().records[0], 'SETTLED_KRW_NET', movement)]

    def tearDown(self):
        self.local.tearDown()

    def assess(self, **changes):
        args = dict(base=self.local.base, settlement=self.local.admission, journal=self.local.journal,
            opening_body={**self.body,'entr':'10000'}, closing_body=self.body,
            account_fingerprint='a'*64, opening_captured_at='2026-10-06T09:00:00+09:00',
            closing_captured_at='2026-10-06T10:00:00+09:00', history_pages=[self.history.page()],
            history_request=self.history.request(), history_captured_at='2026-10-06T10:00:00+09:00',
            reviews=self.reviews, expected_epoch=self.local.epoch,
            expected_snapshot_revision=self.local.revision,
            complete_settlement_scope_attested=True,signed_net_mapping_attested=True,
            fees_tax_completeness_attested=True)
        args.update(changes)
        return assess_native_settlement_readiness(**args)

    def test_full_path_read_only_and_never_order_authority(self):
        self.local.acknowledged()
        before = self.local.journal.db.total_changes
        result = self.assess()
        self.assertTrue(result['ready_for_final_user_authorization'])
        self.assertEqual(before,self.local.journal.db.total_changes)
        self.assertEqual(self.local.journal.shadow_control()['mode'],'MASTER_OFF')
        for report in (result,result['native_history_intake'],result['cashflow_reconciliation']):
            self.assertFalse(report['real_orders_authorized'])
            self.assertFalse(report['broker_request_sent'])
        self.assertNotIn('synthetic-review',repr(result))
        self.assertNotIn('a'*64,repr(result))

    def test_matching_balance_never_repairs_missing_external_evidence(self):
        for changes in (dict(settlement=SettlementAdmission()),
                        dict(signed_net_mapping_attested=False),
                        dict(fees_tax_completeness_attested=False)):
            self.assertFalse(self.assess(**changes)['ready_for_final_user_authorization'])

    def test_late_execution_between_reviews_and_assessment_vetoes(self):
        self.local.acknowledged()
        self.local.journal.record_execution('synthetic-intent',broker_order_id='synthetic-order',
            execution_id='synthetic-late-fill',quantity=2)
        self.assertFalse(self.assess()['ready_for_final_user_authorization'])

    def test_unknown_submission_cannot_hide_behind_empty_history_scope(self):
        self.local.claimed()
        result = self.assess()
        self.assertEqual(result['durable_unresolved_reconciliation_count'],1)
        self.assertFalse(result['ready_for_final_user_authorization'])

    def test_native_page_or_review_omission_stops_full_pipeline(self):
        with self.assertRaises(SettlementHistoryError):
            self.assess(history_pages=[replace(self.history.page(),response_cont_yn='Y',response_next_key='more')])
        with self.assertRaises(CashflowReconciliationError): self.assess(reviews=[])

    def test_unexplained_cash_and_kill_latch_independently_veto(self):
        self.assertFalse(self.assess(closing_body={**self.body,'entr':'9000'})['ready_for_final_user_authorization'])
        self.local.journal.trip_kill_switch()
        self.local.reconcile()
        result = self.assess()
        self.assertFalse(result['ready_for_final_user_authorization'])
        self.assertIn('KILL_SWITCH_LATCHED',result['local_reconciliation_errors'])

    def test_explicit_cash_response_failure_vetoes_even_supplied_external_flags(self):
        before = self.local.journal.shadow_control(),self.local.journal.db.total_changes
        for name in ('opening_body','closing_body'):
            with self.assertRaises(SettlementEvidenceError):
                self.assess(**{name:{**self.body,'return_code':1}})
        self.assertEqual(before,(self.local.journal.shadow_control(),self.local.journal.db.total_changes))
