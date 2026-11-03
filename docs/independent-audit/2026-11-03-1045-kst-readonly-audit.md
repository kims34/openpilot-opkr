# Independent read-only audit — 2026-11-03 10:45 KST

Scope: GitHub branch/Actions and Railway metadata/logs only. No M20 execution, source approval, order, deployment, promotion, or PR merge.

- Research `index-alert-research-v1`, development `index-alert-position-regen-fix-v1`, KRX `indexalert-krx-pit-source-audit-20261013` branch existence confirmed. Current branch HEAD SHAs not independently resolved in this pass.
- GitHub PR search returned no matches; PR #414/#412/#420/#422/#423 states therefore not independently reattested this pass.
- Watchdog run 41499149558 readonly-proof-audit job success; chronology anchor run 41515392296 fetch step failed and validation skipped.
- Railway production PIT rebuild deploy logs: FAIL_CLOSED, COMMON_OHLC_NONPOSITIVE, nonpositive OHLC 27, independent source/model/chronology approvals false, manifest SHA null, ORDERING DISABLED.
- Railway Kiwoom REAL readonly deployment SUCCESS but replicas running=0 crashed=1. Pending staged patch exists; not applied.
- Original ZIP byte-level SHA-256 not independently rehashed; PIT, historical mapping, tradeability, costs/slippage/taxes unapproved. NetEV/PF/CAGR/MDD/ES95/99 cannot be defensibly computed. M20 NO-GO; Frozen/Holdout/Champion/Top3 unchanged.
- Do not infer successful operation from Railway UI online state. No execution or operational mutation performed.
