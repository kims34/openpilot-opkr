"""Read-only aggregate journal inspection, not Shadow/LIVE admission.

Never constructs OrderIntentJournal (which performs startup recovery). Reads one
SQLite snapshot with mode=ro, including WAL; does not create a missing database.
Public output excludes raw identities, payloads, error strings and file paths.
"""
import argparse
import json
from pathlib import Path
import sqlite3

from indexalert_automation_control import AutomationCapitalState, AutomationUserControls


def _require(condition):
    if not condition:
        raise ValueError('INVALID_OPERATIONAL_SNAPSHOT')


def _amount(value):
    _require(type(value) is int and value >= 0)
    return value


def inspect_shadow_operational_status(path):
    report = dict(mode='READ_ONLY_SHADOW_OPERATIONAL_STATUS', diagnostics_complete=False,
        local_blockers=[], real_orders_authorized=False, live_ordering_authorized=False,
        genuine_live_provenance_verified=False, exact_policy_shadow_admitted=False,
        broker_request_sent=False, network_request_attempted=False,
        funds_movement_attempted=False, journal_mutation_attempted=False)
    connection = None
    try:
        connection = sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro', uri=True, isolation_level=None)
        connection.execute('PRAGMA query_only=ON')
        connection.execute('BEGIN')
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        _require({'intents','shadow_control','reconciliation_barrier','reconciled_snapshot_bindings'} <= tables)
        control = connection.execute('SELECT epoch,mode,killed FROM shadow_control WHERE id=1').fetchone()
        barrier = connection.execute('SELECT revision,blocked FROM reconciliation_barrier WHERE id=1').fetchone()
        _require(control is not None and barrier is not None)
        epoch, mode, killed = control
        revision, blocked = barrier
        _amount(epoch); _amount(revision)
        _require(mode in ('MASTER_OFF','SHADOW') and killed in (0,1) and blocked in (0,1))
        blockers = set()
        if killed: blockers.add('KILL_SWITCH_LATCHED')
        if blocked or revision == 0: blockers.add('BATCH_RECONCILIATION_REQUIRED')
        states = dict(connection.execute('SELECT state,COUNT(*) FROM intents GROUP BY state'))
        _require(set(states) <= {'INTENT_CREATED','SUBMITTING','ACKNOWLEDGED','PARTIALLY_FILLED',
            'CANCEL_REQUESTED','CANCELLED','REJECTED','FILLED','RECONCILIATION_REQUIRED'})
        unresolved = states.get('SUBMITTING',0)+states.get('RECONCILIATION_REQUIRED',0)
        if unresolved: blockers.add('UNRESOLVED_DURABLE_INTENTS')
        stale = connection.execute('''SELECT COUNT(*) FROM intents i WHERE i.state!='INTENT_CREATED'
            AND NOT EXISTS(SELECT 1 FROM reconciled_snapshot_bindings b
                WHERE b.key=i.key AND b.revision=? AND b.epoch=?)''',(revision,epoch)).fetchone()[0]
        if stale: blockers.add('ORDER_SNAPSHOT_BINDING_STALE')
        pending, conflicts = 0,0
        inbox_tables = {'native_inbox_receipts','native_inbox_attempts','native_inbox_conflicts'}
        if tables & inbox_tables:
            _require(inbox_tables <= tables)
            pending = connection.execute('''SELECT COUNT(*) FROM native_inbox_receipts r
                WHERE NOT EXISTS(SELECT 1 FROM native_inbox_attempts a WHERE
                a.receipt_sequence=r.sequence AND a.outcome IN ('APPLIED','DUPLICATE'))''').fetchone()[0]
            conflicts = connection.execute('SELECT COUNT(*) FROM native_inbox_conflicts').fetchone()[0]
            if pending: blockers.add('NATIVE_INBOX_PENDING')
            if conflicts: blockers.add('NATIVE_INBOX_CONFLICTED')
        capital = None
        capital_tables = {'shadow_capital_config','shadow_capital_reservations'}
        if tables & capital_tables:
            _require(capital_tables <= tables)
            row = connection.execute('SELECT revision,enabled,maximum,baseline FROM shadow_capital_config WHERE id=1').fetchone()
            _require(row is not None)
            capital_revision, enabled, maximum, raw_baseline = row
            _amount(capital_revision); _require(enabled in (0,1)); _amount(maximum)
            values = json.loads(raw_baseline)
            _require(type(values) is list and len(values)==4)
            baseline = AutomationCapitalState(*values).committed_automation_capital_krw()
            AutomationUserControls(bool(enabled),maximum).validate()
            managed = sum(_amount(row[0]) for row in connection.execute('SELECT reserve FROM shadow_capital_reservations'))
            committed = baseline+managed
            capital = dict(revision=capital_revision, automation_enabled=bool(enabled),
                maximum_krw=maximum, baseline_committed_krw=baseline,
                managed_reserve_krw=managed, total_committed_krw=committed,
                ceiling_exceeded=committed>maximum)
            if not enabled: blockers.add('CAPITAL_CONTROL_DISABLED')
            if committed>maximum: blockers.add('CAPITAL_CEILING_EXCEEDED')
        else:
            blockers.add('CAPITAL_NOT_CONFIGURED')
        report.update(diagnostics_complete=True, local_blockers=sorted(blockers),
            journal_epoch=epoch, shadow_mode=mode, kill_latched=bool(killed),
            snapshot_revision=revision, intent_state_counts=states,
            unresolved_intent_count=unresolved, stale_binding_count=stale,
            native_inbox_pending_count=pending, native_inbox_conflict_count=conflicts,
            capital=capital)
    except (sqlite3.Error, ValueError, TypeError, OSError):
        report['local_blockers']=['OPERATIONAL_SNAPSHOT_UNAVAILABLE']
    finally:
        if connection is not None:
            connection.close()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--journal',required=True)
    args = parser.parse_args(argv)
    report = inspect_shadow_operational_status(args.journal)
    print(json.dumps(report,sort_keys=True))
    return 0 if report['diagnostics_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
