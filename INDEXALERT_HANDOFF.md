# Current handoff update — 2026-10-05 18:53 KST
Active branch: index-alert-position-regen-fix-v1.
Implementation/deployment pin: 03140e9f9c5327bb79b1b0621dafa6e6908ca700.
Latest branch HEAD is the commit containing this update; re-fetch before continuation.
Repair branch: index-alert-holdout-integrity-repair-v1 @ b1d5bb3bfd8f15ee74076a8e67b84d8fb7d1c3dc.
PR #5 merged; GitHub Actions 37292632806 and 37292636269 both SUCCESS (9 tests).
Current Railway PIT deployment a2cd6b78-90d8-4a46-a140-642ba2edf86e SUCCESS.
Source/config now uses the implementation pin above, read-only lineage audit start, NEVER restart.
This update overrides the older implementation pin/deployment below; all other preservation rules apply.

Completed after the first handoff: reproduced label leakage on synthetic data; tested a safe
boundary helper; retired consumed evaluator; blocked consumed standalone gate; CI verified;
merged and deployed the safeguards; inspected only private manifest/receipt/result metadata.
No actual outcomes used for tuning; immutable result hash unchanged.
Immediate blocker: consumed invalid v1 window cannot become an independent holdout through
further approval or rerun. Manifest false-unseal claim is historical evidence, not authority.
No user manual step is required for the completed repair. Remaining evidence admissions
must be resolved before a separately registered untouched prospective protocol can advance.

## 2026-10-05 18:53 KST — consumed v1 holdout integrity correction
This entry supersedes any older claim that the current v1 window is unopened or ready for evaluation.
Observed result: passed=false; result SHA-256 30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82.
Outcome-free lineage audit verified first/last eligible dates 2026-09-28/2026-10-01;
manifest created 2026-10-05T07:37:48Z, acquisition 07:42:41Z, result 08:05:25Z.
The manifest still claims outcomes_unsealed=false although a result exists.
Do not rewrite those historical files to erase the discrepancy.

Synthetic tests using actual v2.engineer reproduced boundary leakage: changing only fresh
returns changes pre-cutoff ret1/ret5 labels under the original evaluator date split.
Disposition: CONSUMED_WINDOW_INVALID_FOR_INDEPENDENT_PROMOTION; failed result retained;
no repair-and-rerun, candidate retune, new-window rescue or downstream promotion.

Repair commit b1d5bb3bfd8f15ee74076a8e67b84d8fb7d1c3dc:
- Retire sealed-holdout-v1 evaluator at entry before private data reads/model execution.
- Reject existing result in standalone sealed gate, even if manifest claims unopened.
- Add synthetic-tested training-boundary helper preserving v2 training length/purge;
  it is not an admitted successor evaluator.
- Nine tests PASS locally and remotely with production dependency versions.
GitHub push Action 37292632806 SUCCESS and PR Action 37292636269 SUCCESS.
PR #5 merged as 03140e9f9c5327bb79b1b0621dafa6e6908ca700.
Railway PIT deployment a2cd6b78-90d8-4a46-a140-642ba2edf86e SUCCESS at that exact pin,
start READ_ONLY_LINEAGE_AUDIT, restart NEVER; no modeling, market collection or score output.
Result/manifest/receipt hashes remain unchanged. Operational server and all volumes remain intact.

Frozen Core criteria and v3 historical cutoff/pass rule/baseline fingerprints unchanged.
Source/PIT/status-economics and genuine broker execution evidence remain independent blockers.
No new ACCEPTED challenger was established; no production alpha/live authority granted.
Next: resolve freeze/access lineage and independent source/execution admissions; a separate
prospective protocol requires independent preregistration/admission and cannot reuse this window.


---

# INDEXALERT_HANDOFF
Verified: 2026-10-05 18:17 KST (GitHub and Railway live queries; older chats are discovery aids only).

