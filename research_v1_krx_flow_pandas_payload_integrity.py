"""Recompute the ORIGINAL KRX worker pandas receipt digests from raw CSV.

Strictly network-free and file-I/O-free: takes original raw bytes and immutable
acquisition receipt objects supplied inside the already-protected KRX owner
environment. It does NOT authenticate that supplied bytes came from KRX or
were originally published/available during 2022.

The original 2026-10-03 worker used:
  pandas==2.3.3, numpy==2.5.3 (requirements-krx-historical-worker.txt)
  pd.read_csv(BytesIO(raw), encoding="EUC-KR")
  schema_fingerprint(response_frame.columns, response_frame.dtypes)
  pd.util.hash_pandas_object(frame, index=True).astype("uint64").tolist()
Those exact same functions and canonical SHA construction are mirrored here.
No raw rows, issuer symbols, task IDs or row hashes are returned.
"""
from __future__ import annotations

import csv
import hashlib
from io import BytesIO, StringIO
import json
import re
from typing import Any, Mapping

from research_v1_krx_flow_private_triple_proof import (
    verify_krx_2022_private_flow_triple,
)
from research_v1_krx_flow_2022_receipt_gate import INSTITUTION_COMPONENTS

PINNED_PANDAS_VERSION = "2.3.3"
PINNED_NUMPY_VERSION = "2.5.3"
# Syntax-only; 2022 KRX amounts and KRW scaling are NOT inferred.
# Accept plain signed values, canonical 3-digit thousands grouping, and an
# optional decimal portion. Blank, placeholders, scientific notation,
# malformed commas and non-finite labels are NOT valid numeric observations.
_SOURCE_AMOUNT = re.compile(
    r"[+-]?(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)(?:[.][0-9]+)?"
)
_REQUIRED_FLOW_BUCKETS = ("외국인", *INSTITUTION_COMPONENTS)


def _verify_required_investor_amount_cell_format(raw: bytes) -> None:
    """Fail closed on opaque original financial cells, not on unknown units.

    Parsed frame SHA can faithfully preserve arbitrary text: that alone does
    NOT establish numeric foreign/institution net-buy data. Check EVERY 2022
    row of all 8 required individual investor buckets against a conservative
    finite displayed-number grammar. Do not normalize units, infer signs,
    aggregate institutions, expose any amount or promote source/PIT.
    """
    try:
        reader = csv.reader(
            StringIO(raw.decode("euc_kr", errors="strict"), newline=""),
            strict=True,
        )
        header = next(reader)
        indexes = [header.index(name) for name in _REQUIRED_FLOW_BUCKETS]
        for row in reader:
            if not row:
                continue
            if len(row) != len(header):
                raise KRXInvestorFlowPandasDigestError(
                    "ORIGINAL_INVESTOR_AMOUNT_CSV_WIDTH_DRIFT"
                )
            for index in indexes:
                value = row[index].strip()
                _need(_SOURCE_AMOUNT.fullmatch(value) is not None,
                      "ORIGINAL_INVESTOR_AMOUNT_NOT_FINITE_NUMERIC_FORMAT")
    except KRXInvestorFlowPandasDigestError:
        # Keep the distinct fail-closed invalid-amount reason. This class
        # subclasses ValueError, which would otherwise be accidentally
        # rewritten as a structural CSV decoding failure.
        raise
    except (UnicodeError, csv.Error, StopIteration, ValueError):
        raise KRXInvestorFlowPandasDigestError(
            "ORIGINAL_INVESTOR_AMOUNT_CSV_PARSE_FAILED"
        ) from None



class KRXInvestorFlowPandasDigestError(ValueError):
    """Only fixed error codes, never private original/source material."""


def _need(yes: bool, code: str) -> None:
    if not yes:
        raise KRXInvestorFlowPandasDigestError(code)


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), default=str,
        ).encode("utf-8")
    ).hexdigest()


