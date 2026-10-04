"""Offline-only runner for aggregate KRX affected-position scope evidence.

Inputs are local/private files only. The command emits aggregate counts and
fingerprints; it never emits symbols, raw status rows, or position identifiers.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from research_v1_krx_affected_position_scope import (
    build_affected_position_scope,
    public_affected_scope_summary,
)


def run(*, positions_path: str, status_events_path: str, source_contract_fingerprint: str) -> dict:
    pp = Path(positions_path)
    sp = Path(status_events_path)
    if not pp.is_file() or not sp.is_file():
        raise FileNotFoundError("private positions/status-event input file is missing")
    if pp.suffix.lower() != ".csv" or sp.suffix.lower() != ".csv":
        raise ValueError("offline affected-scope runner accepts local CSV inputs only")

    positions = pd.read_csv(pp)
    events = pd.read_csv(sp)
    scope = build_affected_position_scope(
        positions=positions,
        status_events=events,
        source_contract_fingerprint=source_contract_fingerprint,
    )
    out = public_affected_scope_summary(scope)
    out.update({
        "mode": "OFFLINE_AFFECTED_POSITION_SCOPE",
        "network_request_attempted": False,
        "raw_rows_emitted": False,
        "position_identifiers_emitted": False,
        "security_identifiers_emitted": False,
    })
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--positions", required=True)
    p.add_argument("--status-events", required=True)
    p.add_argument("--source-contract-fingerprint", required=True)
    args = p.parse_args()
    print(json.dumps(run(
        positions_path=args.positions,
        status_events_path=args.status_events,
        source_contract_fingerprint=args.source_contract_fingerprint,
    ), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
