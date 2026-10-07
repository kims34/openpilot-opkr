import tempfile
import unittest
import json
from pathlib import Path

from kiwoom_type00_frame_extractor import extract_type00_events_json
from kiwoom_protected_execution_intake import ProtectedAccountBinding, KiwoomProtectedExecutionIntake
from kiwoom_execution_inbox import KiwoomExecutionInbox
from kiwoom_order_journal_bridge import KiwoomOrderJournalBridge
from order_intent_journal import OrderIntentJournal

class Type00ProtectedIntakeIntegrationTests(unittest.TestCase):
    def test_extracted_raw_event_reaches_protected_intake_without_live_admission(self):
        with tempfile.TemporaryDirectory() as root:
            journal=OrderIntentJournal(Path(root)/"j.sqlite")
            try:
                journal.register("d",symbol="005930",side="BUY",quantity=1)
                epoch=journal.enable_shadow(expected_epoch=journal.shadow_control()["epoch"])["epoch"]
                journal.claim_submission("d",expected_epoch=epoch)
                journal.bind_acknowledgement("d","o1")
                binding=ProtectedAccountBinding(account="private-account",fingerprint_key=b"k"*32)
                bridge=KiwoomOrderJournalBridge(journal,account_fingerprint=binding.fingerprint,trading_date="2026-10-07")
                bridge.bind_order("d",broker_order_id="o1",native_side="2")
                inbox=KiwoomExecutionInbox(bridge)
                intake=KiwoomProtectedExecutionIntake(inbox,binding)
                frame={"trnm":"REAL","data":[{"type":"00","values":{
                    "9201":"private-account","9203":"o1","9001":"005930","900":"1",
                    "901":"1000","902":"0","904":"","907":"2","908":"091501",
                    "909":"fill-1","910":"1000","911":"1","914":"1000","915":"1",
                    "913":"체결","919":""
                }}]}
                event=extract_type00_events_json(json.dumps(frame).encode('utf-8'))[0]
                out=intake.append("receipt-1","d",event,trading_date="2026-10-07")
                self.assertEqual(out["result"],"RECEIPT_PERSISTED")
                self.assertFalse(out["source_provenance_admitted"])
                self.assertFalse(out["live_ordering_authorized"])
                self.assertEqual(inbox.counts()["pending"],1)
            finally:
                journal.close()

if __name__=="__main__": unittest.main()
