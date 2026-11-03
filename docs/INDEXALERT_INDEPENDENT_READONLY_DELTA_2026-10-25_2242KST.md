# IndexAlert independent read-only verification — 2026-10-25 22:42 KST

Evidence-only audit. No data/source admission, performance test, market orders, deployment, permission changes, PR merge or Champion promotion. This note supplements (does not duplicate or amend) the 22:21 KST audit `docs/INDEXALERT_INDEPENDENT_READONLY_DELTA_2026-10-25_2221KST.md`.

## Live refs inspected (read-only)
- Research `index-alert-research-v1` HEAD previously pinned and still represented as `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` `1e6367d2863a86c3470da13d81a955d277eba485` (these branch HEAD values come from prior 22:21 audit, **not independently refreshed through a SHA-bearing branch endpoint in this run**).
- Draft integration PR #414 current pre-write HEAD `4d43c1fbbca10ee7edfca0290bf1f4d8f841f60e`, gate file Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Latest 22:21 document Git blob `74308a21f3ed39fdd2fa81ec6b2155d116a9f23b`.
- Draft OpenDART PR #412 `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`; optimization #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; single-runner #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.

## Independently re-read original Actions job logs (new audit granularity, not new source admission)
1. KRX 2022 holiday-candidate offline job `119612335677`, [run #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925): **32/32 synthetic tests passed** at 2026-10-22 02:57 UTC, including exact-day mismatch, 2nd-pass private fingerprint drift, wrong venue (KOSDAQ vs KOSPI), notice first-public timing, after-session publication and later-issued year-end holiday. This CI did **not** mount the real Railway /data or certify any 2022 source-empty days.
2. OpenDART PR #412 financial viewer offline job `120189157379`, [run #39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765): **12/12 synthetic tests passed** at 2026-10-23 01:31 UTC, including mixed original/revised receipts and TOC drift rejection; source code explicitly outputs `m20_feature_pit_admitted: False`, `ordering: DISABLED`. No verified 2022/2021 standalone 3-month CFS operating-income amounts or original public available-at.
3. Read-only watchdog job `121154222723`, [run #40188482673](https://github.com/kims34/openpilot-opkr/actions/runs/40188482673): **31/31 governance tests passed**, log states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Artifact ZIP SHA-256 `a08b8ada6653856bf9ce825e2da1a7d48c1cdbdcc9cd7abf6a256abd07dc1bb2` from job log (not independently downloaded/rehashed in this pass).
4. Railway `list_projects` read-only query returned **non-interactive user-input-required**. No Railway deployment/log read succeeded; no workaround attempted. Actual production `ORDERING` flag is NOT VERIFIED.

## Strict verdict
- Prior 1,565/1,565 KRX stored weekday pairs: historic limited raw-integrity PASS **only**; no fresh original private SHA recomputation in this pass. Actual official exchange calendar, 90 ambiguous sessions, 27 nonpositive-OHLC anomalies, 12,003 zero-activity rows, issuer history, CA, halts, fillability, taxes and costs: **NOT VERIFIED**.
- Original 2022/2021 Q3 connected standalone 3-month operating income, amendment lineage, earliest public timestamp, historical issuer/security mapping: **NOT VERIFIED**. Candidate SGML row counts and original archive byte checks are not semantic PIT.
- Frozen H5 consumed/failed Holdout cannot be reused. M20 horizon20/purge20 and WF504/126/126, PIT/labels/Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE, costs/taxes/risk/promotion criteria unchanged.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after actual fills and costs/tax: **NOT VERIFIED / NOT RUN**. PR #413 synthetic parity limited PASS; PR #418 archived original blob gate FAIL, exact dependency/runtime SHA and actual official backtest acceleration NOT VERIFIED.
- **M20 profitability NO-GO.** Cache reuse only after independently approved source/data/code/Frozen/runtime/authorization evidence SHA-256 all match (fail-closed). Only independent read-only postprocessing may parallelize. `ORDERING=false` required; live value unknown.

Next evidence must come from original first-filed DART public timing/semantic fact proof, official historic KRX market/security/CA/transaction-cost provenance, and authorised read-only Railway logs. No specialist code/workflow modifications or repeat economic experiments.
