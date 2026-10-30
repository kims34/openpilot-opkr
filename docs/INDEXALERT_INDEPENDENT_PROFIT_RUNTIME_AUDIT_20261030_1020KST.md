# IndexAlert independent profitability and isolated runtime audit — 2026-10-30 10:20 KST

> Evidence-only, non-admitting review. No original private financial/market values, broker credentials, account data, orders or financial performance replay. Read-only GitHub Actions/Railway checks; one isolated documentation write. No owner code, workflow, Frozen policy, deployment, merge or Champion changes.

## Independently read HEAD and specialist boundaries

| Source | Git HEAD / finding |
|---|---|
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` |
| KRX delegated `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` |
| OpenDART [Draft #412](https://github.com/kims34/openpilot-opkr/pull/412) | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` |
| Runtime [Draft #413](https://github.com/kims34/openpilot-opkr/pull/413) | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` |
| Total profitability [Draft #414](https://github.com/kims34/openpilot-opkr/pull/414) | `7c8bb2c6470a649eff0f18df62ad373d7a0335b2`; latest 2026-10-30 09:44 KST commit adds **documentation only**, not source admission |
| Flow [Draft #416](https://github.com/kims34/openpilot-opkr/pull/416) | `053de553646fc4765d2616544ca1e8d6bbdde35f` |
| Single runner [Draft #418](https://github.com/kims34/openpilot-opkr/pull/418) | `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; base is #413 isolation branch |
| KRX delegated [Draft #420](https://github.com/kims34/openpilot-opkr/pull/420) | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` |
| KRX calendar [Draft #422](https://github.com/kims34/openpilot-opkr/pull/422) | `c14857620973531013799e44625d43080904fd5f` |
| KRX calendar [Draft #423](https://github.com/kims34/openpilot-opkr/pull/423) | `0e38004363cac9fc4475556b3a1c445de9af407f` |

All eight listed PRs remain open, Draft, unmerged. The separate total-profitability PR #414 latest commit `7c8bb2c` was read and its diff shows only `docs/INDEXALERT_INDEPENDENT_READONLY_AUDIT_2026-10-30_0944KST.md`; no conflicting code or evidence authorization. Own isolated audit branch pre-write HEAD `f3a3b7ce3fe33c10e2d0af081f50bbec53576aef`; prior audit blob `9ce191440c5d95461be72508e52beed277417e10`.

## Actual CI / source evidence (not a profitability run)

- Latest repository Actions list: 4,621 runs at read. [Watchdog #40960712047](https://github.com/kims34/openpilot-opkr/actions/runs/40960712047) created 2026-10-29 21:47:26 UTC / 2026-10-30 06:47:26 KST, SUCCESS; job `123752419542` explicitly states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. PASS is only watchdog policy software.
- [Chronology Anchor #40914179246](https://github.com/kims34/openpilot-opkr/actions/runs/40914179246), job `123589876652`, FAILURE: retry exhausted with HTTP 404 for `/anchor/latest`; validation job skipped. Railway HTTP stream independently confirms **20/20** returned 404 in 2026-10-30 01:43–02:21 KST. Response body/private anchor-file existence not checked, so missing anchor is probable, not proven.
- [OpenDART 2021 official #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official job `121379096007`, SUCCESS; source-only 2021 first-filed ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1 SGML, 1,728 tables, 13 earnings-label candidates, **0 period-bound standalone 3-month CFS facts** per pinned specialist source handoff. Artifact `12625042488` ZIP digest `3fe75e2af23f508d3c518a14e98732a399eb0daeca46cccd7b3191b1e2e4777b`, expiration 2026-11-02 03:13:26 UTC; this is artifact-container digest, **not** original filing ZIP digest. Raw original bytes were not independently rehashed in this run.
- [OpenDART 2022 original #38381866190](https://github.com/kims34/openpilot-opkr/actions/runs/38381866190) specialist original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; [#38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) original/corrected 15 candidate row signatures, not a validated CFS three-month fact. 2021 first-filed source cannot be silently substituted for the 2021 comparative cell inside 2022 first-filed Q3. Exact initial available-at clock and complete amendment lineage remain unproved.
- [PR #413 latest #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): all 6 jobs SUCCESS; exact-parity job `115670744341` fixed **34** cases SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, serial process **1.7650s**, longest parallel **2.7079s**, ratio **0.652x** (slower). Historical #38381997417/#38382214223 6/6 and #38419111311 6/6, 13 adversarial mocks, remain limited offline parity evidence.
- [PR #418 one-runner #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 SUCCESS is only isolated regression-phase evidence. [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` FAIL: `research_v1_runtime_manifest.py` expected blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Prior source inspection also found #418 weaker explicit-false authority and no-follow/identity checks than #413. Candidate merge synthetic proof does not pin all transitive dependencies. **Cache FAIL-CLOSED; merge readiness FAIL; real backtest and full CI acceleration NOT VERIFIED**.
- [KRX #420 latest offline #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) SUCCESS only for offline exceptional-session logic. KRX private 2017–2022 stored weekday pairs 1,565/1,565 with original SHA integrity PASS, **90** source/calendar gap sessions unresolved; 2026 prospective 27 bad OHLC rows are a different period and cannot be merged into historical proof. Official historical trading state, corporate actions, identity, fill and tax/cost model NOT VERIFIED.

## Railway production direct evidence

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Direct service inventory, environment status, source commits and runtime/http logs checked.

- PIT `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, SUCCESS; replica **1 running/0 crashed**. Latest returned deploy event 2026-10-29 14:46:21.992 UTC (23:46:21 KST) shows `COMMON_OHLC_NONPOSITIVE` and fail-closed; 803 common-stock rows, 27 invalid OHLC and zero-volume-value rows, no source/chronology/model admission, `ordering=DISABLED`. No newer returned deploy event is not proof of outage; code schedules collection after 18:30 KST.
- Kiwoom real read-only `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd`, SUCCESS but replicas **0 running/1 crashed**. Structured log 2026-10-29 06:22:02.769 UTC: `TOKEN_OR_LOGIN_AUTH`, code `8050`, token false, WebSocket false, TYPE00 count zero. Crash causality NOT VERIFIED; no authentication/permission changes made.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, SUCCESS, one-shot **0 running/0 crashed**; no recent runtime logs and no private-volume re-access. Railway environment-status reports zero-change staged patch `e113dacb-6705-4416-9997-dc694539d382` with `changes=[]`, while inventory says `staged=null`; do not infer pending configuration changes or commit this patch.

## Independent admission and economics decision

**LIMITED PASS**: historical original-receipt/hash and KRX stored pair integrity (as scoped), offline regression equality/policy safety. **FAIL / FAIL-CLOSED**: #418 archived blob mismatch and cache eligibility, prospective OHLC, chronology endpoint 404, broker auth. **NOT VERIFIED**: original first-public 2021/2022 three-month CFS operating profit, units/period/sign, correction chronology and exact available-at, historical issuer/security mapping, official KRX calendar/tradability/corporate actions/realistic fills, costs and tax, approved full source/data/code/runtime/Frozen/evidence SHA-256 closure. **M20 source/PIT and economic RUN NO-GO**. After-tax NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness **NOT EVALUABLE**, not zero.

Preserve frozen H5/consumed Holdout, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, independent Holdout/Champion/Top3/NO_TRADE, immutable execution/risk/cost/tax/promotion gates. Cache only on full independent SHA-256 and approval match, read-only independent post-processing only. No dependent retraining/capital transition parallelism. `ORDERING=false`; no financial experiments, source-PIT admission, order, funds, rights, Champion promotion, merge, deployment or workflow edits.

**Next gated work:** delegated DART first-public period-bound CFS and available-at lineage; delegated KRX exact authenticated historical session/status/corporate action/issuer-to-security/executable-cost proof; isolated #418 full transitive pinned merge/runtime closure and only synthetic offline safety rechecks. Then and only then independently assess eligibility for a single preregistered M20 evaluation with separate approval. Artifact expiration is a retention concern, not source admission or a reason to bypass gates.
