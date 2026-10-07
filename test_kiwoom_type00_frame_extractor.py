import unittest
import json
from kiwoom_type00_frame_extractor import (
    KiwoomType00FrameError, extract_type00_events, summarize_type00_frame,
    extract_type00_events_json, MAX_FRAME_BYTES,
)

class KiwoomType00FrameExtractorTests(unittest.TestCase):
    def test_serialized_utf8_preserves_fid_strings_without_source_admission(self):
        message = {'trnm':'REAL','data':[{'type':'00','values':{'909':'0001','913':'체결'}}]}
        payload = json.dumps(message,ensure_ascii=False)
        for raw in (payload,payload.encode('utf-8')):
            self.assertEqual(extract_type00_events_json(raw), ({'909':'0001','913':'체결'},))
        self.assertFalse(summarize_type00_frame(message)['genuine_live_provenance_verified'])

    def test_serialized_ambiguity_non_json_and_resource_limits_are_private(self):
        for raw in ('{"trnm":"REG","trnm":"REAL","data":[]}',
                    '{"trnm":"REAL","data":[{"type":"00","values":{"909":"first","909":"last"}}]}',
                    '{"trnm":"REAL","data":[],"extra":NaN}',
                    '{"trnm":"REAL","data":[],"extra":Infinity}',
                    '['*2000+'0'+']'*2000,
                    ' '* (MAX_FRAME_BYTES+1),
                    '한'*(MAX_FRAME_BYTES//3+1), b'\xff', '{', None):
            with self.subTest(kind=type(raw).__name__):
                with self.assertRaisesRegex(KiwoomType00FrameError, '^TYPE00_JSON_INVALID$'):
                    extract_type00_events_json(raw)

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
