import open_nowcast_v39 as mod


def _item(open_ts=1_000, close_ts=2_000):
    return {
        "symbol": "SPY",
        "as_of": "2026-09-25",
        "target_date": "2026-09-28",
        "target_open": open_ts,
        "target_close": close_ts,
        "data_digest": "abc",
        "probability": 54.0,
    }


def test_never_available_before_open_grace():
    out = mod.estimate("SPY", _item(), now=1_299)
    assert out["available"] is False
    assert "5분" in out["status"]


def test_unavailable_after_close():
    out = mod.estimate("SPY", _item(), now=2_000)
    assert out["available"] is False
    assert "종료" in out["status"]


def test_target_close_value_is_not_used(monkeypatch):
    mod.CACHE.clear()
    completed = [("2026-09-24", 98.0), ("2026-09-25", 100.0)]
    monkeypatch.setattr(
        mod.base,
        "fetch_history",
        lambda symbol, now=None: (
            completed,
            {"target_date": "2026-09-28"},
        ),
    )
    # Deliberately absurd target-day close. If runtime ever touches it, this
    # test should fail through basis/gap contamination. Only target open=101 is allowed.
    monkeypatch.setattr(
        mod,
        "_daily_ohlc",
        lambda symbol: {
            "2026-09-24": {"open": 97.0, "close": 98.0},
            "2026-09-25": {"open": 99.0, "close": 100.0},
            "2026-09-28": {"open": 101.0, "close": 999999.0},
        },
    )
    seen = {}
    def fake_fit(opens, closes, dates, target_date, target_open, preopen_probability, config):
        seen["target_open"] = target_open
        seen["closes"] = list(closes)
        return {
            "probability": 61.0,
            "preopen_probability": 54.0,
            "adjustment_pp": 7.0,
            "opening_gap_percent": 1.0,
            "training_count": 500,
        }
    monkeypatch.setattr(mod, "_fit_live", fake_fit)
    monkeypatch.setattr(mod, "_score_and_record", lambda symbol, item, result, rows, now: result)

    out = mod.estimate("SPY", _item(), now=1_500)
    assert out["available"] is True
    assert seen["target_open"] == 101.0
    assert seen["closes"] == [98.0, 100.0]
    assert out["probability"] == 61.0


def test_live_gap_guard():
    closes = [100, 101, 102, 103, 104, 105]
    x = mod._live_feature(106.0, closes)
    assert abs(x[0] - (106.0 / 105.0 - 1.0)) < 1e-12
