# IndexAlert independent evidence audit — 2026-11-15 19:24 KST

Scope: read-only GitHub/Railway inspection; isolated documentation only. No trading, backtest, model exploration, deployment, workflow modification or merge.

## GitHub current PR heads (direct fetch)
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
All open Draft/unmerged. #414 base_sha 3b8b7830612a6284d7c7a60628cb527cb741627a; #420 base_sha 1e6367d2863a86c3470da13d81a955d277eba485. Current branch HEADs of index-alert-research-v1 and index-alert-position-regen-fix-v1 NOT VERIFIED independently this run.

## GitHub Actions (direct jobs)
- 38381997417 6/6 PASS; 38382214223 6/6 PASS; 38419111311 6/6 PASS.
- OpenDART 38419439742 2/2 PASS (software checks only, not semantic PIT).
- Single runner 38419649711 1/1 PASS (offline-only).
- Integration 38486028854 0/1 FAIL. Prior logged manifest expected SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b vs observed e428789e2e97ca7be3a4482e0df23b483a1ad69d; not independently re-read failure job log this run.
- Archived 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 NOT VERIFIED by fresh independent recomputation. No claim of overall CI or official market backtest acceleration.

## Railway production (direct status/logs)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- Latest deployments runtime SUCCESS eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00; KRX historical worker SUCCESS 16c93d7c-7cd0-4d84-a327-298d2805376c; PIT rebuild SUCCESS 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5. Replica counts null in get_status: NOT VERIFIED, not assumed active.
- get_status stagedChanges=null but pendingWork contains STAGED patch e113dacb-6705-4416-9997-dc694539d382 since 2026-10-29T06:20:53Z; contradictory surfaces, do not accept/apply patch.
- 2026-11-15 09:10–10:25 UTC KRX worker logs 0. Runtime Investing USD/KRW HTTPError then Yahoo fallback (10:24 UTC).
- PIT rebuild logs at 09:30,09:45,10:00,10:15 UTC: INDEXALERT_PROSPECTIVE_RUNTIME status FAIL_CLOSED; KRXProspectiveOpenAPISourceError, COMMON_OHLC_NONPOSITIVE; 803 common-stock rows, 27 nonpositive OHLC rows / zero-volume-value rows, all_zero_ohlc_rows 0. source_failure_session=2026-09-28; session=2026-11-15; session_manifest_sha256=null. fresh_alpha_observation_admitted=false; independent source/model/chronology admission=false; ordering DISABLED; live_order_authorized=false; funds_movement_authorized=false; private_rejected_source_receipt_saved=true. This is a positive safety fail-closed observation, NOT data PIT admission.

## Gate
- PASS: enumerated offline jobs; operational FAIL_CLOSED veto behaviour in observed PIT logs; prior KRX weekday-pair storage integrity remains historical source evidence only.
- FAIL: PR #418 integration CI; current KRX prospective source-quality gate (27 invalid OHLC rows).
- NOT VERIFIED: official first-original DART semantic cell and precise public available-at, 2021/2022 initial 3-month consolidated operating-profit period/correction lineage, historical entity/ticker mapping, official KRX session/halts/corporate actions/executability, transaction costs and tax, PIT, independent NetEV/PF/CAGR/MDD/ES95/99/concentration/time robustness, overall speedup and fixed-case independent SHA.
- M20 NO-GO. Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout/CPCV/Champion/Top3/NO_TRADE and costs/taxes/risk remain unchanged. Consumed H5 holdout and Dynamic must not be reused. ORDERING=false. No economic experiment, market return replay, permission change, live order, merge or deploy.

## Next evidence only
1. Isolated read-only diagnosis of PR #418 manifest blob SHA mismatch, no workflow edits.
2. Official first-filing semantic and publication-time lineage with source bytes and SHA.
3. KRX 27 nonpositive OHLC source-receipt independent classification, official session/state and execution evidence before any PIT admission.
4. Reconcile Railway stagedChanges=null vs pendingWork STAGED without applying.
