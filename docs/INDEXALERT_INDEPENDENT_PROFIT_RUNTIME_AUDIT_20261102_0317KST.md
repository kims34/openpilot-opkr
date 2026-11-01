# IndexAlert independent profitability + isolated runtime audit — 2026-11-02 03:17 KST

**Mode:** read-only evidence inspection, isolated document-only write. Forked from previous audit commit `27ae75f0aef77dae069be5ef77c34927ea4b6a91` into independent branch `indexalert-independent-profit-runtime-audit-20261102-0317`. No research/development/owner branch code modification, workflow edits, market replay, M20 profitability run, holdout reuse, order, deployment, PR merge, or strategy approval.

## Source/PR provenance independently re-read this run

| Source | Exact HEAD | Decision |
|---|---|---|
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | Frozen, no change |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | no change |
| KRX specialist `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | historical market PIT not approved |
| [Draft #414](https://github.com/kims34/openpilot-opkr/pull/414) | `d87abda4e05087c80321fbb921499d60c6938a33` | owner advanced HEAD since 02:17 audit; frozen gate document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` unchanged; no approval |
| [Draft #412](https://github.com/kims34/openpilot-opkr/pull/412) | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | source-only |
| [Draft #413](https://github.com/kims34/openpilot-opkr/pull/413) | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | 34-case offline parity LIMITED PASS |
| [Draft #418](https://github.com/kims34/openpilot-opkr/pull/418) | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | archived source replay FAIL-CLOSED; adoption NO-GO |
| Other specialist PRs | #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f` | no overlapping modifications |

## Direct GitHub Actions evidence

- Latest [read-only Watchdog #41323960188](https://github.com/kims34/openpilot-opkr/actions/runs/41323960188), created 2026-11-01 15:59 UTC, job `124899883924` SUCCESS. Original job log explicitly: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded artifact `13090537553` ZIP SHA-256 `004aa1cbc4981680683b4cec164a53924c839564ab499b845052fdf47693a4a4`. This is metadata/synthetic safety evidence, not economic validation.
- [OpenDART official-source #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): two jobs `115372550463`, `115372636726` SUCCESS, candidate rows 15 and adjacent numeric signature matching first/corrected SGML. Official first-filing 2021/2022 standalone consolidated three-month operating-profit **period, unit, amount, available-at and complete correction lineage remain NOT VERIFIED**. Earlier first-original ZIP SHA-256 2022 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 2021 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`: prior fingerprints only, not rehashed in this run.
- KRX official 2017–2022 private 1,565/1,565 weekday source-pair storage integrity **prior LIMITED PASS**, not proof of official exchange calendar/trading status. [Synthetic KRX #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), job `119612852155` SUCCESS only. The 90 uncertain sessions, 12,003 zero-activity records, historical issuer/security identity, corporate actions, market-state/fillability, fees and tax remain NOT VERIFIED.
- [#413 parity #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs SUCCESS. Original parity job `115670744341` printed `RUNTIME_OPT_PARITY`: 34 cases, case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, identical outcomes, serial 1.7650 s, parallel longest suite 2.7079 s, speed ratio 0.652 (parallel slower). Earlier #38381997417/#38382214223 each 6/6 and #38419111311 13 adversarial mocks: prior offline-only evidence. No full CI or official backtest speedup attested.
- [#418 archived replay #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395` FAILURE: `SourceDriftError` for `research_v1_runtime_manifest.py`, expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Earlier source review found missing equivalent no-follow/fd/inode and strict receipt boolean protections relative to #413. Separate synthetic one-runner success cannot override archived gate. NO-GO.
- [Chronology #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) anchor job `124184971844` FAILURE, dependent job skipped. Prior Railway HTTP evidence: 20 GET `/anchor/latest` returned 404 on 2026-10-30 16:35–17:13 UTC; no response body, root cause NOT VERIFIED. Do not treat 404 alone as verified `NO_ANCHOR`.

## Railway production read-only evidence

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.

- PIT service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`: deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1 running / 0 crashed. Query since 2026-11-01 14:00 UTC returned four records, latest 2026-11-01 14:46:22.425 UTC (23:46:22 KST). Each shows session 2026-11-01 but `source_failure_session=2026-09-28`, `COMMON_OHLC_NONPOSITIVE`, 803 common-stock rows, 27 quarantined, independent source/chronology/model admission false, `FAIL_CLOSED`, `ORDERING=DISABLED`. This is repeated rejected-source reporting, not evidence of new accepted market data. No later PIT records in this queried interval; Sunday night / premarket cadence is NOT VERIFIED, not proven outage.
- Separate `indexalert-runtime` index/FX service `37902fde-ca05-43e0-bc76-278992bf7732`, deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, 1 running, latest log 2026-11-01 18:17:56 UTC (2026-11-02 03:17:56 KST). This is not M20 PIT or brokerage proof.
- Kiwoom read-only `93074d5f-70b3-48e4-8671-a3c5b23daf7e`: deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (2026-10-29 06:21 UTC, commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`) while environment health reports 0 running / 1 crashed replica, no newer deploy log in query. Actual connectivity NOT VERIFIED.
- Environment still reports staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29 06:20:53 UTC, with empty changes in this view. Previous `get_staged_changes` reported none; cross-API discrepancy NOT VERIFIED. No patch applied.

## Independent decisions and next evidence gate

**LIMITED PASS:** KRX private storage pair integrity (prior evidence), #413 34-case synthetic identity/result parity, selected OpenDART source/candidate signatures (not semantic or timestamp proof).

**FAIL-CLOSED:** 27 OHLC quarantines, chronology anchor fetch failure, #418 archived source manifest mismatch and non-equivalent archived gate; no promotion.

**NOT VERIFIED:** first-public original DART 2021/2022 consolidated 3-month operating profit period/units/value/available-at/correction lineage, historical issuer-security mapping, official KRX calendar/trading lifecycle/corporate actions/fills/fees/taxes, chronology 404 cause, full CI/real backtest speed, Kiwoom replica discrepancy, PIT cadence, staged-patch API discrepancy.

**NOT EVALUABLE / NO-GO:** after-cost/tax M20 NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness and annual risk-adjusted net profit. No M20 economic run or model search.

Next: independent first-filed DART public-time proof; authoritative KRX historical market and execution/cost/tax evidence; original response body/receipt for chronology; #418 owner to resolve archived SHA drift and strict file/receipt safety using synthetic-only tests; check PIT service after a normal market session without restart. Keep Frozen H5, consumed Holdout, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, preregistered risk/cost/tax thresholds unchanged. Cache only exact independently admitted source/data/code/Frozen/runtime/approval evidence SHA-256, fail-closed; parallelize read-only independent postprocessing only, never dependent retraining or capital transitions. No orders, funds, account/credential changes, Champion promotion, workflow edits, PR merges or production deployment.
