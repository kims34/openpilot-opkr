# IndexAlert independent profitability / isolated runtime evidence — 2026-10-28 08:18 KST

> Documentation-only, read-only evidence review. No source/PIT admission, M20 economic execution, Holdout, model search, trading, deployment, merge, workflow modification or Champion promotion. ORDERING=false remains mandatory policy, not a verified production configuration.

## Immutable read targets at this check

| Target | GitHub HEAD SHA |
|---|---|
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` |
| Draft PR #414 integration | `77a2202dd2048d7524dcc3219c4f3ea45a838162` (pre-audit HEAD) |
| Draft PR #413 isolated runtime | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` |
| Draft PR #418 isolated one-runner | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` |
| Draft PR #412 OpenDART | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` |
| KRX specialist | `073d2d49e95f69fb10b943b93e51bb179fb3c698` |
| KRX Draft #420 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` |
| KRX Draft #422 | `c14857620973531013799e44625d43080904fd5f` |
| KRX Draft #423 | `0e38004363cac9fc4475556b3a1c445de9af407f` |

All specified PRs remain Draft and unmerged at the read. Latest repository Actions list observed through 2026-10-27 20:03 UTC (2026-10-28 05:03 KST).

## New independent first-party market-scope check (important negative evidence)

Directly fetched the following KRX-hosted KIND documents as *public first-party page text*, not cryptographically pinned publication-time originals:

1. [2021-08-04 KOSPI / 유가증권시장 closure notice](https://kind.krx.co.kr/external/2021/08/04/000158/20210804000347/99340.htm): explicitly covers **2021-08-16**, including listed cash securities. This supports only its named market/day and does **not** prove source snapshot vintage, each stock's trade status or private stored 2021 empty-day set.
2. [2021-09-27 KOSDAQ closure notice](https://kind.krx.co.kr/external/2021/09/27/000113/20210915000217/71985.htm): explicitly covers **2021-10-04 and 2021-10-11**, but its target market is **KOSDAQ**, not the private historical worker's **KOSPI**. **FAIL for cross-market KOSPI authority if offered as such**; not a claim that KOSPI traded on these dates.
3. [2022-02-10 KOSDAQ election closure notice](https://kind.krx.co.kr/external/2022/02/10/000126/20220209001809/71985.htm): explicitly covers **2022-03-09 and 2022-06-01**, but **KOSDAQ only**. **FAIL for cross-market KOSPI authority if offered as such**.

These original-page *market scopes* independently confirm the fail-closed cross-venue distinction already represented in KRX specialist PR #423's synthetic tests. They do not prove a missing KOSPI notice does not exist. No newly admitted 2021/2022 KOSPI date, official exchange calendar/PIT, security-day tradability, corporate action or fill authority. The actual original Railway 2021 13-date and 2022 14-date sets have **not** been directly compared here.

## Official source / safety evidence

- OpenDART [2021 first-original Actions #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official job `121379096007`: source ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` PASS for byte identity; original 2021 Q3 3-month consolidated operating-income cell, 2022 comparator, full correction lineage, publication instant and issuer/security PIT **NOT VERIFIED**. Earlier 2022 original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` remains historical byte-identity evidence only.
- KRX historical private 1,565/1,565 daily/master weekday pair storage hash audit previously PASS, but 90 unresolved calendar/source-gap dates, 12,003 zero-activity observations, 27 quarantined nonpositive OHLC, official stock state and corporate actions remain **NOT VERIFIED**. [KRX #423 Actions #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) job `119612335677`: **32 synthetic tests PASS**, `DRY_RUN_NO_PRIVATE_STORAGE_READ`, `2022_private_candidate_date_sets_equal=false` (not an actual private comparison).
- Latest [watchdog #40574617617](https://github.com/kims34/openpilot-opkr/actions/runs/40574617617), job `122437575718`: read-only synthetic governance tests PASS; actual log `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is not a production config or official profitability proof.
- Latest [prospective anchor #40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813), job `122295113858`: `/anchor/latest` request ended HTTP **404**, validation job skipped. Chronology admission FAIL / missing prospective evidence.

## Isolated runtime optimization — no new performance claim

- [#413 Actions #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 6/6 jobs successful, immutable 34-case identity/outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` exact PASS; serial 1.7650s vs longest parallel 2.7079s, **0.6520x**, negative regression-phase speed result.
- [#418 Actions #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562): same 34-case digest PASS, single-runner subprocess group 2.3911s serial vs 2.0755s concurrent = **1.1521x** only for the measured process segment. Full CI and admitted-market backtest speedup **NOT VERIFIED**. [Candidate source #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) still lacks complete transitive dependency pinning/merge authority.
- Fresh GitHub compare PR #413 HEAD to #418 HEAD: `diverged`, 49 ahead / 18 behind, merge base `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`. Neither synthetic parity nor local cache/hash receipt authenticates upstream official PIT admission or combined latest source tree.
- Cache requires independently authenticated source/data/code/Frozen/runtime/evidence SHA-256 and fail-closed exact equality. Only independent read-only postprocessing may be parallelized; never dependent refit or capital transitions.

## Railway read limitation and final decision

A fresh read-only Railway `list_projects({})` attempt returned `User input required but current turn is running in a non-interactive mode.` No bypass or credential/permission modification. Latest deployment, runtime logs, exact private 2021/2022 day-set comparisons, prospective endpoint root cause and actual live `ORDERING` **NOT DIRECTLY VERIFIED**.

**M20 original PIT: NO-GO. M20 profitability RUN: NO-GO.** Annual post-fee/tax risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, return concentration and time robustness: **NOT EVALUABLE**. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, sealed/consumed Holdout, Champion/Top3/NO_TRADE, cost/tax/fill/risk/promotion rules remain immutable. No production write or live trade.

Next allowed evidence: independently authenticate **KOSPI** original calendar notices by market and as-of time, privately compare exact stored day sets with authorized Railway read access, prove original 2021/2022 Q3 3-month CFS operating-income lineage and publication instants, establish issuer/security historical mapping and stock-day tradability, and audit complete runtime transitive dependency SHA. Only synthetic/offline safety validation before PIT admission.
