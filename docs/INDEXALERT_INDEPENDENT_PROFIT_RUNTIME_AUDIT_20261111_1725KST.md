# IndexAlert independent profitability/runtime audit — 2026-11-11 17:25 KST

Scope: read-only evidence review, isolated audit document only. No official economic run, deployment, ordering, promotion, workflow edits, or merge.

## Evidence observed this run
- GitHub [PR #414 gate](https://github.com/kims34/openpilot-opkr/blob/refs/pull/414/head/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md) fetched from pull ref; it explicitly states original DART PIT/quarter source fail-closed, H5 archived NO-GO, M20 unapproved, KRX storage-only PASS, offline optimization-only PASS. Exact blob SHA was not returned in this audit record; obtain before promoting any gate.
- GitHub branch README.md fetch at `index-alert-research-v1` and `index-alert-position-regen-fix-v1` returned 404. This does NOT prove branches absent; exact branch HEAD **NOT VERIFIED** this run. Prior recorded research `df474df348f22aa38b1dedaa59fcff66e548b406`, development `1e6367d2863a86c3470da13d81a955d277eba485` are historical references only, not fresh HEAD confirmation.
- Open PR search returned zero results, so individual PR #412/#413/#414/#418/#420/#422/#423 current draft/HEAD metadata **NOT VERIFIED**. PR #414 file did resolve via pull ref.
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 6/6, [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 6/6, [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6, [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1, [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2, [38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499) 6/6: all job conclusions success. Individual 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 mocks, 28 synthetic cases were NOT independently recomputed. Runner phase serial 2.9656s vs concurrent 2.6209s, 1.1315x: historical report only; end-to-end acceleration NOT VERIFIED.
- Railway project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, KRX `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, Kiwoom real-readonly `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (deployment status is not live replica health). PIT/KRX/Kiwoom deployment logs zero entries 06:00–08:30 UTC. Runtime returned 81 entries including USD/KRW Investing HTTP errors and Yahoo fallback at 08:25 UTC; these do not establish official PIT. Backend/push/db-query-readonly offline, db-query-readonly 1 critical issue per environment status. Environment inventory staged=null; environment-status separately reports pending patch with zero changes; did not apply it.
- Previously reported KRX 1,565/1,565 weekday raw pairs storage integrity PASS only on historical evidence; official calendar, trading status, corporate actions, execution feasibility NOT VERIFIED. DART SGML candidate row count 15 historical, original-filing semantics and public available-at NOT VERIFIED.

## Independent verdict
| Gate | Verdict |
|---|---|
| GitHub Actions job success, six selected runs | PASS (jobs only) |
| KRX stored raw pair integrity | PASS (historical scope only) |
| Original DART original-filing/public available-at, 2021/2022 first 3-month consolidated operating profit lineage | NOT VERIFIED |
| Historical corp/security mapping and KRX calendar/status/corporate actions/fills/cost/tax | NOT VERIFIED |
| PIT labels, Purged/CPCV, independent Holdout | NOT VERIFIED |
| NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after costs/tax | NOT VERIFIED |
| Offline runner phase speedup | NOT VERIFIED independently this run; historical phase-only 1.1315x |
| Full CI and official backtest speedup | NOT VERIFIED |
| M20 authorization / Champion promotion / live ordering | NO-GO |

## Frozen constraints and next safe steps
H5 Frozen, M20 horizon20/purge20, WF504/126/126, original PIT, labels, Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE, costs/tax/risk thresholds unchanged. ORDERING=false. H5 consumed/failed Holdout and Dynamic outcomes not independently reusable. Caching fail-closed only if approved source/data/code/frozen policy/runtime/evidence SHA-256 all match; parallelize independent read-only postprocessing only, never dependent retraining/capital transitions. Before PIT source approval, synthetic offline policy/software tests only; no M20 economic run or new market-return/performance/model search.

Next: obtain exact branch and PR HEAD through read-only GitHub refs; independently hash 34-case output from artifacts; have DART/KRX source owners prove official source lineage and available-at, KRX tradability; inspect Railway runtime health without changing deployment. Keep separate Work code untouched. No user approval inferred.