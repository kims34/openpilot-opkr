import unittest
from kiwoom_type00_frame_extractor import (
    KiwoomType00FrameError, extract_type00_events, summarize_type00_frame,
)

class KiwoomType00FrameExtractorTests(unittest.TestCase):
    def test_extracts_only_raw_type00_values(self):
        msg={"trnm":"REAL","data":[
            {"type":"0B","item":"005930","values":{"10":"1000"}},
            {"type":"00","item":"","values":{
                "9201":"private","9203":"0000001","913":"체결","908":"091501",
                "909":"fill-1","914":"1000","915":"1"
            }},
        ]}
        rows=extract_type00_events(msg)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["909"],"fill-1")
        self.assertNotIn("item",rows[0])
        report=summarize_type00_frame(msg)
        self.assertEqual(report["execution_id_present_count"],1)
        self.assertFalse(report["broker_native_execution_id_capture_tested"])

    def test_empty_valid_frame_is_not_evidence(self):
        out=summarize_type00_frame({"trnm":"REAL","data":[]})
        self.assertEqual(out["type00_event_count"],0)
        self.assertFalse(out["source_origin_authenticated"])
        self.assertFalse(out["genuine_live_provenance_verified"])

    def test_control_or_malformed_frames_fail_closed(self):
        for msg in (
            {"trnm":"REG","data":[]},
            {"trnm":"REAL","data":{}},
            {"trnm":"REAL","data":[None]},
            {"trnm":"REAL","data":[{"type":"00","values":[]}]}):
            with self.assertRaises(KiwoomType00FrameError):
                extract_type00_events(msg)

    def test_unknown_fid_and_nonstring_value_rejected(self):
        with self.assertRaises(KiwoomType00FrameError):
            extract_type00_events({"trnm":"REAL","data":[{"type":"00","values":{"999999":"x"}}]})
        with self.assertRaises(KiwoomType00FrameError):
            extract_type00_events({"trnm":"REAL","data":[{"type":"00","values":{"909":1}}]})

    def test_input_is_not_mutated(self):
        msg={"trnm":"REAL","data":[{"type":"00","values":{"909":"e1"}}]}
        before=repr(msg)
        rows=extract_type00_events(msg)
        rows[0]["909"]="changed"
        self.assertEqual(repr(msg),before)

if __name__=="__main__": unittest.main()
