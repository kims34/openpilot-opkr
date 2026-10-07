"""Private append-only normalized execution diagnostics, no network/sender.

Receipt identity is a caller-supplied local identity, not broker provenance.
Persist before applying. A crash after bridge commit but before the attempt
marker causes replay of the same native execution, which is idempotent. Never
guess missing events, reorder arrivals, or clear reconciliation automatically.
"""
from contextlib import contextmanager
import hashlib
import json

from kiwoom_order_journal_bridge import NativeBridgeError, require
from order_intent_journal import record_component_initialization, validate_stored_component_history
from research_v1_kiwoom_native_execution import OFFICIAL_SCHEMA_COMMIT, SOURCE_CONTRACT


class ExecutionInboxError(ValueError):
    pass


TEXT_FIELDS = frozenset('''source_contract official_schema_commit broker source_api
record_granularity privacy_safe_event_sha256 account_fingerprint broker_order_id
broker_execution_id original_order_id symbol order_status order_business_type
order_type trade_type side broker_lifecycle_time order_qty order_price remaining_qty
cumulative_fill_amount fill_price fill_qty unit_fill_price unit_fill_qty fee tax
rejection_reason exchange_code exchange_name sor_flag'''.split())
BOOL_FIELDS = frozenset('''broker_execution_id_available_in_source
broker_native_structure_normalized genuine_live_provenance_verified
project_live_evidence_admitted'''.split())


