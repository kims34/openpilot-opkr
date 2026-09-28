"""Compare prespecified Stage-2 IndexAlert challengers without score cherry-picking."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def metric_block(report: dict, kind: str):
    if kind == "combined":
        x = report["combined_path_fixed_horizon"]
    elif kind == "cross":
        x = report["cross_sectional_rank_ridge"]
    elif kind == "path":
        x = report["path_context"]
    elif kind == "fixed":
        x = report["fixed_horizon_logistic"]
    else:
        raise ValueError(kind)
    return {
        "mean_gross_return": float(x.get("mean_gross_return", 0.0)),
        "mean_net_return": float(x.get("mean_net_return", 0.0)),
        "profit_factor": float(x.get("profit_factor", 0.0)),
        "cluster_low": float(x.get("cluster_low", 0.0)),
        "cluster_high": float(x.get("cluster_high", 0.0)),
        "total_return": float(x.get("total_return", 0.0)),
        "max_drawdown": float(x.get("max_drawdown", 0.0)),
        "expected_shortfall_95": float(x.get("expected_shortfall_95", 0.0)) if x.get("expected_shortfall_95") is not None else None,
        "trades": int(x.get("trades", 0)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="research_results")
    ap.add_argument("--out", default="research_results/stage2_compare.json")
    args = ap.parse_args()
    root = Path(args.root)

    candidates = {}
    files = {
        "path_context": (root / "marcap_pit_path_context" / "summary.json", "path"),
        "fixed_horizon_logistic": (root / "marcap_pit_fixed_horizon" / "summary.json", "fixed"),
        "combined_path_fixed_horizon": (root / "marcap_pit_combined" / "summary.json", "combined"),
        "cross_sectional_rank": (root / "marcap_pit_cross_sectional" / "summary.json", "cross"),
    }
    for name, (path, kind) in files.items():
        if path.exists():
            candidates[name] = metric_block(load(path), kind)

    vol_path = root / "marcap_pit_vol_veto" / "summary.json"
    if vol_path.exists():
        vol = load(vol_path)
        for row in vol.get("results", []):
            name = f"vol_veto_{row.get('max_vol20_rank_allowed')}"
            candidates[name] = {
                "mean_gross_return": float(row.get("mean_gross_return", 0.0)),
                "mean_net_return": float(row.get("mean_net_return", 0.0)),
                "profit_factor": float(row.get("profit_factor", 0.0)),
                "cluster_low": float(row.get("cluster_low", 0.0)),
                "cluster_high": float(row.get("cluster_high", 0.0)),
                "total_return": float(row.get("total_return", 0.0)),
                "max_drawdown": float(row.get("max_drawdown", 0.0)),
                "expected_shortfall_95": float(row.get("expected_shortfall_95", 0.0)),
                "trades": int(row.get("trades", 0)),
            }

    for x in candidates.values():
        x["deployment_candidate"] = bool(
            x["mean_net_return"] > 0
            and x["profit_factor"] > 1.0
            and x["cluster_low"] > 0
            and x["max_drawdown"] > -0.20
        )

    ranked = sorted(
        ({"name": name, **x} for name, x in candidates.items()),
        key=lambda r: (r["deployment_candidate"], r["cluster_low"], r["mean_net_return"], r["profit_factor"]),
        reverse=True,
    )
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_STAGE2_COMPARE",
        "selection_rule": "deployment_pass_first_then_cluster_low_then_netEV_then_profit_factor",
        "candidates": ranked,
        "deployment_candidates": [r["name"] for r in ranked if r["deployment_candidate"]],
        "best_preliminary": ranked[0]["name"] if ranked else None,
        "note": "No candidate is promoted unless all deployment gates pass; ranking among failing candidates is diagnostic only.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("STAGE2_COMPARE=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
