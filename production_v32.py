"""IndexAlert production v3.2: build-bound Android push observability.

Market, probability, KRX, recommendation and execution behavior remain the exact
v31 stack. The build-registration overlay is shared with any compatible runtime
entrypoint so deployment start-command drift cannot silently remove the physical
E2E contract.
"""
from __future__ import annotations

import production_v31
from push_build_registration import (
    PHYSICAL_E2E_BINDING_CONTRACT,
    REGISTRATION_BUILD_CONTRACT,
    SELF_TEST_TRIGGER_CONTRACT,
    RegisterBodyV32,
    _clean_client_build,
    _init_device_build_db,
    _latest_registered_build,
    _latest_registered_device_build,
    _record_device_build,
    attach,
    push_health_v32,
    register_v32,
)

# Re-export `production` for the existing isolated registration tests that patch
# the established base registration implementation through this runtime module.
import production

app = production_v31.app
attach(app)
