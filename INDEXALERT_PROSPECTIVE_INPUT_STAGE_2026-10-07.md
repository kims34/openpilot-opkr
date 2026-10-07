# Prospective input stage — 2026-10-07

Status: INPUT_SNAPSHOT_ONLY_NOT_DECISION. Actual capture and storage of market observations are NOT VERIFIED.

## Implemented

`build_current_session_inputs` builds the current KST session's frozen H5 feature/context matrix without requiring future prices or outcome labels. Synthetic mature-date inputs match the existing frozen reference exactly. Later sessions and outcome columns cannot change the matrix or retained raw-input fingerprint. Rows supplied as available after the decision timestamp reject the entire supplied cross-section rather than change ranks by dropping names. Missing current-session data or insufficient warmup raises an error; neither is NO_TRADE.

`store_input_snapshot` writes canonical JSON outside the Git/public tree with mode 0600, atomic no-overwrite publication and file/directory fsync. Identical retries are idempotent; a conflicting same-session checkpoint cannot replace the original. This is local durability, not protection against a privileged operator or independent proof of when a decision occurred.

Eight synthetic tests cover current-session output, future/outcome isolation, frozen feature parity, late data, missing/warmup data, duplicate/naive timestamps, input-order invariance and checkpoint conflicts/privacy. No historical performance rerun, holdout access, market collection or order is involved.

## Remaining boundaries

- Availability timestamps are caller-supplied claims. This module does not independently establish source rights, completeness, daily-close finality, publication times or historical point-in-time provenance.
- No admitted official data adapter, pinned model/calibration bundle, refit schedule, actual decision producer, scheduler or live deployment is connected by this change.
- Input snapshots do not count as FreshAlpha observations, genuine NO_TRADE decisions, Shadow S1/S2 or accepted Alpha. Signal generation, decision recording, independent source admission and live-order authorization remain false.
- The frozen H5 policy and failed/consumed v1 holdout remain unchanged. Existing statistical evidence does not establish a profitable strategy.
- MASTER_OFF remains in effect. Broker connectivity resolution alone cannot authorize real trading or supply missing strategy evidence.

Next consequential work is to connect an independently admitted official source and a reproducible frozen model/calibration identity to a genuine prospective decision record. This implementation is the input foundation only.
