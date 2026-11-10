# IndexAlert independent audit — 2026-11-11 07:25 KST

Read-only verification, no economic run, no authority to merge/deploy/order.

## Source pins
- Research HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub fetch_commit by branch).
- Development HEAD: `1e6367d2863a86c3470da13d81a955d277eba485` (same method).
- PR #412/#413/#414/#418/#420/#422/#423: OPEN, draft, unmerged at retrieval. PR #414 gate file blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`, fetched at refs/pull/414/head.
- GitHub Actions 38381997417, 38382214223, 38419111311, 38419649711, 38419439742, 38498552499: jobs SUCCESS respectively 6/6, 6/6, 6/6, 1/1, 2/2, 6/6 (direct jobs API). Previously documented 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` not independently recalculated this run. 13 adversarial, 28 synthetic, 21 synthetic results not independently rerun. Offline CI PASS only; real official backtest acceleration NOT VERIFIED. Later PR #413 timing serial 1.7114s vs parallel 2.5776s, regression-phase slowdown; no speedup claim.
- Railway IndexAlert production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: no stagedChanges, pending patch has zero changes; latest deployments PIT, KRX, Runtime, Kiwoom real read-only SUCCESS, backend/push FAILED; numReplicas null, hence live health NOT VERIFIED. 2026-11-10T21:00Z–22:30Z queried: PIT/KRX/Kiwoom deploy logs zero, Runtime 61 entries (market quote processing, not PIT evidence). Deployment success is not running/ordering proof.

## Independent gate assessment
- Historical KRX private weekday raw pairs 1565/1565: PASS only for previously recorded storage integrity, not rehashed here. Official calendar 90 uncertain sessions, zero activity 12003, OHLC invalid 27, historical trading status, corporate actions, fill feasibility: NOT VERIFIED, FAIL-CLOSED.
- OpenDART Action 38419439742 2/2 CI PASS for offline original/correction candidate signatures; original-filing semantic 2021/2022 CFS three-month operating income, original-public available-at, correction lineage, corp/security historical mapping: NOT VERIFIED.
- Frozen H5 consumed holdout, Dynamic: NO-GO for independent reuse. M20 source PIT and economic RUN NOT AUTHORIZED.
- After fees/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, date-cluster robustness, capital/lot feasibility: NOT VERIFIED (no authorized run).
- PR #413/#418 offline isolation safety: jobs PASS; end-to-end CI acceleration, actual backtest acceleration and PR #418 integration-context SHA compatibility NOT VERIFIED. Fail-closed cache only with independently approved source/data/code/Frozen/runtime/evidence SHA-256. Parallelize only independent read-only post-processing, never dependent retraining or capital transitions.

## Next safe steps
1. OpenDART owner: independently establish original filing public available-at and exact 2021/2022 CFS quarter and correction lineage.
2. KRX owner: reconcile official market calendar, trading status, historical mapping, corporate actions and fills against original hashes.
3. Optimization owner: offline-only manifest/parity and isolated synthetic adversarial checks; no official performance benchmark until PIT gate PASS.
4. Orchestrator: retain Frozen H5, M20 horizon20/purge20, WF504/126/126, Holdout, Champion/Top3/NO_TRADE, costs/taxes/risk gates unchanged. ORDERING=false required, runtime env value NOT VERIFIED. No PR merges, workflow changes, deployment, capital movement, orders or champion promotion without distinct approval.
