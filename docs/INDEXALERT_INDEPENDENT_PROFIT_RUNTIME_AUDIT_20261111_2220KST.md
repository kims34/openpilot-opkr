# IndexAlert independent profitability / isolated runtime audit — 2026-11-11 22:20 KST

Scope: read-only verification of upstream GitHub, CI and Railway production. No new market return, model search, M20 economic experiment, broker operation, deployment, merge or workflow modification. This document is an independent snapshot, not approval.

## Verified GitHub refs
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (compare against ref: identical, ahead/behind 0/0).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (identical, 0/0). Research vs development diverged (281 ahead / 1148 behind when development is base).
- Draft/open/unmerged PRs (HEAD): #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` read from `refs/pull/414/head`. It explicitly states M20 no-go, KRX raw-storage-only PASS, OpenDART Q3 PIT fail-closed.
- Actions jobs confirmed successful: 38381997417 6/6, 38382214223 6/6, 38419111311 6/6, 38419649711 1/1, 38419439742 2/2, 38498552499 6/6. These are *CI job conclusions only*, not independent source PIT, market profitability, or end-to-end speed verification.
- Previously reported 34-case fixed test SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 additional synthetic cases: historical evidence, **not independently rehashed this run**. #418 run 38419649711 artifact list empty; no independent artifact rehash available. Serial 2.9656s / concurrent 2.6209s = 1.1315x regression-phase time ratio, not an end-to-end acceleration claim.

## Railway production — live read-only evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest service deployment metadata is historic; no deployment applied by this audit.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS, running 1/1.
- Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: SUCCESS, running 1/1; USD/KRW Investing HTTP error and Yahoo fallback observed.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS deployment, running 0/1 (not a verified healthy worker).
- Kiwoom real-readonly `a77fb922-b679-4d88-92c4-03054ec579cd`: SUCCESS deployment but running 0/1, crashed 1/1: runtime FAIL. No authority to restart or change broker settings.
- Backend and Push offline; db-query-readonly offline with one critical issue. Environment status has an existing staged patch with **zero changes**; left untouched.
- Logs scoped `2026-11-11T12:00:00Z`–`13:25:00Z`: PIT 6 error records at 12:01, 12:16, 12:31, 12:46, 13:01, 13:16 UTC, each `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`; `fresh_alpha_observation_admitted=false`, `funds_movement_authorized=false`, `independent_chronology_admission_verified=false`. KRX and Kiwoom deploy logs 0 in this interval (absence of log is not health evidence). Runtime active logs show provider fallback. Input admission FAIL-CLOSED; official KRX trading validity NOT VERIFIED.

## Evidence gate (scope-sensitive)
| Requirement | Status | Basis / remaining gate |
|---|---|---|
| 2017–2022 KRX 1565/1565 weekday private raw pairs | PASS **storage integrity only (prior evidence)** | Original pairs and SHA historically checked; official holiday/calendar and execution not implied |
| Original OpenDART SGML candidate rows | PASS **candidate signature only (prior evidence)** | Action 38419439742, 15 candidate rows; semantics/period/public timestamp not approved |
| First public filing / exact available-at / original vs corrected lineage / 2021 and 2022 first three-month consolidated operating profit | NOT VERIFIED | Independently reproduce source document, timestamp, accounting period and correction lineage with SHA |
| Historical corporate-to-security map and point-in-time identifiers | NOT VERIFIED | Time-indexed official mapping |
| Official KRX market state, corporate actions, fills, trading feasibility, fees/tax | NOT VERIFIED | Official calendar and state joined to source/decision timestamps; no price-only proxy |
| NetEV / PF / CAGR / MDD / ES95 / ES99 / return concentration / time-regime robustness, net of fees and taxes | NOT VERIFIED | M20 profitability run prohibited before PIT approval; H5 consumed/failed holdout cannot be reused |
| #413/#418 offline software safety and fixed CI job conclusions | PASS **jobs only** | Exact immutable 34-case content digest independently NOT VERIFIED this run |
| End-to-end CI speed or official backtest speedup | NOT VERIFIED | 1.1315x refers only to regression phase |
| Production PIT market-data admission | FAIL-CLOSED | Six consecutive COMMON_OHLC_NONPOSITIVE records; no admission |
| Kiwoom read-only runtime replica | FAIL | Crashed 1/1, even though deployment status SUCCESS |

## Strict unchanged controls / next permitted work
Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT, labels, Purged/CPCV, independent holdout, Champion/Top3/NO_TRADE, costs, taxes, fills, risk and promotion thresholds unchanged. ORDERING=false; M20 NO-GO. Never retune using consumed H5 holdout or Dynamic results. Only offline synthetic safety tests permitted pending independently approved original-filing PIT. Cache must fail closed unless source/data/code/Frozen policy/runtime/approval evidence SHA-256 all match; parallelise read-only postprocessing only, never dependent retraining or capital transition. Separate owners' working code untouched. No live orders, money movement, credential/account permission changes, Champion promotion, deploy, automatic merge or PR #413/#414/#418 merge.

Next: independently obtain official first-filing and correction lineage timestamps and exact period from source; independently validate official KRX calendar/state/corporate action/fill constraints and source SHA; then reconsider gate before *any* economic run. Separately compare #413/#418 immutable synthetic case files and digest against logs, and measure complete CI/runner performance using offline-only fixed workloads. Investigate production KRX nonpositive OHLC and crashed Kiwoom read-only replica by owner, without changing live settings.
