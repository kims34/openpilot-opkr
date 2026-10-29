# IndexAlert independent profitability and isolated runtime evidence — 2026-10-30 00:21 KST

**Scope and authority:** Read-only GitHub PR/branch/Actions and Railway production metadata/deploy logs; this uniquely named audit document only. No official M20 market/economic run, new model search, consumed H5 Holdout reuse, source PIT admission, live broker login, order, funds movement, permission change, workflow edit, deployment, merge, Frozen change or Champion promotion. All verdicts below are scoped to directly inspected evidence; prior source byte digests are historical receipts, not newly rehashed originals.

## Pinned source refs and coordination

Direct GitHub PR metadata at this review: research base HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development base HEAD `1e6367d2863a86c3470da13d81a955d277eba485`. Research/development branch names independently returned by branch search; exact HEADs cross-checked against PR base_sha. All PRs below are open Draft, not merged:

| PR / role | Exact head_sha |
|---|---|
| [#412 OpenDART](https://github.com/kims34/openpilot-opkr/pull/412) | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` |
| [#413 runtime optimization](https://github.com/kims34/openpilot-opkr/pull/413) | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` |
| [#414 profitability integration](https://github.com/kims34/openpilot-opkr/pull/414) | `ae8d98d0948e2177dc114171ee794a9e137d3163` **before this document write** |
| [#416 investor-flow research](https://github.com/kims34/openpilot-opkr/pull/416) | `053de553646fc4765d2616544ca1e8d6bbdde35f` |
| [#418 single runner](https://github.com/kims34/openpilot-opkr/pull/418) | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` |
| [#420 KRX gap review](https://github.com/kims34/openpilot-opkr/pull/420) | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` |
| [#422 KRX 2021](https://github.com/kims34/openpilot-opkr/pull/422) | `c14857620973531013799e44625d43080904fd5f` |
| [#423 KRX 2022](https://github.com/kims34/openpilot-opkr/pull/423) | `0e38004363cac9fc4475556b3a1c445de9af407f` |

KRX dedicated `indexalert-krx-pit-source-audit-20261013` branch existence verified by branch search; exact current SHA not returned by that API, so its prior `073d2d49...` anchor is **not freshly attested**. [Integration gate](https://github.com/kims34/openpilot-opkr/blob/ae8d98d0948e2177dc114171ee794a9e137d3163/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md) blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Read prior [23:19 independent audit](https://github.com/kims34/openpilot-opkr/blob/3f74e3a67137ca5fe3116f373967e185fa366406/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261029_2319KST.md), blob `0ee13a56a94e318803312b2d29472f73c538ee96`; no duplicate code or specialist change.

## Fresh Railway operational read (production)

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest deployment inventory still identifies `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` (2026-10-29 06:21:36 UTC, SUCCESS, **redeploy of older** commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`, not current development HEAD). Deployment-scoped deploy log at 06:22:02 UTC records `STAGE=TOKEN`, `ERROR_CLASS=TOKEN_OR_LOGIN_AUTH`, `DETAIL_CODE=8050`, `RETURN_CODE=3`, `ACCOUNT_ENDPOINT_OK=false`, `WS_CONNECTED=false`, `WS_LOGIN_OK=false`, `TYPE00_EVENT_COUNT=0`, `GENUINE_LIVE_PROVENANCE_VERIFIED=false`, `ORDERING=DISABLED`, `REAL_ORDERS_AUTHORIZED=false`. This particular smoke run **FAILED broker connection**. The environment health API simultaneously labels service `online` but reports replicas `running=0, crashed=1, total=1`; service config is `python -B smoke.py`, restart `NEVER`. **Persistent service health / exact exit-cause NOT VERIFIED**, and the log does not attest all services' ordering flags. No credentials/values inspected or changed.

`indexalert-pit-rebuild` service-scoped latest returned event at **2026-10-29 14:46:21.992 UTC / 23:46:21 KST**: `status=FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 803 common-stock rows, 27 nonpositive OHLC, 27 zero-volume/value, `session_manifest_sha256=null`, source/chronology/model admission `false`, `ordering=DISABLED`, `real_orders_authorized=false`. **Prospective admission FAIL-CLOSED**; this is not a fresh independent KRX official market-state certification.

KRX historical-worker latest successful deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` from 2026-10-12, commit `1e6367d2863a86c3470da13d81a955d277eba485`. Its historical 1,565/1,565 weekday source pairs with zero invalid stored pairs remain a **prior RAW STORAGE INTEGRITY PASS**, not a new byte rehash, nor an official trading-session/fillability PASS. Production `describe_environment` and `get_staged_changes` both report **staged=null and no resource changes**; `environment_status` separately shows empty pendingWork patch `e113dacb-6705-4416-9997-dc694539d382`. Do not interpret this empty pending item as an applied config mutation or approve a deploy.

## GitHub Actions and optimization isolation

- [#38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): directly re-read job lists, **6/6 SUCCESS** each. Historical pinned 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` limited offline parity PASS (digest from original job logs / prior audit; no fresh artifact ZIP rehash).
- [#38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS; original log shows 34 pinned synthetic parity cases, serial 2.9656s vs parallel 2.6209s for a **single regression phase** (1.1315x); whole-CI and official-backtest speedup NOT VERIFIED. [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 SUCCESS; 2.3911s vs 2.0755s (1.1521x), again phase-only.
- [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395` **FAIL**; re-read exact `SourceDriftError` expected `research_v1_runtime_manifest.py` Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Direct `fetch_file` at PR #418 and PR #413 refs reproduced both blob SHAs. #413 checks explicit `False` authority flags and uses no-follow safe-path protections, whereas #418 original's checks are weaker. **Security/authority semantics differ**; repinning only SHA is prohibited. **Cache FAIL-CLOSED** until independent source/data/code/Frozen/runtime/authority SHA-256 and transitive dependencies all match. [#39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) 1/1 limited candidate source audit SUCCESS is not a full provenance admission.
- [OpenDART #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 SUCCESS; 15 original/corrected SGML operating-row candidate signatures only, **not** 2021/2022 exact standalone 3-month consolidated operating-income facts, period, correction lineage, original public available-at. [#40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) 1/1 offline viewer CI SUCCESS; not official source PIT.
- [KRX #39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545) 1/1 metadata-only no-network guard SUCCESS; no official calendar/trading status approval. [Watchdog #40853112299](https://github.com/kims34/openpilot-opkr/actions/runs/40853112299) 1/1 SUCCESS; original log states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`.

## Decision table (source-limited)

| Gate | Verdict |
|---|---|
| Historical KRX private stored-pair SHA integrity | **PASS (historical, storage only)** |
| Offline pinned 34-case regression parity / limited CI | **PASS (synthetic only)** |
| PR #418 merged-source identity and authority semantics | **FAIL; cache FAIL-CLOSED** |
| 2026-10-29 Kiwoom read-only broker token/WS/TYPE00 smoke | **FAIL in observed run** |
| All-service live ordering configuration and replica exit cause | **NOT VERIFIED** |
| Prospective 803-row OHLC market admission | **FAIL-CLOSED** |
| 2021/2022 first-original three-month CFS operating income, available-at, corrections and issuer/security PIT mapping | **NOT VERIFIED** |
| Official KRX session/status, corporate actions, historical fill/fees/tax | **NOT VERIFIED** |
| Full CI / official economic backtest acceleration | **NOT VERIFIED** |
| M20 PIT and economic run | **NO-GO / NOT AUTHORIZED** |
| After-cost/tax NetEV, PF, CAGR, MDD, ES95/99, date concentration and temporal robustness | **NOT EVALUABLE, not zero** |

**Next evidence, without unauthorized experiments:** OpenDART owner attests exact original filing and first-public time/lineage; KRX owner independently validates official historical sessions, issuer-security mapping, corporate actions and fillability; runtime owner reconciles both blob identity and authority semantics plus transitive lock; service owner read-only correlates 8050 event to intended one-shot process/exit without touching credentials. No performance tests until independent PIT PASS. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, independent consumed Holdout, Champion/Top3/NO_TRADE, cost/tax/risk gates and `ORDERING=false`. No merge, workflow edit, deployment, orders, funds, permission change or Champion promotion.
