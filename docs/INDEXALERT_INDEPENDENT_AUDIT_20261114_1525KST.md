# IndexAlert independent audit — 2026-11-14 15:25 KST

Scope: read-only GitHub/Railway evidence; isolated documentation only. No source edits, workflows, deployment, merge, order, account, Champion, economic test or model search.

## GitHub evidence
- Research branch index-alert-research-v1 HEAD (compare base) `df474df348f22aa38b1dedaa59fcff66e548b406`. Development branch index-alert-position-regen-fix-v1 vs research DIVERGED, ahead 1148 / behind 281; compare API does not expose development HEAD directly in its compact result; development exact HEAD NOT VERIFIED in this run. Merge-base `c490974ff6619bb978dc6f83f9c24f2c46622f85`.
- PR #414 integration gate read from refs/pull/414/head: confirms KRX storage integrity only and M20 NO-GO. PR #412/#413/#418 and KRX #404 references retained; current exact PR HEAD/Draft states NOT VERIFIED (search_issues returned no matches, not proof of closure).
- Actions 38381997417 and 38382214223 each 6/6 successful; 38419111311 6/6 successful; OpenDART 38419439742 2/2 successful; single-runner 38419649711 1/1 successful. Historic fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` supplied as prior evidence, not independently recomputed this run.
- Integration Action 38486028854 1/1 FAILED at archived original source identity precheck; job 115599778959 log: `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e428789e2e97ca7be3a4482e0df23b483a1ad69d`. Following tamper tests and four regression suites SKIPPED. No alteration to expected SHA, no bypass. Full CI/official backtest acceleration NOT VERIFIED; synthetic runner comparison 2.9656 s serial vs 2.6209 s concurrent = 1.1315x regression phase only.

## Railway production
- IndexAlert project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX historical `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS. All numReplicas null: current process health NOT VERIFIED. Kiwoom real-readonly deployment FAILED; real-readonly-run last deployment SUCCESS but current health NOT VERIFIED.
- `stagedChanges=null` yet pendingWork patch `e113dacb-6705-4416-9997-dc694539d382` status staged since 2026-10-29. No deploy/accept.
- Logs 2026-11-14 05:20–06:25 UTC: PIT 0, KRX 0, runtime 201 returned (query limit); USDKRW Investing HTTPError -> Yahoo fallback observed, including 06:24:43 UTC. Empty worker logs do not prove worker idle or failure. Prior 27/803 OHLC anomalies unresolved absent new evidence.

## Admission and independent profitability gates
- OpenDART original-filing, public available-at/PIT, 2021/2022 first-three-month consolidated operating-profit period/correction lineage: NOT VERIFIED. Candidate SGML 15 rows and matching numeric-neighbour signatures are not approval.
- Historical entity/security mappings, official KRX calendars, trading states, corporate actions, actual execution and transaction costs/taxes: NOT VERIFIED. Historical private 1565/1565 weekday pairs storage-integrity PASS only; 12003 zero-activity samples excluded; 90-day classification not approved.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness and after-tax annual risk-adjusted profit: NOT VERIFIED. M20 PIT/economics NO-GO; consumed H5 holdout not reusable.
- Frozen H5/M20 horizon20 purge20 WF504/126/126, PIT/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE unchanged. ORDERING=false. Cache fail-closed only on independently approved source/data/code/policy/runtime/evidence SHA-256; only read-only independent postprocessing parallelizable; dependent retraining and capital transitions never parallel.
- Next: independently establish PR HEADs and approved archived original file bytes; resolve source identity drift through authorized owner review (do not change expected hash to match observed); obtain official PIT/lineage and KRX executable-state evidence before any economic run. No user authorization requested for prohibited actions.
