"""Offline structural gate composition; local rows never grant admission.

Use bind_journal_settlement_to_early_live for the journal-backed consistency
boundary. Settlement attestations may be supplied for structural composition,
but neither this module nor caller booleans verify the independent canonical
gate admissions required before final user authorization. Neither path enables
trading or clears a reconciliation barrier.
"""
from dataclasses import dataclass, replace
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json
import re
from kiwoom_account_settlement_evidence import AccountSettlementSnapshot
from order_intent_journal import OrderIntentJournal, OrderJournalError, validate_stored_execution_totals
from order_snapshot_reconciliation import FIELDS, STATUS, load_stored_order_snapshot
from early_live_admission_gate import EarlyLiveAdmissionEvidence, assess_early_live_readiness
class SettlementBindingError(ValueError): pass
@dataclass(frozen=True)
class SettlementAdmission:
    source_account_origin_authenticated: bool=False
    snapshot_freshness_attested: bool=False
    trading_date_origin_attested: bool=False
    settlement_fields_verified: bool=False
    unresolved_reconciliation_count: int=0
def settlement_admitted(e):
    if type(e) is not SettlementAdmission: raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    flags=(e.source_account_origin_authenticated,e.snapshot_freshness_attested,e.trading_date_origin_attested,e.settlement_fields_verified)
    if any(type(v) is not bool for v in flags): raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    if type(e.unresolved_reconciliation_count) is not int or e.unresolved_reconciliation_count<0: raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    return all(flags) and e.unresolved_reconciliation_count==0
def bind_settlement_to_early_live(base,settlement):
    if type(base) is not EarlyLiveAdmissionEvidence: raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    structural=settlement_admitted(settlement)
    fields=dict(base.__dict__)
    fields["account_settlement_tested"]=structural
    out=assess_early_live_readiness(EarlyLiveAdmissionEvidence(**fields))
    # Caller-supplied attestations plus local consistency checks can establish
    # only structural settlement preconditions. They are not an independent
    # canonical admission and must never be reported as one.
    out["account_settlement_structural_preconditions_satisfied"]=structural
    out["independent_settlement_admission_verified"]=False
    out["account_settlement_admitted"]=False
    out["real_orders_authorized"]=False; out["early_live_authorized"]=False
    return out


