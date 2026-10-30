# IndexAlert independent profitability / isolated runtime audit — 2026-10-30 12:22 KST

## Boundaries and provenance
This is a read-only review of current GitHub refs, draft PR metadata, exact Actions job logs and Railway production status/runtime/HTTP logs. The only requested write is this isolated evidence note. No official original ZIP/private KRX bytes were fetched or rehashed in this run; quoted SHA-256 values are existing Actions receipts, **not a newly independent byte-level attestation**. No M20 economics, model search, Holdout replay, production deployment, broker login, order, funds, credential/permission change, merge or workflow modification.

### Exact current refs (GitHub same-ref comparison)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- KRX owner `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`
- Independent audit branch pre-write: `df887c0d7532d86629f43b37c3dcdc77880cfe0e`
- OPEN/DRAFT/unmerged: PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `78fc75ab3e108943073049e6bba075e4aa16c96b`; #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414's newest commit `78fc75ab` adds only `docs/INDEXALERT_INDEPENDENT_PROFIT_GATE_DELTA_20261030_1143KST_AUTOMATION11.md`; avoid duplicate specialist edits. No gate approval in that note.

## Gate decisions (strict evidence scope)
| Gate | Verdict | Source and limitation |
| --- | --- | --- |
| 2022 original DART ZIP receipt | LIMITED PASS for receipt only | [official Actions #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048): prior SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; 15 SGML label candidates are not a three-month consolidated operating-profit cell. |
| 2021 original DART ZIP receipt | LIMITED PASS for receipt only | [official Actions #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official job `121379096007`: prior SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; 13 candidates, zero strictly 3-month period-bound CFS facts. Do not substitute 2022 filing's 2021 comparator. |
| Original Q3 2021/2022 3-month CFS operating profit, sign/units, amendment vintage, original public available-at and historical corp/security mapping | NOT VERIFIED / source admission FAIL-CLOSED | Label proximity and later normalized API data cannot prove original fact and earliest public clock. No M20 admission. |
| Historical KRX private 2017–2022 storage | LIMITED PASS, stored pair integrity only | Existing Railway receipt 1,565/1,565 weekday original daily/master pairs. 90 unresolved sessions; 12,003 zero-activity cases barred from external tradability admission. |
| Official KRX session/halts/delisting/corporate actions/quotes/fills/fees/tax | NOT VERIFIED | KRX owner [#420 synthetic offline CI #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [#422 #39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), [#423 #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) successful software checks are not official trading-state or execution proof. |
| #413 offline parity | LIMITED PASS | [Actions #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs success; exact-parity job `115670744341`: fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, serial 1.7650s vs parallel longest 2.7079s => 0.652x test-phase speed ratio (parallel slower); end-to-end and actual backtest acceleration NOT VERIFIED. |
| #418 one-runner harness | LIMITED PASS | [Actions #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 job success; not full CI or economic speed. |
| #418 immutable merge-context | FAIL / CACHE FAIL-CLOSED | [Actions #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: `research_v1_runtime_manifest.py` archived Git blob SHA-1 expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`; `exact_wheel_hashes_verified=false`, `os_native_dependency_identity_verified=false`. Do not silently repin; require complete independent source+runtime evidence SHA-256 closure. |
| Policy watchdog | LIMITED PASS only | New [Actions #40988735313](https://github.com/kims34/openpilot-opkr/actions/runs/40988735313), job `123845746566` success: 4 watchdog + 31 governance synthetic tests; explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. |
| M20 after-fee/tax NetEV/PF/CAGR/MDD/ES95/ES99, concentration and time robustness | NOT EVALUABLE; RUN NO-GO | No independently accepted PIT, official executable security-level data, tax/cost/fill ledger or immutable runtime. No fabricated returns or zero substitution. |

## Railway production read-only evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. No newly listed deployments since the previous audit.

- `indexalert-pit-rebuild`: deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1 running/0 crashed. Latest returned deploy log `2026-10-29T14:46:21.992Z` (`2026-10-29 23:46:21 KST`) reports `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`, independent source/chronology/model admission false and orders/funds false. Earlier same-day log counts 27 invalid common-stock OHLC rows among 803. Bounded HTTP stream 100/100 `/anchor/latest` requests returned 404, latest `2026-10-29T17:21:16.310Z` (Oct 30 02:21 KST). 404 does not alone prove absent private anchor file; [Chronology Action #40914179246](https://github.com/kims34/openpilot-opkr/actions/runs/40914179246) failed. Scheduled evening-only collection means lack of morning logs is not independently an outage.
- `indexalert-kiwoom-real-readonly`: deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS label, but runtime replica 0 running / 1 crashed. `2026-10-29T06:22:02.769Z` structured log shows `TOKEN_OR_LOGIN_AUTH`, `DETAIL_CODE=8050`, `ORDERING=DISABLED`, no valid authenticated WS evidence. Direct crash cause is NOT VERIFIED.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS deployment label, but no fresh deploy logs returned; no claim of new official market admission.
- Railway `environment_status` exposes a zero-change pending patch `e113dacb-6705-4416-9997-dc694539d382`, while `describe_environment` says `staged=null`; treat as API-view inconsistency, **not** permission to accept/apply any patch.

## Immutable next gates and non-actions
1. OpenDART owner: original 2021/2022 standalone 3-month CFS operating-profit cell with exact period, amount, unit, sign, first-public available-at, amendment lineage and historical issuer identity, pinned original bytes and independent CI receipt.
2. KRX owner: resolve 90 historical uncertain sessions separately from 27 prospective OHLC invalid rows; official original session/status, corporate actions, security history, executable fill, fees/tax and source PIT.
3. Optimization owner: verify full merged-tree transitive source and wheel/native environment SHA-256 against immutable archive, fail closed on any mismatch. Only read-only independent postprocessing may parallelize; dependent model retraining and capital transitions must stay serial.
4. After source, market, execution, and runtime PASS, independently consider *one* preregistered M20 evaluation. Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, Holdout, Champion/Top3/NO_TRADE, risk/cost/tax/upgrade rules unchanged. Consumed H5 Holdout and posthoc Dynamic outcomes cannot be reused.

**ORDERING=false; no live order, funds movement, auth/account rights, Champion promotion, deployment, auto-merge, PR #413/#414/#418 merge or GitHub workflow edit.**
