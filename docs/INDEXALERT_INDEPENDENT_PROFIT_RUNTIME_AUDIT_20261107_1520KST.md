# IndexAlert independent profitability/runtime audit — 2026-11-07 15:20 KST

Scope: read-only verification of GitHub and Railway; no official economic run, deployment, workflow modification, merge, ordering, or trading.

## Exact refs
- research index-alert-research-v1 HEAD: df474df348f22aa38b1dedaa59fcff66e548b406 (self-compare identical).
- development index-alert-position-regen-fix-v1 HEAD: 1e6367d2863a86c3470da13d81a955d277eba485 (self-compare identical).
- PR #414 integration document blob: 984c933651f39f1ee9e26a1d7ac3893aaa5335be.
- PR #412, #413, #414, #418, #420, #422, #423: OPEN / Draft; PR head SHAs not independently extracted this run.

## CI evidence (jobs re-fetched)
- OpenDART 38419439742: 2/2 success. Original-filing semantic/available-at proof NOT VERIFIED.
- Isolated runner 38419649711: 1/1 success. Synthetic only.
- Optimization 38498552499: 6/6 success. Full CI and official backtest acceleration NOT VERIFIED.
- Chronology Anchor 41515392296: auto-anchor FAILURE, validation SKIPPED. Public original-filing chronology NOT VERIFIED.
- Historical regression 38381997417/38382214223 and corrective 38419111311: prior supplied evidence only, not re-fetched this run.

## Railway production (fresh environment_status)
- indexalert-kiwoom-real-readonly: deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS, replicas running 0 / crashed 1. Operational readiness FAIL.
- db-query-readonly: 1 critical notification, root cause NOT VERIFIED.
- PIT rebuild 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5: 1/1 running; KRX historical worker 16c93d7c-7cd0-4d84-a327-298d2805376c: 0/1 running (not necessarily crash). Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00: 1/1 running.
- Pending patch e113dacb-6705-4416-9997-dc694539d382: staged, empty changes []; do not apply.
- Logs for readonly/PIT/KRX queried from 2026-11-07T04:00:00Z; no entries returned. No conclusion about resolution of previous 27 invalid OHLC rows.

## Gates
- KRX historical weekday raw-pair storage integrity 1565/1565: historical PASS only, not newly revalidated.
- Original-filing and precise public available-at/PIT: NOT VERIFIED.
- 2021/2022 first-three-month consolidated operating income period/amendment lineage: NOT VERIFIED.
- Historical issuer/security mapping and official KRX state/corporate actions/executability: NOT VERIFIED.
- Cost/tax-adjusted annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness: NOT VERIFIED.
- Offline synthetic CI: PASS for checked jobs only.
- M20 economic RUN: NO-GO. ORDERING=false policy retained; live config not modified or independently checked.

## Next safe steps
1. Independently inspect chronology anchor job log and source route/commit evidence; resolve only in assigned isolated work area.
2. Read-only investigate crashed replica and db-query critical; distinguish stale success deployment from actual process health.
3. Resolve PIT official source chronology, period/lineage, historical mapping, KRX calendar/status/executability before any economic RUN.
4. Cache only on exact approved data/code/Frozen policy/runtime/evidence SHA-256 equality, fail-closed; parallelize only independent read-only postprocessing.
5. Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout, risk, cost and promotion rules unchanged; no merges, deploys, orders or champion promotion.
