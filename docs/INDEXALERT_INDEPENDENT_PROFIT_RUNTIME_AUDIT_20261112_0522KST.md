# IndexAlert independent audit — 2026-11-12 05:22 KST

Scope: read-only GitHub and Railway evidence; no trading, source PIT admission, model search, performance replay, CI workflow edits, merges, or deployment.

## Source refs
- Research `index-alert-research-v1` identical to `df474df348f22aa38b1dedaa59fcff66e548b406` (ahead/behind 0/0).
- Development `index-alert-position-regen-fix-v1` identical to `1e6367d2863a86c3470da13d81a955d277eba485` (0/0).
- GitHub PR #412/#413/#414/#418/#420/#422/#423 all OPEN/Draft/unmerged at this check. PR #414 gate blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` read from `refs/pull/414/head`; not present on research base (base 404 is expected). PR #414 metadata reports base_sha `3b8b7830612a6284d7c7a60628cb527cb741627a` and head_sha `18c5418d9684d1717df58261ea27f28e514385b2`; these are PR metadata, not a current branch HEAD.
- Actions 38381997417, 38382214223, 38419111311, 38419649711, 38419439742: independent jobs read attempts all returned ReadTimeout this run; historical 6/6, 6/6, 6/6, 1/1, 2/2 successes remain *previously reported only*, NOT VERIFIED fresh. Fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` not independently recomputed.
- Optimization PR #413/#418: historical offline-only parity evidence, no new performance tests; serial 2.9656s vs concurrent 2.6209s (regression phase ratio 1.1315), total CI/official backtest acceleration NOT VERIFIED.

## Railway production (read-only)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild and runtime: 1/1 running. KRX worker: 0/1 running (SUCCESS deployment is not proof of an active worker). Kiwoom real read-only: 0/1 running, 1/1 crashed (FAIL). Backend/push/db-query-readonly offline; db-query-readonly critical issue 1.
- Latest deployments inspected: Kiwoom real read-only `a77fb922-b679-4d88-92c4-03054ec579cd` 2026-10-29; KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` 2026-10-12; PIT `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`.
- 2026-11-11 19:00–20:25 UTC: PIT/KRX/Kiwoom deploy log entries 0; runtime contains USD/KRW Investing HTTPError followed by Yahoo fallback (20:17:46 UTC), unrelated to official KRX PIT admission.
- Environment has staged patch `e113dacb-6705-4416-9997-dc694539d382`, `changes=[]`; do not apply.

## Gate matrix
| Evidence | Decision |
|---|---|
| KRX 2017–2022 original 1565/1565 private weekday pair storage integrity | PASS **historical scope only**, not rehashed this run |
| 2021/2022 OpenDART original-filing operating income consolidated exact 3-month semantics, corrected lineage, public available-at | NOT VERIFIED |
| Historical corporate/security mapping, official KRX session/status/corporate actions, executable fills, costs and taxes | NOT VERIFIED |
| H5 archive promotion and consumed holdout reuse | FAIL / prohibited |
| M20 PIT and profitability RUN admission | FAIL-CLOSED / NO-GO |
| NetEV/PF/CAGR/MDD/ES95/99, concentration, time robustness after costs/taxes | NOT VERIFIED |
| Offline optimization parity historical CI | prior PASS scope only; fresh CI jobs timed out |
| Total backtest runtime acceleration | NOT VERIFIED |
| Kiwoom read-only replica operational health | FAIL (0 running / 1 crashed) |

## Immutable safety and next actions
- Keep Frozen H5; M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, costs/tax/fill/risk/promotion gates unchanged. ORDERING=false; no orders, funds movement, auth changes or Champion promotion.
- Independently retrieve exact GitHub Actions logs and artifacts when the connector responds, recompute fixed-case digest; require official OpenDART original meaning/available-at and official KRX market-status lineage before any M20 profitability RUN.
- Only isolated synthetic/offline software and policy checks are permissible. Cache requires all independent approved source/data/code/Frozen/runtime/evidence SHA-256 equal, otherwise fail-closed. Only read-only postprocessing parallel; never dependent retraining/capital transitions.
- No merge of PR #413/#414/#418, deployment or workflow edits. Other Work-owned code untouched.
