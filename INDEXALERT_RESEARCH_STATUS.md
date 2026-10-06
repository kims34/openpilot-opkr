# Original evidence types and source-gate revalidation — 2026-10-06T08:15Z / 17:15 KST

Project INCOMPLETE. Actual tested code HEADs: index-alert-position-regen-fix-v1 aca95f84e5ce0948c85dfdc09f3495c31d571fef; index-alert-research-v1 4131f17578d42e36fbf8cb22f53b43222d242abe; index-alert-server 8a68b01bca5d551d083ccda263df38d86fa54166. This documentation checkpoint follows those exact tested code heads; resolve current GitHub refs for the self SHA and inspect newer commits before resuming. Current-source restoration used actual GitHub HEAD/commits/Actions/Master/Ledger/Status/Continuity/Handoff and readonly Railway configuration/logs. PR56–117 and the owner preview/device setup were not repeated.

Three further reproduced engineering defects were fixed consecutively, mirrored and merged after exact-head CI:
- PR118/119 reject non-string original authorization metadata before normalization; numeric schema/scope/document SHA could previously become valid-looking metadata. 52 synthetic fixture cases; valid uppercase hash/canonical roundtrip/PARTIAL ceiling remain compatible. Dev feature a5ccff2e10ddf92037894cd208c17f0ee335adc2, merge92e6063c00ac90b50ea158acfb318d813b048dcf; research featurecd537b6c0afed8fdd8fc9a8661db4b9e19e9de03, mergeb43d910a221728be17a34ec90e4f0a87056474ce. Exact CI37433702707/job112170281337 and37433712418/job112170314289 SUCCESS723passed; canonical research full37433915430/job112170958291 SUCCESS1170passed5warnings.
- PR120/121 revalidate the actual A-F entries through the existing source-gate producer instead of trusting stale all-pass/closed summary booleans. Preserve existing statuses, scope and authority semantics. 35 fixture cases for PARTIAL/BLOCKED drift, malformed gates and exact summary/authority types. Dev feature624ab715e334b8ea4d6000837f768fe89f4acc9f, mergedf52c582dd5238bce45107a830f48bec30701e45; research featuref1eae6039fe623e8bafc941a7424fc61b85dd2c6, merge3e8efd55d2005e131594e13af4083ee844efc145. Exact CI37433929442/job112171003935 and37433939763/job112171037126 SUCCESS758passed; canonical full37434135450/job112171670093 SUCCESS1205passed5warnings.
- PR122/123 reject non-string original family/scope/status/evidence in the A-F producer; None/False/numeric/container evidence previously became nonempty text. 41 new cases; valid trim/case normalization and frozen rules preserved. Dedicated workflow now includes the existing ten source-gate cases too. Dev featurea2bb94c19f346290a8bc9834e5dec0063276499f, mergeaca95f84e5ce0948c85dfdc09f3495c31d571fef; research featurec1d5b9e5f776ffbf843cc6a41411a9915eb6fa73, merge4131f17578d42e36fbf8cb22f53b43222d242abe. Exact CI37434156688/job112171741062 and37434169598/job112171783818 SUCCESS809passed.
Final canonical code-head verification actually read job logs: development37434349057/job112172378656 SUCCESS809passed15.91s; research dedicated37434356697/job112172404454 SUCCESS809passed15.01s; research full37434356626/job112172404338 SUCCESS1246passed5warnings21.14s. Added128 fixture cases overall; no actual empirical source experiment or promotion. Local pytest absent was rechecked; local reproductions used isolated synthetic functions, while pytest results are from actual GitHub Actions, not claimed local execution. Automatically triggered push probe logs37433915386/job112170957724 and37433915514/job112170958532 explicitly show push_is_dry_run_only=true, AUTHORIZATION_OR_CONSENT_PREFLIGHT_BLOCKED and authenticated_request_attempted=false; SUCCESS does not imply genuine KRX evidence.

Origin review IA-20261006-ORIGIN-BINDING continued: all122 root research_v1 Python files at pinned93a51a5e666110dc42439b31c610a695cb232751 were read, including successful retry of one missing-content response. In that scoped literal search only investor_flow_lineage refers to source_contract_fingerprint_sha256. Materializer accepts a supplied frozen fingerprint without defining its identity; auth-record, receipt, batch, lineage source-contract and expected-scope hashes are distinct domains. No inspected producer establishes source-contract=batch equality. INDEXALERT_KRX_ORIGIN_BINDING_REVIEW.md records exact producer/blob evidence and prospective questions as OPEN_REQUIRED_INDEPENDENT_EVIDENCE / REVIEW_ONLY_NOT_ADOPTED. It is not a replacement frozen contract, accepted Challenger, preregistration, source PASS or execution permission. Independent authentic-origin/trust-root/contract join remains OPEN.

Readonly Railway snapshot/log retrieval this run: project d1c1a050-b7d6-41ce-b300-13c20f82a20a environment83d5840b-270e-4d3f-a941-a37fd4a55ff7; eight services/three volumes/no staged changes. Runtime37902fde-ca05-43e0-bc76-278992bf7732 pinserver8a68b01bca5d551d083ccda263df38d86fa54166 deploymenteaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, /data500MB volumef96f985a-8aba-41ef-88df-f76999c4ff0c. Market quote logs through2026-10-06T08:02:44Z are not genuine broker-native execution evidence; no fresh HTTP readiness response claimed.
PIT225f2279-d728-4e1a-a3f3-2447ff0f9dc1 pin26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15 deployment7021473a-d9a6-4711-b496-a359fd9bb0c8 SUCCESS, /pit5000MB volume03f389e5-5030-46a9-bfa5-dd8aa3dc24fa, python -S -B audit_retired_validation.py, restart NEVER. Retrieved preserved October5 audit logs verify the three retired holdout hashes, without private outcome parse or rerun.
KRX003812ee-102b-42b6-bda4-36925885b428 pinef95e7857f692fda3855390e918e165487624881 deploymente56cf101-15c5-478e-ae67-228585013ef0 SUCCESS, /data5000MB volume61610fae-dc0c-493e-9920-eb3cef4cea86, python -S -B research_v1_krx_readonly_integrity_audit.py, restart NEVER. Retrieved existing October5 logs:14495 checkpoint entries/14425 objects/errors{}, snapshot17ab461a78822b58b4026fe727d519aff992d200fabe036d905a20c99629a060. Storage integrity is true; coverage/PIT/performance/holdout/LIVE authority remains false. Audits were not reexecuted.
DEMO6be2d733-2a59-4a12-96e3-b6d869db3b97 deploymentcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9 SUCCESS/no volume. Legacy backendcce12a43-592a-4910-9b75-89c6b7cdd159 FAILED and push3ad3102d-ced6-416b-a6da-85c390c9a606 FAILED remain recorded; db-query undeployed; verify-deployment-statusdc287775-7a59-48c7-aa3f-24bd2cd59922 SUCCESS. No service restart/pin/volume/secret/runtime deployment change; these source-governance fixes are not deployed to preserved workers.

Frozen Master Spec798e658d2b3414f95ce648c58945425d9a579182, coverage/PIT contractaba8fc20b6ad0af313a5175ee9c0e7a26a92d4c8 and expected-scope contract864aa4ab115271ce5195d204c10c87017507e42d were re-read at both final code HEADs and are unchanged. Keep PIT/20:00KST/labels/WF/Purged/CPCV/purge/embargo/cost/slippage/partial fill/NetEV/Precision@Selected/PF/MDD/ES95/99/capacity/model/threshold/cutoff/promotion/rejection frozen. Failed invalid consumed v1 remains passed=false with cutoff2026-09-25/window2026-09-28..10-01; result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82, manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907, receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. Never delete/reset/reevaluate/reseal/relabel/retune/open private outcomes or fabricate historical availability/genuine KRX/LIVE. MASTER_OFF; all-source-PASS can only close declared source governance, not model/holdout/LIVE. No REJECT/INCONCLUSIVE/IDEA operational adoption or Champion overwrite.

Unfinished/blockers: independent genuine source/history/status event/availability C/D/E, authentic approval/raw-object identity plus original source-contract join, recovery/delisting cash flows, prospective preregistration/chronology, genuine LIVE600 observations/200dates/400fills/120nearcapacity>=80% of ADV0.0005 with native whole-account/date/owner/fills/fees/settlement, original production signer/push E2E. Owner preview4.8 is not production signer or trading readiness. Actual orders/funds/account-permission changes require separate explicit approval and frozen readiness. Do not assert all independent engineering exhausted.
Exact next resume: recover current refs/newer commits/Actions/state/Railway first; do not repeat PR118–123, owner preview or preserved worker audits. Read the origin review, identify any existing external frozen materializer/source-contract artifact through actual source records; if unavailable keep authentic binding OPEN rather than inventing equality. Continue independent consumer/producer consistency or execution-evidence checks that preserve frozen contracts; only reproduce real defects and validate exact PR heads before merge. Sync only contractually eligible research candidates, preserving Champion and prospective promotion. Retain the existing continuation configuration; no duplicate automation or queue timestamp claimed. This bounded execution is not project completion.

---

# Cross-audit follow-up / exact continuation — 2026-10-06T07:48Z / 16:48 KST

Actual tested code HEADs remain developmenta263b0e7a2c6a30c1e946201d307891534423289 /research814b83a84a55ccb1896b7267cae305fd95ebf7bf/server8a68b01bca5d551d083ccda263df38d86fa54166. The immediately preceding documentation HEADs2e4aa33dbb6bd00e285b4878be0c5baa6000953e /10a59d1747665aa8bd002a0a18175c480ab2a402 are actually verified: developmentExecutionEvidence run37431723150/job112163890809 SUCCESS76passed; researchExecutionEvidence run37431736228/job112163931938 SUCCESS72passed; researchOfficialKRX run37431736167/job112163931785 SUCCESS1118passed,5warnings. Current document commit follows these HEADs; resolve GitHub refs for its self SHA. All three frozen Spec/contract blobs were re-read at those exact documentation HEADs and remain unchanged.

After the eleven-fix milestone/checkpoint, independent inspection continued rather than treating CI or a checkpoint commit as project completion:
- research_v1_krx_investor_flow_lineage.py reports one source_contract_fingerprint_sha256 plus current public-evidence fingerprint.
- research_v1_krx_investor_flow_coverage.py blob78a2dcb09949286faabd0d2f116b911904c64a71 reports independent expected_scope_contract_fingerprint_sha256.
- research_v1_krx_acquisition_batch.py blobc7ecce61a526d105ac0d5e088518baa1d3c36138 computes batch_fingerprint_sha256 from receipt set + family/dataset/authorization/client/schema/public evidence/row counts/authority fields. It is not declared identical to the lineage source-contract fingerprint.
- research_v1_krx_source_data_admission.py blob8761ee5e3f0ccc2d372c9cf9d27aab57358890d1 verifies the canonical batch and combines structural audit booleans. authorization_evidence_provenance_bound checks hash shape of the batch's existing structured-evidence fingerprint; source_data_structurally_admissible/registry-review eligibility must not be promoted into independent authentic-origin proof or experiment permission.
- Existing coverage/PIT composer only emits review candidates; all performance/holdout/LIVE authority remains false. No producer contract currently inspected establishes source_contract_fingerprint=batch_fingerprint. No guessed equality or frozen requirement changed, no new empirical trial/Challenger/Champion adoption.

Next exact execution: recover current HEAD/Actions/state/Master Spec/Railway as usual; do not repeat PR56–117 or owner preview/setup. Continue IA-20261006-ORIGIN-BINDING by reading existing acquisition receipt builder/authorization record validator/source-gate audit and their tests, then locate the original definition/materializer of lineage source_contract_fingerprint. Determine which independently validated source-record identity can legally bind lineage, receipt batch and expected scope. If no existing frozen contract defines that join/trust root, keep the gap as OPEN_REQUIRED_INDEPENDENT_EVIDENCE in Research Ledger/Status and draft a prospective research review artifact without editing frozen criteria or treating a self-hash as attestation. Preserve genuine source/history/PIT/status cashflow/LIVE/signer blockers and all frozen restrictions in the complete checkpoint below. Readonly Railway pins/deployments/volumes unchanged; no new network acquisition/private artifacts or trading permissions touched. Project INCOMPLETE; no claim that all independent engineering is exhausted. Previously enabled continuation retained, no new schedule/queue timestamp claimed.

---

# Expected-scope provenance and immutable resume checkpoint — 2026-10-06T07:45Z / 16:45 KST

Actual tested code HEADs: index-alert-position-regen-fix-v1 a263b0e7a2c6a30c1e946201d307891534423289; index-alert-research-v1 814b83a84a55ccb1896b7267cae305fd95ebf7bf; index-alert-server 8a68b01bca5d551d083ccda263df38d86fa54166. This documentation commit follows those code HEADs; resolve GitHub refs for the final documentation HEAD rather than attempting a self-referential SHA. Initial actual documentation HEADs were development83c61fc436bee4383d62525dec9ed08316a4042e and researchc9764b6ad9262c3af126e181e70125aefc73349c. Actual commits/Actions/Master Spec/Research Ledger/Status/Continuity/Handoff/research refs/Railway were restored first; PR56–95 and owner preview setup were not repeated.

Eleven consecutive engineering fixes across PR96–117 are MERGED on both canonical branches. After each success, development continued immediately to the next reproduced consistency defect. No empirical Challenger/Champion adoption or promotion occurred:
- PR96/97: verify receipt version, canonical request metadata, aware retrieval/transport, exact authority and raw SHA; 46 added fixture cases. Development feature 88b5f583a1e681f18f1fca7a2d1ed4d4fcc109d7, merge 9dd739ac7a0f3b954883d2c567764b8ea3fef899; research feature 2acda09a5c53afb9bd330c04010948d4ac762ec3, merge 3b0c61e705bc33046555a6090b402bbef95469b3.
- PR98/99: canonical receipt date/dataset/path and body content address; 5 added fixture cases. Development feature c2d1c74c0df0085481d009e3d9bde1cf637b23b9, merge 84dbeaef4053e4d49fb4b059aab4c574bf1d91c4; research feature bd4f3e0a1c2936b6997e5c185880b5d88b1719b8, merge fd5ea2a19fa166a0c9de328272240100efb269de.
- PR100/101: reject coerced fetch metadata before private writes; add existing executor suite to dedicated CI; 17 added fixture cases. Development feature 96ba1045cf9153f62984f8e121ae4b5aa65a102c, merge d02860af2422120baf37b08db3a3e9d54e885d99; research feature e76df9fb5e6e3f7e2077766ac299b6f79e2a40b7, merge 7ea9fe4586786efa58bd489fcae10af0402272cd.
- PR102/103: verify frame against exact parsed OpenAPI raw before persistence; canonicalize only synthetic test fixtures; 7 added fixture cases. Development feature ec51af962aa9a85f28d1382419fb8fd4092e9094, merge 8b48f5f0ab8614fb23a8a494f0d5164fbd5d54ad; research feature 5d8a3eb25fb2f4c5379d67bb99aa9a458e0b96b4, merge ae01c165b57d6bf75f713944cfbf26b8f068c574.
- PR104/105: validate immutable reused receipt body/request/time/authority/counts; 18 added fixture cases. Development feature 441d9991ffc4c43ae398fff7bbe4b0d581209ec5, merge d340ccf5fb85f629b9916e7d8d31ad8442e54665; research feature 291f6286252e35ab6ab7a5cd5a9d21f9799d27a9, merge 3ed818de3d9da3c043dbbf82f05ce8dce5d5b5a4.
- PR106/107: reject impossible calendar dates before fetch and relocated scope address; 7 added fixture cases. Development feature 4cfc2e312c4808229792b2a3edbe03d86e3e728a, merge eb81d2ae5b5505f782099ebb00992f239ae092a5; research feature 06e6373d875a4e7ff439e3e229842f1bd022a4f9, merge 2fc5645fd0b65f77b35af11dfb794c66dd64cda1.
- PR108/109: reject noncanonical completed scope paths before private read; 7 added fixture cases. Development feature 2b6b00116de2c8a108ae350c389533b073aaa96a, merge c1ceb2dad992907101ef04f690e193d980a30b2a; research feature cbf9bb61ae4ae1211851efe152cc5bafbd9117a3, merge 467161deeed6a6d1635f9c86988d13063297a27a.
- PR110/111: validate every existing artifact; first valid file cannot hide later conflict; 2 added fixture cases. Development feature 7c091677881dd8a7f23d812d97157583d043f252, merge 2f9dcd152945d625c1c079576e8ea3a049a92ad4; research feature 599a7c8e3d4d0a1f201870aff55e91eedfb02e8e, merge 19eea85904378efa451654ae2672ea4ef921c896.
- PR112/113: validate private scope authority and completion summaries against reconstructed raw; 14 added fixture cases. Development feature 8510b331d7adca48d1a997a0c744688f323a48b7, merge 4c36b9c1834102c2eb0afb2c3c4894dce141a774; research feature a0d0a0ce8623c74d66ab88dfcddbc0791b24c977, merge aa9c7c1f989d3f2172f0ee3f0c10e6a78d3ea79a.
- PR114/115: preserve original summary types; forbid float/bool/string count coercion before checkpoint; 14 added fixture cases. Development feature 2d5634001ef15f7fc4ad72ed1fd05db1b1291ff9, merge 35c567dbb510ca0c38eec057e5cf6f4b1b17999e; research feature 2f24d7bd4758615819a6b07bca600b2002a9c69f, merge 44b94a6524e66784fe48b13c5db2e20e16caba1d.
- PR116/117: enforce existing master-only-after-nonempty-daily rule on resume; empty scope requires None; 6 added fixture cases. Development feature 3c5a8451c8317ef2faa7f11a6160f04902765226, merge a263b0e7a2c6a30c1e946201d307891534423289; research feature ad20bfcbe9e0e7b6739cc1ed3615dc5e646e5677, merge 814b83a84a55ccb1896b7267cae305fd95ebf7bf.

Exact final PR116/117 feature CI: development run37431371765/job112162772591 SUCCESS671passed; research run37431382605/job112162807264 SUCCESS671passed. Final canonical code CI actually checked:
- Developmenta263b0e7a2c6a30c1e946201d307891534423289: KRX source admission exact authority flags run37431472168/job112163093440 SUCCESS671passed in7.59s.
- Research814b83a84a55ccb1896b7267cae305fd95ebf7bf: dedicated run37431481110/job112163122224 SUCCESS671passed in11.77s; Official KRX Status Integrity run37431480932/job112163121405 SUCCESS1118passed,5warnings in19.94s.
- Server exact HEAD Actions37370547332 Server Tests and37370547415 Build Contract Smoke remain completedSUCCESS.
No locally installed pytest execution claimed. Local AST-isolated synthetic metadata guard reproductions/syntax checks rejected malformed transport/time; GitHub Actions performed actual pytest. 143 new regression/compatibility fixture cases plus seven previously existing executor tests newly included in dedicated CI explain the dedicated521→671 increase. Research975→1118 increase is actual log evidence, not genuine KRX/LIVE/performance evidence. Every fixture mutation/rename/delete used disposable test roots only, never actual historical private artifacts.

PR104/105 first CI37430250460/37430261465 failed1,620passed: newly added byte-count check ran before existing differing-payload classification. Preserve existing reconciliation behavior by checking conflicting payload first and count integrity only for compatible reuse; no test relaxed. Final feature441d9991ffc4c43ae398fff7bbe4b0d581209ec5 /291f6286252e35ab6ab7a5cd5a9d21f9799d27a9; CI37430385711/job112159619830 and37430390563/job112159635470 SUCCESS621passed, then merged. Prior canonical milestones were actually checked:1026→1043→1050→1068→1075→1082→1084→1098→1112→1118 full research tests (five existing warnings); dedicated572→596→603→621→628→635→637→651→665→671. Logs fetch attempted while one final job was still running returned unavailable content; re-read actual completion before reporting1118, never inferred a pass from missing logs.

Railway actual production inventory re-read in this execution: projectd1c1a050-b7d6-41ce-b300-13c20f82a20a/env83d5840b-270e-4d3f-a941-a37fd4a55ff7,8services/3volumes,no staged changes. Fresh source config re-read:
- Runtime37902fde-ca05-43e0-bc76-278992bf7732 pinnedserver8a68b01bca5d551d083ccda263df38d86fa54166, deploymenteaaa9f67-b9f2-41d2-832c-7d6fad9b9b00SUCCESS; /data500MB f96f985a-8aba-41ef-88df-f76999c4ff0c. Start execution_evidence_readonly_audit.py + kiwoom_readonly_configuration_audit.py then uvicorn production_v32:app; healthcheck/health. Fresh existing runtime logs through2026-10-06T07:42:45Z show NaverKOSPI/YahooUSD-KRW/ECOS basis fallback; Investing quote failure falls back. Quote-market LIVE labels are not broker-native execution evidence; no fresh HTTP readiness response captured.
- PIT225f2279-d728-4e1a-a3f3-2447ff0f9dc1 pinned26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15, deployment7021473a-d9a6-4711-b496-a359fd9bb0c8SUCCESS; /pit5000MB03f389e5-5030-46a9-bfa5-dd8aa3dc24fa; start python -S -B audit_retired_validation.py,restartNEVER.
- KRX003812ee-102b-42b6-bda4-36925885b428 pinnedef95e7857f692fda3855390e918e165487624881, deploymente56cf101-15c5-478e-ae67-228585013ef0SUCCESS; /data5000MB61610fae-dc0c-493e-9920-eb3cef4cea86; start python -S -B research_v1_krx_readonly_integrity_audit.py,restartNEVER.
- DEMO6be2d733-2a59-4a12-96e3-b6d869db3b97 deploymentcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9SUCCESS/no volume. Legacy backendcce12a43-592a-4910-9b75-89c6b7cdd159 and push3ad3102d-ced6-416b-a6da-85c390c9a606 remainFAILED; db-query-readonly undeployed; verify-deployment-statusdc287775-7a59-48c7-aa3f-24bd2cd59922SUCCESS. Do not claim every service healthy.
Existing Oct5 PIT/KRX audit logs were directly re-read, not re-executed: all three preserved holdout hashes match, model_executed/outcome_metrics_parsed/private_artifacts_mutated/real_orders_sent/network_request_attempted false. KRX14495 checkpoints/14425unique objects,errors{},storage_integrity_pass true,snapshot17ab461a78822b58b4026fe727d519aff992d200fabe036d905a20c99629a060; coverage/PIT/performance/holdout/LIVE false. Successful storage integrity does not close source gates.
No new deployment/restart/staged patch/secret/private-volume/account/order mutation. These development/research safeguards are not deployed on the preserved readonly worker pins.

