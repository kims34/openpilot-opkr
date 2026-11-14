# IndexAlert independent audit — 2026-11-14 14:22 KST

Read-only evidence review; isolated audit document only. No official economic tests, deployments, merges, order, credentials or Champion changes.

## GitHub
- Direct research vs development compare: DIVERGED, development ahead 1148/behind 281; research HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`; merge base `c490974ff6619bb978dc6f83f9c24f2c46622f85`. Development HEAD last observed `1e6367d2863a86c3470da13d81a955d277eba485` from prior evidence, not independently extracted as current head by compare output. Branch divergence is not an hourly change.
- #414 gate path read at research ref returned 404. PR #412/#413/#414/#418 and KRX PR HEADs and draft states NOT VERIFIED this run. Open-PR search returned no entries; do not infer closure.
- Actions independently fetched: 38381997417 6/6 PASS; 38382214223 6/6 PASS; 38419111311 6/6 PASS; 38419439742 2/2 PASS; 38419649711 1/1 PASS; integrated 38486028854 1/1 FAIL.
- New precise failure evidence from job 115599778959 log: `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e428789e2e97ca7be3a4482e0df23b483a1ad69d`. The archived source identity gate fails before regression suites; do not update expected SHA or bypass workflow. Required next: source owner independently establish original approved bytes, intended immutable ref and why observed source differs; only after approved reconciliation may separate offline validation proceed.
- Historical 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` not independently recomputed this run. Serial 2.9656s / concurrent 2.6209s = 1.1315x regression phase only; full CI and official backtest acceleration NOT VERIFIED.

## Railway production
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- Environment inventory: staged=null; configured numReplicas=1 for PIT, KRX, Runtime and Kiwoom real-readonly-run. **Configured replica count is not live process health**. KRX latest deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; PIT 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; Kiwoom real-readonly latest FAILED. Prior pending patch status is NOT VERIFIED from this inventory; do not equate staged=null with resolution.
- 2026-11-14 04:20–05:23 UTC logs: PIT 0, KRX 0; Runtime returned 101 entries against limit 100 (potential truncation). At 05:22:38 UTC Investing USD/KRW HTTPError -> Yahoo fallback. This is not official PIT/KRX or tradeability evidence.
- Historical OHLC anomaly 27/803 remediation NOT VERIFIED.

## Independent admission verdict
- PASS narrowly: historical offline synthetic CI, candidate-row adjacency checks, previously reported 1565/1565 private weekday raw-pair integrity.
- FAIL: PR #418 integrated immutable archived source identity.
- NOT VERIFIED: original-filing semantics and public available-at PIT; 2021/2022 first-three-month consolidated operating profit period/correction lineage; historical entity/security mapping; official KRX calendar/status/corporate actions/executability; costs/taxes; post-cost/post-tax NetEV/PF/CAGR/MDD/ES95/99, return concentration and temporal robustness; full CI acceleration.
- M20 NO-GO. No H5 consumed holdout or Dynamic reuse. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and economics/risks unchanged. ORDERING=false. No economic tests or production changes.

## Safe next steps
1. Obtain exact PR HEADs and original #414 gate from their actual PR refs, without changing other teams' code.
2. Independently retrieve approved archived `research_v1_runtime_manifest.py` original bytes and current candidate, explain Git blob mismatch and independently hash pinned 34-case source; maintain fail-closed until provenance approved.
3. Read-only source-level PIT lineage and official KRX calendar/trading status audit before any M20 economics.
