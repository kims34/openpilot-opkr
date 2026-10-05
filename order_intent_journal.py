"""Broker-neutral durable intent diagnostics. No network, sender or LIVE admission.

Persist a claim before any future adapter submission. A lost response remains
uncertain across restart: retry is forbidden until independently reconciled.
Events here are structural/offline inputs, never empirical execution evidence.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from functools import wraps


class OrderJournalError(ValueError):
    pass


def quarantine_conflict(method):
    @wraps(method)
    def guarded(self, key, *args, **kwargs):
        try:
            return method(self, key, *args, **kwargs)
        except (OrderJournalError, sqlite3.IntegrityError) as error:
            # Persist after the failed event transaction rolled back.
            with self._atomic():
                if isinstance(key, str):
                    self.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE key=? AND state!='INTENT_CREATED'", (key,))
                self._stop_shadow("EVENT_CONFLICT")
            if isinstance(error, sqlite3.IntegrityError):
                raise OrderJournalError('journal persistence conflict') from None
            raise
    return guarded


class OrderIntentJournal:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=10)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS intents (
                key TEXT PRIMARY KEY, payload TEXT NOT NULL,
                state TEXT NOT NULL, broker_order_id TEXT, terminal_status TEXT,
                filled INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS executions (
                key TEXT NOT NULL, execution_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                PRIMARY KEY(key, execution_id));
            CREATE TABLE IF NOT EXISTS shadow_control (
                id INTEGER PRIMARY KEY CHECK(id=1), epoch INTEGER NOT NULL,
                mode TEXT NOT NULL CHECK(mode IN ('MASTER_OFF','SHADOW')),
                killed INTEGER NOT NULL CHECK(killed IN (0,1)), reason TEXT NOT NULL);
            INSERT OR IGNORE INTO shadow_control VALUES(1,0,'MASTER_OFF',0,'STARTUP');
            CREATE TABLE IF NOT EXISTS reconciliation_barrier (
                id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL,
                blocked INTEGER NOT NULL CHECK(blocked IN (0,1)));
            INSERT OR IGNORE INTO reconciliation_barrier VALUES(1,0,0);
            CREATE TABLE IF NOT EXISTS reconciled_snapshot_bindings (
                key TEXT PRIMARY KEY, revision INTEGER NOT NULL,
                epoch INTEGER NOT NULL, payload TEXT NOT NULL);
            CREATE UNIQUE INDEX IF NOT EXISTS single_broker_order_binding
                ON intents(broker_order_id) WHERE broker_order_id IS NOT NULL;
        """)
        # Every new connection is treated conservatively as startup/reconnect.
        # An in-flight submission on another connection also becomes uncertain.
        self.recover()

    def close(self):
        self.db.close()

    @contextmanager
    def _atomic(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self.db.rollback()
            raise
        else:
            self.db.commit()

    @staticmethod
    def _text(value):
        if not isinstance(value, str) or not value.strip():
            raise OrderJournalError("identity must be a nonempty string")
        return value

    def get(self, key):
        self._text(key)
        row = self.db.execute(
            "SELECT payload,state,broker_order_id,filled,terminal_status FROM intents WHERE key=?", (key,)
        ).fetchone()
        if row is None:
            raise OrderJournalError("unknown intent")
        payload = json.loads(row[0])
        return dict(key=key, **payload, state=row[1], broker_order_id=row[2],
                    filled_quantity=row[3], remaining_quantity=payload["quantity"]-row[3],
                    terminal_status=row[4], live_ordering_authorized=False, genuine_live_evidence=False)

    @quarantine_conflict
    def register(self, key, *, symbol, side, quantity):
        self._text(key)
        self._text(symbol)
        if side not in ("BUY", "SELL") or type(quantity) is not int or quantity <= 0:
            raise OrderJournalError("invalid order payload")
        payload = json.dumps(dict(symbol=symbol, side=side, quantity=quantity), sort_keys=True)
        with self._atomic():
            existing = self.db.execute("SELECT payload FROM intents WHERE key=?", (key,)).fetchone()
            if existing and existing[0] != payload:
                raise OrderJournalError("idempotency key collision")
            self.db.execute("INSERT OR IGNORE INTO intents(key,payload,state) VALUES(?,?,'INTENT_CREATED')", (key, payload))
        return self.get(key)

    def shadow_control(self):
        row = self.db.execute("SELECT epoch,mode,killed,reason FROM shadow_control WHERE id=1").fetchone()
        if row is None:
            raise OrderJournalError("missing safety state")
        return dict(epoch=row[0], mode=row[1], killed=bool(row[2]), reason=row[3], live_ordering_authorized=False)

    def _check_epoch(self, expected_epoch):
        if type(expected_epoch) is not int or expected_epoch < 0:
            raise OrderJournalError("expected epoch must be a nonnegative integer")
        control = self.shadow_control()
        if expected_epoch != control["epoch"]:
            raise OrderJournalError("stale safety epoch")
        return control

    def _stop_shadow(self, reason, *, kill=False):
        self.db.execute("UPDATE shadow_control SET epoch=epoch+1,mode='MASTER_OFF',killed=MAX(killed,?),reason=? WHERE id=1", (int(kill), reason))

    def disable_shadow(self):
        with self._atomic():
            self._stop_shadow("OPERATOR_OFF")
        return self.shadow_control()

    def trip_kill_switch(self):
        """Latch local claims OFF. Never cancel, sell or send broker requests."""
        with self._atomic():
            self._stop_shadow("KILL_SWITCH", kill=True)
        return self.shadow_control()

    def reset_kill_switch(self, *, expected_epoch):
        with self._atomic():
            self._check_epoch(expected_epoch)
            self._require_batch_reconciled()
            if self.db.execute("SELECT 1 FROM intents WHERE state IN ('SUBMITTING','RECONCILIATION_REQUIRED') LIMIT 1").fetchone():
                raise OrderJournalError("unresolved state prevents kill reset")
            self.db.execute("UPDATE shadow_control SET epoch=epoch+1,mode='MASTER_OFF',killed=0,reason='EXPLICIT_RESET' WHERE id=1")
        return self.shadow_control()

    def enable_shadow(self, *, expected_epoch):
        """Enable offline diagnostics only; never PAPER or LIVE authority."""
        with self._atomic():
            control = self._check_epoch(expected_epoch)
            if control["killed"]:
                raise OrderJournalError("kill switch is latched")
            self._require_batch_reconciled()
            if self.db.execute("SELECT 1 FROM intents WHERE state IN ('SUBMITTING','RECONCILIATION_REQUIRED') LIMIT 1").fetchone():
                raise OrderJournalError("unresolved state prevents shadow enable")
            self.db.execute("UPDATE shadow_control SET epoch=epoch+1,mode='SHADOW',reason='EXPLICIT_SHADOW_ENABLE' WHERE id=1")
        return self.shadow_control()

    def claim_submission(self, key, *, expected_epoch=None):
        """Exactly one local shadow claimant; this method sends nothing."""
        self._text(key)
        with self._atomic():
            self._claim_submission_locked(key, expected_epoch=expected_epoch)
        return self.get(key)

    def _claim_submission_locked(self, key, *, expected_epoch):
        """Use only inside the journal transaction, including capital reservation."""
        control = self._check_epoch(expected_epoch)
        if control["mode"] != "SHADOW" or control["killed"]:
            raise OrderJournalError("shadow claims disabled")
        self._require_batch_reconciled()
        # Once the optional offline allocator is initialized, BUY claims must
        # use its durable reservation path; the legacy entry cannot bypass it.
        if self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='shadow_capital_config'").fetchone():
            order = self.get(key)
            if order['side'] == 'BUY':
                enabled = self.db.execute('SELECT enabled FROM shadow_capital_config WHERE id=1').fetchone()
                reserved = self.db.execute('SELECT 1 FROM shadow_capital_reservations WHERE key=?', (key,)).fetchone()
                if enabled is None or not enabled[0] or not reserved:
                    raise OrderJournalError('BUY requires enabled durable capital reservation')
        if self.db.execute("SELECT 1 FROM intents WHERE state='RECONCILIATION_REQUIRED' OR (state='SUBMITTING' AND key!=?) LIMIT 1", (key,)).fetchone():
            raise OrderJournalError("unresolved journal state blocks new submissions")
        updated = self.db.execute("UPDATE intents SET state='SUBMITTING' WHERE key=? AND state='INTENT_CREATED'", (key,)).rowcount
        if updated != 1:
            raise OrderJournalError("submission already claimed or intent unknown; reconcile before retry")

    def mark_uncertain(self, key):
        with self._atomic():
            row = self.get(key)
            if row["state"] not in ("SUBMITTING", "ACKNOWLEDGED", "PARTIALLY_FILLED", "RECONCILIATION_REQUIRED"):
                raise OrderJournalError("intent cannot become uncertain in this state")
            self.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE key=?", (key,))
            self._stop_shadow("UNCERTAIN_OUTCOME")
        return self.get(key)

    @quarantine_conflict
    def bind_acknowledgement(self, key, broker_order_id):
        """Offline binding only; no source or broker authority is inferred."""
        self._text(broker_order_id)
        with self._atomic():
            row = self.get(key)
            if row["state"] == "INTENT_CREATED":
                raise OrderJournalError("submission was not claimed")
            if row["broker_order_id"] not in (None, broker_order_id):
                raise OrderJournalError("broker order identity conflict")
            if self.db.execute("SELECT 1 FROM intents WHERE broker_order_id=? AND key!=?", (broker_order_id, key)).fetchone():
                raise OrderJournalError("broker order already bound to another intent")
            self.db.execute("UPDATE intents SET broker_order_id=? WHERE key=?", (broker_order_id, key))
            if row["state"] == "SUBMITTING":
                self.db.execute("UPDATE intents SET state='ACKNOWLEDGED' WHERE key=?", (key,))
        return self.get(key)

    @quarantine_conflict
    def record_execution(self, key, *, broker_order_id, execution_id, quantity):
        with self._atomic():
            self._record_execution_locked(key, broker_order_id=broker_order_id,
                execution_id=execution_id, quantity=quantity)
        return self.get(key)

    def _record_execution_locked(self, key, *, broker_order_id, execution_id, quantity):
        """Called only inside a journal transaction, including source binding."""
        self._text(broker_order_id)
        self._text(execution_id)
        if type(quantity) is not int or quantity <= 0:
            raise OrderJournalError("execution quantity must be a positive integer")
        row = self.get(key)
        if row["broker_order_id"] != broker_order_id:
            raise OrderJournalError("execution requires matching bound broker order")
        if row["state"] in ("INTENT_CREATED", "REJECTED") or row["terminal_status"] == "REJECTED":
            raise OrderJournalError("execution contradicts order state")
        prior = self.db.execute("SELECT quantity FROM executions WHERE key=? AND execution_id=?", (key, execution_id)).fetchone()
        if prior:
            if prior[0] != quantity:
                raise OrderJournalError("conflicting duplicate execution")
        else:
            filled = row["filled_quantity"] + quantity
            if filled > row["quantity"]:
                raise OrderJournalError("execution exceeds requested quantity")
            self.db.execute("INSERT INTO executions VALUES(?,?,?)", (key, execution_id, quantity))
            late_cancel = row['terminal_status'] == 'CANCELLED'
            if late_cancel:
                self._restore_released_principal_locked(key, execution_id)
                self.db.execute('UPDATE reconciliation_barrier SET blocked=1 WHERE id=1')
                self.db.execute('DELETE FROM reconciled_snapshot_bindings')
                self._stop_shadow('LATE_FILL_AFTER_CANCEL')
            # A late fill may cross a cancellation. Never erase executions.
            state = "RECONCILIATION_REQUIRED" if late_cancel or row["state"] == "RECONCILIATION_REQUIRED" else "FILLED" if filled == row["quantity"] else (
                row["state"] if row["state"] in ("CANCELLED", "RECONCILIATION_REQUIRED") else "PARTIALLY_FILLED")
            self.db.execute("UPDATE intents SET filled=?,state=? WHERE key=?", (filled, state, key))
            if filled == row["quantity"]:
                self.db.execute("UPDATE intents SET terminal_status='FILLED' WHERE key=?", (key,))

    def _restore_released_principal_locked(self, key, execution_id):
        """Revoke a local zero-fill release without losing the original audit.

        An actual late fill must be retained even when conservative exposure
        now exceeds the configured ceiling. Nothing here moves broker funds.
        """
        if not self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='shadow_capital_releases'").fetchone():
            return
        released = self.db.execute('SELECT released_principal FROM shadow_capital_releases WHERE key=?', (key,)).fetchone()
        if released is None:
            return
        self.db.execute('''CREATE TABLE IF NOT EXISTS shadow_capital_release_revocations (
            key TEXT PRIMARY KEY, restored_principal INTEGER NOT NULL,
            execution_id TEXT NOT NULL)''')
        if self.db.execute('SELECT 1 FROM shadow_capital_release_revocations WHERE key=?', (key,)).fetchone():
            return
        reservation = self.db.execute('SELECT reserve,fee_buffer FROM shadow_capital_reservations WHERE key=?', (key,)).fetchone()
        if reservation is None or reservation[0] != reservation[1]:
            raise OrderJournalError('released capital reservation inconsistent')
        self.db.execute('UPDATE shadow_capital_reservations SET reserve=reserve+? WHERE key=?', (released[0], key))
        self.db.execute('INSERT INTO shadow_capital_release_revocations VALUES(?,?,?)', (key, released[0], execution_id))
        self.db.execute('UPDATE shadow_capital_config SET revision=revision+1 WHERE id=1')

    def _require_batch_reconciled(self):
        row = self.db.execute("SELECT blocked FROM reconciliation_barrier WHERE id=1").fetchone()
        if row is None or row[0]:
            raise OrderJournalError("unresolved batch reconciliation prevents shadow operation")

    def mark_cancel_requested(self, key):
        with self._atomic():
            row = self.get(key)
            if row["state"] not in ("ACKNOWLEDGED", "PARTIALLY_FILLED"):
                raise OrderJournalError("cancel requires a known open order")
            # A request is not evidence of successful cancellation.
            self.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE key=?", (key,))
            self._stop_shadow("CANCEL_OUTCOME_UNKNOWN")
        return self.get(key)

    def reconcile_snapshot(self, key, *, broker_order_id, status, filled_quantity):
        """Compare offline snapshot to execution ledger; mismatch stays blocked.

        Admission of actual broker snapshots belongs to a future independent
        adapter. This diagnostic cannot authorize retries, orders or LIVE data.
        """
        self._text(broker_order_id)
        if status not in ("OPEN", "CANCELLED", "FILLED", "REJECTED"):
            raise OrderJournalError("unknown snapshot status")
        if type(filled_quantity) is not int or filled_quantity < 0:
            raise OrderJournalError("invalid snapshot quantity")
        with self._atomic():
            row = self.get(key)
            matched = row["broker_order_id"] == broker_order_id and filled_quantity == row["filled_quantity"]
            matched = matched and row["state"] != "INTENT_CREATED"
            matched = matched and ((status == "FILLED") == (filled_quantity == row["quantity"]))
            matched = matched and (status != "REJECTED" or filled_quantity == 0)
            # Terminal states must not be resurrected by stale snapshots.
            matched = matched and (row["terminal_status"] is None or status == row["terminal_status"])
            state = ("PARTIALLY_FILLED" if filled_quantity else "ACKNOWLEDGED") if status == "OPEN" else status
            self.db.execute("UPDATE intents SET state=? WHERE key=?", (state if matched else "RECONCILIATION_REQUIRED", key))
            if matched and status in ("CANCELLED", "REJECTED", "FILLED"):
                self.db.execute("UPDATE intents SET terminal_status=? WHERE key=?", (status, key))
            if not matched:
                self._stop_shadow("SNAPSHOT_CONFLICT")
        return self.get(key)

    def recover(self):
        """Startup/reconnect blocks every previously open or uncertain intent."""
        with self._atomic():
            self._stop_shadow("STARTUP_OR_RECONNECT")
            self.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE state IN ('SUBMITTING','ACKNOWLEDGED','PARTIALLY_FILLED')")
        return [self.get(row[0]) for row in self.db.execute("SELECT key FROM intents WHERE state='RECONCILIATION_REQUIRED' ORDER BY key")]
