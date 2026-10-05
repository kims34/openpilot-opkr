"""Offline materialization of cleanup-trading and delisting events from frozen private identity evidence.

Reads only already-acquired private identity seed material. No network access,
recovery inference, fill inference, holdout access, or authority changes.
"""
from __future__ import annotations
import pandas as pd
from research_v1_krx_historical_identity_materializer import load_identity_seed_material, reconstruct_private_historical_episodes
from research_v1_krx_historical_batch_orchestrator import _history_date, _history_short_code

class KRXPrivateTerminalStatusError(ValueError):
    pass

def materialize_private_terminal_status(root: str, *, git_worktree: str|None=None) -> tuple[pd.DataFrame,pd.DataFrame]:
    seed=load_identity_seed_material(root,git_worktree=git_worktree)
    episodes=reconstruct_private_historical_episodes(root,git_worktree=git_worktree)
    hist=seed["delisted_history"]
    required={"종목코드","상장일","폐지일","정리매매기간_시작일","정리매매기간_종료일"}
    missing=required-set(hist.columns)
    if missing: raise KRXPrivateTerminalStatusError(f"delisted history missing columns: {sorted(missing)}")
    by_key={}
    for row in hist.to_dict("records"):
        try: code=_history_short_code(row["종목코드"])
        except Exception: continue
        listing=_history_date(row["상장일"]); delisting=_history_date(row["폐지일"])
        if listing is None or delisting is None: continue
        key=(code,listing)
        if key in by_key: raise KRXPrivateTerminalStatusError("duplicate delisted-history episode")
        cs=_history_date(row["정리매매기간_시작일"]); ce=_history_date(row["정리매매기간_종료일"])
        if (cs is None)!=(ce is None): raise KRXPrivateTerminalStatusError("partial cleanup interval")
        if cs is not None and (ce<cs or delisting<ce): raise KRXPrivateTerminalStatusError("invalid cleanup/delisting chronology")
        by_key[key]=(delisting,cs,ce)
    cleanup=[]; delist=[]
    for ep in episodes.itertuples(index=False):
        if not bool(ep.source_delisted): continue
        key=(str(ep.short_code).strip().upper().zfill(6),pd.Timestamp(ep.listing_date).normalize())
        if key not in by_key: raise KRXPrivateTerminalStatusError("delisted episode missing exact history key")
        dd,cs,ce=by_key[key]
        if pd.Timestamp(ep.delisting_date).normalize()!=dd: raise KRXPrivateTerminalStatusError("delisting date drift")
        # Identity/history evidence is historical source evidence, not a claim of point-in-time availability.
        available=pd.NaT
        delist.append({"symbol":key[0],"delisting_date":dd,"available_at":available})
        if cs is not None: cleanup.append({"symbol":key[0],"cleanup_start":cs,"cleanup_end":ce,"available_at":available})
    return pd.DataFrame(cleanup,columns=["symbol","cleanup_start","cleanup_end","available_at"]),pd.DataFrame(delist,columns=["symbol","delisting_date","available_at"])
