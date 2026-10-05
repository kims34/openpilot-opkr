"""Stdlib-only configuration observation: no auth/query/order or mutation.

Run with python -S before the public app to avoid sitecustomize side effects.
Presence/matching config are not credential validity or origin attestation.
This audit changes no switch, permission, mode, gate or provider connection.
"""
import json
import os


OFFICIAL_SOURCE_COMMIT = '953e5dbff123f437ab4d11a78a95191a685eb51f'
DEMO_BASE_URL = 'https://mockapi.kiwoom.com'
REAL_BASE_URL = 'https://api.kiwoom.com'


def _present(value):
    return type(value) is str and bool(value.strip())


def audit_configuration(environ=None):
    env = os.environ if environ is None else environ
    raw_mode = env.get('KIWOOM_ENV')
    mode = raw_mode.strip().upper() if type(raw_mode) is str else ''
    environment = mode if mode in ('DEMO', 'REAL') else 'UNKNOWN'
    base = env.get('KIWOOM_BASE_URL')
    host = ('DEMO' if type(base) is str and base in (DEMO_BASE_URL, DEMO_BASE_URL+'/')
        else 'REAL' if type(base) is str and base in (REAL_BASE_URL, REAL_BASE_URL+'/')
        else 'INVALID_OR_MISSING')
    raw_ordering = env.get('KIWOOM_ORDERING_ENABLED')
    setting = raw_ordering.strip().lower() if type(raw_ordering) is str else ''
    ordering = ('DISABLED' if setting in ('0','false','off','no')
        else 'REQUESTED' if setting in ('1','true','on','yes') else 'UNKNOWN')
    key_present = _present(env.get('KIWOOM_APP_KEY'))
    secret_present = _present(env.get('KIWOOM_APP_SECRET'))
    errors = []
    if environment != 'DEMO':
        errors.append('REAL_ENVIRONMENT_NOT_ADMITTED' if environment == 'REAL' else 'EXPLICIT_DEMO_ENVIRONMENT_REQUIRED')
    if host != 'DEMO':
        errors.append('EXACT_OFFICIAL_DEMO_HOST_REQUIRED')
    if ordering != 'DISABLED':
        errors.append('EXPLICIT_READ_ONLY_ORDERING_CONFIGURATION_REQUIRED')
    if not (key_present and secret_present):
        errors.append('APPLICATION_CREDENTIAL_FIELDS_MISSING')
    return dict(mode='READ_ONLY_KIWOOM_CONFIGURATION_AUDIT',
        status='DEMO_CONFIGURATION_ONLY' if not errors else 'CONFIGURATION_BLOCKED',
        configured_environment=environment, configured_host_class=host,
        ordering_configuration=ordering, app_key_field_present=key_present,
        app_secret_field_present=secret_present, errors=errors,
        demo_configuration_preconditions_met=not errors,
        official_documentation_commit=OFFICIAL_SOURCE_COMMIT,
        credentials_validated=False, account_origin_authenticated=False,
        broker_connectivity_verified=False, required_execution_mode='MASTER_OFF',
        execution_mode_attested=False, actual_ordering_switch_enforced=False,
        network_request_attempted=False, broker_request_sent=False,
        database_or_file_mutation_attempted=False, configuration_mutated=False,
        secrets_or_accounts_emitted=False, genuine_live_provenance_verified=False,
        empirical_execution_blocker_closed=False, sealed_holdout_authorized=False,
        live_trading_authorized=False)


def main():
    # This observational audit must not take the unrelated public index app
    # offline when broker config is blocked. It authorizes no broker operation.
    print(json.dumps(audit_configuration(), sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
