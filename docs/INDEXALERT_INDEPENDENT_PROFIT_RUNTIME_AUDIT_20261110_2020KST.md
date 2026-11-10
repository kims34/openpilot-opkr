# IndexAlert independent audit — 2026-11-10 20:20 KST

Read-only audit of GitHub and Railway; no source, strategy, workflow, deployment, trade or permission change. This is an isolated documentation record. Frozen policy, H5/M20 horizon20 purge20, WF504/126/126, Holdout, Champion/Top3/NO_TRADE unchanged; M20 NO-GO; ORDERING must remain false.

## Source refs and evidence
- Research base verified as PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a`; development PR #420 base SHA `1e6367d2863a86c3470da13d81a955d277eba485`. These are PR base SHA snapshots, not independent live branch-tip attestations.
- OPEN/Draft/unmerged PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Original offline Actions 38381997417 and 38382214223: 6/6 SUCCESS each; corrective 38419111311 6/6 SUCCESS; single-runner 38419649711 1/1 SUCCESS; OpenDART 38419439742 2/2 SUCCESS. Historical fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` reported previously, not recomputed this run. Synthetic regression-phase ratio 1.1315x only; full CI/official backtest acceleration NOT VERIFIED.
- PR #414 gate file does not exist on research base (404 expected); source gate must be read from PR branch. Previously reported gate blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` not independently rehashed in this run.

## Railway production
- IndexAlert production status: PIT deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; Kiwoom real readonly `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS; actual replica counts null, so health NOT VERIFIED. Backend/Push latest deployments FAILED. No deploy performed.
- PIT deploy logs 2026-11-10 18:30–20:15 KST at 15-minute intervals show repeated `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, `FAIL_CLOSED`, `ordering=DISABLED`, independent source/chronology/model admission false, live-order authorization false. Session manifest SHA null; this is runtime log evidence, not independent variable attestation.
- KRX and Kiwoom read-only deploy logs since 18:00 KST returned zero entries; absence is not PASS. Production status stagedChanges=null while pendingWork contains an empty staged patch from 2026-10-29; not applied.

## Gate decisions
| Domain | Decision | Scope |
| --- | --- | --- |
| Selected offline CI jobs | PASS | Software-only completed job outcomes; immutable SHA not recomputed |
| Historical KRX 1565/1565 stored pairs | PASS (prior evidence only) | Private storage integrity, not official session/tradability |
| PIT prospective feed | FAIL_CLOSED | 27 nonpositive OHLC among 803; independent admissions false |
| Original OpenDART first-filing, exact publication PIT, 2021/2022 initial consolidated 3-month operating-income lineage | NOT VERIFIED | Candidate rows do not bind semantic fact and vintage |
| Historical issuer/security mapping, KRX official sessions, corporate actions, stock-day status and executable fills | NOT VERIFIED | 90 uncertain sessions and trade feasibility remain unresolved |
| NetEV/PF/CAGR/MDD/ES95/99, tax/cost-adjusted annual risk-adjusted net profitability, concentration, temporal robustness | NOT VERIFIED | No approved original PIT panel or executable cost ledger; economic RUN forbidden |
| Runtime end-to-end speed | NOT VERIFIED | Only synthetic regression-phase ratio recorded |

Next: OpenDART owner independently bind official original 2021/2022 CFS 3-month cell, available-at and correction chain; KRX owner reconcile official calendar, 90 dates, 27 OHLC and security-day tradability; optimization owner verify full transitive archive/runtime closure and strict fail-closed SHA keys in isolated offline-only tests. No duplicated specialist work. Do not replay consumed H5/Holdout, run M20, merge PRs, deploy, change credentials, promote Champion or place orders.