Master Spec blob798e658d2b3414f95ce648c58945425d9a579182, Coverage/PIT contractaba8fc20b6ad0af313a5175ee9c0e7a26a92d4c8, expected-scope contract864aa4ab115271ce5195d204c10c87017507e42d verified unchanged on both branches before final changes; every subsequent tree modification is limited to executor/batch/tests/workflow/state records. Existing frozen PIT/timing/labels/H5 Core/WF504-126-126/rolling1260/purge/embargo/CPCV60/Top30..3/no-backfill/publication20:00KST/cost/slippage/partial-fill/NetEV/Precision@Selected/PF/MDD/ES95/99/capacity/model/threshold/cutoff/acceptance/rejection/promotion unchanged. MASTER_OFF retained. No sealed/private outcome parse/delete/reset/re-evaluation/reseal/relabel/retune, synthetic genuine-evidence substitution or backdated availability.

CONSUMED_FAILED_INVALID_V1_HOLDOUT remains failed/passedfalse/cutoff2026-09-25/window2026-09-28..10-01/discrepancy lineage: result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82; manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907; receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. Never repair, recycle or promote this consumed lineage.

OPEN / exact next resume:
1. Restore actual current branch refs/latest commits/Actions and latest four state files/Master Spec/Railway config/logs; do not repeat PR56–117 or owner preview installation, restart pinned one-shot audits or automatically run acquisition.
2. Expected-scope request/version/time/transport/content-address/raw-frame/materialized-key/immutable-all-files/date/result/completion/request-policy consistency safeguards are now completed. This supersedes the broader OPEN implementation descriptions below. Inspect upstream downstream producer contracts in research_v1_krx_investor_flow_lineage.py, research_v1_krx_investor_flow_coverage.py, research_v1_krx_acquisition_batch.py, research_v1_krx_source_data_admission.py and research_v1_krx_coverage_pit_review.py, then their regression tests: identify established values/meaning for source contract, acquisition batch, raw payload and independent expected-scope fingerprints before implementing any cross-audit join. Do not invent source_contract_fingerprint=batch_fingerprint. Composer emits review candidates only, not GatePASS.
3. Research question IA-20261006-ORIGIN-BINDING remains OPEN_REQUIRED_INDEPENDENT_EVIDENCE: canonical receipt/raw self-hashes and network_request_attempted=true/transport strings prove consistency, not authenticated KRX origin, independent rights or a trust root. Determine existing contract-eligible independent evidence/prospective chronology binding; record any missing contract join/trust-root requirement instead of fabricating authentic provenance or backdating retrieval into availability. No new accepted empirical Challenger found in fresh Ledger/Status; historical ideas/HOLD/REJECT/INCONCLUSIVE remain unapplied.
4. External sourceC/D/E full history/official availability/status-event actual fill/recovery cashflows, independent prospective preregistration chronology/trust root, genuineLIVE broker-native whole-account/day/ownership/fill/fees/settlement evidence and frozen600observations/200dates/400fills/120near-capacity>=80%ADV0.0005 requirements, original production signer/pushE2E remain OPEN. Android4.8 isolated preview ownerUI complete only; original4.7 app/signature/data unchanged. Do not infer account/source/keys absent from missing CI-local secrets.

User authorization covers normal development/tests/deployment/validation. Actual stock orders, funds movement and broker-account permission changes still require separate explicit approval; no promotion/readiness gate bypass. Existing previously enabled five-hour continuation retained, no duplicate schedule created or changed, no fresh queue timestamp verified in this execution. Project INCOMPLETE; continuity checkpoint is not project completion and does not assert all independent engineering exhausted.

---

# Raw-scope reconstruction checkpoint — 2026-10-06T07:00Z / 16:00 KST

Actual tested code HEADs: development index-alert-position-regen-fix-v1 d8136bcb7771d233442474e397a6d65750cebd52; research index-alert-research-v1 4f4026e8e24ebfd2b40c7ec9f6edb1efab6f067b; server index-alert-server8a68b01bca5d551d083ccda263df38d86fa54166. This documentation checkpoint follows these code HEADs; resolve current GitHub refs for the final documentation SHA. No concurrent/newer branch drift observed in the actual reads.

After PR80–91, development continued immediately on the documented raw/parser/provenance issue. Eight sequential engineering fixes across PR80–95 are now complete on both branches; prior full15:46/15:52KST handoffs below preserve every earlier merge/CI and actual Railway/frozen/schedule baseline.

PR92/93 MERGED: explicit valid empty OpenAPI row blocks previously produced a columnless frame that failed scope materialization, while hand-built fixtures passed. Handle truly zero-row frames before nonempty required-schema validation, preserving no trading-date inference or invented keys/zero rows. OpenAPI parsing now requires exactly one explicit supported block, a list of nonempty row objects; missing/malformed/ambiguous blocks and HTTP200 error envelopes fail rather than becoming empty evidence. Nonzero empty-object rows/schemaless frames are rejected. Data Marketplace parser unchanged. Fourteen regressions/compatibility cases; synthetic raw-fixture old/fixed reproductions verify genuine-format explicit empty handling and error-envelope rejection (no real authenticated request or genuine-data claim).
- PR92 final feature63b320605dccbf03838a8da90d5654714465545c; merge2fe6807ef91c66b4b353b61b163442f9da22a213; exact-head run37426507856/job112147260820516passed.
- PR93 final featurede3e53c28d92fd893e8292418d6337e4ce515f1d; mergec6a2d95ba2b6208247628da6368019780de6836e; exact-head run37426518072/job112147292813516passed.
Actual canonical validation of these parser merges:
index-alert-position-regen-fix-v1; KRX source admission exact authority flags; run37426638755/job112147671422; success; 2026-10-06T06:56:56.0674035Z 516 passed in 2.93s
index-alert-research-v1; IndexAlert Research v1 KRX Worker Image Smoke; run37426642912/job112147684676; success; no pytest count inferred
index-alert-research-v1; KRX source admission exact authority flags; run37426642899/job112147685031; success; 2026-10-06T06:56:58.9544940Z 516 passed in 2.63s
index-alert-research-v1; IndexAlert Research v1 Official KRX Status Integrity; run37426642887/job112147684345; success; 2026-10-06T06:57:10.0391692Z 970 passed, 5 warnings in 10.27s
The KRX Worker Image Smoke SUCCESS is CI packaging only; no Railway deployment or authenticated data acquisition is implied.

PR94/95 MERGED: reuse existing read_raw_object and parse_openapi_raw to reconstruct receipt frames from verified raw bytes, then compare actual row counts, existing dataframe payload hashes and schema hashes. Verify scope content-address hash; reuse existing frozen materialize_one_date to reconstruct exact investor/status expected keys and official trading-date boolean. Reject mismatch before any new fetch, including self-rehashed invented keys. Five temporary-fixture tamper cases cover receipt count/payload/schema and invented investor/status keys absent from raw. Empty batch fixtures now parse their frame from the exact same synthetic raw JSON, removing their previous inconsistent hand-built schema. Existing no-refetch, paused-sweep and raw-tamper tests retained. No original private artifact/checkpoint repaired, reset, rewritten, deleted or re-admitted and no genuine source claim.
- PR94 feature2c665f4cdf80b402e67f926fbbf5d1fd1b40fd54; merged8136bcb7771d233442474e397a6d65750cebd52; exact-head run37426749248/job112148025999521passed.
- PR95 featuree71cd3b322fde78c903ae733b857540772b90cc9; merge4f4026e8e24ebfd2b40c7ec9f6edb1efab6f067b; exact-head run37426759569/job112148058719521passed.
Actual canonical final merge validation:
index-alert-position-regen-fix-v1; KRX source admission exact authority flags; run37426897818/job112148502292; SUCCESS; 2026-10-06T06:59:39.4311266Z 521 passed in 3.28s
index-alert-research-v1; IndexAlert Research v1 Official KRX Status Integrity; run37426901709/job112148515571; SUCCESS; 2026-10-06T06:59:54.8856315Z 975 passed, 5 warnings in 9.34s
index-alert-research-v1; KRX source admission exact authority flags; run37426901655/job112148515316; SUCCESS; 2026-10-06T06:59:40.6542385Z 521 passed in 3.77s
Local pytest remains unavailable; no local pytest execution claimed. These offline/temporary-fixture checks are not actual KRX coverage/PIT/Alpha, genuineLIVE, independent external authorization or promotion evidence. No new research trial/ACCEPTED_CHALLENGER/Champion overwrite.

The preceding resume-checkpoint documentation HEADs eba17584da8b795db20fe4903258c03c57e4eed7 and f6523ea0fa3ae02d5ed97deb1c4c4e29b0f34963 were actually verified SUCCESS: Actions37426186535 /37426193746 /37426193751.

Railway actual inventory re-read2026-10-06T06:59:43Z:8services/3volumes, no staged changes; unchanged deployment IDs/runtime/PIT/KRX/DEMO SUCCESS, legacy push/backendFAILED and db-query undeployed. Runtimeeaaa9f67-b9f2-41d2-832c-7d6fad9b9b00; PIT7021473a-d9a6-4711-b496-a359fd9bb0c8; KRXe56cf101-15c5-478e-ae67-228585013ef0; DEMOcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9. Volumes03f389e5-5030-46a9-bfa5-dd8aa3dc24fa/pit5000MB,61610fae-dc0c-493e-9920-eb3cef4cea86/data5000MB,f96f985a-8aba-41ef-88df-f76999c4ff0c/data500MB preserved. Earlier directly read source pins/start commands/logs from this execution remain the actual configuration/audit evidence recorded below; no fresh live-readiness HTTP capture inferred. No redeploy/restart/staged patch/secret/private-volume/broker permission/order mutation.

Master Spec blob798e658d2b3414f95ce648c58945425d9a579182 verified unchanged on both final code HEADs. Coverage/PIT and expected-scope frozen JSON unchanged by these commits. MASTER_OFF and all existing frozen PIT/timing/labels/H5/WF504-126-126/rolling1260/purge/embargo/CPCV60/Top30..3/no-backfill/cost/slippage/partialfill/NetEV/Precision/PF/MDD/ES95/99/capacity/model/threshold/acceptance/rejection/promotion gates retained. No bulk/tiny genuine request, model fit/performance evaluation, original-app uninstall/data clear or real-account order enablement.

Updated exact next resume: recover current HEAD/recent commits/Actions and four latest state records/Master Spec/Railway actual inventory/config/logs. Do not repeat PR56–95 or owner preview setup. Expected-scope counter/status/all-completions-before-fetch checks and raw receipt-frame/exact materialized-key reconstruction are now completed engineering safeguards; this supersedes those broader OPEN descriptions below. Authentic rights/origin, receipt request metadata/timestamp/transport lineage and cross-audit investor-flow source/batch/raw-payload/independent expected-scope binding remain OPEN. Next inspect _verify_receipt request_metadata_sha256/receipt_version/retrieved_at/transport and existing executor request_meta plus frozen preflight contracts before choosing any new implementation; verify semantics using already established endpoints/method/exact params and genuine independent evidence rather than inventing a new fingerprint identity. A verified self-hash/raw-key consistency check is not an independent trust root. Do not equate source_contract_fingerprint with batch_fingerprint or mark source gates closed based on summaryTrue. Any new issue gets recorded in Ledger/Status; synthetic mismatch fixtures remain clearly synthetic.

External source C/D/E full history/availability/status-event actual fill/recovery cashflows, independent prospective preregistration chronology/trustroot, genuineLIVE broker-native whole-account/day/ownership/fill/fees/settlement and frozen count/capacity evidence, original production signing key/pushE2E remain OPEN. Isolated4.8-preview ownerUI is complete only; no repeat installation or assumed production signing closure. Prior enabled5hour continuation schedule retained; no duplicate/change or independently verified queue timestamp claimed in this execution. Project INCOMPLETE; this is continuity, not completion or an assertion that all independent engineering is blocked.

Preserve consumedfailedinvalidv1 holdout passedfalse/cutoff2026-09-25/window2026-09-28..10-01/discrepancy, result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82, manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907, receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. No sealed/private outcome parse/delete/reset/re-evaluation/reseal/relabel/retune, synthetic genuine-evidence substitution or backdated availability. Existing development/test/deploy/validation authorization persists; actual stock orders/funds movement/broker-account permissions still require separate explicit approval.

---

# Expected-scope resume follow-up — 2026-10-06T06:52Z / 15:52 KST

Current exact tested code development HEAD cf7f80735f1ae0cc478d746eb2ca2cf6f03a446c; research HEAD f93087463c9c32d88309f6eda2ab19f6ab73bca4. Server remains8a68b01bca5d551d083ccda263df38d86fa54166. This documentation checkpoint follows these code HEADs; read actual refs for its self SHA when resuming.

After the PR80–89 milestone, independent development continued immediately with the documented expected-scope resume issue. PR90/91 now MERGED after actual exact-head CI493passed:
- PR90 feature a728d52de9d2d362c000097f7aa6611880b0c53e; merge cf7f80735f1ae0cc478d746eb2ca2cf6f03a446c; run37425937985/job112145479879.
- PR91 feature f49545a9159ca09e99c4f358331fd09413e34b36; merge f93087463c9c32d88309f6eda2ab19f6ab73bca4; run37425947942/job112145511121.

The old loader accepted inconsistent completed_task_count/batch_complete and a textual illegal authority claim in direct synthetic isolated-loader reproductions. Resume now checks canonical integer task/completion counts, exact frozen-date membership, mapping entries, status/completion derived from the actual stored completion map and exactFalse source/performance/holdout/trading authority flags. It rejects malformed historical checkpoints rather than repairing or rewriting them. All stored date completions and referenced raw objects are verified before any new fetch, including dates beyond a first missing-date gap. Previously an operational pause could break before verifying those later completions. Thirty-six malformed state/authority cases and one temporary-fixture raw-checksum-tamper gap case added; existing resume-without-refetch and frozen4127date/paused tests retained. Dedicated CI now includes the existing batch integration suite and relevant dependencies. No genuine network request, private Railway checkpoint mutation or reset/restart performed; synthetic FetchResult fixtures are not real KRX evidence.

Actual canonical merge validation:
index-alert-position-regen-fix-v1; KRX source admission exact authority flags; run37426029141/job112145765192; SUCCESS; 2026-10-06T06:50:44.2477366Z 493 passed in 2.03s
index-alert-research-v1; IndexAlert Research v1 Official KRX Status Integrity; run37426035776/job112145786401; SUCCESS; 2026-10-06T06:50:57.2968688Z 956 passed, 5 warnings in 8.36s
index-alert-research-v1; KRX source admission exact authority flags; run37426035872/job112145786736; SUCCESS; 2026-10-06T06:50:50.6037325Z 493 passed in 2.68s

Local pytest unavailable; actual Actions logs supply these counts. PR80–89 doc HEADs fa6a5578ce981cae37c16c7b93789a057594a6f9 /99b96bafeb0d6618855f4fed9b0f2d2c3aaf2f65 also have actual SUCCESS documentation Actions37425766725 /37425774047 /37425774148. Six sequential engineering fixes across PR80–91 are complete. These CI results do not close real data, Alpha, holdout, genuineLIVE or project completion.

Updated exact next resume: refresh current GitHub refs/recent commits/Actions and these four state records/Master Spec; refresh Railway pins/deployments/logs. Do not repeat PR56–91, owner Android preview installation, default signing-key checks, or completed counter/status/all-completions-before-fetch guard. The narrower OPEN issue is full authentic raw-response-to-materialized-key reconstruction and cross-audit batch/payload/source/independent scope binding. Review research_v1_krx_expected_scope_batch.py _verify_receipt/_verify_completed_date with research_v1_krx_expected_scope_executor.py _ensure_fetch_result/_persist_response/private_scope and private-store/official response parser contracts. Existing receipt stores raw-object hash plus response_frame schema/payload hashes, but a self-checksummed scope/receipt does not alone independently establish that private materialized keys were reconstructed from that same authenticated raw response. Determine the established provider parser/serialization and contract meanings before implementing; never assume source_contract_fingerprint=batch_fingerprint or invent a raw-byte/frame equivalence. Any new mismatch reproduction uses clearly synthetic fixtures, not sealed/private outcomes or genuine-data claims. Continue admissible implementation/tests/exact-head CI/merge/canonical verification; do not launch bulk network acquisition from a missing evidence summary.

The preceding full15:46KST handoff remains the Railway/pin/volume/log/frozen/source research/schedule baseline. Its broader resume-counter issue is now resolved by PR90/91; raw-scope reconstruction remains OPEN. Railway directly verified inventory/config/pins at06:36Z and audit logs unchanged: runtimeeaaa9f67-b9f2-41d2-832c-7d6fad9b9b00/PIT7021473a-d9a6-4711-b496-a359fd9bb0c8/KRXe56cf101-15c5-478e-ae67-228585013ef0/DEMOcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9SUCCESS, three volumes preserved, no staged changes. Legacy push/backend FAILED remain, db-query undeployed. No deploy/restart/secret/volume/account/order mutation. No new live-readiness HTTP capture inferred.

Master Spec blob798e658d2b3414f95ce648c58945425d9a579182 and frozen coverage/PIT/expected-scope contract blobs remain unchanged. Source C/D/E/availability/status realized economics, independently attested preregistration chronology/trustroot, genuineLIVE wholeaccount/date/ownership/fill/fees/settlement and frozen execution counts, original production signing key/pushE2E remain OPEN. No new ACCEPTED_CHALLENGER/Champion overwrite; prior research ideas stay HOLD/IDEA/REJECT/INCONCLUSIVE unless existing adoption gates actually pass. Actions-local missing credentials must not be misreported as Railway missing keys.

Project INCOMPLETE; MASTER_OFF/all frozen PIT/time/labels/H5/WF504-126-126/CPCV60/purge/embargo/Top30..3/no-backfill/cost/slippage/partial-fill/NetEV/Precision/PF/MDD/ES95/99/capacity/model/threshold/acceptance/rejection/promotion conditions unchanged. Consumedfailedinvalidv1 cutoff2026-09-25/window2026-09-28..10-01/discrepancy and result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82, manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907, receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63 preserved. No private outcome parse/delete/reset/re-evaluation/reseal/relabel/retune or retrospective timestamp fabrication. Actual orders/funds/broker account permission changes require separate explicit approval. Prior enabled fivehour schedule retained; no duplicate/change or independently verified queue timestamp claimed in this execution. This checkpoint is continuity, not project completion or a claim that all remaining paths are external-only.

---

# INDEXALERT_HANDOFF — 2026-10-06T06:46Z / 15:46 KST

## Actual restored and completed state

At resume GitHub development HEAD 2d41fbd093104c2e7eaf1839c7d0141762385003 and research HEAD dae21213c9f7bfaa3a9f698b1cbb6a39f192af7c matched the prior completed checkpoint; their documentation Actions 37422364097/37422370485/37422370571 were SUCCESS. Related research refs were actually enumerated; no newer adopted Challenger was found in the retrieved Ledger/Status. No merged PR56–79 or owner preview installation was repeated.

Current tested code HEADs: index-alert-position-regen-fix-v1 cf3bea32428036ca1a925f0acb40abe802d361f3; index-alert-research-v1 ea7f82800d6fd9e0a8228d338ffc3d5176e48fdb; index-alert-server 8a68b01bca5d551d083ccda263df38d86fa54166. This documentation commit follows those code HEADs; resolve actual branch refs before resuming.

