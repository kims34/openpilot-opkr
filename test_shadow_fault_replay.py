import socket
import unittest
from unittest.mock import patch

from shadow_fault_replay import run_offline_fault_replay


class OfflineFaultReplayTests(unittest.TestCase):
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
