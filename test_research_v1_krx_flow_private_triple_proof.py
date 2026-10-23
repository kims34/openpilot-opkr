"""Network-free adversarial tests of KRX raw/receipt/request/triple binding."""
from __future__ import annotations

import csv
from datetime import date, timedelta
import hashlib
import io
import unittest

from research_v1_krx_public_evidence import (
    PUBLIC_EVIDENCE_VERSION,
    public_evidence_fingerprint_sha256,
)

from research_v1_krx_flow_private_triple_proof import (
    KRXPrivateFlowTripleError,
    RECEIPT_BODY,
    ORIGINAL_CLIENT_REVISION,
    ORIGINAL_RECEIPT_VERSION, ORIGINAL_RECEIPT_GUARDRAIL,
    ORIGINAL_AUTH_EVIDENCE_REFERENCE, ORIGINAL_AUTH_EVIDENCE_RECORD_SHA256,
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
        "receipt_version": ORIGINAL_RECEIPT_VERSION,
        "source_family": "KRX_INVESTOR_FLOW",
        "intended_use_scope": "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
        "access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "dataset_identifier": "MDCSTAT02303",
        "authorization_evidence_reference": ORIGINAL_AUTH_EVIDENCE_REFERENCE,
        "authorization_evidence_fingerprint_sha256": ORIGINAL_AUTH_EVIDENCE_RECORD_SHA256,
        "client_revision": "krx-data-api@" + ORIGINAL_CLIENT_REVISION,
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
        "public_contract_evidence_version": PUBLIC_EVIDENCE_VERSION,
        "public_contract_evidence_fingerprint_sha256": public_evidence_fingerprint_sha256(),
        "alpha_or_final_judge_promotion_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "guardrail": ORIGINAL_RECEIPT_GUARDRAIL,
    }
    receipt["receipt_fingerprint_sha256"] = _sha(
        {k: receipt[k] for k in RECEIPT_BODY}
    )
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(receipt["response_columns"])
    # Each daily response observation is one distinct 2022 session candidate.
    # Do not claim these synthetic weekday dates are independently KRX-open.
    day = date(2022, 1, 3)
    rows = []
    while len(rows) < 250:
        if day.weekday() < 5:
            rows.append([day.isoformat()] + [str(len(rows))] *
                        (len(receipt["response_columns"]) - 1))
        day += timedelta(days=1)
    writer.writerows(rows)
    raw = buffer.getvalue().encode("euc_kr")
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


def retarget_original_bytes(item, data):
    item["original_raw_bytes"] = data
    item["completion"]["raw_object_sha256"] = hashlib.sha256(data).hexdigest()
    item["completion"]["raw_bytes_size"] = len(data)


def replace_date_in_first_csv_row(item, value):
    original = item["original_raw_bytes"].decode("euc_kr")
    lines = original.splitlines(keepends=True)
    fields = next(csv.reader([lines[1]]))
    fields[0] = value
    buf = io.StringIO(newline="")
    csv.writer(buf).writerow(fields)
    lines[1] = buf.getvalue()
    retarget_original_bytes(item, "".join(lines).encode("euc_kr"))


def reshape_columns_and_rehash_original_receipt(item, retained_columns):
    """Malicious fixture: raw CSV, receipt body, and checkpoint all rehashed.

    Deliberately leaves pandas schema/payload fingerprints as internally
    declared digests, because this standalone structural gate runs before
    full pinned pandas re-materialization. Any false-positive here would be
    especially dangerous when other hashes were self-consistently replaced.
    """
    source = list(csv.reader(io.StringIO(
        item["original_raw_bytes"].decode("euc_kr"), newline=""
    )))
    columns = source[0]
    subset_indices = [columns.index(name) for name in retained_columns]
    buf = io.StringIO(newline="")
    writer = csv.writer(buf)
    writer.writerows([[row[i] for i in subset_indices] for row in source])
    retarget_original_bytes(item, buf.getvalue().encode("euc_kr"))
    rec = item["acquisition_receipt"]
    rec["response_columns"] = list(retained_columns)
    rec["receipt_fingerprint_sha256"] = _sha({
        key: rec[key] for key in RECEIPT_BODY
    })
    item["completion"]["receipt_fingerprint_sha256"] = (
        rec["receipt_fingerprint_sha256"]
    )