Completed five sequential engineering fixes on both development and research branches:
- PR80/81: reject original non-string PIT/source and expected-scope fingerprints before normalization. Old numeric64digit values were accepted; direct synthetic reproduction shows rejection. Fifteen bad-input tests and two valid-string compatibility tests; PR CI362passed.
- PR82/83: retain exact already-validated source_contract_fingerprint_sha256 and expected_scope_contract_fingerprint_sha256 values in audit summary dictionaries, alongside counts. Four cases distinguish different contracts. Additive traceability only; no fingerprint interpretation or admission/authority decision changed. PR CI366passed.
- PR84/85: validate all eight existing COVERAGE_PIT_AUDIT prerequisite requirement flags as exactTrue and the four frozen Gate-C/D requirement lists. Existing validator accepted removal/false of an independent expected-scope prerequisite. Forty-four drift regressions reject; unchanged contract remains valid. Required evidence flags are requirements, not proof that evidence is complete. Dedicated suite now includes existing review tests; PR CI415passed; canonical official research893passed/5warnings.
- PR86/87: enforce existing expected-scope contract requirement to output a scope fingerprint for investor and status outputs. Ten missing/malformed-field regressions; frozen JSON unchanged; PR CI430passed.
- PR88/89: expected-scope materializer previously emitted KOSDAQ common-stock rows under the frozen KOSPI contract. Require daily MKT_NM and master MKT_TP_NM explicitly KOSPI; reject ambiguous/mixed/out-of-scope evidence. No guessed aliases, silent new securities/calendar/zero rows or contract scope changes. Also reject numeric/non-string fingerprints at upstream bind_scope_contract_fingerprint so downstream validation cannot be bypassed by prior coercion. Sixteen regression/compatibility cases; PR CI451passed. Existing empty-daily behavior, exact ISU_CD same-date join, valid string trim/lowercase and input immutability remain. Direct synthetic reproduction stubbed contract loading only for the local materializer experiment; actual CI/production retains required contract validation.

PR80 MERGED; dev; feature c0c8468fae808fdc30e58ddf665ee4b1ff1733e7; merge 425731f574804ab8982e01e08ea63ff4d5b72da5; exact-head run 37424809736/job 112141947518 SUCCESS.
PR81 MERGED; research; feature 35e44ad564edfd5b83f1c93e58bb3010445117f3; merge 11827420277d84f7cfb7c6737c52f90d64d18631; exact-head run 37424816689/job 112141970020 SUCCESS.
PR82 MERGED; dev; feature e1115e44ad62669d900d56b48675c4164275c88a; merge 840fd08e0a9a7169a63892d3733c1b113946bc8b; exact-head run 37424933631/job 112142342584 SUCCESS.
PR83 MERGED; research; feature 8c8b3d6ba58a31815b75e800e4ae4ac467ee2120; merge b3c4c4817a57aa028d55c3e40e01549d1ebbd90c; exact-head run 37424943628/job 112142373847 SUCCESS.
PR84 MERGED; dev; feature 66395b206a43f1b48f9a9851994adf0fcfe246d0; merge bc66b133ce0457d932cb400191c5186af6a37d5e; exact-head run 37425074289/job 112142782005 SUCCESS.
PR85 MERGED; research; feature 02f8913b55eec76375a24061d9ba64bf3e0f63aa; merge f835c8256b9b64ca9b70ea63fe785a8fba7107ce; exact-head run 37425082710/job 112142809283 SUCCESS.
PR86 MERGED; dev; feature abcbb57193ca285380a31e0159ec5a4f4179371a; merge 82c2fb92bd11e196f8adc0581a75b3a13c73d129; exact-head run 37425277388/job 112143413813 SUCCESS.
PR87 MERGED; research; feature 2bb8ec7ef800bbdfd4fbc2c7575c38f8cf4c7222; merge 0d504cb52b08a0787ef077b73a8044dbc50643bc; exact-head run 37425286843/job 112143443644 SUCCESS.
PR88 MERGED; dev; feature 7a8b37265b12bc47eaa9f5899567e5d0da271243; merge cf3bea32428036ca1a925f0acb40abe802d361f3; exact-head run 37425461062/job 112143978389 SUCCESS.
PR89 MERGED; research; feature bfc719159abb30c9cd65cc53360aabbd7d5d159c; merge ea7f82800d6fd9e0a8228d338ffc3d5176e48fdb; exact-head run 37425471292/job 112144010151 SUCCESS.

Local pytest remains unavailable; direct Python reproductions were run, and actual GitHub Actions logs supply pytest counts. These are offline engineering checks, not real KRX data/performance/genuine LIVE evidence. No new Alpha trial or ACCEPTED_CHALLENGER/Champion replacement.

Frozen blobs verified unchanged after guard merges: INDEXALERT_MASTER_SPEC.md 798e658d2b3414f95ce648c58945425d9a579182; INDEXALERT_KRX_COVERAGE_PIT_AUDIT_CONTRACT.json aba8fc20b6ad0af313a5175ee9c0e7a26a92d4c8; INDEXALERT_KRX_EXPECTED_SCOPE_ATTESTATION_CONTRACT.json 864aa4ab115271ce5195d204c10c87017507e42d.

## Actual Railway evidence

Fresh inventory/config reads at2026-10-06T06:36Z: project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production83d5840b-270e-4d3f-a941-a37fd4a55ff7; eight services/three volumes; no staged changes or running new deployment observed. Runtime37902fde-ca05-43e0-bc76-278992bf7732 pin8a68b01bca5d551d083ccda263df38d86fa54166, deploy eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00SUCCESS, /data500MB f96f985a-8aba-41ef-88df-f76999c4ff0c. Read-only evidence/config audit start chain then uvicorn remains. Runtime logs actually read through2026-10-06T06:36:46Z: Yahoo/Naver/ECOS market-display updates; market_state LIVE in quote output is not genuine broker-native fill evidence.

PIT225f2279-d728-4e1a-a3f3-2447ff0f9dc1 pin26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15, deploy7021473a-d9a6-4711-b496-a359fd9bb0c8SUCCESS, /pit5000MB03f389e5-5030-46a9-bfa5-dd8aa3dc24fa, read-only retired audit/NEVER restart. Re-read existing Oct5 audit logs: all preserved hashes match, model_executed/outcome_metrics_parsed/private_artifacts_mutated/network/real_orders false; all retired stages blocked. No new private outcome read.

KRX003812ee-102b-42b6-bda4-36925885b428 pinef95e7857f692fda3855390e918e165487624881, deploye56cf101-15c5-478e-ae67-228585013ef0SUCCESS, /data5000MB61610fae-dc0c-493e-9920-eb3cef4cea86, read-only integrity audit/NEVER restart. Re-read existing Oct5 logs:14495 verified checkpoints/14425 objects, errors{}, snapshot17ab461a78822b58b4026fe727d519aff992d200fabe036d905a20c99629a060. Storage integrity only; historical coverage/PIT/performance/holdout/LIVE false.

DEMOcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9SUCCESS/no volume. Legacy backendcce12a43-592a-4910-9b75-89c6b7cdd159 and push3ad3102d-ced6-416b-a6da-85c390c9a606 remain FAILED; db-query-readonly undeployed; verify-deployment-statusSUCCESS. No redeploy/restart/secret/private-volume/account/order mutation performed.

## Incomplete work and exact resume

Cross-audit source/batch/raw-payload/independent expected-scope binding remains OPEN. Exact fingerprints are now retained, but this does not prove lineage/coverage came from the same authenticated batch/payload/attestation. Never equate source_contract_fingerprint to batch_fingerprint, metadata self-hash to independent trust, or source-contract summaryTrue to genuine proof without the existing contracts/callers establishing that meaning. COVERAGE_PIT_AUDIT permits review candidates only and forbids GatePASS/sourceclosure/performance/holdout/trading.

Expected-scope batch resume review OPEN: _load_or_init_state validates task-set hash but does not yet derive completed_task_count/batch_complete/status from the verified exact completed-date set; _verify_completed_date verifies referenced object hashes but does not reconstruct all materialized scope keys from raw official responses. Inspect immutable private-store and executor contracts/tests before implementing. Never mutate existing private checkpoints, infer actual completed official scope, reset acquisition, or equate a self-hash with independent provenance.

Next exact execution: refresh GitHub refs/Actions and latest four continuity/research files plus Master Spec; refresh Railway pins/deployments/logs before any operational action. Do not repeat PR56–89. Review research_v1_krx_expected_scope_batch.py _load_or_init_state/_verify_completed_date alongside executor/private-store contracts and tests; reproduce inconsistent completion-map/counter/status or exact raw-scope binding with synthetic fixtures only, then reject malformed resume metadata without resetting/re-writing old private acquisition evidence or launching network requests. Check actual completion set and receipt/raw-object provenance; do not assume self-checksummed metadata alone independently attests a historical scope. Any newly justified implementation follows isolated branch, actual exact-head CI, merge and canonical CI before further work.

External source C/D/E history/availability/provenance/status-event realized fill/recovery economics, independent preregistration chronology/trust root, genuine LIVE whole-account/day/ownership/fill/fees/settlement gates, original production signing key and push E2E remain OPEN. Actions-local absent credentials from prior probes are not evidence Railway configured keys are absent. Isolated Android4.8-preview owner UI validation already complete; no original4.7 uninstall/data-clear/key upload authorized or performed. Original package/signing constraints remain in earlier records.

Schedule: prior directly confirmed enabled existing task6ac3b166d460819186ae78ecc3c7444d, first planned Oct6 19:28:47KST/every5hours; latest direct user reauthorization supersedes historical manual-only cancellation notes. Not changed or independently re-queried this execution; no duplicate automation or queue timestamp claim.

## Frozen prohibitions

Project INCOMPLETE. MASTER_OFF and existing PIT/time/labels/H5CoreWF504/126/126 rolling1260/horizonpurge/embargo/CPCV60/Top30..3/no-backfill/cost/slippage/partial-fill/NetEV/Precision@Selected/PF/MDD/ES95/99/capacity/model/threshold/acceptance/rejection/promotion boundaries unchanged. No synthetic/estimated KRX or broker data admitted as real evidence. No unauthorized model fit/performance testing, order implementation below Master Spec gates or actual trading activation.

Preserve CONSUMED_FAILED_INVALID_V1_HOLDOUT, passedfalse, cutoff2026-09-25/window2026-09-28..10-01 and discrepancy lineage. Result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82, manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907, receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. No deletion/reset/reevaluation/reseal/relabel/retune, private outcome parse or retroactive timestamp fabrication. Development/tests/deploy/validation authorization persists; actual orders/funds movements/broker-account permission changes still require separate explicit approval.

## Canonical exact merge validation

index-alert-position-regen-fix-v1 @cf3bea32428036ca1a925f0acb40abe802d361f3; KRX source admission exact authority flags; run37425598932/job112144401669; SUCCESS; 2026-10-06T06:46:14.9349711Z 451 passed in 1.51s
index-alert-research-v1 @ea7f82800d6fd9e0a8228d338ffc3d5176e48fdb; KRX source admission exact authority flags; run37425602427/job112144412401; SUCCESS; 2026-10-06T06:46:20.6006451Z 451 passed in 1.83s
index-alert-research-v1 @ea7f82800d6fd9e0a8228d338ffc3d5176e48fdb; IndexAlert Research v1 Official KRX Status Integrity; run37425602409/job112144412087; SUCCESS; 2026-10-06T06:46:27.3044432Z 919 passed, 5 warnings in 8.61s

These verified CI results are offline engineering validation only. Documentation checkpoint follows; final actual branch HEAD must be resolved from GitHub.

---

# Authorization normalization follow-up — 2026-10-06T06:10Z / 15:10 KST

Actual tested development HEADfaa4b1c5ea2821b3dc750bf5985b2d6db264d043; research HEAD6acf2fbffb3c67f4b92082a517ffb58b88e09c79. This documentation checkpoint follows these code HEADs; obtain exact current branch HEAD from GitHub when resuming.

PR78/79 MERGED after exact-head CI345passed. Numeric0/1/0.0/1.0 previously passed optional-boolean tuple membership. Synthetic input1 initially failed explicit automated-collection permission, normalized toTrue, and passed metadata tiny-probe preflight after roundtrip. The validator now accepts only actual optional booleans;4numeric regressions reject before normalization and3canonical None/False/True roundtrips preserve decisions and record fingerprints. No external approval was established, no tiny/bulk request was made by this work, no old normalized record was rewritten or retrospectively trusted. The underlying external approval artifact remains necessary; already-normalized legacy metadata cannot recover its original type merely by rehashing.

PR78 feature2f1affbc64d3084636ed77a6abb1d4288c9c560e, mergefaa4b1c5ea2821b3dc750bf5985b2d6db264d043, PR CI37422045864/job112133324878345passed.
PR79 feature9a39fb48085be9e852cd10975c0b3ec24ecb6c42, merge6acf2fbffb3c67f4b92082a517ffb58b88e09c79, PR CI37422053941/job112133349378345passed.
Actual canonical merge CI:
- index-alert-position-regen-fix-v1: KRX source admission exact authority flags; run37422191859/job112133789789; success; 2026-10-06T06:09:35.4347114Z 345 passed in 1.58s.
- index-alert-research-v1: IndexAlert Research v1 KRX Status Source Probe; run37422198832/job112133811149; success; success; no pytest count inferred.
- index-alert-research-v1: KRX source admission exact authority flags; run37422198708/job112133810594; success; 2026-10-06T06:09:36.0870863Z 345 passed in 1.16s.
- index-alert-research-v1: IndexAlert Research v1 KRX Investor Flow Probe; run37422198670/job112133811522; success; success; no pytest count inferred.
- index-alert-research-v1: IndexAlert Research v1 Official KRX Status Integrity; run37422198766/job112133810811; success; 2026-10-06T06:09:49.6385352Z 828 passed, 5 warnings in 8.14s.

Previous documentation HEADs60cc79d0cf9a0f65d441a64ff89a651c30e74477 / b034949ce66cd4fb41245b14d8910445951b855b also have SUCCESS Actions37421858353 /37421865292 /37421865281. Dedicated CI345 and official KRX828passed/5warnings are offline engineering checks, not genuine source/Alpha/LIVE evidence. Local direct numeric-permission regression/roundtrip passed; local pytest is unavailable. Source-data admission/PIT/coverage code changes from PR66–77 remain as recorded below.

Fresh Railway inventory at2026-10-06T06:10Z again confirms identical runtime/PIT/KRX/DEMO deployments and all3volumes, no staged changes, legacy backend/push FAILED and db-query undeployed. Source pins/start commands and preserved holdout hashes remain the earlier directly checked configuration/audit evidence. No deployment, restart, private-volume/source record, secret, account permission, actual broker order or model/frozen change was performed. Schedule remains the earlier directly listed ENABLED19:28:47KSTfirst planned start/every5hours; no new automation was created and no queue timestamp inferred.

Next exact resume: fresh actual HEAD/Actions/Status/Continuity/Railway first; do not repeat merged PR56–79 or owner preview installation. Continue the documented cross-audit source/batch/payload/expected-scope binding review only under the existing frozen contract meanings; the current COVERAGE_PIT_AUDIT contract permits review candidates but forbids GatePASS/sourceclosure/performance/holdout/trading. Authentic external approval, independent expected scope and availability lineage remain required. Keep the newly identified summary-binding research/engineering issue OPEN rather than manufacturing a self-attestation or changing fingerprint semantics. Other external source/economics/independent chronology/genuine LIVE/original signing-key/production-push blockers remain OPEN, as below.

Project INCOMPLETE; MASTER_OFF and all frozen H5/PIT/labels/WF/purge/embargo/cost/partial-fill/NetEV/Precision/PF/MDD/ES95/99/holdout/model/threshold/promotion rules are unchanged. Preserve failed consumed v1 cutoff/window/result/manifest/receipt hashes and discrepancy lineage. No re-evaluation, reseal, relabel, private outcome access, retrospective timestamp fabrication or real-order enablement. Real orders/funds/account permission changes still need separate explicit approval. This is a continuation checkpoint, not project completion.

--- Full handoff and historical authoritative records follow. ---

# INDEXALERT_HANDOFF — 2026-10-06T06:04Z / 15:04 KST

Project remains INCOMPLETE. Actual tested code HEADs before this documentation checkpoint:
- index-alert-position-regen-fix-v1@78452bdfde69d6fa2ca1a4a33f90b23683f0b752
- index-alert-research-v1@7950f3dae76a9c1eed67f965603a00b6b6c7d2a2
- index-alert-server@8a68b01bca5d551d083ccda263df38d86fa54166 (fresh branch/config read; unchanged)
The documentation commit follows these tested HEADs. Always retrieve exact current branch HEAD/parent and latest Actions from GitHub rather than treating an earlier checkpoint as current.

Recovered the interruption accurately: PR66 existed at feature2b026eab52855544d3d1df6be135f287297d9d9c with SUCCESS CI37419869880/job112126607451161passed; research counterpart branch did not exist. Completed its merge and research synchronization, then continued through PR77. No completed PR56–65 work or owner preview installation was repeated.

Completed:
- PR66/67: exact string contract fields and authorization digest type at receipt ingress;54 regressions.
- PR68/69: revalidate retrieved_at with the builder's existing timezone-aware parser;5 malformed/naive cases plus2 valid timezone cases. Existing timezone/PIT rules and receipt bytes are not rewritten.
- PR70/71: reject missing/container/numeric contract and digest inputs in the builder before they are coerced into apparently valid strings;40 direct-builder regressions; receipt suite/dependencies added to dedicated CI.
- PR72/73: preserve existing source-family/route allowlists, opaque non-secret references and serialized column types, and require acquisition-only coverage/PIT claims to remain exact False;28 regressions.
- PR74/75: apply canonical scalar contract, digest, route and opaque-reference checks to directly supplied batch manifests;33 regressions.
- PR76/77: CRITICAL PIT CONSUMER REVALIDATION. A previously normalized frame mutated to available_at19:00 while published_at20:00 still emitted chronology_valid=true and permitted a19:30 decision; string"false" lineage_validated also passed coverage. All3 synthetic counterexamples were reproduced against the original consumers. Audit, decision and coverage now require exact True markers and rerun the existing full lineage validator against the current snapshot. Frozen chronology event<=published<=available<=ingested,20:00KST publication floor, identity/public/source checks remain unchanged. Preserve input, caller metadata and index; coverage errors retain their domain type.25 regressions.

Exact PR merges/CI references:
- PR66: merged9e7f199c92fc71eb51a71ab777be1b78734ce9d; CI37419869880/job112126607451 (PR66).
- PR67: merge8c7c989b9d4a20372dfea57db9adf7ffd124d290; CI37420288439/job112127890655.
- PR68: merge23d8d55e957b0afdc91de040a3e668981bb313bb; CI37420392444/job112128215963.
- PR69: merged318c6c59b5a9d3734d34af7b840a96d95b951ad; CI37420401725/job112128246021.
- PR70: merge072e2f36760106c1843a7e6914b9cedc1519cc08; CI37420523552/job112128627795.
- PR71: merge48e0bc6c107520b7a329c92a7c456f33dfbcf850; CI37420533833/job112128659894.
- PR72: merge7b82109d879dba4eb467dacc966d2972295fa244; CI37420785854/job112129439857.
- PR73: mergeedaa69d16cd672ac85016a697e349437148097d9; CI37420795299/job112129467992.
- PR74: merge1c3e0b80cb5d08e8ab8a8a2ea5a390ab36859e5f; CI37421076117/job112130331255.
- PR75: merge8ce53993ca763de80916caaf4fb44b9542ab8e95; CI37421084677/job112130358250.
- PR76: merge78452bdfde69d6fa2ca1a4a33f90b23683f0b752; CI37421499000/job112131639057.
- PR77: merge7950f3dae76a9c1eed67f965603a00b6b6c7d2a2; CI37421507668/job112131666511.

Actual canonical job-log verification:
- index-alert-position-regen-fix-v1: KRX source admission exact authority flags; run37421642473/job112132085189; success; 2026-10-06T06:03:25.2804452Z 329 passed in 1.55s
- index-alert-research-v1: IndexAlert Research v1 Official KRX Status Integrity; run37421649060/job112132104960; success; 2026-10-06T06:03:32.6005524Z 821 passed, 5 warnings in 4.11s
- index-alert-research-v1: KRX source admission exact authority flags; run37421649010/job112132104750; success; 2026-10-06T06:03:36.1558103Z 329 passed in 1.55s
The dedicated suite covers329 offline receipt/batch/source/lineage/coverage tests. Official research suite821passed with5emitted warnings. Local py_compile passed for all5changed modules. Local direct synthetic reproductions verified malformed builder inputs, receipt/batch contracts and all3PIT bypasses fail closed after fixes. Local pytest is unavailable; no local pytest pass is claimed. These are engineering tests, never actual KRX/genuine LIVE/Alpha results.

Master Spec Git blob798e658d2b3414f95ce648c58945425d9a579182 remains unchanged. No frozen thresholds, labels, model, Champion, real-order logic or accepted empirical trial changed. Fresh research Ledger/Status were read; ideas remain HOLD/source/preregistration-gated and no new ACCEPTED_CHALLENGER was found or applied.

