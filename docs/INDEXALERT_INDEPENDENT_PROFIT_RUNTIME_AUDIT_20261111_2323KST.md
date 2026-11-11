# IndexAlert independent profitability/runtime audit — 2026-11-11 23:23 KST

Read-only evidence audit; this document is the sole isolated write. No M20 profitability run, official market performance replay, workflow/code edits, deployments, trades, account changes, merge, or Champion promotion.

## GitHub immutable references
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub compare identical 0 ahead/0 behind).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (identical 0/0).
- PR #412, #413, #414, #418, #420, #422, #423: all OPEN, Draft, not merged on this read.
- PR #414 integration gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` read from PR head branch `indexalert-profitability-integration-evidence-20261013`, Git blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Its explicit conclusion remains M20 NO-GO.
- Original offline Actions: [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 6/6 SUCCESS; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 6/6 SUCCESS; adversarial [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 SUCCESS; independent runner [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS; OpenDART [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 SUCCESS. These are job-level PASS only, not economic/source PIT approval. Original 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` was not independently recomputed this run (NOT VERIFIED). PR #418 historical synthetic 28 cases and timing 2.9656s serial versus 2.6209s suite (1.1315x regression phase) are prior claims; end-to-end CI and official backtest speedup NOT VERIFIED.

## Railway IndexAlert production
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c`, Kiwoom readonly `a77fb922-b679-4d88-92c4-03054ec579cd`.
- Live status: PIT and Runtime each running 1/1; KRX worker 0/1 running (cron/worker execution NOT VERIFIED); Kiwoom readonly 0/1 running, 1/1 crashed (runtime FAIL); backend/push/db-query-readonly offline; db-query-readonly critical=1.
- 2026-11-11 12:00–14:25 UTC PIT deploy logs: ten 15-minute-spaced `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE` entries, 12:01–14:16 UTC. Every observed entry has `fresh_alpha_observation_admitted=false`, `funds_movement_authorized=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`. This supports fail-closed operation (PASS), not official KRX correctness (FAIL/blocked). KRX and Kiwoom deploy logs in same interval: zero entries (not evidence of health). Runtime logs at 14:15 UTC show Investing USD/KRW HTTP errors and Yahoo fallback, unrelated to an approved PIT market return.
- Environment has a historical staged patch ID `e113dacb-6705-4416-9997-dc694539d382`, zero changes in current inventory; not applied.

## Evidence gate adjudication
| Gate | Result | Scope / blocking requirement |
|---|---|---|
| KRX 2017–2022 1,565/1,565 weekday raw-pair storage | Historical PASS only | Prior private pair SHA integrity, not a new rehash |
| KRX 90 uncertain sessions, 12,003 zero-activity samples, 27 suspect OHLC, official trading calendars/status/corporate actions, historical execution, costs/taxes | NOT VERIFIED / FAIL-CLOSED | Official chronological evidence and tradability lineage required |
| Original OpenDART first-filed 2021/2022 consolidated 3-month operating profit, period/correction lineage and exact public available-at | NOT VERIFIED / FAIL-CLOSED | Candidate SGML rows/adjacent numeric signatures do not establish meaning or availability |
| Historical corp-to-security mapping, label PIT, purged/CPCV, independent holdout | NOT VERIFIED | Independent source approvals and provenance required |
| H5 archived economic gate | NO-GO | Failed/consumed holdout and Dynamic results cannot be retuned or reused |
| M20 horizon20/purge20, WF504/126/126; net after costs/taxes NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness | NOT VERIFIED; RUN NOT AUTHORIZED | PIT source gates not approved |
| Offline optimization regression job execution | PASS for listed CI jobs | 34-case content SHA rehash and actual full speedup NOT VERIFIED |
| Operational Kiwoom readonly replica | FAIL | 0 running, 1 crashed; no credential or trading intervention permitted |

## Frozen controls and next authorized work
Keep H5 Frozen, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, costs/taxes/NetEV/fill/risk/promotion gates unchanged; ORDERING=false. Cache only when independently approved source, data, code, Frozen policy, runtime and approval-evidence SHA-256 all match, otherwise fail closed. Parallelize only independent read-only post-processing; never dependent retraining or capital transition. Next: request source-owning teams' independent official DART first-filing availability and KRX official market/tradability evidence; separately investigate KRX nonpositive OHLC and Kiwoom replica crash by read-only log/root-cause inspection. No new model search, market performance run, M20 economics, holdout reuse, or deployment until explicit independent gate approval. No PR merge or live actions.
