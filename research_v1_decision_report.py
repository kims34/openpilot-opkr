"""Automatic adopt/reject report for IndexAlert research challengers.

This intentionally avoids a composite score.  A challenger must improve economic
metrics without hiding a tail-risk deterioration, and promotion remains stricter
than mere incremental improvement.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def passes_promotion(m):
    return (
        float(m.get("mean_net_return", 0.0)) > 0
        and float(m.get("profit_factor", 0.0)) > 1.0
        and float(m.get("cluster_low", 0.0)) > 0
        and float(m.get("max_drawdown", -1.0)) > -0.10
    )


def incremental(candidate, baseline):
    if not candidate or not baseline:
        return {"status": "MISSING"}
    net_delta = float(candidate.get("mean_net_return", 0.0)) - float(baseline.get("mean_net_return", 0.0))
    pf_delta = float(candidate.get("profit_factor", 0.0)) - float(baseline.get("profit_factor", 0.0))
    lcb_delta = float(candidate.get("cluster_low", 0.0)) - float(baseline.get("cluster_low", 0.0))
    mdd_delta = float(candidate.get("max_drawdown", -1.0)) - float(baseline.get("max_drawdown", -1.0))
    improved = net_delta > 0 and pf_delta > 0 and lcb_delta >= 0 and mdd_delta >= -0.02
    return {
        "status": "IMPROVEMENT_CANDIDATE" if improved else "REJECT_INCREMENTAL",
        "delta_mean_net_return": net_delta,
        "delta_profit_factor": pf_delta,
        "delta_cluster_low": lcb_delta,
        "delta_max_drawdown": mdd_delta,
        "promotion_candidate": passes_promotion(candidate),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", default="research_results/marcap_pit_fast/summary.json")
    ap.add_argument("--path", default="research_results/marcap_pit_path_context/summary.json")
    ap.add_argument("--fixed", default="research_results/marcap_pit_fixed_horizon/summary.json")
    ap.add_argument("--out", default="research_results/decision_report")
    args = ap.parse_args()

    fast = load(Path(args.fast))
    path = load(Path(args.path))
    fixed = load(Path(args.fixed))

    baseline = None
    if path:
        baseline = path.get("baseline_logistic_context")
    elif fixed:
        baseline = fixed.get("barrier_label_baseline")
    elif fast:
        ex = fast.get("candidate_primary", {}).get("executable_set", {})
        port = fast.get("candidate_primary", {}).get("portfolio", {})
        baseline = {
            "mean_net_return": ex.get("mean_net_return", 0.0),
            "profit_factor": ex.get("profit_factor", 0.0),
            "cluster_low": ex.get("cluster_bootstrap_95_low", 0.0),
            "max_drawdown": port.get("max_drawdown", -1.0),
        }

    report = {
        "baseline": baseline,
        "baseline_promotion_candidate": passes_promotion(baseline or {}),
        "path_context": incremental(path.get("path_context") if path else None, baseline),
        "fixed_horizon_logistic": incremental(fixed.get("fixed_horizon_logistic") if fixed else None, baseline),
        "fixed_horizon_ridge": incremental(fixed.get("fixed_horizon_ridge_positive_only") if fixed else None, baseline),
        "rule": (
            "Incremental improvement requires better mean net return, PF and cluster LCB without >2 percentage-point MDD deterioration. "
            "Promotion separately requires positive mean net, PF>1, positive cluster LCB and MDD better than -10%."
        ),
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "decision.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# IndexAlert Research Decision Report", "", f"Baseline promotion: **{report['baseline_promotion_candidate']}**", ""]
    for key in ["path_context", "fixed_horizon_logistic", "fixed_horizon_ridge"]:
        r = report[key]
        lines.append(f"- **{key}**: {r.get('status')} / promotion={r.get('promotion_candidate', False)}")
    lines += ["", report["rule"]]
    (out / "decision.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
