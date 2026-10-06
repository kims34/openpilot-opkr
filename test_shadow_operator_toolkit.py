import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from build_shadow_operator_toolkit import ARTIFACTS,build_operator_toolkit


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

    def test_missing_source_or_invalid_commit_fails_before_artifact(self):
        with self.assertRaises(ValueError):
            build_operator_toolkit(self.root,self.output,source_commit='branch-name')
        with self.assertRaises(ValueError):
            build_operator_toolkit(self.tmp.name,self.output,source_commit=self.commit)
        self.assertFalse(self.output.exists())
