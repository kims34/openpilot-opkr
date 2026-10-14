"""Socket-restricted unittest entry point for IndexAlert Kiwoom *offline CI only*.

This safeguards the synthetic unit tests against accidentally opening outbound
socket connections if a mock gets dropped. It does not touch the broker, keys,
Railway, runtime source or the Windows owner-side diagnostics.

This guards the test Python process; it is not a Linux network namespace and
does not claim to prevent a deliberately launched child process from networking.
"""
from __future__ import annotations

import socket
import sys
import unittest
from unittest.mock import patch


class OfflineNetworkAttempt(RuntimeError):
    """Static, credential-free failure for an unexpected real network attempt."""


def _deny_network(*_args, **_kwargs):
    raise OfflineNetworkAttempt("OFFLINE_CI_NETWORK_DENIED")


def main() -> int:
    tests = sys.argv[1:]
    if not tests:
        raise SystemExit("OFFLINE_CI_TEST_MODULES_REQUIRED")

    # unittest uses no external service. Local SQLite, synthetic stream objects,
    # unittest.mock and in-memory assertions remain available.
    with (
        patch.object(socket.socket, "connect", _deny_network),
        patch.object(socket.socket, "connect_ex", _deny_network),
        patch.object(socket.socket, "sendto", _deny_network),
        patch.object(socket, "create_connection", _deny_network),
        patch.object(socket, "getaddrinfo", _deny_network),
    ):
        # First prove that an unexpected broker TCP connect and hostname
        # resolution fail locally before any unit tests are imported.
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            try:
                probe.connect(("127.0.0.1", 1))
            except OfflineNetworkAttempt:
                pass
            else:
                raise RuntimeError("OFFLINE_CONNECT_GUARD_MISSING")
        finally:
            probe.close()
        try:
            socket.getaddrinfo("api.kiwoom.com", 443)
        except OfflineNetworkAttempt:
            pass
        else:
            raise RuntimeError("OFFLINE_DNS_GUARD_MISSING")

        suite = unittest.defaultTestLoader.loadTestsFromNames(tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
