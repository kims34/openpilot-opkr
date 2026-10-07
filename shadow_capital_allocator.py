"""Durable synthetic BUY reservations, atomically coupled to local claims.

This is an offline diagnostic allocator, not the broker execution gateway.
The baseline is caller-supplied capital excluding reservations managed here.
Its account provenance is unverified. Reservations never auto-release on ACK,
cancel, fill, timeout or baseline update; no expected sale proceeds are credited.
Explicit whole-batch-confirmed zero-fill terminal diagnostics may return only
principal while retaining the fee buffer. Actual cash reuse still requires an
independently admitted settlement/account adapter.
"""
import json
from contextlib import nullcontext

from indexalert_automation_control import (
    AutomationCapitalState, AutomationUserControls, DecisionAction,
    EngineOrderIntent, validate_engine_plan,
)
from order_intent_journal import OrderJournalError, validate_stored_execution_totals, validate_stored_intent_row, validate_stored_reconciliation_barrier
from order_snapshot_reconciliation import FIELDS, STATUS, load_stored_order_snapshot


def validate_stored_capital_reservations(connection):
    """Pure reservation audit; caller pins one surrounding SQLite snapshot."""
    reserve = 0
    keys = {row[0] for row in connection.execute('SELECT key FROM shadow_capital_reservations')}
    if not {row[0] for row in connection.execute('SELECT key FROM shadow_capital_releases')} <= keys:
        raise OrderJournalError('orphan managed principal release')
    revocations_exist = connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='shadow_capital_release_revocations'").fetchone()
    if revocations_exist and not {row[0] for row in connection.execute('SELECT key FROM shadow_capital_release_revocations')} <= keys:
        raise OrderJournalError('orphan managed principal restoration')
    for key, price, fee, amount in connection.execute(
            'SELECT key,limit_price,fee_buffer,reserve FROM shadow_capital_reservations'):
        row = connection.execute('SELECT payload,state,broker_order_id,filled,terminal_status FROM intents WHERE key=?', (key,)).fetchone()
        if row is None:
            raise OrderJournalError('orphan managed BUY reservation')
        order = validate_stored_intent_row(*row)
        if (order['side'] != 'BUY' or type(price) is not int or price <= 0
            or type(fee) is not int or fee < 0 or type(amount) is not int or amount < 0):
            raise OrderJournalError('invalid managed BUY reservation')
        principal = order['quantity'] * price
        released = connection.execute('SELECT released_principal,snapshot_revision FROM shadow_capital_releases WHERE key=?', (key,)).fetchone()
        revoked = connection.execute('SELECT restored_principal,execution_id FROM shadow_capital_release_revocations WHERE key=?', (key,)).fetchone() if revocations_exist else None
        expected = principal + fee
        if released is not None:
            if (type(released[0]) is not int or released[0] != principal
                or type(released[1]) is not int or released[1] <= 0):
                raise OrderJournalError('invalid managed principal release')
            expected = fee
            if revoked is not None:
                if (type(revoked[0]) is not int or revoked[0] != principal
                    or type(revoked[1]) is not str or not revoked[1].strip()
                    or not connection.execute('SELECT 1 FROM executions WHERE key=? AND execution_id=?', (key,revoked[1])).fetchone()):
                    raise OrderJournalError('invalid managed principal restoration')
                expected = principal + fee
        elif revoked is not None:
            raise OrderJournalError('orphan managed principal restoration')
        if amount != expected or expected > 2**63-1:
            raise OrderJournalError('managed BUY reservation amount changed')
        reserve += amount
    return reserve


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
            journal.db.execute('''CREATE TABLE IF NOT EXISTS shadow_capital_releases (
                key TEXT PRIMARY KEY, released_principal INTEGER NOT NULL,
                snapshot_revision INTEGER NOT NULL)''')

    def state(self):
        # Standalone readers need the same pinned view as claim/release callers.
        with nullcontext() if self.journal.db.in_transaction else self.journal._atomic():
            return self._state_locked()

    def _state_locked(self):
        row = self.journal.db.execute(
            'SELECT revision,enabled,maximum,baseline FROM shadow_capital_config WHERE id=1').fetchone()
        if row is None:
            raise OrderJournalError('missing shadow capital configuration')
        revision, enabled, maximum, baseline = row
        try:
            values = json.loads(baseline)
        except (json.JSONDecodeError, RecursionError, TypeError):
            raise OrderJournalError('invalid shadow capital configuration') from None
        if (type(revision) is not int or not 0 <= revision <= 2**63-1
            or type(enabled) is not int or enabled not in (0,1)
            or type(maximum) is not int or not 0 <= maximum <= 2**63-1
            or (enabled and maximum == 0)
            or type(values) is not list or len(values) != 4
            or any(type(value) is not int or not 0 <= value <= 2**63-1 for value in values)):
            raise OrderJournalError('invalid shadow capital configuration')
        # Restoring a late-fill reservation can exceed the ceiling or even the
        # SQLite aggregate integer range. Preserve/report exposure exactly.
        reserve = validate_stored_capital_reservations(self.journal.db)
        return dict(revision=revision, controls=AutomationUserControls(bool(enabled), maximum),
            capital=AutomationCapitalState(*values), managed_reserve_krw=reserve)

    def _revision(self, expected):
        state = self.state()
        if type(expected) is not int or expected != state['revision']:
            raise OrderJournalError('stale or invalid shadow capital revision')
        if state['revision'] == 2**63-1:
            raise OrderJournalError('shadow capital revision exhausted')
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

    def release_zero_fill_principal(self, key, *, expected_epoch,
                                    expected_capital_revision, expected_snapshot_revision):
        """Local accounting only. Never credit partial fills or inferred sale cash."""
        self.journal._text(key)
        with self.journal._atomic():
            state = self._revision(expected_capital_revision)
            control = self.journal._check_epoch(expected_epoch)
            self.journal._require_batch_reconciled()
            validate_stored_execution_totals(self.journal.db,
                dict(self.journal.db.execute('SELECT key,filled FROM intents')))
            if control['mode'] != 'MASTER_OFF':
                raise OrderJournalError('principal release requires MASTER_OFF')
            barrier = validate_stored_reconciliation_barrier(self.journal.db)
            if (type(expected_snapshot_revision) is not int or expected_snapshot_revision <= 0
                or barrier is None or barrier != (expected_snapshot_revision, 0)):
                raise OrderJournalError('complete fresh batch required for principal release')
            binding = self.journal.db.execute('SELECT revision,epoch,payload FROM reconciled_snapshot_bindings WHERE key=?', (key,)).fetchone()
            if binding is None or binding[:2] != (expected_snapshot_revision, expected_epoch):
                raise OrderJournalError('snapshot binding stale or absent')
            snapshot = load_stored_order_snapshot(binding[2])
            if (type(snapshot) is not dict or set(snapshot) != FIELDS
                or any(type(snapshot[field]) is not str or not snapshot[field].strip()
                    for field in ('key','broker_order_id','symbol','side','status'))
                or snapshot['key'] != key or snapshot['status'] not in STATUS
                or type(snapshot['quantity']) is not int or snapshot['quantity'] <= 0
                or type(snapshot['filled_quantity']) is not int
                or not 0 <= snapshot['filled_quantity'] <= snapshot['quantity']):
                raise OrderJournalError('invalid principal release snapshot')
            order = self.journal.get(key)
            if (order['side'] != 'BUY' or order['state'] not in ('CANCELLED', 'REJECTED')
                or order['terminal_status'] != snapshot['status']
                or order['filled_quantity'] != 0 or snapshot['filled_quantity'] != 0
                or any(order[f] != snapshot[f] for f in ('symbol','side','quantity','broker_order_id'))):
                raise OrderJournalError('only confirmed unchanged zero-fill terminal BUY can release principal')
            reservation = self.journal.db.execute('SELECT limit_price,fee_buffer,reserve FROM shadow_capital_reservations WHERE key=?', (key,)).fetchone()
            if reservation is None or self.journal.db.execute('SELECT 1 FROM shadow_capital_releases WHERE key=?', (key,)).fetchone():
                raise OrderJournalError('reservation absent or principal already released')
            price, fee, total = reservation
            if (type(price) is not int or price <= 0
                or type(fee) is not int or fee < 0
                or type(total) is not int or total > 2**63-1
                or total != order['quantity'] * price + fee):
                raise OrderJournalError('invalid unreleased BUY reservation')
            released = total - fee
            self.journal.db.execute('UPDATE shadow_capital_reservations SET reserve=? WHERE key=?', (fee, key))
            self.journal.db.execute('INSERT INTO shadow_capital_releases VALUES(?,?,?)', (key, released, expected_snapshot_revision))
            self.journal.db.execute('UPDATE shadow_capital_config SET revision=revision+1 WHERE id=1')
            self.journal._stop_shadow('ZERO_FILL_PRINCIPAL_RELEASED_OFF')
        return dict(mode='OFFLINE_ZERO_FILL_PRINCIPAL_RELEASE', released_principal_krw=released,
            retained_fee_buffer_krw=fee, network_request_attempted=False,
            funds_movement_attempted=False, broker_request_sent=False,
            account_capital_provenance_verified=False, live_ordering_authorized=False)
