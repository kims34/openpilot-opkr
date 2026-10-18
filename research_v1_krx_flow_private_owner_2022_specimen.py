"""Safe, PRE-REGISTERED single 2022 investor-flow source-row specimen audit.

Never fetches historical KRX, resumes workers, redeploys Railway, issues orders,
or exports private raw rows/issuer codes. Owner must independently authorize
use inside the ORIGINAL protected volume; not executable through ChatGPT tools.
Chooses the FIRST 2022 flow task in the ORIGINAL frozen ordered manifest,
after the full original 14,296/11,750 byte/prefix check; no cherry-picking.

Read-only access uses O_NOFOLLOW + dir_fd anchored paths for each artifact.
The result is a safe aggregate/nonadmission report only. One source row bundle
does not establish all issuer data, genuine as-published 2022 PIT, units, trades,
or net profitability.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from research_v1_krx_flow_existing_private_checkpoint_inventory import _sha
from research_v1_krx_flow_private_triple_proof import (
    FROZEN_BLD, ORIGINAL_CLIENT_REVISION, PINNED_PARAMS,
)
from research_v1_krx_flow_frozen_archive_bytes_gate import (
    audit_frozen_2026_10_03_private_krx_flow_snapshot,
)
from research_v1_krx_flow_private_checkpoint_chain import (
    verify_2022_krx_private_full_checkpoint_chain,
)
from research_v1_krx_flow_private_owner_readonly_snapshot import (
    KRXPrivateOwnerReadOnlyError,
    _protected_root,
    _read_exact_private_metadata,
)

FAMILY = "KRX_INVESTOR_FLOW"
DATASET = "MDCSTAT02303"
ACCESS_ROUTE = "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION"
MANIFEST_PATH = ("task_manifests", "per-security-history-v3.json")
STATE_PATH = ("batch_state", "PER_SECURITY_HISTORY.json")


class KRXPrivateOwnerSpecimenError(ValueError):
    """Public-safe static blocker codes only."""


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise KRXPrivateOwnerSpecimenError(code)


def _original_private_json(raw: bytes) -> dict[str, Any]:
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise KRXPrivateOwnerSpecimenError(
            "PRIVATE_ORIGINAL_SNAPSHOT_JSON_INVALID"
        ) from None
    _require(type(obj) is dict, "PRIVATE_ORIGINAL_SNAPSHOT_NOT_OBJECT")
    return obj


def _resolved_request(task: dict[str, Any]) -> dict[str, Any]:
    # Exact five fields passed as request_metadata by the ORIGINAL
    # 2026-10-03 historical request executor.
    return {
        "bld": FROZEN_BLD,
        "method": "csv",
        "menu_id": "MDC0201020302",
        "params": {
            **PINNED_PARAMS,
            **dict(task["request_spec"]["params"]),
        },
        "pinned_client_commit": ORIGINAL_CLIENT_REVISION,
    }


def audit_2022_original_flow_first_specimen(
    *, private_root: str, git_worktree: str,
) -> dict[str, Any]:
    """Read exactly 6 source-owner frozen private files, all without writes.

    1 frozen historical manifest + 1 phase-state snapshot + 4 per-request
    originals (raw object, receipt, manifest, completed checkpoint).
    Only public-safe counts and booleans are returned.
    """
    base = _protected_root(private_root, git_worktree)
    manifest_bytes = _read_exact_private_metadata(base, MANIFEST_PATH)
    phase_bytes = _read_exact_private_metadata(base, STATE_PATH)
    # This rehashes literal frozen manifest bytes and proves the exact original
    # 11,750 completed IDs are a contiguous prefix of its 14,296 tasks.
    snapshot = audit_frozen_2026_10_03_private_krx_flow_snapshot(
        private_manifest_bytes=manifest_bytes,
        private_phase_state_bytes=phase_bytes,
    )
    manifest = _original_private_json(manifest_bytes)
    phase = _original_private_json(phase_bytes)
    selected = next(
        (row for row in manifest["tasks"]
         if row["source_family"] == FAMILY
         and row["request_spec"]["kind"] == "investor_trading_individual_daily"
         and row["request_spec"]["params"]["strtDd"][:4] == "2022"),
        None,
    )
    _require(selected is not None, "ORIGINAL_2022_FLOW_TASK_ABSENT")
    completed = phase["completed"]
    task_id = selected["task_id"]
    _require(task_id in completed, "ORIGINAL_2022_FLOW_TASK_NOT_COMPLETED")
    completion = completed[task_id]
    request = _resolved_request(selected)
    request_sha = _sha(request)
    _require(completion["request_metadata_sha256"] == request_sha,
             "ORIGINAL_2022_FLOW_REQUEST_NOT_CHECKPOINTED")

    receipt_sha = completion["receipt_fingerprint_sha256"]
    raw_sha = completion["raw_object_sha256"]
    _require(len(receipt_sha) == 64 and len(raw_sha) == 64
             and all(x in "0123456789abcdef" for x in receipt_sha + raw_sha),
             "ORIGINAL_2022_FLOW_DIGEST_UNSAFE")
    # These locations are derived ONLY from validated original task/phase
    # SHA values and fixed contract path components. Never trust relative
    # paths read from individual private checkpoint metadata.
    paths = {
        "checkpoint": (
            "checkpoints", FAMILY, ACCESS_ROUTE,
            DATASET, request_sha + ".json",
        ),
        "receipt": ("receipts", FAMILY, DATASET, receipt_sha + ".json"),
        "manifest": (
            "manifests", FAMILY, DATASET,
            request_sha + "-" + receipt_sha + ".json",
        ),
        "raw": ("objects", "sha256", raw_sha[:2], raw_sha + ".bin"),
    }
    checkpoint_bytes = _read_exact_private_metadata(base, paths["checkpoint"])
    receipt_bytes = _read_exact_private_metadata(base, paths["receipt"])
    acquisition_manifest_bytes = _read_exact_private_metadata(base, paths["manifest"])
    raw_bytes = _read_exact_private_metadata(base, paths["raw"])

    proof = verify_2022_krx_private_full_checkpoint_chain(
        original_raw_bytes=raw_bytes,
        acquisition_receipt_bytes=receipt_bytes,
        acquisition_manifest_bytes=acquisition_manifest_bytes,
        request_checkpoint_bytes=checkpoint_bytes,
        canonical_request=request,
        frozen_task=selected,
        phase_completion=completion,
    )
    _require(proof["parsed_payload_digest_independently_recomputed"] is True
             and proof["original_pandas_payload_sha_matches_archived_receipt"] is True
             and proof["original_receipt_file_bytes_sha_matches_manifest"] is True
             and proof["original_manifest_file_bytes_sha_matches_checkpoint"] is True,
             "ORIGINAL_2022_FLOW_SPECIMEN_NOT_VERIFIED")
    return {
        "audit_type": "FROZEN_2026_10_03_FIRST_2022_FLOW_SPECIMEN",
        "source_owner_only_read_only_audit": True,
        "sample_selection": "FIRST_ORIGINAL_ORDERED_2022_FLOW_TASK",
        "original_manifest_byte_sha_matches_public_pin": True,
        "original_completion_prefix_11750_verified": True,
        "investor_flow_completed_request_checkpoints": (
            snapshot["investor_flow_completed_checkpoints"]
        ),
        "year_2022_completed_request_checkpoints": (
            snapshot["year_2022_flow_completed_checkpoints"]
        ),
        "one_original_2022_raw_object_and_checkpoint_chain_checked": True,
        "one_original_2022_pandas_numeric_payload_digest_checked": True,
        "sample_response_nonempty": proof["has_nonempty_source_response"],
        "entire_2022_raw_response_population_verified": False,
        "original_phase_state_snapshot_externally_authenticated": False,
        "original_2022_as_published_vintage_verified": False,
        "historical_release_timestamp_verified": False,
        "historical_correction_lineage_verified": False,
        "official_trading_calendar_and_issuer_universe_verified": False,
        "foreign_institution_unit_semantics_verified": False,
        "source_admitted": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "ordering_enabled": False,
        "network_request_attempted": False,
        "source_numeric_rows_or_identifiers_emitted": False,
    }


def main() -> int:
    try:
        result = audit_2022_original_flow_first_specimen(
            private_root=os.environ.get("KRX_PRIVATE_RAW_DIR", ""),
            git_worktree=str(Path.cwd().resolve()),
        )
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception:
        # No source-private paths, error args, raw rows or issuer/task hashes
        # from any Python exceptions may escape the original owner session.
        print(json.dumps({
            "audit_type": "FROZEN_2026_10_03_FIRST_2022_FLOW_SPECIMEN",
            "status": "BLOCKED",
            "reason_code": "ORIGINAL_PRIVATE_SOURCE_SPECIMEN_UNVERIFIED",
            "source_admitted": False,
            "performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "ordering_enabled": False,
            "network_request_attempted": False,
            "source_numeric_rows_or_identifiers_emitted": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
