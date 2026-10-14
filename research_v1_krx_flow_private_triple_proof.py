"""Pure in-memory integrity check for historical KRX investor-flow source triples.

Input must come from the already-approved private KRX volume/session.
Never writes files, touches environment, requests KRX, accesses broker or logs
numeric data. Matching a 2026-retrieved 2022 response is NOT 2022-vintage PIT.
"""
from __future__ import annotations

from datetime import datetime
import csv
import hashlib
import io
import json
import re
from typing import Any, Mapping

SHA = re.compile(r"^[0-9a-f]{64}$")
DAY = re.compile(r"^[0-9]{8}$")
SOURCE_DAY = re.compile(r"^(?:[0-9]{8}|[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{4}/[0-9]{2}/[0-9]{2}|[0-9]{4}[.][0-9]{2}[.][0-9]{2})$")
ORIGINAL_CLIENT_REVISION = "e6ebac9b71482db127348d8a08ebc6743aa3b50e"
FROZEN_BLD = "dbms/MDC/STAT/standard/MDCSTAT02303"
ORIGINAL_RECEIPT_CLIENT_REVISION = "krx-data-api@" + ORIGINAL_CLIENT_REVISION
# Original pinned third-party endpoint defaults, not user-adjustable mode knobs.
PINNED_PARAMS = {
    "inqTpCd": "2", "trdVolVal": "2", "askBid": "3",
    "detailView": "1", "tboxisuCd_finder_stkisu0_0": "",
    "isuCd2": "", "codeNmisuCd_finder_stkisu0_0": "",
    "param1isuCd_finder_stkisu0_0": "ALL",
    "money": "1", "csvxls_isNo": "false",
}
RECEIPT_BODY = (
    "receipt_version", "source_family", "intended_use_scope",
    "access_route", "dataset_identifier",
    "authorization_evidence_reference",
    "authorization_evidence_fingerprint_sha256", "client_revision",
    "retrieved_at", "request_metadata_sha256", "response_schema_sha256",
    "response_payload_sha256", "response_rows", "response_columns",
    "public_contract_evidence_version",
    "public_contract_evidence_fingerprint_sha256",
    "alpha_or_final_judge_promotion_authorized",
    "sealed_holdout_authorized", "live_trading_authorized",
)


class KRXPrivateFlowTripleError(ValueError):
    pass


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise KRXPrivateFlowTripleError(code)


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False,
                   separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def _valid_sha(value: Any) -> bool:
    return type(value) is str and SHA.fullmatch(value) is not None


def _verified_2022_date(d: Any) -> datetime:
    _require(type(d) is str and DAY.fullmatch(d) is not None,
             "HISTORIC_DATE_FORMAT_DRIFT")
    try:
        parsed = datetime.strptime(d, "%Y%m%d")
    except ValueError:
        raise KRXPrivateFlowTripleError("HISTORIC_DATE_INVALID") from None
    _require(parsed.year == 2022, "HISTORIC_YEAR_NOT_2022")
    return parsed


def _source_csv_day(text: Any) -> datetime:
    """Accept explicit common KRX raw date spellings, never time-travel.

    Source date semantics are a consistency guard, not original publication
    vintage, official trading calendar or a guarantee of first-available time.
    """
    _require(type(text) is str, "ORIGINAL_CSV_DATE_TYPE_DRIFT")
    normalized = text.strip()
    _require(SOURCE_DAY.fullmatch(normalized) is not None,
             "ORIGINAL_CSV_DATE_FORMAT_DRIFT")
    digits = normalized.replace("-", "").replace("/", "").replace(".", "")
    try:
        return datetime(int(digits[:4]), int(digits[4:6]), int(digits[6:8]))
    except ValueError:
        raise KRXPrivateFlowTripleError("ORIGINAL_CSV_DATE_INVALID") from None


