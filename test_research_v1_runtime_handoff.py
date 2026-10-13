"""Synthetic offline-only immutable fan-out handoff tests."""
import copy
import hashlib
import os
from unittest.mock import patch

import research_v1_runtime_handoff as handoff
from pathlib import Path
import tempfile
import unittest

from research_v1_runtime_handoff import UnsafeHandoff, handoff_matches, make_handoff


class ReadOnlyHandoffTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        (self.root / "sub").mkdir()
        (self.root / "sub" / "fixed_records.bin").write_bytes(b"synthetic-fixed-selection")
        (self.root / "cost_report.json").write_bytes(b'{"fixture": true}')
        self.names = ["cost_report.json", "sub/fixed_records.bin"]
        self.key = "a" * 64

    def create(self, **overrides):
        params = {"root": self.root, "filenames": self.names,
                  "upstream_cache_key_sha256": self.key}
        params.update(overrides)
        return make_handoff(**params)

    def test_exact_bytes_and_filename_order_are_stable(self):
        receipt = self.create()
        self.assertTrue(handoff_matches(receipt, root=self.root, filenames=list(reversed(self.names)),
                                        upstream_cache_key_sha256=self.key))
        for permission in ("pit_admission_granted", "profitability_evaluation_authorized",
                           "holdout_access_authorized", "live_orders_authorized"):
            self.assertIs(receipt[permission], False)

    def test_tampering_or_missing_file_fails_closed(self):
        receipt = self.create()
        file = self.root / "sub" / "fixed_records.bin"
        file.write_bytes(b"tampered")
        self.assertFalse(handoff_matches(receipt, root=self.root, filenames=self.names,
                                         upstream_cache_key_sha256=self.key))
        file.unlink()
        self.assertFalse(handoff_matches(receipt, root=self.root, filenames=self.names,
                                         upstream_cache_key_sha256=self.key))

    def test_extra_missing_or_changed_source_key_rejected(self):
        receipt = self.create()
        for filenames in (["cost_report.json"], self.names + ["missing.json"]):
            self.assertFalse(handoff_matches(receipt, root=self.root, filenames=filenames,
                                             upstream_cache_key_sha256=self.key))
        self.assertFalse(handoff_matches(receipt, root=self.root, filenames=self.names,
                                         upstream_cache_key_sha256="b" * 64))
        forged = copy.deepcopy(receipt)
        forged["live_orders_authorized"] = True
        self.assertFalse(handoff_matches(forged, root=self.root, filenames=self.names,
                                         upstream_cache_key_sha256=self.key))

    def test_traversal_absolute_duplicate_and_bad_key_rejected(self):
        for name in ("../outside", "/absolute", "./cost_report.json",
                     "sub/../cost_report.json", "sub\\fixed_records.bin"):
            with self.subTest(name=name), self.assertRaises(UnsafeHandoff):
                self.create(filenames=[name])
        with self.assertRaises(UnsafeHandoff):
            self.create(filenames=["cost_report.json", "cost_report.json"])
        for bad in ("X" * 64, "not-a-digest", ""):
            with self.subTest(bad=bad), self.assertRaises(UnsafeHandoff):
                self.create(upstream_cache_key_sha256=bad)

    def test_symlinked_file_and_directory_rejected(self):
        (self.root / "alias").symlink_to(self.root / "sub", target_is_directory=True)
        with self.assertRaises(UnsafeHandoff):
            self.create(filenames=["alias/fixed_records.bin"])
        (self.root / "shortcut").symlink_to(self.root / "cost_report.json")
        with self.assertRaises(UnsafeHandoff):
            self.create(filenames=["shortcut"])


    def test_symlink_swapped_at_exact_open_is_rejected(self):
        # Reject TOCTOU replacement at the kernel open boundary.
        filename = self.root / "cost_report.json"
        original_open = os.open
        swapped = [False]

        def swap_then_open(path, flags, *args, **kwargs):
            if path == "cost_report.json" and not swapped[0]:
                swapped[0] = True
                filename.unlink()
                filename.symlink_to(self.root / "sub" / "fixed_records.bin")
            return original_open(path, flags, *args, **kwargs)

        with patch.object(handoff.os, "open", side_effect=swap_then_open):
            with self.assertRaises(UnsafeHandoff):
                self.create()
        self.assertTrue(swapped[0])

    def test_intermediate_directory_swap_at_open_is_rejected(self):
        original_open = os.open
        moved = [False]
        directory = self.root / "sub"

        def swap_dir(path, flags, *args, **kwargs):
            if path == "sub" and not moved[0]:
                moved[0] = True
                directory.rename(self.root / "real_sub")
                directory.symlink_to(self.root / "real_sub", target_is_directory=True)
            return original_open(path, flags, *args, **kwargs)

        with patch.object(handoff.os, "open", side_effect=swap_dir):
            with self.assertRaises(UnsafeHandoff):
                self.create()
        self.assertTrue(moved[0])

    def test_mutated_open_file_detected_by_descriptor_identity(self):
        original_digest = hashlib.sha256
        target = self.root / "cost_report.json"
        changed = [False]

        class EditingHash:
            def __init__(self):
                self.inner = original_digest()

            def update(self, data):
                self.inner.update(data)
                if not changed[0]:
                    changed[0] = True
                    target.write_bytes(b'{"changed": true, "extra": 1}')

            def hexdigest(self):
                return self.inner.hexdigest()

        with patch.object(handoff.hashlib, "sha256", side_effect=EditingHash):
            with self.assertRaises(UnsafeHandoff):
                self.create()
        self.assertTrue(changed[0])

    def test_nonregular_fifo_rejected_without_waiting(self):
        pipe = self.root / "pipe"
        os.mkfifo(pipe)
        with self.assertRaises(UnsafeHandoff):
            self.create(filenames=["pipe"])

    def test_wrong_type_in_filename_list_fails_closed(self):
        with self.assertRaises(UnsafeHandoff):
            self.create(filenames=["cost_report.json", 5])
        with self.assertRaises(UnsafeHandoff):
            self.create(filenames=[None])

    def test_signature_or_source_admission_cannot_be_inferred(self):
        receipt = self.create()
        self.assertNotIn("signature", receipt)
        self.assertFalse(receipt["pit_admission_granted"])
        self.assertFalse(receipt["profitability_evaluation_authorized"])


if __name__ == "__main__":
    unittest.main()
