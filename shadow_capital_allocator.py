"""Durable synthetic BUY reservations, atomically coupled to local claims.

This is an offline diagnostic allocator, not the broker execution gateway.
The baseline is caller-supplied capital excluding reservations managed here.
Its account provenance is unverified. Reservations never auto-release on ACK,
cancel, fill, timeout or baseline update; no expected sale proceeds are credited.
An admitted settlement/account adapter is still needed for actual cash reuse.
"""
import json

from indexalert_automation_control import (
    AutomationCapitalState, AutomationUserControls, DecisionAction,
    EngineOrderIntent, validate_engine_plan,
)
from order_intent_journal import OrderJournalError


class ShadowCapitalAllocator:
    def __init__(self, journal):
        self.journal = journal
        with journal._atomic():
            journal.db.execute('''CREATE TABLE IF NOT EXISTS shadow_capital_config (
                id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL,
                enabled INTEGER NOT NULL CHECK(enabled IN (0,1)), maximum INTEGER NOT NULL,
                baseline TEXT NOT NULL)''')
            journal.db.execute('''INSERT OR IGNORE INTO shadow_capital_config
                VALUES(1,0,0,0,'[0,0,0,0]')''')
            journal.db.execute('''CREATE TABLE IF NOT EXISTS shadow_capital_reservations (
                key TEXT PRIMARY KEY, limit_price INTEGER NOT NULL,
                fee_buffer INTEGER NOT NULL, reserve INTEGER NOT NULL)''')

    def state(self):
        row = self.journal.db.execute(
            'SELECT revision,enabled,maximum,baseline FROM shadow_capital_config WHERE id=1').fetchone()
        if row is None:
            raise OrderJournalError('missing shadow capital configuration')
        revision, enabled, maximum, baseline = row
        reserve = self.journal.db.execute('SELECT COALESCE(SUM(reserve),0) FROM shadow_capital_reservations').fetchone()[0]
        return dict(revision=revision, controls=AutomationUserControls(bool(enabled), maximum),
            capital=AutomationCapitalState(*json.loads(baseline)), managed_reserve_krw=reserve)

    def _revision(self, expected):
        state = self.state()
        if type(expected) is not int or expected != state['revision']:
            raise OrderJournalError('stale or invalid shadow capital revision')
        return state

    def configure(self, *, controls, baseline, expected_revision):
        # Reuse the existing frozen user ceiling/accounting rules.
        validate_engine_plan(controls, baseline, [])
        values = [baseline.automated_positions_value_krw,
            baseline.reserved_open_buy_orders_krw,
            baseline.uncertain_submission_reserve_krw, baseline.fees_tax_buffer_krw]
        if any(value > 2**63-1 for value in values+[controls.max_automation_capital_krw]):
            raise OrderJournalError('capital value cannot be stored safely')
        with self.journal._atomic():
            state = self._revision(expected_revision)
            self.journal.db.execute('UPDATE shadow_capital_config SET revision=?,enabled=?,maximum=?,baseline=? WHERE id=1',
                (state['revision']+1, int(controls.automation_enabled),
                 controls.max_automation_capital_krw, json.dumps(values)))
            # A changed user limit/input snapshot requires a fresh local enable.
            self.journal._stop_shadow('CAPITAL_CONFIGURATION_CHANGED')
        return self.state()

    def reserve_and_claim_buy(self, key, *, limit_price_krw, fee_buffer_krw,
                              expected_epoch, expected_capital_revision):
        self.journal._text(key)
        if (type(limit_price_krw) is not int or limit_price_krw <= 0
            or type(fee_buffer_krw) is not int or fee_buffer_krw < 0):
            raise OrderJournalError('invalid conservative BUY price or fee buffer')
        with self.journal._atomic():
            state = self._revision(expected_capital_revision)
            order = self.journal.get(key)
            if order['side'] != 'BUY':
                raise OrderJournalError('allocator only accepts BUY intents')
            for other_key, in self.journal.db.execute("SELECT key FROM intents WHERE key!=? AND state IN ('SUBMITTING','ACKNOWLEDGED','PARTIALLY_FILLED','RECONCILIATION_REQUIRED')", (key,)):
                other = self.journal.get(other_key)
                tracked = self.journal.db.execute('SELECT 1 FROM shadow_capital_reservations WHERE key=?', (other_key,)).fetchone()
                if other['side'] == 'BUY' and not tracked:
                    raise OrderJournalError('unreserved legacy open BUY requires account reconciliation')
            if self.journal.db.execute('SELECT 1 FROM shadow_capital_reservations WHERE key=?', (key,)).fetchone():
                raise OrderJournalError('reservation already exists; no retry or repricing')
            reserve = order['quantity'] * limit_price_krw + fee_buffer_krw
            if reserve > 2**63-1 or state['managed_reserve_krw']+reserve > 2**63-1:
                raise OrderJournalError('reservation cannot be stored safely')
            capital = state['capital']
            accounted = AutomationCapitalState(capital.automated_positions_value_krw,
                capital.reserved_open_buy_orders_krw + state['managed_reserve_krw'],
                capital.uncertain_submission_reserve_krw, capital.fees_tax_buffer_krw)
            validate_engine_plan(state['controls'], accounted,
                [EngineOrderIntent(DecisionAction.BUY, order['symbol'], reserve)])
            # Reservation and claim commit together or both roll back.
            self.journal.db.execute('INSERT INTO shadow_capital_reservations VALUES(?,?,?,?)',
                (key, limit_price_krw, fee_buffer_krw, reserve))
            self.journal._claim_submission_locked(key, expected_epoch=expected_epoch)
            claimed = self.journal.get(key)
        return dict(intent=claimed, reservation_krw=reserve,
            capital_revision=state['revision'], mode='OFFLINE_SHADOW_CAPITAL_CLAIM',
            network_request_attempted=False, broker_request_sent=False,
            account_capital_provenance_verified=False,
            genuine_live_evidence=False, live_ordering_authorized=False)
