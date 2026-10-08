# Tiny Live critical path — 2026-10-08

Goal: reach a safe 100,000 KRW capital-capped Tiny Live state as quickly as possible without weakening any Frozen/PIT/Holdout/NetEV/execution/risk/promotion requirement.

## A — Tiny Live hard blockers

1. **Genuine prospective decision clock is not yet running continuously.**
   The frozen long-history, exact supervised cache and block16 runtime model are now reconstructed/pinned, but a future observation is useful only if the current session is captured before later outcomes. This is the first time-critical blocker and is addressed by the new read-only prospective runtime in this change.
2. **Independent source/model/chronology admission is incomplete.**
   Structural hashes and green CI are not independent admission. The runtime keeps every admission flag false. GitHub chronology anchoring and later trusted source/model admission remain required.
3. **Valid Alpha/Shadow progression is incomplete.**
   The consumed v1 holdout remains immutable failed/invalid evidence. No rescue rerun is permitted. Exact-policy prospective Shadow S1 and Fresh Confirmation S2 cannot be skipped.
4. **Kiwoom REAL type00 LOGIN 8050 remains unresolved.**
   The broker reply removes the IP-rule hypothesis; a fresh-token read-only rerun is still required before broker-native order/fill capture is considered connected. No order is needed for that test.
5. **Independent Early-Live gate composition is not yet implemented/admitted.**
   Caller booleans cannot make final-user readiness true.
6. **Real-order activation remains intentionally absent.**
   Order-create/amend/cancel envelopes, journal, reconciliation, late-fill, Kill and capital controls have substantial offline coverage, but actual ordering cannot be enabled before the preceding gates and a final explicit user authorization.
7. **100,000 KRW production operating ceiling must be frozen in the eventual live deployment.**
   The existing capital allocator is structural/offline; the live deployment must bind the exact account/settlement provenance and hard ceiling before activation.

## B — needed for Tiny Live stabilization

- live broker settlement/cash-reuse admission across repeated cycles;
- broker-native provenance packaging for real order/fill evidence;
- operator-facing status/Kill visibility and installed production-signing continuity;
- roll-forward/rollback separation between the pinned operating version and development.

## C — post-Tiny-Live backlog

- noncritical UI polish;
- additional model/challenger exploration not needed for the admitted Champion;
- refactors that do not remove a current A/B blocker;
- broad feature expansion and convenience automation.

## This change: start the non-skippable future clock

`research_v1_prospective_runtime_runner.py` is intentionally **not** a trading runtime. It runs only after 19:00 KST, consumes the approved KRX OpenAPI daily-trade/security-master endpoints, fills only the post-2026-09-23 warm-up gap, binds the pinned frozen block16 bundle, and writes an immutable structural prospective session. It exposes only hash-only public-safe status/anchor material.

Important boundaries:

- no Kiwoom import or broker order request;
- no historical decision backfill;
- empty/non-session OpenAPI response is not converted into NO_TRADE evidence;
- current source finality/source admission remains false;
- model admission remains false;
- chronology admission remains false until the external GitHub anchor verifier succeeds;
- Fresh Alpha, Shadow S1, S2, promotion and live authority remain false;
- ORDERING stays disabled and funds/permissions are untouched.

The service is designed to use the already-verified PIT volume and pinned runtime model so genuine future structural observations can start accumulating while the remaining independent blockers are solved in parallel.
