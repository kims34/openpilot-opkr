"""Offline CLI for assessing genuine LIVE execution evidence against frozen v1.

This command performs no broker/network action and cannot create evidence. It
only reads an existing CSV, binds the exact input bytes by SHA-256, validates the
frozen protocol/document pair and writes the evaluator result. Passing never
independently authorizes holdout, promotion or live trading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

import pandas as pd

from research_v1_execution_sufficiency_assessment import (
    assess_execution_sufficiency,
    load_frozen_project_protocol,
)


def assess_execution_sufficiency_file(
    input_csv: str | Path,
    *,
    output_json: str | Path | None = None,
    protocol_dir: str | Path = ".",
) -> dict:
    source = Path(input_csv)
    if not source.is_file():
        raise FileNotFoundError(f"execution evidence CSV not found: {source}")
    raw = source.read_bytes()
    if not raw:
        raise ValueError("execution evidence CSV is empty")

    table = pd.read_csv(source)
    protocol, document = load_frozen_project_protocol(protocol_dir)
    result = assess_execution_sufficiency(
        table,
        protocol,
        protocol_document_text=document,
    )
    result = {
        "evidence_file_name": source.name,
        "evidence_file_sha256": hashlib.sha256(raw).hexdigest(),
        "evidence_rows_read": int(len(table)),
        **result,
    }

    if output_json is not None:
        destination = Path(output_json)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assess existing genuine LIVE execution CSV against the frozen IndexAlert v1 protocol."
    )
    parser.add_argument("--input", required=True, help="existing execution-evidence CSV")
    parser.add_argument("--output", help="optional result JSON path; otherwise print JSON")
    parser.add_argument(
        "--protocol-dir",
        default=".",
        help="directory containing the frozen protocol .md and .json files",
    )
    args = parser.parse_args(argv)

    result = assess_execution_sufficiency_file(
        args.input,
        output_json=args.output,
        protocol_dir=args.protocol_dir,
    )
    if args.output is None:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
