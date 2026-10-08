# Prospective read-only runtime — 2026-10-08

Status: STRUCTURAL CURRENT-SESSION CAPTURE ONLY — NO SOURCE/MODEL/CHRONOLOGY ADMISSION, NO FRESH ALPHA, NO LIVE ORDER AUTHORITY.

The frozen H5 block16 model is now an immutable runtime bundle and the exact supervised-session calendar prefix from adopted Action 36643183157 is pinned with SHA-256 `852f25e6f43e3c1df6dd201604eab5fea9ec1bd7b7468b9dea30eac3fe334ee3`.

`research_v1_prospective_runtime.py` closes the next execution gap without touching the broker:

- refuses to run before 18:30 KST;
- requires the exact read-only KRX network authority marker and `KRX_AUTH_KEY`;
- fails closed if any real-order, funds-movement or permission-change flag is true or `ORDERING` is not `DISABLED`;
- verifies the immutable 2015-origin long-history source on the Railway PIT volume;
- loads only recent verified prior-session rows as feature warmup;
- fetches official KRX OpenAPI KOSPI daily-trade/security-master data for the small post-freeze gap through the current session;
- extends the pinned supervised-session calendar only with non-empty official market sessions;
- binds the prebuilt block16 model without refitting historical outcomes;
- transactionally stores source, input, producer, model, decision and final session-manifest artifacts under a private PIT-volume directory;
- emits a separate hash-only anchor payload for later independent chronology anchoring.

A market holiday produces `NO_MARKET_SESSION` and no decision. A same-session completed manifest is idempotently reported as already committed. A partial/conflicting same-session state remains fail-closed.

The runtime does not import or call Kiwoom/broker order code. It cannot authorize or place an order. Every committed session keeps independent source/model/chronology admission, Fresh Alpha admission, Shadow S1, Fresh Confirmation S2, promotion and live-order authority false.

The next boundary after this PR is autonomous external chronology anchoring of the hash-only payload; only after that can a fresh observation be considered for independent evidence admission.


## Continuous read-only wrapper

The production image now starts `research_v1_prospective_http_runtime.py`.
It performs startup-only validation of the read-only authority flags, pinned
model, pinned session calendar and immutable PIT source, then remains online
without contacting KRX until the 18:30 KST finality guard has passed.

The wrapper exposes only `GET /health`, `GET /status`, and
`GET /anchor/latest`. Every POST is rejected with 405. The anchor endpoint
contains only the immutable per-session hash payload already written by
`run_once()`; it contains no securities, scores, account data or credentials.

After finality the wrapper retries the existing `run_once()` producer at most
once per 15 minutes. The decision/model/source implementation remains the
same-session-universe-safe implementation from PR #343. No endpoint can grant
source/model/chronology admission, Fresh Alpha, Shadow, promotion, funds,
permissions or live-order authority.