Railway read-only recovery:
Projectd1c1a050-b7d6-41ce-b300-13c20f82a20a / production83d5840b-270e-4d3f-a941-a37fd4a55ff7;8services/3volumes/no staged changes.
- Runtime37902fde-ca05-43e0-bc76-278992bf7732: deploymenteaaa9f67-b9f2-41d2-832c-7d6fad9b9b00SUCCESS, pin8a68b01bca5d551d083ccda263df38d86fa54166; /data500MB volume f96f985a-8aba-41ef-88df-f76999c4ff0c; read-only evidence/configuration audits then uvicorn. Actual latest inspected logs2026-10-06T05:47:42Z remain market-display/provider observations, not native fills or official source-admission evidence.
- PIT225f2279-d728-4e1a-a3f3-2447ff0f9dc1: deployment7021473a-d9a6-4711-b496-a359fd9bb0c8SUCCESS, pin26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15; /pit5000MB volume03f389e5-5030-46a9-bfa5-dd8aa3dc24fa; audit_retired_validation.py/restartNEVER. Existing audit log confirms all3preserved hashes, no model/outcome parse/private mutation/network/orders; all retired validation stages blocked.
- KRX003812ee-102b-42b6-bda4-36925885b428: deploymente56cf101-15c5-478e-ae67-228585013ef0SUCCESS, pinef95e7857f692fda3855390e918e165487624881; /data5000MB volume61610fae-dc0c-493e-9920-eb3cef4cea86; read-only integrity/restartNEVER. Existing actual audit log14495verified checkpoints/14425objects/errors{}; historical_coverage_validated=false, pit_availability_validated=false and all later authoritiesfalse.
- DEMO deploymentcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9SUCCESS, no volume. Legacy backend/push still retain September23FAILED deployments; db-query has no deployment. Do not claim whole-project health.
No deployment/restart/source-pin/volume/secret/account/broker/real-order changes this run. Do not roll these code changes into retired/consumed validation or alter old immutable receipt/fill bindings.

Schedule freshly listed this run: existing task6ac3b166d460819186ae78ecc3c7444d ENABLED, Asia/Seoul, DTSTART20261006T192847 and RRULE:FREQ=HOURLY;INTERVAL=5. First planned19:28:47KSTOctober6. Returned next_run_time=null; no queue timestamp claimed. Latest explicit owner reauthorization supersedes historical cancellation. No duplicate automation or new scheduling change.

Exact next resume:
1. Fetch GitHub latest HEADs/commits/open PRs/Actions, including documentation checkpoint workflows, plus current Railway inventory/config/logs. Do not restart successful readonly workers or repeat PR56–77.
2. Continue source-proof composition review in research_v1_krx_source_data_admission.py, research_v1_krx_investor_flow_lineage.py, research_v1_krx_investor_flow_coverage.py and the existing source/coverage-PIT audit contracts. NEW RESEARCH/ENGINEERING FOLLOWUP: lineage summaries report source fingerprint COUNT, coverage summaries report expected-scope fingerprint COUNT, and composed source admission accepts audit booleans without a defined linkage to the exact batch/payload/expected-scope artifact. Investigate the existing frozen meanings and callers before proposing a binding contract. Do not invent source_contract_fingerprint=batch_fingerprint, substitute self-hashes for independent provenance, or mark any real dataset admitted without authentic source/availability/economics evidence.
3. If a further independently reproducible input/snapshot bypass is found, implement fail-closed regression coverage and exact-head CI/research synchronization. Keep research ideas/HOLD/REJECT/INCONCLUSIVE out of Champion. No formal successor/preregistration chronology or empirical promotion was established here.
4. External blockers remain source C/D/E history/availability/provenance and exact status-event realized fill/recovery economics; independent prospective chronology/trust root; genuine LIVE broker-native whole-account/day/ownership/fill/fee/settlement evidence and frozen600observations/200dates/400fills/120near-capacity>=80%ADV0.0005 admission. Isolated handset preview UI is COMPLETE; original production compatible signing-key path and production push E2E remain OPEN. Do not repeat completed owner preview/default-key checks or fabricate substitutes.

Frozen prohibitions: preserve PIT/time/labels/H5/WF504-126-126/rolling1260/horizon purge+embargo/CPCV60/Top3/no-backfill/cost/slippage/partial-fill/NetEV/Precision@Selected/PF/MDD/ES95/99/model/threshold/acceptance/rejection/promotion rules. MASTER_OFF and readiness remain mandatory; real orders, funds movement or broker-account permission changes require separate explicit approval. No real-order implementation below Master Spec gates.

CONSUMED_FAILED_INVALID_V1_HOLDOUT cutoff2026-09-25/window2026-09-28..10-01 and failed/discrepancy/immutable lineage preserved:
result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82;
manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907;
receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63.
No delete/reset/re-evaluate/reseal/relabel/retune/private outcome parse. This checkpoint is not project completion or a claim of continuous background execution outside an actual run.

--- Historical authoritative records follow. ---

# Latest checkpoint — 2026-10-06 14:41 KST

Development tested code HEAD465dc1c166d80557532cbd8b9dc6652f57d28a23; research tested code HEAD806a38f9e75f9bbc27f25c651e7059ae30be473f. This documentation commit is their subsequent checkpoint; resolve the exact current branch HEAD from GitHub when resuming.

PR64/65 are now MERGED. Added strict SHA-256 string-format validation of receipt request_metadata_sha256, response_schema_sha256 and response_payload_sha256 before batching. Three malformed non-digest reproductions passed the original validator; all15 synthetic malformed cases now raise the domain error, preserving the canonical normal-receipt batch digest. Feature4e5656e3260247b23fdece16df15dc296af94f2a / 02f3e4faff617199c6af3887b228cff4675ad6f4. Actual PR runs37419576229/job112125697599 and37419584190/job112125722834 both107passed. Actual canonical merge CI: development37419627378/job112125858962107passed; research37419634579/job112125880559107passed; Official KRX Status Integrity37419634613/job112125881011634passed,5warnings; Worker Image Smoke37419634596/job112125880499SUCCESS. Local py_compile passed and direct malformed-case reproduction passed; local pytest is unavailable and is not claimed. No performance or genuine LIVE inference follows from these tests.

Master Spec Git blob798e658d2b3414f95ce648c58945425d9a579182 is unchanged from the prior development checkpoint and equal on current development/research branches. Actual development comparison from612f08b58c4e93fc9058f8b13f2300a9d4ac4c51 changes only four status/ledger/handoff documents, two source-integrity modules, their two tests and one offline workflow. No model, frozen threshold, PIT labels, trial, holdout or real-order code was changed. Runtime and Railway pins/volumes/deployments remain as the preceding read-only inventory states.

Schedule remains enabled with first planned2026-10-06 19:28:47Asia/Seoul, every5hours, existing task6ac3b166d460819186ae78ecc3c7444d. The latest direct owner request supersedes old cancellation records. No queue timestamp is asserted beyond the confirmed persisted schedule.

Resume immediately after completed PR56–65; do not repeat their changes, tests or owner preview installation. Retrieve latest actual HEAD/Actions/Research Ledger first, preserve concurrent changes. The prior next-step digest-format audit is COMPLETE; next independent review is exact receipt contract-field type/identity consistency at verify_receipt_fingerprint/_single_value and builder _require_text. Reproduce acceptance defects against canonical builders and synthetic rehashed receipts before changing implementation; avoid inventing any real provenance. External source/chronology/execution/signing/push blockers and all frozen prohibitions from the full record below remain OPEN. Project remains INCOMPLETE, MASTER_OFF. Normal development can continue; this checkpoint is not a claim that only external work remains.

--- Earlier checkpoint and authoritative historical evidence follow. ---

# Continuation reauthorized and KRX manifest validation — 2026-10-06 14:38 KST

This is the current continuation record; older disabled/manual-only instructions below are historical. The owner's latest explicit request at2026-10-06T14:28:47+09:00 reauthorized continued development and a repeating five-hour reservation. Existing automation6ac3b166d460819186ae78ecc3c7444d is ENABLED, Asia/Seoul, DTSTART20261006T192847, RRULE:FREQ=HOURLY;INTERVAL=5. Update and subsequent list both confirmed the exact persisted schedule; returned next_run_time=null, so no independent queue timestamp is claimed. No duplicate automation was created.

Project remains INCOMPLETE. Actual tested code HEAD before this documentation checkpoint:
- index-alert-position-regen-fix-v1@380bdc6a13c1cf05f853dd1b54a85a9fdc36de99.
- index-alert-research-v1@db86100a69f54f4187b47ad33a8f9af4431064a2.
- index-alert-server@8a68b01bca5d551d083ccda263df38d86fa54166, unchanged.
- Android build52377357c0c5260673fc823be3e8a0451abbea72 remains the already-installed isolated preview lineage; do not repeat its completed owner UI step.

Completed engineering:
1. PR56/57 strict downstream authority denial flags merged into development24a6cf0ab29860ca93744a8e9e4e4d6f3a8951a5 and research2105f1fd46ee755c1570f14c840db21c78d2d2fd. Canonical source-admission runs37418806472/37418809957 SUCCESS; research official status37418809991 SUCCESS.
2. PR58/59 require exact boolean False in each receipt authority field before batching, preventing malformed null/zero/empty values from being normalized into clean denial flags. Original local synthetic reproduction accepted18/24 malformed cases; fixed rejected24/24. Canonical False batch digest stayed96f98b7133ba80e0940e611e7daa30c4fde02c51d57d16d7af3f7131527865b6. Feature716b5989d0991ab2082073d6617e4944d33ed5af / cf4f2677e047f33dbe03ac994d0c445057adf87f; merges5fba774cf37e95d5c2e43f66bec1ad0c956a0957 / efee576fbfca7e1f0c464b4a0bb9db212b3f68a9. Actual PR CI37419032887/job112124012698 and37419110261/job112124251232 both66passed. Dedicated offline workflow now includes acquisition batch tests.
3. PR60/61 reject coerced boolean/string/fractional receipt counts, negative or malformed total rows, and dictionary/nested/non-SHA receipt collections. Six malformed rehashed cases demonstrably passed the original local validator; fixed raises the domain error. Featureb73efbb2ce3c13785c9183384df6bc7fa612668d / f0d124a595a2281a5abab23788f5a266172b5e2c; merges78fe5d1cb0b562f135e25b665aec71530f54b54f / 5bceba332e4b1660128dbd2c3f95a57728775d52. Exact PR CI37419195465/job112124509761 and37419204124/job112124536268 both84passed; canonical37419253415/37419259371 SUCCESS; official research37419259349 SUCCESS.
4. PR62/63 require non-negative integer response_rows at the receipt verifier before aggregation, and remove truncating/string/bool integer coercion. Canonical zero rows remain valid. Feature969e5a723320c9db6e8cf1665cd71a1672af405b / a27b66c24b9c865b2ac3094518fa8af7a0df9634; merges are the current tested code HEADs above. Exact PR CI37419291500/job112124805440 and37419298863/job112124828775 both92passed. Canonical source runs37419363435/37419368678 SUCCESS; image smoke37419368685 SUCCESS. Official research run37419368669 must use the evidence recorded below, never an assumed result.
Local pytest is unavailable; local direct Python reproductions used synthetic frames only. CI test counts are offline engineering checks, never empirical KRX/genuine LIVE/Alpha evidence.

Fresh Railway read-only inventory/config/logs:
- Projectd1c1a050-b7d6-41ce-b300-13c20f82a20a, production83d5840b-270e-4d3f-a941-a37fd4a55ff7;8services,3volumes, no staged changes. Legacy backend/push retain September23 FAILED deployments; db-query-readonly has no deployment. Do not claim the whole project is healthy.
- Runtime37902fde-ca05-43e0-bc76-278992bf7732 deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, pin8a68b01bca5d551d083ccda263df38d86fa54166; volume f96f985a-8aba-41ef-88df-f76999c4ff0c /data500MB. Startup still performs two read-only audits before uvicorn. Latest actual logs2026-10-06T05:31:42Z show explicit ETF_CLOSED_PROXY/extended_estimate=true/actual_extended_trade=false and quote fallback; these are not official KRX or native fill evidence.
- PIT225f2279-d728-4e1a-a3f3-2447ff0f9dc1 deployment7021473a-d9a6-4711-b496-a359fd9bb0c8 SUCCESS; pin26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15; /pit5000MB volume03f389e5-5030-46a9-bfa5-dd8aa3dc24fa. Start python -S -B audit_retired_validation.py; restart NEVER. Existing log verifies all three preserved hashes, model_executed=false, outcome_metrics_parsed=false, private_artifacts_mutated=false, real_orders_sent=false; retired lineage stages remain blocked.
- KRX003812ee-102b-42b6-bda4-36925885b428 deploymente56cf101-15c5-478e-ae67-228585013ef0 SUCCESS; pinef95e7857f692fda3855390e918e165487624881; /data5000MB volume61610fae-dc0c-493e-9920-eb3cef4cea86. Start read-only integrity audit/restart NEVER. Existing stored log14495 verified checkpoints/14425 unique objects/errors{}; coverage/PIT/performance/holdout/LIVE authority false. Storage integrity does not close source admission.
- DEMO6be2d733-2a59-4a12-96e3-b6d869db3b97 latestcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9 SUCCESS, no volume. No deployment/restart, secret, account permission, raw KRX acquisition or broker/order mutation was performed this turn.

Remaining work and exact resume:
1. Fetch actual branch HEADs and this checkpoint's commit before touching any branch; preserve concurrent Research Ledger changes. Check canonical runs at new documentation HEAD and confirm no failed/pending workflows. Do not rerun completed PR56–63 work.
2. Continue receipt/batch/PIT provenance review at research_v1_krx_acquisition_batch.py::verify_receipt_fingerprint and _single_value: receipt request/schema/payload digest formats and exact contract-field types remain unaudited here. First reproduce any actual acceptance defect against canonical builders and rehashed synthetic malformed receipts; only then implement fail-closed validation with offline regressions and research sync. Self-rehashed metadata proves neither authenticity nor true market data.
3. Reconstruct latest Ledger/Status and examine only contract-admissible Challenger results. Latest reviewed research ideas (including generic first-approval/patent/legal episode ideas) remain HOLD/preregistration/source-gated, not ACCEPTED_CHALLENGER; none applied to Champion.
4. External blockers remain source C/D/E full history/availability/provenance and exact status-event realized fill/recovery economics; independent prospective preregistration chronology/trust root; genuine LIVE broker-native whole-account/day/ownership/fill/fee/settlement evidence and frozen600observations/200dates/400fills/120near-capacity>=80%ADV0.0005 admission. Isolated preview UI is COMPLETE, but compatible original production signing-key path and production push E2E remain OPEN. No fabricated substitute, holdout access or real-order implementation below Master Spec gates.
5. Never alter existing PIT/labels/H5/WF504-126-126/rolling1260/horizon purge+embargo/CPCV60/Top3/no-backfill/costs/slippage/partial-fill/NetEV/Precision@Selected/PF/MDD/ES95/99/model/threshold or promotion/rejection rules. Old rounded immutable fill bindings are not automatically rewritten/admitted.

CONSUMED_FAILED_INVALID_V1_HOLDOUT remains failed; cutoff2026-09-25/window2026-09-28..10-01 and immutable discrepancy/lineage preserved:
- result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82;
- manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907;
- receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63.
No delete/reset/re-evaluate/reseal/relabel/retune/private outcome parse. MASTER_OFF/readiness gates remain mandatory; real orders, money transfers and broker-account permission changes require separate explicit approval. This checkpoint and scheduling are not project completion.

Final canonical job-log evidence: development37419363435/job11212503379792passed; research37419368678/job11212505030392passed; official research37419368669/job112125050157619passed,5warnings. All SUCCESS. Warnings are reported as emitted; no new empirical evidence or promotion is inferred.

--- Historical records follow; later dated explicit owner instructions above supersede old scheduling cancellation. ---

# Preview handset UI observation — 2026-10-06 11:34 KST

The owner installation/screen-observation step is COMPLETE. Do not ask to repeat preview installation, original4.7 APK inspection or the absent default debug-key check.

Owner supplied a handset screenshot with title "IndexAlert 4.8 검증", separate-app/no-notifications/no-automation explanation, visible unavailable text "현재 자동매매를 사용할 수 없습니다." and refresh button. Screenshot SHA256a7751574a5326dc5da24eb74deeb115c4385e9cedc8f59db88c10378e48522b8. This is owner-reported screenshot UI evidence: exact installed APK bytes and raw HTTP payload were not independently captured. The delivered canonical preview artifact remains11385867401/run37402569974/head52377357c0c5260673fc823be3e8a0451abbea72/APKSHA3e873425ce04cee59e10c0886fc61695d7e91d3b39610108b4874dd672a18379. Do not conflate build proof with runtime byte attestation. Isolated preview UI observation is verified; production4.8 signing continuity/push receipt/E2E and full automated trading readiness remain OPEN/false.

Observed pre-record branches: dev4da4c45b91c9f09362dc156428fb984fa70d7993, research3ca93d4c164bdefe68ddccd19c7b476f57be4e87, Android52377357c0c5260673fc823be3e8a0451abbea72, server8a68b01bca5d551d083ccda263df38d86fa54166. Last actual doc CI: dev7bbc3d/37402974916 PASS76; research99d52d/37403055616 PASS72 and37403055610 PASS548/5warnings. New documentation is not yet tested merely because those previous runs passed.

Railway refreshed: no pending work;8services,3existing legacy issues,0recent failures. Runtimeeaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS1running0crashed; completed PIT/KRX/DEMO deployments remain SUCCESS0running. No service/source pin/volume/credential/config/deployment changes.

Exact next continuation: recover actual refs/Actions and latest authoritative records; mark ONLY the isolated preview owner-UI step closed. Preserve original4.7/data and the production signer/push blocker. Continue only contract-justified independent source/PIT/status-economics/preregistration/admission/native account/execution evidence work; do not manufacture trust roots, a new successor/admission or genuine LIVE samples. No additional handset action is required for the completed screen check. Existing frozen criteria and consumed failed invalidv1 result/manifest/receipt hashes below remain untouched; no orders/funds/account-permission changes, private outcomes, retune, cutoff/model/threshold/promotion-rule changes. Project remains INCOMPLETE.

# Development-room synchronization — 2026-10-06T02:13:03.080Z

Development documentation7bbc3dda222b12a3eb0c29200ae8534566a99f2e records actual owner-reported installed4.7 public APK identity, absent standard local debug key and completed separate readonly preview engineering. Android PR53 merged52377357c0c5260673fc823be3e8a0451abbea72: com.indexalert.preview4.8-preview preserves original com.indexalert.app4.7; no Firebase/WorkManager/registration/orders. Actual canonical preview37402569974/job112072791477 and original-app regression37402570020/job112072791464 PASS4 each with SDK APK verification; unsigned original release hash remainsf8e3c9e32355355ea412a0a4a55ddd8db9afff41ea9f6399ed617ceec6370e4b. Exact canonical preview APK hash3e873425ce04cee59e10c0886fc61695d7e91d3b39610108b4874dd672a18379/artifact11385867401; owner UI observation is still OPEN and cannot establish production push, signing continuity or trading readiness. Development PR54 wireless host-audit mergebe589692fd4e38f4f6292d77b0f2773af4469b5c actual canonical37402515132/job112072617582 PASS10 synthetic/mock tests. Development checkpoint16246e1dd64b207877d5ab034e0c1dd67117c58a actual37402813251/job112073573356 PASS76. Do not turn these engineering counts into research/empirical evidence.

No new accepted empirical Challenger, registration chronology/admission, official source/PIT/status economics, whole-account/fill/fee/settlement or genuine LIVE observations were established. Master Spec and Champion unchanged. Research previously observed HEAD1edb94a5af5192556d4ae1a137e20565168b6ece; fetch resulting documentation HEAD on resume and confirm relevant current CI rather than claiming a future pass. Current runtime source8a68b01bca5d551d083ccda263df38d86fa54166/deploymenteaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS1running0crashed; PIT/KRX read-only completed workers and all private volumes/pins intact, no duplicate restart/deployment. Pending Railway work[]/8services/3legacyissues/0recentfailures. Actual logs and immutable consumed holdout hashes were re-read only, without outcome parsing.

Frozen consumed failed invalidv1 cutoff2026-09-25 remains retired; resultSHA30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82, manifestSHAff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907, receiptSHA3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63 unchanged. No re-evaluation/reset/reseal/relabel/retune/cutoff/model/threshold/promotion-rule changes; no synthetic/DEMO as genuine LIVE. Actual stock orders/funds/broker-account permission changes remain disabled and separately authorized.

Exact research continuation: re-fetch current Ledger/Status/Master Spec, inspect only contract-eligible prospective registration/source evidence; do not adopt ideas/REJECT/INCONCLUSIVE or invent independent admission/availability/native executions. Consult the latest development records before repeating owner steps. Preview device observation can proceed independently of research evidence gates and closes only isolated UI verification.

# Latest implementation and exact resume — 2026-10-06T00:37:52Z

This supersedes the prior current-state header below. Project remains INCOMPLETE; all frozen evidence/authority boundaries remain mandatory. Retrieve live branch refs: these records cannot contain their own future content-derived commit SHA.

