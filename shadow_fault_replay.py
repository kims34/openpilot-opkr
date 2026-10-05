"""Synthetic cross-component fault replay; no strategy or broker admission.

Uses only fresh temporary SQLite databases. Never reads the sealed holdout,
production databases, credentials, quotes or broker endpoints.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from indexalert_automation_control import (
    AutomationCapitalState, AutomationControlError, AutomationUserControls,
    DecisionAction, EngineOrderIntent, validate_engine_plan,
)
from order_intent_journal import OrderIntentJournal, OrderJournalError


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


if __name__ == '__main__':
    print(json.dumps(run_offline_fault_replay(), sort_keys=True))
