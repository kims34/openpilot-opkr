# IndexAlert independent read-only gate — 2026-10-26 20:49 KST

Scope: independent re-attestation only, following existing 20:23 KST audit. No specialist code edits, market-source acquisition, profitability run, strategy/model changes, Holdout access, PR merge, workflow change, deploy, account/permission/funds change or orders.

## Immutable refs inspected

- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft integration PR #414 pre-write HEAD `2324ae211eef3c66d56f32f0550af74ba28ee530`; core gate blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Prior audit doc `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-26_2023KST.md` blob `f202601a14852b79f63c4c06855234b43fa63cfa`.
- OpenDART Draft #412 HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; optimizer Draft #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; independent runner Draft #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Drafts #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`; #404 closed.

## This run's direct log-level checks (no new source admission)

- [Read-only Watchdog #40278112152](https://github.com/kims34/openpilot-opkr/actions/runs/40278112152), job `121425140550`, success on HEAD `04bdfc93975bb59961f1cb3bd3598d04f8e7bff4`. Log explicitly states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded artifact `12630449536` ZIP SHA-256 `f5b5feae6c656e6ab3479c8b6b84f41d157dca337ba2d47fe4e35a8c5a9fa347`. These are test/attestation boundary indicators, not live Railway configuration.
- [OpenDART #40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758), job `121379780273`, 13/13 offline first-viewer TOC safety tests PASS; `m20_feature_pit_admitted=False`, `m20_performance_run_authorized=False`, `ordering=DISABLED`. Synthetic software test only, no real original CFS financial-cell proof.
- [2021 official first-original source #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), job `121379096007`, original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; 1 SGML, 1,728 table shapes, 13 lexical operating-label candidates, 0 same-table strict three-month/period matches. Artifact `12625042488` ZIP SHA-256 `3fe75e2af23f508d3c518a14e98732a399eb0daeca46cccd7b3191b1e2e4777b`. Original archive identity PASS; 2021/2022 CFS 3-month earnings, corrections and earliest public available-at NOT VERIFIED. 2022 first-original historical pinned SHA `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` not re-downloaded.
- [KRX #423 #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677`, 32/32 offline tests PASS; actual `DRY_RUN_NO_PRIVATE_STORAGE_READ` and `official_market_status_admitted=False`. No authoritative private 14-day date-set match or KOSPI trading-state proof. Prior 1,565/1,565 stored weekday pairs are storage-only historical evidence; 90 calendar/source gaps and 27 bad OHLC require source-owner resolution.
- [Optimizer #413 #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): historical pinned 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; serial 1.7650 s, parallel 2.7079 s, ratio 0.652x (slower). [Runner #418 #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archived source-blob identity FAIL (expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`). Exact wheel/OS dependency closure, full CI and real approved backtest speed NOT VERIFIED. No re-pin, cache admission, or merge.

## Railway read-only access boundary

Railway `list_projects` returned `User input required but current turn is running in a non-interactive mode`. No bypass or second attempt. Current production deployments, log evidence, and effective `ORDERING=false` are **NOT VERIFIED THIS RUN**; the latter is a mandatory safety policy, not a live setting attestation.

## PASS / FAIL / NOT VERIFIED, decision

- **PASS (narrow)**: pinned 2021 source ZIP SHA integrity and offline source-shape; offline viewer/market guard tests; archived 34-case test outcome digest.
- **FAIL-CLOSED**: #418 archived blob-identity gate; unapproved M20 source/PIT and market admission.
- **NOT VERIFIED**: first-public original-filing available-at; 2022/2021 first 3-month consolidated CFS operating-profit cell and correction lineage; historical issuer/security identity; official KRX sessions/trading state/CA/fills; costs, slippage, tax; after-tax NetEV, PF, CAGR, MDD, ES95/99, profit concentration, temporal robustness and annual risk-adjusted profitability; Railway effective ordering state.
- **M20 performance execution = NO-GO.** No official market performance run, strategy search, new economic experiment, posthoc H5/Dynamic adjustment, spent Holdout reuse, Champion/Top3 change, or promotion. Preserve Frozen H5; M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, precommitted cost/tax/risk thresholds. Require `ORDERING=false`.
- Cache only if independently approved source/data/code/Frozen-policy/runtime/evidence SHA-256 closure matches, otherwise fail closed; parallelize only independent read-only post-processing, never dependent training or capital transition.

Next owner-separated evidence: OpenDART original CFS cell + publication instant and amendments; KRX original historical market/CA/fill proof; optimizer full transitive source/runtime closure and synthetic whole-CI timing; integration independent economics only after all gates. No substantive newly admissible financial evidence was found beyond the 20:23 KST audit.
