# IndexAlert independent profitability / isolated runtime evidence — 2026-10-28 15:21 KST

Scope: READ-ONLY GitHub source/PR/Actions and attempted read-only Railway project discovery. This file is a segregated audit receipt only. No specialist code, workflow, market source, Frozen policy, Holdout, Champion, deploy, merge, orders, credentials, funds or permissions changed. `ORDERING=false` is mandatory policy; live Railway setting could not be directly inspected.

## Live GitHub references actually read

| Subject | Exact HEAD or ref | Finding |
|---|---|---|
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | unchanged from prior independent audit |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | unchanged |
| OpenDART Draft PR #412 | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | OPEN/DRAFT |
| Runtime Draft PR #413 | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | OPEN/DRAFT |
| Integration Draft PR #414, before this receipt | `09bd564cac8cad920d59ba3b3a55477d051a5961` | OPEN/DRAFT; independent receipts may advance this branch |
| Flow Draft PR #416 | `053de553646fc4765d2616544ca1e8d6bbdde35f` | OPEN/DRAFT |
| Single-runner Draft PR #418 | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | OPEN/DRAFT |
| KRX audit branch | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | read-only |
| KRX Draft PR #420/#422/#423 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f` | OPEN/DRAFT |

Integration policy document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` at #414 HEAD has Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; not edited. Prior [14:18 independent receipt](https://github.com/kims34/openpilot-opkr/blob/7df5b93565ce38847ebf761c651c875fc831d07b/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261028_1418KST.md) has blob `07b071212fee7da26772a1e1b7dd37c502c7e654`, and was directly fetched again.

## Newest Actions and independent job-log inspection

- [Newest watchdog run #40638905543](https://github.com/kims34/openpilot-opkr/actions/runs/40638905543), created 2026-10-28 05:35:44 UTC / 14:35:44 KST, HEAD `04bdfc93975bb59961f1cb3bd3598d04f8e7bff4`, job `122652181922` SUCCESS. Decoded log states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Artifact ID `12795145293`, GitHub uploaded ZIP SHA-256 `e2ba2a470207125f1d061b5378fe1a1e68f1676ad4dee9d5bae36686ec297903`. This is **synthetic/offline governance PASS only**, not live Railway authorization or source PIT admission. It supersedes the prior 08:44 KST watchdog as latest returned run.
- [Prospective chronology anchor #40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813), job `122295113858` FAILED with prior observed HTTP 404; follow-on job `122295116456` SKIPPED. No new valid prospective available-at attestation. No endpoint edit/retry.
- [#413 34-case parity #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773), six jobs SUCCESS, parity job `115670744341`, fixed outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, serial 1.7650s vs parallel 2.7079s = 0.652x (regression-phase speedup **FAIL**). No full-CI or actual official backtest speedup.
- [#418 one-runner #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562), job `117628139856` SUCCESS; fixed 34-case SHA matches, observed 2.3484s vs 2.0154s = 1.1650x for that particular offline regression phase. The log also has a distinct four-case negative-control microfixture with sub-millisecond serial time and <1x ratio. Neither result certifies total CI/official H5/M20 acceleration.
- [#418 candidate merge #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494), job `117628139749` SUCCESS as a safety check, but decoded log explicitly `candidate_approved_for_merge=false`, `all_transitive_imports_pinned=false`, `exact_wheel_hashes_verified=false`, `os_native_dependency_identity_verified=false`. [Archived source check #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395` FAIL_CLOSED: `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, merged-context observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Direct standalone file reads again establish #418 former and #413 latter; branches are diverged (49 ahead / 18 behind), not safely combinable. #413 requires literal `False` for holdout/order authorization and present aliases, and uses no-follow fd identity checks; #418 standalone tests only `is True` and opens by path after symlink check. Do not repin archived source.
- [KRX #423 offline #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677` SUCCESS on synthetic source-scope tests. The log explicitly checks `DRY_RUN_NO_PRIVATE_STORAGE_READ`, `2022_private_candidate_date_sets_equal=false`, and `ordering=DISABLED`. No official KOSPI calendar/market-status admission.

## Source / economics evidence matrix

| Gate | Independent status | Reason |
|---|---|---|
| OpenDART original 2022 / 2021 ZIP source integrity | **Historical PASS** (prior Action log digests, not independently re-downloaded in this run) | 2022 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; 2021 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` |
| First-filed 2021/2022 exact July–Sept CFS three-month operating profit, original/amendment cell lineage, public available-at | **NOT VERIFIED** | candidate SGML labels are not authoritative financial-cell/period/PIT proof; 2021 prior 13 table candidates with zero exact same-table bindings; 2022 15 candidates |
| Historical issuer-to-tradable-security as-of mapping | **NOT VERIFIED** | no independently attested corporate/security PIT |
| KRX 2017–2022 stored raw weekday pairs | **Historical storage-integrity PASS** | previous Railway aggregate 1,565/1,565, not directly rechecked in this run |
| KRX official venue-specific calendar, 2021 13 / 2022 14 private date-set equality, halt/CA/volume/fills | **NOT VERIFIED** | 90 uncertain source/calendar sessions, 27 nonpositive OHLC, 12,003 zero-activity quarantines; dry-run synthetic CI cannot certify live source |
| Costs/taxes, actual fills, annual risk-adjusted after-cost/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness | **NOT EVALUABLE** | no PIT-admitted market source or authorized frozen economic run |
| Optimization #413 parity | **PASS** offline only | fixed 34-case SHA matches |
| Optimization #413 regression-phase speedup | **FAIL** | 0.652x |
| Optimization #418 standalone parity | **PASS** offline only | fixed 34-case SHA matches |
| Optimization #418 merge-source integrity | **FAIL_CLOSED** | archived manifest blob mismatch; transitive dependency/wheel/OS pinning incomplete |
| Full CI / genuine market backtest acceleration | **NOT VERIFIED** | phase-only synthetic measurements |

## Railway access and exact next gates

Read-only `Railway.list_projects({})` was attempted once; connector returned **`User input required but current turn is running in a non-interactive mode.`** Do not bypass. Current deployment IDs, live logs, live `ORDERING` value and private source date-set comparison **NOT DIRECTLY VERIFIED**. Separately authorized interactive Railway connector read-only access is required for those exact facts; historical status does not replace fresh observation.

**M20 PIT admission = NO-GO. M20 profitability run = NOT AUTHORIZED.** Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, sealed independent Holdout, Champion/Top3/NO_TRADE, original cost/tax/risk/promotion criteria and `ORDERING=false` remain unchanged. H5 failed/consumed Holdout and Dynamic observations cannot be retuned/reused. No source admission, synthetic result or cached hash is financial evidence.

Finite next evidence: (1) original-filing CFS three-month numeric cell and first-publication instant, 2021/2022 with correction chronology and issuer-security PIT; (2) KRX official KOSPI session and per-security halt/CA/fill/cost/tax as-of proof, exact private source hash/date-set; (3) #418 full transitive closure, independently approved receipt and full CI wall-time benchmark, without altering baseline; (4) only after independent gates, separately authorize any frozen economic execution. No new material admission or critical blocker beyond previously documented issues this run.