- Observed implementation HEADs before this record: dev **1ee210e218c3970a0304c1bd6984a55c9759f81c**; research **0830f769ff6b62d39b9091814091d9fd07b22d6c**; Android **aaac565a7dc99f36b369b36cadabaf4e2faf1bf5**; server HEAD/Railway pin **8a68b01bca5d551d083ccda263df38d86fa54166**. Broker-safety code remainsc0c05d485c2cba3f66cfb969af6c4a1309186269 with actual236/93 suites as recorded below; no rerun or broader-current-suite claim is made for unchanged code.
- Completed **PR50** research: feature7c980a996686311cb09b42d635837af970419f28, merge0830f769ff6b62d39b9091814091d9fd07b22d6c; actualfeature37394296777/job112046476736 PASS31, canonical37394389229/job112046775142 PASS31. **PR51** dev equivalent: feature883d8650239b161827b866604c679bed97a9e9a3, mergef0d72597caf6a04666186ebf5461a57b68c4ca8f; actualfeature37394305040/job112046504316 PASS31, canonical37394392746/job112046785958 PASS31. Reproduced malformed required preregistered_at values (not-a-time/date-only/boolean/object) yielding structuralACCEPTED_CHALLENGER. Fixed offset-aware ISO datetime input syntax under existing mandatory-field contract; existing valid offsets and canonical JSON fingerprints retained. Four new test methods; no actual/historical trial re-evaluation, outcome access, policy/cost/model/cutoff/threshold/acceptance-rule changes. This DOES NOT verify immutable preregistration-before-outcomes chronology; independent registration/admission evidence remains OPEN.
- Additional actual research0830 postmerge verification: internal completeness37394389871/job112046777073 PASS39unittest +16pytest; orchestrator37394389152/job112046774117 PASS23; successor37394389143/job112046774202 PASS31. These counts are suite-specific, never summed as independent empirical evidence. Previous docs checkpoints23cefb71099dda91c983e93b8a18488d231e6254 and08c3c087af013743b98c3e1cff0f8ae813b02a6e actually PASS76(dev37394021027/job112045566891),72(research37394026174/job112045585126),548/5warnings(KRX37394025536/job112045582603). Frozen hard gates remain open despite engineering CI success.
- Completed **PR52**: initial feature1f9deeaa718155fe0f65239ca806a6972ba069b4, finalfeature4e6ef885a9e57c89c6efc1a6acc4ae422253145e, merge1ee210e218c3970a0304c1bd6984a55c9759f81c. Actualfeature37394784569/job112048045885 PASS7 at00:35:17Z; canonical37394851843/job112048265321 PASS7 at00:36:06Z; local7 PASS. Installed-only audit requires NO candidate APK and NO signing key: candidate=null/comparison=false/signing-continuity=false; exit0 is successful public APK observation only, never installation authority. Added leading package identity guard after a SYNTHETIC ambiguous metadata string showed old-parser identity shadowing; no malicious real APK/handset attack is claimed. Existing signed-candidate comparison remains separate, no install/uninstall/appdata/key/broker/order access. Actual local adb availability check returned absent; no connected handset or actual SDK handset inspection is claimed. Owner-side steps are ready in INDEXALERT_ANDROID_UPDATE_VERIFICATION.md; keys/passwords must never be uploaded.
- Android app remains4.8-48, actual canonical SDK build proof37376946309/f772 and artifact IDs/digests/signers below. Currentaaac differs from verifiedf772 only in the separate historical-signing workflow. Real SDK verification found historical4.7/candidate4.8 debug signer mismatch; do not treat per-run debug keys as stable update identity. Actual installed signer and4.8 exact-device/build physical push/readinessE2E still unobserved. Existing4.7 receipt is historical and not4.8 proof. No app deletion or data migration has been authorized.
- Research synchronization just refreshed: economics branch **5aefb98988f7b4ccf7c95e7cdf2a671a7bdfee7e** latest commit2026-10-05T02:59:11Z; Ledger actually reread, no independent eligible successor/admission found. Earlylive draft **1d81eb526f59b87c528d63be9e3883e0f76fedf6** unchanged; immutable history **585d763542b2fbbdc3f928621f679fb14c8c3bbf** unchanged. Branch inventory pages1/2 and actual last-commit timestamps checked for related probability/research/ablation/authority/provenance/physical branches; their older engineering/legacy studies are not newly accepted Challenger evidence. No REJECT/INCONCLUSIVE/idea operational adoption or Champion overwrite.
- Railway latest actual read unchanged: runtimeeaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS1running0crashed, pin8a68 and/data volume f96f985a-8aba-41ef-88df-f76999c4ff0c; DEMOcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9 SUCCESS0running0crashed/no volume/pinc2d497; PIT7021473a-d9a6-4711-b496-a359fd9bb0c8 SUCCESS0running0crashed/pin26f56e63,/pit03f389e5-5030-46a9-bfa5-dd8aa3dc24fa; KRXe56cf101-15c5-478e-ae67-228585013ef0 SUCCESS0running0crashed/pinef95e785,/data61610fae-dc0c-493e-9920-eb3cef4cea86. Full pins/commands/report timestamps retained below. No pending/staged changes, no duplicate deploy/request/retired evaluator run, no service/volume/credential changes. Startup TABLE_MISSING and DEMO_CONFIGURATION_ONLY remain non-admission, not fabricated zero/genuineLIVE; actual8a68 public smoke199/unavailableMASTER_OFF proof below retained.
- Remaining external/evidence blockers: owner's actual installed public APK signer observation and compatible existing local signing identity/4.8 device receipt; official source expected scope/PIT/status-economics; independently admitted prospective successor/immutable chronology; genuine native account/day/whole-account/ownership/execution/actual fees and sales settlement. Synthetic parser/governance/journal tests cannot supply those. MasterSpec14 still forbids real Kiwoom order implementation/activation below Alpha gates; absent independently specified accounting/admission cannot be invented to enable controls. No actual stock orders, funds moves or broker-account permission changes.
- **Exact next resume:** fetch live dev/research/server/Android/related refs + latest Status/Continuity/Handoff/Actions first. Confirm these new records' docs execution/source CI without duplicating active runs; distinguish last tested implementation from documentation HEAD. Review immutable preregistration/independent gate-admission contracts and source/native-account evidence backlog; syntax proof does not close chronology. Only implement justified independent engineering under current contracts, keep any unsupported trust root/empirical gate fail-closed, and record new research gaps. When the owner provides actual installed-only audit output, validate public package/version/certificate provenance before deciding a compatible signed update; never ask for key/password uploads or uninstall by default. Then separately require4.8 exact handset receipt/UI verification. Preserve completedworkers/currentruntime pin; no redeploy for docs/host-tools/research-only changes. Continue independent work while handset path is blocked.
- Frozen **CONSUMED_FAILED_INVALID_V1_HOLDOUT** unchanged: cutoff2026-09-25, consumed2026-09-28..10-01/passedfalse. ResultSHA30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82; manifestSHAff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907; receiptSHA3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. Preserve discrepancy/history/immutable lineage. No reset/delete/re-evaluation/reseal/relabel/retune/private outcome rescue. PIT/labels/WF/Purged/CPCV/purge/embargo/cost/slippage/partialfill/NetEV/Precision/PF/MDD/ES95/99/holdout/model/threshold/promotion/rejection remain unchanged. Synthetic/DEMO never genuineLIVE. Environment/run limits are not project completion; future continuation restores this exact latest authoritative state.

# Current authoritative continuation — 2026-10-06T00:25Z

This entry supersedes previous current-state entries; historical failures/evidence remain intact. Project is incomplete. No milestone success is a reason to enable trading or stop independent work.

- Observed refs before recording: dev17982e1ba1f070159173590f57b37dc00bc5fbb5 (PR49 merge; broker-safety implementationc0c05d485c2cba3f66cfb969af6c4a1309186269 unchanged/full236 and durable93 actualPASS); research6ce8e91382f678d206d19fa3ac01181924047d61; Androidaaac565a7dc99f36b369b36cadabaf4e2faf1bf5; serverHEAD/pin8a68b01bca5d551d083ccda263df38d86fa54166. This content-derived record cannot embed its own resulting SHA: fetch actual branch HEAD on every resume. PR43 research exclusion hardeningc691 merged/PASS27; no accepted empirical successor.
- Completed Android canonical build proof37376946309/job111988355734 SUCCESS on exactf772ce57d8ef9fd313797559b9d0a37aa417f7c0. Actual4 JUnit executions/0failures-errors-skips; com.indexalert.app4.8/code48. DebugAPK SHA2564e254e6fd7840e07f3f281918da5e013e51ae9af28d79c24eea3d9a82967e6f0, signer96c9cfd617adeca8003ba60db7d5dcbe0e5792add2a3cb7112e5d22ed6cb09a7. Unsigned releaseSHA256f8e3c9e32355355ea412a0a4a55ddd8db9afff41ea9f6399ed617ceec6370e4b,8362877bytes, artifact11372392458 ZIPdigest1a5711adaa573d0fee2910ed35a079ca002936670fe7ee55f9cbfa7596b51445. Proof artifact11371549087 ZIPdigest0dd319c289d805930efffa9be91989d70c85628c1df558be620fa99683c4075e. Actual comparef772..aaac shows ONLY separate audit workflow added; no app source change requiring another build.
- Completed PR48 feature92381b19106c385167af702d42a8b173db438963/mergeaaac565a7dc99f36b369b36cadabaf4e2faf1bf5, actual37377380596/job111989964638 SUCCESS. Downloaded real immutable v4.7 artifact11158994269 and v4.8 artifact11371148102 inside SDK CI; source/name/ID/digest verified. Historical actualAPK SHA2569e1b72432b44f41a04c7f502d98502d3c77d69ec451718b8da34a260269eca01, signerecb7486e3ce65fba42f6bf55ff8359abd0ee7d8268c8305e248340c84443c6fa. Candidate actualSHA2566ae4cc5f6ca503461396c9ca69dd19866d5f3077375b923a41162b9a543e7855, signer24d1f8adf0b2ed7ad2d47c2f7d957105ce8297fa76b6620d908549c22286ad23. SIGNERS DIFFER. Actual signing report artifact11372436925 ZIPdigest42fac3962f05fdb1e32d4b6679177dae690e572a24c9426e3cf281d78f7c622b. Old physical audit DebugSHA0aec298a0d0276f8a5e40dc22429b595e8bb11636f22ceeea75cb018a4a7e411 is GitHub ZIP digest, not contained APK hash. Preserve original record; distinguish levels. None of these historical artifacts proves the signer actually installed on a handset. Local large APK download stalls were real; SDK CI downloads succeeded. A later local executor capability check succeeded; no permanent tool/quota blocker is claimed.
- Completed PR49 feature78946ae1b768ba619ee9df0edd62989bda6a480c/merge17982e1ba1f070159173590f57b37dc00bc5fbb5. Local4 synthetic tests PASS, actualfeature37393595994/job112044173878 PASS4 (00:21:50Z), exactcanonical37393665836/job112044398471 PASS4 (00:22:38Z). verify_indexalert_installed_apk.py reads only one owner-authorized USB physical handset's public base APK and compares actual SDK package/version/signers. No device identifier/appdata/key/credential/account/broker access; no installation/uninstall/permission changes. Wrong package, ambiguity, unauthorized device, unsigned APK/tool error fail closed. Tests are MOCKED/SYNTHETIC, not actual device evidence. Instructions and artifact provenance are in INDEXALERT_ANDROID_UPDATE_VERIFICATION.md. Existing4.7 physical E2E is not4.8 E2E. Installed signing continuity remainsfalse/unobserved. If a signer differs, retain app/data; use the independently verified existing signing identity locally, never upload keys/passwords or propose an unapproved uninstall workaround.
- Current checkpoint actual tests: dev8b50 execution integrity37377109497/job111988974174 PASS76; research6ce8 execution integrity37377115083/job111988994376 PASS72; research6ce8 KRX/source code integrity37377115348/job111988995745 PASS548/5warnings. These are code-path checks, not official source/PIT/economics/LIVE admission. Previous dev runs37372192433/37371119084 report workflowfailure but their actual jobs111971838055/111968218737 were CANCELLED BEFOREsteps; no new test failure inferred. Previous genuine obsolete-holdout-assertion failures are retained below.
- Railway refreshed2026-10-06T00:22Z: publiceaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS1running0crashed/pin8a68, /data500MBf96f985a-8aba-41ef-88df-f76999c4ff0c. Actual startup20:36:35Z ledgerTABLE_MISSING (not fabricated0) and DEMO_CONFIGURATION_ONLY; no native LIVE/admission/order authority. Actual new-pin publicsmoke37370547415 attempt3/job111977030114 PASS199/publicruntime_revision8a68/unavailableMASTER_OFF all9flagsfalse. DEMOcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9 SUCCESS0running0crashed/pinc2d497c76cc43a1b59a17f04c5ffd1d67a88c02a, no volume, completed1page0holdings; no restart. PIT7021473a-d9a6-4711-b496-a359fd9bb0c8 SUCCESS0running0crashed/pin26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15,/pit5000MB03f389e5-5030-46a9-bfa5-dd8aa3dc24fa. KRXe56cf101-15c5-478e-ae67-228585013ef0 SUCCESS0running0crashed/pinef95e7857f692fda3855390e918e165487624881,/data5000MB61610fae-dc0c-493e-9920-eb3cef4cea86. Readonly start commands/NEVER worker restarts preserved. No pending/staged changes. Legacy offline services untouched. No server redeploy for Android/host-tool/docs-only work.
- New research follow-up: Continuous Research Contract rule8 requires preregistration-before-results; current evaluator summarizes represented booleans/fingerprints but cannot prove immutable registration chronology. Need independent registration/admission receipts in future research governance; do not fabricate timestamps or change historical trial outcomes, criteria or promotion authority. This is OPEN evidence/architecture work, not a new accepted Challenger.
- Remaining/open: actual compatible signing identity/installed-handset inspection and4.8 physical notification/readiness E2E require the owner's device/material; no handset is attached here. Official historical expected-scope/PIT availability, affected-position event economics, independent eligible successor/chronology, genuine native account/day/whole-account/ownership/side/execution identity and actual fee/sale settlement remain open. Frozen canonical pretrade/capital/stop integration cannot be marked complete from offline236/durable93 tests. Re-read MasterSpec14 before any broker-order implementation; Alpha below promotion prerequisites means real Kiwoom ordering remains forbidden. No new independently accepted result was found in current Ledger/Status.
- Exact next resume: fetch all live refs/Actions/records before editing; confirm new docs execution/source CI (do not restart queued jobs). Review independent registration chronology and canonical source/native-account admission contracts; implement only justified engineering under those exact contracts, never infer evidence from self-authored flags. Preserve server8a68 and completedworkers. For Android use verified unsigned artifact provenance, wait for an actual owner-provided public installed-signer audit/compatible signed candidate before any device update, then existing exact-device/build receipt verifier4.8-48 and readinessUI observation. Continue other independent eligible work while that path is blocked; record every new research issue.
- Frozen CONSUMED_FAILED_INVALID_V1_HOLDOUT: cutoff2026-09-25/window2026-09-28..10-01/passedfalse. ResultSHA30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82; manifestSHAff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907; receiptSHA3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. Manifest/result discrepancy and immutable lineage585d763542b2fbbdc3f928621f679fb14c8c3bbf retained. Never reset/delete/re-evaluate/reseal/relabel/retune or rescue failedv1; no private outcome parsing. All PIT/time/labels/WF/Purged/CPCV/purge/embargo/cost/slippage/partialfill/NetEV/Precision/PF/MDD/ES95/99/holdout/model/threshold/promotion/rejection unchanged. No synthetic/DEMO evidence presented as genuineLIVE, no actual orders/funds/broker-account permission changes.


## Current authoritative continuation — 2026-10-05T21:37Z (supersedes pending PR43/46 entries below)

- Canonical implementation: dev c0c05d485c2cba3f66cfb969af6c4a1309186269; pre-record HEAD c670026f57c32585daf2dab48fba84f4405fe306. Research HEAD c691aac95355ed94cc2cecaab1dfbb086bbceabe. Server HEAD/pin8a68b01bca5d551d083ccda263df38d86fa54166. Android HEADf772ce57d8ef9fd313797559b9d0a37aa417f7c0 (PR46 merge6cefecd758da3f35be2f99d5c55d7e38fd589473; PR47 mergef772). Record commits cannot embed their own content-derived SHA: fetch live branch first at resume; previous tested heads remain distinct.
- Completed PR43 exclusion input safety: actual feature37370827400 attempt3/job111978033282 PASS27; postmerge37374769588/job111980474628 PASS27. Earlier before-step cancellations preserved; no empirical Challenger admission or frozen criteria change. PR44 dev equivalent also PASS27 feature/postmerge.
- PR45 actual canonical full236 PASS37372530271/job111972964752; durable93 PASS37372530315/job111972964700. Replay ZIP11370942418 hash65b6301dca275462e44932c5cbf6e53618085599b84d6c3e966b11deaf27926a independently downloaded/parsed:8shadow+6protected-capital synthetic scenarios, no real settlement/LIVE/promotion evidence.
- PR46 Android4.8/code48 merged. Feature37371912963 attempt2/job111976296312 and canonical37375781875/job111984056330 actualSUCCESS: tests task, debug and unsigned release builds/uploads. Four exact JUnit executions are proven separately by PR47 below; previous quiet Gradle log alone did not establish count. Original4.7 physical proof is NOT4.8 proof.
- PR47 workflow-only build-proof feature9b39efcb7977dfa77c54f3274d17a90469cdd194; actual37376198533/job111985591013 SUCCESS. 2026-10-05T21:33:59.0436482Z report:4 tests,0failures/errors/skips; actual APK com.indexalert.app4.8/code48. Debug11835131bytes SHA2566ae4cc5f6ca503461396c9ca69dd19866d5f3077375b923a41162b9a543e7855; verified signerSHA25624d1f8adf0b2ed7ad2d47c2f7d957105ce8297fa76b6620d908549c22286ad23. Unsigned release8362877bytes SHA256f8e3c9e32355355ea412a0a4a55ddd8db9afff41ea9f6399ed617ceec6370e4b, unsigned verified as expected. Proof artifact11372376207 ZIPdigest00fde249fd373fd2d073831e0a635a8d0b8b003508cda1bca861fea204c5bc13. Source head9b39, checkout PR merge3e78bb4a48e3ceef4abf23ba04896b64247c34d9. Physical E2E/installed signing continuity/broker requests/orders/LIVE/frozen changes allfalse. Local large APK downloads stalled before files arrived; remote SDK CI proof is real, local APK inspection is not claimed.
- Railway actual refreshed2026-10-05T21:36Z: public deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS1running0crashed; no pending/staged changes. Runtime8a68 actual199 tests +public v32smoke37370547415 attempt3/job111977030114 SUCCESS, runtime revision bound21:07:45Z, unavailable MASTER_OFF all9authority/mutation flagsfalse. Runtime /data volume f96f985a-8aba-41ef-88df-f76999c4ff0c retained. DEMOcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9 SUCCESS0running0crashed/no volume, pinc2d497c76cc43a1b59a17f04c5ffd1d67a88c02a; completed1page0holdings preserved, no restart. PIT7021473a-d9a6-4711-b496-a359fd9bb0c8 and KRXe56cf101-15c5-478e-ae67-228585013ef0 SUCCESS0running0crashed; /pit03f389e5-5030-46a9-bfa5-dd8aa3dc24fa and KRX/data61610fae-dc0c-493e-9920-eb3cef4cea86 retained. Legacy offline services untouched. Startup ledger TABLE_MISSING remains, not fabricated as0; DEMO configuration is not authenticated LIVE evidence.
- Remaining: exact canonical PR47 postmerge CI not yet observed; verify by actual source HEAD/run/log and store report. Continue independent engineering/source-integrity work after that; do not stop on this milestone. v4.8 actual device/push/readiness E2E and installed signer continuity still unobserved; do not uninstall app or claim compatibility without actual signer proof. Native actual account/day/whole-account/ownership/execution IDs/fees/sale settlement, official source/PIT/economics and independently admitted successor remain blockers. Research economics5aefb98988f7b4ccf7c95e7cdf2a671a7bdfee7e remains historical negative; no REJECT/INCONCLUSIVE adoption. Real ordering forbidden by Master Spec14 while Alpha gates below criteria.
- Exact resume: fetch dev/research/server/build refs and latest Status/Continuity/Handoff; find canonical f772 build Actions (do not duplicate active jobs); read actual proof log and artifacts, then source/engineering backlog under unchanged gates. Keep runtime8a68 pin; no runtime deploy needed for Android/docs/test-only work. Check current Railway pending work before any service action.
- Frozen CONSUMED_FAILED_INVALID_V1_HOLDOUT: cutoff2026-09-25, consumed2026-09-28..10-01, passedfalse. Preserve resultSHA30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82, manifestSHAff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907, receiptSHA3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63; manifest/result discrepancy retained. Never delete/reset/re-evaluate/reseal/relabel/retune/parse outcomes to rescue failed v1. Immutable lineage585d763542b2fbbdc3f928621f679fb14c8c3bbf retained. All PIT/labels/WF/Purged/CPCV/purge/embargo/cost/slippage/partialfill/NetEV/Precision/PF/MDD/ES95/99/holdout/model/threshold/promotion/rejection unchanged; synthetic/DEMO is no genuine LIVE. No actual orders/funds/broker permission changes.

# Current research continuation — 2026-10-05T20:18:26.846Z

## Verified smoke and current resume supplement — 2026-10-05T21:12:00Z

Current refs actually observed before this record: dev **98b008561abac0ea69283b62179cc96dcb1e47cb** (last tested implementationc0c05d485c2cba3f66cfb969af6c4a1309186269), research **f20848576a11bbf2ff276b1b7e385514fcf13ef0**, server **8a68b01bca5d551d083ccda263df38d86fa54166**, Android build5154ef7943353791f615622394523ecd52ef8b0f. Retrieve live refs on resume; record commits advance document HEAD without changing tested code.

**New-pin public verification DONE:** actual v32 smoke **37370547415 attempt3/job111977030114 SUCCESS**, exact8a68 workflow source and actual runtime_revision8a68; full **199 tests**,2026-10-05T21:07:44Z, real API output21:07:45Z GET-only readiness **BROKER_AUTOMATION_UNAVAILABLE / MASTER_OFF**, all nine order/provenance/account/persistence/mutation/frozen flags false, required controls exactly automation_enabled/max_automation_capital_krw. Existing build-bound push contract also passed in the same actual production step. Prior jobs111966304367 and111971908806 cancelled BEFORE any steps; preserved, not test failures. Successful runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00/8a68 pin/1running0crashed and both readonly startup audits remain as below. No duplicate redeploy/DEMO/PIT/KRX rerun, account or order activation.

