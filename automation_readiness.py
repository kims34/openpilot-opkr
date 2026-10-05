"""Public read-only capability status; never evaluates or grants admission."""
PATH = '/automation/readiness'


def readiness():
    # This deployed stack has no executable broker automation integration.
    # Environment flags, request parameters and caller assertions cannot turn
    # this capability report into a sender or independent gate admission.
    return dict(status='BROKER_AUTOMATION_UNAVAILABLE',mode='MASTER_OFF',
        message='자동매매 실행 기능이 아직 연결되지 않았습니다.',
        live_ordering_authorized=False,broker_order_submission_implemented=False,
        automation_control_persistence_implemented=False,
        independent_gate_admission_evaluated=False,
        account_or_capital_snapshot_observed=False,
        orders_requested=False,funds_movement_attempted=False,
        database_or_file_mutation_attempted=False,
        frozen_criteria_changed=False,
        required_user_control_fields=['automation_enabled','max_automation_capital_krw'])


def attach(app):
    for route in app.router.routes:
        if getattr(route,'path',None)==PATH:
            if getattr(route,'endpoint',None) is readiness and getattr(route,'methods',None)=={'GET'}:
                return
            raise RuntimeError('conflicting automation readiness route')
    app.add_api_route(PATH,readiness,methods=['GET'],tags=['automation'])
    app.openapi_schema = None
