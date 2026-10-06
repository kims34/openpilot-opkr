import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from build_shadow_operator_toolkit import ARTIFACTS,build_operator_toolkit
import test_native_settlement_review_cli as native_fixtures


class OperatorToolkitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(__file__).resolve().parent
        self.output = Path(self.tmp.name)/'toolkit.zip'
        self.commit = 'a'*40

    def tearDown(self): self.tmp.cleanup()

    def test_archive_is_allowlisted_and_hashes_exact_source_files(self):
        result = build_operator_toolkit(self.root,self.output,source_commit=self.commit)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(set(archive.namelist()),set(ARTIFACTS)|{'toolkit-manifest.json'})
            for entry in archive.infolist():
                self.assertEqual(entry.create_system, 3)
                self.assertEqual(entry.date_time, (1980,1,1,0,0,0))
            manifest = json.loads(archive.read('toolkit-manifest.json'))
            self.assertEqual(manifest['source_commit'],self.commit)
            self.assertFalse(manifest['real_orders_authorized'])
            for name in ARTIFACTS:
                self.assertEqual(archive.read(name),(self.root/name).read_bytes())
                self.assertEqual(manifest['files'][name],hashlib.sha256(archive.read(name)).hexdigest())
        self.assertEqual(result['archive_sha256'],hashlib.sha256(self.output.read_bytes()).hexdigest())

    def test_archive_can_run_without_repository_and_does_not_create_missing_journal(self):
        build_operator_toolkit(self.root,self.output,source_commit=self.commit)
        target = Path(self.tmp.name)/'extracted'
        with zipfile.ZipFile(self.output) as archive: archive.extractall(target)
        missing = target/'missing.sqlite'
        run = subprocess.run([sys.executable,str(target/'shadow_operational_status.py'),
            '--journal',str(missing)],cwd=target,capture_output=True,text=True)
        self.assertEqual(run.returncode,2)
        self.assertFalse(json.loads(run.stdout)['diagnostics_complete'])
        self.assertFalse(missing.exists())
        # Import every component from the extracted directory, not the repo.
        run = subprocess.run([sys.executable,'-c',
            'import native_settlement_review_cli, shadow_operational_dashboard'],cwd=target,capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)

    def test_same_source_produces_identical_archive(self):
        first = build_operator_toolkit(self.root,self.output,source_commit=self.commit)
        second = build_operator_toolkit(self.root,self.output,source_commit=self.commit)
        self.assertEqual(first['archive_sha256'],second['archive_sha256'])

    def test_extracted_native_review_runs_outside_repo_and_preserves_journal(self):
        fixture = native_fixtures.NativeReviewCLITests()
        fixture.setUp()
        try:
            build_operator_toolkit(self.root,self.output,source_commit=self.commit)
            target = Path(self.tmp.name)/'native-package'
            with zipfile.ZipFile(self.output) as archive: archive.extractall(target)
            env = dict(os.environ)
            env.pop('PYTHONPATH',None)
            before = fixture.journal.shadow_control(),fixture.journal.db.total_changes

            def review():
                run = subprocess.run([sys.executable,str(target/'native_settlement_review_cli.py'),
                    '--journal',str(fixture.path),'--input',str(fixture.input)],
                    cwd=target,env=env,capture_output=True,text=True,encoding='utf-8',timeout=20)
                self.assertEqual(run.stderr,'')
                for private in ('a'*64,'synthetic-review',str(fixture.path),str(fixture.input)):
                    self.assertNotIn(private,run.stdout)
                return run.returncode,json.loads(run.stdout)

            code,result = review()
            self.assertEqual(code,0)
            self.assertTrue(result['assessment_completed'])
            self.assertTrue(result['cashflow_reconciliation']['cash_balance_matched'])
            self.assertFalse(result['cashflow_reconciliation']['settlement_fields_consistent'])
            self.assertFalse(result['ready_for_final_user_authorization'])
            self.assertFalse(result['real_orders_authorized'])

            for text in ('8,9,99','8_999','８９９９'):
                fixture.payload['closing']['body']['entr'] = text
                fixture.write()
                code,result = review()
                self.assertEqual(code,2)
                self.assertFalse(result['assessment_completed'])
                self.assertNotIn('cashflow_reconciliation',result)
                self.assertFalse(result['real_orders_authorized'])
            self.assertEqual(before,(fixture.journal.shadow_control(),fixture.journal.db.total_changes))
        finally:
            fixture.tearDown()

    def test_missing_source_or_invalid_commit_fails_before_artifact(self):
        with self.assertRaises(ValueError):
            build_operator_toolkit(self.root,self.output,source_commit='branch-name')
        with self.assertRaises(ValueError):
            build_operator_toolkit(self.tmp.name,self.output,source_commit=self.commit)
        self.assertFalse(self.output.exists())
