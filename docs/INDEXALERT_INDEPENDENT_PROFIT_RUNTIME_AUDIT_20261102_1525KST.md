# IndexAlert independent profitability and isolated backtest-runtime audit — 2026-11-02 15:25 KST

**Audit class:** read-only evidence reconciliation and isolated documentation only. **Final decision:** M20 PIT **NOT VERIFIED**, economic run **NOT AUTHORIZED**, after-fee/tax risk-adjusted profitability **NOT EVALUABLE / NO-GO**. No actual financial-return test, model search, Holdout reuse, broker/order, deployment, workflow edit or merge.

## 1. Fresh source identities and other owners' scope

Direct GitHub branch and Draft PR metadata resolution (2026-11-02 15:25 KST):

| Source | Exact HEAD | Evidence |
|---|---|---|
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | GitHub branches API |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | GitHub branches API |
| KRX specialist `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | GitHub branches API |
| [Draft #412](https://github.com/kims34/openpilot-opkr/pull/412) original DART | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | open/draft, no merge |
| [Draft #413](https://github.com/kims34/openpilot-opkr/pull/413) parallel offline | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | open/draft, no merge |
| [Draft #414](https://github.com/kims34/openpilot-opkr/pull/414) integration owner | `bb5bf842675a76829b2140fdf0ebad96a669faba` | 2026-11-02 14:43 KST update; **not modified here** |
| [Draft #418](https://github.com/kims34/openpilot-opkr/pull/418) one-runner | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | base #413; open/draft |
| [Draft #416](https://github.com/kims34/openpilot-opkr/pull/416) investor flow | `053de553646fc4765d2616544ca1e8d6bbdde35f` | separate owner |
| [KRX #420](https://github.com/kims34/openpilot-opkr/pull/420), [#422](https://github.com/kims34/openpilot-opkr/pull/422), [#423](https://github.com/kims34/openpilot-opkr/pull/423) | `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, `c14857620973531013799e44625d43080904fd5f`, `0e38004363cac9fc4475556b3a1c445de9af407f` | all open/draft |

