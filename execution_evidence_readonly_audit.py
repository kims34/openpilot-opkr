"""Private operator-only count audit; no credentials, raw rows or admission.

Does not import the runtime/ledger (their imports can initialise/write tables).
Missing/incompatible data is UNKNOWN, never silently zero observations.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path


SOURCES = (
    ('paper_labelled', 'PROSPECTIVE_PAPER_EXECUTION_LOG'),
    ('live_labelled', 'PROSPECTIVE_LIVE_EXECUTION_LOG'),
    ('legacy_shadow_fill', 'PROSPECTIVE_SHADOW_EXECUTION_LOG'),
    ('misfiled_shadow_decision', 'PROSPECTIVE_SHADOW_DECISION_LOG'),
)


def audit_counts(path):
    report = dict(mode='READ_ONLY_EXECUTION_LEDGER_COUNTS', status='UNKNOWN',
                  observations=None, counts=None, broker_native_identity_columns_present=None,
                  genuine_live_provenance_verified=False, empirical_sufficiency_assessed=False,
                  live_trading_authorized=False, sealed_holdout_read=False,
                  database_mutation_attempted=False, network_request_attempted=False)
    target = Path(path).resolve()
    if not target.is_file():
        report['status'] = 'DATABASE_MISSING'
        return report
    con = None
    try:
        con = sqlite3.connect(target.as_uri() + '?mode=ro', uri=True, timeout=5)
        con.execute('PRAGMA query_only=ON')
        con.execute('BEGIN')
        if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='execution_evidence'").fetchone():
            report['status'] = 'TABLE_MISSING'
            return report
        columns = {row[1] for row in con.execute('PRAGMA table_info(execution_evidence)')}
        if not {'source', 'decision_date', 'filled_qty'}.issubset(columns):
            report['status'] = 'SCHEMA_INCOMPATIBLE'
            return report
        report['broker_native_identity_columns_present'] = {'broker_order_id', 'broker_execution_id'}.issubset(columns)
        total = con.execute('SELECT COUNT(*) FROM execution_evidence').fetchone()[0]
        counts = {}
        known = 0
        for label, source in SOURCES:
            row = con.execute("""SELECT COUNT(*), COUNT(DISTINCT decision_date),
                SUM(CASE WHEN typeof(filled_qty) IN ('integer','real') AND filled_qty>0 THEN 1 ELSE 0 END)
                FROM execution_evidence WHERE source=?""", (source,)).fetchone()
            counts[label] = dict(rows=int(row[0]), distinct_stored_decision_dates=int(row[1]),
                                 positive_fill_quantity_rows=int(row[2] or 0))
            known += row[0]
        counts['unrecognized_source_rows'] = int(total - known)
        report.update(status='COUNTED', observations=int(total), counts=counts)
        return report
    except (sqlite3.Error, OSError, ValueError):
        # Exception messages may contain paths, identifiers or database content.
        report['status'] = 'READ_ERROR'
        return report
    finally:
        if con is not None:
            con.close()


if __name__ == '__main__':
    print(json.dumps(audit_counts(os.getenv('INDEXALERT_DB', '/tmp/indexalert.db')), sort_keys=True))
