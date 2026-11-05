# IndexAlert independent profitability/runtime audit — 2026-11-05 16:18 KST

Scope: read-only GitHub PR/Actions and Railway production deployment/log checks. Independent audit documentation only; no backtest, code, workflow, deployment, ordering or trading changes.

## Source refs
- Research branch index-alert-research-v1: PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a`; exact current branch HEAD **NOT VERIFIED** (base SHA is not proof of live branch HEAD).
- Development index-alert-position-regen-fix-v1: PR #420 base SHA `1e6367d2863a86c3470da13d81a955d277eba485`; exact current branch HEAD **NOT VERIFIED**.
- Draft OPEN unmerged PR HEADs: [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) `18c5418d9684d1717df58261ea27f28e514385b2`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate doc `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` on draft branch; prior blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` **not rehashed this run**.

## Independent gate status
| Gate | Verdict | Reason |
| --- | --- | --- |
| OpenDART original filing source bytes and 15 SGML candidate signatures | PASS limited to previously attested byte/row software evidence | Action [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 jobs successful now; source semantic and publication-time attestation not established |
| 2021/2022 original first-three-month consolidated operating profit, correction lineage, public available-at | NOT VERIFIED | Original/correction row adjacency does not prove CFS value/period, initial public timestamp or complete revision lineage |
| Historical issuer/security as-of mapping | NOT VERIFIED | No independently certified point-in-time tradable identity mapping |
| KRX 2017–2022 private weekday pair storage integrity | PASS historical report only, NOT REVERIFIED | Prior 1565/1565 pairs; official trading calendar/status and private-volume re-read missing |
| KRX actual calendar, 90 ambiguous sessions, 27 invalid OHLC, 12003 zero-activity, corporate actions, execution and fees/taxes | NOT VERIFIED | KRX #420/#422/#423 offline controls are not official source admission |
| Offline runtime parity #413 | PASS CI-only | [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), [38466023642](https://github.com/kims34/openpilot-opkr/actions/runs/38466023642) each 6/6 successful jobs |
| Independent single runner #418 | PASS CI-only | [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 successful; historical fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` not recalculated now; 2.9656s / 2.6209s = 1.1315x regression-phase only, not total CI acceleration |
| Chronology anchor | FAIL observed CI | [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296) auto-anchor failed, validation skipped; production anchor NOT VERIFIED |
| NetEV/PF/CAGR/MDD/ES95/ES99/concentration/time stability after costs and taxes | NOT VERIFIED / NOT EVALUABLE | PIT and execution gates not admitted; M20 RUN prohibited |

## Railway production read-only observation
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, running 1/1; KRX worker SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c`, running 0/1 (cron/idle not equivalent to unavailable); both deploy-log queries since 06:00 UTC returned 0 entries.
- Runtime SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, running 1/1; 07:17–07:18 UTC log shows Investing.com USD/KRW HTTP error followed by Yahoo fallback and ETF closed-hours futures proxy. This is display data, not official market PIT.
- Kiwoom real-readonly SUCCESS but replica running 0/crashed 1; push/backend offline warnings, db-query-readonly offline critical. Existing staged patch `e113dacb-6705-4416-9997-dc694539d382` untouched.
- A SUCCESS deployment status and missing recent logs do not establish original KRX PIT, runtime health, or economic profitability.

## Next safe work
Independently retrieve exact research/development branch HEAD via immutable commit/ref source; original provider bytes and precise public timestamps; official private KRX date/status reconciliation with access-safe provenance; archive immutable evidence SHA-256; only synthetic offline policy tests for fail-closed cache key (approved source/data/code/Frozen/runtime/evidence SHA), serial dependent training/capital transition, read-only postprocessing parallelism. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout quarantine, NO_TRADE, ORDERING=false. Do not execute M20 economics or change workflow, other Work branches, deployment, orders or Champion without required independent gates and explicit approvals.
