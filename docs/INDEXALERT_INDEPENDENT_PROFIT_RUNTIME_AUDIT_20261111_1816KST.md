# IndexAlert independent gate and isolated runtime audit — 2026-11-11 18:16 KST

Scope: independent read-only evidence review. Not a source-PIT approval, financial performance run, deployment or order authorisation.

## GitHub source snapshot
- Research `index-alert-research-v1`: compare API base commit SHA `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1`: PR #420 base SHA `1e6367d2863a86c3470da13d81a955d277eba485` (current branch tip not separately independently fetched). Compare reports diverged, development ahead 1,148 / behind 281 relative to research.
- OPEN / draft PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All fetched directly from GitHub PR metadata this run.
- #414 gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`, read from #414 HEAD, blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Explicitly states M20 performance_run_authorized=false, H5/0-N NO-GO, no live orders.
- GitHub Actions jobs checked directly: 38381997417 6/6 SUCCESS; 38382214223 6/6; 38419111311 6/6; 38419649711 1/1; OpenDART 38419439742 2/2; KRX 38498552499 6/6. Job success is CI-only PASS; per-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` was NOT independently recomputed this run.

## Railway production (read-only)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild running 1/1; runtime running 1/1; KRX historical worker 0/1 (actual worker execution NOT VERIFIED); Kiwoom real read-only 0/1, crashed 1/1 (runtime FAIL).
- Backend, push and db-query-readonly offline; db-query-readonly 1 critical issue.
- Staged environment patch `e113dacb-6705-4416-9997-dc694539d382`, 0 changes; not applied.
- Deployment log query 2026-11-11 07:00–09:20 UTC: PIT 0, KRX 0, Kiwoom 0; runtime 101 returned records, including Investing.com USD/KRW HTTP errors and Yahoo fallback around 09:15 UTC. No source-PIT or economic approval inferred from those logs. Successful historical deployments are not proof of current replicas.

## Gate verdicts
| Gate | Verdict | Limitation |
|---|---|---|
| Existing KRX 2017–2022 1565/1565 weekday private raw-pair storage | HISTORICAL PASS only | Current independent original digest replay not performed; official calendar and trading state unapproved |
| OpenDART 2021/2022 first-filed original CFS 3-month operating profit, period, amendments and public available-at | NOT VERIFIED / FAIL-CLOSED | Historical 15 SGML candidate rows and numeric adjacency do not establish source semantics/PIT |
| Historical corp/security mappings, KRX official status, corporate actions, executable prices, tax and costs | NOT VERIFIED / FAIL-CLOSED | 90 uncertain days, 27 bad OHLC and 12003 zero-activity samples cannot be silently accepted |
| Offline optimisation #413/#418 CI | PASS (job success only) | Synthetic 34-case identity SHA not independently rehashed; runner 2.9656s vs concurrent suite 2.6209s = 1.1315x regression-phase, not overall speed-up |
| Post-tax annual risk-adjusted profitability, NetEV, PF, CAGR, MDD, ES95/99, date robustness, concentration | NOT VERIFIED | No approved official PIT M20 economic run |
| Kiwoom read-only live replica | FAIL | 0 running / 1 crashed; no account or auth changes permitted |

## Separate work lanes and next gates
1. Source owner: prove original filing, correct 2021/2022 three-month consolidated operating-profit semantics, original-versus-correction lineage, exact public available-at and historical security identity with source hashes. Do not backfill from amendments.
2. KRX owner: certify official calendar, historical statuses, corporate actions, executable prices, 90-day classification, 27 bad OHLC, 12003 zero-activity veto and fees/taxes independently.
3. Isolated optimisation owner: synthetic offline-only parity, fail-closed cache key combining approved original/data/calculation/Frozen/runtime/evidence SHA-256, only parallel read-only postprocessing. Never parallel dependent retraining/capital transitions. No claims of official speedup without independent CI wall-clock evidence.
4. Integrator: maintain original Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE; no post-hoc holdout recycling. Only after independent source+market PASS consider separately authorised one-time M20 net-of-cost/tax validation.

ORDERING=false. No economic experiments, strategy search, merges (#413/#414/#418), workflow edits, deployments, account changes, Champion promotion, money transfers or orders. This audit creates only a new document on an isolated branch. All unverified gates remain blocked.
