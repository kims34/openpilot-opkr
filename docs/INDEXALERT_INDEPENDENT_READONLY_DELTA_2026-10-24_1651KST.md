# IndexAlert independent read-only delta — 2026-10-24 16:51 KST

Scope: append-only evidence delta relative to [16:18 KST full gate](INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-24_1618KST.md). Read-only verification of refs, Actions jobs, log output, artifact metadata. No private original download or independent source-byte SHA-256; GitHub blob SHA-1 and Actions artifact SHA-256 are distinct, and matching Actions log/metadata does not prove source PIT.

## Live refs (connector read, not inferred from old notes)
- Research branch HEAD: `3b8b7830612a6284d7c7a60628cb527cb741627a` (direct branch-ref commit resolution).
- Development branch HEAD: `1e6367d2863a86c3470da13d81a955d277eba485` (direct branch-ref commit resolution).
- Draft #414 HEAD: `b7d411d217af1c83dbcd66ff44fbcff6e8836b16`, integration-gate Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (unchanged).
- Draft #412 HEAD `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All remain open Draft. No merge attempted.

## Newly cross-checked bounded evidence
- [Read-only watchdog Actions #40067673639](https://github.com/kims34/openpilot-opkr/actions/runs/40067673639) job `120794227889` SUCCESS; actual job log at `2026-10-24T05:48:18Z`: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded artifact `12550355815` metadata digest `sha256:99fea0e7137c5f2b4cd24f520d3beab0b35a5e075cec71c2dcd1c482ed00e8d2` matches the job log's uploaded ZIP digest. **PASS only for log-to-artifact metadata consistency and offline watchdog; NOT an independent PIT, Railway configuration, or source-byte proof.**
- [OpenDART #39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351) artifact `12471308613` SHA-256 `02e829d3a5fdde8754f649431363c74221eb192b78b8237c911f74b54325820c` remains a bounded 2026-10-22 official-index count receipt, not original 2022/2021 three-month consolidated profit or precise public available-at.
- [Chronology #39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) anchor job `120476944660` FAIL: HTTP 404 at `/anchor/latest`; validation job skipped. Chronology/PIT admission remains FAIL-CLOSED.
- [KRX #39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545) offline safety job `119635081965` SUCCESS; this is not private exact-day, official tradability, corporate action or fill validation.
- [Runtime #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archive-pinned guard job `117628139395` FAIL; [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) isolated one-runner job SUCCESS, artifact `12130627489` SHA-256 `0a07b46bdc93081b1783a89c1b5b3a1128d06cb86941028c936035c0c6713131`. Do not repin archived SHA, merge #418, or infer full CI/backtest speedup.

## Admission decision
- **PASS limited:** original OpenDART and KRX stored-byte receipt evidence previously recorded; current offline CI safety and bounded Actions artifact metadata consistency.
- **FAIL / FAIL-CLOSED:** chronology anchor fetch HTTP 404; #418 archived-source pin mismatch.
- **NOT VERIFIED:** original 2022/2021 three-month CFS operating profit semantics and earliest public time, complete correction lineage, historical issuer/security PIT mapping, KRX official session/halts/delist/corporate actions/real fills, independently pinned cost/tax, after-tax NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness.
- Railway `list_projects({})` still returns `User input required but current turn is running in a non-interactive mode.`; current production deployments, logs and actual ORDERING setting are **NOT VERIFIED**. No credential/rights change attempted.

**NO-GO:** M20 performance run, Holdout access, Champion promotion, live orders, funding, deployment and PR merge remain unauthorized. Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/Purged/CPCV; Top3/NO_TRADE; fixed execution/cost/tax/risk gates unchanged. `ORDERING=false` remains a required invariant, not a freshly observed Railway setting. Do not modify delegated work, workflows or cache approval pins. Next: source owners provide independently timestamped original DART CFS facts and official KRX security-day tradability/corporate-action receipts; Railway operational read requires an interactive authenticated session.
