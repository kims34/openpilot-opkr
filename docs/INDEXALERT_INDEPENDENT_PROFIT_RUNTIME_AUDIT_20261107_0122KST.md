# IndexAlert independent profitability and offline optimization audit — 2026-11-07 01:22 KST

## Scope and isolation
Read-only GitHub/Railway evidence inspection; no model search, market backtest, trading, deployments, merges, workflow edits or permission changes. This audit branch descends from independent audit commit `26c5fda8214fd5524c3dcfa3e63ac8504a38db60`, not the PR #413/#414/#418 branches. Evidence and statuses below are point-in-time, not authorization.

## Verified GitHub PR HEADs (2026-11-07 01:22 KST)
- #412 OPEN/DRAFT: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- #413 OPEN/DRAFT: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- #414 OPEN/DRAFT: `18c5418d9684d1717df58261ea27f28e514385b2`
- #418 OPEN/DRAFT: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- KRX #420 OPEN/DRAFT: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`
- KRX #422 OPEN/DRAFT: `c14857620973531013799e44625d43080904fd5f`
- KRX #423 OPEN/DRAFT: `0e38004363cac9fc4475556b3a1c445de9af407f`
- Research branch `index-alert-research-v1` and development `index-alert-position-regen-fix-v1` both exist, but their current HEAD SHA was not independently resolved this run: **NOT VERIFIED**. Prior known SHAs are not presented as current.
- PR #414 gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched at PR HEAD: blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.

## GitHub Actions job evidence (read-only)
- https://github.com/kims34/openpilot-opkr/actions/runs/38381997417 : 6/6 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38382214223 : 6/6 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419111311 : 6/6 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 : 1/1 success, offline one-runner comparison.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 : 2/2 success, OpenDART offline row tests/candidate diff.
- https://github.com/kims34/openpilot-opkr/actions/runs/41515392296 : auto-anchor FAILURE, validation SKIPPED. **FAIL / downstream NOT VERIFIED**.
- Prior frozen 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, synthetic 28 and adversarial 13 are historical assertions; this run verified job conclusions, not independently recomputed fixture digest or test counts. **Digest replay NOT VERIFIED**.
- Reported serial 2.9656 s / concurrent 2.6209 s = 1.1315x regression-phase ratio only. Full CI and official market backtest speedup **NOT VERIFIED**.

## Railway production evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (deployment status alone does not imply source quality PASS).
- PIT rebuild runtime logs 2026-11-06 23:01:51, 23:16:48, 23:31:57, 23:46:56 KST: each `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`, 803 common-stock rows, 27 nonpositive OHLC rows, 27 zero-volume/value rows, fresh_alpha_observation_admitted=false, live_order_authorized=false. **Source quality FAIL; admission fail-closed PASS**. No later log observed in the queried window.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, no new deploy logs in queried window; official exchange calendar/tradability **NOT VERIFIED**.
- Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS. Backend and push latest deployments FAILED (historical). 
- `get_status` reports stagedChanges=null while pendingWork still includes `patch:e113dacb-6705-4416-9997-dc694539d382` (started 2026-10-29), and `describe_environment` staged=null. Effective patch state **NOT VERIFIED**; no apply attempted.

## Independent admission gates
| Gate | Verdict | Basis |
|---|---|---|
| KRX historical weekday pair storage integrity | historical PASS only | 1565/1565 stored pairs previously recorded; not rehashed this run |
| Prospective OHLC quality | FAIL | 27/803 nonpositive rows in four latest observed logs |
| Runtime fail-closed/no trade | PASS (observed logs) | admission and live order flags false |
| Original filing and public available-at PIT | NOT VERIFIED | 15 SGML candidate rows do not prove original meaning or public timing |
| 2021/2022 initial consolidated 3-month operating profit correction lineage | NOT VERIFIED | independent original/correction period mapping missing |
| Historical entity/security identity and corporate actions | NOT VERIFIED | authoritative PIT mapping not approved |
| Official KRX calendar, trade states, execution feasibility | NOT VERIFIED | private storage not sufficient |
| Fees, taxes, NetEV/PF/CAGR/MDD/ES95/99, concentration, regime robustness | NOT VERIFIED | no admitted official market profitability run |
| Optimization correctness | historical CI PASS, current replay NOT VERIFIED | offline jobs passed; SHA fixture not rehashed this run |
| Whole-pipeline acceleration | NOT VERIFIED | phase-only benchmark cannot establish total speedup |

**M20 NO-GO.** Keep ORDERING=false. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all cost/tax/risk/promotion gates. Never reuse consumed H5 holdout or dynamic results. No M20 economics, market strategy search or new performance experiments before source PIT approval.

## Next independent checks
1. Read failing chronology anchor job diagnostics and isolate root cause without workflow modifications or bypasses.
2. Compare the 27 rejected OHLC cases to authoritative official source/transaction state privately, preserving raw SHA and chronology. Do not publish sensitive raw payloads.
3. Obtain independent first-filing publication timestamp and corrected-period lineage receipts for 2021/2022 3-month consolidated operating income.
4. Confirm branch HEADs and fixed-fixture hashes via independent source API/CI before promoting any optimization evidence.
5. If all original-data/PIT/tradability gates independently pass, seek separate explicit authorization before M20 economics. No merge, deploy, Champion promotion, orders, funds or permissions changes.

No code, workflow, deployment, PR merge or market execution changed in this audit.
