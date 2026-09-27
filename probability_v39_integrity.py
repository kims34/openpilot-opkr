"""Integrity diagnostics for the research-only open-aware nowcast."""
import numpy as np
import probability_v39_open_nowcast as v39


def diagnose(opens, raw_closes, validated_closes, dates, target_date):
    opens = np.asarray(opens, float)
    raw = np.asarray(raw_closes, float)
    validated = np.asarray(validated_closes, float)
    if not (len(opens) == len(raw) == len(validated) == len(dates)):
        raise AssertionError('OHLC alignment mismatch')

    # Same Yahoo daily quote basis should agree essentially exactly. A loose
    # tolerance covers serialization only; a corporate-action basis mismatch
    # would be orders of magnitude larger.
    rel = np.abs(raw / validated - 1.0)
    max_close_basis_error = float(np.max(rel))
    if max_close_basis_error > 0.002:
        raise AssertionError(f'raw/validated close basis mismatch: {max_close_basis_error}')

    gaps = opens[1:] / raw[:-1] - 1.0
    finite = gaps[np.isfinite(gaps)]
    max_abs_gap = float(np.max(np.abs(finite)))
    extreme_gap_count = int(np.sum(np.abs(finite) > 0.15))
    if extreme_gap_count:
        raise AssertionError(f'possible split/unit gaps >15%: {extreme_gap_count}, max={max_abs_gap}')

    result = v39.evaluate(opens, validated, dates, target_date)
    if not result.get('holdout_passed'):
        raise AssertionError('primary v3.9 holdout gate no longer passes')

    return {
        'points': len(dates),
        'max_close_basis_error': max_close_basis_error,
        'max_abs_overnight_gap': max_abs_gap,
        'extreme_gap_count': extreme_gap_count,
        'holdout_passed': True,
        'selected': result.get('selected'),
        'test_gain_all': result.get('test_gain_all'),
        'test_gain_first': result.get('test_gain_first'),
        'test_gain_second': result.get('test_gain_second'),
    }
