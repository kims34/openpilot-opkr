# IndexAlert 2021 actual private source day-set comparison (isolated offline, NO PIT)

**Status:** An executable READ-ONLY code path has been added. **The real 2021 private Railway volume has NOT been re-read or date-compared by this work.** This is a new exact day-set reconciliation capability, not completed calendar certification, KRX index service approval, investment backtest, or operational authorization.

## Why this closes a practical tooling gap

An actual Railway historical worker deployment, \`16c93d7c-7cd0-4d84-a327-298d2805376c\`, logged that its 2021 original private source stored **261/261 weekday daily/master source pairs**, its full annual private source receipt fingerprint was \`362716e7bb5e025a9dcd39207b1ee095d97c633b8ca907722c766edf799ec2a1\`, and **13** daily responses were empty, with **no official PIT or market status admission**. An annual count of 13 matching 10 originally expected + 3 subsequently announced KRX exchange closed sessions is **not** proof that the *same thirteen days* were empty.

The approved history service already stores every weekday's original source checkpoint as \`/data/openapi_kospi_history_v1/acquisitions/YYYYMMDD.json\` with SHA-backed content-addressed daily/master raw objects; the existing \`research_v1_krx_openapi_private_integrity_audit.py\` verifies original bytes/length/source schema/source date/authorizations and builds a deterministic snapshot fingerprint.

### Implemented independent no-network 2021 comparator

File \`research_v1_krx_private_2021_calendar_candidate_audit.py\`:

1. Defaults to **dry run** (no volume read). \`--audit\` permits a read only in the already existing named Railway \`indexalert-krx-historical-worker\`, only for a validated dedicated \`/data\` private volume path.
2. Re-runs **full 2021 261-day, dual-source, raw-byte SHA and schema integrity** via the existing audit, requires the exact previously logged **2021 SHA256**, exactly **13** original empty days, zero missing/invalid receipts, and rejects any source/permission drift.
3. Re-reads all **261** existing per-day private receipts (no external query) and independently recomputes the exact first-pass fingerprint. A mismatch from a changed/rotated source during the audit **fails closed** rather than asserting a holiday match.
4. Compares the **exact 13 empty calendar day keys in memory** with the explicitly fixed **10** dates in the [2020-12-28 KRX-derived public stock-market schedule](https://www.yna.co.kr/view/AKR20201225031900002), plus the **3** closure days announced on [2021-08-04](https://www.yna.co.kr/view/AKR20210804093200002): 2021-08-16, 2021-10-04, 2021-10-11. Reports **only aggregate matched/missing/unexpected counts** and boolean equality. Never prints the actual private date list, original raw rows/identifiers, price data, source receipt digest, credentials or any account data.
5. Even a complete date-set match is classified **PRIVATE_EMPTY_DATE_SET_MATCHES_CANDIDATES_NOT_PIT**, **NOT** an authenticated exchange calendar, as-of-publication proof, individual stock tradability or permissible backtest. An unmatched date fails the command with an explicit **PRIVATE_EMPTY_DATE_SET_MISMATCH_NOT_PIT** classification; source integrity failures are **FAIL_CLOSED**.

Companion \`test_research_v1_krx_private_2021_calendar_candidate_audit.py\` tests an all-matching invented 261-day source set, a swapped incorrect day that **still totals 13**, missing 1/261 day, SHA mismatch across passes, malformed receipt/row count, mismatched class, first pass source permission drift, wrong worker/mount, and no-work dry run. Synthetic CI has no real data and no Railway/data mount.

### Execution boundary

The existing deployed worker cannot execute this new GitHub source until an owner separately authorizes and performs an appropriate reviewed deployment/access step; **none is requested or done here**. The code is a prepared reproducible private offline audit for the responsible worker owner. Deploying or otherwise executing inside a live production worker must be independently approved and cannot be inferred from this PR. No additional KRX OpenAPI service route, issuance key, network, authenticated historical calendar endpoint, live orders, model change, Holdout or capital transition.

The 2017–2022 outstanding **90 original day classes** remain completely unadmitted. The separate **2026-09-28 27 prospective H5 nonpositive OHLC stock rows** must not be combined with the 2021 date review. 2022 original first-publication DART 3-month CFS operating profit is also still NOT verified. Frozen H5/M20/504-126-126/PIT/WF/purge/CPCV/Champion/Top3/NO_TRADE are unchanged. \`ORDERING=false\`.

This branch is intentionally based upon the KRX owner's current isolated Draft PR #420 branch. **Keep both PRs Draft and unmerged.**