## Authority and branches
Repository: https://github.com/kims34/openpilot-opkr
Active PIT development branch: index-alert-position-regen-fix-v1.
Verified implementation HEAD / Railway source pin: 1bf1a69e8db44f24b6426b7069ce332788e81d1c.
This documentation commit advances branch HEAD; the Railway implementation pin remains the SHA above. Re-fetch branch HEAD before continuation.
Research/source-audit branch current HEAD: 5aefb98988f7b4ccf7c95e7cdf2a671a7bdfee7e.
Frozen per-security execution branch: index-alert-krx-per-security-resume-v1 @ 585d763542b2fbbdc3f928621f679fb14c8c3bbf (historical frozen execution identity; never move this pin).
Server branch HEAD: 4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5.
Authority: INDEXALERT_MASTER_SPEC.md -> INDEXALERT_RESEARCH_LEDGER.md -> reproducible current code/Actions/logs. Older continuity/status files describe earlier stages and must not override observed holdout consumption.
GitHub Actions query for implementation HEAD returned no runs. Do not claim this HEAD passed CI.

## Railway inventory
Project IndexAlert: d1c1a050-b7d6-41ce-b300-13c20f82a20a.
Production environment: 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- indexalert-runtime: 37902fde-ca05-43e0-bc76-278992bf7732; deployment 2ae60f51-720c-463f-96cb-c9ef98fc449b SUCCESS; one running replica, zero crashes. Server source branch index-alert-server. Current /health observed 2026-10-05T09:16:40Z: ok=true, firebase=true, poll_seconds=60, version=1.2.0. Volume indexalert-data f96f985a-8aba-41ef-88df-f76999c4ff0c, 500 MB, /data. This health check is not new handset E2E or model evidence.
- indexalert-pit-rebuild: 225f2279-d728-4e1a-a3f3-2447ff0f9dc1; implementation pin 1bf1a69e8db44f24b6426b7069ce332788e81d1c; root /pit_rebuild. Latest containment deployment 11c68209-a9a2-4de7-9469-f914a59ccdc9 SUCCESS. Start command is a standard-library read-only result audit; restart NEVER. Completed batch has zero running and zero crashed replicas. Volume indexalert-pit-data 03f389e5-5030-46a9-bfa5-dd8aa3dc24fa, 5000 MB, /pit.
- indexalert-krx-historical-worker: 003812ee-102b-42b6-bda4-36925885b428; deployment 66439d6d-7a92-4f9e-9fde-eddb540bc954 SUCCESS, source pin ceb134a0a049363a34fbe2b59ef8a4d9c8997811 on index-alert-research-v1-krx-economics-audit; start research_v1_krx_offline_structure_audit.py, restart NEVER; completed batch zero running/zero crashed. Volume 61610fae-dc0c-493e-9920-eb3cef4cea86, 5000 MB, /data. Actual current mode is offline structure audit, not the older preflight-only description.
- indexalert-backend / indexalert-push are legacy FAILED/offline services; db-query-readonly has never deployed/offline; verify-deployment-status last deployment SUCCESS. Do not delete or relabel them as healthy.
Environment pending work: none at final status query. One earlier PIT failure within 8 hours (93606b06-6779-4773-8a05-6cd905ba117b) remains historical, not a new containment failure.

## Observed holdout consumption and containment
Original evaluator deployment d607ddfd-7f76-44aa-b1b3-d566fe046bb4 completed at 2026-10-05T08:05:26Z:
sealed_evaluation=COMPLETE, passed=false, metrics_emitted=false, result_written=/pit/private/sealed_holdout_result.json, pass_rule_status=PREDECLARED_BEFORE_EVALUATION.
Read-only containment deployment independently observed result_exists=true, passed=false, cutoff=2026-09-25, policy_changed_after_unseal=false.
Result bytes SHA-256: 30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82.
No model execution/network collection/result mutation in containment. Promotion/live authority reported false.
DO NOT describe this window as unopened. DO NOT delete/overwrite result, manifest, receipt, source data or baseline. DO NOT rerun evaluation, acquire replacement data into this namespace, reset one-shot state, change cutoff/pass rule, or tune from this result. passed=false is an observed result, not a clean independent Final-Judge validation.

