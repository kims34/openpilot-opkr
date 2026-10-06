import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import io
import json

from verify_indexalert_installed_apk import InstalledApkAuditError, audit_installed_apk, main


class InstalledApkAuditTest(unittest.TestCase):
    def audit(self, *, installed_signer='a', candidate_signer='a', paths=None,
              state='device', package='com.indexalert.app', signed=True, inspect_only=False):
        calls = []
        def run(argv):
            calls.append(argv)
            if argv[:3] == ['adb', '-d', 'get-state']:
                return state
            if argv[:4] == ['adb', '-d', 'shell', 'pm']:
                return paths if paths is not None else 'package:/data/app/synthetic/base.apk\npackage:/data/app/synthetic/split.apk\n'
            if argv[:3] == ['adb', '-d', 'pull']:
                Path(argv[-1]).write_bytes(b'synthetic-installed-public-apk')
                return ''
            if argv[:3] == ['aapt2', 'dump', 'badging']:
                return f"package: name='{package}' versionCode='48' versionName='4.8'\n"
            if argv[:2] == ['apksigner', 'verify']:
                if not signed:
                    raise InstalledApkAuditError('READ_ONLY_TOOL_FAILED')
                signer = installed_signer if argv[-1].endswith('installed-base.apk') else candidate_signer
                return 'Signer #1 certificate SHA-256 digest: ' + signer * 64
            raise AssertionError('Unexpected command: ' + repr(argv))
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / 'candidate.apk'
            candidate.write_bytes(b'synthetic-candidate-public-apk')
            result = audit_installed_apk(None if inspect_only else candidate, run=run)
        return result, calls

    def test_matching_installed_signer_is_only_signing_continuity(self):
        result, calls = self.audit()
        self.assertTrue(result['installed_signing_continuity_verified'])
        for field in ('automatic_install_authorized', 'physical_e2e_verified', 'apk_installed',
                      'app_uninstalled', 'app_data_accessed', 'signing_key_accessed',
                      'broker_request_sent', 'orders_requested', 'live_ordering_authorized',
                      'frozen_criteria_changed'):
            self.assertIs(result[field], False)
        adb_calls = [c for c in calls if c[0] == 'adb']
        self.assertEqual(len(adb_calls), 3)
        self.assertEqual(adb_calls[0], ['adb', '-d', 'get-state'])
        self.assertEqual(adb_calls[1], ['adb', '-d', 'shell', 'pm', 'path', 'com.indexalert.app'])
        self.assertEqual(adb_calls[2][:3], ['adb', '-d', 'pull'])
        self.assertFalse(Path(adb_calls[2][-1]).exists())

    def test_mismatch_does_not_authorize_update_or_uninstall(self):
        result, _ = self.audit(candidate_signer='b')
        self.assertFalse(result['installed_candidate_signers_match'])
        self.assertFalse(result['installed_signing_continuity_verified'])
        self.assertFalse(result['automatic_install_authorized'])
        self.assertFalse(result['app_uninstalled'])

    def test_installed_inspection_requires_no_candidate_or_signing_key(self):
        result, calls = self.audit(inspect_only=True)
        self.assertIsNone(result['candidate'])
        self.assertIsNone(result['installed_candidate_signers_match'])
        self.assertFalse(result['candidate_signer_comparison_performed'])
        self.assertFalse(result['installed_signing_continuity_verified'])
        self.assertFalse(result['signing_key_accessed'])
        self.assertFalse(result['automatic_install_authorized'])
        self.assertFalse(result['physical_e2e_verified'])
        self.assertEqual(len([c for c in calls if c[:3] == ['aapt2','dump','badging']]), 1)
        self.assertEqual(len([c for c in calls if c[:2] == ['apksigner','verify']]), 1)

    def test_cli_without_candidate_reports_observation_without_upgrade_authority(self):
        result, _ = self.audit(inspect_only=True)
        output = io.StringIO()
        with patch('sys.argv', ['verify_indexalert_installed_apk.py']), \
             patch('verify_indexalert_installed_apk.audit_installed_apk', return_value=result) as audit, \
             patch('sys.stdout', output):
            self.assertEqual(main(), 0)
        self.assertIsNone(audit.call_args.args[0])
        report = json.loads(output.getvalue())
        self.assertFalse(report['installed_signing_continuity_verified'])
        self.assertFalse(report['automatic_install_authorized'])
        self.assertFalse(report['apk_installed'])

    def test_ambiguous_or_non_app_base_path_fails_closed(self):
        for paths in ('', 'package:/data/app/a/base.apk\npackage:/data/app/b/base.apk',
                      'package:/data/user/0/com.indexalert.app/base.apk',
                      'package:/data/app/../private/base.apk', 'package:/data/app/a b/base.apk'):
            with self.subTest(paths=paths), self.assertRaises(InstalledApkAuditError):
                self.audit(paths=paths)

    def test_unauthorized_handset_wrong_package_or_unsigned_candidate_fail(self):
        for args in ({'state': 'unauthorized'}, {'package': 'other.app'}, {'signed': False}):
            with self.subTest(args=args), self.assertRaises(InstalledApkAuditError):
                self.audit(**args)


if __name__ == '__main__':
    unittest.main()
