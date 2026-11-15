# IndexAlert independent audit — 2026-11-15 10:23 KST

Scope: read-only GitHub Actions and Railway; no live trading, deployment, merge, or market-economics run.

## Fresh direct evidence
- GitHub Actions 38381997417: 6/6 jobs SUCCESS; 38382214223: 6/6 SUCCESS; 38419111311: 6/6 SUCCESS; 38419649711: 1/1 SUCCESS; OpenDART 38419439742: 2/2 SUCCESS. Job-level conclusions checked through connector this run.
- PR #418 integration Action 38486028854: 1/1 FAILURE (job 115599778959). Job logs fetched. Historical blob mismatch previously identified; current failure not treated as resolved. This is a software integration FAIL, not a measured financial performance FAIL.
- Historical fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is a prior evidence reference; independent recomputation this run NOT VERIFIED.
- Railway IndexAlert production environment ID 83d5840b-270e-4d3f-a941-a37fd4a55ff7; staged=null. PIT deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS (deployment success does not prove live replicas or data correctness). Kiwoom real-readonly 028c7110-5cbf-457b-b1a6-539c818280b0 FAILED. Backend and push latest deployments FAILED. No deploy/write attempted.
- Railway logs 2026-11-15 00:10–01:25 UTC: PIT 0 entries; KRX 0 entries; runtime reports Investing USD/KRW HTTPError with Yahoo fallback at 01:23:41 UTC. This is NOT official source/PIT evidence.
- Research and development branch names found; exact latest HEAD SHA NOT VERIFIED. PR metadata and head SHA not independently checked in this run. Gate document lookup on research/development branches returned 404; PR #414 source not independently read this run.

## Independent gate
- DART original filing semantic lineage, precise public available-at, 2021/2022 first 3-month consolidated operating profit, historical corporate/security mapping: NOT VERIFIED.
- KRX official calendar/status/corporate actions/fill feasibility/costs/taxes: NOT VERIFIED. Earlier private weekday pair storage integrity PASS applies only to storage, not tradability.
- NetEV, PF, CAGR, MDD, ES95/99, concentration and temporal robustness after all costs/taxes: NOT VERIFIED. M20 economic RUN NO-GO.
- Offline CI: historical successes PASS at job level; PR #418 integration FAIL. End-to-end acceleration NOT VERIFIED. Reported regression-phase serial 2.9656 s vs concurrent 2.6209 s = 1.1315x is prior synthetic evidence only.

## Frozen controls / next safe steps
- Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/holdout/Champion/Top3/NO_TRADE, ORDERING=false. No post-hoc use of consumed H5 holdout.
- Diagnose PR #418 source SHA mismatch using immutable source blobs in a separate owned isolation branch, with synthetic offline-only tests. No workflow bypass, no shared code changes.
- Obtain immutable original-filing/available-at and KRX official trading-state lineage with SHA/CI evidence before any economics run; verify PR heads and frozen policy without modifying PRs.
- No approval to promote, merge, deploy, place orders, move funds, or change credentials.
