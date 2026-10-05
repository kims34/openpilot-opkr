"""Bounded explicit DEMO pagination; cursor termination is not source admission."""
from copy import deepcopy
import time


TABLES={'kt00007':'acnt_ord_cntr_prps_dtl','ka10076':'cntr'}


class SnapshotCollectionError(ValueError):
    pass


def require(condition):
    if not condition:raise SnapshotCollectionError('DEMO_SNAPSHOT_COLLECTION_BLOCKED')


class PrivateDemoSnapshot:
    __slots__=('source_api','rows','page_count')
    def __init__(self,api,rows,pages):self.source_api,self.rows,self.page_count=api,rows,pages
    def __repr__(self):return '<PrivateDemoSnapshot redacted; DEMO/unadmitted>'
    def report(self):
        return dict(mode='DEMO_READ_ONLY_CURSOR_COLLECTION',source_api=self.source_api,
            page_count=self.page_count,row_count=len(self.rows),pagination_terminated=True,
            source_account_origin_authenticated=False,query_scope_completeness_attested=False,
            snapshot_freshness_attested=False,trading_date_origin_attested=False,
            fees_settled=False,genuine_live_provenance_verified=False,
            project_live_evidence_admitted=False,empirical_execution_blocker_closed=False,
            live_trading_authorized=False,database_or_file_mutation_attempted=False)


def collect_demo_snapshot(transport,api_id,body,*,max_pages=10):
    """Stop on first N marker; reject loops, duplicates and capped Y pages.

    Ten is a workload ceiling matching the reviewed official examples, not a
    completeness criterion. Missing pages are never interpreted as no orders.
    No automatic auth/refresh/retry; transport retains the DEMO-only allowlist.
    """
    require(type(api_id) is str and api_id in TABLES)
    require(type(body) is dict and type(max_pages) is int and 1<=max_pages<=10)
    require(all(type(k) is str and type(v) is str and len(v)<=256 for k,v in body.items()))
    request=dict(body);rows=[];orders=set();cursors=set();continuation='N';key=''
    try:
        for index in range(max_pages):
            if index:time.sleep(0.3)
            page=transport.query(api_id,deepcopy(request),continuation=continuation,next_key=key)
            require(page.continuation_header_present is True)
            batch=page.body.get(TABLES[api_id])
            require(type(batch) is list and all(type(row) is dict for row in batch))
            for row in batch:
                order=row.get('ord_no')
                require(type(order) is str and bool(order.strip()) and len(order)<=256 and order not in orders)
                orders.add(order);rows.append(deepcopy(row))
            require(page.continuation in ('N','Y'))
            if page.continuation=='N':return PrivateDemoSnapshot(api_id,rows,index+1)
            key=page.next_key
            require(type(key) is str and bool(key) and len(key)<=4096 and key not in cursors)
            require('\r' not in key and '\n' not in key)
            cursors.add(key);continuation='Y'
        raise SnapshotCollectionError('DEMO_SNAPSHOT_COLLECTION_BLOCKED')
    except Exception:
        # No partial snapshot is returned as successful; private cursor/order
        # values and provider errors must not escape through exception text.
        raise SnapshotCollectionError('DEMO_SNAPSHOT_COLLECTION_BLOCKED') from None
