# IndexAlert independent audit — 2026-11-14 13:18 KST

Scope: read-only profitability verification and separate offline-only optimisation safety audit. No economic experiments, production writes, merges or trades.

## Fresh GitHub evidence
- Direct compare research `index-alert-research-v1` against development `index-alert-position-regen-fix-v1`: **DIVERGED**, ahead 1148, behind 281, merge-base `c490974ff6619bb978dc6f83f9c24f2c46622f85`; research base HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`. This comparison is between DIFFERENT branches, unlike earlier self-comparisons; not evidence of a new hourly change. Development HEAD from earlier audit `1e6367d2863a86c3470da13d81a955d277eba485` not refreshed independently in this call.
- Open-PR search returned empty; cannot establish #412/#413/#414/#418/#420/#422/#423 state or HEAD. PR #414 gate fetch from development branch returned 404. Prior #414 document blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` historical, not reverified. Do not infer merged or closed.
- Actions job results independently refreshed: 38381997417 6/6 PASS; 38382214223 6/6 PASS; 38419111311 6/6 PASS; OpenDART 38419439742 2/2 PASS; 38419649711 1/1 PASS; 38486028854 1/1 FAIL.
- Failed job `115599778959` step 6 'Enforce original CI regression-source blob identities before any test' FAIL. Step 7 fail-closed tampering tests and step 8 four disjoint regressions SKIPPED. Dependency pinning step 5 PASS. Failure remains a hard safety gate, not permission to adjust the workflow.
- Archived 34-case expected SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: independent exact-byte recomputation NOT VERIFIED. 13 adversarial mocks and 28 synthetic tests historical evidence. Serial 2.9656s vs parallel 2.6209s = 1.1315x regression phase only, not whole CI/backtest acceleration.

## Fresh Railway production evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild 1/1 running, Runtime 1/1 running. KRX historical worker and Kiwoom real-readonly-run 0/1 despite SUCCESS deployments; Backend, Push and db-query-readonly offline. Persistent pending staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29 06:20:53 UTC. No deployment or staged patch application performed.
- Logs 2026-11-14 03:20–04:20 UTC: PIT 0, KRX 0, Runtime 251 entries returned against limit 250 (truncation possible). At 04:18:38 UTC Investing USD/KRW HTTPError -> Yahoo fallback. This is runtime quote behaviour, NOT approved official PIT or KRX trading evidence. Prior OHLC anomaly 27/803 remediation NOT VERIFIED.

## Independent gates
- PASS only narrow historical technical checks: specified older offline Actions, OpenDART candidate-row numeric adjacency, previously established 1565/1565 private weekday raw-pair storage integrity.
- FAIL PR #418 integrated immutable archived-source identity gate.
- NOT VERIFIED official original-filing semantics/public available-at PIT; 2021/2022 first-three-month consolidated operating profit correction/period lineage; historical entity/security mapping; official KRX calendar/status/actions/executability; fees/taxes; post-cost/post-tax annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, return concentration and temporal robustness; full CI acceleration and archived SHA independent reproduction.
- M20 NO-GO. H5 failed/consumed Holdout and Dynamic not retuned/reused. Frozen H5/M20 horizon20 purge20 WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and financial thresholds unchanged. ORDERING=false.

## Next permitted steps
1. Obtain read-only exact PR HEADs and #414 document from actual PR refs; avoid other teams' code.
2. Inspect failing archived blob identities and exact original bytes, independently recompute 34-case SHA-256 offline. Do not bypass workflow safety.
3. Independently approve official original-filing public available-at lineage and KRX tradability/cost/tax before any M20 economic run.
4. Only synthetic offline safety tests; fail-closed cache with all approved SHA-256 inputs equal; parallelise read-only postprocessing, never dependent retraining or capital transitions.
5. No deployment, PR merge, orders, money movement, credential/account changes or Champion promotion.