def verify_2022_krx_flow_pandas_payload(
    *,
    original_raw_bytes: bytes,
    acquisition_receipt: Mapping[str, Any],
    completion: Mapping[str, Any],
    canonical_request: Mapping[str, Any],
    frozen_task: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify **two independent pandas digests** after original SHA/CSV gate.

    Does not change, promote or bypass any existing source/PIT/economics flag.
    """
    prior = verify_krx_2022_private_flow_triple(
        original_raw_bytes=original_raw_bytes,
        acquisition_receipt=acquisition_receipt,
        completion=completion,
        canonical_request=canonical_request,
        frozen_task=frozen_task,
    )
    try:
        import numpy as np
        import pandas as pd
    except ImportError:
        raise KRXInvestorFlowPandasDigestError(
            "PINNED_PANDAS_NUMPY_UNAVAILABLE"
        ) from None

    _need(pd.__version__ == PINNED_PANDAS_VERSION,
          "ORIGINAL_PANDAS_VERSION_DRIFT")
    _need(np.__version__ == PINNED_NUMPY_VERSION,
          "ORIGINAL_NUMPY_VERSION_DRIFT")
    try:
        frame = pd.read_csv(BytesIO(original_raw_bytes), encoding="EUC-KR")
    except Exception:
        raise KRXInvestorFlowPandasDigestError(
            "ORIGINAL_PANDAS_PARSE_FAILURE"
        ) from None

    column_names = [str(c) for c in frame.columns]
    dtype_names = [str(t) for t in frame.dtypes]
    _need(not frame.columns.duplicated().any(),
          "ORIGINAL_PANDAS_DUPLICATE_COLUMNS")
    _need(column_names == acquisition_receipt["response_columns"]
          and len(frame) == acquisition_receipt["response_rows"],
          "ORIGINAL_PANDAS_SHAPE_DISAGREES_WITH_RECEIPT")

    schema_fingerprint = _sha([
        {"name": col, "dtype": dtype}
        for col, dtype in zip(column_names, dtype_names)
    ])
    _need(
        schema_fingerprint == acquisition_receipt["response_schema_sha256"],
        "ORIGINAL_PANDAS_SCHEMA_SHA_MISMATCH",
    )
    try:
        row_hashes = (
            pd.util.hash_pandas_object(frame, index=True)
            .astype("uint64").tolist()
        )
        fingerprint = _sha({
            "columns": column_names,
            "dtypes": dtype_names,
            "rows": int(len(frame)),
            "row_hashes": [int(value) for value in row_hashes],
        })
    except Exception:
        raise KRXInvestorFlowPandasDigestError(
            "ORIGINAL_PANDAS_CONTENT_HASH_ERROR"
        ) from None
    _need(
        fingerprint == acquisition_receipt["response_payload_sha256"],
        "ORIGINAL_PANDAS_PAYLOAD_SHA_MISMATCH",
    )
    # A fully matching historical pandas content digest can still cover
    # arbitrary strings. Before deeming a 2022 request a usable numeric
    # *candidate*, reject malformed foreign/institution cells. The source
    # response is not thereby admitted as authentic, PIT or KRW-scaled.
    _verify_required_investor_amount_cell_format(original_raw_bytes)
    return {
        **prior,
        "checked_type": "KRX_INVESTOR_FLOW_2022_ORIGINAL_PANDAS_DIGEST",
        "original_pandas_version_exactly_matched": True,
        "original_numpy_version_exactly_matched": True,
        "original_pandas_schema_sha_independently_recomputed": True,
        "parsed_payload_digest_independently_recomputed": True,
        "original_pandas_payload_sha_matches_archived_receipt": True,
        # Header-only CSV cannot establish ANY actual numeric observation.\n        "original_2022_foreign_institution_amount_display_format_checked": (\n            prior["has_nonempty_source_response"]\n        ),
        "original_2022_net_buy_amount_unit_or_scale_verified": False,
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
        "source_numeric_rows_or_identifiers_emitted": False,
    }
