# IndexAlert independent audit — 2026-11-15 00:22 KST

Read-only observation; no trading, deployment, merge, workflow modification, or economic experiment.

## Exact PR heads (GitHub fetch_pr)
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f (draft/open)
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0 (draft/open)
- #414 18c5418d9684d1717df58261ea27f28e514385b2 (draft/open)
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee (draft/open)
- #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581 (draft/open)
- #422 c14857620973531013799e44625d43080904fd5f (draft/open)
- #423 0e38004363cac9fc4475556b3a1c445de9af407f (draft/open)
- #414 gate file blob Git SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be. Research/development branch HEAD **NOT VERIFIED in this run**; previously reported research df474df348f22aa38b1dedaa59fcff66e548b406 and development 1e6367d2863a86c3470da13d81a955d277eba485 must not be presented as fresh.

## Actions (fresh job read)
- 38381997417: 6/6 SUCCESS; 38382214223: 6/6 SUCCESS; 38419111311: 6/6 SUCCESS.
- 38419439742: 2/2 SUCCESS (candidate rows only, no PIT approval).
- 38419649711: 1/1 SUCCESS (synthetic runner).
- 38486028854: 1/1 FAILURE; previously observed immutable manifest Git blob SHA-1 mismatch expected 108f66714602a1bd3ae42c34dcca7c16e38f460b versus observed e428789e2e97ca7be3a4482e0df23b483a1ad69d; root-cause byte lineage NOT VERIFIED in this run.
- Historical 34-case fixture SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 **NOT independently recomputed**. End-to-end CI and official backtest speedup NOT VERIFIED.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild 1/1, runtime 1/1, KRX historical worker 0/1, Kiwoom real-readonly-run 0/1. Pending staged patch e113dacb-6705-4416-9997-dc694539d382 since 2026-10-29 remains.
- PIT 2026-11-14 14:15–15:25 UTC: 3 observed prospective cycles at 14:16, 14:31, 14:46, each COMMON_OHLC_NONPOSITIVE, 27 nonpositive among 803 common-stock rows, independent source/model/chronology admission false, fresh alpha false, ordering DISABLED, live order false. This is fail-closed evidence, NOT source approval.
- KRX worker: 0 logs in same window, not proof of success.
- Runtime: 15:22 UTC Investing USD/KRW HTTPError -> Yahoo fallback; operational quote fallback is not PIT evidence.

## Independent profitability gates
- KRX private raw weekday pair storage 1565/1565: historical storage-integrity PASS (prior evidence only); official calendar, historical trade state, corporate actions, fills, fees/taxes NOT VERIFIED.
- OpenDART original SGML candidate signatures: historical syntactic check PASS (prior evidence only); 2021/2022 initial three-month consolidated operating profit period and correction lineage, original filing available-at/PIT NOT VERIFIED.
- Historic entity/security mapping, M20 horizon20/purge20 WF504/126/126, Purged/CPCV, independent holdout and NetEV/PF/CAGR/MDD/ES95/99/concentration/time robustness: NOT VERIFIED. M20 economic run NO-GO. H5 consumed holdout not reusable.
- Optimisation: synthetic offline CI PASS as above, immutable-manifest integration FAIL, whole CI / real official backtest speedup NOT VERIFIED. Cache fail-closed on independently approved input/code/frozen-policy/runtime/evidence SHA-256; parallelise read-only postprocessing only.

## Next safe work
1. Independently compare approved original runner manifest bytes/blob lineage with #418 failing CI, without altering expected SHA.
2. Verify DART original filing public available-at and 2021/2022 correction lineage, then official KRX calendar/status/corporate action and executable fill/cost/tax evidence before economic runs.
3. Investigate 27/803 OHLC reject classification and staged patch via read-only evidence; do not deploy or accept patch.
4. Recompute fixed 34-case SHA and isolate wheel/OS lock evidence using synthetic offline tests only.

Frozen H5/M20/NO_TRADE/Champion gates unchanged. ORDERING=false. No merge, deploy, order, transfer, credential change, promotion, or workflow write.