def verify_krx_2022_private_flow_triple(
    *,
    original_raw_bytes: bytes,
    acquisition_receipt: Mapping[str, Any],
    completion: Mapping[str, Any],
    canonical_request: Mapping[str, Any],
    frozen_task: Mapping[str, Any],
) -> dict[str, Any]:
    """Cross-bind exact bytes, receipt, resolved request and frozen task.

    A byte hash proves ONLY equality to the archived digest; it does not
    prove the raw provider was authentic or available during 2022.
    The parsed dataframe payload fingerprint is NOT recomputed here.
    """
    _require(type(original_raw_bytes) is bytes,
             "RAW_SOURCE_BYTES_REQUIRED")
    _require(isinstance(acquisition_receipt, Mapping)
             and isinstance(completion, Mapping)
             and isinstance(canonical_request, Mapping)
             and isinstance(frozen_task, Mapping),
             "PRIVATE_RECEIPT_RECORDS_REQUIRED")
    _require(frozen_task.get("phase") == "PER_SECURITY_HISTORY"
             and frozen_task.get("source_family") == "KRX_INVESTOR_FLOW",
             "FROZEN_TASK_FAMILY_DRIFT")
    spec = frozen_task.get("request_spec")
    _require(isinstance(spec, Mapping)
             and spec.get("kind") == "investor_trading_individual_daily"
             and isinstance(spec.get("params"), Mapping),
             "FROZEN_TASK_SPEC_DRIFT")
    task_params = spec["params"]
    _require(set(task_params) == {"isuCd", "strtDd", "endDd"},
             "FROZEN_FLOW_TASK_PARAMS_DRIFT")
    start = _verified_2022_date(task_params.get("strtDd"))
    end = _verified_2022_date(task_params.get("endDd"))
    _require(start <= end, "FROZEN_FLOW_WINDOW_REVERSED")
    _require(type(task_params.get("isuCd")) is str
             and re.fullmatch(r"[0-9A-Z]{12}", task_params["isuCd"]) is not None,
             "FROZEN_HISTORIC_ISSUE_FORMAT_DRIFT")
    task_id = frozen_task.get("task_id")
    _require(_valid_sha(task_id)
             and task_id == _sha({k: v for k, v in frozen_task.items()
                                  if k != "task_id"}),
             "FROZEN_TASK_FINGERPRINT_DRIFT")

    _require(set(canonical_request) == {
        "bld", "method", "menu_id", "params", "pinned_client_commit"
    }, "PINNED_SOURCE_REQUEST_KEYS_DRIFT")
    _require(canonical_request["bld"] == FROZEN_BLD
             and canonical_request["method"] == "csv"
             and canonical_request["menu_id"] == "MDC0201020302"
             and canonical_request["pinned_client_commit"] == ORIGINAL_CLIENT_REVISION,
             "SOURCE_ROUTE_PIN_DRIFT")
    params = canonical_request["params"]
    _require(isinstance(params, Mapping), "PINNED_SOURCE_PARAMS_MISSING")
    _require(all(params.get(k) == value for k, value in {
        "inqTpCd": "2", "trdVolVal": "2", "askBid": "3",
        "detailView": "1", "money": "1",
    }.items()), "NET_BUY_VALUE_REQUEST_MODE_DRIFT")
    _require(all(params.get(k) == task_params[k]
                 for k in ("isuCd", "strtDd", "endDd")),
             "REQUEST_TO_FROZEN_TASK_DRIFT")
    expected_params = {**PINNED_PARAMS, **dict(task_params)}
    _require(set(params) == set(expected_params)
             and all(params[k] == v for k, v in expected_params.items()),
             "SOURCE_RESOLVED_PARAMS_DRIFT")

    r = acquisition_receipt
    _require(all(k in r for k in RECEIPT_BODY)
             and _valid_sha(r.get("receipt_fingerprint_sha256")),
             "RECEIPT_FIELDS_OR_FINGERPRINT_MISSING")
    body = {k: r[k] for k in RECEIPT_BODY}
    _require(_sha(body) == r["receipt_fingerprint_sha256"],
             "RECEIPT_BODY_TAMPERED")
    _require(r.get("source_family") == "KRX_INVESTOR_FLOW"
             and r.get("access_route")
                 == "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION"
             and r.get("dataset_identifier") == "MDCSTAT02303",
             "RECEIPT_SOURCE_ROUTE_DRIFT")
    _require(r.get("client_revision") == ORIGINAL_RECEIPT_CLIENT_REVISION,
             "ORIGINAL_RECEIPT_CLIENT_REVISION_DRIFT")
    _require(_sha(dict(canonical_request)) == r["request_metadata_sha256"],
             "RECEIPT_TO_ACTUAL_REQUEST_DRIFT")
    _require(type(r.get("response_rows")) is int
             and r["response_rows"] >= 0
             and type(r.get("response_columns")) is list
             and all(type(c) is str for c in r["response_columns"]),
             "RECEIPT_RESPONSE_SHAPE_DRIFT")
    for k in ("response_schema_sha256", "response_payload_sha256"):
        _require(_valid_sha(r.get(k)), "RECEIPT_DATASET_DIGEST_MISSING")
    timestamp = r.get("retrieved_at")
    _require(type(timestamp) is str, "RECEIPT_CAPTURE_TIME_MISSING")
    try:
        captured = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise KRXPrivateFlowTripleError("RECEIPT_CAPTURE_TIME_INVALID") from None
    _require(captured.tzinfo is not None
             and captured.utcoffset() is not None,
             "RECEIPT_CAPTURE_TIME_NOT_AWARE")
    _require(captured.date() >= end.date(), "RETRIEVED_BEFORE_HISTORIC_END")
    _require(all(r.get(flag) is False for flag in (
        "alpha_or_final_judge_promotion_authorized",
        "sealed_holdout_authorized", "live_trading_authorized",
    )), "RECEIPT_ESCALATED_AUTHORITY")

    _require(completion.get("task_id") == task_id,
             "COMPLETED_TASK_ID_DRIFT")
    raw_sha = hashlib.sha256(original_raw_bytes).hexdigest()
    _require(raw_sha == completion.get("raw_object_sha256")
             and len(original_raw_bytes) == completion.get("raw_bytes_size"),
             "ORIGINAL_RAW_OBJECT_BYTE_SHA_DRIFT")
    for key in ("request_metadata_sha256", "response_schema_sha256",
                "response_payload_sha256", "receipt_fingerprint_sha256"):
        _require(completion.get(key) == r.get(key),
                 "RECEIPT_COMPLETION_DIGEST_DRIFT")
    _require(completion.get("response_rows") == r["response_rows"],
             "RECEIPT_COMPLETION_ROW_COUNT_DRIFT")

    # The historical KRX worker used pandas.read_csv(..., encoding="EUC-KR").
    # First cross-check the immutable original raw CSV against the declared
    # receipt shape with standard-library parsing. This is deliberately NOT
    # a replacement for the pandas-content payload SHA (dtype semantics can
    # differ) and does not establish units or the provider's publication time.
    try:
        decoded = original_raw_bytes.decode("euc_kr", errors="strict")
        stream = csv.reader(io.StringIO(decoded, newline=""), strict=True)
        columns = next(stream)
        _require(bool(columns) and all(bool(v) for v in columns)
                 and len(columns) == len(set(columns)),
                 "ORIGINAL_CSV_HEADER_INVALID")
        _require(columns == r["response_columns"],
                 "ORIGINAL_CSV_HEADER_RECEIPT_DRIFT")
        _require("일자" in columns, "ORIGINAL_CSV_DATE_COLUMN_MISSING")
        date_index = columns.index("일자")
        observed_dates: set[datetime] = set()
        csv_rows = 0
        for row in stream:
            if not row:  # Match pandas.read_csv(skip_blank_lines=True).
                continue
            _require(len(row) == len(columns), "ORIGINAL_CSV_ROW_WIDTH_DRIFT")
            observed_day = _source_csv_day(row[date_index])
            _require(start <= observed_day <= end,
                     "ORIGINAL_CSV_DATE_OUTSIDE_2022_TASK_WINDOW")
            _require(observed_day not in observed_dates,
                     "ORIGINAL_CSV_DUPLICATE_OBSERVATION_DATE")
            observed_dates.add(observed_day)
            csv_rows += 1
        _require(csv_rows == r["response_rows"],
                 "ORIGINAL_CSV_ROW_COUNT_RECEIPT_DRIFT")
    except (UnicodeDecodeError, csv.Error, StopIteration):
        raise KRXPrivateFlowTripleError("ORIGINAL_EUCKR_CSV_INVALID") from None

    return {
        "checked_type": "KRX_INVESTOR_FLOW_2022_PRIVATE_ORIGINAL_TRIPLE",
        "exact_raw_object_bytes_match_checkpoint_sha": True,
        "exact_receipt_fingerprint_matches_body": True,
        "exact_original_resolved_request_hash_matches_receipt": True,
        "frozen_task_id_and_window_match_request": True,
        "checked_2022_historical_year": True,
        "has_nonempty_source_response": r["response_rows"] > 0,
        "archived_csv_header_and_row_count_cross_checked": True,
        "archived_csv_observed_dates_in_2022_task_window_checked": True,
        "archived_csv_duplicate_day_rejected": True,
        "source_numeric_rows_or_identifiers_emitted": False,
        "parsed_payload_digest_independently_recomputed": False,
        "provider_authenticity_independently_verified": False,
        "original_2022_as_published_vintage_verified": False,
        "original_2022_historical_publication_instant_verified": False,
        "historical_correction_lineage_verified": False,
        "foreign_institution_value_unit_semantics_verified": False,
        "full_historical_universe_verified": False,
        "source_admitted": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "ordering_enabled": False,
        "network_request_attempted": False,
    }