## Integrity blockers
1. Evaluator computes v2.engineer(allx) on combined history + fresh data, then selects train by decision date <= cutoff. engineer constructs ret1/ret2/ret3/ret5 with future-session joins. Evaluator does not enforce label outcome end <= cutoff or the frozen purge. Thus a pre-cutoff training decision can receive a post-cutoff fresh outcome label. Code-level label-overlap defect must be independently audited; no outcome-guided repair and rerun of the consumed window.
2. Evaluator does not invoke validation_stage_gate.check("sealed_holdout"), validate the manifest/receipt/source/baseline bindings, or reconcile all independent Master Spec source/execution prerequisites before reading/modeling fresh data. A standalone result-file existence check is not full authority admission.
3. Manifest asserts never-inspected/frozen-before-access booleans without proving development access lineage. Older records describe development through 2026-09-28, while this holdout cutoff is 2026-09-25. Actual extent of overlap must be established from metadata/access evidence without inspecting new outcomes; do not silently claim overlap resolved.
4. Evaluator trains on all supplied history; the v2 development policy documents rolling 1260-session training with purge 5. Freeze equivalence and primary-rule provenance must be audited, not assumed.
5. Real complete affected-position fill/recovery economics, source A-F/PIT admission and genuine independent broker execution evidence remain open. Current KRX logs explicitly keep exact_status_economics_ready=false, realized_fill_economics_proven=false, realized_recovery_cashflows_proven=false and source C/D/E closed=false.
The observed failed/consumed window and validation-integrity defects block Shadow S1, Fresh Confirmation S2 and production promotion.

## Completed in this continuation
- Queried live GitHub repo metadata, branches, source files, implementation HEAD and Actions; Railway inventory/config/volumes/deployments/runtime health/logs.
- Reconstructed current implementation vs older chat/status drift.
- Preserved consumed failed holdout result; changed PIT start from evaluator to read-only audit and restart NEVER, deployed and verified success + result SHA.
- Observed current server health; preserved all volumes and source/code pins.
- Queried research-room context and repository ledger. No new ACCEPTED/ACCEPTED_CHALLENGER trial with preregistration fingerprint and independent OOS evidence was verified; no new performance research was applied.
- Recorded blocker and exact continuation boundaries in this handoff.

## Major existing commits
b0a723ef4ae7e0a621d17996318021ec0ae73879: earlier PIT fix, historical.
1ea1173c1390b554dccea5787277d731118420fa: verifier selection fingerprint semantics.
0dd22db33685b65213899bf712218a3b9ed5d1d4: exact PIT session calendar checks.
ba55cc2a9029bc2c5b93081668985fccfb091427: development baseline artifact replacement; NOT production model promotion.
eab6bd53f9395f22e177196f09dca3e0a5e709ff: fingerprint regression included in image.
580a99efabf892bf3e77f6668309f00e39b1bcdf: manifest acquisition/receipt prerequisites in standalone gate.
5991644d0c5b790923e6c7b2ba686bc3d62828bd: evaluator included in image.
79ee4fb189b51fee8cb547dbbdfde756ef94d34f: PIT schema probe.
1bf1a69e8db44f24b6426b7069ce332788e81d1c: normalized decision_date support.

## Frozen boundaries — never alter from outcomes
- Existing H5 Core research: train/cal/test 504/126/126, horizon-matched purge/embargo, original decision-time Top3, no rank-4+ backfill, 0..3 and NO_TRADE valid, q25/cost/recency/execution gates unchanged.
- H10 REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE; H6-H9 sweep forbidden; H20 archive/out of scope.
- v3 development artifact is a separate policy lineage from H5 Core. Do not treat its artifact replacement or simple primary pass rule as satisfying Master Spec promotion.
- v3 baseline selection fingerprint 8a442cbf42ff8449e9d7d6a28e9ac7e4215e2997d45aa6e17e109318598a6156; position fingerprint 53c6e32d18fb75f61825da07423f0f6e21b839ea234069e69e3d1c153a81387f.
- Consumed evaluator cutoff 2026-09-25 and predeclared primary H1, 1% coverage, 25bp, >=30 trades, mean net >0, positive fraction >0.50 remain immutable historical records; no weakening after failure.
- Execution protocol minimum 600 genuine LIVE observations / 200 dates / 400 fills and 0.0005 PIT ADV capacity unchanged. Synthetic/demo/paper data cannot close genuine LIVE provenance gates.
- Holdout -> Shadow S1 -> Fresh Confirmation S2 progression requires valid independent admission. Current window cannot progress.
- User authorizes development/test/deploy/validation continuation. Real stock orders, funds movement and brokerage permissions require separate explicit authorisation.

