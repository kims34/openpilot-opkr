"""IndexAlert KOSPI full research v1 using FinanceData/marcap PIT files.

The marcap repository stores daily KRX cross-sections by year and therefore
lets us reconstruct the dated KOSPI universe without relying on today's members
or on a live KRX login.  This runner loads only rows that actually existed on
each date, writes them into the research SQLite store, then runs both the simple
baseline tournament and the regularized logistic walk-forward tournament.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import time
from datetime import datetime

import pandas as pd

import research_kospi_baseline as base
import research_kospi_model_v1 as model

SOURCE = "FinanceData/marcap (KRX daily cross-sections)"
SCHEMA = "kospi-pit-marcap-v1"


def _norm_code(x):
    s = str(x).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s.zfill(6)


def _find_year_file(marcap_dir: str, year: int) -> str:
    candidates = [
        os.path.join(marcap_dir, f"marcap-{year}.csv.gz"),
        os.path.join(marcap_dir, f"marcap-{year}.csv"),
        os.path.join(marcap_dir, f"marcap-{year}.parquet"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    hits = sorted(glob.glob(os.path.join(marcap_dir, f"*{year}*")))
    if hits:
        return hits[0]
    raise FileNotFoundError(f"marcap yearly file not found: {year} in {marcap_dir}")


def _read_year(path: str) -> pd.DataFrame:
    if path.endswith('.parquet'):
        return pd.read_parquet(path)
    return pd.read_csv(path, dtype={"Code": str})


def _column(df, *names):
    for n in names:
        if n in df.columns:
            return n
    raise KeyError(f"missing columns, expected one of {names}")


def load_marcap(from_date: str, to_date: str, marcap_dir: str, store: base.ResearchStore):
    start = pd.Timestamp(base._ymd(from_date))
    end = pd.Timestamp(base._ymd(to_date))
    years = range(start.year, end.year + 1)
    written_days = 0
    total_rows = 0

    for year in years:
        path = _find_year_file(marcap_dir, year)
        df = _read_year(path)
        date_col = _column(df, "Date", "date")
        market_col = _column(df, "Market", "market")
        code_col = _column(df, "Code", "code")
        open_col = _column(df, "Open", "open")
        high_col = _column(df, "High", "high")
        low_col = _column(df, "Low", "low")
        close_col = _column(df, "Close", "close")
        vol_col = _column(df, "Volume", "volume")
        amount_col = _column(df, "Amount", "amount")

        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df[(df[date_col] >= start) & (df[date_col] <= end)]
        df = df[df[market_col].astype(str).str.upper().eq("KOSPI")]
        if df.empty:
            continue

        numeric_cols = [open_col, high_col, low_col, close_col, vol_col, amount_col]
        for c in numeric_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna(subset=[date_col, code_col] + numeric_cols)

        for d, g in df.groupby(date_col, sort=True):
            trade_date = pd.Timestamp(d).strftime("%Y%m%d")
            bars = []
            for _, r in g.iterrows():
                try:
                    o = float(r[open_col]); h = float(r[high_col]); l = float(r[low_col]); c = float(r[close_col])
                    v = float(r[vol_col]); a = float(r[amount_col])
                    if not all(math.isfinite(x) for x in (o, h, l, c, v, a)):
                        continue
                    # Keep only actually tradable rows for selection. Zero-volume suspended
                    # rows remain absent from that day's candidate set by design.
                    if o <= 0 or c <= 0 or a <= 0:
                        continue
                    if not (l <= o <= h and l <= c <= h):
                        continue
                    bars.append(base.Bar(_norm_code(r[code_col]), o, h, l, c, v, a))
                except Exception:
                    continue
            if len(bars) < 100:
                continue

            now = time.time()
            with store.con:
                store.con.execute("DELETE FROM research_daily_ohlcv WHERE trade_date=?", (trade_date,))
                store.con.executemany(
                    "INSERT INTO research_daily_ohlcv VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    [(trade_date, b.ticker, b.open, b.high, b.low, b.close, b.volume, b.value,
                      SOURCE, SCHEMA, now) for b in bars],
                )
                store.con.execute(
                    "INSERT INTO research_daily_meta(trade_date,row_count,source,schema_version,ingested_at) "
                    "VALUES(?,?,?,?,?) ON CONFLICT(trade_date) DO UPDATE SET "
                    "row_count=excluded.row_count,source=excluded.source,schema_version=excluded.schema_version,ingested_at=excluded.ingested_at",
                    (trade_date, len(bars), SOURCE, SCHEMA, now),
                )
            written_days += 1
            total_rows += len(bars)

        print("marcap-year", {"year": year, "path": path, "written_days": written_days, "rows": total_rows}, flush=True)

    days = [
        r[0] for r in store.con.execute(
            "SELECT trade_date FROM research_daily_meta WHERE trade_date>=? AND trade_date<=? ORDER BY trade_date",
            (base._ymd(from_date), base._ymd(to_date)),
        ).fetchall()
    ]
    if len(days) < 35:
        raise RuntimeError(f"insufficient stored trading days: {len(days)}")
    return days, {"source": SOURCE, "schema": SCHEMA, "written_days": written_days, "rows": total_rows}


def run(from_date: str, to_date: str, marcap_dir: str, db_path: str):
    store = base.ResearchStore(db_path)
    days, build = load_marcap(from_date, to_date, marcap_dir, store)

    baseline_result = base.backtest(days, store)
    baseline_result.update({
        "from_date": base._ymd(from_date),
        "to_date": base._ymd(to_date),
        "trading_days": len(days),
        "data_build": build,
        "created_at": datetime.utcnow().isoformat() + "Z",
    })

    observations = model.build_observations(days, store)
    model_result = model.walk_forward(days, observations)
    model_result.update({
        "market": "KOSPI",
        "from_date": base._ymd(from_date),
        "to_date": base._ymd(to_date),
        "trading_days": len(days),
        "observation_rows": len(observations),
        "feature_version": model.FEATURE_VERSION,
        "feature_names": list(model.FEATURE_NAMES),
        "model_version": model.MODEL_VERSION,
        "train_days": model.TRAIN_DAYS,
        "test_days": model.TEST_DAYS,
        "purge_days": model.PURGE_DAYS,
        "top_k": model.TOP_K,
        "base_label_cost": model.BASE_COST,
        "cost_scenarios": base.COST_SCENARIOS,
        "data_build": build,
        "created_at": datetime.utcnow().isoformat() + "Z",
    })

    return {
        "research_version": "indexalert-kospi-full-v1",
        "data_source": SOURCE,
        "from_date": base._ymd(from_date),
        "to_date": base._ymd(to_date),
        "trading_days": len(days),
        "baseline": baseline_result,
        "model_tournament": model_result,
        "status": "PRELIMINARY_RESEARCH_ONLY",
        "profitability_validated": False,
        "validation_note": (
            "Actual historical PIT-like KOSPI cross-sections are tested here, but profitability is not promoted to validated "
            "until transaction costs are replaced by broker/quote-derived estimates, corporate actions are reconstructed, "
            "and sealed holdout + shadow phases pass."
        ),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--from-date", default="20180102")
    p.add_argument("--to-date", default="20260925")
    p.add_argument("--marcap-dir", required=True)
    p.add_argument("--db", default="/tmp/indexalert-research.sqlite")
    p.add_argument("--output", default="research_results/kospi_full_v1.json")
    args = p.parse_args()
    payload = run(args.from_date, args.to_date, args.marcap_dir, args.db)
    text = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
