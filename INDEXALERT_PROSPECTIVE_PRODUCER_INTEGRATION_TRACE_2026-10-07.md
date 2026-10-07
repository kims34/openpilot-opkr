# Frozen H5 prospective producer integration trace — 2026-10-07

Inspection only; no historical replay, model fit, private raw-data read, holdout access, network acquisition or deployment. Research ref194da5016ad3aecc2ceb25944666daa74f038083. This narrows the previously identified capture gap to exact existing functions and their missing runtime inputs; it does not create or adopt a new policy/trust root.

## Existing source path

| Stage | Existing source and blob | Actual interface | Integration limit |
|---|---|---|---|
| Fixed policy metadata | research_v1_fresh_alpha_protocol.py / fae9a7302d4054d11951aaca1c3d60110a1f8315 | load_protocol, validate_protocol, eligible_decision_timestamp | Validator only; does not generate signals or record sessions. |
| Historical diagnostic entry | research_v1_recent_gate_diagnostic.py / 0dafde6f6a2411005599dc9754d56ae151d6fe27 | load_panel -> load_or_build -> add_context -> add_fixed_horizon_target -> selected_calibration_walk_forward -> window reports | Historical evaluation CLI, default private research_data and research_results paths; not a deployed prospective producer. |
| Mean and residual calibration | research_v1_selected_calibration.py / 1975688b15291999a86d529563c64e02753224ed | selected_calibration_walk_forward trains _pipe on fh_label_available rows, predicts calibration/test features, applies calibration-only selected residual quantiles | Model and quantiles are local objects; returned outputs are combined retrospective predictions/fold metadata, not an independently identified deployed model/calibration snapshot. |
| Prediction helpers | research_v1_distributional_netev.py / 4019f01a58c1378edeec7ace55215a62b4ad6fd4 | _pipe, _apply_distribution, freeze_original_topk | Reusable mathematical helpers do not supply real decision-time feature/PIT evidence, universe identity or durable capture. |
| Legacy research reporting | research_v1_decision_report.py / 8f5db01c7143fdfe8b3d2ad15f01f492dd820afd | loads old research result JSON and writes comparative decision report | “decision” filename denotes a research comparison, not a live session decision ledger. |
| Successor staging | research_v1_successor_core.py / c5049a5345ce1a916fa41812fa0764a7bd29602e | build_successor_artifact, assess_successor_eligibility | Caller booleans do not provide independent admission; explicitly not promotion/live authority. |
| Private KRX objects | research_v1_krx_private_store.py / 93a0bd839d31fc6b099ba7660a55f1bc75529e2c | private raw/JSON atomic storage and content verification | Acquisition object storage is not a H5 prospective signal ledger or model identity. |

The historical selected-calibration loop uses anchored train dates[:train_end],126 calibration sessions,126 test sessions and H5 separation when invoked with the frozen defaults. Do not replace anchored training with rolling504 merely because a summary calls the reference504/126/126. No code or parameter was changed here.

The loop's test model prediction itself does not require test outcomes; however its historical entry prepares fixed-horizon targets/record maps and evaluates executable/stateful admissions with historical records. A prospective adapter must preserve this distinction: mature training/calibration outcomes may be used under exact availability rules; same-session H5 outcomes cannot be supplied at decision time. Do not call the historical evaluator and relabel replay output as a real-time recommendation.

## Required concrete integration inputs

1. Independently identified frozen reference model/calibration state (or the already approved exact prospective refit schedule and anchored data cutoff), with original source/feature lineage and identity. No unreviewed refit cadence or model artifact is inferred from fold metadata.
2. Exact real decision-time feature/universe/normal-market status input with original availability timestamps. Retrieval time must not become historical availability; missing values must not become synthetic history.
3. Defined actual decision-time capture and private append-only session store. Every eligible session, including genuine NO_TRADE, must be recorded when produced; skipped sessions cannot be backfilled.
4. Outcome attachment only when real H5 outcomes become available, preserving corporate-action-safe return/cost rules and observed evidence.

The existing protocol describes the frozen diagnostic policy and reports, but the inspected producer functions do not establish these runtime inputs/cadence/store. A recorder alone cannot authenticate invented outputs. Current disposition remains ACTUAL_CAPTURE_AND_STORAGE_NOT_VERIFIED, not formalShadowS1/S2, ACCEPTED successor or live permission. No new observation count or126/504 completion clock is claimed.

## Owner actions settled in this session

- User now defines “ㅇ” as continue toward small-capital automatic trading until a genuine owner dependency is encountered; real orders/funds/broker permission changes still require separate explicit authority.
- Owner reported clicking Kiwoom Q&A registration at21:55KST. Submission is owner-reported; no ticket ID or independent submission receipt seen. Wait for reply before unchanged8050 reruns.
- KRX email body/date and displayed sender/mailed-by evidence received, matching existing rights scope; no additional permission request.
- Android original-key backup availability: owner answered “모르겠음” at21:54KST. Preserve installed production app; no repeat completed USERPROFILE search, uninstall or clear-data. Existing isolated Preview remains the reversible engineering path.

Frozen H5/Core/PIT/labels/WF/PurgedCPCV/purge/embargo/cost/capacity/promotion rules and consumed failed-invalidv1 holdout are unchanged. MASTER_OFF; all real-order/funds/permission authority false.