def bind_journal_settlement_to_early_live(base, settlement, snapshot, journal, *,
                                        expected_epoch, expected_snapshot_revision):
    """Recheck durable local state atomically before structural assessment.

    A result is valid only for its reported epoch/revision. This is diagnostic
    composition, not a reusable activation token, final-user-ready signal, or
    independent broker/gate proof.
    Origin, freshness, date and settlement attestations must still be supplied
    by their independent admissions. No clock TTL is invented here.
    """
    if type(base) is not EarlyLiveAdmissionEvidence or type(journal) is not OrderIntentJournal:
        raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    settlement_admitted(settlement)  # Preserve original exact-type checks.
    if (type(snapshot) is not AccountSettlementSnapshot
        or type(expected_epoch) is not int or expected_epoch < 0
        or type(expected_snapshot_revision) is not int or expected_snapshot_revision <= 0):
        raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    try:
        if (type(snapshot.account_fingerprint) is not str
            or not re.fullmatch(r'(?:sha256:)?[0-9a-f]{64}', snapshot.account_fingerprint)
            or type(snapshot.captured_at) is not str):
            raise ValueError
        captured = datetime.fromisoformat(snapshot.captured_at.replace('Z', '+00:00'))
        if captured.tzinfo is None or captured.utcoffset() is None:
            raise ValueError
        day = captured.astimezone(timezone(timedelta(hours=9))).date().isoformat()
        cash = (snapshot.deposit_cash_krw, snapshot.withdrawable_cash_krw,
                snapshot.d2_estimated_cash_krw, snapshot.orderable_amount_krw)
        if any(type(v) is not Decimal or not v.is_finite() or v < 0 for v in cash):
            raise ValueError
    except (ValueError, TypeError, OverflowError):
        raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED") from None

    errors = set()
    with journal._atomic():
        control = journal.shadow_control()
        barrier = journal.db.execute('SELECT revision,blocked FROM reconciliation_barrier WHERE id=1').fetchone()
        if control['epoch'] != expected_epoch or control['mode'] != 'MASTER_OFF':
            errors.add('JOURNAL_CONTROL_CHANGED')
        if control['killed']:
            errors.add('KILL_SWITCH_LATCHED')
        if barrier != (expected_snapshot_revision, 0):
            errors.add('BATCH_RECONCILIATION_REQUIRED')
        try:
            journal._require_batch_reconciled()
        except OrderJournalError:
            errors.add('INBOX_OR_BATCH_UNRESOLVED')
        try:
            intent_fills = dict(journal.db.execute('SELECT key,filled FROM intents'))
            validate_stored_execution_totals(journal.db, intent_fills)
        except OrderJournalError:
            errors.add('ORDER_SNAPSHOT_CONTENT_CHANGED')
        tables = {r[0] for r in journal.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        scope = (journal.db.execute('SELECT account,day FROM native_journal_scope WHERE id=1').fetchone()
                 if 'native_journal_scope' in tables else None)
        account = 'sha256:' + snapshot.account_fingerprint.removeprefix('sha256:')
        if scope != (account, day):
            errors.add('ACCOUNT_DATE_SCOPE_UNBOUND')
        unresolved = 0
        known = []
        for key, in journal.db.execute("SELECT key FROM intents WHERE state!='INTENT_CREATED'"):
            known.append(key)
            try:
                order = journal.get(key)
            except OrderJournalError:
                errors.add('ORDER_SNAPSHOT_CONTENT_CHANGED')
                continue
            if order['state'] in ('SUBMITTING', 'RECONCILIATION_REQUIRED'):
                unresolved += 1
            bound = journal.db.execute('SELECT revision,epoch,payload FROM reconciled_snapshot_bindings WHERE key=?', (key,)).fetchone()
            if bound is None or bound[:2] != (expected_snapshot_revision, expected_epoch):
                errors.add('ORDER_SNAPSHOT_BINDING_STALE')
                continue
            try:
                source = load_stored_order_snapshot(bound[2])
                if (type(source) is not dict or set(source) != FIELDS
                    or type(source['quantity']) is not int or source['quantity'] <= 0
                    or type(source['filled_quantity']) is not int
                    or not 0 <= source['filled_quantity'] <= source['quantity']
                    or type(source['status']) is not str or source['status'] not in STATUS):
                    raise ValueError
                if any(source[f] != order[f] for f in ('key','broker_order_id','symbol','side','quantity','filled_quantity')):
                    raise ValueError
                state = ('PARTIALLY_FILLED' if order['filled_quantity'] else 'ACKNOWLEDGED') if source['status'] == 'OPEN' else source['status']
                if state != order['state']:
                    raise ValueError
            except (ValueError, TypeError, KeyError):
                errors.add('ORDER_SNAPSHOT_CONTENT_CHANGED')
        if {r[0] for r in journal.db.execute('SELECT key FROM reconciled_snapshot_bindings')} != set(known):
            errors.add('ORDER_SNAPSHOT_SCOPE_CHANGED')
        if unresolved:
            errors.add('UNRESOLVED_DURABLE_INTENTS')
        effective = replace(settlement,
            settlement_fields_verified=settlement.settlement_fields_verified and not errors,
            unresolved_reconciliation_count=max(settlement.unresolved_reconciliation_count, unresolved))
        effective_base = replace(base,
            unresolved_reconciliation_count=max(base.unresolved_reconciliation_count, unresolved))
        out = bind_settlement_to_early_live(effective_base, effective)
        out.update(mode='OFFLINE_JOURNAL_SETTLEMENT_BINDING', journal_epoch=control['epoch'],
            snapshot_revision=barrier[0] if barrier else None,
            local_reconciliation_errors=sorted(errors),
            durable_unresolved_reconciliation_count=unresolved,
            broker_request_sent=False, network_request_attempted=False,
            genuine_live_provenance_verified=False)
    return out
