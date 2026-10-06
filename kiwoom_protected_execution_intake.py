"""Offline protected account equality before normalized receipt retention.

Inject synthetic/protected context locally, never through logs or artifacts.
Keyed account fingerprints prevent a public unkeyed account-number dictionary
hash. Equality and HMAC do NOT authenticate environment, source or trading date.
No network, credential discovery, real-account query, sender or LIVE admission.
"""
import hashlib
import hmac
from decimal import Decimal, InvalidOperation

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
NORMALIZER_FIELDS = frozenset('''9201 9203 9001 900 901 902 903 904 905 906 907 908
909 910 911 912 913 914 915 919 938 939 2134 2135 2136'''.split())
RAW_FIELDS = NORMALIZER_FIELDS | frozenset('''9205 302 10 27 28 920 921 922 923 10010'''.split())


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

    def _normalize_locked(self, raw_event, trading_date):
        require(type(raw_event) is dict and set(raw_event) <= RAW_FIELDS)
        require(all(type(v) is str and len(v) <= 4096 for v in raw_event.values()))
        require(self.binding.matches(raw_event.get('9201')))
        require(self.binding.fingerprint == self.inbox.bridge.account)
        self.inbox.bridge._context(trading_date)
        # Official extra fields (administrator/screen/terminal/loan/quotes)
        # are recognized but not needed for this mapping. Drop them before
        # retention or local identity hashing.
        selected = {k:v for k,v in raw_event.items() if k in NORMALIZER_FIELDS}
        return normalize_realtime_order_fill_event(selected,
            account_fingerprint=self.binding.fingerprint)

    @staticmethod
    def _report(result, *, bound_order_resolved=False):
        return dict(result, mode='OFFLINE_PROTECTED_EXECUTION_INTAKE',
            raw_account_equality_checked=True,
            broker_order_binding_resolved=bound_order_resolved,
            fingerprint_scheme='HMAC_SHA256_ACCOUNT_V1',
            environment_origin_authenticated=False, trading_date_origin_attested=False)

    @staticmethod
    def _has_execution_signal(row):
        if row.get('order_status') == '체결' or str(row.get('broker_execution_id', '')).strip():
            return True
        for field in ('fill_price','fill_qty','unit_fill_price','unit_fill_qty'):
            value = str(row.get(field, '')).strip()
            if value:
                try:
                    amount = Decimal(value.replace(',', ''))
                except InvalidOperation:
                    require(False)
                require(amount.is_finite())
                if amount != 0:
                    return True
        return False

    def _resolve_bound_key_locked(self, row, supplied_key=None):
        broker_order_id = row.get('broker_order_id')
        require(isinstance(broker_order_id, str) and bool(broker_order_id.strip()))
        bound = self.inbox.journal.db.execute(
            'SELECT key FROM native_order_bindings WHERE broker_order_id=?',
            (broker_order_id,)).fetchone()
        require(bound is not None and isinstance(bound[0], str) and bool(bound[0]))
        if supplied_key is not None:
            require(isinstance(supplied_key, str) and supplied_key == bound[0])
        return bound[0]

    def _ignored_nonfill_report(self, *, bound_order_resolved):
        return self._report(self.inbox._report('NON_FILL_EVENT_IGNORED',
            executions_created=False), bound_order_resolved=bound_order_resolved)

    def append(self, receipt_id, key, raw_event, *, trading_date):
        # Raw equality checks and immutable broker-order routing complete before
        # the account-free normalized row may be retained. Pure order-lifecycle
        # messages are not execution receipts and must not poison the inbox.
        try:
            with self.inbox.bridge._guard():
                row = self._normalize_locked(raw_event, trading_date)
                self._resolve_bound_key_locked(row, supplied_key=key)
                if not self._has_execution_signal(row):
                    return self._ignored_nonfill_report(bound_order_resolved=True)
            result = self.inbox.append(receipt_id, key, row, trading_date=trading_date)
        except (NativeBridgeError, ValueError, TypeError, UnicodeError):
            raise ProtectedIntakeError('PROTECTED_INTAKE_RECONCILIATION_REQUIRED') from None
        return self._report(result, bound_order_resolved=True)

    def append_for_bound_order(self, receipt_id, raw_event, *, trading_date):
        """Resolve the immutable local decision key from broker_order_id.

        This avoids trusting a transport caller to route a broker execution to a
        decision key. Known non-fill lifecycle events are ignored by this
        execution-only inbox. Any fill signal continues down the durable,
        fail-closed execution path.
        """
        try:
            with self.inbox.bridge._guard():
                row = self._normalize_locked(raw_event, trading_date)
                key = self._resolve_bound_key_locked(row)
                if not self._has_execution_signal(row):
                    return self._ignored_nonfill_report(bound_order_resolved=True)
            result = self.inbox.append(receipt_id, key, row, trading_date=trading_date)
        except (NativeBridgeError, ValueError, TypeError, UnicodeError):
            raise ProtectedIntakeError('PROTECTED_INTAKE_RECONCILIATION_REQUIRED') from None
        return self._report(result, bound_order_resolved=True)