**Dev current full postmerge DONE:**37372530271/job111972964752 on exactc0c05d485c2cba3f66cfb969af6c4a1309186269 **236 pytest PASS**,21:04:15Z; canonical durable93 and governance27 actual PASS already recorded below. **Research latest KRX/source-code integrity:**37373429847/job111975967124 on exactf20848576a11bbf2ff276b1b7e385514fcf13ef0 **548 PASS /5warnings**,21:03:15Z. Code-path tests provide no official source/PIT/status-economics/alpha/LIVE gate closure. Latest docs execution CI37373424226(dev98)/37373429906(researchf208) remain QUEUED at last observation, not new proof.

Still active, do not duplicate:
- Research **PR43 OPEN**, exactbf17231fe6e48aaf020ff0085c6781dec201bf6f, run37370827400 **attempt3/job111978033282 QUEUED**. Initial111967221633 and second111972553851 cancelled before any steps; explicit relevant-only retries. Same exact source fix is local27-tested and dev PR44/27-CI/postmerge27 merged, but research counterpart is NOT yet merged or CI-passed. Wait for actual expected-head success, then merge43 and verify postmerge; keep Champion and frozen criteria unchanged.
- Android **PR46 OPEN**, exacta0ddaab8ed93f4ae39c17140ff2aa94201a8f4ed/candidatev4.8-code48, CI37371912963 **attempt2/job111976296312 QUEUED**, initial111970897295 cancelled before any setup/build steps. Four Kotlin test methods and bounded read-only availability display are prepared, but no local Android compiler/Gradle or actual CI compile/JUnit/APK result exists yet. Never claim v4.8 artifact or handset E2E; old auditedv4.7-code47 proof remains distinct. On actual successful build inspect candidate artifacts/version and test result, merge expected head, recheck canonical build and separately track genuine new handset verification.
- Current-source docs integrity and research postmerge queues may be polled; retry only real cancellations still relevant, never queued jobs or superseded old heads. Reconstruct all latest statuses from GitHub/Railway before new work. The project remains incomplete; remaining external/admission/account/settlement/pretrade/Kill and two-control accounting contract gaps below are unchanged. Transient CI queueing is not a user-only blocker or a reason to disable continuation.

**CONSUMED_FAILED_INVALID_V1_HOLDOUT** unchanged: result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82 / manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907 / receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. No private outcomes parsed, failure reset/re-evaluation/reseal/relabel/retune, Master Spec/model/threshold/Champion or frozen numerical/statistical/market/execution/promotion criteria changed. No genuine LIVE evidence manufactured, no actual stock orders/funds/account-permission changes. All existing restrictions and exact next steps below remain in force.



## Current authoritative development/research synchronization — 2026-10-05T21:00:00Z

Verified refs before this documentation checkpoint: development `index-alert-position-regen-fix-v1` **c0c05d485c2cba3f66cfb969af6c4a1309186269**; server `index-alert-server` **8a68b01bca5d551d083ccda263df38d86fa54166**; research `index-alert-research-v1` **32fb10dbffb74f6fa82d88fa42e0d88d092c7159**; Android `index-alert-build` **5154ef7943353791f615622394523ecd52ef8b0f** (v4.7/code47); isolated DEMO **c2d497c76cc43a1b59a17f04c5ffd1d67a88c02a**. Fetch live refs again at resume; this checkpoint records the exact observed pre-record HEAD and cannot embed its own content-derived commit SHA. Historical checkpoints below are superseded only for current state, not erased.

Completed this continuation, with actual evidence:
- PR35 merge0f8bf39b0527548e10598a6c3ff1deee08404635: server GET-only unavailable automation readiness/no account read/control persistence/order authority,6 focused HTTP and199 full regression tests; actual production smoke37369433070/job111962600050 SUCCESS on runtime revision0f8,2026-10-05T20:29:09Z, BROKER_AUTOMATION_UNAVAILABLE/MASTER_OFF/GET-only OpenAPI/all authority and mutation flags false.
- Real secondary v32 dependency failure37369223920/job111961876601 (missing test-only httpx; public step skipped) fixed by PR41 featuref3b61aa91f8427412abf49d8a5b612dcb69c077c/merge8a68. Feature CI37369661577/job111963366131 SUCCESS199; canonical8a68 CI37370547332 attempt2/job111971912251 SUCCESS **199**,20:57:19Z. First canonical job111966304859 cancelled before any steps. GitHub compare0f8..8a68 proves only2 workflow YAML files changed, application/readiness code identical.
- PR37 merge83b122cefc42a93b27961aac4b076a1b0e599077:3 Kill/claim/reconnect transaction-order tests,234/91 actual feature CI. PR45 featuree4709c85530bdb69b89e64fe0c84e0c93b8ad33d/merge**c0c05d485c2cba3f66cfb969af6c4a1309186269** extends to explicit OFF/zero-capital configuration racing BUY. Configuration-first rejects stale claim/no reserve; claim-first retains83 synthetic reserve and OFF through reconnect. Local236pytest/93unittest and actual CI37371364907/job111969042298 **236 PASS**,37371364939/job111969045356 **93 PASS**; canonical durable37372530315/job111972964700 **93 PASS**,20:58:54Z. Current canonical full37372530271/job111972964752 QUEUED. Actual artifact11370942418 downloaded/parsed: ZIP SHA25665b6301dca275462e44932c5cbf6e53618085599b84d6c3e966b11deaf27926a matches GitHub digest;8 shadow and6 protected-capital replay scenarios pass, all actual settlement/broker/network/strategy/holdout/promotion/LIVE flags false. Synthetic only.
- PR38 research merge1c2e907bf952d567b6b8db4b9d98692a0b5ac549/PR39 dev merge8c48798a05686c8d21e01108e2b17e4fbfcb7817: exact boolean/data-role/reference safety,25 CI each, no empirical research adoption. New exclusion-flag defect reproduced on both actual canonical sources: `sealed_holdout_used="true"` or `criteria_changed_after_results="true"` incorrectly admitted a successor build (all actual authority stayed false). Present non-boolean veto flags now block artifact creation; optional absence/exact booleans retain existing contract. Dev PR44 feature54335d0637596664f33452795b2339229aaf8b2d/merge**827bfeb41abfe26a4ecc15fcb74214f6ea662a0e**, actual27 CI37370834473 attempt2/job111972554939 and postmerge37372525361/job111972948331 PASS. Research counterpart **PR43 OPEN** featurebf17231fe6e48aaf020ff0085c6781dec201bf6f, run37370827400 attempt2/job111972553851 QUEUED (initial111967221633 cancelled before steps), local27 PASS, not yet research canonical.
- Research stale untouched-holdout doc assertion caused actual1failed/71passed on37366646599 and37368185812. PR40 feature702b5fbbcac75e9e6ad0c4aff371c6b515114df2 **merged32fb10dbffb74f6fa82d88fa42e0d88d092c7159** after actual CI37368979054 attempt3/job111971913984 **72 PASS**,20:55:58Z; first2 jobs111961026486/111966644515 cancelled before steps. Dev equivalent PR42 merged8c8c3a4998c6a47c9b9de85cea29a4a480d03952, actual **76** feature/postmerge tests37369895620/37370566261. New doc guard requires consumed-failed v1 disposition/all3 frozen hashes and preserves no trading/research credit from physical notification E2E. Research canonical execution37372839697/job111974002774 and KRX status integrity37372839667/job111974002675 QUEUED; no success claim yet.

Actual Railway projectd1c1a050-b7d6-41ce-b300-13c20f82a20a / environment83d5840b-270e-4d3f-a941-a37fd4a55ff7 rechecked20:57:20Z, no staged/applying work. Public service37902fde-ca05-43e0-bc76-278992bf7732 pin**8a68**, deployment **eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS**,1running0crashed; only source pin/non-secret revision markers changed, /data500MB volumef96f985a-8aba-41ef-88df-f76999c4ff0c and readonly audit/production_v32 start preserved. Actual20:36:35Z startup: execution ledger TABLE_MISSING/counts/observations/native identity null; DEMO_CONFIGURATION_ONLY/ordering DISABLED; origin/connectivity/provenance/settlement/LIVE/holdout flags false. Healthcheck passed; **new-pin public/build-bound v32 smoke37370547415 attempt2/job111971908806 still QUEUED**, first job111966304367 cancelled before steps. Old0f8 public proof is not new-pin public proof.
Completed DEMOcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9/pinc2d497c76cc43a1b59a17f04c5ffd1d67a88c02a/NEVER/no volume/0running0crashed remains untouched; actual19:26:51Z one kt00018 page/0 observed rows/cursor end, no whole-account/cash/ownership/fees/LIVE admission. PIT7021473a-d9a6-4711-b496-a359fd9bb0c8/pin26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15/NEVER/0running0crashed,/pit5000MB03f389e5-5030-46a9-bfa5-dd8aa3dc24fa and KRXe56cf101-15c5-478e-ae67-228585013ef0/pinef95e7857f692fda3855390e918e165487624881/NEVER/0running0crashed,/data5000MB61610fae-dc0c-493e-9920-eb3cef4cea86 unchanged. Legacy push/backend/db-query OFFLINE issues preserved, not restarted. No secret values read or real-account requests/order switch changes.

Next client work is **PR46 OPEN**, `index-alert-android-readonly-readiness-v1` feature **a0ddaab8ed93f4ae39c17140ff2aa94201a8f4ed**, candidatev4.8/code48. Current auditedv4.7 dashboard has no automation availability display. Candidate adds bounded GET-only availability card: exact unavailable/MASTER_OFF/all nine exact-boolean flags false -> unavailable; network/missing/malformed/unknown READY/LIVE -> unknown, NEVER enable/persist/edit capital/place orders. Four pure Kotlin test methods; PR Gradle tests and separatedebug/unsignedreleasev4.8 builds. CI37371912963/job111970897295 **QUEUED**; local Java available but no Gradle/Kotlin compiler/Android build capability; no local or remote compilation/JUnit/APK success or new handset E2E claimed. Existing auditedv4.7/code47 physical notification proof is preserved, not v4.8 proof. No artifact install/publish/order control yet.

Exact next actions: inspect existing43/46/server-v32/current-dev236/research72+KRX postmerge runs; do not duplicate queued jobs or deploys. On actual cancelled-before-step jobs retry only still-relevant exact sources; on real test/build/API failures diagnose actual logs then fix/retest. Merge43 and46 only after actual expected-head CI success; preserve Champion/Master Spec/failed holdout and record postmerge Actions. For46 inspect candidate APK metadata and test results; new physical E2E stays unobserved until genuinely obtained. Refresh both canonical Status/Continuity/Handoff and dev JSON statuses with exact refs/results. Do not repin completed DEMO/PIT/KRX jobs for test-only changes.

Remaining true project gaps: official historical expected scope/PIT availability/source gates/affected-position economics, genuinely independent successor, broker-native account/day/whole-account/side/stable automation ownership/actual fee and sale settlement, admitted pretrade freshness/NetEV/capacity/risk and actual cancel/reconnect/Kill/control persistence/canonical accounted-capital contract. Readonly DEMO/synthetic/storage/notification/readiness cannot close them. Economics5aefb98988f7b4ccf7c95e7cdf2a671a7bdfee7e and future-only early-live1d81eb526f59b87c528d63be9e3883e0f76fedf6 unchanged; no new admitted empirical candidate. Ideas/REJECT/INCONCLUSIVE never enter production; old probability48fd04bd2ce8882ac4a8838b1dcd6f5f701b255c/v4185bfd892ef8cc8e36b434983945cf45ce9d7e070 are historical, not fresh Challenger permission.

**CONSUMED_FAILED_INVALID_V1_HOLDOUT**: failed result30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82; manifestff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907; receipt3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63. Failure2026-10-05T08:05:25.795261Z/cutoff2026-09-25/window2026-09-28..10-01/retirement03140e9f9c5327bb79b1b0621dafa6e6908ca700/repairb1d5bb3bfd8f15ee74076a8e67b84d8fb7d1c3dc and manifest discrepancy preserved. Do not delete/reset/re-evaluate/reseal/relabel/retune/reuse outcomes. All Master Spec PIT/time/labels/WF/Purged/CPCV60/H5 504-126-126/rolling1260/horizon purge+embargo/Top3no-backfill0..3NO_TRADE/q25/cost/slippage/partialfill/NetEV/Precision@Selected/PF/MDD/ES95/99/recency/model/threshold/promotion/rejection unchanged. H10rejected/no H6-H9 rescue,H20archive;H1separate1%25bp>=30tradesmeanNet>0positivefraction>.5 unchanged. Final600genuineLIVEobs/200distinctdates/400fills/120nearcapacity>=80%ADV0.0005 plus all independent quality gates immutable. Independently admitted capped validation does not require waiting200days to start, but final thresholds cannot be loosened. Master Spec section14 forbids implementing/activating real ordering below Alpha gates; real stock orders/funds/broker permissions need separately explicit authority AFTER frozen readiness. Project is not complete. Transient runner queue/cancellation is not a proven user-only blocker; no automation creation or disable is justified by it.



**CONSUMED_FAILED_INVALID_V1_HOLDOUT — DO NOT REUSE.** This is a factual continuation record, not new outcome evaluation. Preserve resultSHA30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82, manifestSHAff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907, receiptSHA3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63; frozen2026-09-25 cutoff/2026-09-28..10-01 consumed window and manifest discrepancy. No deletion/reset/reseal/rerun/relabel/retune/new-window rescue, private outcome parsing or promotion.

Research branch verified base before this feature **1c2e907bf952d567b6b8db4b9d98692a0b5ac549**: PR36 holdout-lineage documentation correction merged atb1d4b3480035da10b0f30c6082a27b5b2509015e; PR38 strict input safeguards merged at1c2e907... after exact finalcf4782d64d590cf44491340f6030f4ed245cfb5e CI37367541069/job111956227569 **SUCCESS /25 tests**, log2026-10-05T20:10:36.3693894Z. No research performance/strategy/Champion/model/threshold change. Postmerge governance37368185856,orchestrator37368185834,execution37368185812,internal-completeness37368185985 were QUEUED at the last read.

**Actual remaining CI defect found and repaired in this feature:** doc-sync research run37366646599/job111953338195 executed tests and failed2026-10-05T20:02:24Z (**1failed/71passed**). Existing Physical E2E documentation test required the historical phrase “SEALED HOLDOUT — untouched”, conflicting with the consumed failed v1 evidence. This is not a runner interruption. Replace only that obsolete expectation with mandatory CONSUMED_FAILED_INVALID_V1_HOLDOUT disposition and all three preserved identities in Status/Continuity. Keep every original handset proof, notification contract and no-research/no-trading-authority assertion. **5 focused tests pass locally**; full72 remote integrity tests remain required before merge. Official KRX status run37366646601/job111953338472 was separately cancelled before steps; do not mistake it for a failed test or retry old superseded source indiscriminately.

Development current recorded HEAD **0a7d7abf6850b6644bee4b40e842a3b9b0ba2e23**, last merged implementationed3e0f2cbb2a30830aed452e01c7426545dfad05; PR37 feature2dff54057fc8e9479c9fc325074bbe1f8432830e has234 local pytest/91 durable unittest and **remote durable91 SUCCESS** at37366906358/job111954177861. Full234 run37366906284 attempt1 job111954177592 cancelled before steps; attempt2 job111959549313 QUEUED. PR39 dev strict-input synchronization0bbc0f8a9d7219436566e2c72d4deec04794048a run37367737970/job111956885581 QUEUED,25 local tests. These are not yet merged.

Server PR35 latest actual feature **52a900b0a6d174e2b8a1e8c25568ee2b2615b109** extends the unchanged199-test application code62f706... with revision-bound public readiness GET/OpenAPI/report verification in existing production smoke. Final-head CI37368494570/job111959430409 QUEUED; prior37364545547 attempts1/2 cancelled before steps and attempt3 is superseded by the updated smoke workflow. Never use superseded-head CI as final-head evidence. Public source/pin remainsserverb5d01da4bb1c3185de7959bd480fe71f46c8a4fc, deploymenta824af66-f8d0-4006-a7a1-49d4cd79e4f9 SUCCESS/1running0crashed, /data500MB. No readiness route deployed yet; local urllib proxy timed out and web open was inaccessible, so remote actual smoke is needed after deployment.

Railway services actually rechecked unchanged: isolated DEMOc2d497c76cc43a1b59a17f04c5ffd1d67a88c02a/cd47a5f0-709c-46cc-9b8f-ea0969ce2ba9 SUCCESS/0running0crashed/no volume/NEVER; actual kt00018 report2026-10-05T19:26:51.265407712Z one page/0 observed rows/all origin/completeness/cash/settlement/ownership/LIVE/holdout/trading flagsfalse. PIT26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15/7021473a-d9a6-4711-b496-a359fd9bb0c8 read-only retirement audit/NEVER,/pit5000MB volume03f389e5-5030-46a9-bfa5-dd8aa3dc24fa. KRXef95e7857f692fda3855390e918e165487624881/e56cf101-15c5-478e-ae67-228585013ef0 read-only storage audit/NEVER,/data5000MB volume61610fae-dc0c-493e-9920-eb3cef4cea86. No staged changes observed; legacy offline warnings remain unresolved. Do not restart completed DEMO/PIT/KRX jobs or merge isolated root railway.json into dev.

Exact resume: verify this doc-test correction at its actual feature head with full72 CI before merge, then synchronize the same test/lineage guard into development without dropping separate Ledger history. Poll existing PR35/37/39 and postmerge research jobs/logs; only merge exact tested heads. After PR35 CI199 passes, stage only public runtime source and non-secret revision markers to actual server mergeSHA, preserve both startup audits/volume/credentials/order flags, inspect staged patch then accept authorized deployment and verify real revision-bound smoke. Keep developing independently admissible work while a job waits; no queued job is success or a user/account blocker.

All frozen Master Spec/PIT/label/rolling1260/504-126-126/purge-embargo/CPCV60/Top3no-backfill/0..3NO_TRADE/q25/cost/slippage/partial-fill/NetEV/Precision@Selected/PF/MDD/ES95/99/recency/promotion/rejection gates remain unchanged. H10 rejected/no-retune;H20archive. Final execution600genuineLIVEobs/200distinctdates/400fills/120near-capacity>=80% frozen ADV0.0005 plus all noncompensating gates unchanged. Remaining source/PIT/status affected-position economics, native account/day/whole-account scope/stable ownership/settlement, independent successor and live pretrade/reconnect/Kill are unclosed. DEMO/synthetic/notification/storage diagnostics give no promotion credit. Actual stock orders/funds/broker permissions require separate explicit authority after frozen readiness. Project is not complete.

---

# IndexAlert Research Status

## Current authoritative correction — 2026-10-05T19:56:04.948Z

**CONSUMED_FAILED_INVALID_V1_HOLDOUT — NO PROMOTION OR REUSE AUTHORITY.** This supersedes older “untouched/unopened” statements below. It records existing evidence; no private outcome was opened or reevaluated for this synchronization.

Development record: `index-alert-position-regen-fix-v1@ced2f2190ee70f4ba853d21aaabbd365b7912747`, last implementation `ed3e0f2cbb2a30830aed452e01c7426545dfad05`. Failed result was already created at **2026-10-05T08:05:25.795261Z**, passed=false, frozen cutoff **2026-09-25**, consumed window **2026-09-28..2026-10-01**. The original evaluator had future-label leakage and ignored the rolling1260 requirement; this is invalid independent promotion evidence, not a passing candidate.

Preserve these SHA-256 identities and the historical manifest/result discrepancy:
- Result: `30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82`.
- Manifest: `ff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907`.
- Receipt: `3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63`.
- Manifest outcomes_unsealed=false despite the existing failed result is retained as historical discrepancy, not corrected by rewriting private artifacts.

**Do not delete/reset/reseal/rerun/relabel/retune or use a new window to rescue v1.** Retirement merge `03140e9f9c5327bb79b1b0621dafa6e6908ca700`, repair `b1d5bb3bfd8f15ee74076a8e67b84d8fb7d1c3dc`; nine synthetic boundary tests and Actions37292632806/37292636269 passed. These are engineering boundary evidence only. No independent successor or promotion authority has been admitted.

Actual PIT service225f2279-d728-4e1a-a3f3-2447ff0f9dc1 is pinned at `26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15`, completed deployment7021473a-d9a6-4711-b496-a359fd9bb0c8, read-only retired-validation audit, restartNEVER, /pit5000MB volume03f389e5-5030-46a9-bfa5-dd8aa3dc24fa. Its prior safe audit reported three matching frozen hashes and four stages blocked, without opening outcomes or authorizing model evaluation. Do not restart the retired evaluator.

All Master Spec criteria remain frozen: PIT/label/CA returns, H5 504/126/126, rolling1260, horizon purge/embargo,60-case CPCV,Top3/no-backfill,0..3/NO_TRADE,q25,cost/slippage/partial-fill,NetEV/Precision@Selected/PF/MDD/ES95/99/recent evidence and promotion/rejection rules. H10 remains rejected/no-retune; H20 archive. Final execution requires600 genuine LIVE observations/200 distinct decision dates/400fills/120near-capacity fills >=80% frozen cap ADV0.0005 plus every existing noncompensating gate. No loosening or current live-order authority. Any future independent successor must be preregistered and admitted through existing contracts before its own untouched holdout; this consumed v1 window is unavailable.

