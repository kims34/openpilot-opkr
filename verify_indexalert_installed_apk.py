"""Read one physically connected handset's IndexAlert base APK; never install.

Only the installed public APK is copied temporarily. No app data, credentials,
account state, broker connection or private signing key is accessed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


PACKAGE = 'com.indexalert.app'


class InstalledApkAuditError(ValueError):
    pass


def run_tool(argv):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    if result.returncode:
        # adb output can contain private device IDs and host paths.
        raise InstalledApkAuditError('READ_ONLY_TOOL_FAILED')
    return result.stdout


def apk_identity(apk, *, aapt2, apksigner, run=run_tool):
    badging = run([aapt2, 'dump', 'badging', str(apk)])
    package = next((line for line in badging.splitlines() if line.startswith('package:')), '')
    fields = dict(re.findall(r"(name|versionCode|versionName)='([^']*)'", package))
    if fields.get('name') != PACKAGE or not fields.get('versionCode', '').isdigit() or not fields.get('versionName'):
        raise InstalledApkAuditError('INDEXALERT_APK_IDENTITY_REQUIRED')
    certificates = run([apksigner, 'verify', '--verbose', '--print-certs', str(apk)])
    signers = sorted(set(re.findall(r'certificate SHA-256 digest: ([0-9a-fA-F]{64})', certificates)))
    if not signers:
        raise InstalledApkAuditError('VERIFIED_APK_SIGNER_REQUIRED')
    return dict(application_id=PACKAGE, version_code=int(fields['versionCode']),
                version_name=fields['versionName'], signer_sha256=[s.lower() for s in signers],
                signature_verified=True, apk_sha256=hashlib.sha256(Path(apk).read_bytes()).hexdigest())


def audit_installed_apk(candidate, *, adb='adb', aapt2='aapt2', apksigner='apksigner', run=run_tool):
    # -d selects a USB physical handset, never an emulator or arbitrary serial.
    if run([adb, '-d', 'get-state']).strip() != 'device':
        raise InstalledApkAuditError('ONE_AUTHORIZED_PHYSICAL_HANDSET_REQUIRED')
    paths = run([adb, '-d', 'shell', 'pm', 'path', PACKAGE]).splitlines()
    base = [line[len('package:'):] for line in paths
            if line.startswith('package:') and line.endswith('/base.apk')]
    if (len(base) != 1 or not base[0].startswith('/data/app/')
            or '..' in base[0].split('/') or any(c.isspace() for c in base[0])):
        raise InstalledApkAuditError('ONE_INSTALLED_INDEXALERT_BASE_APK_REQUIRED')
    with tempfile.TemporaryDirectory(prefix='indexalert-apk-readonly-') as directory:
        installed_apk = Path(directory) / 'installed-base.apk'
        run([adb, '-d', 'pull', base[0], str(installed_apk)])
        installed = apk_identity(installed_apk, aapt2=aapt2, apksigner=apksigner, run=run)
    proposed = apk_identity(Path(candidate), aapt2=aapt2, apksigner=apksigner, run=run)
    matches = installed['signer_sha256'] == proposed['signer_sha256']
    return dict(schema_version='INDEXALERT_INSTALLED_APK_READONLY_v1',
                installed=installed, candidate=proposed,
                installed_candidate_signers_match=matches,
                installed_signing_continuity_verified=matches,
                automatic_install_authorized=False, physical_e2e_verified=False,
                apk_installed=False, app_uninstalled=False, app_data_accessed=False,
                signing_key_accessed=False, broker_request_sent=False,
                orders_requested=False, live_ordering_authorized=False,
                frozen_criteria_changed=False)


def main():
    parser = argparse.ArgumentParser(description='Inspect installed IndexAlert APK signing without installing or uninstalling.')
    parser.add_argument('candidate', help='Already signed candidate APK to compare with the installed app')
    parser.add_argument('--adb', default='adb')
    parser.add_argument('--aapt2', default='aapt2')
    parser.add_argument('--apksigner', default='apksigner')
    args = parser.parse_args()
    try:
        result = audit_installed_apk(args.candidate, adb=args.adb, aapt2=args.aapt2, apksigner=args.apksigner)
    except (InstalledApkAuditError, OSError, subprocess.TimeoutExpired):
        print(json.dumps({'schema_version': 'INDEXALERT_INSTALLED_APK_READONLY_v1',
                          'status': 'UNVERIFIED', 'installed_signing_continuity_verified': False,
                          'physical_e2e_verified': False, 'apk_installed': False,
                          'app_uninstalled': False, 'orders_requested': False,
                          'live_ordering_authorized': False}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result['installed_signing_continuity_verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
