# IndexAlert independent read-only profitability gate — 2026-10-26 16:55 KST

Scope: an incremental audit after `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-26_1547KST.md`. No specialist edits, market backtest, new provider query, M20 run, holdout access, trading, permission, funds, deployment, workflow edit, or PR merge. **This is not source PIT or profitability admission.**

## GitHub refs read from authenticated connector

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft #414 `indexalert-profitability-integration-evidence-20261013`: `6f6f0649b268d48126588eeeca8b733a326b3be5`; primary integration gate file Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; prior independent 15:47 audit Git blob `7b095e88bae990bf08e2c67a78d4da9c61eddc85`.
- Draft #412 OpenDART: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; Draft #413 runtime: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; Draft #418 one-runner: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX specialist Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; dependent Draft #422 `c14857620973531013799e44625d43080904fd5f`; Draft #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. Adjacent flow #416 remains independently owned.

## Incremental direct CI job-log / artifact metadata cross-check

- [Watchdog #40278112152](https://github.com/kims34/openpilot-opkr/actions/runs/40278112152) job `121425140550` SUCCESS: 31 research-governance offline tests, explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Job log's uploaded ZIP SHA256 `f5b5feae6c656e6ab3479c8b6b84f41d157dca337ba2d47fe4e35a8c5a9fa347` matches Actions artifact #12630449536 `digest` exactly; expires `2026-11-02T06:08:58Z`. This is metadata-only, not live Railway configuration proof.
- [2021 first-original #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) job `121379096007` SUCCESS: original official ZIP SHA256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1 SGML, 1728 tables, 13 profit-label candidates, **zero strictly verified standalone 3-month CFS cells**. Uploaded artifact #12625042488 log SHA256 `3fe75e2af23f508d3c518a14e98732a399eb0daeca46cccd7b3191b1e2e4777b` matches Actions artifact metadata; expires `2026-11-02T03:13:26Z`. No 2022 original's 2021 comparator or available-at proof.
- [OpenDART TOC #40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) job `121379780273` SUCCESS with 13 synthetic tests; no official CFS earnings cell or PIT approval.
- [KRX #420 #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) job `119612852155` SUCCESS, synthetic 39+25+8=72 controls; actual private 2021 13-day and 2022 14-day day-set comparison **NOT VERIFIED**. Historical 2017–2022 1565/1565 private raw-pair SHA integrity is a previously recorded storage-only PASS, not freshly reread in this turn.
- [Runtime #413 #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs SUCCESS, 34 immutable case outcomes SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. Parity job `115670744341` reports serial 1.7650s vs parallel 2.7079s, **0.652x (slower)**; output ZIP artifact #11868941555 log digest `b5a14cc645b8c490ff8f1c4e5376524b3a67f5074531415ac899f5a6c0b72651` equals Actions metadata, expires `2026-10-28T03:50:19Z`. No full CI / official market backtest speedup.
- [Runtime #418 #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` FAIL: `research_v1_runtime_manifest.py` archived expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Archived source integrity gate remains binding. Exact wheel hashes/native runtime identity not verified. No re-pin or bypass.

## Railway live read boundary

Authenticated `list_projects` returned `User input required but current turn is running in a non-interactive mode.` No live project, service, deployment, log or live `ORDERING` value was retrieved. No authentication workaround or Railway write attempted. Live `ORDERING=false` **NOT VERIFIED**; it remains a mandatory operating constraint.

## Independent PASS / FAIL / NOT VERIFIED

- **PASS, narrow:** exact official 2021 source ZIP digest, metadata/log artifact digest consistency, offline safety regressions and 34-case synthetic parity; historical 1565/1565 KRX storage SHA PASS is inherited evidence only.
- **FAIL:** #418 archived source-implementation Git blob gate; any attempt to admit the #418 candidate as the archived exact implementation is rejected.
- **NOT VERIFIED:** original first 2022 and 2021 three-month consolidated operating-profit signed cells and 2022-original 2021 comparative, original first-public available-at/PIT and correction lineage, issuer-to-security vintage, actual KRX session/halts/CA/stock-level tradability/fill, costs/fees/taxes/slippage, after-tax NetEV/PF/CAGR/MDD/ES95/ES99, concentration/temporal robustness, independent risk-adjusted annual net profitability, complete runtime SHA transitive closure and production ORDERING.

**NO-GO:** M20 official profitability or new strategy/performance tests. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, sealed and spent Holdout restrictions, Champion/Top3/NO_TRADE, fixed costs/taxes/NetEV/fill/risk/promotion gates. Cache fail-closed unless independently approved original/data/calculation/Frozen/runtime/authorization evidence SHA256 all match; parallelize only independent read-only postprocessing, never dependent refits/capital transitions. `ORDERING=false` required. No orders, money, account/credential/permission changes, deploy, merges, Champion promotion.

Next independent source-owner proofs: #412 first-edition numeric CFS cells with exact first public time and correction-vintage binding; KRX source-owner official original day/security/CA and actual private set read under separately authorized existing read-only method; authenticated Railway read-only session to attest current live ORDERING without altering permissions. Existing specialist code and workflows untouched. No newly admitted economic evidence since prior audit.
