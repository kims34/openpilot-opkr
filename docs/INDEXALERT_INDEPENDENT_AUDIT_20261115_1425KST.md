# IndexAlert independent audit — 2026-11-15 14:25 KST

Scope: read-only evidence audit; no model search, economic experiment, deployment, merge, trading or permission changes. This is NOT approval of PIT or M20.

## HEADs verified directly via GitHub REST
- research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All Draft, open, unmerged.
- PR #414 gate source blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be, docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md; explicit M20 performance authorization false and NO-GO.

## GitHub Actions checked (REST run and job evidence)
- 38381997417 success 6/6, head 55e7fe2b3fe322e39f817914ff1ed5b589bbe0da
- 38382214223 success 6/6, head 05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56
- 38419111311 success 6/6, head b22e4f39517c2bc38e173e63e8fd52f29a535dad
- 38419439742 success, head 39af5b0043e122bc0e42935d8813759ff6c1a6e7 (SGML row signature is NOT original period/PIT approval)
- 38419649711 success 1/1, head 8f363b8683d34a48754916b34810a5a8bb958896
- 38486028854 FAIL 1/1, head 8f9a473d7751afd85e39f24bfa956d3283f77347, job 115599778959. Prior diagnostic: immutable manifest Git blob SHA-1 expected 108f66714602a1bd3ae42c34dcca7c16e38f460b vs observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. This run independently confirms job FAIL, not the log-level hash discrepancy. Original 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is historical evidence only, NOT independently recomputed this run. Historical serial 2.9656s vs concurrent 2.6209s = regression phase 1.1315x; full CI / official backtest acceleration NOT VERIFIED.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS 1/1; KRX historical 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS 0/1; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS 1/1.
- 2026-11-15 04:15–05:25 UTC: PIT 0 logs, KRX 0 logs, Runtime 61 returned records (limit 60 requested; tool returned 61). At 05:24:42 UTC Investing USD/KRW HTTPError, Yahoo fallback. Not a PIT validation.
- backend, push, db-query-readonly offline; db-query-readonly 1 critical. Pending staged patch e113dacb-6705-4416-9997-dc694539d382 since 2026-10-29, no deployment action taken.

## Gates and disposition
- KRX 1565/1565 weekday raw pairs: historical storage integrity PASS, official calendar/trading-state/corporate actions/execution feasibility NOT VERIFIED. 90-day gap classification and 12003 zero-activity cases remain excluded.
- OpenDART original-filing and public available-at, exact 2021/2022 original consolidated 3-month operating profit and correction lineage, historical corp/security mapping: NOT VERIFIED.
- Transaction costs/tax-adjusted annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness: NOT VERIFIED; M20 economic run NO-GO.
- PR #418 integrated immutable source validation FAIL; earlier synthetic CI PASS is not full performance proof.
- Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, ORDERING=false. No reuse of consumed H5 holdout, no dependent retraining/capital-transition parallelization. Cache only with independently approved matching source/data/code/policy/runtime/evidence SHA-256, fail closed.
- Next: OpenDART owner independently attest original period, correction lineage and public timestamp; KRX owner attest official trading states; PR #418 owner reconcile immutable manifest hash without weakening validation, then offline synthetic rerun in isolated scope. No economic M20 until source gates independently PASS.
