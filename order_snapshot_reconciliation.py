"""Atomic whole-journal snapshot diagnostics, never broker or LIVE admission.

Caller-supplied revisions enforce local ordering only. They cannot prove a
snapshot's broker origin, account scope, completeness or freshness. A future
independently admitted adapter must establish those before actual operation.
No network, execution insertion, auto-enable, cancellation or submission.
"""
import json

from order_intent_journal import OrderJournalError


FIELDS = {'key', 'broker_order_id', 'symbol', 'side', 'quantity', 'filled_quantity', 'status'}
STATUS = {'OPEN', 'CANCELLED', 'FILLED', 'REJECTED'}


def reconcile_order_snapshot_batch(journal, *, revision, orders):
    """Compare every claimed intent under one SQLite write transaction.

    A mismatch blocks all subsequent local claims, including after restart or
    individual order reconciliation. Only a newer fully matched batch clears
    this barrier, and it always leaves MASTER_OFF and preserves the Kill latch.
    """
    errors = set()
    material = orders if isinstance(orders, (list, tuple)) else []
    if not isinstance(orders, (list, tuple)):
        errors.add('INVALID_SNAPSHOT_COLLECTION')
    valid_revision = type(revision) is int and 0 < revision <= 2**63-1
    if not valid_revision:
        errors.add('INVALID_SNAPSHOT_REVISION')
    with journal._atomic():
        last = journal.db.execute('SELECT revision FROM reconciliation_barrier WHERE id=1').fetchone()
        if last is None:
            raise OrderJournalError('missing batch reconciliation safety state')
        if valid_revision and revision <= last[0]:
            errors.add('STALE_OR_REPLAYED_SNAPSHOT')
        known = {row[0]: journal.get(row[0]) for row in journal.db.execute(
            "SELECT key FROM intents WHERE state!='INTENT_CREATED' ORDER BY key")}
        seen, broker_ids, matched, snapshots = set(), set(), [], []
        for order in material:
            if not isinstance(order, dict) or set(order) != FIELDS:
                errors.add('INVALID_SNAPSHOT_ROW')
                continue
            if any(not isinstance(order[f], str) or not order[f].strip()
                   for f in ('key', 'broker_order_id', 'symbol', 'side', 'status')):
                errors.add('INVALID_SNAPSHOT_IDENTITY')
                continue
            if (type(order['quantity']) is not int or order['quantity'] <= 0
                or type(order['filled_quantity']) is not int or order['filled_quantity'] < 0
                or order['status'] not in STATUS):
                errors.add('INVALID_SNAPSHOT_QUANTITY_OR_STATUS')
                continue
            key, broker_id = order['key'], order['broker_order_id']
            if key in seen or broker_id in broker_ids:
                errors.add('DUPLICATE_ORDER_BINDING')
            seen.add(key)
            broker_ids.add(broker_id)
            row = known.get(key)
            if row is None:
                errors.add('UNKNOWN_OR_UNCLAIMED_ORDER')
                continue
            if any(row[field] != order[field] for field in
                   ('broker_order_id', 'symbol', 'side', 'quantity', 'filled_quantity')):
                errors.add('ORDER_BINDING_OR_QUANTITY_MISMATCH')
                continue
            status, filled = order['status'], order['filled_quantity']
            if ((status == 'FILLED') != (filled == row['quantity'])
                or (status == 'REJECTED' and filled != 0)
                or (row['terminal_status'] is not None and row['terminal_status'] != status)):
                errors.add('TERMINAL_STATUS_CONFLICT')
                continue
            state = ('PARTIALLY_FILLED' if filled else 'ACKNOWLEDGED') if status == 'OPEN' else status
            matched.append((state, status if status != 'OPEN' else row['terminal_status'], key))
            snapshots.append((key, json.dumps(order, sort_keys=True)))
        if seen != set(known):
            errors.add('ORDER_SCOPE_MISMATCH')
        if errors:
            # Keep original fills and terminal facts, quarantine even matched rows.
            journal.db.execute("UPDATE intents SET state='RECONCILIATION_REQUIRED' WHERE state!='INTENT_CREATED'")
        else:
            journal.db.executemany('UPDATE intents SET state=?,terminal_status=? WHERE key=?', matched)
        journal.db.execute('UPDATE reconciliation_barrier SET revision=?,blocked=? WHERE id=1',
            (max(last[0], revision) if valid_revision else last[0], int(bool(errors))))
        journal._stop_shadow('BATCH_SNAPSHOT_CONFLICT' if errors else 'BATCH_RECONCILED_OFF')
        # A later event/startup/enable invalidates this snapshot's epoch binding.
        # Failed batches cannot leave previously accepted settlement bindings.
        journal.db.execute('DELETE FROM reconciled_snapshot_bindings')
        if not errors:
            epoch = journal.shadow_control()['epoch']
            journal.db.executemany('INSERT INTO reconciled_snapshot_bindings VALUES(?,?,?,?)',
                [(key, revision, epoch, payload) for key, payload in snapshots])
    return dict(mode='OFFLINE_ORDER_SNAPSHOT_RECONCILIATION', matched=not errors,
        errors=sorted(errors), observed_order_count=len(material), expected_order_count=len(known),
        network_request_attempted=False, broker_request_sent=False,
        executions_created=False, real_broker_origin_verified=False,
        account_scope_attested=False, snapshot_freshness_attested=False,
        genuine_live_evidence=False, live_ordering_authorized=False,
        shadow_control=journal.shadow_control())