class PurePrivateOriginalTripleTest(unittest.TestCase):
    def test_synthetic_triple_hashes_match_without_any_pit_claim(self):
        r = verify_krx_2022_private_flow_triple(**fixture())
        self.assertTrue(r["exact_raw_object_bytes_match_checkpoint_sha"])
        self.assertTrue(r["exact_receipt_fingerprint_matches_body"])
        self.assertTrue(r["exact_original_resolved_request_hash_matches_receipt"])
        self.assertTrue(r["has_nonempty_source_response"])
        self.assertTrue(r["archived_csv_header_and_row_count_cross_checked"])
        self.assertTrue(r["archived_csv_observed_dates_in_2022_task_window_checked"])
        self.assertTrue(r["archived_csv_duplicate_day_rejected"])
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

    def test_authorization_record_sha_matches_exact_original_git_artifact(self):
        # The 2026-10-03 producer's trusted *metadata record*, NOT the
        # original external email or current site approval, is independently
        # reconstructed from the original secret-free Git blob. The full
        # historical authorization still cannot pass any source/PIT gate.
        import json
        from pathlib import Path
        from datetime import datetime, timezone
        from research_v1_krx_authorization_evidence import (
            validate_authorization_evidence,
        )
        p = (
            Path(__file__).resolve().parent
            / "INDEXALERT_KRX_AUTH_EVIDENCE_INVESTOR_FLOW.json"
        )
        raw = p.read_bytes()
        git_blob_sha = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw
        ).hexdigest()
        self.assertEqual(
            git_blob_sha, "e4c19187cc66aefd895c87a4ef8973981a248d00"
        )
        record = json.loads(raw.decode("utf-8"))
        result = validate_authorization_evidence(
            record,
            expected_source_family="KRX_INVESTOR_FLOW",
            expected_access_route="DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
            expected_intended_use_scope="INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
            evaluation_time=datetime(2026, 10, 3, tzinfo=timezone.utc),
            expected_reference=ORIGINAL_AUTH_EVIDENCE_REFERENCE,
        )
        self.assertEqual(
            result["record_fingerprint_sha256"],
            ORIGINAL_AUTH_EVIDENCE_RECORD_SHA256,
        )
        self.assertFalse(result["bulk_historical_acquisition_authorized"])
        self.assertFalse(result["feature_performance_testing_authorized"])
        self.assertFalse(result["live_trading_authorized"])

    def test_original_public_evidence_source_blob_stays_frozen(self):
        from pathlib import Path
        path = Path(__file__).resolve().parent / "research_v1_krx_public_evidence.py"
        data = path.read_bytes()
        self.assertEqual(
            hashlib.sha1(
                b"blob " + str(len(data)).encode("ascii") + bytes([0]) + data
            ).hexdigest(),
            "d3876658d5793eaeddf794343c31c0b10f7cac57",
        )

    def test_wrong_authorization_fingerprint_with_rehashed_receipt_rejected(self):
        item = fixture()
        r = item["acquisition_receipt"]
        r["authorization_evidence_fingerprint_sha256"] = "a" * 64
        r["receipt_fingerprint_sha256"] = _sha({
            k: r[k] for k in RECEIPT_BODY
        })
        item["completion"]["receipt_fingerprint_sha256"] = (
            r["receipt_fingerprint_sha256"]
        )
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError,
            "ORIGINAL_RECEIPT_AUTH_EVIDENCE_DRIFT",
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_wrong_original_authorization_reference_with_rehashed_receipt_rejected(self):
        item = fixture()
        r = item["acquisition_receipt"]
        r["authorization_evidence_reference"] = "UNTRUSTED_ALTERNATE_RECORD"
        r["receipt_fingerprint_sha256"] = _sha({
            k: r[k] for k in RECEIPT_BODY
        })
        item["completion"]["receipt_fingerprint_sha256"] = (
            r["receipt_fingerprint_sha256"]
        )
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError,
            "ORIGINAL_RECEIPT_AUTH_EVIDENCE_DRIFT",
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_wrong_original_public_contract_version_rehashed_rejected(self):
        item = fixture()
        r = item["acquisition_receipt"]
        r["public_contract_evidence_version"] = "2026-10-04.v9"
        r["receipt_fingerprint_sha256"] = _sha({
            k: r[k] for k in RECEIPT_BODY
        })
        item["completion"]["receipt_fingerprint_sha256"] = (
            r["receipt_fingerprint_sha256"]
        )
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError,
            "ORIGINAL_RECEIPT_PUBLIC_CONTRACT_EVIDENCE_DRIFT",
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_wrong_original_public_contract_fingerprint_rehashed_rejected(self):
        item = fixture()
        r = item["acquisition_receipt"]
        r["public_contract_evidence_fingerprint_sha256"] = "0" * 64
        r["receipt_fingerprint_sha256"] = _sha({
            k: r[k] for k in RECEIPT_BODY
        })
        item["completion"]["receipt_fingerprint_sha256"] = (
            r["receipt_fingerprint_sha256"]
        )
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError,
            "ORIGINAL_RECEIPT_PUBLIC_CONTRACT_EVIDENCE_DRIFT",
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_wrong_original_receipt_version_still_rejected(self):
        item = fixture()
        r = item["acquisition_receipt"]
        r["receipt_version"] = "2026-10-02.v1"
        r["receipt_fingerprint_sha256"] = _sha({
            k: r[k] for k in RECEIPT_BODY
        })
        item["completion"]["receipt_fingerprint_sha256"] = (
            r["receipt_fingerprint_sha256"]
        )
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError, "ORIGINAL_RECEIPT_VERSION_DRIFT"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_wrong_historical_source_scope_still_rejected(self):
        item = fixture()
        r = item["acquisition_receipt"]
        r["intended_use_scope"] = "INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION"
        r["receipt_fingerprint_sha256"] = _sha({
            k: r[k] for k in RECEIPT_BODY
        })
        item["completion"]["receipt_fingerprint_sha256"] = (
            r["receipt_fingerprint_sha256"]
        )
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError, "ORIGINAL_RECEIPT_SCOPE_DRIFT"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_guardrail_override_still_rejected(self):
        item = fixture()
        item["acquisition_receipt"]["guardrail"] = "PERFORMANCE_APPROVED"
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError, "ORIGINAL_RECEIPT_GUARDRAIL_DRIFT"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_unknown_receipt_promotion_field_is_blocked(self):
        item = fixture()
        item["acquisition_receipt"]["promotion_authorized"] = True
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError, "ORIGINAL_RECEIPT_FIELDS_DRIFT"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_date_only_csv_never_passes_investor_schema(self):
        item = fixture()
        reshape_columns_and_rehash_original_receipt(item, ["일자"])
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError,
            "ORIGINAL_CSV_INVESTOR_BUCKET_SCHEMA_DRIFT"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_foreign_only_csv_never_counts_as_institution_coverage(self):
        item = fixture()
        reshape_columns_and_rehash_original_receipt(item, ["일자", "외국인"])
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError,
            "ORIGINAL_CSV_INVESTOR_BUCKET_SCHEMA_DRIFT"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_pension_component_omission_is_not_full_investor_panel(self):
        item = fixture()
        all_columns = item["acquisition_receipt"]["response_columns"]
        reshape_columns_and_rehash_original_receipt(
            item, [name for name in all_columns if name != "연기금 등"]
        )
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError,
            "ORIGINAL_CSV_INVESTOR_BUCKET_SCHEMA_DRIFT"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_header_alias_cannot_replace_original_investor_category(self):
        item = fixture()
        raw = item["original_raw_bytes"].decode("euc_kr")
        self.assertIn("연기금 등", raw)
        retarget_original_bytes(item, raw.replace(
            "연기금 등", "기관계", 1
        ).encode("euc_kr"))
        rec = item["acquisition_receipt"]
        rec["response_columns"] = [
            "기관계" if x == "연기금 등" else x for x in rec["response_columns"]
        ]
        rec["receipt_fingerprint_sha256"] = _sha({
            k: rec[k] for k in RECEIPT_BODY
        })
        item["completion"]["receipt_fingerprint_sha256"] = (
            rec["receipt_fingerprint_sha256"]
        )
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError,
            "ORIGINAL_CSV_INVESTOR_BUCKET_SCHEMA_DRIFT"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_valid_original_categories_can_arrive_in_different_column_order(self):
        item = fixture()
        cols = item["acquisition_receipt"]["response_columns"]
        reshape_columns_and_rehash_original_receipt(
            item, [cols[1], cols[0]] + cols[2:]
        )
        evidence = verify_krx_2022_private_flow_triple(**item)
        self.assertTrue(evidence["archived_csv_investor_bucket_schema_cross_checked"])
        self.assertFalse(evidence["parsed_payload_digest_independently_recomputed"])
        self.assertFalse(evidence["source_admitted"])

    def test_self_consistent_raw_sha_does_not_admit_non_csv_bytes(self):
        item = fixture()
        retarget_original_bytes(item, b"these-are-not-even-CSV-fields")
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ORIGINAL_CSV_HEADER"):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_raw_header_cannot_invent_a_different_source_schema(self):
        item = fixture()
        old = item["original_raw_bytes"].decode("euc_kr")
        changed = old.replace("일자,", "항목,", 1).encode("euc_kr")
        retarget_original_bytes(item, changed)
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ORIGINAL_CSV_HEADER_RECEIPT_DRIFT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_raw_source_can_not_hide_missing_rows(self):
        item = fixture()
        old = item["original_raw_bytes"].decode("euc_kr")
        parts = old.splitlines(keepends=True)
        retarget_original_bytes(item, "".join(parts[:-1]).encode("euc_kr"))
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ORIGINAL_CSV_ROW_COUNT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_rehashed_raw_with_extra_csv_column_rejected(self):
        item = fixture()
        old = item["original_raw_bytes"].decode("euc_kr")
        parts = old.splitlines(keepends=True)
        parts[1] = parts[1].rstrip("\\r\\n") + ",999\\r\\n"
        retarget_original_bytes(item, "".join(parts).encode("euc_kr"))
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ORIGINAL_CSV_ROW_WIDTH_DRIFT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_wrong_2022_source_receipt_client_revision_rejected(self):
        item = fixture()
        r = item["acquisition_receipt"]
        r["client_revision"] = ORIGINAL_CLIENT_REVISION  # Missing original prefix
        r["receipt_fingerprint_sha256"] = _sha({k: r[k] for k in RECEIPT_BODY})
        item["completion"]["receipt_fingerprint_sha256"] = r["receipt_fingerprint_sha256"]
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "CLIENT_REVISION_DRIFT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_unpinned_extra_payer_or_source_param_rejected(self):
        item = fixture()
        item["canonical_request"]["params"]["unapproved_investor_mode"] = "all"
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "SOURCE_RESOLVED_PARAMS_DRIFT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_invalid_euc_kr_bytes_rejected_even_if_sha_matches(self):
        item = fixture()
        retarget_original_bytes(item, bytes([0xff, 0xfe, 0xfd, 0]))
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ORIGINAL_EUCKR_CSV_INVALID"):
            verify_krx_2022_private_flow_triple(**item)

    def test_exact_row_count_and_byte_hash_do_not_allow_duplicate_observation_day(self):
        item = fixture()
        raw = item["original_raw_bytes"].decode("euc_kr")
        lines = raw.splitlines(keepends=True)
        # Keep 250 rows and all archived SHA fields internally consistent.
        lines[2] = lines[1]
        retarget_original_bytes(item, "".join(lines).encode("euc_kr"))
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError, "ORIGINAL_CSV_DUPLICATE_OBSERVATION_DATE"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_mismatched_historical_year_not_disguised_by_header_and_row_count(self):
        item = fixture()
        replace_date_in_first_csv_row(item, "2026-10-04")
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError, "ORIGINAL_CSV_DATE_OUTSIDE_2022_TASK_WINDOW"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_day_outside_frozen_window_but_inside_2022_is_rejected(self):
        item = fixture()
        replace_date_in_first_csv_row(item, "2022-01-01")
        # 2022-01-01 is outside this synthetic task's Jan-03 -> Dec-30 span.
        with self.assertRaisesRegex(
            KRXPrivateFlowTripleError, "ORIGINAL_CSV_DATE_OUTSIDE_2022_TASK_WINDOW"
        ):
            verify_krx_2022_private_flow_triple(**item)

    def test_unparseable_original_csv_date_rejected(self):
        item = fixture()
        replace_date_in_first_csv_row(item, "Oct. 04, 2022")
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ORIGINAL_CSV_DATE_FORMAT_DRIFT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_nonexistent_2022_calendar_date_rejected(self):
        item = fixture()
        replace_date_in_first_csv_row(item, "2022-02-30")
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ORIGINAL_CSV_DATE_INVALID"):
            verify_krx_2022_private_flow_triple(**item)

    def test_accept_yyyy_mm_dd_slash_date_spelling_without_pit_promotion(self):
        item = fixture()
        replace_date_in_first_csv_row(item, "2022/01/03")
        result = verify_krx_2022_private_flow_triple(**item)
        self.assertTrue(result["archived_csv_observed_dates_in_2022_task_window_checked"])
        self.assertFalse(result["source_admitted"])

    def test_accept_yyyymmdd_date_spelling_without_pit_promotion(self):
        item = fixture()
        replace_date_in_first_csv_row(item, "20220103")
        result = verify_krx_2022_private_flow_triple(**item)
        self.assertFalse(result["provider_authenticity_independently_verified"])

    def test_allow_yyyy_mm_dd_dotted_original_csv_date(self):
        item = fixture()
        replace_date_in_first_csv_row(item, "2022.01.03")
        result = verify_krx_2022_private_flow_triple(**item)
        self.assertTrue(result["archived_csv_observed_dates_in_2022_task_window_checked"])
        self.assertFalse(result["source_admitted"])

    def test_reject_ambiguous_mixed_calendar_date_separators(self):
        item = fixture()
        replace_date_in_first_csv_row(item, "2022/01-03")
        with self.assertRaisesRegex(KRXPrivateFlowTripleError, "ORIGINAL_CSV_DATE_FORMAT_DRIFT"):
            verify_krx_2022_private_flow_triple(**item)

    def test_unverified_calendar_weekdays_are_not_promoted_to_market_open(self):
        item = fixture()
        # Source task 2022-01-03 -> 2022-12-30; Saturday Jan 08 is inside
        # this date interval but needs independent official market calendar.
        replace_date_in_first_csv_row(item, "2022-01-08")
        result = verify_krx_2022_private_flow_triple(**item)
        self.assertFalse(result["full_historical_universe_verified"])
        self.assertFalse(result["original_2022_as_published_vintage_verified"])

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
        header_only = io.StringIO(newline="")
        csv.writer(header_only).writerow(item["acquisition_receipt"]["response_columns"])
        retarget_original_bytes(item, header_only.getvalue().encode("euc_kr"))
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
