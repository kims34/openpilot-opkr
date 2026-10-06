"""Synthetic cross-component fault replay; no strategy or broker admission.

Uses only fresh temporary SQLite databases. Never reads the sealed holdout,
production databases, credentials, quotes or broker endpoints.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from indexalert_automation_control import (
    AutomationCapitalState, AutomationControlError, AutomationUserControls,
    DecisionAction, EngineOrderIntent, validate_engine_plan,
)
from order_intent_journal import OrderIntentJournal, OrderJournalError
from order_snapshot_reconciliation import reconcile_order_snapshot_batch
from shadow_capital_allocator import ShadowCapitalAllocator
from kiwoom_order_journal_bridge import KiwoomOrderJournalBridge, NativeBridgeError
from kiwoom_execution_inbox import KiwoomExecutionInbox
from kiwoom_type00_frame_extractor import extract_type00_events
from kiwoom_protected_execution_intake import (
    ProtectedAccountBinding, KiwoomProtectedExecutionIntake, ProtectedIntakeError,
)


def _require(condition, message):
    if not condition:
        raise RuntimeError(message)


def _denied(call, error):
    try:
        call()
    except error:
        return
    raise RuntimeError('expected fail-closed refusal was absent')


def run_offline_fault_replay():
    completed = []
    with tempfile.TemporaryDirectory(prefix='indexalert-shadow-replay-') as root:
        journal = OrderIntentJournal(Path(root) / 'synthetic.sqlite')
        try:
            journal.register('synthetic-decision', symbol='SYNTHETIC', side='BUY', quantity=10)
            intent = EngineOrderIntent(DecisionAction.BUY, 'SYNTHETIC', 80)
            enabled = AutomationUserControls(True, 100)
            disabled = AutomationUserControls(False, 100)
            empty_capital = AutomationCapitalState(0, 0)

            _denied(lambda: validate_engine_plan(disabled, empty_capital, [intent]), AutomationControlError)
            _require(journal.get('synthetic-decision')['state'] == 'INTENT_CREATED', 'disabled plan changed order state')
            completed.append('disabled_user_control_blocks_new_exposure')

            _denied(lambda: validate_engine_plan(enabled, AutomationCapitalState(10, 10, 1), [intent]), AutomationControlError)
            completed.append('positions_reservations_and_uncertain_cash_enforce_ceiling')

            idle = validate_engine_plan(enabled, empty_capital, [EngineOrderIntent(DecisionAction.NO_TRADE)])
            _require(idle[0].action == DecisionAction.NO_TRADE and journal.shadow_control()['mode'] == 'MASTER_OFF', 'idle caused enable or exposure')
            completed.append('no_trade_preserves_cash_and_default_off')

            validate_engine_plan(enabled, empty_capital, [intent])
            epoch = journal.enable_shadow(expected_epoch=journal.shadow_control()['epoch'])['epoch']
            journal.trip_kill_switch()
            _denied(lambda: journal.claim_submission('synthetic-decision', expected_epoch=epoch), OrderJournalError)
            _require(journal.get('synthetic-decision')['state'] == 'INTENT_CREATED', 'Kill permitted a claim')
            completed.append('kill_invalidates_previously_enabled_shadow_epoch')

            journal.reset_kill_switch(expected_epoch=journal.shadow_control()['epoch'])
            _require(journal.shadow_control()['mode'] == 'MASTER_OFF', 'reset enabled execution')
            epoch = journal.enable_shadow(expected_epoch=journal.shadow_control()['epoch'])['epoch']
            claimed = journal.claim_submission('synthetic-decision', expected_epoch=epoch)
            _require(not claimed['live_ordering_authorized'] and not claimed['genuine_live_evidence'], 'synthetic claim granted authority')
            journal.mark_uncertain('synthetic-decision')
            journal.close()
            journal = OrderIntentJournal(Path(root) / 'synthetic.sqlite')
            _denied(lambda: journal.claim_submission('synthetic-decision', expected_epoch=epoch), OrderJournalError)
            _denied(lambda: journal.enable_shadow(expected_epoch=journal.shadow_control()['epoch']), OrderJournalError)
            completed.append('timeout_restart_preserves_uncertainty_and_blocks_retry')

            journal.bind_acknowledgement('synthetic-decision', 'synthetic-order')
            journal.reconcile_snapshot('synthetic-decision', broker_order_id='synthetic-order', status='OPEN', filled_quantity=0)
            _require(journal.shadow_control()['mode'] == 'MASTER_OFF', 'reconciliation auto-enabled')
            journal.record_execution('synthetic-decision', broker_order_id='synthetic-order', execution_id='synthetic-fill-1', quantity=4)
            journal.record_execution('synthetic-decision', broker_order_id='synthetic-order', execution_id='synthetic-fill-1', quantity=4)
            _require(journal.get('synthetic-decision')['filled_quantity'] == 4, 'duplicate fill increased exposure')
            completed.append('offline_reconciliation_stays_off_and_deduplicates_fills')

            journal.mark_cancel_requested('synthetic-decision')
            _require(journal.get('synthetic-decision')['remaining_quantity'] == 6, 'cancel request erased residual')
            journal.reconcile_snapshot('synthetic-decision', broker_order_id='synthetic-order', status='CANCELLED', filled_quantity=4)
            journal.record_execution('synthetic-decision', broker_order_id='synthetic-order', execution_id='synthetic-late-fill', quantity=6)
            _require(journal.get('synthetic-decision')['filled_quantity'] == 10, 'late fill lost')
            _require(journal.get('synthetic-decision')['state'] == 'RECONCILIATION_REQUIRED', 'crossed cancel/fill not blocked')
            _require(journal.get('synthetic-decision')['terminal_status'] == 'FILLED', 'full fill fact lost')
            completed.append('cancel_late_fill_race_conserves_executed_quantity')

            _denied(lambda: journal.record_execution('synthetic-decision', broker_order_id='synthetic-order', execution_id='synthetic-late-fill', quantity=5), OrderJournalError)
            _require(journal.get('synthetic-decision')['state'] == 'RECONCILIATION_REQUIRED', 'conflict not quarantined')
            _require(journal.shadow_control()['mode'] == 'MASTER_OFF', 'conflict left controls enabled')
            _require(journal.get('synthetic-decision')['filled_quantity'] == 10, 'conflict changed quantity')
            completed.append('conflicting_execution_preserves_quantity_and_stops_claims')
        finally:
            journal.close()

    return dict(mode='OFFLINE_SYNTHETIC_FAULT_REPLAY', scenarios=completed,
                passed=True, scenario_count=len(completed),
                network_request_attempted=False, broker_request_sent=False,
                sealed_holdout_read=False, strategy_evaluated=False,
                genuine_live_evidence=False, live_ordering_authorized=False,
                production_promotion_authorized=False)


def run_protected_capital_fault_replay():
    """Exercise the protected-input -> durable inbox -> capital path together.

    Every value is synthetic. A local zero-fill release is not settled broker
    cash; the replay verifies that a late fill restores that local reservation.
    """
    completed = []
    with tempfile.TemporaryDirectory(prefix='indexalert-protected-replay-') as root:
        path = Path(root) / 'synthetic.sqlite'
        journal = OrderIntentJournal(path)
        binding = ProtectedAccountBinding(account='synthetic-private-account',
            fingerprint_key=b's' * 32)
        day = '2026-10-05'
        try:
            allocator = ShadowCapitalAllocator(journal)
            allocator.configure(controls=AutomationUserControls(True, 100),
                baseline=AutomationCapitalState(0, 0), expected_revision=0)
            journal.register('synthetic-decision', symbol='005930', side='BUY', quantity=10)
            epoch = journal.enable_shadow(expected_epoch=journal.shadow_control()['epoch'])['epoch']
            allocator.reserve_and_claim_buy('synthetic-decision', limit_price_krw=8,
                fee_buffer_krw=3, expected_epoch=epoch, expected_capital_revision=1)
            journal.bind_acknowledgement('synthetic-decision', 'synthetic-order')
            bridge = KiwoomOrderJournalBridge(journal,
                account_fingerprint=binding.fingerprint, trading_date=day)
            bridge.bind_order('synthetic-decision', broker_order_id='synthetic-order', native_side='2')
            inbox = KiwoomExecutionInbox(bridge)
            intake = KiwoomProtectedExecutionIntake(inbox, binding)
            snapshot = dict(key='synthetic-decision', broker_order_id='synthetic-order',
                symbol='005930', side='BUY', quantity=10, filled_quantity=0, status='CANCELLED')
            _require(reconcile_order_snapshot_batch(journal, revision=1,
                orders=[snapshot])['matched'], 'synthetic cancellation mismatch')
            allocator.release_zero_fill_principal('synthetic-decision',
                expected_epoch=journal.shadow_control()['epoch'],
                expected_capital_revision=1, expected_snapshot_revision=1)
            _require(allocator.state()['managed_reserve_krw'] == 3, 'fee buffer lost')
            journal.trip_kill_switch()
            _require(journal.shadow_control()['killed'], 'Kill did not latch before late fill')
            completed.append('kill_latches_before_late_type00_fill')
            raw = dict(zip(('9201','9203','9001','900','901','902','904','907',
                '908','909','910','911','914','915','913','919'),
                ('synthetic-private-account','synthetic-order','005930','10','8','6','','2',
                 '091501','synthetic-execution','8','4','8','4','체결','')))
            lifecycle = dict(raw)
            lifecycle.update({'902':'10','909':'','910':'','911':'','914':'','915':'','913':'접수'})
            lifecycle_frame = {'trnm':'REAL','data':[{'type':'00','item':'','values':lifecycle}]}
            lifecycle_event = extract_type00_events(lifecycle_frame)[0]
            lifecycle_out = intake.append_for_bound_order(
                'synthetic-lifecycle-receipt', lifecycle_event, trading_date=day)
            _require(lifecycle_out['result'] == 'NON_FILL_EVENT_IGNORED',
                'known type00 lifecycle event entered execution inbox')
            _require(inbox.counts()['receipts'] == 0 and inbox.counts()['pending'] == 0,
                'non-fill lifecycle event poisoned durable execution inbox')
            _require(journal.shadow_control()['killed'], 'ignored lifecycle event cleared Kill latch')
            completed.append('nonfill_type00_lifecycle_precedes_fill_without_poisoning_inbox')
            frame = {'trnm':'REAL','data':[{'type':'00','item':'','values':raw}]}
            extracted = extract_type00_events(frame)
            _require(len(extracted) == 1 and extracted[0]['909'] == 'synthetic-execution',
                'type00 frame extraction lost execution identity')
            raw = extracted[0]
            completed.append('type00_frame_extracts_before_protected_routing')
            intake.append_for_bound_order('synthetic-receipt', raw, trading_date=day)
            _require(journal.shadow_control()['killed'], 'pending late fill cleared Kill latch')
            _denied(lambda: journal.enable_shadow(expected_epoch=journal.shadow_control()['epoch']),
                OrderJournalError)
            completed.append('protected_pending_late_fill_blocks_released_cash_reuse')

            journal.close()
            journal = OrderIntentJournal(path)
            allocator = ShadowCapitalAllocator(journal)
            bridge = KiwoomOrderJournalBridge(journal,
                account_fingerprint=binding.fingerprint, trading_date=day)
            inbox = KiwoomExecutionInbox(bridge)
            intake = KiwoomProtectedExecutionIntake(inbox, binding)
            _require(inbox.counts()['pending'] == 1, 'pending receipt lost on restart')
            _require(journal.shadow_control()['killed'], 'restart cleared Kill latch')
            payload = journal.db.execute('SELECT payload FROM native_inbox_receipts').fetchone()[0]
            _require('synthetic-private-account' not in payload, 'raw account persisted')
            _denied(lambda: journal.enable_shadow(expected_epoch=journal.shadow_control()['epoch']),
                OrderJournalError)
            completed.append('restart_retains_pending_receipt_without_raw_account_or_enable')

            _require(inbox.replay_next()['executions_created'], 'late native fill lost')
            _require(journal.get('synthetic-decision')['filled_quantity'] == 4, 'fill quantity mismatch')
            _require(allocator.state()['managed_reserve_krw'] == 83, 'late principal not restored')
            _require(journal.shadow_control()['mode'] == 'MASTER_OFF', 'late fill enabled claims')
            _require(journal.shadow_control()['killed'], 'late fill replay cleared Kill latch')
            completed.append('protected_native_late_fill_restores_principal_atomically')

            intake.append_for_bound_order('synthetic-redelivery', raw, trading_date=day)
            _require(not inbox.replay_next()['executions_created'], 'redelivery created another fill')
            _require(allocator.state()['managed_reserve_krw'] == 83, 'redelivery changed reservation')
            _require(journal.get('synthetic-decision')['filled_quantity'] == 4, 'redelivery changed quantity')
            completed.append('distinct_protected_redelivery_never_duplicates_fill_or_reserve')

            alternate = dict(raw, **{'910':'9','914':'9'})
            _denied(lambda: intake.append_for_bound_order('synthetic-receipt',
                alternate, trading_date=day), ProtectedIntakeError)
            _require(inbox.counts()['conflicts'] == 1, 'conflicting delivery lost')
            _require(allocator.state()['managed_reserve_krw'] == 83, 'conflict released capital')
            _denied(lambda: journal.enable_shadow(expected_epoch=journal.shadow_control()['epoch']),
                OrderJournalError)
            completed.append('protected_conflict_keeps_quantity_capital_and_master_off')

            _denied(lambda: KiwoomOrderJournalBridge(journal,
                account_fingerprint=binding.fingerprint, trading_date='2026-10-06'), NativeBridgeError)
            _require(allocator.state()['managed_reserve_krw'] == 83, 'day rollover reset capital')
            completed.append('native_day_rebind_cannot_erase_conservative_reservation')
        finally:
            journal.close()
    return dict(mode='OFFLINE_SYNTHETIC_PROTECTED_CAPITAL_FAULT_REPLAY',
        scenarios=completed, scenario_count=len(completed), passed=True,
        network_request_attempted=False, broker_request_sent=False,
        sealed_holdout_read=False, strategy_evaluated=False,
        actual_cash_settlement_verified=False, genuine_live_evidence=False,
        live_ordering_authorized=False, production_promotion_authorized=False)


if __name__ == '__main__':
    replay = run_protected_capital_fault_replay if sys.argv[1:] == ['--protected-capital'] else run_offline_fault_replay
    print(json.dumps(replay(), sort_keys=True))
