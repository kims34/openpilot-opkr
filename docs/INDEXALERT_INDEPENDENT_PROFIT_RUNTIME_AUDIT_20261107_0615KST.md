# IndexAlert independent profit/runtime audit — 2026-11-07 06:15 KST

Scope: read-only GitHub/Railway verification; documentation-only isolated branch. No source admission, economic run, market fetch, deployment, merge, orders, credential/permission change, Champion promotion, or workflow edits.

## Exact source refs
- Research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub branch REST read).
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branch REST read).
- Draft PR #414 HEAD `18c5418d9684d1717df58261ea27f28e514385b2`; integration gate blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` is **previously recorded**, not freshly rehashed this run.
- Draft PR #418 HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`. PR #412/#413/#414/#418/#420/#422/#423 all OPEN, draft, unmerged as read from current PR metadata. Exact HEADs of remaining PRs not independently retained in this report.

## GitHub Actions evidence checked in this run
- [Chronology #41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE, validation SKIPPED; run head `f17283d9a5f0427c3d5b8a865d39455f92ee2f1d`. Prior HTTP 404 /anchor/latest remains a previously reported diagnosis, not newly reproduced here.
- [Runtime offline parity #38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499): 6/6 jobs SUCCESS.
- [Single runner #38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 SUCCESS.
- [OpenDART #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 SUCCESS.
- Earlier fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic additions, and 1.1315x regression-phase comparison are *historical evidence*, not newly rehashed artifacts. Whole CI wall-time and official backtest acceleration NOT VERIFIED.

## Railway production read-only evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- `indexalert-pit-rebuild` latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (created 2026-10-10 UTC).
- `indexalert-krx-historical-worker` deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12 UTC).
- `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS (2026-10-05 UTC).
- Production environment inventory reports **staged=null**, zero staged changes on listed services. This supersedes previous unverified assertions that a patch remained staged, without implying any patch was applied or any functionality fixed.
- PIT and KRX service deploy-log queries from 2026-11-06 20:00 UTC yielded no entries. Thus no fresh source-quality or calendar recovery proof. Runtime has 2026-11-06 21:16 UTC logs for SPY/QQQ/SCHD and USDKRW monitoring; these are *not* M20 PIT or profitability evidence.
- Previously observed 803 common stocks/27 nonpositive OHLC: data-quality FAIL **historical**, current remediation NOT VERIFIED. Earlier 1565/1565 private weekday-pair SHA integrity PASS **historical**; 90 unresolved day classifications and 12003 zero-activity quarantines not independently resolved.

## Independent gate verdict
| Gate | Verdict | Reason |
| --- | --- | --- |
| OpenDART original filing SGML shape/offline CI | PASS (narrow software/shape only) | 2/2 checked; not semantic original 3-month CFS proof |
| 2021/2022 original 3-month consolidated operating-profit semantics, corrections lineage, public available-at | NOT VERIFIED | No approved original/complete corrections/timestamp chain |
| Historical issuer/security mapping and official KRX session/security status/corporate actions/tradability/fills | NOT VERIFIED | Raw-pair integrity does not establish exchange status or executions |
| 27 historical OHLC anomaly source-quality | FAIL (last observed); current status NOT VERIFIED | No new PIT logs in query window |
| Chronology anchor | FAIL | GitHub auto-anchor failure, validation skipped |
| Offline parity safety CI | PASS (bounded) | 6/6, 1/1 verified; no economic authority |
| Cache approval SHA chain and whole-run speedup | NOT VERIFIED | No approved data/policy/runtime/evidence SHA chain |
| NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness after costs and taxes | NOT VERIFIED | Official PIT/economic run prohibited |
| M20 PIT admission / profitability RUN | NO-GO | All upstream source/tradability gates not passed |
| ORDERING | Must remain false | No authority to change |

## Next isolated read-only work
1. Inspect exact failing chronology job log and compare endpoint routing/response contract against deployed immutable SHA, without deployment or workflow changes.
2. Seek independently authenticated original 2021/2022 quarterly CFS source semantics, complete correction lineage and public availability timestamps; do not substitute filing date.
3. Independently reconcile official KRX calendar and stock-day state, corporate actions and fill/cost/tax evidence. Private 2021/2022 exact-set comparator PRs are synthetic-only pending separately approved worker read.
4. For optimization, pin SHA-256 of all independently approved source/data/code/Frozen policy/runtime/approval evidence before any cache reuse; only parallelize read-only independent post-processing. Never parallelize dependent training/capital transitions.
5. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/sealed Holdout/Champion/Top3/NO_TRADE, no post-hoc H5/Dynamic reuse, and no M20 economic experiment before source admission.
