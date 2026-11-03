# IndexAlert independent profitability and isolated runtime audit — 2026-11-03 15:19 KST

## Scope and immutable authority
Read-only GitHub PR metadata, actual Actions job statuses, Railway deployment inventory and runtime logs. No official M20 performance trial, market-source replay, broker order, capital movement, merge, deployment or workflow edit. Frozen H5/M20, horizon20/purge20, WF504/126/126, Holdout, Top3/NO_TRADE, cost/tax and Champion rules unchanged; ORDERING=DISABLED.

## Source references verified this cycle
- Research baseline: PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a` (historical PR base, **not** independently acquired current research branch HEAD). Prior audit reports research HEAD `bba25477b41fcd0a8beca78168abb0009fb5b82c`; NOT VERIFIED fresh.
- Development: Railway KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` commit `1e6367d2863a86c3470da13d81a955d277eba485`; deployed commit, **not** independently acquired current branch HEAD.
- Draft #414 head `18c5418d9684d1717df58261ea27f28e514385b2`; Draft #418 head `2f98401cc50a6c6a25808a98516efd5bf0c944ee`. Draft #412/#413/#420/#422/#423 open, unmerged; metadata read this cycle. #422 head `c14857620973531013799e44625d43080904fd5f`; #423 head `0e38004363cac9fc4475556b3a1c445de9af407f`.
- GitHub Actions #38419111311: 6 jobs SUCCESS; #38419649711: 1 job SUCCESS; #41515392296: auto-anchor FAILURE on public payload fetch, validation SKIPPED. These are real job status reads, not fresh recomputation of artifact SHA or 34-case parity.
- Prior pinned offline testcase SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is historical evidence only. Prior #418 single-runner serial 2.9656s vs concurrent 2.6209s (serial/concurrent 1.1315), not end-to-end CI/backtest speedup.
- Railway IndexAlert production: historical KRX worker latest inventory shows SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`; prospective PIT service read-only runtime logs show session 2026-11-02 `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, `session_manifest_sha256=null`, `FAIL_CLOSED`, `ORDERING=DISABLED`; last inspected entries at 2026-11-02 12:16 UTC, not proof of subsequent recovery. Separate Kiwoom real-readonly log shows TOKEN_OR_LOGIN_AUTH code 8050, WS_CONNECTED=false, ORDERING=DISABLED; deployment SUCCESS is not token success.
- Prior anchor Action failure and Railway 404 remain unresolved; this cycle's limited HTTP sample does not prove recovery. No response body or private anchor store inspected.

## Gate decision
| Gate | Decision | Reason |
|---|---|---|
| 2017–2022 KRX private raw pair integrity | historical scoped PASS | 1565/1565 weekday SHA pairs reported previously; not rehashed in this run |
| Official market sessions, security historical status, corporate actions, fills, taxes | NOT VERIFIED | 90 gaps, 12003 zero activity and prospective 27 OHLC exclusions do not certify historical tradability |
| Original-filing 2021/2022 3-month CFS operating profit, correction lineage and intraday available-at | NOT VERIFIED | original SGML candidate shapes and archive hashes do not establish exact period semantics or PIT |
| Issuer/security historical mapping | NOT VERIFIED | no independent original dated map |
| PR #413 synthetic software parity | historical limited PASS | Actions success, historical pinned testcase digest; fresh digest not recomputed |
| PR #418 archived manifest integrity | FAIL-CLOSED (previous evidence) | mismatch not shown repaired; fresh manifest digest not independently recomputed |
| Full CI / official backtest acceleration | NOT VERIFIED | only synthetic timing evidence |
| M20 net annual risk-adjusted profitability (NetEV/PF/CAGR/MDD/ES95/99/concentration/robustness) | NOT EVALUABLE / NO-GO | PIT, tradability, costs and independent holdout gates not admitted |

## Next safe work
1. Independently read latest research and development refs and precise PR #413 HEAD, then pin all current commit SHA and document source lineage.
2. Inspect official original-filing semantic 3-month CFS 2021/2022 and exact publication timestamp/correction history; no amended backfill.
3. Resolve official dated KRX market calendar, historical security/day statuses, corporate actions, fillability and cost/tax proof without removing problematic samples to force PASS.
4. Recompute offline parity SHA and archived manifest under pinned CI evidence only; keep cache fail-closed and parallelize only independent read-only post-processing. No M20 economic run until all source gates independently PASS.