class KiwoomExecutionInbox:
    def __init__(self, bridge):
        self.bridge = bridge
        self.journal = bridge.journal
        with self._guard():
            validate_stored_component_history(self.journal.db)
            tables = {row[0] for row in self.journal.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            required = {'native_inbox_receipts','native_inbox_conflicts','native_inbox_attempts'}
            require(not tables & required or required <= tables)
            for name, columns in (
                ('native_inbox_receipts', 'sequence INTEGER PRIMARY KEY AUTOINCREMENT, receipt_id TEXT UNIQUE NOT NULL, key TEXT NOT NULL, day TEXT NOT NULL, payload TEXT NOT NULL, digest TEXT NOT NULL'),
                ('native_inbox_conflicts', 'sequence INTEGER PRIMARY KEY AUTOINCREMENT, receipt_id TEXT NOT NULL, key TEXT NOT NULL, day TEXT NOT NULL, payload TEXT NOT NULL, digest TEXT NOT NULL'),
                ('native_inbox_attempts', 'sequence INTEGER PRIMARY KEY AUTOINCREMENT, receipt_sequence INTEGER NOT NULL, outcome TEXT NOT NULL CHECK(outcome IN (\'APPLIED\',\'DUPLICATE\',\'BLOCKED\'))'),
            ):
                self.journal.db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({columns})')
                for operation in ('UPDATE', 'DELETE'):
                    self.journal.db.execute(f'''CREATE TRIGGER IF NOT EXISTS {name}_{operation.lower()}_immutable
                        BEFORE {operation} ON {name} BEGIN SELECT RAISE(ABORT,'immutable normalized inbox'); END''')
            self._audit_existing_locked()
            record_component_initialization(self.journal.db, 'inbox')

    @contextmanager
    def _guard(self):
        try:
            with self.bridge._guard():
                yield
        except NativeBridgeError:
            raise ExecutionInboxError('EXECUTION_INBOX_RECONCILIATION_REQUIRED') from None

    @staticmethod
    def _text(value):
        require(isinstance(value, str) and bool(value.strip()) and len(value) <= 256)

    @staticmethod
    def _report(result, **extra):
        return dict(mode='OFFLINE_NORMALIZED_EXECUTION_INBOX', result=result,
            network_request_attempted=False, broker_request_sent=False,
            raw_broker_artifact_retained=False, real_account_origin_verified=False,
            source_provenance_admitted=False, live_ordering_authorized=False, **extra)

    def _validate_row(self, row):
        require(isinstance(row, dict) and set(row) == TEXT_FIELDS | BOOL_FIELDS)
        require(all(isinstance(row[f], str) and len(row[f]) <= 4096 for f in TEXT_FIELDS))
        require(all(type(row[f]) is bool for f in BOOL_FIELDS))
        require(row['source_contract'] == SOURCE_CONTRACT and row['official_schema_commit'] == OFFICIAL_SCHEMA_COMMIT)
        require(row['broker'] == 'KIWOOM' and row['source_api'] == 'domestic_realtime_order_fill_00')
        require(row['record_granularity'] == 'broker_execution_event' and row['account_fingerprint'] == self.bridge.account)
        require(row['broker_native_structure_normalized'] and row['broker_execution_id_available_in_source'])
        require(not row['genuine_live_provenance_verified'] and not row['project_live_evidence_admitted'])

    @staticmethod
    def _decode_payload(payload):
        def unique_fields(pairs):
            fields = {}
            for key, value in pairs:
                require(key not in fields)
                fields[key] = value
            return fields

        try:
            return json.loads(payload, object_pairs_hook=unique_fields)
        except RecursionError:
            # Decoder exhaustion is corrupt durable input, not permission to
            # bypass the existing private rollback/quarantine boundary.
            require(False)

    def _audit_existing_locked(self):
        """Fail closed on durable inbox corruption before any replay is trusted."""
        receipts = {}
        for sequence, receipt_id, key, day, payload, digest in self.journal.db.execute(
                'SELECT sequence,receipt_id,key,day,payload,digest FROM native_inbox_receipts'):
            require(type(sequence) is int and sequence > 0)
            self._text(receipt_id); self._text(key); self.bridge._context(day)
            require(isinstance(payload, str) and isinstance(digest, str))
            require(hashlib.sha256(payload.encode()).hexdigest() == digest)
            row = self._decode_payload(payload)
            self._validate_row(row)
            receipts[sequence] = (key, day, row)
        for receipt_id, key, day, payload, digest in self.journal.db.execute(
                'SELECT receipt_id,key,day,payload,digest FROM native_inbox_conflicts'):
            self._text(receipt_id); self._text(key); self.bridge._context(day)
            require(isinstance(payload, str) and isinstance(digest, str))
            require(hashlib.sha256(payload.encode()).hexdigest() == digest)
            self._validate_row(self._decode_payload(payload))
            require(self.journal.db.execute(
                'SELECT 1 FROM native_inbox_receipts WHERE receipt_id=?', (receipt_id,)).fetchone() is not None)
        for receipt_sequence, outcome in self.journal.db.execute(
                'SELECT receipt_sequence,outcome FROM native_inbox_attempts'):
            require(receipt_sequence in receipts and outcome in ('APPLIED', 'DUPLICATE', 'BLOCKED'))
            if outcome in ('APPLIED', 'DUPLICATE'):
                key, day, row = receipts[receipt_sequence]
                # A terminal attempt marker must never hide a receipt whose
                # durable native binding/execution disappeared or never existed.
                self.bridge._verify_existing_execution_locked(key,row,trading_date=day)

    def append(self, receipt_id, key, row, *, trading_date):
        """Persist a normalized copy before any execution-journal mutation."""
        conflict = False
        with self._guard():
            self._text(receipt_id); self._text(key)
            self.bridge._context(trading_date)
            self._validate_row(row)
            payload = json.dumps(row, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
            digest = hashlib.sha256(payload.encode()).hexdigest()
            old = self.journal.db.execute('SELECT key,day,payload,digest FROM native_inbox_receipts WHERE receipt_id=?', (receipt_id,)).fetchone()
            material = (key, trading_date, payload, digest)
            if old is None:
                self.journal.db.execute('INSERT INTO native_inbox_receipts(receipt_id,key,day,payload,digest) VALUES(?,?,?,?,?)', (receipt_id, *material))
                self.journal.db.execute('UPDATE reconciliation_barrier SET blocked=1 WHERE id=1')
                self.journal.db.execute('DELETE FROM reconciled_snapshot_bindings')
                self.journal._stop_shadow('NORMALIZED_EXECUTION_PENDING')
            elif old != material:
                # Preserve the alternate delivery before quarantining. It must
                # never replace the original receipt or be applied implicitly.
                self.journal.db.execute('INSERT INTO native_inbox_conflicts(receipt_id,key,day,payload,digest) VALUES(?,?,?,?,?)', (receipt_id, *material))
                # Persist the alternate and quarantine in the SAME commit.
                # A crash after this commit cannot retain an enabled mode.
                self.journal.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE state!='INTENT_CREATED'")
                self.journal.db.execute('UPDATE reconciliation_barrier SET blocked=1 WHERE id=1')
                self.journal.db.execute('DELETE FROM reconciled_snapshot_bindings')
                self.journal._stop_shadow('NORMALIZED_EXECUTION_CONFLICT')
                conflict = True
        if conflict:
            raise ExecutionInboxError('EXECUTION_INBOX_RECONCILIATION_REQUIRED') from None
        return self._report('RECEIPT_PERSISTED' if old is None else 'DUPLICATE_RECEIPT')

    def replay(self, receipt_id):
        sequence = None
        try:
            with self._guard():
                self._text(receipt_id)
                record = self.journal.db.execute('SELECT sequence,key,day,payload,digest FROM native_inbox_receipts WHERE receipt_id=?', (receipt_id,)).fetchone()
                require(record is not None)
                stored_sequence, key, day, payload, digest = record
                require(type(stored_sequence) is int and stored_sequence > 0)
                sequence = stored_sequence
                require(hashlib.sha256(payload.encode()).hexdigest() == digest)
                row = self._decode_payload(payload)
                # A conflicting receipt requires an independent resolution;
                # neither the original nor alternate may silently win.
                require(not self.journal.db.execute('SELECT 1 FROM native_inbox_conflicts WHERE receipt_id=?', (receipt_id,)).fetchone())
                # Hold the write lock from receipt/conflict verification through
                # fill binding. No competing conflict can commit in between.
                result = self.bridge._apply_execution_locked(key, row, trading_date=day)
            outcome = 'APPLIED' if result['executions_created'] else 'DUPLICATE'
            with self._guard():
                self.journal.db.execute('INSERT INTO native_inbox_attempts(receipt_sequence,outcome) VALUES(?,?)', (sequence, outcome))
        except (ExecutionInboxError, NativeBridgeError):
            if sequence is not None:
                with self._guard():
                    self.journal.db.execute("INSERT INTO native_inbox_attempts(receipt_sequence,outcome) VALUES(?,'BLOCKED')", (sequence,))
            raise ExecutionInboxError('EXECUTION_INBOX_RECONCILIATION_REQUIRED') from None
        return self._report(outcome, executions_created=result['executions_created'])

    def replay_next(self):
        """Arrival order only. Missing-first recovery needs explicit replay()."""
        with self._guard():
            row = self.journal.db.execute('''SELECT r.receipt_id FROM native_inbox_receipts r
                WHERE NOT EXISTS (SELECT 1 FROM native_inbox_attempts a WHERE
                    a.receipt_sequence=r.sequence AND a.outcome IN ('APPLIED','DUPLICATE'))
                ORDER BY r.sequence LIMIT 1''').fetchone()
        return self.replay(row[0]) if row else self._report('NO_PENDING_RECEIPT', executions_created=False)

    def counts(self):
        """Public-safe diagnostics: no identifiers, payloads, hashes or account."""
        with self._guard():
            counts = {name: self.journal.db.execute(f'SELECT COUNT(*) FROM native_inbox_{name}').fetchone()[0]
                for name in ('receipts', 'conflicts', 'attempts')}
            counts['pending'] = self.journal.db.execute('''SELECT COUNT(*) FROM native_inbox_receipts r
                WHERE NOT EXISTS (SELECT 1 FROM native_inbox_attempts a WHERE
                    a.receipt_sequence=r.sequence AND a.outcome IN ('APPLIED','DUPLICATE'))''').fetchone()[0]
        return self._report('COUNTS_ONLY', **counts)
