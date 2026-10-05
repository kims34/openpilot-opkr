"""Bind a broker account snapshot to journal/capital state without crediting cash.

This is offline validation only. A passing binding proves internal consistency
of already-captured evidence; it never authenticates account origin, releases
capital, credits sale proceeds, enables SHADOW, or authorizes an order.
"""
import json
from order_intent_journal import OrderJournalError
from kiwoom_account_settlement_evidence import SettlementEvidenceError

class AccountSettlementBinder:
    def __init__(self,journal,allocator):
        self.journal=journal; self.allocator=allocator
        with journal._atomic():
            journal.db.execute("""CREATE TABLE IF NOT EXISTS account_settlement_bindings(
              snapshot_sha256 TEXT PRIMARY KEY, capital_revision INTEGER NOT NULL,
              payload TEXT NOT NULL)""")

    def bind(self,snapshot,*,expected_capital_revision,expected_epoch):
        if not isinstance(snapshot,dict) or snapshot.get("settlement_admitted") is not False:
            raise SettlementEvidenceError("UNADMITTED_SETTLEMENT_SNAPSHOT")
        if snapshot.get("sale_proceeds_reusable") is not False:
            raise SettlementEvidenceError("SALE_PROCEEDS_MUST_REMAIN_LOCKED")
        with self.journal._atomic():
            self.journal._check_epoch(expected_epoch)
            self.journal._require_batch_reconciled()
            state=self.allocator._revision(expected_capital_revision)
            # Compare broker positions to journal filled BUY quantities only for
            # symbols managed by this journal. Aggregate broker rows cannot
            # manufacture executions and manual/pre-existing holdings are not
            # silently opted into automation.
            managed={}
            for key,side,symbol in self.journal.db.execute("SELECT key,side,symbol FROM intents"):
                if side!="BUY": continue
                order=self.journal.get(key)
                if order["filled_quantity"]:
                    managed[symbol]=managed.get(symbol,0)+order["filled_quantity"]
            broker={p["symbol"]:p["quantity"] for p in snapshot.get("positions",[])}
            mismatches={s:(q,broker.get(s)) for s,q in managed.items() if broker.get(s)!=q}
            if mismatches:
                self.journal.db.execute("UPDATE reconciliation_barrier SET blocked=1 WHERE id=1")
                self.journal.db.execute("DELETE FROM reconciled_snapshot_bindings")
                self.journal._stop_shadow("ACCOUNT_SETTLEMENT_POSITION_MISMATCH")
                raise OrderJournalError("account settlement position mismatch")
            digest=snapshot.get("snapshot_sha256")
            if not isinstance(digest,str) or len(digest)!=64:
                raise SettlementEvidenceError("INVALID_SETTLEMENT_DIGEST")
            payload=json.dumps({"managed_symbols":len(managed),"broker_positions":len(broker)},
                sort_keys=True,separators=(",",":"))
            old=self.journal.db.execute("SELECT capital_revision,payload FROM account_settlement_bindings WHERE snapshot_sha256=?",(digest,)).fetchone()
            if old is not None and old!=(state["revision"],payload):
                raise OrderJournalError("settlement snapshot binding conflict")
            self.journal.db.execute("INSERT OR IGNORE INTO account_settlement_bindings VALUES(?,?,?)",
                (digest,state["revision"],payload))
        return {"mode":"OFFLINE_ACCOUNT_SETTLEMENT_BINDING","position_match":True,
          "capital_released":False,"sale_proceeds_credited":False,
          "account_origin_verified":False,"live_ordering_authorized":False}
