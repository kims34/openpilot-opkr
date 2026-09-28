"""Heuristic security-scope diagnostics for IndexAlert Research v1.

This module is intentionally *not* an identity authority.  The PIT marcap source
contains daily KOSPI membership but no validated common/preferred share-class
field.  These flags are used only for challenger diagnostics until an official
security master is joined point-in-time.

Policy goals:
- never mark the dataset Judge-eligible from this heuristic;
- preserve each component flag so disagreements are visible;
- avoid treating REIT-like names as non-common solely because of their business
  type; this module only tries to identify preferred-share-like securities.
"""
from __future__ import annotations

import re

import pandas as pd

# Common Korean preferred-share code convention.  This is a research heuristic,
# not an official security-master classification.
_PREFERRED_CODE_SUFFIXES = frozenset({"5", "7", "9", "K", "L"})

# Strong name forms are much less likely to collide with an ordinary company
# whose legal name simply ends in the Hangul syllable "우".
_STRONG_PREFERRED_NAME_RE = re.compile(
    r"(?:[1-9]\d*우(?:B|C)?|우B|우C|우선주)$",
    re.IGNORECASE,
)
_PLAIN_U_SUFFIX_RE = re.compile(r"우$", re.IGNORECASE)


def _normalise_symbol(value) -> str:
    s = "" if pd.isna(value) else str(value).strip().upper()
    if s.endswith(".0"):
        s = s[:-2]
    return s.zfill(6) if s.isdigit() else s


def _normalise_name(value) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", "", str(value).strip())


def apply_common_like_heuristic(panel: pd.DataFrame) -> pd.DataFrame:
    """Attach preferred/common-like diagnostic flags without claiming validation.

    `preferred_like_heuristic` is deliberately conservative:
    - preferred-looking code suffix, OR
    - a strong preferred-share name form (e.g. 2우B / 우B / 우선주).

    A plain name ending only in `우` is recorded separately but does not exclude a
    security by itself, because ordinary company names can also end in that
    syllable.  When the code also looks preferred, the code rule already excludes
    it.  This favors false negatives over false exclusion of ordinary shares.
    """
    required = {"symbol", "name"}
    missing = required.difference(panel.columns)
    if missing:
        raise ValueError(f"security-scope heuristic requires {sorted(missing)}")

    x = panel.copy()
    symbols = x["symbol"].map(_normalise_symbol)
    names = x["name"].map(_normalise_name)

    x["preferred_by_code_heuristic"] = symbols.str[-1:].isin(_PREFERRED_CODE_SUFFIXES)
    x["preferred_by_name_strong_heuristic"] = names.map(
        lambda s: bool(_STRONG_PREFERRED_NAME_RE.search(s))
    )
    x["preferred_by_name_plain_u_hint"] = names.map(
        lambda s: bool(_PLAIN_U_SUFFIX_RE.search(s))
    )

    x["preferred_like_heuristic"] = (
        x["preferred_by_code_heuristic"]
        | x["preferred_by_name_strong_heuristic"]
    )
    x["common_like_heuristic"] = ~x["preferred_like_heuristic"]
    x["security_scope_identity_validated"] = False
    x["security_scope_policy"] = "HEURISTIC_DIAGNOSTIC_ONLY__NOT_SECURITY_MASTER"
    return x


def common_like_diagnostics(tagged: pd.DataFrame) -> dict:
    """Summarize heuristic scope and disagreement rates for auditability."""
    required = {
        "symbol", "preferred_by_code_heuristic",
        "preferred_by_name_strong_heuristic", "preferred_by_name_plain_u_hint",
        "preferred_like_heuristic", "common_like_heuristic",
    }
    missing = required.difference(tagged.columns)
    if missing:
        raise ValueError(f"tagged panel missing {sorted(missing)}")

    # Count unique securities as well as rows so a long-lived preferred share is
    # not mistaken for many independent classification events.
    latest = (
        tagged.sort_values("decision_date")
        .drop_duplicates("symbol", keep="last")
        if "decision_date" in tagged.columns else tagged.drop_duplicates("symbol")
    )
    code = latest["preferred_by_code_heuristic"].astype(bool)
    strong = latest["preferred_by_name_strong_heuristic"].astype(bool)
    plain = latest["preferred_by_name_plain_u_hint"].astype(bool)
    pref = latest["preferred_like_heuristic"].astype(bool)

    return {
        "policy": "HEURISTIC_DIAGNOSTIC_ONLY__NOT_SECURITY_MASTER",
        "judge_identity_validated": False,
        "rows": int(len(tagged)),
        "unique_symbols": int(tagged["symbol"].nunique()),
        "common_like_rows": int(tagged["common_like_heuristic"].astype(bool).sum()),
        "preferred_like_rows": int(tagged["preferred_like_heuristic"].astype(bool).sum()),
        "common_like_unique_symbols": int((~pref).sum()),
        "preferred_like_unique_symbols": int(pref.sum()),
        "code_preferred_unique_symbols": int(code.sum()),
        "strong_name_preferred_unique_symbols": int(strong.sum()),
        "plain_u_name_hint_unique_symbols": int(plain.sum()),
        "code_only_unique_symbols": int((code & ~strong).sum()),
        "strong_name_only_unique_symbols": int((~code & strong).sum()),
        "code_and_strong_name_unique_symbols": int((code & strong).sum()),
        "plain_u_hint_without_code_unique_symbols": int((plain & ~code).sum()),
        "warning": (
            "Common-like is a conservative preferred-share heuristic only. "
            "Do not use it to set common_stock_identity_validated=True."
        ),
    }


def filter_common_like_heuristic(panel: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    tagged = apply_common_like_heuristic(panel)
    diag = common_like_diagnostics(tagged)
    return tagged[tagged["common_like_heuristic"]].copy(), diag
