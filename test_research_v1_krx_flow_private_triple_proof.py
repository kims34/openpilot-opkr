"""Network-free adversarial tests of KRX raw/receipt/request/triple binding."""
from __future__ import annotations

import hashlib
import unittest

from research_v1_krx_flow_private_triple_proof import (
    KRXPrivateFlowTripleError,
    RECEIPT_BODY,
    ORIGINAL_CLIENT_REVISION,
    _sha,
    verify_krx_2022_private_flow_triple,
)


def fixture():
    task = {
        "plan_id": "INDEXALERT-KRX-HIST-ACQ-v3",
        "execution_contract_id": "INDEXALERT-KRX-HIST-EXEC-v3",
        "phase": "PER_SECURITY_HISTORY",
        "source_family": "KRX_INVESTOR_FLOW",
        "request_spec": {
            "kind": "investor_trading_individual_daily",
            "params": {
                "isuCd": "KR7005930003",
                "strtDd": "20220103",
                "endDd": "20221230",
            },
        },
        "contains_security_identifier": True,
    }
    task["task_id"] = _sha(task)
    request = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT02303",
        "method": "csv",
        "menu_id": "MDC0201020302",
        "params": {
            "inqTpCd": "2", "trdVolVal": "2", "askBid": "3",
            "detailView": "1", "money": "1",
            "tboxisuCd_finder_stkisu0_0": "",
            "isuCd2": "",
            "codeNmisuCd_finder_stkisu0_0": "",
            "param1isuCd_finder_stkisu0_0": "ALL",
            "csvxls_isNo": "false",
            "isuCd": "KR7005930003",
            "strtDd": "20220103",
            "endDd": "20221230",
        },
        "pinned_client_commit": ORIGINAL_CLIENT_REVISION,
    }
    receipt = {
        "receipt_version": "2026-10-02.v1",
        "source_family": "KRX_INVESTOR_FLOW",
        "intended_use_scope": "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
        "access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "dataset_identifier": "MDCSTAT02303",
        "authorization_evidence_reference": "SYNTHETIC_ONLY",
        "authorization_evidence_fingerprint_sha256": "f"*64,
        "client_revision": ORIGINAL_CLIENT_REVISION,
        "retrieved_at": "2026-10-03T12:30:00+09:00",
        "request_metadata_sha256": _sha(request),
        "response_schema_sha256": "b"*64,
        "response_payload_sha256": "c"*64,
        "response_rows": 250,
        "response_columns": [
            "일자", "금융투자", "보험", "투신", "사모", "은행",
            "기타금융", "연기금 등", "기타법인", "개인", "외국인",
            "기타외국인", "전체",
        ],
        "public_contract_evidence_version": "SYNTHETIC",
        "public_contract_evidence_fingerprint_sha256": "e"*64,
        "alpha_or_final_judge_promotion_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    receipt["receipt_fingerprint_sha256"] = _sha(
        {k: receipt[k] for k in RECEIPT_BODY}
    )
    raw = b"synthetic-private-krx-csv-byte-fixture"
    completion = {
        "task_id": task["task_id"],
        "request_metadata_sha256": receipt["request_metadata_sha256"],
        "raw_object_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_bytes_size": len(raw),
        "response_rows": receipt["response_rows"],
        "response_schema_sha256": receipt["response_schema_sha256"],
        "response_payload_sha256": receipt["response_payload_sha256"],
        "receipt_fingerprint_sha256": receipt["receipt_fingerprint_sha256"],
    }
    return {
        "original_raw_bytes": raw,
        "acquisition_receipt": receipt,
        "completion": completion,
        "canonical_request": request,
        "frozen_task": task,
    }


