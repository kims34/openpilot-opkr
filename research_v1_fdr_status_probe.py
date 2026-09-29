"""Metadata-only probe for public KRX delisting/status history via FinanceDataReader.

Purpose: determine whether the current public reproducible path can help replace
heuristic terminal-absence handling. This is data-quality work, not alpha research.
No price rows or security names are persisted; only reachability, row counts,
columns and date coverage are written.
"""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    out = Path("research_results/fdr_status_probe")
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "purpose": "DATA_QUALITY_SOURCE_FEASIBILITY_ONLY_NOT_ALPHA_RESEARCH",
        "numeric_market_data_persisted": False,
        "status": "PENDING",
    }
    try:
        import FinanceDataReader as fdr

        listing = fdr.StockListing("KRX-DELISTING", "2015-06-15", "2026-09-28")
        report["delisting_listing"] = {
            "status": "REACHABLE",
            "rows": int(len(listing)),
            "columns": [str(c) for c in listing.columns],
        }
        if "DelistingDate" in listing.columns and len(listing):
            d = listing["DelistingDate"]
            report["delisting_listing"].update({
                "min_date": str(d.min()),
                "max_date": str(d.max()),
            })

        # One historical delisted issue documented by FinanceDataReader. Only
        # return metadata; do not persist rows.
        px = fdr.DataReader("KRX-DELISTING:068400", "2023-01-01", "2024-01-31")
        report["delisted_price_probe"] = {
            "status": "REACHABLE",
            "rows": int(len(px)),
            "columns": [str(c) for c in px.columns],
            "has_stop_order": "StopOrder" in px.columns,
            "has_issues": "Issues" in px.columns,
            "has_standard_price": "StandardPrice" in px.columns,
            "min_date": str(px.index.min()) if len(px) else None,
            "max_date": str(px.index.max()) if len(px) else None,
        }
        report["status"] = "SOURCE_REACHABLE"
    except Exception as exc:
        report.update({
            "status": "SOURCE_UNREACHABLE_OR_CHANGED",
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:500],
        })

    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("FDR_STATUS_PROBE=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
