"""Prove archived first-source count replay remains fail-closed after 7-day expiry."""
import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import research_v1_m20_source_capsule_replay as p
from test_research_v1_m20_original_source_evidence_gate import fixture
from research_v1_m20_original_source_evidence_gate import (
    EvidenceGap, EXPECTED, validate_source_counts,
)


def install_fixture(root):
    m, reports, _ = fixture()
    man = root/"INDEXALERT_M20_2022_Q3_VERIFIED_SOURCE_ARTIFACT_MANIFEST.json"
    man.write_text(json.dumps(m), encoding="utf-8")
    base = root/"research_results/m20_original_gated_inputs"
    checks = {}
    for key in EXPECTED:
        folder = base/key
        folder.mkdir(parents=True)
        path = folder/"counts.json"
        path.write_text(json.dumps(reports[key]), encoding="utf-8")
        checks[key] = p._digest(path)
    verdict= root/"research_results/opendart_m20_original_evidence_gate/verdict.json"
    verdict.parent.mkdir(parents=True)
    verdict.write_text(json.dumps(validate_source_counts(reports)), encoding="utf-8")
    capsule = {
        "kind": p.CAPSULE_KIND,
        "source_kind": p.SOURCE_KIND,
        "source_manifest_sha256": p._digest(man),
        "source_count_files_sha256": checks,
        "source_gate_verdict_sha256": p._digest(verdict),
        "original_cfs_profit_cells_verified": False,
        "first_publication_instant_verified": False,
        "m20_feature_pit_admitted": False,
        "m20_performance_run_authorized": False,
        "real_orders_authorized": False,
        "ordering": "DISABLED",
    }
    cap = root/"research_results/m20_original_source_capsule/checksums.json"
    cap.parent.mkdir(parents=True)
    cap.write_text(json.dumps(capsule), encoding="utf-8")
    return cap, base, man, verdict


class SealedCapsuleReplayTests(unittest.TestCase):
    def test_success_is_history_snapshot_not_new_pit(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            install_fixture(root)
            result=p.replay(root, root/"replay.json")
            self.assertEqual(result["original_official_run_count_in_archive"],4)
            self.assertEqual(result["original_viewer_table_tags"],329)
            self.assertEqual(result["original_operating_label_candidates"],2)
            self.assertFalse(result["source_replay_is_new_official_dart_result"])
            self.assertFalse(result["m20_performance_run_authorized"])
            self.assertFalse(result["real_orders_authorized"])
            self.assertEqual(result["ordering"],"DISABLED")

    def test_tampered_source_json_rejected_by_sha(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            _,base,_,_=install_fixture(root)
            pth=base/"same_table"/"counts.json"
            data=json.loads(pth.read_text())
            data["profit_candidate_tables"]=3
            pth.write_text(json.dumps(data))
            with self.assertRaisesRegex(EvidenceGap,"REPLAY_CHECKSUM_MISMATCH"):
                p.replay(root,root/"out.json")

    def test_missing_fourth_original_source_fails_closed(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            _,base,_,_=install_fixture(root)
            (base/"header_rows"/"counts.json").unlink()
            with self.assertRaises(EvidenceGap):
                p.replay(root,root/"out.json")

    def test_explicit_pit_or_orders_in_capsule_are_never_admitted(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            cap,_,_,_=install_fixture(root)
            for field in ("original_cfs_profit_cells_verified",
                          "m20_feature_pit_admitted","real_orders_authorized"):
                unsafe=json.loads(cap.read_text())
                unsafe[field]=True
                cap.write_text(json.dumps(unsafe))
                with self.subTest(field=field),self.assertRaises(EvidenceGap):
                    p.replay(root,root/"out.json")
                unsafe[field]=False
                cap.write_text(json.dumps(unsafe))

    def test_change_manifest_identity_rejected_even_with_rehash(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            cap,_,manifest,_=install_fixture(root)
            altered=json.loads(manifest.read_text())
            altered["source_records"][0]["head_sha"]="f"*40
            manifest.write_text(json.dumps(altered))
            capsule=json.loads(cap.read_text())
            capsule["source_manifest_sha256"]=p._digest(manifest)
            cap.write_text(json.dumps(capsule))
            with self.assertRaisesRegex(EvidenceGap,"PINNED_SOURCE_REFERENCE_MISMATCH"):
                p.replay(root,root/"out.json")

    def test_sealed_original_verdict_mismatch_is_rejected(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            cap,_,_,verdict=install_fixture(root)
            tampered=json.loads(verdict.read_text())
            tampered["real_orders_authorized"]=True
            verdict.write_text(json.dumps(tampered))
            capsule=json.loads(cap.read_text())
            capsule["source_gate_verdict_sha256"]=p._digest(verdict)
            cap.write_text(json.dumps(capsule))
            with self.assertRaisesRegex(EvidenceGap,"REPLAY_PREVIOUS_VERDICT_DRIFT"):
                p.replay(root,root/"out.json")

    def test_intermediate_source_input_directory_symlink_denied_even_with_valid_hashes(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            install_fixture(root)
            source=root/"research_results/m20_original_gated_inputs"
            outside=root/"outside_source_files"
            source.rename(outside)
            source.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(EvidenceGap,"REPLAY_CAPSULE_PATH_SYMLINK"):
                p.replay(root,root/"out.json")

    def test_individual_count_parent_directory_symlink_denied(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            install_fixture(root)
            folder=root/"research_results/m20_original_gated_inputs/same_table"
            outside=root/"elsewhere_same_table"
            folder.rename(outside)
            folder.symlink_to(outside,target_is_directory=True)
            with self.assertRaisesRegex(EvidenceGap,"REPLAY_CAPSULE_PATH_SYMLINK"):
                p.replay(root,root/"out.json")

    def test_manifest_and_verdict_intermediate_or_final_symlinks_denied(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            install_fixture(root)
            manifest=root/"INDEXALERT_M20_2022_Q3_VERIFIED_SOURCE_ARTIFACT_MANIFEST.json"
            direct=root/"other_manifest.json"
            manifest.rename(direct)
            manifest.symlink_to(direct)
            with self.assertRaisesRegex(EvidenceGap,"REPLAY_CAPSULE_PATH_SYMLINK"):
                p.replay(root,root/"out.json")
        with TemporaryDirectory() as td:
            root=Path(td)
            install_fixture(root)
            dirname=root/"research_results/opendart_m20_original_evidence_gate"
            direct=root/"elsewhere_verdict"
            dirname.rename(direct)
            dirname.symlink_to(direct,target_is_directory=True)
            with self.assertRaisesRegex(EvidenceGap,"REPLAY_CAPSULE_PATH_SYMLINK"):
                p.replay(root,root/"out.json")

    def test_sealed_file_path_must_be_relative_and_inside_archive(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            install_fixture(root)
            for name in ("../outside.json",str(root/"absolute.json")):
                with self.subTest(name=name),self.assertRaisesRegex(
                    EvidenceGap,"REPLAY_RELATIVE_PATH_INVALID"
                ):
                    p._sealed_file(root,Path(name))

    def test_capsule_directory_symlink_denied(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            install_fixture(root)
            alias=root/"alias"
            alias.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(EvidenceGap,"REPLAY_CAPSULE_ROOT_INVALID"):
                p.replay(alias, root/"out.json")


if __name__ == "__main__":
    unittest.main()
