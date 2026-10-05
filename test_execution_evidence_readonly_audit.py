import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from execution_evidence_readonly_audit import audit_counts


class ReadOnlyAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'private counts ?.sqlite'

    def tearDown(self):
        self.tmp.cleanup()

    def create(self):
        con = sqlite3.connect(self.path)
        con.execute('CREATE TABLE execution_evidence(source TEXT, decision_date TEXT, filled_qty REAL, symbol TEXT)')
        con.commit()
        return con

    def test_missing_database_is_unknown_and_not_created(self):
        result = audit_counts(self.path)
        self.assertEqual(result['status'], 'DATABASE_MISSING')
        self.assertIsNone(result['observations'])
        self.assertFalse(self.path.exists())

    def test_missing_table_and_schema_are_unknown(self):
        with sqlite3.connect(self.path) as con:
            con.execute('CREATE TABLE other(x TEXT)')
        self.assertEqual(audit_counts(self.path)['status'], 'TABLE_MISSING')
        with sqlite3.connect(self.path) as con:
            con.execute('CREATE TABLE execution_evidence(source TEXT)')
        result = audit_counts(self.path)
        self.assertEqual(result['status'], 'SCHEMA_INCOMPATIBLE')
        self.assertIsNone(result['observations'])

    def test_empty_existing_table_is_verified_zero_without_mutation(self):
        self.create().close()
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = audit_counts(self.path)
        self.assertEqual(result['status'], 'COUNTED')
        self.assertEqual(result['observations'], 0)
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), before)
        self.assertFalse(result['broker_native_identity_columns_present'])

    def test_counts_never_emit_private_values_or_grant_live_admission(self):
        con = self.create()
        con.executemany('INSERT INTO execution_evidence VALUES(?,?,?,?)', [
            ('PROSPECTIVE_LIVE_EXECUTION_LOG', '2026-10-01', 1, 'PRIVATE_SYMBOL'),
            ('PROSPECTIVE_LIVE_EXECUTION_LOG', '2026-10-01', 0, 'PRIVATE_SYMBOL'),
            ('PROSPECTIVE_PAPER_EXECUTION_LOG', '2026-10-02', 1, 'PRIVATE_SYMBOL'),
            ('SECRET_UNKNOWN_SOURCE', 'PRIVATE_DATE', 1, 'PRIVATE_SYMBOL'),
            (None, None, 0, 'PRIVATE_SYMBOL')])
        con.commit()
        con.close()
        result = audit_counts(self.path)
        self.assertEqual(result['observations'], 5)
        self.assertEqual(result['counts']['live_labelled']['rows'], 2)
        self.assertEqual(result['counts']['live_labelled']['distinct_stored_decision_dates'], 1)
        self.assertEqual(result['counts']['live_labelled']['positive_fill_quantity_rows'], 1)
        self.assertEqual(result['counts']['unrecognized_source_rows'], 2)
        encoded = json.dumps(result)
        for private in ('PRIVATE_SYMBOL', 'PRIVATE_DATE', 'SECRET_UNKNOWN_SOURCE', str(self.path)):
            self.assertNotIn(private, encoded)
        for field in ('genuine_live_provenance_verified', 'empirical_sufficiency_assessed', 'live_trading_authorized'):
            self.assertIs(result[field], False)

    def test_reads_committed_wal_without_immutable_stale_snapshot(self):
        con = self.create()
        con.execute('PRAGMA journal_mode=WAL')
        con.execute("INSERT INTO execution_evidence VALUES('PROSPECTIVE_LIVE_EXECUTION_LOG','2026-10-01',1,'PRIVATE')")
        con.commit()
        self.assertEqual(audit_counts(self.path)['observations'], 1)
        con.close()

    def test_corrupt_database_does_not_leak_exception_content(self):
        self.path.write_text('SECRET_CORRUPT_DATA')
        result = audit_counts(self.path)
        self.assertEqual(result['status'], 'READ_ERROR')
        self.assertIsNone(result['observations'])
        self.assertNotIn('SECRET', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
