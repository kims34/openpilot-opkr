"""Synthetic offline safety tests for private existing KRX flow task inventory."""
from __future__ import annotations

import copy
import unittest

from research_v1_krx_flow_existing_private_checkpoint_inventory import (
    KRXExistingFlowInventoryError, _sha, _verify_original_execution_prefix,
    summarise_existing_flow_checkpoints,
    summarise_frozen_2026_10_03_checkpoint_set,
)

PLAN = "INDEXALERT-KRX-HIST-ACQ-v3"
EXEC = "INDEXALERT-KRX-HIST-EXEC-v3"
FLOW = "investor_trading_individual_daily"
HALT = "trading_halt"


def task(kind, start, end, isu_cd="KR7005930003"):
    params = {"isuCd": isu_cd, "strtDd": start, "endDd": end}
    if kind == HALT:
        params["isuCd2"] = "005930"
    data = {
        "plan_id": PLAN,
        "execution_contract_id": EXEC,
        "phase": "PER_SECURITY_HISTORY",
        "source_family": "KRX_INVESTOR_FLOW" if kind == FLOW else "KRX_SECURITY_STATUS",
        "request_spec": {"kind": kind, "params": params},
        "contains_security_identifier": True,
    }
    data["task_id"] = _sha(data)
    return data


def receipt(item, rows=3):
    return {
        "task_id": item["task_id"],
        "request_metadata_sha256": "a" * 64,
        "raw_object_sha256": "b" * 64,
        "raw_bytes_size": 512,
        "response_rows": rows,
        "response_schema_sha256": "c" * 64,
        "response_payload_sha256": "d" * 64,
        "receipt_fingerprint_sha256": "e" * 64,
    }


def sample():
    tasks = [
        task(FLOW, "20220103", "20221230"),
        task(FLOW, "20230102", "20231229"),
        task(HALT, "20220101", "20230101"),
        task(FLOW, "20220201", "20220331", "KR7000060004"),
    ]
    ids = sorted(t["task_id"] for t in tasks)
    fp = _sha(ids)
    manifest = {
        "plan_id": PLAN, "execution_contract_id": EXEC,
        "phase": "PER_SECURITY_HISTORY", "task_count": len(tasks),
        "task_set_fingerprint_sha256": fp, "tasks": tasks,
    }
    state = {
        "plan_id": PLAN, "execution_contract_id": EXEC,
        "phase": "PER_SECURITY_HISTORY",
        "expected_task_count": len(tasks),
        "task_set_fingerprint_sha256": fp,
        "expected_task_ids_sha256": ids,
        "completed": {
            tasks[0]["task_id"]: receipt(tasks[0], 3),
            tasks[2]["task_id"]: receipt(tasks[2], 0),
            tasks[3]["task_id"]: receipt(tasks[3], 0),
        },
        "completed_task_count": 3,
        "failed_task_count": 0,
        "phase_complete": False,
    }
    return manifest, state, fp


def audit(manifest, state, fp):
    return summarise_existing_flow_checkpoints(
        manifest, state,
        expected_by_kind={FLOW: 3, HALT: 1},
        expected_task_fingerprint_sha256=fp,
    )


