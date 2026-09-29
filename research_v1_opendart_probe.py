"""Metadata-only OpenDART source feasibility probe.

No disclosure content is persisted.  The probe only checks whether an API key is
configured and whether the official disclosure-list endpoint returns a valid
response for one already-completed date.  If adopted later, same-day disclosures
are conservatively shifted to the next eligible decision because the list API's
receipt-date field alone does not prove an intraday availability timestamp.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import requests


def main() -> None:
    out = Path("research_results/opendart_probe")
    out.mkdir(parents=True, exist_ok=True)
    key = os.getenv("OPENDART_API_KEY") or os.getenv("DART_API_KEY")
    report = {
        "purpose": "DATA_SOURCE_FEASIBILITY_ONLY_NOT_PERFORMANCE_RESEARCH",
        "source": "OpenDART_official_list_api",
        "numeric_or_document_content_persisted": False,
        "credentials_present": bool(key),
        "status": "AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "available_at_policy_if_adopted": (
            "receipt-date-only historical records are shifted to the next eligible decision unless an archived exact publication timestamp is independently established"
        ),
    }
    if not key:
        (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("OPENDART_PROBE=" + json.dumps(report, ensure_ascii=False), flush=True)
        return

    try:
        r = requests.get(
            "https://opendart.fss.or.kr/api/list.json",
            params={
                "crtfc_key": key,
                "bgn_de": "20260923",
                "end_de": "20260923",
                "page_count": "10",
            },
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        status = str(data.get("status", ""))
        report.update({
            "http_status": int(r.status_code),
            "dart_status": status,
            "dart_message": str(data.get("message", ""))[:200],
            "status": "SOURCE_REACHABLE" if status in {"000", "013"} else "SOURCE_REACHABLE_API_REJECTED",
            "reported_total_count": int(data.get("total_count", 0) or 0),
            "probe_date": "2026-09-23",
        })
    except Exception as exc:
        report.update({
            "status": "SOURCE_UNREACHABLE_OR_AUTH_FAILED",
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:500],
        })

    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OPENDART_PROBE=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
