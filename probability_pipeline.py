"""Nonblocking probability responses with one coalesced background worker.

Only timing-specific overlays are cached. The daily probability and its live
gate always come from the current base payload. A new target, base revision,
session boundary or expired overlay cache suppresses old overlays immediately.
"""
import copy
import threading
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

US_IDS = ("sp500", "ndx", "djdiv")
LAYERS = ("preopen_futures", "extended_session", "after_open", "first_hour")
VERSIONS = {
    "preopen_futures": "3.12-preopen-futures",
    "extended_session": "4.1-extended-session",
    "after_open": "3.9-open-nowcast",
    "first_hour": "4.0-first-hour",
}


class ProbabilityPipeline:
    def __init__(self, base_supplier, enrichers, clock=time.time, refresh_seconds=30, max_age=120):
        self.base_supplier = base_supplier
        self.enrichers = tuple(enrichers)
        self.clock = clock
        self.refresh_seconds = refresh_seconds
        self.max_age = max_age
        self.lock = threading.Lock()
        self.running = False
        self.cached = None
        self.cached_key = None
        self.completed = 0.0
        self.last_attempt = float("-inf")
        self.attempt_key = None

    @staticmethod
    def key(payload, now):
        rows = []
        for index_id in US_IDS:
            row = (payload.get("items") or {}).get(index_id) or {}
            op, cl = int(row.get("target_open") or 0), int(row.get("target_close") or 0)
            boundaries = (op-25*60, op, op+5*60, op+65*60, cl)
            phase = sum(now >= point for point in boundaries) if op and cl else -1
            rows.append((index_id, row.get("as_of"), row.get("target_date"),
                         row.get("data_digest"), row.get("probability"), op, cl, phase))
        seoul = datetime.fromtimestamp(now, timezone.utc).astimezone(ZoneInfo("Asia/Seoul"))
        minute = seoul.hour*60 + seoul.minute
        return (tuple(rows), seoul.date().isoformat(), minute >= 9*60, minute >= 15*60+30)

    @staticmethod
    def waiting(payload):
        out = copy.deepcopy(payload)
        out.update(preopen_futures_model=VERSIONS["preopen_futures"],
                   preopen_futures_baseline_model="3.2-live-guardrails:fixed-base-rate",
                   extended_session_model_version=VERSIONS["extended_session"],
                   after_open_model_version=VERSIONS["after_open"],
                   first_hour_model_version=VERSIONS["first_hour"])
        for index_id in US_IDS:
            item = out.setdefault("items", {}).setdefault(index_id, {})
            op = int(item.get("target_open") or 0)
            for layer in LAYERS:
                item[layer] = {"available": False, "model_version": VERSIONS[layer],
                               "target_date": item.get("target_date"), "status": "시장 데이터 갱신 중"}
            item["after_open"]["available_from"] = op + 5*60 if op else None
            item["first_hour"]["available_from"] = op + 65*60 if op else None
        return out

    def _build(self, payload, key):
        try:
            result = copy.deepcopy(payload)
            for enrich in self.enrichers:
                result = enrich(result)
            completed = self.clock()
            # Do not publish work that straddled a market timing boundary.
            if self.key(result, completed) == key:
                with self.lock:
                    self.cached = copy.deepcopy(result)
                    self.cached_key = key
                    self.completed = completed
        except Exception as exc:
            print("probability pipeline refresh failed", type(exc).__name__, flush=True)
        finally:
            with self.lock:
                self.running = False

    def get(self):
        payload = self.base_supplier()
        now = self.clock()
        key = self.key(payload, now)
        ready = all(not ((payload.get("items") or {}).get(i) or {}).get("error")
                    and ((payload.get("items") or {}).get(i) or {}).get("target_open")
                    for i in US_IDS)
        with self.lock:
            usable = self.cached_key == key and self.cached is not None and 0 <= now-self.completed <= self.max_age
            cached = copy.deepcopy(self.cached) if usable else None
            completed = self.completed if usable else None
            launch = ready and not self.running and (key != self.attempt_key or now-self.last_attempt >= self.refresh_seconds)
            if launch:
                self.running = True
                self.last_attempt = now
                self.attempt_key = key
        if launch:
            threading.Thread(target=self._build, args=(payload, key), daemon=True).start()
        out = self.waiting(payload)
        if cached is not None:
            for index_id, item in (cached.get("items") or {}).items():
                if index_id not in US_IDS:
                    # KOSPI is supplied by the extended-session layer.
                    if item.get("valid_until", now+1) > now:
                        out["items"][index_id] = item
                    continue
                for layer in LAYERS:
                    if layer in item:
                        out["items"][index_id][layer] = item[layer]
        out["pipeline_status"] = "ready" if cached is not None else "refreshing"
        out["pipeline_updated_at"] = completed
        return out


def install_scheduler(scheduler, pipeline):
    """Keep prospective recording active even when no phone is querying."""
    if not scheduler.get_job("probability-pipeline-refresh"):
        scheduler.add_job(pipeline.get, "interval", seconds=60,
                          id="probability-pipeline-refresh", max_instances=1, coalesce=True)
