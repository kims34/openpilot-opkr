# IndexAlert independent read-only gate — 2026-10-25 18:46 KST

Scope: profitability independent evidence review only, not authorization or performance execution. No data acquisition, official market backtest, Holdout use, broker interaction, code/workflow edits, deployment, merge or Champion promotion. This document is an isolated note; other owners retain their code/experiments.

## GitHub pinned heads (connector reads in this check)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Integration Draft PR #414: `74dd339d4b21b27f020522617ca7d6da0895dc6d` (this is the head before this note); integration gate document Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Runtime Draft #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- One-runner Draft #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422: `c14857620973531013799e44625d43080904fd5f`; #423: `0e38004363cac9fc4475556b3a1c445de9af407f`. All remain open/draft.

## CI evidence freshly read
- Latest listed repository workflow #40167777488, 2026-10-25 06:04 UTC: SUCCESS, job `121092240087`. Log explicitly: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; artifact ZIP logged SHA-256 `c0f90b91564348a8c958edab0ffcc958f5dcc7004e01a9aa2b89ae9935dd8b8b`. This is CI-only, **not** live Railway proof.
- KRX #420 run #39714369438, #422 #39001836000, #423 #39714207925: selected synthetic/no-provider jobs SUCCESS. These do not establish original protected-volume day sets, trading state or fillability.
- OpenDART #412 runs #39884427765 and #39884427805: offline-only jobs SUCCESS; original 2022 document SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` is a previously reported identity receipt, not new 2022/2021 first-public financial semantics.
- Runtime #413 run #38508247773: six jobs SUCCESS; prior pinned 34-case parity SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; serial 1.7650s versus parallel 2.7079s in that run, no full-CI/market speed proof.
- Runtime #418 #39111405478: immutable archived case job FAIL (prior code blob mismatch), do not re-pin old archive or merge.
- Prospective chronology anchor #39972035700: failed with HTTP 404 at `/anchor/latest`; historical prospective continuity NOT VERIFIED.
- Railway `list_projects` read failed because interactive authentication was required in this non-interactive run. No bypass or further authentication. Live deployment, logs and actual ORDERING state NOT VERIFIED.

## Decision (original SHA / source PIT / economics)
- **PASS, limited:** directly retrieved branch/PR refs, selected CI job outcomes, synthetic offline parity; prior OpenDART original ZIP and KRX storage-only SHA receipts within their recorded scope.
- **FAIL:** #418 archived code identity check; chronology anchor continuity.
- **NOT VERIFIED:** exact original-first-filed 2022/2021 July–September 3-month consolidated operating-profit account/period/sign/units, exact public available-at and full amendments; historical issuer/security as-of identity; official KRX calendar/halts/delist/corporate actions/invalid OHLC resolution/actual fills; fees, slippage and taxes; after-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness, lot feasibility; full-backtest acceleration and actual Railway order state.
- **NO-GO:** M20 source/PIT admission and profitability run. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE and original risk/cost gates unchanged. H5 consumed Holdout and Dynamic posthoc results cannot be independently reused. `ORDERING=false` is required, **not independently attested in production**.

Next: source owners must supply independently checkable first-public OpenDART semantic/PIT receipt and KRX private official as-of tradability/corporate-action/fill-cost/tax evidence; restore authorized read-only Railway observability without changing credentials or permissions in this audit. Never use synthetic PASS as an M20 economic approval. No other owner code or PR was changed.
