# Prospective structural session commit — 2026-10-08

Status: END-TO-END STRUCTURAL CAPTURE TRANSACTION — NOT ADMITTED FRESH ALPHA, NOT SHADOW, NOT LIVE.

The prospective path now has independently tested component boundaries for current-session official KRX OpenAPI normalization, label-free inputs, freeze-anchor model/refit identity, and append-only decisions. This change makes their durability semantics explicit as one session transaction.

`commit_structural_prospective_session` consumes already-retrieved KRX OpenAPI daily-trade/security-master raw bytes plus prior market history and the scheduled pre-test supervised frame. It:

1. creates and stores the exact KRX source receipt and content-addressed raw objects;
2. binds that source-receipt SHA-256 into the label-free input snapshot;
3. reconstructs the exact freeze-anchor anchored-WF producer/model block;
4. stores the deterministic model bundle and per-target producer binding;
5. generates and stores the complete pre-outcome decision capture;
6. publishes one immutable `session-YYYY-MM-DD.json` manifest only after every component succeeds.

A source/model/input artifact may exist after a crash or later validation failure. That partial state is **not** a committed session because the final manifest is absent. Identical retries are idempotent; conflicting same-session source/input/producer/decision/manifest files fail closed instead of overwriting history.

The final manifest records only structural completion. It keeps source admission, model admission, chronology admission, Fresh Alpha admission, formal Shadow S1, Fresh Confirmation S2, promotion and live-order authority exact false.

The tests deliberately fail after source persistence by withholding scheduled supervised history and confirm that no decision or final session manifest is created. They also verify same-session idempotence and reject target/future rows smuggled into prior history.

This remains network-free engineering in CI. It does not perform a KRX request, private production fit, consumed holdout read, historical performance rerun, broker order, funds movement or permission change.
