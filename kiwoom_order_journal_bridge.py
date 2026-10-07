"""Offline normalized-source binding. No source admission, network or sender.

One journal binds to one declared account fingerprint/trading date. The date
and native side code are external diagnostic scope inputs, not independently
attested origin or semantics. Broker 00 times lack a date. REST aggregates can
only compare existing fills; they can never create per-execution records.
"""
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
import sqlite3

from order_intent_journal import OrderJournalError, validate_stored_execution_totals, record_component_initialization, validate_stored_component_history
from research_v1_kiwoom_native_execution import (
    OFFICIAL_SCHEMA_COMMIT, SOURCE_CONTRACT, KT00007_SOURCE_CONTRACT,
    KA10076_SOURCE_CONTRACT,
)


class NativeBridgeError(ValueError):
    pass


def require(condition):
    if not condition:
        raise NativeBridgeError('NATIVE_SCOPE_OR_SOURCE_CONFLICT')


def number(value, *, integer=False, positive=False):
    require(isinstance(value,str) and bool(value.strip()))
    try:
        n=Decimal(value.replace(',',''))
    except InvalidOperation:
        raise NativeBridgeError('INVALID_NATIVE_NUMBER') from None
    require(n.is_finite() and n >= 0 and (not positive or n > 0))
    if integer:
        require(n==n.to_integral_value() and n <= 2**63-1)
        return int(n)
    return n


def exact_decimal_identity(value):
    """Canonical finite value without context-dependent rounding or arithmetic.

    Decimal.normalize() applies the thread's precision before removing zeros.
    That can collapse different execution prices or change a replay digest.
    Removing trailing coefficient zeros directly preserves every significant
    digit and keeps equivalent decimal/exponent spellings idempotent.
    """
    sign, digits, exponent = value.as_tuple()
    digits = list(digits)
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
        exponent += 1
    return str(Decimal((sign, tuple(digits), exponent)))


