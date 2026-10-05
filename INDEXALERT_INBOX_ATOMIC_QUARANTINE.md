# Atomic offline inbox quarantine

Conflict receipt insertion now commits together with MASTER_OFF, the reconciliation barrier, intent uncertainty and invalidation of settlement bindings. Previously a process interruption between the conflict commit and the subsequent error guard could leave the mode observationally enabled, although claim gates still rejected conflicts. No conflict is resolved or removed.

Replay now retains BEGIN IMMEDIATE from receipt digest/conflict verification through native execution binding. A competing writer cannot insert a conflict between those checks and the fill mutation. The private locked helper requires an active transaction. Public bridge callers retain their existing transaction guard. The attempt marker remains a separate transaction so existing crash/replay idempotence is preserved.

Three synthetic fault tests verify interruption after a conflict commit, a competing SQLite writer, and native-binding failure rollback. No broker request, source admission, cash settlement, model/threshold change or trading authority is introduced. Offline diagnostics remain distinct from genuine broker evidence.
