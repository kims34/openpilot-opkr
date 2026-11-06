# IndexAlert independent profitability and runtime audit — 2026-11-06 11:25 KST

Scope: read-only source/CI/Railway review; no live trading, no model search, no economic M20 execution, no merge or deployment. This document is isolated from PR #413/#414/#418 and other workspaces.

## Verified source identity
- research branch HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development branch HEAD: `1e6367d2863a86c3470da13d81a955d277eba485`
- PR #412: OPEN Draft `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- PR #413: OPEN Draft `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- PR #414: OPEN Draft `18c5418d9684d1717df58261ea27f28e514385b2`; gate document blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`
- PR #418: OPEN Draft `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- KRX PR #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f` (all OPEN Draft).
- API evidence: https://api.github.com/repos/kims34/openpilot-opkr/pulls/414 and corresponding branches/PR endpoints.

## CI read-only checks (actual API run and job responses)
- Actions 38381997417 (HEAD 55e7fe2b3fe322e39f817914ff1ed5b589bbe0da), 38382214223 (05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56), 38419111311 (b22e4f39517c2bc38e173e63e8fd52f29a535dad): SUCCESS, 6/6 jobs each.
- 38419649711 (8f363b8683d34a48754916b34810a5a8bb958896): SUCCESS 1/1 job.
- OpenDART 38419439742 (39af5b0043e122bc0e42935d8813759ff6c1a6e7): SUCCESS 2/2 jobs; original-filing semantic meaning and public available-at NOT VERIFIED.
- Chronology Anchor 41515392296 (f17283d9a5f0427c3d5b8a865d39455f92ee2f1d): FAILURE (auto-anchor), validation SKIPPED.
- Prior 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and 2.9656/2.6209=1.1315x regression-phase timings are historical evidence, NOT independently recalculated in this run. Full CI or real-market speedup NOT VERIFIED.

## Railway production (read-only, 2026-11-06)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS, replica 1/1; no deploy logs since 00:00Z in queried window.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS, running 0/1 (cron/idle), no deploy logs since 00:00Z.
- Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: SUCCESS 1/1; 02:25:42Z logs include Investing.com USD/KRW HTTP errors then Yahoo fallback, not official PIT evidence.
- Backend, Push, db-query-readonly offline; db-query-readonly critical 1. Kiwoom real-readonly displays online but replica 0 running / 1 crashed.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` exists, no application attempted.
- Historical 27/803 nonpositive OHLC condition: current resolution NOT VERIFIED; no new PIT/KRX logs this window.

## Gate decisions and blockers
- KRX 1565/1565 weekday raw pairs: historical storage integrity PASS only; official calendar, security state, corporate actions, tradability, costs/taxes NOT VERIFIED.
- OpenDART 2021/2022 original three-month consolidated operating-profit period, correction lineage, original filing public available-at and historical entity/security mappings NOT VERIFIED.
- Chronology prospective anchor FAILURE; downstream validation SKIPPED. Official PIT admission FAIL-CLOSED.
- M20 horizon20/purge20 WF504/126/126 and H5 Frozen, CPCV/independent Holdout/Champion/Top3/NO_TRADE unchanged. Holdout previously consumed: no independent reuse.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness after actual trading costs and taxes: NOT VERIFIED, not executed.
- Optimization: offline CI safety PASS within observed job scope; cache only on complete independent SHA-256 evidence equality and fail-closed; parallelize read-only post-processing only. End-to-end speedup NOT VERIFIED.
- Decision: **M20 NO-GO; ORDERING=false policy (actual live variable not independently read)**. No orders, fund transfers, privilege changes, promotion, merge, deployment or workflow edits.

Next safe checks: obtain authoritative original filing available-at and period/correction lineage, official KRX trading calendar/state/corporate action evidence, independent evidence SHA and chronological anchor resolution; re-run only allowed offline synthetic checks, never economic M20 before source PIT approval.
