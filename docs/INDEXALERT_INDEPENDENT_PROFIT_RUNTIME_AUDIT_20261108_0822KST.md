# IndexAlert independent read-only evidence audit — 2026-11-08 08:22 KST

Scope: independent profitability gate and isolated offline runtime-optimization evidence. No market backtest, model search, holdout reuse, deployment, broker action, workflow edit, or merge.

## Immutable GitHub refs independently checked
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`; compare to this SHA: identical, ahead/behind 0/0.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`; identical, ahead/behind 0/0.
- All following PRs are OPEN/Draft/unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`: Git blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (direct fetch at PR head).

## Current read-only CI verification
- GitHub Actions runs [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), [38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): each 6/6 completed successful jobs, **offline software parity only**.
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 completed successful one-runner offline job.
- [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 completed successful OpenDART candidate/security jobs, not original financial-cell/PIT admission.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296) and [40360864884](https://github.com/kims34/openpilot-opkr/actions/runs/40360864884): auto-anchor FAILURE; validation SKIPPED.
- Historic immutable 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic additions, serial 2.9656s / concurrent 2.6209s (1.1315x regression phase) are **prior evidence only**; this run did not download/recompute artifact bytes or full CI wall-time. Other reported offline parallel slowdowns mean real backtest acceleration is NOT VERIFIED.

## Railway production direct read
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`; staged patch **null**.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c`, real-readonly `a77fb922-b679-4d88-92c4-03054ec579cd`: deployment summaries SUCCESS, configured replicas 1 each. These are **not** proof of live healthy instances.
- Fresh deploy-log query from 2026-11-07 21:00 UTC returned **zero entries** for each of PIT/KRX/real-readonly; cannot claim source recovery, new authoritative KRX dates, or broker service health from absence of logs.
- Backend and push latest deployment summaries FAILED (2026-09-23). Readonly DB service latest deployment null. Previous observed real-readonly crashed instance and OHLC 27/803 are historical alerts, not independently reobserved in this window.

## Admission matrix
| Evidence | Status | Reason |
| --- | --- | --- |
| 2021/2022 original ZIP and historical KRX 1565/1565 stored pairs | PASS only for previously documented narrow byte/storage integrity; NOT REVERIFIED today | No new raw provider bytes or private volume manifest independently recomputed |
| OpenDART first-filed consolidated operating-income Q3 3-month cells, corrections lineage and exact public available-at | NOT VERIFIED | Candidate rows/SGML matching do not bind semantic account, reporting period, release timestamp |
| Historical issuer/security as-of mapping | NOT VERIFIED | No independently attested historical mapping |
| Official KRX session calendar, halt/delist/corporate actions, fills, fees and taxes | NOT VERIFIED | Offline controls and private weekday pairs do not establish official execution status |
| Chronology anchor | FAIL | Original GitHub Actions auto-anchor failed and validation skipped |
| Offline runtime software regression parity | PASS limited to observed CI jobs | No production economics or full pipeline acceleration attestation |
| Actual end-to-end speedup | NOT VERIFIED | No approved production-equivalent benchmark |
| Annual post-cost/post-tax risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness | NOT VERIFIED | Source/PIT/official execution blockers; no authorized M20 run |

## Immutable safety / next admissible work
- **M20 NO-GO**. **ORDERING=false** / no order authority; no live configuration mutation was attempted. Preserve Frozen H5, horizon20/purge20, WF504/126/126, PIT, Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE and existing costs/taxes/risk/upgrade policy. Never reuse failed/consumed H5 Holdout or post-hoc Dynamic evidence.
- Keep #413 and #418 isolated, cache fail-closed on independently approved source/data/code/Frozen/runtime/approval SHA-256 identity, parallelize only independent read-only postprocessing; no dependent retraining/capital transitions.
- Next: independent official OpenDART original filing account/period/vintage/public timestamp attestation; private KRX official session/status and corporate-action/fill reconciliation; chronology anchor restoration verified by a new read-only check; only then separately authorize economic validation. No PR merge, deployment, workflow edit, broker action, model search or M20 replay.