## Exact next steps
1. Re-fetch active branch HEAD, this handoff, source pin and Railway production pending state. Keep read-only PIT start and NEVER restart.
2. Verify result SHA remains 30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82 via read-only metadata audit; never invoke evaluate_sealed_holdout.py.
3. In an isolated audit branch, build synthetic-only tests demonstrating boundary-label leakage and gate bypass, without reading actual private outcomes. Audit historical immutable freeze/manifest/acquisition/access metadata for cutoff contamination. Preserve failed evidence and negative dispositions.
4. Record consumed current-window disposition and source/execution blockers in canonical ledger/status by reference to this evidence; do not retrofit a pass or repair-and-rerun.
5. A genuinely new prospective trial needs an independently preregistered ID/protocol/freeze, source/execution prerequisite admission and data not already inspected. Do not select a new cutoff/window to rescue this candidate from observed failure.
6. Continue official source/PIT/status evidence work that is independent of consumed outcomes. Accept researcher proposals only with exact trial/protocol/OOS evidence; no direct Core replacement.
No additional user approval can turn the consumed invalid window into valid holdout evidence.

## 2026-10-05 19:02 KST — automatic-trading preparation continuation
User goal: continue until a result suitable for real automated trading; development,
testing and deployment approved, real orders/funds/account permissions excluded.

Completed:
- Rejected unknown/string actions and malformed engine payloads.
- BUY/REPLACE require positive conservative reservation and symbol identity.
- HOLD/EXIT/NO_TRADE cannot disguise added exposure.
- Aggregate reservation accounts for positions, open buys, uncertain submissions and fee buffer.
- Lowering the user capital ceiling no longer blocks zero-exposure exits/idle plans;
  new exposure still fails closed.
- Existing 8 and new 8 tests: 16 PASS locally; Actions 37293705791 and 37293711189 SUCCESS.
- PR #6 merged; implementation commit 9f7a0249e4f21a86dada4cf0bb1a33d12ca3fa14
  (repair head 555b3c29e596cbf6218fc1fab0ccdc2c19c7c191).
This broker-neutral module is research/development code, not a deployed live broker loop.
No strategy/model/threshold/holdout change and no broker request/order occurred.

Live platform verification:
runtime /health at 2026-10-05T10:01:11Z: ok=true, firebase=true, poll_seconds=60;
runtime deployment 2ae60f51-720c-463f-96cb-c9ef98fc449b remains SUCCESS.
PIT deployment a2cd6b78-90d8-4a46-a140-642ba2edf86e remains SUCCESS;
source pin 03140e9f9c5327bb79b1b0621dafa6e6908ca700 and read-only audit unchanged.
Environment pending work none. Brokerage credential names exist, but connector
redacts values: current KIWOOM_ENV and KIWOOM_ORDERING_ENABLED values were not
verified; never infer live configuration from variable presence.

Actual completion blockers:
1. Consumed v1 failed/invalid holdout is immutable. No rescue rerun or cutoff change.
2. Historical terminal-status materializer emits available_at=NaT intentionally:
   archived historical publication/availability evidence is missing. Do not backdate
   current retrieval times or substitute event dates as availability.
3. Realized affected-position fills/recovery cashflows and 56 no-cleanup terminal
   episode resolutions remain independent evidence requirements.
4. Frozen EXEC-SUFFICIENCY-v1 requires 600 genuine LIVE observations, 200 distinct
   decision dates, 400 fills and 120 near-capacity observations; demo/synthetic
   results and programming effort cannot manufacture these samples. The 200 dates
   require observation time; immediate full completion is not evidenced.
5. A validated independent candidate, source/execution admissions, prospective
   validation and permitted release-stage progression are still required.
6. No broker-capable live release or account permission change is authorised here.

Next exact executable work: verify new HEAD and CI, keep deployed read-only pin;
resolve actual archival source/availability and official terminal-economics evidence
through permitted evidence sources. Only independently preregistered research can
create an accepted successor; do not weaken frozen sample or promotion gates.
Current real-trading-ready=false. These are evidence/authority blockers, not CI failures.
