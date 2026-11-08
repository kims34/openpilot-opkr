# IndexAlert independent read-only audit — 2026-11-08 10:24 KST

Scope: source/CI/runtime observation only; no PIT admission, trading, backtest, deployment, merge, or policy changes. Isolated audit branch based on prior independent audit commit `2c1109b07c3e63c4ec840ea6440ae694b2516e70`.

## GitHub observed (read-only this run)
- PR #412 OpenDART HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 optimization HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 integration HEAD `18c5418d9684d1717df58261ea27f28e514385b2`; #418 isolated runner HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX PR #420 HEAD `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All seven PRs OPEN, Draft, unmerged at retrieval.
- PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a`, development reference seen in #420 base `1e6367d2863a86c3470da13d81a955d277eba485`. These are PR base SHA observations, **not independent confirmation of current branch tips**. Previous audit reported research tip `df474df348f22aa38b1dedaa59fcff66e548b406`; NOT reverified here.
- Gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched from PR #414 branch, blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. The frozen research branch returns 404 for this draft-only file, which is expected.
- GitHub Actions job status directly queried: #38381997417 6/6 SUCCESS, #38382214223 6/6 SUCCESS, #38419111311 6/6 SUCCESS, #38419649711 1/1 SUCCESS, #38419439742 2/2 SUCCESS. #41515392296 auto-anchor FAILURE, validation SKIPPED. Historical fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 2.9656s/2.6209s timings are prior claims, **not recomputed from artifacts in this run**.

## Railway production observed
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, commit `1e6367d2863a86c3470da13d81a955d277eba485` (2026-10-12).
- PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (2026-10-10); real readonly `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (2026-10-29); runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS (2026-10-05). Deployment SUCCESS does not establish healthy replicas or correctness.
- Backend latest deployment `cce12a43-592a-4910-9b75-89c6b7cdd159` FAILED; push `3ad3102d-ced6-416b-a6da-85c390c9a606` FAILED, both from September.
- Runtime emitted logs through 2026-11-08 01:24 UTC (10:24 KST), including USDKRW Yahoo/ECOS market CLOSED basis. This is **not** proof of IndexAlert PIT or strategy economics. PIT/KRX/real-readonly service logs since 00:00 UTC were empty; no recovery evidence. Replica health and staged environment state not independently checked in this run.

## Independent gates
- **PASS limited scope:** Historical KRX 1565/1565 weekday private raw-pair storage SHA integrity (previous original evidence only); GitHub synthetic/offline CI job completion above.
- **FAIL:** Chronology Anchor auto-anchor job #41515392296; validation skipped.
- **NOT VERIFIED / FAIL-CLOSED:** official original-filing public available-at, 2021/2022 Q3 first three-month consolidated operating profit and correction lineage, historical company/security mapping, official KRX calendars/trading states/corporate actions/executable fills, complete transaction costs and taxes, NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness, and real end-to-end acceleration. Candidate SGML signatures do not prove semantic PIT correctness.
- **M20 NO-GO. ORDERING=false policy unchanged.** No official-market performance run, model search, H5 consumed Holdout reuse, Champion promotion, order, cash movement, credential change, PR merge, deployment or workflow edit.

## Next evidence dependencies
1. Independent first-publication original-filing timestamps and 2021/2022 quarter lineage, with immutable raw SHA and source evidence.
2. Official KRX trading-calendar, suspension/delist, corporate-action, historical mapping and executable-cost proof with source SHA.
3. Resolve failed chronology anchor and reproduce strict evidence fingerprints before any frozen PIT admission; only offline synthetic tests permitted now.
4. Verify real runtime health separately from deployment SUCCESS, and reproduce optimization artifact timing with full runner overhead and approved source bindings. Do not parallelize dependent retraining/capital transitions or relax cache SHA fail-closed gates.
