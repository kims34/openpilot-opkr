import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from research_v1_krx_readonly_integrity_audit import audit_private_acquisitions, canonical_hash


class IntegrityAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.raw = b'private opaque response, never emitted'
        self.digest = hashlib.sha256(self.raw).hexdigest()
        self.object_path = self.root/'objects'/'sha256'/self.digest[:2]/(self.digest+'.bin')
        self.object_path.parent.mkdir(parents=True)
        self.object_path.write_bytes(self.raw)
        os.chmod(self.object_path, 0o600)
        self.receipt = {
            'receipt_version': '2026-10-01.v2', 'source_family': 'KRX_SECURITY_STATUS',
            'intended_use_scope': 'INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION',
            'access_route': 'DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION',
            'dataset_identifier': 'synthetic_private_dataset',
            'authorization_evidence_reference': 'synthetic_only',
            'authorization_evidence_fingerprint_sha256': 'a'*64,
            'client_revision': 'synthetic_only', 'retrieved_at': '2026-10-01T01:00:00+00:00',
            'request_metadata_sha256': 'b'*64, 'response_schema_sha256': 'c'*64,
            'response_payload_sha256': 'd'*64, 'response_rows': 1,
            'response_columns': ['PRIVATE_COLUMN'], 'public_contract_evidence_version': '2026-10-02.v2',
            'public_contract_evidence_fingerprint_sha256': 'e'*64,
            'alpha_or_final_judge_promotion_authorized': False,
            'sealed_holdout_authorized': False, 'live_trading_authorized': False,
        }
        self.receipt['receipt_fingerprint_sha256'] = canonical_hash(self.receipt)
        self.manifest = dict(manifest_version='2026-10-02.v1', source_family=self.receipt['source_family'],
            dataset_identifier=self.receipt['dataset_identifier'], request_metadata_sha256='b'*64,
            raw_object_sha256=self.digest, raw_bytes_size=len(self.raw),
            response_schema_sha256='c'*64, response_payload_sha256='d'*64,
            receipt_fingerprint_sha256=self.receipt['receipt_fingerprint_sha256'],
            sealed_holdout_authorized=False, live_trading_authorized=False)
        self.cp = dict(checkpoint_version='2026-10-02.v1', state='COMPLETE',
            source_family=self.receipt['source_family'], dataset_identifier=self.receipt['dataset_identifier'],
            request_metadata_sha256='b'*64, raw_object_sha256=self.digest, raw_bytes_size=len(self.raw),
            receipt_relpath='receipts/r.json', manifest_relpath='manifests/m.json',
            receipt_fingerprint_sha256=self.receipt['receipt_fingerprint_sha256'],
            feature_performance_testing_authorized=False, sealed_holdout_authorized=False, live_trading_authorized=False)
        self.rebind_outer_hashes()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, relative, value):
        path = self.root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        data = (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2)+'\n').encode()
        path.write_bytes(data)
        os.chmod(path, 0o600)
        return hashlib.sha256(data).hexdigest()

    def rebind_outer_hashes(self):
        self.manifest['receipt_metadata_sha256'] = self.write('receipts/r.json', self.receipt)
        self.cp['manifest_metadata_sha256'] = self.write('manifests/m.json', self.manifest)
        self.write('checkpoints/c.json', self.cp)

    def audit(self):
        return audit_private_acquisitions(self.root)

    def test_valid_observed_storage_passes_without_granting_source_or_performance_authority(self):
        before = {str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.audit()
        self.assertTrue(result['storage_integrity_pass'])
        self.assertEqual(result['verified_checkpoint_count'], 1)
        self.assertEqual(result['verified_unique_raw_object_count'], 1)
        self.assertEqual(before, {str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        for field in ('historical_coverage_validated', 'pit_availability_validated',
                      'feature_performance_testing_authorized', 'sealed_holdout_authorized',
                      'live_trading_authorized', 'alpha_or_final_judge_promotion_authorized'):
            self.assertIs(result[field], False)
        encoded = json.dumps(result)
        self.assertNotIn('PRIVATE_COLUMN', encoded)
        self.assertNotIn(str(self.root), encoded)
        self.assertNotIn('private opaque', encoded)

    def test_raw_tamper_and_missing_object_fail(self):
        self.object_path.write_bytes(b'altered')
        self.assertIn('RAW_CHECKSUM_MISMATCH', self.audit()['errors'])
        self.object_path.unlink()
        self.assertIn('FILE_MISSING', self.audit()['errors'])

    def test_receipt_inner_fingerprint_checked_even_if_outer_hashes_rebound(self):
        self.receipt['response_rows'] = 2
        self.rebind_outer_hashes()
        self.assertIn('RECEIPT_FINGERPRINT_MISMATCH', self.audit()['errors'])

    def test_manifest_byte_tamper(self):
        self.manifest['raw_bytes_size'] += 1
        self.write('manifests/m.json', self.manifest)
        self.assertIn('MANIFEST_BYTE_HASH_MISMATCH', self.audit()['errors'])

    def test_mixed_bindings_fail_after_valid_outer_rehash(self):
        self.manifest['dataset_identifier'] = 'other_private_dataset'
        self.rebind_outer_hashes()
        self.assertIn('CROSS_ARTIFACT_BINDING_MISMATCH', self.audit()['errors'])

    def test_permission_drift_is_not_silently_repaired(self):
        os.chmod(self.object_path, 0o644)
        self.assertIn('FILE_MODE_DRIFT', self.audit()['errors'])
        self.assertEqual(self.object_path.stat().st_mode & 0o777, 0o644)

    def test_path_escape_cannot_read_external_file(self):
        self.cp['receipt_relpath'] = 'receipts/../../external.json'
        self.rebind_outer_hashes()
        self.assertIn('UNSAFE_PATH', self.audit()['errors'])

    def test_symlink_object_is_blocked(self):
        self.object_path.unlink()
        other = self.root/'outside.bin'
        other.write_bytes(self.raw)
        os.chmod(other, 0o600)
        self.object_path.symlink_to(other)
        self.assertIn('SYMLINK_FORBIDDEN', self.audit()['errors'])

    def test_orphan_receipt_is_not_ignored(self):
        self.write('receipts/orphan.json', self.receipt)
        self.assertIn('UNBOUND_RECEIPTS', self.audit()['errors'])

    def test_duplicate_metadata_binding_fails(self):
        self.write('checkpoints/duplicate.json', self.cp)
        self.assertIn('DUPLICATE_METADATA_BINDING', self.audit()['errors'])

    def test_authority_claims_fail_even_with_recomputed_hashes(self):
        self.cp['live_trading_authorized'] = True
        self.rebind_outer_hashes()
        self.assertIn('ILLEGAL_OR_MISSING_AUTHORITY_FLAG', self.audit()['errors'])

    def test_empty_missing_and_nonprivate_roots_never_pass(self):
        self.assertFalse(audit_private_acquisitions(self.root/'missing')['storage_integrity_pass'])
        empty = self.root/'empty'
        empty.mkdir()
        self.assertIn('NO_CHECKPOINTS_OBSERVED', audit_private_acquisitions(empty)['errors'])
        public = self.root/'public'
        public.mkdir()
        self.assertIn('PUBLIC_ROOT_FORBIDDEN', audit_private_acquisitions(public)['errors'])


if __name__ == '__main__':
    unittest.main()