class PurePrivateOriginalTripleTest(unittest.TestCase):
    def test_synthetic_triple_hashes_match_without_any_pit_claim(self):
        r = verify_krx_2022_private_flow_triple(**fixture())
        self.assertTrue(r["exact_raw_object_bytes_match_checkpoint_sha"])
        self.assertTrue(r["exact_receipt_fingerprint_matches_body"])
        self.assertTrue(r["exact_original_resolved_request_hash_matches_receipt"])
        self.assertTrue(r["has_nonempty_source_response"])
        for flag in (
            "provider_authenticity_independently_verified",
            "original_2022_as_published_vintage_verified",
            "original_2022_historical_publication_instant_verified",
            "historical_correction_lineage_verified",
            "foreign_institution_value_unit_semantics_verified",
            "parsed_payload_digest_independently_recomputed",
            "source_admitted", "performance_testing_authorized",
            "sealed_holdout_authorized", "ordering_enabled",
            "network_request_attempted", "source_numeric_rows_or_identifiers_emitted",
        ):
            self.assertIs(r[flag], False, flag)
        self.assertNotIn("KR7005930003", str(r))
        self.assertNotIn("SYNTHETIC_ONLY", str(r))

    def test_modifying_original_byte_rejects_old_checkpoint_hash(self):
        item = fixture()
        item["original_raw_bytes"] += b"\n"
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "BYTE_SHA_DRIFT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_receipt_body_change_rejected_even_if_completion_still_matches(self):
        item = fixture()
        item["acquisition_receipt"]["response_rows"] += 1
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "BODY_TAMPERED"):
            verify_krx_2022_private_flow_triple(**item)

    def test_malicious_rehash_cannot_mask_altered_net_buy_mode(self):
        item = fixture()
        item["canonical_request"]["params"]["askBid"] = "1"
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "NET_BUY_VALUE"):
            verify_krx_2022_private_flow_triple(**item)

    def test_relabel_2026_as_2022_rejected(self):
        item = fixture()
        item["frozen_task"]["request_spec"]["params"]["strtDd"] = "20260921"
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "HISTORIC_YEAR"):
            verify_krx_2022_private_flow_triple(**item)

    def test_2022_request_window_mismatch_rejected(self):
        item = fixture()
        item["canonical_request"]["params"]["endDd"] = "20221229"
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "REQUEST_TO_FROZEN"):
            verify_krx_2022_private_flow_triple(**item)

    def test_completion_attaches_wrong_task_rejected(self):
        item = fixture()
        item["completion"]["task_id"] = "0"*64
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "COMPLETED_TASK_ID_DRIFT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_retrieval_time_without_timezone_rejected(self):
        item = fixture()
        item["acquisition_receipt"]["retrieved_at"] = "2026-10-03T12:30:00"
        item["acquisition_receipt"]["receipt_fingerprint_sha256"] = _sha(
            {k: item["acquisition_receipt"][k] for k in RECEIPT_BODY}
        )
        item["completion"]["receipt_fingerprint_sha256"] = item["acquisition_receipt"]["receipt_fingerprint_sha256"]
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "NOT_AWARE"):
            verify_krx_2022_private_flow_triple(**item)

    def test_empty_response_cannot_claim_full_source(self):
        item = fixture()
        item["acquisition_receipt"]["response_rows"] = 0
        item["acquisition_receipt"]["receipt_fingerprint_sha256"] = _sha(
            {k: item["acquisition_receipt"][k] for k in RECEIPT_BODY}
        )
        item["completion"]["response_rows"] = 0
        item["completion"]["receipt_fingerprint_sha256"] = item["acquisition_receipt"]["receipt_fingerprint_sha256"]
        r = verify_krx_2022_private_flow_triple(**item)
        self.assertFalse(r["has_nonempty_source_response"])
        self.assertFalse(r["source_admitted"])

    def test_no_escalation_of_orders_or_holdout(self):
        item = fixture()
        item["acquisition_receipt"]["sealed_holdout_authorized"] = True
        item["acquisition_receipt"]["receipt_fingerprint_sha256"] = _sha(
            {k: item["acquisition_receipt"][k] for k in RECEIPT_BODY}
        )
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ESCALATED_AUTHORITY"):
            verify_krx_2022_private_flow_triple(**item)


if __name__ == "__main__":
    unittest.main()
