# IndexAlert independent read-only profitability and optimization audit — 2026-10-15 18:25 KST

Status: NON-ADMITTING / DRAFT / NO MERGE / NO DEPLOY / NO ORDERS.
This is an isolated audit note, not a change to the PR #414 integration gate, any delegated specialist code, any workflow, or any Frozen policy.

## Immutable checked refs (GitHub API, 2026-10-15 18:25 KST)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft #414 integration: `8858eaa79ea40784b7d47410d995e96120369605` (this audit note is independent; do not modify its existing integration document).
- Draft #412 OpenDART: `debcd436da3ea3207c00a8afd08015e05c3b7d4b`.
- Draft #420 KRX: `0288a1218269cae239364672ea1abe1545e2b713`.
- Draft #413 runtime: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft #418 single runner: `ecb5662e728365c24e3ae8f43c5683062d88aace`.
- All five PRs were OPEN/DRAFT/UNMERGED when read.

## Source/PIT admission
- OpenDART #38708786002, official source job and offline job SUCCESS, fixed first-original 2022-Q3 slot 5; artifact `11958909398` ZIP SHA-256 `d615ae2888883df0fe1cb7ce093cc4ed4faa84ef8b8ebca39785ef74b83f8aa3`.
- Four original-viewer financial subdocuments: two operating-income row candidates; operating row + exact CFS heading in one subsection; operating row + literal 3-month wording in one subsection; **zero** same-subsection matches with full original 2022-Q3 or comparative 2021-Q3 July–September windows. Cooccurrence does NOT establish a connected statement line item, original edition, or public available-at timestamp.
- Verdict: original 2022/2021 standalone 3-month CFS operating-income values NOT VERIFIED; correction lineage and historical issuer/security PIT NOT VERIFIED; M20 feature admission and profitability RUN BLOCKED. Latest #38709367170 and #38709367140 are offline-only safety jobs, not new original fact proof.
- Railway KRX private 2017–2022 historical worker active deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` at development HEAD `1e6367d...`. Raw weekday-pair integrity 1,565/1,565 PASS; aggregate SHA-256 `e2503a3bc623d4386e5783ec19272916fe6abba9bc191c14040d2c0831c7f01a`. **90** official-calendar/source-gap days unresolved; **12,003** zero-activity OHLC samples quarantined. Separate prospective read-only PIT runtime FAIL_CLOSED on 27 common-stock nonpositive OHLC rows. Official trading state, delisting/halts, corporate actions, fills, fee/tax provenance and as-of tradability NOT VERIFIED.
- KRX #38690425674 offline synthetic CI SUCCESS (not original source admission).
- Net EV, Profit Factor, after-fee/tax CAGR, MDD, ES95/99, concentration and temporal robustness: NOT VERIFIED; do not invent returns or invoke M20 economic runs.

## Independent runtime/CI safety boundary
- #413 HEAD `f003ef62...` and #418 HEAD `ecb5662e...` are different isolated draft contexts.
- #418 candidate proof #38708560319 SUCCESS for 21 directly checked files, archived 34-case identity/outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, but `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`.
- #418 archived-parallel job #38708559866 FAILED CLOSED as designed: `research_v1_runtime_manifest.py` archived blob expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Never silently re-pin old archive.
- #418 one-runner #38708560192 SUCCESS for pinned 34-case outcomes; serial test subprocess 1.9997 s versus parallel 2.0426 s, ratio 0.979x (parallel slower). Full CI wall-time or genuine financial backtest speedup NOT VERIFIED. Candidate source check is not an approved merged source closure; TOCTOU/file identity review remains required.
- Only fail-closed SHA256 manifest/caches with independently approved source, data, code, policy, runtime and approval evidence can be considered. Parallelize independent read-only postprocessing only, not model retraining or capital transitions.

## Railway operating safety
- Production: 10 services, 3 offline (indexalert-push, indexalert-backend, db-query-readonly), 7 online; no staged/pending work.
- Historical KRX and prospective PIT runtime log payloads explicitly state `ordering=DISABLED` and trading/holdout/Champion/funds permissions false. Do not infer every Railway environment variable from a log statement.

## Gate decision and next dependency
- M20 source PIT gate BLOCKED; official tradeability/CA/fill gate BLOCKED; independently computed post-cost/tax economics NOT VERIFIED.
- #413/#418 integration merge BLOCKED; test-phase speed evidence is not production speed evidence.
- Specialist owners should independently prove original CFS cell/period/publication/correction chronology and historical KRX status, then separate reviewers must verify full source dependency closure, fail-closed cache and file identity guards. No overlap with delegated source capture/code branches.
- Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and costs/taxes/execution/risk thresholds unchanged. Consumed Holdout never reused. No workflow changes, merges, deployment, account permissions, money movement, or orders. `ORDERING=false`.

Sources:
- https://github.com/kims34/openpilot-opkr/pull/412
- https://github.com/kims34/openpilot-opkr/pull/413
- https://github.com/kims34/openpilot-opkr/pull/414
- https://github.com/kims34/openpilot-opkr/pull/418
- https://github.com/kims34/openpilot-opkr/pull/420
- https://github.com/kims34/openpilot-opkr/actions/runs/38708786002
- https://github.com/kims34/openpilot-opkr/actions/runs/38708560319
- https://github.com/kims34/openpilot-opkr/actions/runs/38708559866
- https://github.com/kims34/openpilot-opkr/actions/runs/38708560192
- https://github.com/kims34/openpilot-opkr/actions/runs/38690425674
