import socket
import unittest
from unittest.mock import patch

from shadow_fault_replay import run_offline_fault_replay, run_protected_capital_fault_replay


class OfflineFaultReplayTests(unittest.TestCase):
    def test_protected_native_receipt_and_capital_replay_without_network_or_admission(self):
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('network forbidden')):
            result = run_protected_capital_fault_replay()
        self.assertTrue(result['passed'])
        self.assertEqual(result['scenario_count'], 7)
        self.assertEqual(len(set(result['scenarios'])), 7)
        self.assertIn('type00_frame_extracts_before_protected_routing', result['scenarios'])
        self.assertNotIn('synthetic-private-account', str(result))
        for field in ('network_request_attempted','broker_request_sent','sealed_holdout_read',
            'strategy_evaluated','actual_cash_settlement_verified','genuine_live_evidence',
            'live_ordering_authorized','production_promotion_authorized'):
            self.assertIs(result[field],False)

    def test_cross_component_replay_with_network_connections_forbidden(self):
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('network forbidden')):
            result = run_offline_fault_replay()
        self.assertTrue(result['passed'])
        self.assertEqual(result['scenario_count'], 8)
        self.assertEqual(len(set(result['scenarios'])), 8)
        self.assertEqual(result['mode'], 'OFFLINE_SYNTHETIC_FAULT_REPLAY')
        for field in ('network_request_attempted', 'broker_request_sent', 'sealed_holdout_read',
                      'strategy_evaluated', 'genuine_live_evidence', 'live_ordering_authorized',
                      'production_promotion_authorized'):
            self.assertIs(result[field], False)


if __name__ == '__main__':
    unittest.main()
