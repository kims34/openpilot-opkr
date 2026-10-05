# Kiwoom configuration observation

The stdlib-only `python -S kiwoom_readonly_configuration_audit.py` command emits enum classifications and credential-field presence only. It does not emit secrets, raw hosts, accounts, or credential values. It performs no network request, file/database write, authentication, or broker operation. `-S` avoids provider sitecustomize startup effects.

Only explicitly configured DEMO, the canonical official mock HTTPS host, explicit ordering-disabled configuration, and both nonempty credential fields yield DEMO_CONFIGURATION_ONLY. All other combinations are CONFIGURATION_BLOCKED. Neither status verifies credential origin/validity, connectivity, account identity, MASTER_OFF enforcement, genuine LIVE evidence, or trading authority. The required MASTER_OFF value is a requirement, not a measured app state. The process exits successfully to preserve the unrelated public index application; a blocked observation does not change settings or grant authority.

Official source commit: Kiwoom-Securities/Kiwoom-REST-API@953e5dbff123f437ab4d11a78a95191a685eb51f, kiwoom/core/auth.py. This is a commit SHA (tree 4eb7d5497f4155ace73d8d37a03f3dc18abbe6fa).

Railway activation is a separately verified pinned deployment startup command retaining the existing execution-ledger audit, followed by this audit and the existing uvicorn application. No frozen research contract, model, threshold, holdout, credential, or order switch is modified. This observation cannot close empirical execution or promotion blockers.

Validation: 14 focused offline unit tests cover strict host matching, missing/unknown/REAL configuration, ordering requests, privacy, no input mutation, and no CLI file/network access. Server Actions must also pass before merge.
