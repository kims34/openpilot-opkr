"""App-native milestone notification for prospective probability validation.

This module compares the deployed model with frozen shadow challengers only on
matching, prospectively-recorded sessions.  Once every challenger has at least
60 matched outcomes for SPY, QQQ and SCHD, IndexAlert sends a durable one-time
FCM notification per registered device.  ChatGPT is not involved.
"""
import json
import os
import sqlite3
import time

import firebase_admin
from firebase_admin import credentials, messaging

from probability_shadow import SHADOW_MODELS

SYMBOLS = ("SPY", "QQQ", "SCHD")
THRESHOLD = 60


def _table_exists(con, name):
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def build_comparison(db_path, model_version, threshold=THRESHOLD):
    """Return a fair matched-session comparison of v3.1 and each shadow model."""
    with sqlite3.connect(db_path, timeout=10) as con:
        if not _table_exists(con, "probability_forecasts") or not _table_exists(
            con, "probability_shadow_forecasts"
        ):
            return {"ready": False, "threshold": threshold, "min_count": 0, "models": {}}

        rows = con.execute(
            """SELECT s.model,s.symbol,b.p,b.outcome,s.p,s.outcome
               FROM probability_shadow_forecasts s
               JOIN probability_forecasts b
                 ON b.symbol=s.symbol AND b.as_of=s.as_of
               WHERE b.model=? AND b.outcome IS NOT NULL AND s.outcome IS NOT NULL
               ORDER BY s.model,s.symbol,s.as_of""",
            (model_version,),
        ).fetchall()

    grouped = {}
    mismatch = 0
    for shadow_model, symbol, base_p, base_y, shadow_p, shadow_y in rows:
        if shadow_model not in SHADOW_MODELS or symbol not in SYMBOLS:
            continue
        if int(base_y) != int(shadow_y):
            mismatch += 1
            continue
        key = (shadow_model, symbol)
        item = grouped.setdefault(key, {"count": 0, "base_sse": 0.0, "shadow_sse": 0.0})
        y = int(base_y)
        item["count"] += 1
        item["base_sse"] += (float(base_p) - y) ** 2
        item["shadow_sse"] += (float(shadow_p) - y) ** 2

    models = {}
    counts = []
    for shadow_model in SHADOW_MODELS:
        per_symbol = {}
        total_n = 0
        total_base_sse = 0.0
        total_shadow_sse = 0.0
        wins = 0
        for symbol in SYMBOLS:
            item = grouped.get((shadow_model, symbol), {"count": 0, "base_sse": 0.0, "shadow_sse": 0.0})
            n = int(item["count"])
            counts.append(n)
            total_n += n
            total_base_sse += item["base_sse"]
            total_shadow_sse += item["shadow_sse"]
            base_brier = item["base_sse"] / n if n else None
            shadow_brier = item["shadow_sse"] / n if n else None
            improved = bool(n and shadow_brier < base_brier)
            wins += int(improved)
            per_symbol[symbol] = {
                "count": n,
                "base_brier": base_brier,
                "shadow_brier": shadow_brier,
                "improved": improved,
            }
        models[shadow_model] = {
            "count": total_n,
            "base_brier": total_base_sse / total_n if total_n else None,
            "shadow_brier": total_shadow_sse / total_n if total_n else None,
            "improved_symbols": wins,
            "symbols": per_symbol,
        }

    min_count = min(counts) if counts else 0
    ready = bool(models) and min_count >= threshold and mismatch == 0
    ranked = sorted(
        (
            (name, values)
            for name, values in models.items()
            if values["shadow_brier"] is not None and values["base_brier"] is not None
        ),
        key=lambda pair: pair[1]["shadow_brier"],
    )
    best_name, best = ranked[0] if ranked else (None, None)
    eligible = bool(
        ready
        and best
        and best["shadow_brier"] < best["base_brier"]
        and best["improved_symbols"] >= 2
    )
    verdict = "shadow_improved" if eligible else "keep_3_1"
    return {
        "ready": ready,
        "threshold": threshold,
        "min_count": min_count,
        "outcome_mismatches": mismatch,
        "model_version": model_version,
        "best_candidate": best_name,
        "verdict": verdict,
        "models": models,
    }


def _init_firebase():
    if firebase_admin._apps:
        return True
    raw = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        return False
    try:
        firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)))
        return True
    except Exception as exc:
        print("probability milestone firebase init failed", type(exc).__name__, flush=True)
        return False


