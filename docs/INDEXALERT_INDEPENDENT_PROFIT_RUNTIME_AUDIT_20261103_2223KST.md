# IndexAlert independent evidence audit — 2026-11-03 22:23 KST

Read-only source inspection. No PIT approval, performance execution, strategy modification, deployment, merge, trading or credentials change.

## Exact refs independently retrieved
- research index-alert-research-v1 HEAD df474df348f22aa38b1dedaa59fcff66e548b406 (compare identical).
- development index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485 (compare identical).
- Draft OPEN PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee.
- KRX Draft OPEN #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- #414 gate document fetched from PR head; blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be. This is a policy/evidence integration document, not approval.

## CI and runtime
- GitHub Actions jobs API: 38419111311 six success; 38419649711 one success; 41515392296 auto-anchor failure and validation skipped. The old 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic tests and 2.9656s/2.6209s benchmark are inherited evidence, not recomputed in this run. Actual full backtest speedup NOT VERIFIED.
- Railway project d1c1a050-b7d6-41ce-b300-13c20f82a20a; KRX historical-worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, commit 1e6367d2863a86c3470da13d81a955d277eba485. Successful deployment is not historical market tradability proof.
- Railway pit-rebuild latest deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS but runtime error COMMON_OHLC_NONPOSITIVE persisted through 2026-11-03T13:16:18Z. Fail closed; no admission. Runtime alert logs are operational context only, not performance proof.

## Verdicts and blockers
- Storage integrity of 1565/1565 weekday source pairs: historical PASS limited to storage, not rehashed this run.
- Original filing, precise public available-at, 2021/2022 first three-month consolidated operating profit period and correction lineage, historical issuer/security mapping: NOT VERIFIED.
- Official KRX calendar, status, corporate actions, fillability, fees and taxes: NOT VERIFIED; zero-activity and OHLC errors excluded from admission.
- Chronology Anchor Action 41515392296: FAIL; downstream validation SKIPPED.
- PR #413/#418 synthetic regression CI: limited PASS; archived manifest SHA mismatch unresolved, complete speedup NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness and after-tax annual risk-adjusted return: NOT EVALUABLE; M20 NO-GO.

## Next safe steps
Reconcile original-filing period/available-at lineage with independent original artifact hashes; obtain official KRX session/state/corporate-action and execution-cost proofs; resolve chronology-anchor HTTP retrieval and manifest SHA mismatch via owning teams. Until then synthetic offline policy-only checks, cache fail-closed on all approved SHA-256 provenance, parallelize read-only independent post-processing only. Frozen H5, M20 horizon20/purge20 WF504/126/126 and all selection/risk gates unchanged; ORDERING=false. No holdout reuse or dependent training/capital-transition parallelization.
