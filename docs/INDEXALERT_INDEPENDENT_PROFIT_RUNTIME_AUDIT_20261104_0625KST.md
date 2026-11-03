# IndexAlert independent profitability and runtime audit — 2026-11-04 06:25 KST

Scope: read-only GitHub/Railway verification. No M20, market-performance testing, deployment, merge, workflow mutation, or order.

## Evidence directly retrieved this run
- GitHub Actions job API: 38381997417, 38382214223, 38419111311 each six jobs reported successful in prior evidence; current first-page jobs returned success (full job counts not independently recounted). 38419649711 one job success. 38419439742 two jobs success. 41515392296 auto-anchor failed at public hash-only payload fetch; validation skipped.
- Prior 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and serial 2.9656 s / concurrent 2.6209 s are historical claims, NOT independently recomputed.
- Railway project d1c1a050-b7d6-41ce-b300-13c20f82a20a production: indexalert-pit-rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, commit 1e6367d2863a86c3470da13d81a955d277eba485 (deployment commit, NOT current branch HEAD); runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS. Since 2026-11-03 18:00Z PIT and KRX deploy logs returned zero entries, NOT proof of repair. Runtime logs at 2026-11-03 21:25Z show market quote checks, NOT PIT/economic authority.
- GitHub branch search returned independent-audit-20261104-0222kst and other historical audit branches; GitHub issue search returned no matching PR metadata. PR #412/#413/#414/#418 and KRX PR HEAD/Draft statuses are NOT independently verified this run. Research and development latest HEAD NOT VERIFIED. Attempts to fetch README and gate file returned 404; do not infer branch absence from file 404.
- OpenDART candidate SGML 15-row signature and KRX 1565 weekday raw pairs are historical user-supplied evidence, not freshly hash-audited.

## Gates
- Original-filing and public available-at PIT, 2021/2022 first-three-month consolidated operating profit period/correction lineage, historical issuer/security map: NOT VERIFIED.
- Official KRX calendar/status, corporate actions, executable fills, taxes/costs: NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/ES99, concentration and temporal robustness after costs/taxes: NOT EVALUABLE; M20 NO-GO.
- Offline synthetic optimization job completion: limited PASS; integrity SHA and full CI speedup NOT VERIFIED. 1.1315x is a historical regression-phase ratio only.
- Chronology anchor: FAIL; downstream validation SKIPPED.
- Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, Champion/Top3/NO_TRADE, ORDERING=false, fail-closed SHA-256 cache, read-only postprocessing parallelism. No source PIT approval, no performance trials or economic runs.

## Next permitted actions
Independently resolve exact GitHub branch/PR HEAD via metadata API, fetch original filing chronology and correction lineage, inspect official KRX calendar/status and raw-source SHA, inspect chronology anchor failure; rerun only offline synthetic policy checks after isolated review. Do not merge PR #413/#414/#418 or alter deployment/workflow.
