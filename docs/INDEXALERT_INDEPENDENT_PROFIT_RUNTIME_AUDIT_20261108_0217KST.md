# IndexAlert independent read-only audit — 2026-11-08 02:17 KST

## Immutable scope and heads
- Research `index-alert-research-v1` HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub compare self/self).
- Development `index-alert-position-regen-fix-v1` HEAD: `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub compare self/self).
- PRs #412 OpenDART, #413 runtime optimisation, #414 integration gate, #418 independent one-runner, KRX #420/#422/#423: open search results, all remain unmerged as far as observed. Search metadata does not independently certify each exact PR HEAD or draft flag in this run; those fields are NOT VERIFIED.
- Integration gate source path `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`: direct fetch on research branch returned 404; no independent current blob SHA claim this run. Previous `984c933651f39f1ee9e26a1d7ac3893aaa5335be` is prior evidence only.

## Exact CI evidence checked now
- OpenDART [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 jobs success; original SGML row signature is structural only, original semantics and available-at NOT VERIFIED.
- One runner [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 job success; synthetic-only.
- Optimisation [38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499): 6/6 jobs success; archived 34-case canonical SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` reported in PR #413, not recomputed from downloaded artifacts this run.
- Chronology anchor [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE; validation SKIPPED.
- One-runner regression-phase serial 2.9656 s vs concurrent 2.6209 s = 1.1315x (historical PR evidence only); full CI speed and actual official backtest speed NOT VERIFIED. Another #413 CI #38498552499 reports parallel slower (0.664x), demonstrating run-to-run variability.

## Railway direct read-only
- IndexAlert project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Environment staged=null; no deployment/config changes.
- PIT rebuild latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (2026-10-10); KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12); readonly REAL `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (2026-10-29); runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS (2026-10-05). SUCCESS does not prove live replica health.
- PIT 2026-11-07 21:00–23:16 KST logs: repeated `KRXProspectiveOpenAPISourceError`, `COMMON_OHLC_NONPOSITIVE`; independent source, chronology, model, alpha and trading authority flags false. Earlier logs documented 803 common-stock rows, 27 invalid OHLC and 27 zero-volume/value, original failed session 2026-09-28, manifest SHA null; these counts were NOT independently re-extracted from complete log JSON this run.
- No fresh PIT, KRX or REAL readonly deploy log lines after 2026-11-08 01:00 KST in the queried range. Absence of logs is not proof of recovery.
- Runtime last retrieved entries at 2026-11-08 02:17 KST include Investing.com USD/KRW HTTP failure followed by Yahoo fallback; not a source PIT admission.

## Decision matrix
| Evidence gate | Verdict | Reason |
| --- | --- | --- |
| Offline CI job outcomes (specified runs) | PASS | Exact GitHub Actions job results read |
| Official OpenDART original filing semantics / public available-at | NOT VERIFIED | SGML candidate shape is insufficient |
| 2021/2022 first three-month consolidated operating profit correction lineage | NOT VERIFIED | Period/filing revision/vintage unadmitted |
| Historic issuer-security mapping, KRX calendar/status/corporate actions/fillability | NOT VERIFIED | Private SHA pair integrity is not market-state PIT |
| Prospective PIT admission | FAIL (fail-closed) | Repeated OHLC source error, admission flags false |
| Costs/taxes and NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness | NOT VERIFIED | No admitted market replay |
| Actual full backtest/whole CI speedup | NOT VERIFIED | Synthetic regression timings only |
| M20 profitability RUN | NO-GO | PIT/source and chronology gates unapproved |
| ORDERING | false / DISABLED policy | No orders or live authority granted |

## Next safe work
1. Independent original first-filing bytes and public available-at/period/correction lineage evidence, SHA-pinned and reviewed, without replay.
2. Independently authenticate historical exchange calendar, security-day trading states, corporate actions, costs and executable fill model; quarantine 90 uncertain sessions, 27 invalid OHLC, and 12,003 zero-activity observations.
3. Reconcile exact immutable code/policy/data/runtime/approval SHA-256 manifests, fail-closed cache keys and only read-only independent postprocessing; no dependent retraining or capital-transition parallelisation.
4. Recheck chronology-anchor failure from its existing logs without changing workflows; preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, purged/CPCV, consumed Holdout, Champion, Top3/NO_TRADE and costs/taxes.
5. Require separate explicit approval for any real order, money movement, credential/entitlement change, Champion promotion or M20 economic run. No merges, production deployments or workflow edits.

This audit changes documentation only on a new isolated branch.