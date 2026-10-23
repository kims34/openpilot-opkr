"""Read-only replay of a previously GitHub-sealed four-source M20 count capsule.

Requires the separately verified GitHub Actions ZIP artifact 12138239045
from run 39132675511 at SHA faa68ad257fff1eff697e78653e1e369db3453f3.
This script does NOT download it or contact OpenDART/market/broker. It only
validates extracted count JSONs, SHA256 checksums, and the already pinned
original source manifest after the original seven-day artifacts expire.

Replay is NOT renewed original filing verification, CFS facts or financial PIT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from research_v1_m20_original_source_evidence_gate import (
    EXPECTED, EvidenceGap, PUB_SAFE_ERROR, _read,
    validate_contract, validate_source_counts,
)

ARCHIVE_RUN = 39132675511
ARCHIVE_HEAD_SHA = "faa68ad257fff1eff697e78653e1e369db3453f3"
ARCHIVE_ARTIFACT_ID = 12138239045
ARCHIVE_ZIP_DIGEST = "sha256:c9465d204b6a5c0b109807b06c352e46e12a50d8d717e953bd06ab3e9176036b"
OUT = Path("research_results/m20_source_replay_verdict/verdict.json")
CAPSULE_KEYS = frozenset({
    "kind", "source_kind", "source_manifest_sha256",
    "source_count_files_sha256", "source_gate_verdict_sha256",
    "original_cfs_profit_cells_verified", "first_publication_instant_verified",
    "m20_feature_pit_admitted", "m20_performance_run_authorized",
    "real_orders_authorized", "ordering",
})
CAPSULE_KIND = "READ_ONLY_REPLAY_FOUR_FIRST_RECEIPT_COUNTS_NOT_PIT"
SOURCE_KIND = "PREVIOUSLY_VERIFIED_EXACT_GITHUB_RUNS"


def _digest(path: Path) -> str:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 32768:
        raise EvidenceGap("REPLAY_SOURCE_SIZE_OR_SYMLINK_INVALID")
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _checked_checksum(field: str, path: Path, expected: str) -> None:
    if type(expected) is not str or len(expected) != 71 or not expected.startswith("sha256:"):
        raise EvidenceGap("REPLAY_CHECKSUM_INVALID")
    if _digest(path) != expected:
        raise EvidenceGap("REPLAY_CHECKSUM_MISMATCH")


def _sealed_file(root: Path, relative: Path) -> Path:
    """Refuse aliases anywhere below the extracted, pinned archive root.

    The final JSON file's own is_symlink check in _digest is insufficient
    when an *intermediate directory* resolves outside the capsule root.
    """
    if relative.is_absolute() or not relative.parts or any(
        part in ("..", ".") for part in relative.parts
    ):
        raise EvidenceGap("REPLAY_RELATIVE_PATH_INVALID")
    current = root
    for index, component in enumerate(relative.parts):
        current = current / component
        if current.is_symlink():
            raise EvidenceGap("REPLAY_CAPSULE_PATH_SYMLINK")
        if index < len(relative.parts) - 1 and not current.is_dir():
            raise EvidenceGap("REPLAY_CAPSULE_PARENT_INVALID")
    if not current.is_file():
        raise EvidenceGap("REPLAY_SOURCE_SIZE_OR_SYMLINK_INVALID")
    return current


def replay(root: Path, output: Path) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise EvidenceGap("REPLAY_CAPSULE_ROOT_INVALID")
    manifest_path = _sealed_file(root, Path("INDEXALERT_M20_2022_Q3_VERIFIED_SOURCE_ARTIFACT_MANIFEST.json"))
    source_dir = Path("research_results/m20_original_gated_inputs")
    verdict_path = _sealed_file(root, Path("research_results/opendart_m20_original_evidence_gate/verdict.json"))
    checksum_path = _sealed_file(root, Path("research_results/m20_original_source_capsule/checksums.json"))
    capsule = _read(checksum_path, 16384)
    if set(capsule) != CAPSULE_KEYS or (
        capsule.get("kind") != CAPSULE_KIND or capsule.get("source_kind") != SOURCE_KIND
        or capsule.get("ordering") != "DISABLED"
    ):
        raise EvidenceGap("REPLAY_CAPSULE_TYPE_OR_SCOPE_MISMATCH")
    for field in (
        "original_cfs_profit_cells_verified",
        "first_publication_instant_verified",
        "m20_feature_pit_admitted",
        "m20_performance_run_authorized",
        "real_orders_authorized",
    ):
        if capsule.get(field) is not False:
            raise EvidenceGap("REPLAY_UNAUTHORIZED_FINANCIAL_PIT_OR_ORDERS")
    manifest = _read(manifest_path, 16384)
    validate_contract(manifest)
    _checked_checksum("manifest", manifest_path, capsule["source_manifest_sha256"])
    pins = capsule.get("source_count_files_sha256")
    if type(pins) is not dict or set(pins) != set(EXPECTED):
        raise EvidenceGap("REPLAY_FOUR_PINNED_SOURCE_COUNTS_MISSING")
    records = {}
    for key in EXPECTED:
        path = _sealed_file(root, source_dir / key / "counts.json")
        records[key] = _read(path, 16384)
        _checked_checksum(key, path, pins[key])
    recomputed = validate_source_counts(records)
    sealed_verdict = _read(verdict_path, 16384)
    if sealed_verdict != recomputed:
        raise EvidenceGap("REPLAY_PREVIOUS_VERDICT_DRIFT")
    _checked_checksum("verdict", verdict_path, capsule["source_gate_verdict_sha256"])
    if (recomputed["actual_original_cfs_operating_profit_cell_period_lineage_verified"] is not False
            or recomputed["historical_first_publication_instant_verified"] is not False
            or recomputed["frozen_strategy_source_data_admitted"] is not False
            or recomputed["m20_performance_run_authorized"] is not False
            or recomputed["real_orders_authorized"] is not False
            or recomputed["ordering"] != "DISABLED"):
        raise EvidenceGap("REPLAY_MANDATORY_PIT_NO_GO_NOT_MET")
    result = {
        "purpose": "FOUR_PREVIOUSLY_VERIFIED_FIRST_FILING_SOURCE_COUNTS_ARCHIVE_REPLAY",
        "status": "FOUR_SEALED_SOURCE_COUNTS_REPLAY_CONSISTENT_NOT_NEW_OFFICIAL_SOURCE",
        "original_official_run_count_in_archive": len(EXPECTED),
        "original_viewer_table_tags": recomputed["financial_viewer_table_tags"],
        "original_operating_label_candidates": recomputed["first_original_operating_label_table_candidates"],
        "original_2022_q3_cfs_fact_verified": False,
        "original_2021_q3_cfs_fact_verified": False,
        "historical_first_publication_instant_verified": False,
        "source_replay_is_new_official_dart_result": False,
        "m20_feature_pit_admitted": False,
        "m20_performance_run_authorized": False,
        "independent_holdout_authorized": False,
        "champion_change_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permissions_change_authorized": False,
        "ordering": "DISABLED",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print("M20_SEALED_CAPSULE_REPLAY=" + json.dumps(result, sort_keys=True), flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--capsule-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUT)
    params=parser.parse_args()
    try:
        replay(params.capsule_root, params.output)
    except (EvidenceGap, KeyError, ValueError, TypeError, OSError, UnicodeError):
        raise SystemExit(PUB_SAFE_ERROR) from None


if __name__ == "__main__":
    main()
