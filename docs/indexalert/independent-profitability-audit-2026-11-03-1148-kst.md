# Independent profitability gate — 2026-11-03 11:48 KST

Scope: isolated documentation only. No backtest, data mutation, trading, deployments, permission changes, PR merge, champion promotion or other workstream overlap.

## Live read-only observations
- Research branch `index-alert-research-v1` HEAD `bba25477b41fcd0a8beca78168abb0009fb5b82c` (includes preceding isolated audit writes); development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`. These SHA values are GitHub compare self-ref responses, not independent raw object rehashes.
- PR #414, #412, #420, #422, #423: open, draft, unmerged (GitHub fetch_pr).
- GitHub Actions: commit-specific pull-request workflow query for research and development HEAD returned no runs. This query does not establish repository-wide latest Actions state. Previously recorded Watchdog success and Chronology Anchor HTTP 404 are NOT independently reconfirmed here.
- Railway project IndexAlert / production: PIT rebuild deployed SUCCESS, one running replica. Most recent returned PIT runtime record: 2026-11-02T14:46:22Z, session 2026-11-02, `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive OHLC rows among 803 common-stock rows; source/model/chronology admissions false, session manifest SHA null, `ordering=DISABLED`.
- Railway Kiwoom REAL readonly: SUCCESS deployment metadata but 0 running / 1 crashed replica; staged environment patch remains uncommitted. Neither patch nor deployment modified.

## Independent admission matrix
- Original OpenDART/KRX bytes and SHA-256: NOT independently rehashed this run; historical logged digests do not equal original byte attestation.
- Point-in-time (first publication timestamp, correction lineage, symbol identity, trading calendar): NOT APPROVED.
- Tradability (price/volume validity, session matching, execution feasibility): NOT APPROVED; 90 historical uncertain sessions and 27 bad OHLC rows remain previously reported, not independently recomputed here.
- Cost, spread, slippage, commissions and tax model: NOT APPROVED for the immutable M20 dataset.
- NetEV, PF, CAGR, MDD, ES95, ES99: NOT ESTIMABLE on admitted evidence; no profitability replay permitted.
- M20 admission: NO-GO. Frozen / Holdout / Champion / Top3 remain unchanged; ORDERING=false and no real orders.

Next admission requires independently reproduced original byte hashes, first-filed chronology and correction lineage, verified KRX sessions/tradability, and pinned executable cost/tax assumptions before a separately authorised single immutable M20 evaluation.
