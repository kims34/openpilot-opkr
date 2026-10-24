# IndexAlert independent integration read-only gate — 2026-10-24 22:48 KST

## Read-only HEAD ledger
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (GitHub branch endpoint).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branch endpoint).
- Integration Draft #414: pre-write HEAD `726e51dce2331fddfe53111f494da6eb73e0a46c`; gate document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- KRX Drafts #420 / #422 / #423: `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Runtime Drafts #413 / #418: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` / `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- #414 changed paths queried: documentation-only `docs/` paths; prior HEAD `726e51d...` was itself a one-file document commit. This is a path-level boundary only.

## New independently inspected CI observation
- Repository latest Actions list queried. Latest read-only watchdog [#40087709481](https://github.com/kims34/openpilot-opkr/actions/runs/40087709481), created 2026-10-24 10:53:39 UTC, completed SUCCESS; exact job `120853913810` log read.
- Log explicitly reports `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Its ZIP artifact ID `12557812112` and uploader-reported SHA-256 `1c86706ccb0de2b84bbff26f67febfc1594bc833d0cf337723d05e998eb14baa` are **Action-attested only**, not independently downloaded/rehashed and **not live Railway authority**.
- OpenDART #412 latest head CI [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) and [#39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) are offline-only SUCCESS, not original 2022/2021 standalone consolidated three-month profit or intraday first-public PIT proof.
- KRX #420 [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) and #423 [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) are offline-only SUCCESS, not actual private original calendar/stock-status/corporate-action/fill verification.
- Runtime #413 [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) offline parity SUCCESS, negative measured regression-phase speed ratio (serial 1.7650 s / parallel 2.7079 s = 0.652x); #418 [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) pinned archived source gate FAIL due to manifest blob identity mismatch. No source re-pin or speedup approval.
- Railway `list_projects` read-only was attempted and returned `User input required but current turn is running in a non-interactive mode.` No fresh production deployment/logs, private bytes or live ORDERING value independently observed. No authorisation bypass.

## Admission matrix (no economic execution)
- Git HEAD/PR identity: **PASS metadata only**.
- Watchdog and synthetic offline guards: **PASS narrowly**, no financial or operational admission.
- #418 archived source identity: **FAIL** (real CI).
- OpenDART original filing, public available-at/PIT, 2022/2021 original three-month CFS operating-income and amendment lineage: **NOT VERIFIED**.
- Historical issuer/security map: **NOT VERIFIED**.
- Official KRX trading sessions, stock tradability, corporate actions, fillability: **NOT VERIFIED**; prior 90 historical calendar/source-gap flags and 27 nonpositive OHLC cases remain quarantined.
- Fees/taxes/slippage/impact and NetEV/PF/CAGR/MDD/ES95/99, concentration and time-slice robustness: **NOT VERIFIED / NOT EVALUABLE** without admitted source and immutable authorised evaluation.
- Railway live environment and actual `ORDERING`: **NOT VERIFIED**.

**Decision: M20 PIT admission NO-GO; M20 economic RUN NO-GO.** Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV, sealed Holdout, Champion, Top3/NO_TRADE and all frozen cost/tax/risk/promotion thresholds. Require `ORDERING=false`; never imply the production value was checked. No specialist code edits, new performance trials, consumed Holdout reuse, live orders, funds, credentials/permissions, deployment, merges or promotion.

Next proof belongs to specialist source owners (original OpenDART edition and exact first-public/period lineage; official KRX per-day private vs public status and corporate actions; runtime original source and complete wheel/native/transitive dependency attestation). Operational attestation requires Railway interactive authorisation. This audit only records read-only evidence and does not duplicate their tests.
