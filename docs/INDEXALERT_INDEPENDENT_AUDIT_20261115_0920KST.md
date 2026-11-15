# IndexAlert independent audit — 2026-11-15 09:20 KST

Scope: read-only evidence review plus this isolated documentation-only commit. No market backtest, strategy/model change, CI/workflow change, production deployment, merge, order, account/credential modification, or Champion promotion.

## GitHub evidence
- Research branch `index-alert-research-v1`: prior confirmed HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`; current branch HEAD **NOT VERIFIED** in this run (branch existence confirmed only).
- Development branch `index-alert-position-regen-fix-v1`: prior confirmed HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; current branch HEAD **NOT VERIFIED** in this run.
- Current Draft/open/unmerged PR HEADs independently read: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate file read at branch `indexalert-profitability-integration-evidence-20261013`; explicit PIT/market-profitability NO-GO.
- Actions job records read this run: 38381997417 PASS 6/6; 38382214223 PASS 6/6; 38419111311 PASS 6/6; 38419439742 PASS 2/2; 38419649711 PASS 1/1; 38486028854 FAIL 1/1 (job 115599778959). Prior job log documents archived source Git blob SHA-1 mismatch `research_v1_runtime_manifest.py`: expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e428789e2e97ca7be3a4482e0df23b483a1ad69d`; this run did not re-fetch job log. 34-case fixed SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` independently recomputed this run: **NOT VERIFIED**. Existing offline-only pass does not certify total CI or official backtest acceleration.

## Railway production evidence (read-only)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS, 1/1 running; KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS, 0/1 running; Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: SUCCESS, 1/1 running.
- 2026-11-14 23:15 to 2026-11-15 00:25 UTC log query: PIT 0 entries, KRX 0 entries; Runtime 101 returned entries (limit 100 requested). At 00:20:42 UTC Investing USD/KRW HTTPError and Yahoo fallback observed. Runtime quote logs are not PIT approval.
- backend offline (4 warnings), push offline (1 warning), db-query-readonly offline (1 critical); no recent failed deployments in 8h. Environment staged patch `e113dacb-6705-4416-9997-dc694539d382` from 2026-10-29 06:20:53 UTC remains staged, changes array empty. Do not apply.

## Independent gate
- Historical private KRX 1565/1565 weekday pairs: prior storage integrity PASS; actual official session calendar, security status, corporate actions, execution feasibility and full costs/taxes **NOT VERIFIED**. 90 uncertain sessions and 12,003 zero-activity records remain excluded.
- Original-filing DART public available-at, 2021/2022 first 3-month consolidated operating profit exact period/correction lineage, historical entity/security mapping: **NOT VERIFIED**. Original/correction SGML candidate signatures are not semantics/time approval.
- PIT, label, purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE, NetEV/PF/CAGR/MDD/ES95/99, return concentration and time robustness: economic admission **NOT VERIFIED / NO-GO**. H5 consumed holdout must not be reused. M20 horizon20/purge20 WF504/126/126 frozen; no economic RUN.
- Optimization: offline-only CI passes as listed, but integrated #418 FAIL; fixed-case independent SHA recomputation and full acceleration **NOT VERIFIED**. Cache must fail closed on complete source/data/code/frozen policy/runtime/evidence SHA-256; only independent read-only postprocessing may parallelize. No dependent retraining/capital transition parallelization.

Next safe steps: independently establish branch HEADs and original-filing/publication-time evidence; resolve archived manifest source mismatch in an owner-controlled isolated code review without modifying another Work's code; obtain official KRX state/feasibility proofs. Keep ORDERING=false, Frozen policy and M20 NO-GO. No user approval is implied by this document.
