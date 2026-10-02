"""Dedicated CLI entrypoint for KRX expected-scope attestation.

Default mode is network-free preflight/plan inspection only.
Network execution requires BOTH:
- --execute
- exact KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT sentinel

Historical Data Marketplace bulk consent never substitutes for this consent.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from research_v1_krx_expected_scope_attestation import public_plan_summary
from research_v1_krx_expected_scope_batch import execute_expected_scope_batch
from research_v1_krx_expected_scope_preflight import evaluate_expected_scope_preflight


class KRXExpectedScopeWorkerError(RuntimeError):
    pass


def run_expected_scope_worker(
    *,
    execute: bool,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    max_new_dates: int | None = None,
    batch_runner: Callable[..., dict[str, Any]] = execute_expected_scope_batch,
) -> dict[str, Any]:
    env = dict(os.environ if environment is None else environment)
    worktree = git_worktree or str(Path.cwd().resolve())
    preflight = evaluate_expected_scope_preflight(
        environment=env,
        git_worktree=worktree,
    )

    if not execute:
        return {
            "mode": "PREFLIGHT_ONLY",
            "preflight": preflight,
            "plan": public_plan_summary(),
            "network_request_attempted": False,
            "source_gate_c_closed": False,
            "source_gate_d_closed": False,
            "source_gate_e_closed": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        }

    if not preflight["expected_scope_network_execution_authorized"]:
        raise KRXExpectedScopeWorkerError(
            "expected-scope execution preflight blocked: "
            + ",".join(preflight["missing_requirements"])
        )

    out = batch_runner(
        environment=env,
        git_worktree=worktree,
        max_new_dates=max_new_dates,
    )
    if out.get("source_gate_c_closed") is not False:
        raise KRXExpectedScopeWorkerError(
            "expected-scope batch illegally closed Gate C"
        )
    if out.get("sealed_holdout_authorized") is not False:
        raise KRXExpectedScopeWorkerError(
            "expected-scope batch illegally authorized holdout"
        )
    if out.get("live_trading_authorized") is not False:
        raise KRXExpectedScopeWorkerError(
            "expected-scope batch illegally authorized live trading"
        )
    return {
        **out,
        "mode": "EXECUTE_EXPECTED_SCOPE_BATCH",
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the consent-gated expected-scope batch.",
    )
    parser.add_argument(
        "--max-new-dates",
        type=int,
        default=None,
        help="Operational pause limit; does not alter the frozen 4,127-date task set.",
    )
    args = parser.parse_args()
    out = run_expected_scope_worker(
        execute=bool(args.execute),
        max_new_dates=args.max_new_dates,
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
