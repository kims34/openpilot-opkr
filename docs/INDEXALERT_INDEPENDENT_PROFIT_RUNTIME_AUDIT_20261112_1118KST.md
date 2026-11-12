# IndexAlert independent audit — 2026-11-12 11:18 KST

Scope: read-only GitHub/Railway cross-check, documentation-only isolated evidence. No strategy, data, workflow, CI, production, order, permissions or Champion changes. Historical claims remain separated from fresh verification.

## Immutable source references
- Research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406` (self compare identical).
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (self compare identical).
- Draft/open/unmerged PR HEAD: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 integration gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (fetched from PR branch, not research base).
- GitHub Actions job outcomes freshly checked: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. Individual job logs, artifacts and frozen 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` NOT independently recomputed this run.

## Railway production evidence (read-only)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest deployment statuses: runtime SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`; PIT rebuild SUCCESS `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`; KRX worker SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c`; Kiwoom real-readonly SUCCESS `a77fb922-b679-4d88-92c4-03054ec579cd`. These are latest deployment records, NOT live replica health attestations (replica counts null in status response). Backend and push latest deployments FAILED; db-query-readonly has no deployment.
- For 2026-11-12 01:30–02:20 UTC, PIT rebuild, KRX worker and Kiwoom real-readonly deploy logs yielded zero records; absence of logs is not health PASS. Runtime returned 41 log entries including USD/KRW Yahoo live quote and KOSPI market quote at 02:18 UTC. No trading permission inferred.
- Environment `stagedChanges=null`, but `pendingWork` contains staged patch `e113dacb-6705-4416-9997-dc694539d382` with empty changes. Left untouched; status inconsistency NOT VERIFIED.

## Admission matrix
| Domain | Decision | Reason |
|---|---|---|
| KRX 2017–2022 1565/1565 weekday raw-pair storage | PASS (prior pinned integrity only) | No fresh private raw SHA recomputation; official calendar, 90 uncertain days, 12003 zero-activity rows and 27 invalid OHLC entries remain excluded |
| Original 2021/2022 DART source byte fingerprint | PASS (prior source-only evidence) | Prior 2021 SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; 2022 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; not freshly recomputed |
| First-original 2021/2022 consolidated 3-month operating income period, correction lineage, exact public available-at/PIT | NOT VERIFIED | SGML candidate/adjacent signature is not semantic period and timing approval; 2021 previous 13 candidates / 0 exact explicit 3-month same-table matches |
| Historical issuer/security mapping, KRX market status/corporate actions/executability and costs/taxes | NOT VERIFIED | No independent complete official PIT chain |
| Annual after-cost/after-tax risk-adjusted NetEV/PF/CAGR/MDD/ES95/ES99/concentration/temporal robustness | NOT VERIFIED | Official M20 economic run prohibited; archived H5 and 0-N NO-GO, consumed holdout not reusable |
| PR #413/#418 isolated offline CI | PASS (CI job outcomes only) | Synthetic checks not market profitability proof; regression phase 2.9656s serial vs 2.6209s concurrent = 1.1315x; full CI/official backtest acceleration NOT VERIFIED |
| Live replica health, ORDERING runtime value | NOT VERIFIED | Deployment success does not imply live health; do not claim operational flag verification |

## Frozen constraints and next steps
M20 NO-GO. Keep H5 frozen, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, original costs/taxes/NetEV/execution/risk/promotion rules unchanged; ORDERING=false required, no real orders. Cache only when independently approved original/data/code/Frozen/runtime/evidence SHA-256 all match (fail-closed). Parallelize read-only post-processing only, never dependent retraining or capital transitions. Next: obtain independent exact first-filing period/timestamp lineage and official KRX session/tradeability mapping; independently verify frozen synthetic test digest and inspect replica health without changing service. Do not rerun H5 holdout or conduct M20 economic experiment, merge PRs, modify workflows, deploy, trade, move funds or promote Champion without separate authorization.
