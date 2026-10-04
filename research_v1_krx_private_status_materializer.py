"""Offline reconstruction of normalized KRX halt events from private store.

Reads only already-acquired raw objects and frozen task/completion metadata.
No network calls. Output is private and may contain identifiers.
"""
from __future__ import annotations
from typing import Any
import hashlib, json
import pandas as pd
from research_v1_krx_historical_fetchers import parse_data_marketplace_raw
from research_v1_krx_private_store import read_private_json, read_raw_object\nfrom research_v1_krx_acquisition_receipt import canonical_request_metadata
from research_v1_krx_acquisition_batch import verify_receipt_fingerprint

class KRXPrivateStatusMaterializerError(ValueError):
    pass

def _sha256(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode("utf-8")).hexdigest()

def _safe_component(value):
    text=str(value).strip()
    if not text or any(x in text for x in ("..","/","\\\\","\\x00")): raise KRXPrivateStatusMaterializerError("unsafe private-store path component")
    return text

def _retrieved_at_from_checkpoint(root, *, task, completion, git_worktree=None):
    spec=task.get("request_spec") or {}
    request_metadata=task.get("request_metadata") or spec.get("request_metadata") or spec
    request_sha=_sha256(canonical_request_metadata(request_metadata))
    expected=str(completion.get("request_metadata_sha256") or "").lower()
    if request_sha != expected: raise KRXPrivateStatusMaterializerError("request metadata fingerprint mismatch")
    family=_safe_component(task.get("source_family") or "KRX_SECURITY_STATUS")
    route=_safe_component(task.get("access_route") or "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION")
    dataset=_safe_component(task.get("dataset_identifier") or spec.get("dataset_identifier") or "")
    rel=f"checkpoints/{family}/{route}/{dataset}/{request_sha}.json"
    cp=read_private_json(root,rel,git_worktree=git_worktree)["value"]
    if cp.get("state")!="COMPLETE": raise KRXPrivateStatusMaterializerError("checkpoint is not COMPLETE")
    if str(cp.get("raw_object_sha256")) != str(completion.get("raw_object_sha256")): raise KRXPrivateStatusMaterializerError("checkpoint raw object mismatch")
    receipt=read_private_json(root,str(cp.get("receipt_relpath")),git_worktree=git_worktree)["value"]
    if verify_receipt_fingerprint(receipt) != str(cp.get("receipt_fingerprint_sha256")): raise KRXPrivateStatusMaterializerError("receipt fingerprint mismatch")
    ts=pd.Timestamp(receipt.get("retrieved_at"))
    if pd.isna(ts) or ts.tzinfo is None or ts.utcoffset() is None: raise KRXPrivateStatusMaterializerError("receipt retrieved_at must be timezone-aware")
    return ts

def _first(frame, names):
    for name in names:
        if name in frame.columns:
            return name
    raise KRXPrivateStatusMaterializerError(f"missing expected column family: {names}")

def _yyyymmdd(series):
    return pd.to_datetime(series.astype("string").str.replace(r"[^0-9]","",regex=True),format="%Y%m%d",errors="coerce").dt.normalize()

def materialize_private_status_events(root: str, *, git_worktree: str | None=None) -> pd.DataFrame:
    state=read_private_json(root,"batch_state/PER_SECURITY_HISTORY.json",git_worktree=git_worktree)["value"]
    if state.get("status")!="COMPLETE" or state.get("phase_complete") is not True:
        raise KRXPrivateStatusMaterializerError("PER_SECURITY_HISTORY is not complete")
    manifest=read_private_json(root,"task_manifests/per-security-history-v3.json",git_worktree=git_worktree)["value"]
    tasks=manifest.get("tasks") if isinstance(manifest,dict) else None
    if not isinstance(tasks,list):
        raise KRXPrivateStatusMaterializerError("private task manifest has no task list")
    by_id={str(t.get("task_id")):t for t in tasks}
    rows:list[dict[str,Any]]=[]
    for tid,completion in dict(state.get("completed") or {}).items():
        task=by_id.get(str(tid))
        spec=(task or {}).get("request_spec") or {}
        if not task or spec.get("kind")!="trading_halt":
            continue
        raw=read_raw_object(root,completion["raw_object_sha256"],expected_size=int(completion["raw_bytes_size"]),git_worktree=git_worktree)
        frame=parse_data_marketplace_raw(str(spec.get("method") or "csv"),raw)
        if frame.empty:
            continue
        symbol=str(spec.get("params",{}).get("isuCd2") or "").strip().upper()
        if not symbol:
            raise KRXPrivateStatusMaterializerError("halt task has no private short code")
        available=_retrieved_at_from_checkpoint(root,task=task,completion=completion,git_worktree=git_worktree)
        start_col=_first(frame,("거래정지일","정지일","HALT_DD","trading_halt_date"))
        end_col=next((c for c in ("거래재개일","재개일","RESUME_DD","resume_date") if c in frame.columns),None)
        starts=_yyyymmdd(frame[start_col]); ends=_yyyymmdd(frame[end_col]) if end_col else pd.Series(pd.NaT,index=frame.index)
        for start,resume in zip(starts,ends):
            if pd.isna(start): continue
            end=start if pd.isna(resume) else resume-pd.Timedelta(days=1)
            rows.append({"symbol":symbol.zfill(6) if symbol.isdigit() else symbol,"event_type":"HALT","event_start":start,"event_end":end,"available_at":available})
    return pd.DataFrame(rows,columns=["symbol","event_type","event_start","event_end","available_at"])