Core [integration gate](https://github.com/kims34/openpilot-opkr/blob/indexalert-profitability-integration-evidence-20261013/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md) blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` unchanged. The #414 owner's newly committed 14:42 KST note `docs/INDEXALERT_INDEPENDENT_PROFIT_GATE_DELTA_20261102_1442KST_AUTOMATION11.md` (blob `a6f114c49a261205229a668e18493eee5e9d2e4c`) independently preserves NO-GO. No overlapping edits to its documents or other specialists' code.

## 2. GitHub Actions: exact fresh branch-wide run lookup, not just pinned historical links

- [Latest repository-wide listed run #41368406818](https://github.com/kims34/openpilot-opkr/actions/runs/41368406818), 2026-11-02 00:40Z, HEAD `f17283d9a5f0427c3d5b8a865d39455f92ee2f1d`, one job `125033414398` **SUCCESS**. Decoded log: 4 watchdog synthetic tests and 31 governance synthetic tests PASS; explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is **software/governance**, not market or M20 economic PASS. Repository runs collection (30 most recent) showed no newer run at read time.
- [OpenDART #412 branch](https://github.com/kims34/openpilot-opkr/pull/412) most recent runs `40263193758`, `40263181687`, `40263176872` all SUCCESS at HEAD `bf3d9514...` (2026-10-26), but viewer/edition **offline safety** only. [Earlier official Action #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 15 candidate SGML operating-profit row signatures, not original exact CFS three-month facts or first public timestamp. Previously CI-reported ZIP SHA-256: 2022 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 2021 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; **not independently rehashed original bytes this pass**.
- [#413 latest run #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773), HEAD `f003ef...`, six jobs **SUCCESS**. Fixed 34-case identity/result SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` parity limited PASS. Historical serial 1.7650 s vs parallel 2.7079 s = 0.652x speed (regression); no whole-CI/official backtest speedup proof.
- [#418 same HEAD concurrent CI](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) has **different conclusions by workflow**: pinned-parallel archived run `39111405478` job `117628139395` **FAIL**; candidate merge source audit `39111405494` **SUCCESS**; one-runner wall-time probe `39111405562` **SUCCESS**. Decoded failing job shows `SourceDriftError` for `research_v1_runtime_manifest.py`: archived expected blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, merged candidate observed `e0055c66c59398fd4a1158077446d886b54c4e37`. **FAIL-CLOSED for adoption**, even though synthetic isolated runner succeeds. Do not repin hash without independent source/security and archive authority.
- KRX specialist branch latest `39721289545` source-PIT handoff synthetic SUCCESS (2026-10-22, HEAD `1611b250...`), #420 `39714369438` SUCCESS (offline exception review), #422 `39001836000` SUCCESS (offline 2021 calendar candidate), #423 `39714207925` SUCCESS (offline 2022 holiday candidate). These do not establish authenticated official historic session/security tradability or a complete PIT panel.
- [Chronology #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151), job `124184971844` **FAIL**, validation skipped; 20 attempted requests for `/anchor/latest` ended HTTP 404. No public-available-at attestation.

## 3. Railway production direct read-only evidence

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. The latest `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` reports SUCCESS and is pinned to source `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`. The exact deployed [HTTP source](https://github.com/kims34/openpilot-opkr/blob/e57054ecdb3e734ced3c9a981b887d9b5fc60f97/research_v1_prospective_http_runtime.py) blob SHA-1 `026710d8d48b3db666832e199fd3bca95a113d3b` implements `/anchor/latest` (lines 414–440), with 404 `NO_ANCHOR` when no matching valid candidate file is found; unexpected read/validation errors 503. Route presence is **source-level PASS**; live 404 response JSON body, private file inventory and precise historical causal linkage are **NOT VERIFIED**.

Railway HTTP proxy log independently records **20/20 GET `/anchor/latest` 404** between 2026-10-30 16:35:22Z and 17:13:23Z (no proxy upstream errors). This is not a missing deployed route based on the source. However, 404 status alone does not attest body or absence of any private anchor file. A read-only public endpoint body probe from this audit environment was unavailable (DNS/access failure), so **no fresh body proof** is claimed.

PIT runtime last returned deploy log **2026-11-01 14:46:22.425Z = 23:46:22 KST**: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock OHLC invalid, `session_manifest_sha256=null`, `fresh_alpha_observation_admitted=false`, all independent admissions false, `ordering=DISABLED`, `real_orders_authorized=false`. Approximately **15h39m observation gap** at 15:25 KST 11/02; a service deployment marked SUCCESS is not proof of current data ingestion, nor is a log gap proof of downtime. KRX dedicated worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS pinned to `1e6367d...` (read-only historical audit), prior 1,565/1,565 weekday raw daily/master stored pairs SHA integrity PASS **only**. Separate index/FX `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, returned fresh 2026-11-02 06:25Z logs, **not** M20/PIT proof.

## 4. Independent admission matrix

| Gate | Decision | Unresolved independent proof |
|---|---|---|
| GitHub original source/CI identities | **PASS (bounded SHA/CI identity only)** | actual private official original bytes not independently rehashed now |
| OpenDART first original 2021/2022 Q3 consolidated 3-month operating income, correction lineage, exact public available-at | **NOT VERIFIED / FAIL-CLOSED** | exact CFS facts, period, first-filed version, publication instant, corp/security historic mapping |
| KRX 2017–2022 stored 1,565 pairs | **PASS (stored-pair integrity only)** | exchange official calendar, 90 uncertain days, 12,003 zero-activity samples, security status, actions and 27 OHLC vetoes |
| KRX tradability, historic corporate actions, fills, costs, taxes | **NOT VERIFIED** | official source-vintage identity, executable quote/lot/capacity and cost/tax proof |
| #413 fixed synthetic 34-case parity | **PASS (bounded)** | parallel speed regression; official CI/backtest acceleration unverified |
| #418 archived merged-source admissibility | **FAIL-CLOSED** | immutable manifest mismatch; synthetic runner success does not override |
| Chronology live 404/anchor | **FAIL to obtain anchor; root cause NOT VERIFIED** | live JSON body, private hash-only file inventory, exact source failure linkage |
| M20 after-fee/tax NetEV/PF/CAGR/MDD/ES95/ES99, date concentration/regime robustness | **NOT EVALUABLE / NO-GO** | all PIT/tradability/cost gates must pass before one preregistered run |

**Frozen boundary:** H5 consumed/failed Holdout cannot be recycled. M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE, execution/risk/cost/tax/promotion policy unchanged. Cache fail-closed unless approved original/data/calculation code/Frozen/runtime/approval evidence SHA-256 all match; only independent read-only postprocessing may be parallel, no dependent retraining or capital transition concurrency. `ORDERING=false` and all live orders, money transfers, credential/account permission changes, Champion promotion, PR merges and deployment remain forbidden absent separate explicit authorization.

**Next independent read-only gate:** owner-authorized hash-only inventory of private anchor/manifest receipts plus exact live 404 body, tie observed failure session to KRX original source receipt; OpenDART owner proves original consolidated Q3 values and public available-at; KRX owner proves official vintage market state/actions/fillability; optimizer owner reconciles #418 archived manifest without weakening validation. No M20 economics, new performance experiments or operational changes in the meantime.