def _notification_text(report):
    best_name = report.get("best_candidate")
    best = (report.get("models") or {}).get(best_name) or {}
    if report.get("verdict") == "shadow_improved":
        body = (
            f"3.1 Brier {best['base_brier']:.4f} → {best_name} {best['shadow_brier']:.4f} · "
            f"{best['improved_symbols']}/3 지수 개선. 자동 승격 없이 검증 결과만 알립니다."
        )
    else:
        if best and best.get("base_brier") is not None:
            body = (
                f"동일 실전 구간에서 3.1 Brier {best['base_brier']:.4f}, 최저 Shadow "
                f"{best_name} {best['shadow_brier']:.4f}. 3.1을 유지합니다."
            )
        else:
            body = "실전 예측 60회 비교가 완료됐습니다. 현재 3.1을 유지합니다."
    return "IndexAlert 실전 예측 60회 검증 완료", body


def _send_message(token, protocol, title, body, data):
    message = messaging.Message(
        token=token,
        notification=None if int(protocol or 1) >= 2 else messaging.Notification(title=title, body=body),
        data=data,
        android=messaging.AndroidConfig(priority="high", ttl=3600),
    )
    return messaging.send(message)


def maybe_notify(db_path, model_version, now=None, threshold=THRESHOLD):
    """Send the milestone through IndexAlert itself, once per registered device."""
    now = time.time() if now is None else float(now)
    report = build_comparison(db_path, model_version, threshold)
    if not report["ready"]:
        return {
            "ready": False,
            "threshold": threshold,
            "min_count": report["min_count"],
        }

    event_id = f"probability:{model_version}:prospective-{threshold}"
    title, body = _notification_text(report)
    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":"))

    with sqlite3.connect(db_path, timeout=10) as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS probability_milestone_deliveries(
                event_id TEXT NOT NULL,
                token TEXT NOT NULL,
                created REAL NOT NULL,
                sent INTEGER NOT NULL DEFAULT 0,
                sent_at REAL,
                payload TEXT NOT NULL,
                PRIMARY KEY(event_id,token)
            )"""
        )
        if not _table_exists(con, "devices"):
            return {"ready": True, "threshold": threshold, "min_count": report["min_count"], "sent": 0, "pending": 0}
        devices = con.execute("SELECT token,COALESCE(protocol,1) FROM devices").fetchall()
        con.executemany(
            "INSERT OR IGNORE INTO probability_milestone_deliveries(event_id,token,created,payload) VALUES(?,?,?,?)",
            [(event_id, token, now, payload) for token, _ in devices],
        )
        con.commit()
        pending = con.execute(
            """SELECT m.token,COALESCE(d.protocol,1)
               FROM probability_milestone_deliveries m
               JOIN devices d ON d.token=m.token
               WHERE m.event_id=? AND m.sent=0""",
            (event_id,),
        ).fetchall()

    if not pending or not _init_firebase():
        return {
            "ready": True,
            "threshold": threshold,
            "min_count": report["min_count"],
            "sent": 0,
            "pending": len(pending),
            "verdict": report["verdict"],
        }

    best_name = report.get("best_candidate") or ""
    best = (report.get("models") or {}).get(best_name) or {}
    data = {
        "message_id": event_id,
        "event_id": event_id,
        "event_type": "probability_milestone",
        "title": title,
        "body": body,
        "milestone": str(threshold),
        "model_version": model_version,
        "verdict": str(report.get("verdict") or ""),
        "best_candidate": best_name,
        "base_brier": "" if best.get("base_brier") is None else f"{best['base_brier']:.8f}",
        "candidate_brier": "" if best.get("shadow_brier") is None else f"{best['shadow_brier']:.8f}",
        "improved_symbols": str(best.get("improved_symbols", 0)),
        "sent_at": str(now),
    }
    sent = 0
    for token, protocol in pending:
        try:
            _send_message(token, protocol, title, body, data)
            with sqlite3.connect(db_path, timeout=10) as con:
                con.execute(
                    "UPDATE probability_milestone_deliveries SET sent=1,sent_at=? WHERE event_id=? AND token=?",
                    (time.time(), event_id, token),
                )
            sent += 1
        except messaging.UnregisteredError:
            with sqlite3.connect(db_path, timeout=10) as con:
                con.execute("DELETE FROM devices WHERE token=?", (token,))
                con.execute(
                    "UPDATE probability_milestone_deliveries SET sent=1,sent_at=? WHERE event_id=? AND token=?",
                    (time.time(), event_id, token),
                )
        except Exception as exc:
            print("probability milestone FCM retry pending", type(exc).__name__, flush=True)

    with sqlite3.connect(db_path, timeout=10) as con:
        remaining = con.execute(
            "SELECT COUNT(*) FROM probability_milestone_deliveries WHERE event_id=? AND sent=0",
            (event_id,),
        ).fetchone()[0]
    return {
        "ready": True,
        "threshold": threshold,
        "min_count": report["min_count"],
        "sent": sent,
        "pending": int(remaining),
        "verdict": report["verdict"],
        "best_candidate": best_name,
    }
