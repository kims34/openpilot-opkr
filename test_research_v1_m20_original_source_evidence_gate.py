"""Offline tests for exact four run IDs + immutable official artifacts, NO PIT."""
import copy
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import research_v1_m20_original_source_evidence_gate as p


def fixture():
    contract = {
        "schema_version": "M20_FIRST_Q3_ORIGINAL_VIEWER_EVIDENCE_1",
        "fixed_cohort_slot": 5,
        "year": 2022,
        "report": "Q3",
        "ordering": "DISABLED",
        "performance_authorization": False,
        "order_authorization": False,
        "source_records": [
            {"key": key, "run_id": v[0], "head_sha": v[1],
             "artifact_id": v[2], "artifact_name": v[3], "artifact_digest": v[4]}
            for key, v in p.EXPECTED.items()
        ],
    }
    reports = {}
    metadata = {}
    for key, v in p.EXPECTED.items():
        reports[key] = {
            "fixed_cohort_slot": 5,
            "source_status": v[5],
            "ordering": "DISABLED",
            "credential_present": True,
            **{field: False for field in p.REQUIRED_BLOCKS},
            **p.OBSERVED[key],
        }
        metadata[key] = {
            "run": {"id": v[0], "head_sha": v[1],
                    "status": "completed", "conclusion": "success"},
            "artifact": {"id": v[2], "name": v[3],
                         "digest": v[4], "expired": False},
        }
    return contract, reports, metadata


class PinnedOriginalEvidenceTests(unittest.TestCase):
    def test_successful_count_reconciliation_stays_explicit_no_go(self):
        c, reports, meta=fixture()
        p.validate_contract(c)
        p.validate_metadata(c,meta)
        a=p.validate_source_counts(reports)
        self.assertEqual(a["verified_pinned_source_artifact_count"],4)
        self.assertEqual(a["financial_viewer_table_tags"],329)
        self.assertEqual(a["first_original_operating_label_table_candidates"],2)
        self.assertFalse(a["actual_original_cfs_operating_profit_cell_period_lineage_verified"])
        self.assertFalse(a["frozen_strategy_source_data_admitted"])
        self.assertFalse(a["m20_performance_run_authorized"])
        self.assertEqual(a["ordering"],"DISABLED")

    def test_malformed_manifest_reference_or_missing_run_blocks(self):
        c,reports,meta=fixture()
        for bad in (
            lambda z:z["source_records"].pop(),
            lambda z:z["source_records"][2].update(run_id=1),
            lambda z:z["source_records"][3].update(artifact_digest="sha256:"+"0"*64),
            lambda z:z.update(performance_authorization=True),
            lambda z:z.update(fixed_cohort_slot=4),
            lambda z:z.update(ordering="ENABLED"),
        ):
            changed=copy.deepcopy(c)
            bad(changed)
            with self.assertRaises(p.EvidenceGap):
                p.validate_contract(changed)

    def test_forged_run_head_or_expired_artifact_fails(self):
        c,_,metadata=fixture()
        for key,field,value in (
            ("same_table","run",{"id":p.EXPECTED["same_table"][0],
                                 "head_sha":"0"*40,"status":"completed","conclusion":"success"}),
            ("header_rows","artifact",{"id":p.EXPECTED["header_rows"][2],
                                         "name":p.EXPECTED["header_rows"][3],
                                         "digest":p.EXPECTED["header_rows"][4],
                                         "expired":True}),
        ):
            tampered=copy.deepcopy(metadata)
            tampered[key][field]=value
            with self.assertRaises(p.EvidenceGap):
                p.validate_metadata(c,tampered)

    def test_any_false_to_true_pit_or_broker_change_fails_closed(self):
        _,reports,_=fixture()
        for flag in (*p.REQUIRED_BLOCKS,"original_cfs_identity_and_profit_colmap_verified",
                     "original_2022_q3_standalone_cfs_operating_amount_verified"):
            sample=copy.deepcopy(reports)
            sample["header_rows"][flag]=True
            with self.subTest(field=flag),self.assertRaises(p.EvidenceGap):
                p.validate_source_counts(sample)

    def test_mismatch_source_count_or_period_flag_fails(self):
        _,reports,_=fixture()
        for key,field,val in (
            ("financial_sections","viewer_financial_total_table_tags",328),
            ("same_subdocument","operating_and_2022_complete_q3_window_same_section_count",1),
            ("same_table","profit_tables_with_three_month_header",1),
            ("header_rows","operating_with_preceding_current_and_prior_quarter_words",1),
        ):
            sample=copy.deepcopy(reports)
            sample[key][field]=val
            with self.subTest(key=key,field=field),self.assertRaises(p.EvidenceGap):
                p.validate_source_counts(sample)

    def test_unknown_private_error_string_or_missing_permission_bit_blocks(self):
        _,reports,_=fixture()
        r=copy.deepcopy(reports)
        r["financial_sections"]["raw_private_receipt"]="20221114000001"
        with self.assertRaises(p.EvidenceGap):
            p.validate_source_counts(r)
        r=copy.deepcopy(reports)
        r["financial_sections"].pop("real_orders_authorized")
        with self.assertRaises(p.EvidenceGap):
            p.validate_source_counts(r)

    def test_duplicate_json_field_is_rejected_before_summary(self):
        with self.assertRaisesRegex(p.EvidenceGap,"DUPLICATE_JSON_KEY"):
            json.loads('{"source_status":"pass","source_status":"override"}',
                       object_pairs_hook=p._unique_pairs)

    def test_full_materialized_offline_evidence_and_metadata_roundtrip(self):
        manifest,reports,metadata=fixture()
        with TemporaryDirectory() as td:
            root=Path(td)
            man=root/"manifest.json"
            inp=root/"artifacts"
            meta=root/"metadata"
            target=root/"verdict.json"
            man.write_text(json.dumps(manifest),encoding="utf-8")
            meta.mkdir()
            for key in p.EXPECTED:
                section=inp/key
                section.mkdir(parents=True)
                (section/"counts.json").write_text(
                    json.dumps(reports[key]),encoding="utf-8")
                for typ in ("run","artifact"):
                    (meta/(key+"."+typ+".json")).write_text(
                        json.dumps(metadata[key][typ]),encoding="utf-8")
            outcome=p.run(man,inp,meta,target)
            self.assertEqual(outcome["status"],"FOUR_OFFICIAL_SOURCE_DIAGNOSTICS_AGREE_NO_PIT")
            self.assertFalse(outcome["real_orders_authorized"])
            self.assertFalse(outcome["frozen_strategy_source_data_admitted"])
            self.assertNotIn("20221114000001",target.read_text(encoding="utf-8"))


if __name__=="__main__":
    unittest.main()
