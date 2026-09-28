"""Automatic suitability assessment for IndexAlert Research v1 smoke/Judge runs."""
from __future__ import annotations

import json
from pathlib import Path


def _load(path: str):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _row(name: str, m: dict, objective=None, admission_rule=None):
    ex = m.get("executable_set", {})
    port = m.get("portfolio", {})
    return {
        "name": name,
        "objective": objective or m.get("objective"),
        "admission_rule": admission_rule or m.get("admission_rule") or m.get("policy"),
        "trades": ex.get("trades", 0),
        "mean_net_return": ex.get("mean_net_return", 0.0),
        "profit_factor": ex.get("profit_factor", 0.0),
        "bootstrap_low": ex.get("cluster_bootstrap_95_low"),
        "total_return": port.get("total_return", 0.0),
        "max_drawdown": port.get("max_drawdown", 0.0),
        "trade_day_coverage": m.get("trade_day_coverage"),
        "primary_rank_mean_net_return": m.get("primary_rank_mean_net_return"),
        "backfill_mean_net_return": m.get("backfill_mean_net_return"),
    }


def _classify(row: dict):
    trades = int(row.get("trades") or 0)
    net = float(row.get("mean_net_return") or 0.0)
    pf = float(row.get("profit_factor") or 0.0)
    lo = row.get("bootstrap_low")
    mdd = float(row.get("max_drawdown") or 0.0)
    if trades == 0:
        return "NO_TRADE_FAIL_CLOSED", ["No policy had sufficiently robust positive evidence to admit trades."]
    reasons = []
    if net <= 0:
        reasons.append("Cost-adjusted mean trade return is not positive.")
    if pf <= 1.0:
        reasons.append("Profit factor is not above 1.0.")
    if lo is None or float(lo) <= 0:
        reasons.append("Date-cluster bootstrap lower bound is not above zero.")
    if mdd <= -0.10:
        reasons.append("Portfolio drawdown exceeds 10% in this smoke replay.")
    if not reasons:
        return "PROMISING_SMOKE_ONLY", ["All smoke diagnostics are positive, but PIT validation is still required."]
    if net > 0 and pf > 1.0:
        return "INSUFFICIENT_CONFIDENCE", reasons
    return "NOT_SUITABLE_YET", reasons


