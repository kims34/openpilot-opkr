# IndexAlert independent read-only audit — 2026-11-16 07:23 KST

Scope: isolated audit evidence only; no production, trading, merge, workflow or model changes. All statuses refer only to evidence actually retrieved in this run.

## GitHub
- Branch name discovery: `index-alert-research-v1` and `index-alert-position-regen-fix-v1` exist. Exact HEAD SHA NOT VERIFIED by this run.
- PR draft/HEAD metadata NOT VERIFIED (GitHub issue search returned no matching records); do not infer closure or merge.
- Actions 38381997417: 6/6 jobs success; 38382214223: 6/6 success; 38419111311: 6/6 success; 38419439742: 2/2 success; 38419649711: 1/1 success. These are offline CI results only, not economic/PIT approval.
- Action 38486028854: 1/1 job failure, job 115599778959. Fresh job-log read: `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e428789e2e97ca7be3a4482e0df23b483a1ad69d`. Immutable archive parity FAIL. No downstream speed/economic inference.
- Previously supplied fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: independent recomputation NOT VERIFIED this run.
- Gate document at requested research ref returned GitHub 404: contents/branch location NOT VERIFIED; do not interpret as deleted.

## Railway production (read-only)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (2026-10-10), historical KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12), runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS (2026-10-05). Deployment SUCCESS is not source quality approval.
- Environment inventory reports staged=null; prior pending patch discrepancy requires independent resolution, NOT VERIFIED.
- 2026-11-15 21:00–22:30 UTC log query: PIT 0 deploy entries, KRX worker 0 deploy entries. Neither resolves prior 27/803 invalid OHLC evidence.
- Runtime at 2026-11-15 22:23:44 UTC: Investing USD/KRW HTTP errors and Yahoo fallback. This is a source substitution and not independently approved PIT evidence.

## Economic/source gate
- DART original filing, exact public available-at, 2021/2022 first-quarter consolidated operating-income lineage: NOT VERIFIED.
- Historical corporate/security mapping; official KRX calendar, status, corporate actions, executable fills, cost/tax: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, time robustness after cost and tax: NOT VERIFIED. M20 economic RUN NO-GO.
- Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE unchanged. H5 consumed holdout cannot be reused. ORDERING=false.
- Optimization only offline synthetic and fail-closed policy checks until source approval. Cache requires all approved SHA-256 dimensions; parallelize only independent read-only postprocessing; no dependent retraining/capital transitions.
- No live orders, transfers, access changes, promotion, deployment, PR merge, or workflow edit.

## Next independent work
1. Resolve immutable archive manifest SHA drift in isolated PR #418 diagnostics without changing frozen evidence or workflow; compare blob bytes and source lineage.
2. Obtain official DART first-public timestamp and correction/period lineage; official KRX trading-status and invalid-OHLC row proof.
3. Retrieve authoritative branch/PR HEAD and current draft metadata; independently reproduce fixed-test SHA before any acceleration claim.
