# IndexAlert independent profitability / isolated runtime audit — 2026-11-03 01:24 KST

**Authority boundary:** Read-only verification of GitHub and Railway, plus this independent audit document only. No official M20 return generation, model exploration, data-source approval, workflow edit, PR merge, deployment, trading, funding, permission changes, or Champion promotion. The separate specialist branches and code remain untouched.

## Exact source and GitHub heads

Repository: `kims34/openpilot-opkr`. Research `index-alert-research-v1` is the observed PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` is the observed PR #420 base SHA `1e6367d2863a86c3470da13d81a955d277eba485`. These are PR base observations, **not** a separately proven current branch-ref lookup. All below PRs were queried as OPEN, DRAFT, UNMERGED:

- [OpenDART #412](https://github.com/kims34/openpilot-opkr/pull/412) head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- [Optimization #413](https://github.com/kims34/openpilot-opkr/pull/413) head `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- [Integration #414](https://github.com/kims34/openpilot-opkr/pull/414) **pre-write** head `4945cfc13b1561087d0ae8ecc2c7ed186d248583`
- [Flow #416](https://github.com/kims34/openpilot-opkr/pull/416) head `053de553646fc4765d2616544ca1e8d6bbdde35f`
- [Single runner #418](https://github.com/kims34/openpilot-opkr/pull/418) head `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- [KRX #420](https://github.com/kims34/openpilot-opkr/pull/420) head `fab3cbbd63a951a4e081f9e7f08c1391ca308581`
- [KRX 2021 #422](https://github.com/kims34/openpilot-opkr/pull/422) head `c14857620973531013799e44625d43080904fd5f`
- [KRX 2022 #423](https://github.com/kims34/openpilot-opkr/pull/423) head `0e38004363cac9fc4475556b3a1c445de9af407f`

Primary frozen integration document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` was fetched on PR #414 with blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` unchanged.

## Directly checked GitHub Actions jobs and source limitations

- OpenDART HEAD-linked [#40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) and [#40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687): **1/1 + 1/1 SUCCESS**, strict first-edition viewer/TOC parser and edition-selector **offline synthetic only**. The former job log shows 13 named no-network safety tests passing and explicit `m20_feature_pit_admitted=False`, `m20_performance_run_authorized=False`, `ordering=DISABLED`. They do **not** establish the 2021/2022 initial 3-month consolidated operating-profit value, period semantics, original/correction lineage, public available-at timestamp or issuer/security PIT.
- Historical OpenDART [#38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): prior evidence of original/corrected SGML candidate operating rows (15) and adjacent numeric signatures matching. Treat as **limited row-shape PASS**, not a new independent economic/semantic PASS.
- Optimization PR #413 HEAD-linked [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): **6/6 SUCCESS**. Actual exact-parity job `115670744341` log: **34** pinned case names/outcomes, SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, serial regression 1.7650 s, longest parallel suite 2.7079 s, test-phase speed ratio **0.652** (parallel slower). `actual_backtest_speedup_measured=false` and `ci_end_to_end_speedup_measured=false`.
- PR #418 HEAD-linked [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478): **1/1 FAIL** before regression cases, verified job log `117628139395` reports `SourceDriftError`: `research_v1_runtime_manifest.py` archived expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. **FAIL-CLOSED; do not silently re-pin/waive**.
- Separate [#39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) candidate merge *proof-only* **1/1 SUCCESS**, job log `117628139749` says `candidate_approved_for_merge=false`, `original_archived_manifest_replayed_without_change=false`, `all_transitive_imports_pinned=false`, with 22 checked files and unchanged 34-case digest. This does **not** supersede the failed archived gate. [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) single-runner **1/1 SUCCESS**, test-phase only, not whole CI/official financial backtest acceleration.
- KRX #420 [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), #422 [#39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), #423 [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925): each checked as **1/1 SUCCESS**, but **synthetic/offline no-provider** checks, not official historical exchange calendar/market state/real fill admission.

## Railway production, direct read-only checks

Project `IndexAlert` `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `production` `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.

- PIT service `indexalert-pit-rebuild`, deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (created 2026-10-10T10:28:46Z), live source pinned `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`. Latest returned prospective runtime log is **2026-11-02T14:46:22.403874064Z (23:46:22 KST)**, with 27/803 common-stock OHLC invalid, failure session 2026-09-28, `status=FAIL_CLOSED`, `session_manifest_sha256=null`, independent source/chronology/model approvals false, `ordering=DISABLED`, and no order/fund/permission authority. Query from 2026-11-02T15:00Z returned **0 log entries**; this is an observation gap, **not** proof of outage or of repair. Environment health shows PIT **1/1 running**.
- Historical KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, source commit `1e6367d2863a86c3470da13d81a955d277eba485`. Prior official-private raw audit: **1,565/1,565 weekday source pairs storage SHA limited PASS**, 90 calendar/source gaps, 12,003 zero-activity OHLC samples, 27 prospective OHLC vetoes. Current worker log query returned **0 entries**; no new private SHA proof or calendar admission is claimed.
- Runtime `indexalert-runtime` latest SUCCESS deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`. Recent HTTP stream has successful 200s for status/history endpoints (last returned 2026-11-02T13:57:30Z), but no post-15:00Z HTTP entries and no response body/private anchor file evidence. Earlier `/anchor/latest` 404 root cause **NOT VERIFIED**.
- Railway `get_status` and `environment_status` report pending patch `e113dacb-6705-4416-9997-dc694539d382` with empty change list, while `get_staged_changes` and `describe_environment` report `staged=null` and 0 staged changes. **Cross-view telemetry discrepancy NOT VERIFIED**; no accept/deploy.
- `indexalert-kiwoom-real-readonly` reported `online` while replica count is **0 running / 1 crashed** in health view; unresolved status inconsistency. PIT and runtime each 1/1 running. No restart or configuration mutation.

## Independent decision matrix

| Requirement | Current decision |
|---|---|
| Official original OpenDART ZIP/SGML row candidate integrity | **Limited PASS** on previously verified bounded evidence |
| Exact original 2021/2022 consolidated first-3-month operating income, period, correction lineage, public available-at, historical issuer/security mapping | **NOT VERIFIED** |
| Historical KRX 2017–2022 original private pair storage SHA | **Limited PASS** from prior 1,565/1,565 audit, not freshly re-run |
| Official market calendar, historical trading state, corporate actions, fills, fees, taxes | **NOT VERIFIED** |
| PR #413 34-case offline parity | **Limited PASS**, test-phase 0.652x and real end-to-end acceleration **NOT VERIFIED** |
| PR #418 immutable archived original source | **FAIL-CLOSED** on SHA mismatch; candidate merge proof not admission |
| H5 failed/consumed Holdout or dynamic post-hoc reuse | **FORBIDDEN** |
| M20 after-tax NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness and annual risk-adjusted net return | **NOT EVALUABLE / NO-GO** |
| M20 PIT/economic RUN, Holdout, Champion promotion, Tiny Live, live orders | **NOT AUTHORIZED** |

**Next:** require independently verified original DART financial-period/publication/correction evidence and historical issuer mapping; official KRX calendar/tradability/corporate-action/fill-cost-tax evidence; resolve immutable archived #418 source identity with independent original baseline rather than a new convenience digest; reconcile Railway log freshness/anchor 404 and status telemetry through read-only evidence. Only after independent source/PIT PASS can a separately authorized single frozen M20 evaluation be considered.

Frozen H5 and M20 horizon20/purge20, WF504/126/126, Purged/CPCV, Top3/NO_TRADE, sealed Holdout, fixed cost/tax/risk/promotion gates remain untouched. Cache requires **all** independently approved source/data/code/Frozen/runtime/evidence SHA-256 and fail-closed; parallelism only for independent read-only postprocessing, not dependent refits/capital transitions. `ORDERING=false`; no merge/deploy/trade/funds/permissions/promotion.