class KiwoomOrderJournalBridge:
    def __init__(self,journal,*,account_fingerprint,trading_date):
        self.journal=journal
        self.account=account_fingerprint
        self.day=trading_date
        with self._guard():
            validate_stored_component_history(journal.db)
            require(isinstance(self.account,str) and re.fullmatch(r'sha256:[0-9a-f]{64}',self.account))
            require(isinstance(self.day,str) and date.fromisoformat(self.day).isoformat()==self.day)
            tables = {row[0] for row in journal.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            required = {'native_journal_scope','native_order_bindings','native_fill_bindings'}
            require(not tables & required or (required <= tables and
                journal.db.execute('SELECT 1 FROM native_journal_scope WHERE id=1').fetchone() is not None))
            journal.db.execute('''CREATE TABLE IF NOT EXISTS native_journal_scope (
                id INTEGER PRIMARY KEY CHECK(id=1), account TEXT NOT NULL, day TEXT NOT NULL)''')
            journal.db.execute('''CREATE TABLE IF NOT EXISTS native_order_bindings (
                key TEXT PRIMARY KEY, broker_order_id TEXT UNIQUE NOT NULL, native_side TEXT NOT NULL)''')
            journal.db.execute('''CREATE TABLE IF NOT EXISTS native_fill_bindings (
                key TEXT NOT NULL, execution_id TEXT NOT NULL, digest TEXT NOT NULL,
                payload TEXT NOT NULL, PRIMARY KEY(key,execution_id))''')
            scope=journal.db.execute('SELECT account,day FROM native_journal_scope WHERE id=1').fetchone()
            require(scope is None or scope==(self.account,self.day))
            journal.db.execute('INSERT OR IGNORE INTO native_journal_scope VALUES(1,?,?)',(self.account,self.day))
            validate_stored_execution_totals(journal.db,
                dict(journal.db.execute('SELECT key,filled FROM intents')))
            for key, broker_id, side in journal.db.execute(
                    'SELECT key,broker_order_id,native_side FROM native_order_bindings'):
                order = journal.get(key)
                require(order['state'] != 'INTENT_CREATED' and order['broker_order_id'] == broker_id)
                require(type(side) is str and bool(side.strip()))
            self._audit_existing_fill_bindings_locked()
            record_component_initialization(journal.db, 'native')
            for table in ('native_journal_scope','native_order_bindings','native_fill_bindings'):
                for operation in ('UPDATE','DELETE'):
                    journal.db.execute(f'''CREATE TRIGGER IF NOT EXISTS {table}_{operation.lower()}_immutable
                        BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'immutable native binding'); END''')

    @contextmanager
    def _guard(self):
        try:
            with self.journal._atomic():
                yield
        except (NativeBridgeError,OrderJournalError,ValueError,TypeError,KeyError,sqlite3.IntegrityError):
            # No supplied identifiers, account, raw source or exception text emitted.
            with self.journal._atomic():
                self.journal.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE state!='INTENT_CREATED'")
                self.journal.db.execute('UPDATE reconciliation_barrier SET blocked=1 WHERE id=1')
                self.journal.db.execute('DELETE FROM reconciled_snapshot_bindings')
                self.journal._stop_shadow('NATIVE_BRIDGE_CONFLICT')
            raise NativeBridgeError('NATIVE_BRIDGE_RECONCILIATION_REQUIRED') from None

    def _context(self,day):
        require(day==self.day)
        require(self.journal.db.execute('SELECT account,day FROM native_journal_scope WHERE id=1').fetchone()==(self.account,self.day))

    def _audit_existing_fill_bindings_locked(self):
        """Structural durable audit only; never authenticates stored source."""
        fields = {'account','day','order','symbol','native_side','execution_id',
            'quantity','price','time','remaining'}
        for key, execution, payload in self.journal.db.execute(
                'SELECT key,execution_id,payload FROM native_fill_bindings'):
            try:
                material = json.loads(payload)
            except RecursionError:
                require(False)
            require(type(material) is dict and set(material) == fields)
            require(material['execution_id'] == execution)
            order = self.journal.get(key)
            row = dict(source_contract=SOURCE_CONTRACT,official_schema_commit=OFFICIAL_SCHEMA_COMMIT,
                broker='KIWOOM',record_granularity='broker_execution_event',
                broker_native_structure_normalized=True,genuine_live_provenance_verified=False,
                project_live_evidence_admitted=False,account_fingerprint=material['account'],
                broker_order_id=material['order'],symbol=material['symbol'],
                order_qty=str(order['quantity']),original_order_id='',
                source_api='domestic_realtime_order_fill_00',broker_execution_id_available_in_source=True,
                side=material['native_side'],order_status='체결',rejection_reason='',
                broker_execution_id=execution,fill_qty=str(material['quantity']),
                unit_fill_qty=str(material['quantity']),fill_price=material['price'],
                unit_fill_price=material['price'],remaining_qty=str(material['remaining']),
                broker_lifecycle_time=material['time'])
            self._verify_existing_execution_locked(key,row,trading_date=material['day'])

    def bind_order(self,key,*,broker_order_id,native_side):
        with self._guard():
            self._context(self.day)
            require(isinstance(native_side,str) and bool(native_side.strip()))
            order=self.journal.get(key)
            require(order['state']!='INTENT_CREATED' and order['broker_order_id']==broker_order_id)
            old=self.journal.db.execute('SELECT broker_order_id,native_side FROM native_order_bindings WHERE key=?',(key,)).fetchone()
            require(old is None or old==(broker_order_id,native_side))
            self.journal.db.execute('INSERT OR IGNORE INTO native_order_bindings VALUES(?,?,?)',(key,broker_order_id,native_side))
        return self._report('ORDER_BOUND',executions_created=False)

    def _row(self,key,row,day,source,granularity):
        self._context(day)
        require(isinstance(row,dict))
        require(row.get('source_contract')==source and row.get('official_schema_commit')==OFFICIAL_SCHEMA_COMMIT)
        require(row.get('broker')=='KIWOOM' and row.get('record_granularity')==granularity)
        require(row.get('broker_native_structure_normalized') is True)
        require(row.get('genuine_live_provenance_verified') is False and row.get('project_live_evidence_admitted') is False)
        require(row.get('account_fingerprint')==self.account)
        order=self.journal.get(key)
        binding=self.journal.db.execute('SELECT broker_order_id,native_side FROM native_order_bindings WHERE key=?',(key,)).fetchone()
        require(binding is not None and row.get('broker_order_id')==binding[0]==order['broker_order_id'])
        require(row.get('symbol')==order['symbol'] and number(row.get('order_qty'),integer=True,positive=True)==order['quantity'])
        # Amendment/cancellation chains need independent original-order semantics.
        require(row.get('original_order_id')=='')
        return order,binding

    @staticmethod
    def _report(result,**extra):
        return dict(mode='OFFLINE_KIWOOM_JOURNAL_BRIDGE',result=result,
            network_request_attempted=False,broker_request_sent=False,
            real_account_origin_verified=False,trading_date_origin_attested=False,
            native_side_semantics_attested=False,fees_settled=False,
            genuine_live_evidence=False,live_ordering_authorized=False,**extra)

    def apply_execution(self,key,row,*,trading_date):
        with self._guard():
            return self._apply_execution_locked(key,row,trading_date=trading_date)

    def _execution_material_locked(self,key,row,*,trading_date):
        """Derive execution identity without applying a fill or trusting markers."""
        require(self.journal.db.in_transaction)
        order,binding=self._row(key,row,trading_date,SOURCE_CONTRACT,'broker_execution_event')
        quantities = [record[0] for record in self.journal.db.execute(
            'SELECT quantity FROM executions WHERE key=?', (key,))]
        require(all(type(quantity) is int and quantity > 0 for quantity in quantities))
        require(sum(quantities) == order['filled_quantity'])
        require(row.get('source_api')=='domestic_realtime_order_fill_00')
        require(row.get('broker_execution_id_available_in_source') is True)
        require(row.get('side')==binding[1] and row.get('order_status')=='체결' and row.get('rejection_reason')=='')
        execution=row.get('broker_execution_id')
        require(isinstance(execution,str) and bool(execution.strip()))
        qty=number(row.get('fill_qty'),integer=True,positive=True)
        # Both reported and unit quantities/prices must agree. Ambiguous
        # cumulative-vs-unit data cannot be interpreted as another fill.
        require(qty==number(row.get('unit_fill_qty'),integer=True,positive=True))
        price=number(row.get('fill_price'),positive=True)
        require(price==number(row.get('unit_fill_price'),positive=True))
        remaining=number(row.get('remaining_qty'),integer=True)
        require(qty + remaining <= order['quantity'])
        time=row.get('broker_lifecycle_time')
        require(isinstance(time,str) and re.fullmatch(r'[0-9]{6}',time))
        datetime.strptime(time,'%H%M%S')
        payload=dict(account=self.account,day=self.day,order=binding[0],symbol=order['symbol'],
            native_side=binding[1],execution_id=execution,quantity=qty,
            price=exact_decimal_identity(price),time=time,remaining=remaining)
        serialized=json.dumps(payload,sort_keys=True,separators=(',',':'))
        digest=hashlib.sha256(serialized.encode()).hexdigest()
        return order,binding,execution,qty,remaining,serialized,digest

    def _verify_existing_execution_locked(self,key,row,*,trading_date):
        """Compare receipt, native binding and execution in the same snapshot."""
        _,_,execution,qty,_,serialized,digest=self._execution_material_locked(
            key,row,trading_date=trading_date)
        stored=self.journal.db.execute(
            'SELECT digest,payload FROM native_fill_bindings WHERE key=? AND execution_id=?',
            (key,execution)).fetchone()
        require(stored==(digest,serialized))
        require(self.journal.db.execute(
            'SELECT quantity FROM executions WHERE key=? AND execution_id=?',
            (key,execution)).fetchone()==(qty,))

    def _apply_execution_locked(self,key,row,*,trading_date):
        """Caller holds the journal write transaction, including receipt checks."""
        order,binding,execution,qty,remaining,serialized,digest=self._execution_material_locked(
            key,row,trading_date=trading_date)
        old=self.journal.db.execute('SELECT digest FROM native_fill_bindings WHERE key=? AND execution_id=?',(key,execution)).fetchone()
        if old:
            # Replay remains idempotent even after later fills or restart.
            self._verify_existing_execution_locked(key,row,trading_date=trading_date)
            created=False
        else:
            require(not self.journal.db.execute('SELECT 1 FROM executions WHERE key=? AND execution_id=?',(key,execution)).fetchone())
            require(order['quantity']-order['filled_quantity']-qty==remaining)
            self.journal._record_execution_locked(key,broker_order_id=binding[0],execution_id=execution,quantity=qty)
            self.journal.db.execute('INSERT INTO native_fill_bindings VALUES(?,?,?,?)',(key,execution,digest,serialized))
            created=True
        return self._report('EXECUTION_RECORDED' if created else 'DUPLICATE_EXECUTION',executions_created=created)

    def verify_rest_snapshot(self,key,row,*,trading_date):
        """Compare only; never insert executions or clear a whole-batch barrier."""
        with self._guard():
            require(isinstance(row,dict))
            api=row.get('source_api')
            sources={'kt00007':KT00007_SOURCE_CONTRACT,'ka10076':KA10076_SOURCE_CONTRACT}
            require(api in sources)
            order,binding=self._row(key,row,trading_date,sources[api],'order_aggregate_snapshot')
            validate_stored_execution_totals(self.journal.db,
                dict(self.journal.db.execute('SELECT key,filled FROM intents')))
            require(row.get('broker_execution_id')=='' and row.get('broker_execution_id_available_in_source') is False)
            require(number(row.get('fill_qty'),integer=True)==order['filled_quantity'])
            require(number(row.get('remaining_qty'),integer=True)==order['remaining_quantity'])
        return self._report('REST_IDENTITY_AND_QUANTITY_MATCH',executions_created=False,
            whole_account_snapshot_admitted=False,order_state_reconciled=False)