Current independent engineering evidence: dev PR31-34,231 offline tests; PR33 integrated synthetic capital fault replay88 tests; DEMO kt00018 read-only holdings report2026-10-05T19:26:51.265407712Z at isolated pin`c2d497c76cc43a1b59a17f04c5ffd1d67a88c02a`, deploymentcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9 SUCCESS/0running0crashed, one page/zero observed rows. Account-origin/completeness/freshness/ownership/cash/fee-settlement/capital-release/genuineLIVE/holdout/trading flags remain false. This is DEMO plumbing only; zero observed rows do not establish account-wide zero exposure or genuine execution evidence.

Public runtime still pins server`b5d01da4bb1c3185de7959bd480fe71f46c8a4fc`, deploymenta824af66-f8d0-4006-a7a1-49d4cd79e4f9 SUCCESS/1running0crashed, /data500MB volumef96f985a-8aba-41ef-88df-f76999c4ff0c. PR35`62f7060727a0e27df2b99bbbd277ea1e9e7e183a` is OPEN/unmerged/undeployed: read-only unavailable-automation diagnostics only,199 local tests passed. CI37364545547 attempt1 was interrupted/cancelled before steps; job111946502765 retry requested. Never represent local tests or a queued retry as remote CI success.

KRX service003812ee-102b-42b6-bda4-36925885b428 pin`ef95e7857f692fda3855390e918e165487624881`, deploymente56cf101-15c5-478e-ae67-228585013ef0 SUCCESS/0running0crashed, /data5000MB volume61610fae-dc0c-493e-9920-eb3cef4cea86: storage-integrity audit only; source/PIT/status-economics gates are not closed by acquisition or storage hashes.

Research main before this documentation correction: `c490974ff6619bb978dc6f83f9c24f2c46622f85`; economics audit`5aefb98988f7b4ccf7c95e7cdf2a671a7bdfee7e`; early-LIVE draft`1d81eb526f59b87c528d63be9e3883e0f76fedf6`. No REJECT/INCONCLUSIVE/idea or future draft has been applied to the Champion. No code, Master Spec, model, threshold, immutable execution history or private holdout artifact is changed by this synchronization.

Research follow-up: independently resolve the canonical committed-capital/user-control contract before integrating the currently separate server and development structural interfaces. Their capital-ceiling domains/action vocabularies differ; no silent mapping or numerical criterion change is authorized. Complete account/day/side/whole-account scope, stable cross-day ownership, native fee/sale settlement, source/PIT/affected-position economics, genuine LIVE evidence and frozen reconnect/Kill/pretrade admission remain unresolved. Caller flags, synthetic replay, estimated valuation fees and DEMO snapshots cannot satisfy these gates.

Exact resume: re-fetch actual dev/server/research heads and PR35 run/job detail; merge/deploy only after exact-head CI199 success. Preserve public source pin/startup audits/volume and DEMO isolation root. Continue admissible independent engineering and research contract work, recording new issues in the ledger; do not reopen v1 or activate broker orders. Actual stock orders/funds/broker permission changes require separate explicit authority after frozen readiness. The project is not complete.

---

Updated: 2026-10-04 KST  
Branch: `index-alert-research-v1`  
Master authority: `INDEXALERT_MASTER_SPEC.md`  
Experiment authority: `INDEXALERT_RESEARCH_LEDGER.md`  
Promotion authority: **none yet**.

## Current bottom line

The current price/volume/context stack is **not ready for live short-term investment recommendations**. PIT discipline, CA-safe returns, frozen Top3/no-backfill, realistic costs, abstention, anchored purged walk-forward, corrected CPCV and reproducible CI are implemented, but robust recent execution-ready edge is not established.

Do **not** relax q25, TopK, costs, recent-evidence requirements, horizon, fill/capacity assumptions or holdout rules merely to create trades.

## Frozen research policy

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; no H6-H9 sweep or H10 retune from completed outcomes.
- H20 = outside requested 5-10-session scope; archive only.
- Anchored walk-forward = train 504 / calibration 126 / test 126 with horizon-matched purge/embargo.
- Correct CPCV = six contiguous groups, all two-test-group combinations, each remaining group once as calibration, other three train = **60 cases per horizon**.
- Original decision-time Top3 frozen; vetoed/held/unfillable slots remain empty; **no rank-4+ backfill**.
- 0..3 trades and `NO_TRADE` valid.
- Corporate-action-safe KRX base-price returns mandatory.
- Primary evidence = executable cost-adjusted NetReturn/NetEV, PF, date-cluster uncertainty, MDD/ES/tails, cost stress, coverage/abstention, execution/capacity realism and recent evidence.
- The v1 one-shot holdout is consumed, failed and invalid for promotion; see the authoritative correction above. Do not reuse it. Existing future independent-successor admission and prospective confirmation requirements remain frozen.

## Current empirical reference and frozen negative evidence

### H5 developmental reference — not promotable

- 278 executed entries / 137 trade days
- mean NetReturn **+1.150%**, PF **1.546**
- date-cluster 95% lower bound below zero
- 2x-cost mean **+0.787%**, PF **1.344**
- portfolio total **+16.39%**, CAGR ~1.83%, MDD **-24.39%**, Sharpe ~0.23
- admissions concentrated in 2018-2021
- no admissions in 2022-2026/latest 504 OOS sessions
- remove-best-5 turns mean negative and PF below 1

Classification: `DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE`.

### Uncertainty Audit

`EXP-2026-09-29-UNCERTAINTY-AUDIT-01`, Action `36637333875`: **KEEP_ABSTENTION**.
- all-OOS q25-blocked mean -0.8432%, PF 0.8425;
- 2022+ q25-blocked mean -1.2551%, PF 0.8005;
- latest-504 blocked mean -0.6263%, PF 0.9012; remove-best-5 -1.2697%, PF 0.8011;
- latest conservative-positive subset: 4 rows, mean -22.5669%, PF 0.1381.

Do not weaken q25 or launch a conditional-q25 rescue from this result.

### Policy-aligned calibration

`EXP-2026-09-29-POLICY-CAL-01`, Action `36643183157`: **ADOPT STRUCTURAL ALIGNMENT / NO PERFORMANCE CHANGE / NOT PROMOTION EVIDENCE**. Reference and challenger selected the same 278 records with identical compact economics.

### Corrected 60-case CPCV

Action `36637351334`: **CPCV_DOES_NOT_ESTABLISH_ROBUST_EDGE**.
- H5 median PF 0.381; positive NetEV 43.3%; positive date-cluster LCB 11.7%.
- H10 median PF 0.745; positive NetEV 50.0%; positive date-cluster LCB 33.3%.

Older 15-combination CPCV and conflicting old-chat recollections are superseded. Rolling-160 and CA-safe path challengers remain rejected; H10 remains do-not-retune; H20 archive only. Stop price-only threshold/feature mining.

## KRX source gates A-F — frozen and machine-audited

Canonical gates:
- Gate A — `AUTHORIZED_OFFICIAL_ROUTE`
- Gate B — `EXACT_DATASET_SCHEMA_MAPPING`
- Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- Gate D — `PIT_AVAILABILITY_LINEAGE`
- Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- Gate F — `INTENDED_USE_RIGHTS`

Only `PASS` closes a gate. All six passing closes only the source contract for the declared scope; it does not authorize Alpha/Final-Judge promotion, sealed holdout or live trading.

Current states remain:
- **Security/status:** A PARTIAL, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PASS (personal/internal research scope only); `judge_security_status_ready=false`.
- **Investor flow:** A PARTIAL, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PASS (personal/internal research scope only); `feature_performance_testing_authorized=false`.

Machine-readable public evidence remains version `2026-10-02.v2`, fingerprint:
`39f357fda6eec5bb994f1dcba1ba44ed913714df256ec6b542b5aeadf14a0380`.

## KRX authorization and source-data pipeline

The authorization boundary remains three separate layers:
1. route-specific credentials;
2. matching validated non-secret structured authorization evidence;
3. exact per-run consent for one tiny authenticated request.

Canonical runtime/configuration names are `KRX_AUTH_EVIDENCE_JSON` for the structured non-secret authorization record and `KRX_EXPLICIT_PROBE_CONSENT` for the exact per-run request-consent sentinel. An opaque approval reference alone is not validated evidence.

Canonical components include:
- `research_v1_krx_authorization_evidence.py`
- `research_v1_krx_auth_readiness.py`
- `research_v1_krx_auth_preflight.py`
- `research_v1_krx_status_source_probe.py`
- `research_v1_krx_investor_flow_probe.py`
- `research_v1_krx_acquisition_receipt.py`
- `research_v1_krx_acquisition_batch.py`
- `research_v1_krx_investor_flow_lineage.py`
- `research_v1_krx_investor_flow_coverage.py`
- `research_v1_krx_status_coverage.py`
- `research_v1_krx_status_event_integrity.py`
- `research_v1_krx_source_data_admission.py`

Frozen future source flow:
`structured authorization-evidence validation -> network-free auth readiness -> explicit manual request consent -> authorization preflight -> tiny authenticated probe/acquisition -> immutable receipt -> consistent batch -> PIT lineage -> exact expected-scope coverage -> A-F audit -> source-data admission -> separate experiment-registry/preregistration review`.

Push research-probe workflows remain dry-run only. Separately, production OpenAPI evidence now demonstrates authenticated GET access for the approved `유가증권 종목기본정보` and `유가증권 일별매매정보` services on basis date `20261001` (942 rows each, exact expected schemas; server revision `4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5`, Smoke Action `36956234911`). Canonical evidence is `INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.md/.json`; `research_v1_krx_openapi_connectivity_evidence.py` fail-closed validates the committed evidence and forbids authority escalation. This OpenAPI evidence is separate from the later authenticated Data Marketplace tiny probes. Those probes move Gate A to `PARTIAL` for both declared source families; they still do not close full-history/PIT/source contracts. KRX permission evidence v3 now closes Gate F for the declared personal/internal-research scope. Remaining source blockers are actual full-history technical coverage, stable IDs across the required period, exact all-period route/schema equivalence, record-level PIT lineage and immutable acquisition provenance.

Latest authenticated OpenAPI plumbing/schema reference: production Smoke Action `36956234911` at server revision `4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5` succeeded and recorded sanitized KRX response metadata plus per-service schema/payload SHA-256 fingerprints. Existing broad source-governance integrity reference remains Action `36817784717` at `bc5792640e0ba611f50f459f8c3b17c108cdd4bf`; documentation/handoff drift repairs later passed Action `36835918274`.

## KRX low-frequency internal-research reply evidence

The latest KRX permission evidence v3 states that personal research may use complete full-historical-period download/query plus programmatic/automated low- and high-frequency collection without a separate approval procedure, while external leakage, sale and third-party distribution are prohibited. Canonical evidence is `INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.md/.json`; latest reply provenance is bound by redacted normalized SHA-256 `7361065e06599f947216233fc84e97126b1675de5af41068114cf6ef9577e304`. The exact timestamp of the latest v3 reply was not re-provided and is intentionally left unknown. Gate F is now PASS for the declared personal/internal-research scope.

## Data Marketplace automation-permission boundary

The Data Marketplace terms boundary remains frozen in `INDEXALERT_KRX_DATA_MARKETPLACE_TERMS_AUDIT.md/.json`: credentials alone never authorize automation. KRX permission v3 now establishes full-history/high-frequency rights for personal research. Network-free Action `36973737546` established tiny-probe readiness; the separately consented status Action `36976085781` and investor-flow Action `36976873119` subsequently completed successfully. A new, broader full-history network job is governed by the separate historical-acquisition plan/consent gate.

`research_v1_krx_authorization_evidence.py` now treats a Data Marketplace record without `automated_collection_authorized=true` as insufficient, and `research_v1_krx_auth_preflight.py` independently enforces the same requirement.

### Pinned Data Marketplace route map

`INDEXALERT_KRX_DATA_MARKETPLACE_ROUTE_MAP.md/.json` now records authenticated tiny-probe reachability for `MDCSTAT21301`, `MDCSTAT23701` and `MDCSTAT02303`. `MDCSTAT23701` remains provisional for the full historical contract. The route-map validator still rejects any attempt to self-grant Gate A/B PASS, holdout or live authority.

## Authenticated KRX status tiny probe

Action `36976085781` completed successfully under explicit one-run consent. The authenticated status route returned current security identity plus new-listing, delisted-history, trading-halt `MDCSTAT21301` and cleanup-trading `MDCSTAT23701` metadata. Gate A for `KRX_SECURITY_STATUS` is now `PARTIAL` rather than BLOCKED. Gate B remains `PARTIAL`; C/D remain BLOCKED; `judge_security_status_ready=false`. Canonical evidence is `INDEXALERT_KRX_STATUS_TINY_PROBE_EVIDENCE.md/.json`.

## Authenticated KRX investor-flow tiny probe

Action `36976873119` completed successfully under explicit one-run consent. `MDCSTAT02303` returned 3 rows for `005930` over `2026-09-21..2026-09-23` with the observed investor-category schema. Investor-flow Gate A is now `PARTIAL`; Gate B remains `PARTIAL`; Gate C remains `BLOCKED`; Gate D remains `PARTIAL`. Feature-performance testing remains unauthorized. Canonical evidence is `INDEXALERT_KRX_INVESTOR_FLOW_TINY_PROBE_EVIDENCE.md/.json`.

## Frozen KRX historical acquisition plan

`INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.md/.json` freezes the primary required source window `2015-06-15..2026-10-01` for KOSPI, preserving the existing long-history research protocol rather than silently expanding model evaluation. The plan defines identity reconstruction, 730-day halt chunks, calendar-year investor-flow chunks, PIT lineage, receipts/batches, private raw-data handling and bounded concurrency. KRX rights are confirmed, but actual bulk network execution remains separately gated by `research_v1_krx_historical_acquisition_preflight.py` and an exact user execution-consent sentinel.

## KRX historical worker implementation readiness

Internal implementation for the future private full-history job is now materially complete through the first executable stage:

- acquisition plan: `INDEXALERT-KRX-HIST-ACQ-v3`;
- execution contract: `INDEXALERT-KRX-HIST-EXEC-v3`;
- exact historical identity/standard-code reconstruction and request planner;
- raw-preserving Data Marketplace/OpenAPI fetch adapters;
- content-addressed private raw store, receipt/manifest/checkpoint and verified resume;
- canonical one-request executor;
- staged batch orchestrator;
- fail-closed private phase state;
- preflight-first one-shot worker entrypoint;
- dedicated worker Dockerfile and deployment contract `INDEXALERT-KRX-HIST-WORKER-DEPLOY-v1`.

Latest integrated KRX integrity reference for the worker deployment boundary: Action `36997637052` at research revision `190d914e14190077d55b14de6f2637bf1abf5d90` succeeded.

Since that reference, the expected-scope acquisition path has also been implemented and fail-closed hardened behind its own execution boundary: separate consent-gated worker entrypoint, content-addressed immutable per-date scope/receipt records, checkpointed resume, and explicit rejection of scope-path drift or tampered raw/receipt reconciliation. Expected-scope hardening revision `090271828fe0915e8bc9004c623eb848419ea62e` passed Official KRX Status Integrity Action `37009561566` with **397 passed, 1 warning**. The immediately preceding failures at `f2c9ead`, `db9dc8c`, and `ccaf6cd` were superseded by the green HEAD after fixing the content-addressed checkpoint test/verification path; no KRX bulk network acquisition was performed by these CI tests.

Railway provisioning and worker-secret setup are complete for the dedicated `indexalert-krx-historical-worker`: isolated service/volume, `Dockerfile.krx-historical-worker`, restart `NEVER`, no cron and no public domain. A Railway builder conflict was found and fixed by pinning the research-branch root `railway.json` to the worker Dockerfile; fresh preflight deployment `83be77ba-ccb1-4dcf-a40d-dd67a49fa9fb` at exact revision `6343f01b493404d59736e06eb6968e9820d0e595` then passed with all three credential-presence flags true and zero network requests.

The user separately authorized only the first 27-request `IDENTITY_SEED`. Fresh deployment `d268e5b0-b7c2-46be-b9ae-ca41d27cdb02` executed that stage on the exact pinned worker image and completed **27/27**, with zero resumes, 27 network requests, phase `COMPLETE`, task-set fingerprint `fb69ed44c2944911417dc26f088f0c5876942530a7c17abdd1fc38ee3f197aa1`, private-batch metadata fingerprint `054a9689adac7f57fa5a797f10ff9a69d3a7abd34a8697b624464588c6f0502f`, and `raw_rows_emitted=false`. Canonical sanitized evidence is `INDEXALERT_KRX_HISTORICAL_IDENTITY_SEED_EXECUTION_EVIDENCE.md/.json`.

Immediately after completion, the exact execution sentinel was disabled again and the worker start command was restored to preflight-only. `IDENTITY_STANDARD_CODE_BINDING`, expected-scope execution, per-security history, status economics, feature-performance testing, sealed holdout and live trading remain unauthorized. Gates C/D/E remain open.

Canonical Railway readiness evidence is `INDEXALERT_KRX_HISTORICAL_RAILWAY_READINESS_EVIDENCE.md/.json`. Provisioning authority remains separated by `INDEXALERT_KRX_WORKER_PROVISIONING_CONSENT_CONTRACT.md/.json`; completed preflight infrastructure setup cannot authorize historical bulk acquisition or expected-scope network execution.

## Exact KRX status economics — internal audit implemented, real evidence missing

Final Judge requires exact halt/delisting economics. Structural status-event consistency or daily price history is not sufficient.

Canonical contract: `INDEXALERT_KRX_STATUS_ECONOMICS_CONTRACT.md`.  
Executable audit: `research_v1_krx_status_economics.py`.

The audit requires independently attested complete affected-position scope, exact position-ID coverage, quantity conservation, accepted actual execution/recovery evidence, explicit fees/taxes, timezone-aware economic availability and matching source-contract lineage. It rejects backtest/synthetic/modelled fills, market-open assumptions, Shadow/Paper fill substitution, daily OHLC and MDCSTAT239 daily price rows as proof that an IndexAlert order filled.

Even `exact_status_economics_ready=true` is only one Final-Judge input and does not itself set Judge readiness, promotion, holdout or live authority.

Implementation tests passed Action `36834108231`. Contract drift initially failed in `36834285722` only because human-readable wording omitted a canonical forbidden-source identifier; the document was corrected without changing policy. Action `36834718544` then succeeded.

**Project-level exact halt/cleanup/delisting economics remains OPEN** because no real complete affected-position economics dataset has been supplied.

## Execution evidence — structural LIVE evidence is not empirical sufficiency

Canonical contract: `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md`.

Evidence tiers remain:
1. `PROSPECTIVE_SHADOW_DECISION_LOG` — decisions only, no broker fills.
2. `PROSPECTIVE_PAPER_EXECUTION_LOG` — paper/simulation plumbing evidence, not real fill quality.
3. `PROSPECTIVE_LIVE_EXECUTION_LOG` — real-account executions; the only tier eligible to contribute raw empirical live fill/slippage/partial-fill/latency/markout/capacity evidence.

`research_v1_execution_evidence.py` separates `live_structural_execution_evidence_present` from empirical execution sufficiency. One or several LIVE rows can never automatically close the empirical blocker. Until a separately frozen protocol is evaluated:
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_sufficiency_assessed=false`;
- `empirical_execution_blocker_closed=false`;
- `promotion_ready=false`.

Execution integrity Action `36834616144` succeeded after freezing this separation.

## Execution-sufficiency preregistration — project v1 frozen, genuine LIVE not yet observed

Canonical preregistration/evaluator stack is now:
- `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md` — human-readable frozen protocol;
- `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.json` — SHA-256-bound machine-readable schema v2 criteria;
- `research_v1_execution_sufficiency_protocol.py` — fail-closed preregistration validator with legacy schema-v1 compatibility;
- `research_v1_execution_sufficiency_assessment.py` — frozen numerical execution-gate evaluator;
- `INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md` — separate fail-closed genuine-LIVE provenance admission contract.

The project protocol was frozen before any genuine LIVE observation. Core criteria include at least 600 LIVE observations across at least 200 distinct decision dates, at least 400 filled observations, decision-time PIT ADV participation capped at the existing research assumption `0.0005` (0.05%), 120 near-capacity observations at >=80% of that ceiling, date-cluster fill/slippage gates, Wilson no-fill/partial-fill bounds, 5m/30m/close markouts with ES95/ES99 reporting, latency/expiry controls, fee/tax comparison, and zero unknown/reconciliation/risk/capacity-integrity breaches. Thresholds are bound to the protocol document fingerprint and may not be weakened using outcomes from the evidence window they judge.

The metric evaluator requires LIVE-labelled rows, the frozen decision/execution policy IDs and PIT provenance timestamps, but it cannot authenticate real-account origin from a caller-supplied CSV. A source label or CSV SHA-256 is identity/structure evidence only. Numerical success is exposed separately as `execution_metric_gates_passed`, while the fact that the metric calculation was run is `execution_metric_sufficiency_assessed=true`. Project-level readiness additionally requires independent broker-native provenance admission for the exact evidence bundle. The metric evaluator by itself keeps `genuine_live_provenance_verified=false`, `empirical_execution_sufficiency_assessed=false`, `live_empirical_execution_evidence_ready=false`, `empirical_execution_blocker_closed=false`, `promotion_ready=false`, `sealed_holdout_authorized=false` and `live_trading_authorized=false`.

No genuine staged LIVE execution observations or broker-native provenance admission exist yet, so current project state remains:
- `genuine_live_provenance_verified=false`;
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_sufficiency_assessed=false`;
- `empirical_execution_blocker_closed=false`;
- `promotion_ready=false`.

