"""Read-only, fail-closed status snapshot for IndexAlert research workstreams.

Passing this check never grants PIT admission, profitability, holdout, or order authority.
Only allowlisted public GitHub PR metadata are fetched; no provider or broker records.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY = "kims34/openpilot-opkr"
WORKSTREAM_PRS = {
    "opendart": 412,
    "backtest_runtime": 413,
    "profitability": 414,
    "kiwoom_readonly": 415,
    "investor_flow": 416,
}

def extract_pr_fields(payload: dict) -> dict:
    """Allowlisted fields only; raw API payloads and credentials are never persisted."""
    if not isinstance(payload, dict):
        raise ValueError("PR metadata must be an object")
    head = payload.get("head")
    if not isinstance(head, dict):
        raise ValueError("PR head metadata is missing")
    sha = head.get("sha")
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("PR HEAD SHA is malformed")
    state = payload.get("state")
    draft = payload.get("draft")
    if state not in ("open", "closed") or type(draft) is not bool:
        raise ValueError("PR state/draft malformed")
    return {
        "number": payload.get("number"), "state": state,
        "draft": draft, "head_sha": sha,
        "updated_at": payload.get("updated_at"),
        "html_url": payload.get("html_url"),
    }

def fetch_github_json(url: str, token: str) -> dict:
    if not url.startswith(f"https://api.github.com/repos/{REPOSITORY}/pulls/"):
        raise ValueError("not an allowlisted read-only PR URL")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "IndexAlert-readonly-proof-watchdog"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request(url, headers=headers, method="GET")
    with urlopen(req, timeout=12) as response:
        return json.load(response)

def build_report(fetcher=fetch_github_json, token: str = "") -> dict:
    report = {
        "schema_version": "indexalert-hourly-proof-watchdog-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": REPOSITORY,
        "mode": "READ_ONLY_METADATA_PLUS_OFFLINE_REGRESSION",
        "workstreams": {},
        "checks_completed": False,
        "source_pit_admission": "NOT_ATTESTED_BY_WATCHDOG",
        "m20_performance_run_authorized": False,
        "independent_holdout_authorized": False,
        "automatic_promotion_authorized": False,
        "real_order_authorized": False,
        "funds_movement_authorized": False,
        "ordering_switch_change_authorized": False,
        "blockers": [],
    }
    errors = []
    for label, number in WORKSTREAM_PRS.items():
        url = f"https://api.github.com/repos/{REPOSITORY}/pulls/{number}"
        try:
            fields = extract_pr_fields(fetcher(url, token))
            if fields["number"] != number:
                raise ValueError("mismatched PR number")
            report["workstreams"][label] = fields
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError, KeyError) as exc:
            # Never copy exception payloads: providers may attach sensitive data.
            errors.append({"workstream": label, "error_type": type(exc).__name__})
            report["workstreams"][label] = {"number": number, "status": "UNVERIFIED"}
    report["checks_completed"] = not errors
    report["blockers"] = ["OFFICIAL_PIT_ADMISSION_NOT_ATTESTED"]
    if errors:
        report["blockers"].append("READ_ONLY_GITHUB_METADATA_INCOMPLETE")
        report["fetch_errors"] = errors
    return report

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = build_report(token=os.getenv("GITHUB_TOKEN", ""))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("IndexAlert read-only evidence metadata:", "COMPLETE" if report["checks_completed"] else "INCOMPLETE")
    print("M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED")
    return 0 if report["checks_completed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
