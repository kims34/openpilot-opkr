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
        except OrderJournalError:
            # Persist after the failed event transaction rolled back.
            with self._atomic():
                self.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE key=? AND state!='INTENT_CREATED'", (key,))
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

    def claim_submission(self, key):
        """Exactly one local claimant; this method itself sends nothing."""
        self._text(key)
        with self._atomic():
            if self.db.execute("SELECT 1 FROM intents WHERE state='RECONCILIATION_REQUIRED' OR (state='SUBMITTING' AND key!=?) LIMIT 1", (key,)).fetchone():
                raise OrderJournalError("unresolved journal state blocks new submissions")
            updated = self.db.execute("UPDATE intents SET state='SUBMITTING' WHERE key=? AND state='INTENT_CREATED'", (key,)).rowcount
            if updated != 1:
                raise OrderJournalError("submission already claimed or intent unknown; reconcile before retry")
        return self.get(key)

    def mark_uncertain(self, key):
        with self._atomic():
            row = self.get(key)
            if row["state"] not in ("SUBMITTING", "ACKNOWLEDGED", "PARTIALLY_FILLED", "RECONCILIATION_REQUIRED"):
                raise OrderJournalError("intent cannot become uncertain in this state")
            self.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE key=?", (key,))
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
            self.db.execute("UPDATE intents SET broker_order_id=? WHERE key=?", (broker_order_id, key))
            if row["state"] == "SUBMITTING":
                self.db.execute("UPDATE intents SET state='ACKNOWLEDGED' WHERE key=?", (key,))
        return self.get(key)

    @quarantine_conflict
    def record_execution(self, key, *, broker_order_id, execution_id, quantity):
        self._text(broker_order_id)
        self._text(execution_id)
        if type(quantity) is not int or quantity <= 0:
            raise OrderJournalError("execution quantity must be a positive integer")
        with self._atomic():
            row = self.get(key)
            if row["broker_order_id"] != broker_order_id:
                raise OrderJournalError("execution requires matching bound broker order")
            if row["state"] in ("INTENT_CREATED", "REJECTED"):
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
                # A late fill may cross a cancellation. Never erase executions.
                state = "FILLED" if filled == row["quantity"] else (
                    row["state"] if row["state"] in ("CANCELLED", "RECONCILIATION_REQUIRED") else "PARTIALLY_FILLED")
                self.db.execute("UPDATE intents SET filled=?,state=? WHERE key=?", (filled, state, key))
                if state == "FILLED":
                    self.db.execute("UPDATE intents SET terminal_status='FILLED' WHERE key=?", (key,))
        return self.get(key)

    def mark_cancel_requested(self, key):
        with self._atomic():
            row = self.get(key)
            if row["state"] not in ("ACKNOWLEDGED", "PARTIALLY_FILLED"):
                raise OrderJournalError("cancel requires a known open order")
            # A request is not evidence of successful cancellation.
            self.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE key=?", (key,))
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
        return self.get(key)

    def recover(self):
        """Startup/reconnect blocks every previously open or uncertain intent."""
        with self._atomic():
            self.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE state IN ('SUBMITTING','ACKNOWLEDGED','PARTIALLY_FILLED')")
        return [self.get(row[0]) for row in self.db.execute("SELECT key FROM intents WHERE state='RECONCILIATION_REQUIRED' ORDER BY key")]