Historical preregistration Actions `36835013828` and `36835231533` succeeded. The frozen project protocol/evaluator Action `36881327868` also succeeded. Unit-test fixtures may exercise numerical pass/fail paths only and are not project evidence; a synthetic fixture may never close the project execution blocker.

## Android / push Physical E2E state — CONFIRMED

Canonical audit: `INDEXALERT_PHYSICAL_E2E_AUDIT.md`.

Current Android build branch is `index-alert-build`, HEAD `5154ef7943353791f615622394523ecd52ef8b0f`. The audited build is `versionName=4.7`, `versionCode=47`, therefore `client_build=4.7-47`.

Latest APK Action `36856589300` succeeded:
- debug `IndexAlert-v4.7-debug`, artifact ID `11158994269`, SHA256 `0aec298a0d0276f8a5e40dc22429b595e8bb11636f22ceeea75cb018a4a7e411`;
- unsigned release `IndexAlert-v4.7-unsigned-release`, artifact ID `11159209190`, SHA256 `77f7ba0acb991ae48827dcac8658b917fe60edc0ec677ae4548d8e797c8f4780`.

The v4.7 Android client sends its privacy-safe `client_build` during registration and uses the build-specific self-test/receipt path. Provider send success is never treated as handset receipt; confirmation requires the actual client `/push-ack` for the exact server event.

During the real handset audit, the first v4.7 registration attempts reached production but returned HTTP 400. Root cause was an exact-key mismatch between the Android `enabled_levels` payload and server-side display-only rules such as `usdkrw` whose alert `levels` are empty. The server overlay was fixed to synthesize only missing **display-only** empty-level keys; alert-bearing keys are never synthesized and continue to fail closed when missing or invalid.

The validated server branch `index-alert-server` production revision is now `d8523810b1c2c092a9ffc8f6245586e3bb719645` (`Test v4.7 registration with display-only server rules`). Server Tests Action `36874615526` succeeded, including regression coverage for the v4.7 payload/display-only compatibility boundary.

Frozen Physical-E2E contracts remain:
- `registration_build_contract = "register-client-build-v1"`;
- `self_test_trigger_contract = "android-register-direct-v1"`;
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`;
- `physical_e2e_blocker_contract = "physical-e2e-blocker-v1"`.

The server binds Physical E2E to the exact latest registered **device and build**. A same-build receipt from another device, an older-build receipt, or a newer legacy/unknown-build registration all fail closed. A legacy registration with no `client_build` is preserved as the latest unknown-build observation so it cannot resurrect an older build-aware device as the apparent latest candidate.

`/push-health` exposes privacy-safe diagnostics including `latest_registered_client_build`, `latest_self_test_build`, `latest_self_test_sent`, `latest_self_test_receipt_confirmed`, `registration_device_matches_self_test`, `registration_build_matches_self_test`, `physical_e2e_blocker`, and `current_build_physical_e2e_confirmed`. Raw token/event IDs remain server-private.

Read-only verifier `verify_push_physical_e2e.py` requires the exact expected registered build, same-device/same-build binding, all frozen contract markers, sent self-test, real receipt timestamp and `physical_e2e_blocker == "CONFIRMED"`; it cannot send FCM, register a device, or manufacture a receipt.

### Real production Physical E2E evidence — DONE

Railway production deployment `4cde730b-2aca-49c2-9950-f895897fe642` is built from exact server revision `d8523810b1c2c092a9ffc8f6245586e3bb719645` and completed SUCCESS.

After that revision became live, the real Android handset performed the physical path in production:
- `POST /register` — HTTP 200;
- `POST /push-self-test` — HTTP 200;
- real handset `POST /push-ack` — HTTP 200.

The v32 Build Contract Smoke Action `36874615527` was rerun after the real handset ACK and completed SUCCESS. Its exact-revision `/push-health` observation reported:
- `runtime_revision = "d8523810b1c2c092a9ffc8f6245586e3bb719645"`;
- `physical_e2e_blocker = "CONFIRMED"`;
- `latest_registered_client_build = "4.7-47"`;
- `latest_self_test_build = "4.7-47"`;
- `registration_device_matches_self_test = true`;
- `registration_build_matches_self_test = true`;
- `current_build_physical_e2e_confirmed = true`.

Therefore the Android notification Physical E2E blocker is **CLOSED for the audited v4.7-47 build and exact production revision above**. This is plumbing/safety evidence only. It is not model-promotion evidence, execution sufficiency, KRX evidence, sealed-holdout evidence or live-order authority.

## U.S. mover production-data integrity — fail-closed and auditable

Constituent mover quotes now require Yahoo instrument type `EQUITY`; index/ETF/fund/currency contamination is rejected before ranking. Corporate-action discontinuities are not removed by an arbitrary percentage threshold. They are suppressed only on a source-backed event/date registered in `corporate_action_registry.py` when raw previous-close comparison is economically non-comparable.

`/laggards` exposes per-universe exclusion provenance through `excluded_non_equity_symbols` and `excluded_corporate_action_symbols`. Final exact-revision Production Smoke Action `36853857418` verified the live contract:
- S&P500 coverage `502/503`, `excluded_corporate_action_symbols=["CTVA"]` on the documented 2026-10-01 CTVA/Vylor separation date;
- NASDAQ100 coverage `100/100`, no deliberate exclusion;
- SCHD coverage `98/99`, `excluded_non_equity_symbols=["USD"]`, preventing ProShares Ultra Semiconductors from masquerading as a stock constituent.

Direction/sign checks remained valid for all three universes. This is an operational data-integrity safeguard, not Alpha/promotion evidence and not a change to the frozen research statistics or KRX A-F state.

## USD/KRW startup basis integrity — fail-closed and exact-revision audited

The public USD/KRW day-change contract is versioned as `ecos-1530-fail-closed-v1`. A live current quote may remain available during startup, but before the Bank of Korea ECOS prior 15:30 close is completely verified the public comparison fields are forced to:
- `previous_close = null`;
- `previous_close_date = null`;
- `day_change = null`;
- `day_change_percent = null`;
- `basis_provider = null`;
- `basis_verified = false`.

`fx_basis.public_basis_fields()` accepts a public daily basis only when the prior close is finite/positive, the date and day-change fields are complete, `basis_verified=true`, and the provider explicitly identifies ECOS. Unit tests reject a Yahoo/provider fallback even if an older layer marks the shape as otherwise plausible. `/status` and `/history/usdkrw` use the same fail-closed sanitizer and expose the non-secret `basis_contract` marker.

The original exact-revision production validation of this FX contract was Production Smoke `36853857418`: it passed only after `runtime_revision == a416d64c3bc444fc6126a85db94bdaa1d2b346c2` and verified the ECOS-ready state with `basis_contract="ecos-1530-fail-closed-v1"`, `basis_verified=true`, `previous_close=1352.8`, `previous_close_date="2026-09-30"`, and an ECOS basis provider. Later server revisions retained the same tested FX sanitizer; current operational runtime alignment is tracked separately below.

The timing-sensitive smoke did **not** itself capture a complete public response during the short pre-ECOS transition; unit tests enforce the null-field transition contract. Internal startup logs may still show an older-layer Yahoo fallback calculation before the outer v3.1 sanitizer completes; that internal calculation is not accepted as the public official day-change basis.

## Operational deployment evidence state

Railway `indexalert-runtime` is now aligned to server revision `4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5` through deployment `2ae60f51-720c-463f-96cb-c9ef98fc449b` (SUCCESS). Production Smoke Action `36956234911` succeeded on that exact runtime revision and included the sanitized KRX connectivity/schema proof. The original physical handset event remains the earlier v4.7-47 `/register -> /push-self-test -> /push-ack` evidence; the newer deployment must not be misdescribed as a new handset event.

This closes server deployment drift, stale-runtime ambiguity, the latest-registration ordering gap, the v4.7 display-only registration compatibility gap, the Physical E2E blocker, the mover-provenance observability gap and the public startup FX-basis leakage path. It does not close the execution evidence blocker, KRX blockers, sealed holdout, promotion, or live-order authority. Real-account ordering remains disabled.

## External evidence still missing

Internal code cannot fabricate the still-missing actual full-history KRX coverage/PIT/provenance evidence, real complete affected-position status economics, genuine staged LIVE execution observations or a later independent execution-sufficiency assessment. Personal-research acquisition rights themselves are now evidenced by KRX permission v3.

## Remaining blockers

1. **KRX authorization/data:** basic-info/daily-trade OpenAPI connectivity, both Data Marketplace tiny probes, personal-research full-history/high-frequency rights, and the internal private historical-acquisition implementation are complete through a preflight-only dedicated-worker image. Gate F is PASS for the declared scope; Gate A remains PARTIAL. The dedicated private Railway worker/volume and worker secrets are complete, and the 27-request `IDENTITY_SEED` is complete with canonical metadata-only evidence. `IDENTITY_STANDARD_CODE_BINDING` has now also been prepared **network-free** from the private seed: exactly 145 `security_master` tasks were frozen with task-set SHA-256 `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`, private-manifest metadata SHA-256 `940f446caec81dd1a4a7b3a01053ae3f6a6ef6c79654e23bf2b971dca3622a6c`, and zero network requests. Canonical evidence is `INDEXALERT_KRX_IDENTITY_BINDING_PREPARATION_EVIDENCE.md/.json`. The separate identity-binding approval was supplied and consumed. Railway deployment `3501cbb8-a6a6-4972-bf82-4fb8e3fb36f6` at exact revision `6c152d8f29354d843b16c35be27a86a8a8058908` completed the frozen `IDENTITY_STANDARD_CODE_BINDING` stage **145/145**, zero resumes, exactly 145 network requests, phase `COMPLETE`, task-set SHA-256 `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`, and private execution-batch metadata SHA-256 `d5ca4e7ea45033f6bd6d45e301f1d3041b2e7257836e60d71c442fa73d8013be`; raw rows/identifiers were not emitted publicly. Both consent values were disabled again and the worker was restored to preflight-only. Canonical evidence is `INDEXALERT_KRX_IDENTITY_BINDING_EXECUTION_EVIDENCE.md/.json`. `PER_SECURITY_HISTORY` network-free preparation is now complete on Railway deployment `f683b1a2-5db6-4e95-81a7-6ec5889a2c59` from exact revision `ffe0e2c05e2a705c4b4cf06922600d07daa464cc`: **14,296** requests were frozen (**9,485** `investor_trading_individual_daily` + **4,811** `trading_halt`), task-set SHA-256 `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`, private-manifest metadata SHA-256 `0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116`, and zero KRX network requests during preparation. Before freezing, PIT-safe identity reconciliation preserved official six-character alphanumeric short codes and excluded only issues proven non-common by same-day/start-date official master evidence; missing/ambiguous mappings remain fail-closed. Canonical evidence is `INDEXALERT_KRX_PER_SECURITY_HISTORY_PREPARATION_EVIDENCE.md/.json`. The exact prepared scope is now code-pinned and execution-contract-pinned. The separate exact approval `I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1` has now been supplied and consumed only for the frozen one-shot scope. The original Railway execution deployment `bc79d1b5-5fb8-46c7-8067-682e61947014` at source revision `9009c48a00394063c813d29219507ee2190ce09e` **CRASHED** at 2026-10-03T00:45:16Z because that executor revision incorrectly required `isuCd2` to be decimal-only even though the already-frozen PIT-safe planner correctly preserves official six-character ASCII alphanumeric short codes. The executor is now patched and regression-tested to the same six-character ASCII alphanumeric domain. A network-free aggregate status deployment `92439b24-644a-4d3d-a888-9e0ba568bfac` verified the private checkpoint at **11,750 / 14,296 complete**, **2,546 remaining**, **0 failed**, phase `IN_PROGRESS`, frozen fingerprint `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`, with `network_request_attempted=false`. Canonical interruption evidence is `INDEXALERT_KRX_PER_SECURITY_HISTORY_INTERRUPTION_EVIDENCE.md/.json`. The original one-shot authority is consumed and both consent values are disabled again; configured worker start is preflight-only with restart `NEVER`. The alphanumeric short-code fix is now verified at exact revision `585d763542b2fbbdc3f928621f679fb14c8c3bbf`: Official KRX Status Integrity Action `37087007640` is SUCCESS, and fresh preflight-only Railway deployment `c1f875b2-4164-491a-9aaf-e6c5b2a387db` used `Dockerfile.krx-historical-worker` with `network_request_attempted=false` and no execution consent. Frozen source branch `index-alert-krx-per-security-resume-v1` points exactly to that revision. The frozen `PER_SECURITY_HISTORY` resume is now **COMPLETE**. Frozen-source deployment `1baafc07-6ee3-41d4-80be-857dec448f8a` at revision `585d763542b2fbbdc3f928621f679fb14c8c3bbf` completed **14,296/14,296** with **0 failed**, **11,750 resumed**, and **2,546 network request attempts**. The task-set fingerprint remained `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`; finalized private-batch metadata SHA-256 is `9609d6a73a486a51a7005e7081f825c45f78e1fb160f8e45e5017a47d0cc81de`. The one-shot resume authority is consumed.

Post-completion controls are restored: execution consents are non-authorizing, worker start is preflight-only, and restart policy is `NEVER`. Network-free finalization deployment `951015f9-2d0d-4157-94b4-f12b5aa585ec` independently verified COMPLETE, the same counts/fingerprints, and `network_request_attempted=false`; finalizer egress and DNS were zero. Final preflight-only deployment `f3d7e6b8-326b-4265-90c5-0d178b1623d2` succeeded without crash/failure.

This completion does not authorize `STATUS_ECONOMICS`, feature-performance testing, sealed holdout, genuine LIVE, or live trading. Those remain governed by their separate frozen gates and future explicit authorities. Canonical interruption evidence remains `INDEXALERT_KRX_PER_SECURITY_HISTORY_INTERRUPTION_EVIDENCE.md/.json`, and completion evidence must preserve the interruption/resume lineage.
2. **Security/status economics:** real complete affected-position fill/recovery economics must pass the exact audit; the internal auditor alone does not close the blocker.
3. **Investor flow:** real full official history must pass provenance, PIT, coverage, A-F and source-data admission; then separate preregistration before any feature-performance experiment.
4. **Execution:** genuine staged LIVE observations, frozen numerical sufficiency assessment and independent broker-native provenance admission for the exact evidence bundle. Structurally valid or self-labelled LIVE rows alone do not close this blocker.
5. **Research governance:** no rejected-candidate revival; maintain Ledger/multiple-testing discipline.
6. **One-shot sealed holdout:** v1 consumed/failed/invalid and unavailable for reuse. A future independently admitted successor requires its own preregistered untouched holdout and existing Shadow S1 -> Fresh Confirmation S2; no successor currently admitted.
7. **Physical notification E2E:** **DONE for audited Android v4.7-47 and production revision `d8523810…`**; do not reinterpret this plumbing success as Alpha/execution/promotion evidence.
8. **Live ordering:** disabled until all frozen promotion/safety gates and explicit user activation requirements are met.

## Promotion rule

Positive mean, PF or CAGR alone cannot promote a candidate. Promotion requires cost-adjusted OOS economics, PF > 1, positive date-cluster lower bound, best-day robustness, credible recent evidence, acceptable MDD/ES/tails, cost-stress survival, PIT correctness, official source/status integrity and execution realism. Final promotion additionally requires the one-shot sealed holdout and prospective confirmation sequence.

## Kiwoom demo/read-only connectivity — observed, non-promotional

Canonical demo evidence records `TOKEN_OK`, `ACCOUNT_OK`, `BALANCE_OK`, and `FILLS_OK` against the Kiwoom mock/demo host in a user-operated read-only smoke test. This is plumbing/readiness evidence only. Genuine LIVE broker-native provenance, empirical execution sufficiency, real status-event economics, KRX external evidence, sealed holdout and live ordering remain blocked/unauthorized as previously frozen.

## Continuous Research Lab — ENABLED, isolated from Core

Continuous research governance is now implemented by `research_v1_continuous_research.py` under `INDEXALERT_CONTINUOUS_RESEARCH_CONTRACT.md`. Automated research may queue ideas and evaluate preregistered challengers, but cannot mutate Core, open the sealed holdout, authorize live ordering, or auto-promote a candidate. Existing frozen blockers and criteria are unchanged.

## Internal completeness audit — authority boundary hardened

`INDEXALERT_INTERNAL_COMPLETENESS_AUDIT.md` records the internal audit. Successor research may satisfy represented promotion conditions but remains `promotion_eligible=false` until independent canonical gate admission exists; caller booleans cannot grant that authority. The audit also fixed a legacy KRX staging ambiguity: `research_v1_krx.py` now hard-codes `judge_eligible=false`, requires source-governance admission, and cannot label pykrx transport success as authenticated Final-Judge evidence. Real-order and sealed-holdout authorization remain false. Remaining material blockers are external/evidence-bound.


### STATUS_ECONOMICS network-free preparation — 2026-10-04
Network-free preparation is complete. The frozen prepared scope contains **27** cleanup-price tasks across **83** delisted episodes; **56** episodes have no cleanup interval and therefore generate no cleanup-price request. Prepared task-set SHA-256 is `b3738dca89ab5cb6966a1e3158f995b75cbf6e2ae2cd4c199f02c95a8ba4c1d8`; private-manifest metadata SHA-256 is `e744530ae017510477c7353c917b5d4c9d8cccec8c0ed4543b6434b133628a79`. Railway preparation deployment `2ad84e2e-7ff6-4afc-951e-3f095be159f8` reported `network_request_attempted=false`, emitted no security identifiers or raw rows, and had zero DNS/egress observations. An unrelated malformed delisted-history row exposed a fail-closed preparation bug; the builder now ignores only malformed rows that cannot match a canonical episode, while exact episode lookup remains mandatory. The frozen scope is code-pinned and Official KRX Status Integrity Action `37180990297` is SUCCESS at revision `a41c033db057867718ff1d9622f017bb9d94e5e2`. Railway is restored to preflight-only with restart `NEVER`. Actual STATUS_ECONOMICS network execution remains unauthorized, as do feature-performance testing, sealed holdout, genuine LIVE and live trading.


### STATUS_ECONOMICS acquisition completion — 2026-10-04
The frozen cleanup-price-context acquisition is **COMPLETE: 27/27, failed=0**. After an initial parser interruption, the official CSV adapter was hardened to preserve raw bytes while accepting the observed UTF-8 response fallback; Official KRX Status Integrity is SUCCESS at revision `a27ef4cdbdadfab4d44ce3d4dcde87039dcd8a6e`. Re-authorized deployment `64311852-0e38-46b4-8d06-c8f5d5bc31b0` resumed **21** already-persisted tasks and made **6** remaining network request attempts. Frozen task-set SHA-256 remained `b3738dca89ab5cb6966a1e3158f995b75cbf6e2ae2cd4c199f02c95a8ba4c1d8`; finalized private-batch metadata SHA-256 is `6b81db555f6a8a709e2d38801f8ca88647cc80ad960687f229fbf89a05c0b97d`. Network-free finalizer deployment `6b9e51eb-9785-4de2-9696-d5ddee776d58` independently verified COMPLETE, 27/27, failed=0, with zero DNS/network-flow observations during finalization. Execution consents were disabled immediately after completion and the worker was returned to preflight-only with restart `NEVER`. This closes cleanup-price-context acquisition only: `exact_status_economics_ready=false`; realized fill economics and recovery cashflows remain unproven; source gates C/D/E, feature-performance testing, sealed holdout, Shadow S1, genuine LIVE and live trading remain unauthorized.


### Execution evidence input-integrity hardening — 2026-10-06
PR126-133 completed symmetric development/research hardening for missing execution identities, fractional share quantities, boolean coercion into numeric/identity/timestamp fields, and timezone-naive/numeric/non-scalar timestamp inputs. Exact-head Actions passed before merge; frozen execution-sufficiency thresholds and provenance requirements are unchanged. This is structural validation only and does not close genuine LIVE provenance, empirical execution sufficiency, source/PIT/status-economics, successor/holdout, Shadow or live-order gates. Real-account ordering remains disabled.


## 2026-10-06 — Decision-date and symbol identity hardening

Continued execution-evidence audit after PR134-137. PR138/139 require `decision_date` to preserve an exact `YYYY-MM-DD` string rather than accepting full datetime/numeric coercion, protecting the frozen distinct-decision-date counting semantics. PR140/141 remove lossy symbol coercion (`5930.0` -> `005930`) and accept only original string/integer 1-6 digit codes before deterministic zero-padding. Exact-head Actions passed before all four merges. Current merge heads before this documentation update: development `55ee21f37e6acfc5b2c3470c87d07f657ab0da25`, research `ec7ee4cc7f059b84f920aa1309be790bdcc7c5e3`. No genuine LIVE evidence was created/admitted; frozen numerical thresholds/model/horizon/cost rules and consumed-invalid-v1 holdout disposition remain unchanged; real ordering remains disabled.
