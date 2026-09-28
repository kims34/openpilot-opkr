"""Diagnose post-entry missing-bar cases in the PIT preliminary dataset.

Primary PnL labels remain unchanged.  This script only classifies why an
executable bar disappeared by consulting the full daily membership lineage that
includes invalid/halted rows.  It prevents us from silently treating every data
absence as the same economic event before exact KRX halt/delisting data exist.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_pit_labels import make_pit_supervised
from run_research_v1 import load_panel


def _session_distance(all_dates: list[pd.Timestamp], start: pd.Timestamp, end: pd.Timestamp) -> int | None:
    pos = {d: i for i, d in enumerate(all_dates)}
    if start not in pos or end not in pos:
        return None
    return int(pos[end] - pos[start])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--membership", default="research_data/marcap_kospi_pit/lineage/membership_status.parquet")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_gap_diagnostics")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    membership_path = Path(args.membership)
    if not membership_path.exists():
        raise RuntimeError(f"membership lineage missing: {membership_path}")
    membership = pd.read_parquet(membership_path)
    membership["decision_date"] = pd.to_datetime(membership["decision_date"])
    membership["symbol"] = membership["symbol"].astype(str)

    frame, record_map, label_diag = make_pit_supervised(
        raw,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
    )
    gaps = frame[frame["post_entry_missing_future"].fillna(False).astype(bool)].copy()

    all_dates = sorted(pd.Timestamp(x) for x in membership["decision_date"].drop_duplicates())
    member_keys = set(zip(membership["decision_date"].dt.date, membership["symbol"].astype(str)))
    invalid_keys = set(zip(
        membership.loc[~membership["bar_valid_for_execution"].fillna(False).astype(bool), "decision_date"].dt.date,
        membership.loc[~membership["bar_valid_for_execution"].fillna(False).astype(bool), "symbol"].astype(str),
    ))
    valid_dates_by_symbol = {
        str(s): sorted(pd.Timestamp(x) for x in g["decision_date"].unique())
        for s, g in raw.groupby("symbol", sort=False)
    }
    member_dates_by_symbol = {
        str(s): sorted(pd.Timestamp(x) for x in g["decision_date"].unique())
        for s, g in membership.groupby("symbol", sort=False)
    }

    rows = []
    for row in gaps.itertuples(index=False):
        decision_day = pd.Timestamp(row.decision_date).date()
        symbol = str(row.symbol)
        rec = record_map.get((decision_day, symbol))
        if rec is None or rec.outcome != "STOP_DATA_GAP":
            continue
        missing_ts = pd.Timestamp(rec.exit_day)
        key = (missing_ts.date(), symbol)
        membership_present = key in member_keys
        invalid_bar_present = key in invalid_keys

        later_membership = [d for d in member_dates_by_symbol.get(symbol, []) if d > missing_ts]
        later_valid = [d for d in valid_dates_by_symbol.get(symbol, []) if d > missing_ts]
        next_member = later_membership[0] if later_membership else None
        next_valid = later_valid[0] if later_valid else None

        if membership_present and invalid_bar_present:
            cause = "MEMBER_PRESENT__BAR_INVALID_OR_HALTED"
        elif membership_present:
            # Should be rare: membership row exists and claims valid bar but was
            # absent from the executable lookup. Keep it explicit as a pipeline
            # integrity category instead of guessing.
            cause = "MEMBER_PRESENT__UNEXPECTED_LOOKUP_GAP"
        elif next_member is not None:
            cause = "MEMBER_ABSENT__REAPPEARS_LATER"
        else:
            cause = "MEMBER_ABSENT__NO_REAPPEARANCE_IN_OBSERVED_WINDOW"

        rows.append({
            "decision_date": pd.Timestamp(row.decision_date),
            "symbol": symbol,
            "missing_date": missing_ts,
            "cause": cause,
            "membership_present_on_missing_date": bool(membership_present),
            "invalid_bar_present_on_missing_date": bool(invalid_bar_present),
            "next_membership_date": next_member,
            "next_valid_execution_date": next_valid,
            "sessions_to_membership_return": _session_distance(all_dates, missing_ts, next_member) if next_member is not None else None,
            "sessions_to_valid_execution_return": _session_distance(all_dates, missing_ts, next_valid) if next_valid is not None else None,
            "primary_net_return": float(rec.net_return),
        })

    detail = pd.DataFrame(rows)
    if detail.empty:
        cause_counts = {}
        valid_resume = np.array([], dtype=float)
    else:
        cause_counts = {str(k): int(v) for k, v in detail["cause"].value_counts().items()}
        valid_resume = pd.to_numeric(detail["sessions_to_valid_execution_return"], errors="coerce").dropna().to_numpy(dtype=float)

    report = {
        "evaluation_stage": "PIT_PRELIMINARY_DATA_LINEAGE_DIAGNOSTIC",
        "primary_pnl_labels_changed": False,
        "label_diagnostics": label_diag,
        "post_entry_missing_cases_in_frame": int(len(gaps)),
        "classified_stop_data_gap_cases": int(len(detail)),
        "cause_counts": cause_counts,
        "resume_statistics": {
            "cases_with_later_valid_execution": int(len(valid_resume)),
            "median_sessions_to_valid_execution_return": float(np.median(valid_resume)) if len(valid_resume) else None,
            "p90_sessions_to_valid_execution_return": float(np.quantile(valid_resume, 0.90)) if len(valid_resume) else None,
        },
        "interpretation": {
            "MEMBER_PRESENT__BAR_INVALID_OR_HALTED": "Security remains in same-day PIT membership but lacks an executable OHLC bar; do not equate automatically with delisting.",
            "MEMBER_ABSENT__REAPPEARS_LATER": "Security disappears from daily membership temporarily then returns; exact corporate-action/status history is needed.",
            "MEMBER_ABSENT__NO_REAPPEARANCE_IN_OBSERVED_WINDOW": "Terminal observed absence, but not automatically proven delisting without an official event/status source.",
            "MEMBER_PRESENT__UNEXPECTED_LOOKUP_GAP": "Potential pipeline-integrity inconsistency requiring investigation.",
        },
        "next_rule": (
            "Do not replace the conservative STOP_DATA_GAP primary policy until exact executable economics are sourced. "
            "Use these counts to determine which official halt/delisting data are worth integrating first."
        ),
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    detail.to_csv(out / "cases.csv", index=False)
    print("GAP_DIAGNOSTICS=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
