"""Prespecified cross-asset regime challenger for IndexAlert.

Only four external regime features are added to the frozen long-history
selection-conditioned Distributional NetEV protocol:
- lagged NASDAQ Composite 1d and 5d returns
- lagged VIX log level and 5d change

FRED is used only as a developmental historical carrier.  To avoid assuming a
FRED observation is immediately published at the underlying U.S. close, an
observation on U.S. trading day t becomes eligible only one calendar day after
the *next* NASDAQ observation.  This deliberately stale mapping covers ordinary
next-day publication plus weekend/holiday timing.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_netev import _fixed_record_map
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_selected_calibration import _evaluate_with_runner, selected_calibration_walk_forward
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

CROSS_ASSET_FEATURES = [
    "nasdaq_ret1_available",
    "nasdaq_ret5_available",
    "vix_log_available",
    "vix_change5_available",
]
CROSS_ASSET_CONTEXT_FEATURES = CONTEXT_FEATURES + CROSS_ASSET_FEATURES


def _read_fred_csv_bytes(content: bytes, series_id: str) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))
    if df.shape[1] < 2:
        raise ValueError(f"FRED {series_id}: expected date/value columns")
    date_col = df.columns[0]
    value_col = series_id if series_id in df.columns else df.columns[1]
    out = pd.DataFrame({
        "observation_date": pd.to_datetime(df[date_col], errors="coerce"),
        "value": pd.to_numeric(df[value_col], errors="coerce"),
    }).dropna()
    out = out.sort_values("observation_date").drop_duplicates("observation_date", keep="last")
    if out.empty:
        raise ValueError(f"FRED {series_id}: no numeric observations")
    return out.reset_index(drop=True)


def fetch_fred_series(series_id: str) -> tuple[pd.DataFrame, dict]:
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv"
    r = requests.get(url, params={"id": series_id}, timeout=30)
    r.raise_for_status()
    content = r.content
    df = _read_fred_csv_bytes(content, series_id)
    meta = {
        "series_id": series_id,
        "source_url": r.url,
        "sha256": hashlib.sha256(content).hexdigest(),
        "rows": int(len(df)),
        "first_observation": str(df["observation_date"].min().date()),
        "last_observation": str(df["observation_date"].max().date()),
    }
    return df, meta


def build_available_cross_asset(nasdaq: pd.DataFrame, vix: pd.DataFrame) -> pd.DataFrame:
    n = nasdaq.copy().sort_values("observation_date").reset_index(drop=True)
    v = vix.copy().sort_values("observation_date").reset_index(drop=True)

    n["nasdaq_ret1_available"] = n["value"].pct_change(1, fill_method=None)
    n["nasdaq_ret5_available"] = n["value"].pct_change(5, fill_method=None)
    n["next_us_observation"] = n["observation_date"].shift(-1)
    n["available_date"] = n["next_us_observation"] + pd.Timedelta(days=1)
    n = n.rename(columns={"observation_date": "source_observation_date"})

    v["vix_log_available"] = np.log(v["value"].where(v["value"] > 0))
    v["vix_change5_available"] = v["value"].pct_change(5, fill_method=None)
    v = v.rename(columns={"observation_date": "vix_observation_date"})

    # For each NASDAQ observation, attach the latest VIX observation no later
    # than that U.S. date.  This never uses a future VIX value.
    joined = pd.merge_asof(
        n.sort_values("source_observation_date"),
        v[["vix_observation_date", "vix_log_available", "vix_change5_available"]].sort_values("vix_observation_date"),
        left_on="source_observation_date",
        right_on="vix_observation_date",
        direction="backward",
        tolerance=pd.Timedelta(days=7),
    )
    joined = joined.dropna(subset=["available_date"]).copy()
    cols = [
        "source_observation_date", "vix_observation_date", "available_date",
        *CROSS_ASSET_FEATURES,
    ]
    return joined[cols].sort_values("available_date").reset_index(drop=True)


def add_cross_asset_features(supervised: pd.DataFrame, available: pd.DataFrame) -> pd.DataFrame:
    dates = pd.DataFrame({"decision_date": sorted(pd.to_datetime(supervised["decision_date"].unique()))})
    mapped = pd.merge_asof(
        dates.sort_values("decision_date"),
        available.sort_values("available_date"),
        left_on="decision_date",
        right_on="available_date",
        direction="backward",
    )
    mapped["cross_asset_source_lag_days"] = (
        mapped["decision_date"] - mapped["source_observation_date"]
    ).dt.days
    # Hard integrity condition: no same/future U.S. observation may reach a
    # Korean decision row under the conservative mapping.
    bad = mapped[
        mapped["source_observation_date"].notna()
        & (mapped["source_observation_date"] >= mapped["decision_date"])
    ]
    if len(bad):
        raise RuntimeError(f"cross-asset availability leakage detected in {len(bad)} dates")

    keep = [
        "decision_date", "source_observation_date", "vix_observation_date",
        "available_date", "cross_asset_source_lag_days", *CROSS_ASSET_FEATURES,
    ]
    return supervised.merge(mapped[keep], on="decision_date", how="left", validate="many_to_one")


def _promotion_view(result: dict) -> dict:
    gated = result["market_eligibility_overlay"]
    m = gated["metrics"]
    best5 = gated["extreme_day_dependency"].get("remove_best_days", {}).get("5", {}).get("metrics", {})
    return {
        "trades": int(m.get("trades", 0)),
        "mean_net_return": float(m.get("mean_net_return", 0.0)),
        "profit_factor": float(m.get("profit_factor", 0.0)),
        "cluster_bootstrap_95_low": float(m.get("cluster_bootstrap_95_low", 0.0)),
        "expected_shortfall_95": float(m.get("trade_expected_shortfall_95", 0.0)),
        "max_drawdown": float(gated.get("portfolio", {}).get("max_drawdown", 0.0)),
        "best5_removed_mean_net_return": float(best5.get("mean_net_return", 0.0)),
        "best5_removed_profit_factor": float(best5.get("profit_factor", 0.0)),
    }


def _recent_view(selected: pd.DataFrame, all_dates: list[pd.Timestamp], sessions: int = 504) -> dict:
    recent = all_dates[-min(int(sessions), len(all_dates)):] if all_dates else []
    if not recent:
        return {"sessions": 0, "records": 0}
    start, end = recent[0].date(), recent[-1].date()
    if selected.empty:
        return {"start": str(start), "end": str(end), "sessions": len(recent), "records": 0}
    d = pd.to_datetime(selected["decision_date"]).dt.date
    sub = selected[(d >= start) & (d <= end)].copy()
    net = pd.to_numeric(sub.get("fh_net_return"), errors="coerce").dropna() if len(sub) else pd.Series(dtype=float)
    if net.empty:
        return {"start": str(start), "end": str(end), "sessions": len(recent), "records": 0}
    gains = float(net[net > 0].sum())
    losses = float(-net[net < 0].sum())
    return {
        "start": str(start), "end": str(end), "sessions": len(recent),
        "records": int(len(net)), "mean_net_return": float(net.mean()),
        "positive_rate": float((net > 0).mean()),
        "profit_factor": float(gains / losses) if losses > 0 else (float("inf") if gains > 0 else 0.0),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_cross_asset")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--train-days", type=int, default=504)
    ap.add_argument("--cal-days", type=int, default=126)
    ap.add_argument("--test-days", type=int, default=126)
    args = ap.parse_args()

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        nasdaq, nasdaq_meta = fetch_fred_series("NASDAQCOM")
        vix, vix_meta = fetch_fred_series("VIXCLS")
    except Exception as exc:
        report = {
            "evaluation_stage": "CROSS_ASSET_SOURCE_UNAVAILABLE",
            "source_error_type": type(exc).__name__,
            "source_error": str(exc)[:500],
            "performance_test_run": False,
        }
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("CROSS_ASSET=" + json.dumps(report, ensure_ascii=False), flush=True)
        return

    available = build_available_cross_asset(nasdaq, vix)
    raw = load_panel(Path(args.cache))
    frame, legacy_map, label_diag, cache_meta = load_or_build(
        raw, Path(args.supervised_cache), horizon=args.horizon,
        target_return=0.04, stop_return=-0.025,
        participation=0.0005, commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    enriched = add_cross_asset_features(context, available)
    z = add_fixed_horizon_target(raw, enriched, legacy_map, args.horizon)
    fixed_map = _fixed_record_map(z, args.horizon)

    runner = lambda zz, **kw: selected_calibration_walk_forward(zz, top_k=args.top_k, **kw)
    reference, _, reference_gate_selected = _evaluate_with_runner(
        z, fixed_map, raw,
        name="all_context_selection_conditioned_q25_reference",
        features=CONTEXT_FEATURES, runner=runner,
        train_days=args.train_days, cal_days=args.cal_days, test_days=args.test_days,
        horizon=args.horizon, top_k=args.top_k,
    )
    challenger, _, challenger_gate_selected = _evaluate_with_runner(
        z, fixed_map, raw,
        name="all_context_plus_cross_asset_selection_conditioned_q25",
        features=CROSS_ASSET_CONTEXT_FEATURES, runner=runner,
        train_days=args.train_days, cal_days=args.cal_days, test_days=args.test_days,
        horizon=args.horizon, top_k=args.top_k,
    )

    dates = sorted(pd.Timestamp(x) for x in z["decision_date"].drop_duplicates())
    ref_view = _promotion_view(reference)
    ch_view = _promotion_view(challenger)
    ref_recent = _recent_view(reference_gate_selected, dates)
    ch_recent = _recent_view(challenger_gate_selected, dates)
    deltas = {k: ch_view[k] - ref_view[k] for k in ch_view}

    mapped_dates = enriched[["decision_date", "source_observation_date", "cross_asset_source_lag_days"]].drop_duplicates("decision_date")
    valid_lags = pd.to_numeric(mapped_dates["cross_asset_source_lag_days"], errors="coerce").dropna()
    source_diag = {
        "nasdaq": nasdaq_meta,
        "vix": vix_meta,
        "raw_source_values_persisted": False,
        "availability_rule": "eligible_one_calendar_day_after_next_NASDAQ_observation",
        "mapped_decision_dates": int(mapped_dates["source_observation_date"].notna().sum()),
        "min_source_lag_days": int(valid_lags.min()) if len(valid_lags) else None,
        "median_source_lag_days": float(valid_lags.median()) if len(valid_lags) else None,
        "max_source_lag_days": int(valid_lags.max()) if len(valid_lags) else None,
        "same_or_future_source_rows": int((valid_lags <= 0).sum()) if len(valid_lags) else 0,
    }

    criteria = {
        "positive_mean": ch_view["mean_net_return"] > 0,
        "pf_gt_1": ch_view["profit_factor"] > 1,
        "cluster_lcb_positive": ch_view["cluster_bootstrap_95_low"] > 0,
        "best5_mean_positive": ch_view["best5_removed_mean_net_return"] > 0,
        "best5_pf_gt_1": ch_view["best5_removed_profit_factor"] > 1,
        "recent_has_admissions": ch_recent.get("records", 0) > 0,
        "recent_mean_positive": ch_recent.get("mean_net_return", 0.0) > 0,
        "recent_pf_gt_1": ch_recent.get("profit_factor", 0.0) > 1,
        "es95_not_worse": ch_view["expected_shortfall_95"] >= ref_view["expected_shortfall_95"],
        "mdd_not_worse": ch_view["max_drawdown"] >= ref_view["max_drawdown"],
        "availability_integrity": source_diag["same_or_future_source_rows"] == 0,
    }
    full_pass = all(criteria.values())

    report = {
        "evaluation_stage": "DEVELOPMENTAL_CROSS_ASSET_REGIME_FAMILY_NOT_HOLDOUT",
        "history_start": str(raw["decision_date"].min().date()),
        "history_end": str(raw["decision_date"].max().date()),
        "protocol": {
            "only_change": "add_prespecified_NASDAQ_VIX_cross_asset_family",
            "model_changed": False,
            "calibration_quantiles_changed": False,
            "admission_threshold_changed": False,
            "top_k_changed": False,
            "cost_model_changed": False,
            "lag_search": False,
            "feature_subset_search": False,
            "promotion_allowed": False,
        },
        "cross_asset_features": CROSS_ASSET_FEATURES,
        "source_diagnostics": source_diag,
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "reference_promotion_view": ref_view,
        "challenger_promotion_view": ch_view,
        "delta_challenger_minus_reference": deltas,
        "reference_latest_504_sessions": ref_recent,
        "challenger_latest_504_sessions": ch_recent,
        "predeclared_criteria": criteria,
        "all_predeclared_criteria_pass": full_pass,
        "classification": (
            "DEVELOPMENTAL_CROSS_ASSET_WORTH_FURTHER_FALSIFICATION"
            if full_pass else "DEVELOPMENTAL_CROSS_ASSET_NOT_PROMOTABLE"
        ),
        "guardrail": (
            "FRED is a developmental historical carrier and this history is not sealed. "
            "Do not tune lags/windows/thresholds from this result."
        ),
    }
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("CROSS_ASSET=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
