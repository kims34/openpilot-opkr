# IndexAlert independent profitability and offline optimization audit — 2026-11-10 11:22 KST

Read-only evidence review. M20 PIT/economic RUN NO-GO. No orders, deploy, merges, workflow edits, or Frozen policy modifications.

## GitHub verified
- compare `index-alert-research-v1...index-alert-position-regen-fix-v1`: diverged; development ahead 1148, behind 281; research base SHA `df474df348f22aa38b1dedaa59fcff66e548b406`. Development SHA `1e6367d2863a86c3470da13d81a955d277eba485` is the previously verified SHA and the Railway KRX worker deployment commit; latest development HEAD not independently returned by compare excerpt, so do not elevate it to newly verified.
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): each 6/6 job conclusions success, fetched directly in this audit. [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 success; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 success. Job conclusion PASS does not independently prove source PIT or actual market profitability.
- Historical 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests, and 2.9656s serial vs 2.6209s concurrent (regression-phase 1.1315x) are previously reported, not independently rehashed or rerun today. End-to-end acceleration NOT VERIFIED.
- PR #412/#413/#414/#418 and KRX #420/#422/#423 head/draft status NOT VERIFIED anew in this audit because the available connector lacks a PR read action. Last audited states were open draft; do not represent these as fresh reads. #414 gate file is not present at research ref (fetch error), historically found on dedicated integration branch with blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`, not freshly re-fetched today.
- Prior audit source: [10:19 audit](https://github.com/kims34/openpilot-opkr/blob/e49572b44ab2fc05848d48db77e2305dfcc73ef3/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261110_1019KST.md), blob SHA `699a0a96b9ee99ce55b3ec6c9c0b15e7c8196692`.

## Railway production verified
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Service inventory read; deployment list read.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12), linked development SHA `1e6367d2863a86c3470da13d81a955d277eba485`. Kiwoom readonly deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (2026-10-29); deployment SUCCESS alone is not replica health PASS.
- PIT rebuild `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, KRX worker `003812ee-102b-42b6-bda4-36925885b428`, Kiwoom readonly run `762b4352-b260-4fd2-a43b-95eae68eddec`: deploy logs queried from 2026-11-10 00:00 UTC; each returned 0 entries with service status SUCCESS. No inference of health or anomaly resolution. Previous OHLC anomalies 27/803 NOT VERIFIED resolved. Replica status not newly checked in this audit.

## Independent admission decisions
- OpenDART original/amended SGML 15 candidate rows: historical software evidence only; original-filing semantic identity, precise public available-at/PIT, 2021/2022 consolidated three-month operating profit period and correction lineage NOT VERIFIED.
- KRX 2017–2022 private weekday raw pair 1565/1565 historical storage integrity PASS only; official calendar, trading status, historical issuer/security mapping, corporate actions, execution feasibility, transaction costs and taxes NOT VERIFIED.
- PIT/labels/Purged/CPCV/independent Holdout, net-of-cost-and-tax NetEV/PF/CAGR/MDD/ES95/99, concentration and time robustness NOT VERIFIED. H5 consumed holdout must not be reused. No official market economic tests or model search authorised.
- Frozen H5 and M20 horizon20/purge20 WF504/126/126, Champion/Top3/NO_TRADE, ORDERING=false unchanged. Cache only with independently approved source/data/code/policy/runtime/evidence SHA-256 binding; parallelise only independent read-only postprocessing. No dependent retraining or capital-transition parallelism.

## Next safe steps
Read original OpenDART first-public timestamps and correction lineage, official KRX trade calendar/status/corporate actions and historical security identity, independently signed cost/tax/feasibility provenance; bind exact source/code/policy/runtime evidence SHA before any PIT approval. Continue only isolated synthetic offline safety verification and read-only source audits. No approval to trade, change credentials, promote Champion, merge, deploy or run M20.