class KRXPrivateFlowInventoryTest(unittest.TestCase):
    def test_original_sequential_prefix_proves_all_flow_in_synthetic_order(self):
        m, s, _ = sample()
        m["tasks"].sort(key=lambda t: t["source_family"])
        first_three = m["tasks"][:3]
        s["completed"] = {t["task_id"]: receipt(t) for t in first_three}
        s["completed_task_count"] = 3
        proof = _verify_original_execution_prefix(
            m, s, expected_flow_count=3,
        )
        self.assertTrue(proof["original_flow_first_task_order_verified"])
        self.assertTrue(proof["original_execution_completion_prefix_verified"])
        self.assertEqual(proof["flow_completed_by_verified_prefix"], 3)
        self.assertEqual(proof["flow_remaining_by_verified_prefix"], 0)
        self.assertFalse(proof["original_source_data_bytes_independently_verified"])
        self.assertFalse(proof["original_2022_flow_vintage_verified"])

    def test_old_completion_count_cannot_mask_out_of_order_hole(self):
        m, s, _ = sample()
        m["tasks"].sort(key=lambda t: t["source_family"])
        # Keep exactly 3 completed, but skip the second flow task and
        # spuriously include one later halt task.
        s["completed"] = {
            t["task_id"]: receipt(t)
            for t in (m["tasks"][0], m["tasks"][2], m["tasks"][3])
        }
        s["completed_task_count"] = 3
        with self.assertRaisesRegex(
            KRXExistingFlowInventoryError,
            "NONCONTIGUOUS_ORIGINAL_EXECUTION_PREFIX",
        ):
            _verify_original_execution_prefix(m, s, expected_flow_count=3)

    def test_sorted_manifest_required_before_prefix_claim(self):
        m, s, _ = sample()
        # Original synthetic fixture interleaves status and flow.
        with self.assertRaisesRegex(
            KRXExistingFlowInventoryError,
            "ORIGINAL_FLOW_FIRST_TASK_ORDER_DRIFT",
        ):
            _verify_original_execution_prefix(m, s, expected_flow_count=3)

    def test_exact_prefix_partial_flow_completion_is_not_full(self):
        m, s, _ = sample()
        m["tasks"].sort(key=lambda t: t["source_family"])
        first_two = m["tasks"][:2]
        s["completed"] = {t["task_id"]: receipt(t) for t in first_two}
        s["completed_task_count"] = 2
        proof = _verify_original_execution_prefix(
            m, s, expected_flow_count=3,
        )
        self.assertEqual(proof["flow_completed_by_verified_prefix"], 2)
        self.assertEqual(proof["flow_remaining_by_verified_prefix"], 1)

    def test_counts_2022_existing_receipts_without_confusing_with_pit(self):
        manifest, state, fp = sample()
        out = audit(manifest, state, fp)
        self.assertEqual(out["investor_flow_total_tasks"], 3)
        self.assertEqual(out["investor_flow_completed_checkpoints"], 2)
        self.assertEqual(out["investor_flow_pending_checkpoints"], 1)
        self.assertEqual(out["year_2022_flow_expected_tasks"], 2)
        self.assertEqual(out["year_2022_flow_completed_checkpoints"], 2)
        self.assertEqual(out["year_2022_flow_nonempty_response_checkpoints"], 1)
        self.assertEqual(out["year_2022_flow_empty_response_checkpoints"], 1)
        self.assertEqual(out["trading_halt_completed_checkpoints"], 1)
        self.assertEqual(out["remaining_tasks"], 1)
        for key in (
            "private_raw_objects_reverified_in_this_function",
            "source_owner_private_manifest_storage_origin_verified",
            "independent_original_2022_publication_vintage_verified",
            "historical_issuer_universe_and_tradability_verified",
            "source_admitted", "performance_testing_authorized",
            "sealed_holdout_authorized", "ordering_enabled",
            "network_request_attempted", "raw_rows_or_identifiers_emitted",
        ):
            self.assertIs(out[key], False, key)
        self.assertNotIn("005930", str(out))
        self.assertNotIn("KR7005930003", str(out))
        self.assertNotIn("task_id", str(out))

    def test_frozen_incompatible_fake_manifest_is_rejected(self):
        m, s, _ = sample()
        with self.assertRaises(KRXExistingFlowInventoryError):
            summarise_frozen_2026_10_03_checkpoint_set(m, s)

    def test_public_result_ignores_fake_source_admission_flags(self):
        m, s, fp = sample()
        m["source_admitted"] = True
        s["performance_testing_authorized"] = True
        result = audit(m, s, fp)
        self.assertFalse(result["source_admitted"])
        self.assertFalse(result["performance_testing_authorized"])

    def test_fake_completion_not_in_pinned_task_set_rejected(self):
        m, s, fp = sample()
        s["completed"]["f" * 64] = receipt(m["tasks"][1])
        s["completed_task_count"] += 1
        with self.assertRaises(KRXExistingFlowInventoryError):
            audit(m, s, fp)

    def test_task_semantics_changed_without_hash_change_rejected(self):
        m, s, fp = sample()
        m["tasks"][0]["request_spec"]["params"]["strtDd"] = "20210103"
        with self.assertRaisesRegex(KRXExistingFlowInventoryError, "TASK_CONTENT"):
            audit(m, s, fp)

    def test_stale_expected_task_set_rejected(self):
        m, s, fp = sample()
        s["expected_task_ids_sha256"].pop()
        with self.assertRaisesRegex(KRXExistingFlowInventoryError, "MEMBERSHIP"):
            audit(m, s, fp)

    def test_missing_digest_is_not_a_completed_receipt(self):
        m, s, fp = sample()
        s["completed"][m["tasks"][0]["task_id"]]["raw_object_sha256"] = "missing"
        with self.assertRaisesRegex(KRXExistingFlowInventoryError, "DIGEST"):
            audit(m, s, fp)

    def test_unexpected_flow_request_mode_is_rejected(self):
        m, s, fp = sample()
        m["tasks"][0]["request_spec"]["params"]["askBid"] = "1"
        m["tasks"][0]["task_id"] = _sha({k:v for k,v in m["tasks"][0].items() if k!="task_id"})
        with self.assertRaises(KRXExistingFlowInventoryError):
            audit(m, s, fp)

    def test_zero_return_not_promoted_to_numeric_flow(self):
        m, s, fp = sample()
        result = audit(m, s, fp)
        self.assertEqual(result["year_2022_flow_empty_response_checkpoints"], 1)
        self.assertFalse(result["source_admitted"])

    def test_bogus_complete_phase_with_missing_tasks_rejected(self):
        m, s, fp = sample()
        s["phase_complete"] = True
        with self.assertRaisesRegex(KRXExistingFlowInventoryError, "COMPLETENESS"):
            audit(m, s, fp)

    def test_negative_row_count_rejected(self):
        m, s, fp = sample()
        s["completed"][m["tasks"][0]["task_id"]]["response_rows"] = -1
        with self.assertRaisesRegex(KRXExistingFlowInventoryError, "LENGTH"):
            audit(m, s, fp)

    def test_unverified_security_identity_format_rejected(self):
        m, s, fp = sample()
        m["tasks"][0]["request_spec"]["params"]["isuCd"] = "005930"
        with self.assertRaises(KRXExistingFlowInventoryError):
            audit(m, s, fp)

    def test_missing_manifest_task_rejected(self):
        m, s, fp = sample()
        m["tasks"].pop()
        with self.assertRaises(KRXExistingFlowInventoryError):
            audit(m, s, fp)

    def test_reversed_year_window_rejected(self):
        m, s, fp = sample()
        m["tasks"][0]["request_spec"]["params"]["endDd"] = "20211231"
        with self.assertRaises(KRXExistingFlowInventoryError):
            audit(m, s, fp)

    def test_duplicate_manifest_task_rejected(self):
        m, s, fp = sample()
        m["tasks"].append(copy.deepcopy(m["tasks"][0]))
        m["task_count"] += 1
        with self.assertRaisesRegex(KRXExistingFlowInventoryError, "DUPLICATE"):
            audit(m, s, fp)


if __name__ == "__main__":
    unittest.main()
