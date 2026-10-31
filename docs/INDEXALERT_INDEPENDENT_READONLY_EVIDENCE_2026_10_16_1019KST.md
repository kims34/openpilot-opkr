# IndexAlert independent read-only evidence checkpoint — 2026-10-16 10:19 KST

Status: **NON-ADMITTING, NO MERGE, NO DEPLOY, NO TRADING**. Documentation-only, separate from the existing profitability integration gate and other specialist code paths.

## Exact GitHub refs read through connected GitHub API
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft PR #414: `3cee2cbcf97818fea51e498329cf3cb81a825340`, unmerged.
- Draft PR #412 OpenDART: `6a4550de4a46e5e3e5bf8c7aff232af5f675d249`, unmerged.
- Draft PR #420 KRX: `851762a7ecc029337bb7b3b568dfd65ef82ec68c`, unmerged.
- Draft PR #413 runtime: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, unmerged.
- Draft PR #418 isolated runner: `c9b125ff5d3d080848dd9ab1f23a8755af4faaa9`, unmerged; base is #413 branch, not research.

## Latest matching HEAD Actions read-only
- OpenDART #412: runs [38822687826](https://github.com/kims34/openpilot-opkr/actions/runs/38822687826) (12 synthetic tests) and [38822687857](https://github.com/kims34/openpilot-opkr/actions/runs/38822687857) (13 synthetic tests) SUCCESS. Neither proves first-original 2022/2021 Q3 CFS profit/3-month period binding, full amendment lineage, intraday public available-at, or issuer/security historical PIT.
- KRX #420: runs [38821830289](https://github.com/kims34/openpilot-opkr/actions/runs/38821830289) and [38821830295](https://github.com/kims34/openpilot-opkr/actions/runs/38821830295) SUCCESS synthetic only (2021 holiday 6 tests). No real private-day reconciliation/official trade-status admission.
- #413 [38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs SUCCESS; pinned archived 34-case identity/outcome SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` remains historical comparator.
- #418 [38822156136](https://github.com/kims34/openpilot-opkr/actions/runs/38822156136) FAIL CLOSED at original source blob check, later tests skipped. [38822156164](https://github.com/kims34/openpilot-opkr/actions/runs/38822156164) candidate source lineage 22 direct files PASS, 34-case pinned SHA PASS, `candidate_approved_for_merge=false`; upstream exact HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`. [38822156116](https://github.com/kims34/openpilot-opkr/actions/runs/38822156116) one-runner 34-case parity PASS, serial subprocess wall 2.5989 s vs parallel group wall 2.6011 s, no demonstrated speedup. Candidate proof does not imply full transitive dependency closure, no-follow TOCTOU completeness or authorized source.
- #414 document-only draft: no commit-associated PR-triggered workflow runs returned.

## Railway read-only inventory and log evidence
- IndexAlert production staged patch: none; no deployments or configuration changes made.
- KRX historical worker deployed SUCCESS 2026-10-12, historical private capture 2017–2022 1565/1565 weekday source pairs, 90 unresolved exchange-calendar/source-gap days. The stored aggregate digest `e2503a3bc623d4386e5783ec19272916fe6abba9bc191c14040d2c0831c7f01a` is a *logged fingerprint*, not a freshly recomputed raw-byte hash by this audit.
- KRX 2023–2026 984/984 weekday source pairs, 66 unresolved calendar/source-gap days, 19060 zero-activity OHLC rows, one additional abnormal row; aggregate log fingerprint `be12af649926d95a9694381e41f3dffa0add637b72fd46fe1e7aed9a407499a0`.
- PIT read-only logs through 2026-10-15 14:01 UTC repeatedly reject 27 common-stock nonpositive OHLC rows tied to 2026-09-28, `status=FAIL_CLOSED`, `ordering=DISABLED`. No fresh source admission.
- Railway environment health lists kiwoom-real-readonly running=0/crashed=1 despite overall service state marked online; do not treat as a healthy authenticated broker path.
- Service inventory `staged=null`. The runtime health of the KRX worker reported running=0/crashed=0/total=1; this does not establish an active running worker.

## Gate verdicts
| Requirement | Verdict |
|---|---|
| Historical private source storage checkpoint/integrity logs | PASS for reported pair counts only; independent raw-byte rehash NOT VERIFIED |
| Original OpenDART 2022 vs 2021 3-month consolidated operating profit, correction lineage and exact public available-at | NOT VERIFIED |
| Issuer/security historical mapping | NOT VERIFIED |
| KRX historical official exchange sessions, halts, delists, corporate actions, fillability | NOT VERIFIED |
| Realistic trading costs, taxes and execution model | NOT VERIFIED |
| Net EV / PF / CAGR / MDD / ES95 / ES99 / concentration / regime robustness | NOT VERIFIED — no authorized profitability run |
| #413/#418 offline synthetic parity | PASS where matching pinned 34 cases |
| #418 original immutable source comparison | FAIL CLOSED by design |
| #418 candidate partial lineage audit | PASS limited to 22 direct files, NOT VERIFIED for complete transitive closure |
| End-to-end CI / real backtest speedup | NOT VERIFIED |
| M20 PIT admission, performance run, independent Holdout reuse, Champion promotion | BLOCKED |

## Next permissible steps (owner-isolated)
1. OpenDART specialist: independently bind *same original table* to exact 2022/2021 standalone three-month CFS operating-profit facts, corrections and public available-at; record immutable original bytes/SHA. Do not run M20.
2. KRX specialist: reconcile 90 historical days and 27 quarantined 2026 rows to authenticated official session/security status, plus historical mappings, actions, fills and cost/tax path. Do not promote source.
3. Optimization specialist: inspect #418 source-open/TOCTOU and complete dependency/workflow trigger coverage with offline-only synthetic controls; keep #413/#418 unmerged and reject any claim of speedup absent full CI evidence.
4. Profitability orchestrator: only after independent source PIT approvals and frozen evidence ledger PASS may an explicitly authorized preregistered M20 economic run be considered; no H5 consumed Holdout replay or dynamic ex-post adjustment.

Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, cost/tax/NetEV/fill/risk/promotion gates unchanged. `ORDERING=false`. No orders, funds, permission changes, deployments, PR merges, model exploration or performance trials were attempted.
