# IndexAlert independent profitability gate — 2026-10-31 17:42 KST

Scope: read-only GitHub/Railway evidence audit; this Markdown note is the only permitted write. This is **not** source admission, model validation, trading authorization, or a performance run.

## Immutable references independently re-read
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX audit `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Integration Draft PR #414: head `5155641b4fcd68bfd3146566d23b3947ae383b2d`, open/unmerged; its 350 changed files are all Markdown at time of review. OpenDART Draft PR #412 head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, open/unmerged. KRX Draft PRs #420/#422/#423 also open/unmerged.
- Watchdog Actions [#41178674319](https://github.com/kims34/openpilot-opkr/actions/runs/41178674319) completed 2026-10-31 06:58 UTC: one successful job, 31/31 offline governance tests PASS, explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`.
- Prospective Chronology Anchor [#41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) failed on latest payload retrieval, HTTP 404; later chronology steps skipped. No manual retry or endpoint workaround.
- OpenDART [2022 source-only #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048) and [2021 source-only #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066): both offline and official jobs successful, but **original archive bytes were not independently downloaded/rehashed in this audit**. Prior officially recorded 2022 SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` and 2021 SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` remain **recorded claims**, not newly independently rehashed originals. Exact first-published 2022/2021 CFS three-month earnings binding, original-vs-amended fact lineage, precise public available-at and historical issuer/security mapping remain unproven.
- KRX 2017–2022 historical source SHA pair 1,565/1,565 archival integrity previously reported, but 90 uncertain session/source-gap classifications remain unresolved against independent original calendar/security-day PIT. Distinct prospective 2026-09-28 27 nonpositive-OHLC rows remain quarantined. Neither count is certified tradability.

## Railway read-only observations
- Production PIT rebuild service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`: one running replica, latest returned deploy-log record `2026-10-30T14:46:37Z`, `COMMON_OHLC_NONPOSITIVE`, independent source/model/chronology admissions false and live order false. Historical source evidence still fails closed; no 2026-10-31 runtime log was returned.
- REAL Kiwoom read-only service `93074d5f-70b3-48e4-8671-a3c5b23daf7e`: Railway deployment SUCCESS, but replicaStatus 0 running / 1 crashed, with no new verified login/WS success in returned logs. Do not infer readiness from displayed 'online' state.
- Railway environment-status returned pending staged patch ID `e113dacb-6705-4416-9997-dc694539d382`, but get-staged-changes returned `staged=null`; contradictory views, **no approval, deployment, or mutation**.

## Admission and economic gates
- No independently approved as-published M20 source PIT or historic per-security tradability; missing corporate actions, actual order/fill/slippage constraints, verified brokerage fees and account/ETF/security-specific taxes. Therefore a valid after-tax trade-level net P&L vector does not exist.
- **Do not compute, interpolate, or invent NetEV, PF, CAGR, MDD, ES95 or ES99.** M20 performance run remains **NO-GO** until all original-source, chronology, tradability, costs/taxes and fixed Frozen protocol gates pass. No replay or independent Holdout access.
- Frozen H5/M20, 504/126/126 walk-forward, purge20, Champion, Top3/no rank-4 backfill, independent sealed Holdout and `ORDERING=false` remain unchanged.
- No actual orders, funds, account/permissions, new provider calls, workflow reruns, Railway deployment, PR merge or Champion promotion. No other workstream code modified.

Next authorized work is evidence review only. Escalate only an independently attested new original/PIT gate, required external approval, or a material new blocker; routine repeats should not trigger a notification.
