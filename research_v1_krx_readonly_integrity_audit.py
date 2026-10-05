"""Read-only stored-acquisition validation. No raw rows, network or admission.

Uses the frozen private-store and receipt byte/fingerprint formats, but avoids
their write-capable root initialisation. Checks observed storage only, never
claims complete historical scope, PIT availability or performance eligibility.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re


RECEIPT_FIELDS = (
    'receipt_version', 'source_family', 'intended_use_scope', 'access_route',
    'dataset_identifier', 'authorization_evidence_reference',
    'authorization_evidence_fingerprint_sha256', 'client_revision', 'retrieved_at',
    'request_metadata_sha256', 'response_schema_sha256', 'response_payload_sha256',
    'response_rows', 'response_columns', 'public_contract_evidence_version',
    'public_contract_evidence_fingerprint_sha256',
    'alpha_or_final_judge_promotion_authorized', 'sealed_holdout_authorized',
    'live_trading_authorized',
)
SHA = re.compile(r'^[0-9a-f]{64}$')


class AuditError(ValueError):
    pass


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), default=str).encode()).hexdigest()


def _require(ok, code):
    if not ok:
        raise AuditError(code)


def _digest(value):
    _require(isinstance(value, str) and SHA.fullmatch(value), 'INVALID_DIGEST')
    return value


def _safe_file(root, relative):
    _require(isinstance(relative, str), 'UNSAFE_PATH')
    rel = Path(relative)
    _require(not rel.is_absolute() and '..' not in rel.parts, 'UNSAFE_PATH')
    current = root
    for part in rel.parts:
        current = current / part
        _require(not current.is_symlink(), 'SYMLINK_FORBIDDEN')
    _require(current.is_file(), 'FILE_MISSING')
    _require(current.stat().st_mode & 0o777 == 0o600, 'FILE_MODE_DRIFT')
    return current


def _read_json(root, relative):
    path = _safe_file(root, relative)
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError):
        raise AuditError('INVALID_JSON') from None
    _require(isinstance(value, dict), 'INVALID_METADATA_OBJECT')
    return value, hashlib.sha256(raw).hexdigest()


def _raw(root, digest, cache):
    digest = _digest(digest)
    if digest in cache:
        return cache[digest]
    path = _safe_file(root, f'objects/sha256/{digest[:2]}/{digest}.bin')
    before = path.stat()
    sha, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            sha.update(chunk)
            size += len(chunk)
    after = path.stat()
    _require((before.st_ino, before.st_size, before.st_mtime_ns) ==
             (after.st_ino, after.st_size, after.st_mtime_ns), 'OBJECT_CHANGED_DURING_AUDIT')
    _require(sha.hexdigest() == digest, 'RAW_CHECKSUM_MISMATCH')
    cache[digest] = size
    return size


def _false_authority(value, fields):
    for field in fields:
        _require(value.get(field) is False, 'ILLEGAL_OR_MISSING_AUTHORITY_FLAG')


def _checkpoint(root, path, cache):
    checkpoint, cp_sha = _read_json(root, str(path.relative_to(root)))
    _require(checkpoint.get('checkpoint_version') == '2026-10-02.v1', 'CHECKPOINT_VERSION')
    _require(checkpoint.get('state') == 'COMPLETE', 'CHECKPOINT_NOT_COMPLETE')
    _false_authority(checkpoint, ('feature_performance_testing_authorized', 'sealed_holdout_authorized', 'live_trading_authorized'))
    receipt_rel = checkpoint.get('receipt_relpath')
    manifest_rel = checkpoint.get('manifest_relpath')
    _require(isinstance(receipt_rel, str) and receipt_rel.startswith('receipts/'), 'RECEIPT_PATH_SCOPE')
    _require(isinstance(manifest_rel, str) and manifest_rel.startswith('manifests/'), 'MANIFEST_PATH_SCOPE')
    receipt, receipt_sha = _read_json(root, receipt_rel)
    manifest, manifest_sha = _read_json(root, manifest_rel)
    _require(manifest_sha == _digest(checkpoint.get('manifest_metadata_sha256')), 'MANIFEST_BYTE_HASH_MISMATCH')
    _require(manifest.get('manifest_version') == '2026-10-02.v1', 'MANIFEST_VERSION')
    _require(receipt_sha == _digest(manifest.get('receipt_metadata_sha256')), 'RECEIPT_BYTE_HASH_MISMATCH')
    _require(all(field in receipt for field in RECEIPT_FIELDS), 'RECEIPT_FIELDS_MISSING')
    _require(receipt.get('receipt_version') == '2026-10-01.v2', 'RECEIPT_VERSION')
    _false_authority(receipt, ('alpha_or_final_judge_promotion_authorized', 'sealed_holdout_authorized', 'live_trading_authorized'))
    _false_authority(manifest, ('sealed_holdout_authorized', 'live_trading_authorized'))
    fingerprint = _digest(receipt.get('receipt_fingerprint_sha256'))
    _require(canonical_hash({field: receipt[field] for field in RECEIPT_FIELDS}) == fingerprint, 'RECEIPT_FINGERPRINT_MISMATCH')
    _digest(receipt.get('authorization_evidence_fingerprint_sha256'))
    _digest(receipt.get('request_metadata_sha256'))
    _digest(receipt.get('public_contract_evidence_fingerprint_sha256'))
    for field in ('source_family', 'dataset_identifier', 'request_metadata_sha256', 'receipt_fingerprint_sha256'):
        _require(checkpoint.get(field) == manifest.get(field) == receipt.get(field), 'CROSS_ARTIFACT_BINDING_MISMATCH')
    for field in ('response_schema_sha256', 'response_payload_sha256'):
        _require(manifest.get(field) == receipt.get(field), 'RESPONSE_BINDING_MISMATCH')
        _digest(receipt.get(field))
    _require(checkpoint.get('raw_object_sha256') == manifest.get('raw_object_sha256'), 'RAW_BINDING_MISMATCH')
    size = checkpoint.get('raw_bytes_size')
    _require(type(size) is int and size >= 0 and size == manifest.get('raw_bytes_size'), 'INVALID_RAW_SIZE')
    digest = _digest(checkpoint.get('raw_object_sha256'))
    _require(_raw(root, digest, cache) == size, 'RAW_SIZE_MISMATCH')
    _require(type(receipt.get('response_rows')) is int and receipt['response_rows'] >= 0, 'INVALID_RESPONSE_ROWS')
    return dict(checkpoint_sha256=cp_sha, manifest_sha256=manifest_sha,
                receipt_sha256=receipt_sha, raw_object_sha256=digest), receipt_rel, manifest_rel


def audit_private_acquisitions(root):
    report = dict(mode='READ_ONLY_KRX_STORED_INTEGRITY_VALIDATION',
        storage_integrity_pass=False, observed_checkpoint_count=0, verified_checkpoint_count=0,
        verified_unique_raw_object_count=0, errors={}, snapshot_fingerprint_sha256=None,
        database_or_file_mutation_attempted=False, raw_rows_emitted=False,
        security_identifiers_emitted=False, network_request_attempted=False,
        historical_coverage_validated=False, pit_availability_validated=False,
        feature_performance_testing_authorized=False, sealed_holdout_authorized=False,
        live_trading_authorized=False, alpha_or_final_judge_promotion_authorized=False)
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        report['errors'] = {'INVALID_OR_MISSING_PRIVATE_ROOT': 1}
        return report
    root = root.resolve()
    if set(part.lower() for part in root.parts) & {'public', 'static', 'www', 'htdocs'}:
        report['errors'] = {'PUBLIC_ROOT_FORBIDDEN': 1}
        return report
    errors, cache, bindings, receipts, manifests = Counter(), {}, [], set(), set()
    try:
        checkpoints = sorted((root / 'checkpoints').rglob('*.json'))
        report['observed_checkpoint_count'] = len(checkpoints)
        if not checkpoints:
            errors['NO_CHECKPOINTS_OBSERVED'] += 1
        for path in checkpoints:
            try:
                binding, receipt, manifest = _checkpoint(root, path, cache)
                _require(receipt not in receipts and manifest not in manifests, 'DUPLICATE_METADATA_BINDING')
                receipts.add(receipt)
                manifests.add(manifest)
                bindings.append(binding)
            except AuditError as exc:
                errors[str(exc)] += 1
            except (OSError, TypeError, ValueError):
                errors['UNREADABLE_OR_MALFORMED_ARTIFACT'] += 1
        # Detect incomplete/orphan acquisitions rather than silently ignore them.
        for category, referenced in (('receipts', receipts), ('manifests', manifests)):
            observed = {str(p.relative_to(root)) for p in (root/category).rglob('*.json')}
            if observed != referenced:
                errors['UNBOUND_'+category.upper()] += len(observed.symmetric_difference(referenced))
        raw_files = sorted((root / 'objects').rglob('*.bin'))
        for path in raw_files:
            try:
                digest = _digest(path.stem)
                expected = root/'objects'/'sha256'/digest[:2]/(digest+'.bin')
                _require(path == expected, 'NONCANONICAL_OBJECT_PATH')
                _raw(root, digest, cache)
            except AuditError as exc:
                errors[str(exc)] += 1
            except OSError:
                errors['UNREADABLE_RAW_OBJECT'] += 1
        referenced_raw = {binding['raw_object_sha256'] for binding in bindings}
        if set(cache) != referenced_raw:
            errors['UNBOUND_RAW_OBJECTS'] += len(set(cache).symmetric_difference(referenced_raw))
    except OSError:
        errors['PRIVATE_INVENTORY_UNREADABLE'] += 1
    report.update(verified_checkpoint_count=len(bindings), verified_unique_raw_object_count=len(cache),
        errors=dict(sorted(errors.items())), storage_integrity_pass=bool(bindings) and not errors,
        snapshot_fingerprint_sha256=canonical_hash(sorted(bindings, key=lambda x:x['checkpoint_sha256'])) if bindings else None)
    return report


if __name__ == '__main__':
    print(json.dumps(audit_private_acquisitions(os.environ.get('KRX_PRIVATE_RAW_DIR') or '/data'), sort_keys=True), flush=True)
