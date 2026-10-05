"""Offline protected account equality before normalized receipt retention.

Inject synthetic/protected context locally, never through logs or artifacts.
Keyed account fingerprints prevent a public unkeyed account-number dictionary
hash. Equality and HMAC do NOT authenticate environment, source or trading date.
No network, credential discovery, real-account query, sender or LIVE admission.
"""
import hashlib
import hmac

from kiwoom_order_journal_bridge import NativeBridgeError, require
from research_v1_kiwoom_native_execution import normalize_realtime_order_fill_event


class ProtectedIntakeError(ValueError):
    pass


class ProtectedAccountBinding:
    """Process-local secret context. Default repr never exposes fields."""
    __slots__ = ('_account', '_fingerprint')

    def __init__(self, *, account, fingerprint_key):
        if (not isinstance(account, str) or not account or account != account.strip()
            or len(account) > 256 or type(fingerprint_key) is not bytes or len(fingerprint_key) < 32):
            raise ProtectedIntakeError('INVALID_PROTECTED_ACCOUNT_CONTEXT')
        try:
            self._account = account.encode('utf-8')
        except UnicodeError:
            raise ProtectedIntakeError('INVALID_PROTECTED_ACCOUNT_CONTEXT') from None
        self._fingerprint = 'sha256:' + hmac.new(fingerprint_key,
            b'indexalert-kiwoom-account-fingerprint-v1\x00' + self._account,
            hashlib.sha256).hexdigest()

    def __repr__(self):
        return '<ProtectedAccountBinding redacted>'

    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise AttributeError('protected account context is immutable')
        object.__setattr__(self, name, value)

    @property
    def fingerprint(self):
        return self._fingerprint

    def matches(self, value):
        return isinstance(value, str) and hmac.compare_digest(self._account, value.encode('utf-8'))


# Official reviewed type00 fields only; unknown raw fields may contain private
# account/credential material and must never reach normalized receipt storage.
RAW_FIELDS = frozenset('''9201 9203 9001 900 901 902 903 904 905 906 907 908
909 910 911 912 913 914 915 919 938 939 2134 2135 2136'''.split())


class KiwoomProtectedExecutionIntake:
    def __init__(self, inbox, binding):
        self.inbox = inbox
        self.binding = binding
        try:
            with inbox.bridge._guard():
                require(type(binding) is ProtectedAccountBinding)
                require(binding.fingerprint == inbox.bridge.account)
        except NativeBridgeError:
            raise ProtectedIntakeError('PROTECTED_INTAKE_RECONCILIATION_REQUIRED') from None

    def append(self, receipt_id, key, raw_event, *, trading_date):
        # Raw equality checks complete before the account-free normalized row
        # may be retained. No raw event, account or exception text returned.
        try:
            with self.inbox.bridge._guard():
                require(type(raw_event) is dict and set(raw_event) <= RAW_FIELDS)
                require(all(type(v) is str and len(v) <= 4096 for v in raw_event.values()))
                require(self.binding.matches(raw_event.get('9201')))
                require(self.binding.fingerprint == self.inbox.bridge.account)
                self.inbox.bridge._context(trading_date)
                row = normalize_realtime_order_fill_event(raw_event,
                    account_fingerprint=self.binding.fingerprint)
            result = self.inbox.append(receipt_id, key, row, trading_date=trading_date)
        except (NativeBridgeError, ValueError, TypeError, UnicodeError):
            raise ProtectedIntakeError('PROTECTED_INTAKE_RECONCILIATION_REQUIRED') from None
        return dict(result, mode='OFFLINE_PROTECTED_EXECUTION_INTAKE',
            raw_account_equality_checked=True,
            fingerprint_scheme='HMAC_SHA256_ACCOUNT_V1',
            environment_origin_authenticated=False, trading_date_origin_attested=False)
