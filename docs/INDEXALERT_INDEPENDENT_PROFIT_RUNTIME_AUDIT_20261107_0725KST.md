# IndexAlert independent profitability and isolated runtime audit — 2026-11-07 07:25 KST

Scope: read-only GitHub and Railway cross-check. This isolated document is the only write; no workflow, code, data, deployment, PR merge, backtest or order.

## Exact refs (fresh connector reads)
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (compare against branch: identical, ahead/behind 0/0).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (identical, 0/0).
- All OPEN Draft and unmerged: PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.

## CI verified (job-level)
- Original isolated parallel #38381997417 and #38382214223: each 6/6 success. Corrective #38419111311: 6/6 success. Later #38498552499: 6/6 success.
- Single-runner #38419649711: 1/1 success; OpenDART #38419439742: 2/2 success.
- Chronology #41515392296: auto-anchor FAILURE, validation SKIPPED. Earlier job log indicated `/anchor/latest` HTTP 404; root cause not independently fixed/verified.
- Historical synthetic 34-case hash `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 13 adversarial mocks / 28 additional synthetic tests remain prior pinned claims, not newly reproduced full artifact SHA this run. Serial 2.9656s vs concurrent 2.6209s = regression phase 1.1315x only. Overall CI and official backtest acceleration NOT VERIFIED.

## Railway production (fresh environment inventory and deploy logs)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`; staged patch null.
- PIT worker latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX historical `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS. Deploy SUCCESS is not data validation.
- PIT/KRX service logs from 2026-11-06 20:00Z onward: no entries returned, therefore prior 27/803 `COMMON_OHLC_NONPOSITIVE` resolution NOT VERIFIED (previous observed data quality FAIL, fail-closed PASS). Runtime logs through 2026-11-06 22:25Z show Investing.com USDKRW HTTPError and Yahoo fallback; not a trading approval.
- Historical KRX private 1565/1565 weekday pairs: previously pinned storage integrity PASS only; official calendar, zero-activity 12003, trade states, corporate actions and execution NOT VERIFIED.

## Admission verdict
| Control | Verdict | Blocker |
| --- | --- | --- |
| Original-filing OpenDART ZIP/SGML candidate extraction | PASS for historical byte/candidate checks only | 15 candidate rows and matching adjacent numeric signature do not establish original account/period meaning |
| Exact public available-at and first-filed 2021/2022 consolidated three-month operating profit, correction lineage | NOT VERIFIED | No independently approved source-time/semantic/period mapping |
| Historical issuer-security mapping and official KRX trading states/corporate actions/executability | NOT VERIFIED | Official PIT reconciliation and executable price/volume absent |
| PIT rebuild OHLC quality | FAIL (last observed); current resolution NOT VERIFIED | 27/803 nonpositive OHLC previously fail-closed |
| Safety isolation | PASS for previously observed fail-closed controls | No promotion of invalid data; ORDERING=false |
| After-fee/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, time robustness | NOT VERIFIED | Official PIT/market admission blocked, no M20 economics RUN |
| Offline software parity | PASS for listed CI jobs | Not evidence of market alpha or end-to-end speed |
| Chronology evidence route | FAIL | Anchor job failed; validation skipped |

**Decision: M20 NO-GO.** Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, fees, taxes, risk and promotion gates unchanged. Holdout and Dynamic results cannot be retrospectively tuned or reused. Only synthetic offline safety/parity allowed; no market economics, new model search, dependent retraining parallelism, capital-transition parallelism, orders or deployment.

Next: read-only reconcile chronology endpoint route vs deployment commit and 404; inspect original DART publication timestamp and 2021/22 Q3 CFS semantics; reconcile official KRX calendar/status and OHLC at original SHA. Cache only if independent approved source/data/code/Frozen/runtime/approval SHA-256 all match, fail-closed. Parallelize read-only post-processing only. No PR merge or workflow modification.
