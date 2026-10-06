"""Build an allowlisted offline operator archive; no databases or source data."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


MODULES = (
    'order_intent_journal.py','order_snapshot_reconciliation.py',
    'indexalert_automation_control.py','shadow_capital_allocator.py',
    'kiwoom_account_settlement_evidence.py','early_live_admission_gate.py',
    'account_settlement_binding.py','account_cashflow_reconciliation.py',
    'kiwoom_settlement_history.py','native_cashflow_binding.py',
    'native_cashflow_review_manifest.py','native_settlement_readiness.py',
    'native_settlement_review_cli.py','shadow_operational_status.py',
    'shadow_operational_dashboard.py',
)
ARTIFACTS = MODULES + ('INDEXALERT_OPERATOR_TOOLKIT_README.md','operator-toolkit-requirements.txt')


def build_operator_toolkit(root, output, *, source_commit):
    if type(source_commit) is not str or not re.fullmatch(r'[0-9a-f]{40}',source_commit):
        raise ValueError('exact source commit required')
    root, output = Path(root),Path(output)
    files = {}
    for name in ARTIFACTS:
        path = root/name
        if path.is_symlink() or not path.is_file():
            raise ValueError('required toolkit source missing')
        data = path.read_bytes()
        if name in MODULES:
            compile(data,name,'exec')
        files[name] = data
    manifest = dict(format_version=1,mode='OFFLINE_SHADOW_OPERATOR_TOOLKIT',
        source_commit=source_commit,
        files={name:hashlib.sha256(data).hexdigest() for name,data in files.items()},
        raw_account_data_included=False,credentials_included=False,
        real_orders_authorized=False,genuine_live_provenance_verified=False,
        source_account_origin_authenticated=False)
    files['toolkit-manifest.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(files.items()):
            info = zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info,data)
    return dict(source_commit=source_commit,file_count=len(files),
        archive_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        real_orders_authorized=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',default=str(Path(__file__).resolve().parent))
    parser.add_argument('--output',required=True)
    parser.add_argument('--source-commit',required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build_operator_toolkit(args.source_root,args.output,
        source_commit=args.source_commit),sort_keys=True))


if __name__ == '__main__': main()