def main():
    baseline = _load("research_results/public_smoke/summary.json")
    ml = _load("research_results/public_smoke_ml/summary.json")
    selective = _load("research_results/public_smoke_selective/summary.json")
    holdaware = _load("research_results/public_smoke_holdaware/summary.json")
    context = _load("research_results/public_smoke_context/summary.json")

    rows = [_row(name, m) for name, m in ml.get("models", {}).items()]

    sel = selective.get("result", {})
    if sel:
        rows.append(_row(
            "logistic_calibrated_abstention", sel,
            objective="probability_positive_net_return",
            admission_rule="calibration_window_positive_cluster_LCB",
        ))

    for name, m in holdaware.get("models", {}).items():
        rows.append(_row(
            f"holdaware_{name}", m,
            objective="probability_positive_net_return",
            admission_rule="original_top3_only__held_names_leave_empty_slots",
        ))

    for name, m in context.get("models", {}).items():
        rows.append(_row(f"context_{name}", m))

    evaluated = []
    for row in rows:
        grade, reasons = _classify(row)
        evaluated.append({**row, "smoke_grade": grade, "issues": reasons})

    baseline_rows = []
    for name, s in baseline.get("strategies", {}).items():
        ex = s.get("executable_set", {})
        port = s.get("portfolio", {})
        baseline_rows.append({
            "name": name,
            "trades": ex.get("trades", 0),
            "mean_net_return": ex.get("mean_net_return", 0.0),
            "profit_factor": ex.get("profit_factor", 0.0),
            "bootstrap_low": ex.get("cluster_bootstrap_95_low"),
            "total_return": port.get("total_return", 0.0),
            "max_drawdown": port.get("max_drawdown", 0.0),
        })

    judge_eligible = bool(ml.get("judge_eligible")) and bool(baseline.get("judge_eligible"))
    overall = (
        "ENGINEERING_VALIDATED__INVESTMENT_PERFORMANCE_UNVERIFIED"
        if not judge_eligible
        else ("JUDGE_CANDIDATE_EXISTS" if any(x["smoke_grade"] == "PROMISING_SMOKE_ONLY" for x in evaluated) else "NO_JUDGE_CANDIDATE")
    )

    structural = []
    if any((x.get("backfill_mean_net_return") is not None and x.get("primary_rank_mean_net_return") is not None and x["backfill_mean_net_return"] < x["primary_rank_mean_net_return"]) for x in evaluated):
        structural.append("Backfilled lower-ranked names underperform primary ranks; do not force portfolio fill.")
    if any(float(x.get("profit_factor") or 0.0) < 1.0 and int(x.get("trades") or 0) > 0 for x in evaluated):
        structural.append("Current feature set/objectives do not yet consistently overcome transaction costs.")
    if any(int(x.get("trades") or 0) == 0 for x in evaluated):
        structural.append("Strict abstention can choose cash; this is preferable to forcing statistically unsupported trades.")
    if holdaware:
        structural.append("Hold-aware original-top3-only policy is explicitly benchmarked against deeper-rank backfill.")
    if context:
        structural.append("Simple market breadth/residual-return context is benchmarked without increasing model complexity.")
    if not judge_eligible:
        structural.append("Current 30-stock fixed basket is non-PIT and survivorship/selection biased; results cannot establish real profitability.")

    ranked = sorted(
        evaluated,
        key=lambda x: (
            float(x.get("bootstrap_low") or -999),
            float(x.get("mean_net_return") or -999),
            float(x.get("profit_factor") or 0),
        ),
        reverse=True,
    )

    report = {
        "overall_status": overall,
        "judge_eligible": judge_eligible,
        "interpretation": (
            "Engineering/model-selection diagnostics only until a historical point-in-time universe is available."
            if not judge_eligible else "Judge-eligible PIT assessment."
        ),
        "baseline_candidates": baseline_rows,
        "model_candidates": evaluated,
        "best_smoke_candidate_by_conservative_sort": ranked[0] if ranked else None,
        "structural_issues": structural,
        "next_actions": [
            "Use 0..3 admission; do not promote lower ranks merely to fill empty slots.",
            "Prefer direct economic-value objectives only if they improve cost-adjusted OOS results.",
            "Keep simple market/sector/regime context only if it improves the conservative lower bound, not just the point estimate.",
            "Do not add model complexity until a simple objective shows positive cost-adjusted edge.",
            "Replace fixed smoke basket with authenticated PIT KOSPI universe before any profitability claim.",
        ],
    }
    out = Path("research_results/assessment")
    out.mkdir(parents=True, exist_ok=True)
    (out / "assessment.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# IndexAlert Research v1 — Short-Term Suitability Assessment",
        "",
        f"**Overall:** `{overall}`",
        "",
        "## Model diagnostics",
        "",
        "| Model | Grade | Trades | Mean net/trade | PF | Cluster LCB | Total return | MDD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for x in evaluated:
        lines.append(
            f"| {x['name']} | {x['smoke_grade']} | {x['trades']} | {float(x['mean_net_return'] or 0):.4%} | "
            f"{float(x['profit_factor'] or 0):.3f} | {float(x['bootstrap_low'] or 0):.4%} | "
            f"{float(x['total_return'] or 0):.2%} | {float(x['max_drawdown'] or 0):.2%} |"
        )
    lines += ["", "## Structural issues", ""]
    lines += [f"- {x}" for x in structural]
    lines += ["", "## Interpretation", "", report["interpretation"]]
    (out / "assessment.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
