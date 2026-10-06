"""Fail-closed tracker for user-operated validations that are intentionally deferred.

This is workflow state only. It never executes commands, reads credentials, contacts
brokers, grants gate admission, or authorizes trading.
"""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class DeferredUserValidation:
    validation_id: str
    purpose: str
    script_path: str
    completed: bool = False

    def validate(self):
        if not all(type(v) is str and v.strip() for v in
                   (self.validation_id, self.purpose, self.script_path)):
            raise ValueError("non-empty validation metadata required")
        if type(self.completed) is not bool:
            raise ValueError("completed must be exact bool")
        return self


def current_deferred_validations() -> dict:
    items = (
        DeferredUserValidation(
            "KIWOOM_REAL_ACCOUNT_SCOPE_READONLY_v1",
            "Verify complete read-only REAL account scope for orders, open orders, fills and holdings",
            "kiwoom_real_account_scope_readonly_smoke.ps1",
            completed=True,
        ),
    )
    material = tuple(item.validate() for item in items)
    return {
        "mode": "DEFERRED_USER_VALIDATION_TRACKER",
        "items": [asdict(item) for item in material],
        "pending_count": sum(not item.completed for item in material),
        "blocks_independent_development": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "broker_permission_change_authorized": False,
    }
