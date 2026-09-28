"""Walk-forward ML smoke tournament for IndexAlert Research v1.

This module is intentionally conservative and is NOT Judge-eligible when fed the
fixed public smoke universe. It verifies that model training, fold isolation,
ranking, economic outcomes, and portfolio replay all work end-to-end before an
authenticated point-in-time universe is available.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from research_v1_core import AmbiguousFirstHit, Bar, cost_model_return, date_cluster_bootstrap_mean, economic_outcome, summarize
from research_v1_portfolio import simulate_portfolio, summary_dict
from run_research_v1 import add_features, build_lookup, load_panel

FEATURES = [
    "ret1", "ret5", "ret20", "vol20", "log_adv20",
    "ret5_rank", "ret20_rank", "vol20_rank", "adv20_rank",
]


def make_supervised(
    raw_panel: pd.DataFrame,
    horizon: int = 5,
    target_return: float = 0.04,
    stop_return: float = -0.025,
    half_spread_bps: float = 4.0,
    explicit_bps: float = 23.0,
    participation: float = 0.0005,
    impact_coefficient: float = 0.10,
):
    x = add_features(raw_panel)
    x["log_adv20"] = np.log1p(x["adv20"].clip(lower=0))
    for col in ["ret5", "ret20", "vol20", "adv20"]:
        x[f"{col}_rank"] = x.groupby("decision_date")[col].rank(pct=True)
    dates, date_to_pos, by_symbol = build_lookup(x)

    rows = []
    record_map = {}
    ambiguous = skipped = 0
    for row in x.itertuples(index=False):
        vals = [getattr(row, f) for f in FEATURES]
        if any(pd.isna(v) for v in vals):
            continue
        decision_ts = pd.Timestamp(row.decision_date)
        pos = date_to_pos[decision_ts]
        future_dates = dates[pos + 1: pos + 1 + horizon]
        if len(future_dates) < horizon:
            continue
        hist = by_symbol.get(row.symbol)
        if hist is None:
            skipped += 1
            continue
        try:
            entry_row = hist.loc[pd.Timestamp(future_dates[0])]
        except KeyError:
            skipped += 1
            continue
        future = []
        valid = True
        for d in future_dates:
            try:
                r = hist.loc[pd.Timestamp(d)]
            except KeyError:
                valid = False
                break
            future.append(Bar(
                day=pd.Timestamp(d).date(), open=float(r.open), high=float(r.high),
                low=float(r.low), close=float(r.close), volume=float(r.volume), value=float(r.value),
            ))
        if not valid:
            skipped += 1
            continue
        cost = cost_model_return(
            half_spread_bps, explicit_bps, float(row.vol20), participation, impact_coefficient
        )
        kwargs = dict(
            decision_day=decision_ts.date(), symbol=str(row.symbol), score=0.0,
            entry_price=float(entry_row.open), future_bars=future,
            target_return=target_return, stop_return=stop_return,
            round_trip_cost_return=cost,
        )
        try:
            rec = economic_outcome(**kwargs)
            was_ambiguous = False
        except AmbiguousFirstHit:
            ambiguous += 1
            was_ambiguous = True
            # Do not remove a candidate using future path information. The
            # primary smoke/Judge sensitivity scores unknown same-bar ordering
            # pessimistically as STOP-first until intraday data resolves it.
            rec = economic_outcome(**kwargs, ambiguous_policy="stop_first")
        key = (decision_ts.date(), str(row.symbol))
        record_map[key] = rec
        item = {
            "decision_date": decision_ts,
            "symbol": str(row.symbol),
            "label_positive_net": int(rec.net_return > 0),
            "net_return": rec.net_return,
            "ambiguous_same_bar": bool(was_ambiguous),
        }
        item.update({f: float(getattr(row, f)) for f in FEATURES})
        rows.append(item)
    frame = pd.DataFrame(rows).sort_values(["decision_date", "symbol"]).reset_index(drop=True)
    return frame, record_map, {
        "ambiguous": ambiguous,
        "skipped": skipped,
        "ambiguous_primary_policy": "stop_first_conservative_no_future_filter",
    }


def _pipeline(kind: str) -> Pipeline:
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), FEATURES)
    ], remainder="drop")
    if kind == "logistic_l2":
        clf = LogisticRegression(C=1.0, penalty="l2", solver="liblinear", max_iter=2000, random_state=20260928)
    elif kind == "logistic_elasticnet":
        clf = LogisticRegression(C=0.5, penalty="elasticnet", l1_ratio=0.5, solver="saga", max_iter=3000, random_state=20260928)
    else:
        raise ValueError(kind)
    return Pipeline([("prep", prep), ("clf", clf)])


def walk_forward_predictions(frame: pd.DataFrame, kind: str, train_days: int = 200, test_days: int = 40) -> pd.DataFrame:
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    out = []
    start = train_days
    while start < len(dates):
        test_block = dates[start:start + test_days]
        if not test_block:
            break
        train_block = dates[:start]
        train = frame[frame["decision_date"].isin(train_block)]
        test = frame[frame["decision_date"].isin(test_block)].copy()
        if train["label_positive_net"].nunique() < 2 or test.empty:
            start += test_days
            continue
        pipe = _pipeline(kind)
        pipe.fit(train[FEATURES], train["label_positive_net"])
        test["prob"] = pipe.predict_proba(test[FEATURES])[:, 1]
        test["model"] = kind
        test["train_end"] = train_block[-1]
        out.append(test[["decision_date", "symbol", "label_positive_net", "net_return", "ambiguous_same_bar", "prob", "model", "train_end"]])
        start += test_days
    if not out:
        return pd.DataFrame(columns=["decision_date", "symbol", "label_positive_net", "net_return", "ambiguous_same_bar", "prob", "model", "train_end"])
    return pd.concat(out, ignore_index=True).sort_values(["decision_date", "prob"], ascending=[True, False])


def _records_from_top_signal(pred: pd.DataFrame, record_map: dict, top_k: int):
    selected = pred.groupby("decision_date", group_keys=False).head(top_k).copy()
    records = []
    for row in selected.itertuples(index=False):
        key = (pd.Timestamp(row.decision_date).date(), str(row.symbol))
        base = record_map.get(key)
        if base is None:
            continue
        records.append(base.__class__(**{**asdict(base), "score": float(row.prob)}))
    return records, selected


def stateful_select_records(
    scored: pd.DataFrame,
    record_map: dict,
    top_k: int = 3,
    threshold: float | None = None,
    active_until: dict[str, object] | None = None,
):
    """Select up to K executable names per day and backfill blocked top ranks.

    Availability is determined only from positions that would already be known
    open at that point in the replay. A blocked rank is replaced by the next
    eligible scored name rather than silently shrinking the portfolio.
    """
    state = active_until if active_until is not None else {}
    records = []
    selected_rows = []
    blocked = 0
    backfilled = 0
    for day, d in scored.groupby("decision_date", sort=True):
        ranked = d.sort_values("prob", ascending=False)
        picked = 0
        for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
            prob = float(row["prob"])
            if threshold is not None and prob < threshold:
                break
            symbol = str(row["symbol"])
            key = (pd.Timestamp(day).date(), symbol)
            base = record_map.get(key)
            if base is None:
                continue
            prev_exit = state.get(symbol)
            if prev_exit is not None and prev_exit >= base.entry_day:
                blocked += 1
                continue
            rec = base.__class__(**{**asdict(base), "score": prob})
            records.append(rec)
            state[symbol] = rec.exit_day
            out_row = row.to_dict()
            out_row["selection_rank"] = rank
            out_row["backfill"] = bool(rank > top_k)
            selected_rows.append(out_row)
            if rank > top_k:
                backfilled += 1
            picked += 1
            if picked >= top_k:
                break
    return records, pd.DataFrame(selected_rows), {
        "active_position_candidates_blocked": int(blocked),
        "backfill_selections": int(backfilled),
    }


def evaluate_model(pred: pd.DataFrame, record_map: dict, raw_panel: pd.DataFrame, horizon: int, top_k: int = 3):
    if pred.empty:
        return {}, pd.DataFrame(), pd.DataFrame()
    signal_records, _ = _records_from_top_signal(pred, record_map, top_k)
    executable_records, selected_exec, state_diag = stateful_select_records(pred, record_map, top_k=top_k)
    metrics_signal = summarize(signal_records)
    metrics_exec = summarize(executable_records)
    point, lo, hi = date_cluster_bootstrap_mean(executable_records) if executable_records else (0.0, 0.0, 0.0)
    eval_start = pd.Timestamp(pred["decision_date"].min()).date()
    eval_end = max(
        pd.Timestamp(pred["decision_date"].max()).date(),
        max((r.exit_day for r in executable_records), default=eval_start),
    )
    portfolio_path, portfolio_summary = simulate_portfolio(
        raw_panel, executable_records, horizon=horizon, initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon, suppress_duplicate_symbols=False,
        evaluation_start=eval_start, evaluation_end=eval_end,
    )
    y = pred["label_positive_net"].to_numpy(dtype=int)
    p = pred["prob"].to_numpy(dtype=float)
    brier = float(brier_score_loss(y, p))
    auc = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
    frac_pos, mean_pred = calibration_curve(y, p, n_bins=8, strategy="quantile")
    report = {
        "signal_set": asdict(metrics_signal),
        "executable_set": {
            **asdict(metrics_exec),
            "cluster_bootstrap_mean_net_return": point,
            "cluster_bootstrap_95_low": lo,
            "cluster_bootstrap_95_high": hi,
        },
        **state_diag,
        "brier": brier,
        "roc_auc_diagnostic": auc,
        "calibration_points": [
            {"mean_pred": float(mp), "fraction_positive": float(fp)}
            for mp, fp in zip(mean_pred, frac_pos)
        ],
        "portfolio": summary_dict(portfolio_summary),
        "prediction_rows": int(len(pred)),
        "selected_signal_rows": int(len(signal_records)),
        "selected_executable_rows": int(len(executable_records)),
        "selected_ambiguous_rows": int(selected_exec.get("ambiguous_same_bar", pd.Series(dtype=bool)).fillna(False).astype(bool).sum()) if not selected_exec.empty else 0,
        "test_dates": int(pred["decision_date"].nunique()),
    }
    return report, selected_exec, portfolio_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/public_smoke_daily")
    ap.add_argument("--result-dir", default="research_results/public_smoke_ml")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    pit = bool(raw.get("point_in_time_universe", pd.Series([False])).fillna(False).astype(bool).all())
    frame, record_map, diag = make_supervised(
        raw, horizon=args.horizon, target_return=args.target, stop_return=args.stop,
        participation=args.participation,
    )
    out_dir = Path(args.result_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "result_class": "JUDGE" if pit else "SMOKE_NONPIT",
        "judge_eligible": pit,
        "label": "positive_net_economic_outcome",
        "fold_policy": {
            "type": "expanding_walk_forward",
            "train_days_initial": args.train_days,
            "test_days": args.test_days,
            "preprocessing": "fit_inside_each_fold",
        },
        "selection_policy": "stateful_top_k_with_active_position_exclusion_and_rank_backfill",
        "features": FEATURES,
        "dataset_rows": int(len(frame)),
        "dataset_dates": int(frame["decision_date"].nunique()) if not frame.empty else 0,
        "diagnostics": diag,
        "models": {},
    }
    for kind in ["logistic_l2", "logistic_elasticnet"]:
        pred = walk_forward_predictions(frame, kind, args.train_days, args.test_days)
        model_report, selected, portfolio_path = evaluate_model(pred, record_map, raw, args.horizon, args.top_k)
        report["models"][kind] = model_report
        pred.to_csv(out_dir / f"{kind}_predictions.csv", index=False)
        selected.to_csv(out_dir / f"{kind}_selected_executable.csv", index=False)
        portfolio_path.to_csv(out_dir / f"{kind}_portfolio.csv", index=False)
    if not pit:
        report["warning"] = "Non-PIT smoke result. Engineering validation only; forbidden for model promotion or profitability claims."
    (out_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
