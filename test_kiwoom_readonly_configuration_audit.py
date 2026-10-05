import contextlib
import io
import json
import unittest
from unittest.mock import patch

from kiwoom_readonly_configuration_audit import audit_configuration, main


class ConfigurationAuditTests(unittest.TestCase):
    def demo(self, **changes):
        env=dict(KIWOOM_ENV='DEMO',KIWOOM_BASE_URL='https://mockapi.kiwoom.com',
            KIWOOM_ORDERING_ENABLED='false',KIWOOM_APP_KEY='synthetic-key',
            KIWOOM_APP_SECRET='synthetic-secret')
        env.update(changes)
        return env

    def test_empty_configuration_is_blocked_without_defaults(self):
        out=audit_configuration({})
        self.assertFalse(out['demo_configuration_preconditions_met'])
        self.assertEqual(out['configured_environment'],'UNKNOWN')
        self.assertEqual(out['ordering_configuration'],'UNKNOWN')

    def test_explicit_demo_is_only_configuration_not_authentication_or_authority(self):
        out=audit_configuration(self.demo())
        self.assertTrue(out['demo_configuration_preconditions_met'])
        self.assertEqual(out['status'],'DEMO_CONFIGURATION_ONLY')
        for field in ('credentials_validated','account_origin_authenticated','broker_connectivity_verified',
            'execution_mode_attested','actual_ordering_switch_enforced','genuine_live_provenance_verified',
            'empirical_execution_blocker_closed','sealed_holdout_authorized','live_trading_authorized'):
            self.assertFalse(out[field])

    def test_real_config_remains_blocked_even_with_present_credentials(self):
        out=audit_configuration(self.demo(KIWOOM_ENV='REAL',KIWOOM_BASE_URL='https://api.kiwoom.com'))
        self.assertFalse(out['demo_configuration_preconditions_met'])
        self.assertIn('REAL_ENVIRONMENT_NOT_ADMITTED',out['errors'])

    def test_unknown_mode_never_defaults_to_demo_or_real(self):
        for mode in ('PAPER','AUTO','',None,True,'private-unknown-mode'):
            out=audit_configuration(self.demo(KIWOOM_ENV=mode))
            self.assertEqual(out['configured_environment'],'UNKNOWN')
            self.assertFalse(out['demo_configuration_preconditions_met'])

    def test_demo_mode_with_real_host_is_blocked(self):
        self.assertFalse(audit_configuration(self.demo(KIWOOM_BASE_URL='https://api.kiwoom.com'))['demo_configuration_preconditions_met'])

    def test_host_match_rejects_userinfo_query_path_scheme_port_and_similar_names(self):
        for host in ('http://mockapi.kiwoom.com','https://mockapi.kiwoom.com:443',
            'https://user:private@mockapi.kiwoom.com','https://mockapi.kiwoom.com/?token=private',
            'https://mockapi.kiwoom.com/path','https://mockapi.kiwoom.com.evil','https://mockapi.kiwoom.com#private',None):
            out=audit_configuration(self.demo(KIWOOM_BASE_URL=host))
            self.assertEqual(out['configured_host_class'],'INVALID_OR_MISSING')
            self.assertFalse(out['demo_configuration_preconditions_met'])

    def test_explicit_ordering_requests_are_blocked(self):
        for setting in ('true','1','on','yes',' TRUE '):
            out=audit_configuration(self.demo(KIWOOM_ORDERING_ENABLED=setting))
            self.assertEqual(out['ordering_configuration'],'REQUESTED')
            self.assertFalse(out['demo_configuration_preconditions_met'])

    def test_missing_or_unknown_switch_never_means_enforced_off(self):
        for setting in ('',None,False,'unrecognized'):
            out=audit_configuration(self.demo(KIWOOM_ORDERING_ENABLED=setting))
            self.assertEqual(out['ordering_configuration'],'UNKNOWN')
            self.assertFalse(out['actual_ordering_switch_enforced'])

    def test_missing_key_or_secret_fails_only_presence_precondition(self):
        for field in ('KIWOOM_APP_KEY','KIWOOM_APP_SECRET'):
            out=audit_configuration(self.demo(**{field:''}))
            self.assertFalse(out['demo_configuration_preconditions_met'])
            self.assertIn('APPLICATION_CREDENTIAL_FIELDS_MISSING',out['errors'])

    def test_whitespace_and_nonstring_credentials_are_not_counted_present(self):
        for value in ('   ',None,True,12,[]):
            out=audit_configuration(self.demo(KIWOOM_APP_KEY=value))
            self.assertFalse(out['app_key_field_present'])

    def test_audit_does_not_mutate_input_configuration(self):
        env=self.demo();before=dict(env)
        audit_configuration(env)
        self.assertEqual(env,before)

    def test_sensitive_values_never_appear_even_in_unknown_config_report(self):
        env=self.demo(KIWOOM_ENV='private-mode',KIWOOM_BASE_URL='private-host',
            KIWOOM_ORDERING_ENABLED='private-switch',KIWOOM_APP_KEY='private-key',KIWOOM_APP_SECRET='private-secret')
        serialized=json.dumps(audit_configuration(env))
        for value in env.values():self.assertNotIn(value,serialized)

    def test_cli_is_json_only_without_network_or_files(self):
        output=io.StringIO()
        with (patch.dict('os.environ',self.demo(),clear=True),patch('socket.socket',side_effect=AssertionError('network forbidden')),
            patch('builtins.open',side_effect=AssertionError('file access forbidden')),contextlib.redirect_stdout(output)):
            main()
        out=json.loads(output.getvalue())
        self.assertFalse(out['network_request_attempted'])
        self.assertFalse(out['database_or_file_mutation_attempted'])

    def test_demo_case_and_canonical_root_slash_are_accepted_without_echoing_values(self):
        out=audit_configuration(self.demo(KIWOOM_ENV='demo',KIWOOM_BASE_URL='https://mockapi.kiwoom.com/',KIWOOM_ORDERING_ENABLED='OFF'))
        self.assertTrue(out['demo_configuration_preconditions_met'])


if __name__=='__main__':unittest.main()
