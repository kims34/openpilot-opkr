# IndexAlert independent profitability + isolated runtime audit — 2026-11-02 04:22 KST

**Scope / isolation.** Read-only GitHub and Railway inspection; document-only append on pre-existing isolated audit branch `indexalert-independent-profit-runtime-audit-20261102-0317` (pre-write HEAD `36a7117ea8229c664706df8daf1625296fc3841d`). No edits to research/development/owner branches or workflow; no official-market replay, model search, M20 profitability execution, Holdout access, broker/order/fund/permission action, deployment, PR merge or Champion promotion. Earlier audit: `docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261102_0317KST.md` (blob `c2ae37cbbaf43f180e5262e16f740a14a2874919`).

## Independently re-read immutable pointers

| Ref | HEAD / blob SHA | Scope |
|---|---|---|
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | unchanged, Frozen preserved |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | unchanged |
| KRX specialist `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | source integrity is not market PIT |
| [Draft PR #414](https://github.com/kims34/openpilot-opkr/pull/414) | `6990f11bee6dae8802ecdb5de37ca075f8d87b35` | owner advanced from prior 03:17 audit `d87abda4e05087c80321fbb921499d60c6938a33`; integration gate file blob still `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; no source admission |
| [Draft #412](https://github.com/kims34/openpilot-opkr/pull/412) | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | OpenDART source-only |
| [Draft #413](https://github.com/kims34/openpilot-opkr/pull/413) | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | offline synthetic parity LIMITED PASS |
| [Draft #418](https://github.com/kims34/openpilot-opkr/pull/418) | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | archived replay FAIL-CLOSED; adoption NO-GO |
| Other specialists | #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f` | no cross-owner code edits |

## GitHub Actions: actual job and log checks this run

- Latest repo Actions query (35 runs) yielded [read-only watchdog #41323960188](https://github.com/kims34/openpilot-opkr/actions/runs/41323960188), created 2026-11-01 15:59:15 UTC, as latest. Job `124899883924` SUCCESS; raw log: **31 synthetic tests**, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is safety, not official source/profit proof.
- OpenDART [#38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 jobs SUCCESS (candidate rows 15 with adjacent-number signatures), and [#38484411722](https://github.com/kims34/openpilot-opkr/actions/runs/38484411722) 2/2 SUCCESS. Pinned original/corrected 2022 SGML normalized text comparison: 1,570 original tables, 1,576 corrected, six corrected-only table texts (prior documented evidence); not proof of exact authoritative first 2021/2022 July–September consolidated operating-profit fact, its first public available-at, correction lineage, issuer mapping or PIT.
- KRX [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) 1/1 synthetic safety job SUCCESS. Private 2017–2022 1,565/1,565 weekday source-pair integrity **prior LIMITED PASS**, not newly rehashed here and not proof of exchange calendar, corporate actions, historical security identity, tradability or execution. 90 uncertain sessions and 12,003 zero-activity records remain quarantined/unadmitted.
- Optimization [#38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) and [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): 6/6 jobs each SUCCESS; [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 SUCCESS, 13 adversarial mocks per previous evidence. [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 SUCCESS; raw parity job `115670744341`: 34 cases, SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, identical outcomes; serial **1.7650s**, parallel longest suite **2.7079s**, speed ratio **0.652x** (slower). Full CI / official PIT-backtest speedup **NOT VERIFIED**.
- #418 [#38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS, synthetic-only; later [#38484754749](https://github.com/kims34/openpilot-opkr/actions/runs/38484754749) and [#38484754752](https://github.com/kims34/openpilot-opkr/actions/runs/38484754752) 1/1 each SUCCESS; however [archived replay #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` FAILURE, raw log `SourceDriftError`: `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Exact wheel hashes and OS-native dependency identity not verified. Fail-closed; no #418 adoption.
- [Chronology #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): anchor job `124184971844` FAILURE, dependent validation SKIPPED. Prior HTTP observations: 20 `/anchor/latest` GET 404 on 2026-10-30 16:35–17:13 UTC; response body not captured, so precise `NO_ANCHOR` cause **NOT VERIFIED**.

## Railway production: fresh read-only inspection

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.

- `indexalert-pit-rebuild` service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1 running / 0 crashed. Last returned PIT log **2026-11-01 14:46:22.425 UTC (23:46:22 KST)**, source failure session `2026-09-28`, 803 common-stock rows, 27 nonpositive OHLC (also 27 zero-volume/value), private rejected-source receipt saved, session manifest SHA null, independent source/chronology/model admission all false, `FAIL_CLOSED`, `ORDERING=DISABLED`, no order/funds/permission authority. No later PIT logs in queried recent interval; this does **not** independently prove a scheduler outage or freshness.
- `indexalert-runtime` service `37902fde-ca05-43e0-bc76-278992bf7732`, deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, 1 running / 0 crashed, separate index/FX notification logs through **2026-11-01 19:23:44.391 UTC (2026-11-02 04:23:44 KST)**. Not an M20 or broker proof.
- `indexalert-kiwoom-real-readonly` service `93074d5f-70b3-48e4-8671-a3c5b23daf7e`, latest deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, yet health snapshot shows **0 running / 1 crashed** while service state says online; physical connectivity **NOT VERIFIED**. No restart.
- `describe_environment` says staged **null**, while `environment_status` shows pending `patch:e113dacb-6705-4416-9997-dc694539d382` with empty changes since 2026-10-29 06:20:53 UTC. Cross-API disagreement **NOT VERIFIED**; no accept-deploy.
- No new production deployment for PIT/worker observed; historical KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS. Empty recent KRX worker logs are not new official validation.

## Independent decision, hard gates and next action

**LIMITED PASS:** historical private KRX storage pair integrity (prior evidence); #413 34-case synthetic regression parity; bounded OpenDART source/candidate text signatures; safety CI only.

**FAIL / FAIL-CLOSED:** #418 archived source drift; Chronology anchor job failure; 27 invalid OHLC rejected. None imply an authorized performance run.

**NOT VERIFIED:** official first-public original-filing 2021/2022 exact consolidated three-month operating-profit period, units, amounts, corrections and public available-at; corp/security historical mapping; KRX official calendar/market status/corporate actions/fills/fees/taxes; chronology 404 body; full CI or PIT backtest speed; Kiwoom replica health and staged patch discrepancy.

**NOT EVALUABLE / NO-GO:** M20 after-cost/tax NetEV, PF, CAGR, MDD, ES95/99, return concentration, temporal robustness and annual risk-adjusted net profit. No new return, M20 economics or model search executed.

**Next evidence path:** independent DART first-original fact/time and corrections attestation; official KRX historical lifecycle, corporate actions, executable prices and all-in costs/taxes; chronology original response receipt; #418 owner synthetic-only repair of archived SHA provenance and strict file/receipt guards, then rerun same pinned 34 cases without using Holdout. Review PIT log cadence after an actual market session, without restarting. Cache only if independent approved source/data/code/Frozen/runtime/approval SHA-256 all match, fail-closed; parallelize independent read-only postprocessing only. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all original cost/risk/promotion gates. Keep `ORDERING=false`; no orders, funds, credentials, workflow writes, merges, deploys, or promotions.
