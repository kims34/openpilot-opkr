"""Synthetic kt00015 shape tests only; no broker or account observations."""
import unittest
from dataclasses import replace
from decimal import Decimal

from kiwoom_settlement_history import *


class HistoryTests(unittest.TestCase):
    def request(self):
        return dict(strt_dt='20261001',end_dt='20261006',tp='0',gds_tp='0',
                    dmst_stex_tp='%',stk_cd='',crnc_cd='',frgn_stex_code='',qry_sort_tp='2')

    def row(self):
        return dict(trde_dt='20261006',trde_no='SYNTHETIC-1',exct_amt='-1,001',
                    entra_remn='8999',crnc_cd='SYN',io_tp='UNVERIFIED',cmsn='1',
                    trde_agri_tax='0',tax_sum_cmsn='1',proc_tm='090000',orig_deal_no='')

    def page(self,row=None):
        return SettlementHistoryPage({'return_code':0,ARRAY:[self.row() if row is None else row]},'','N','')

    def normalize(self,pages=None,request=None):
        return normalize_kt00015_history(pages or [self.page()],request=request or self.request(),
            account_fingerprint='a'*64,captured_at='2026-10-06T10:00:00+09:00')

    def test_retains_native_currency_direction_costs_without_cashflow_inference(self):
        batch=self.normalize()
        record=batch.records[0]
        self.assertEqual(dict(record.native_fields)['io_tp'],'UNVERIFIED')
        self.assertEqual(dict(record.native_fields)['proc_tm'],'090000')
        self.assertEqual(dict(record.money_fields)['exct_amt'],Decimal('-1001'))
        report=batch.report()
        for name in ('account_settlement_admitted','complete_settlement_scope_attested',
                     'signed_net_mapping_attested','fees_tax_completeness_attested',
                     'genuine_live_provenance_verified','real_orders_authorized'):
            self.assertFalse(report[name])
        self.assertNotIn('SYNTHETIC-1',repr(report))
        self.assertNotIn('UNVERIFIED',repr(report))

    def test_closed_contiguous_pages_and_identical_redelivery(self):
        first=replace(self.page(),response_cont_yn='Y',response_next_key='cursor-1')
        second=replace(self.page(),request_next_key='cursor-1')
        batch=self.normalize([first,second])
        self.assertEqual(len(batch.records),1)
        self.assertEqual(batch.duplicate_delivery_count,1)

    def test_incomplete_client_limit_does_not_pass(self):
        page=replace(self.page(),response_cont_yn='Y',response_next_key='more')
        with self.assertRaises(SettlementHistoryError): self.normalize([page])

    def test_skipped_or_replayed_page_cursor_is_rejected(self):
        first=replace(self.page(),response_cont_yn='Y',response_next_key='one')
        skipped=replace(self.page(),request_next_key='other')
        with self.assertRaises(SettlementHistoryError): self.normalize([first,skipped])
        replay=replace(first,request_next_key='one')
        final=replace(self.page(),request_next_key='one')
        with self.assertRaises(SettlementHistoryError): self.normalize([first,replay,final])

    def test_filtered_query_cannot_be_whole_account_history(self):
        for name,value in (('tp','4'),('gds_tp','1'),('dmst_stex_tp','KRX'),('stk_cd','005930'),('crnc_cd','KRW')):
            request=self.request();request[name]=value
            with self.assertRaises(SettlementHistoryError): self.normalize(request=request)

    def test_duplicate_identity_with_conflicting_balance_or_cost_is_rejected(self):
        row=self.row(); row['cmsn']='2'
        page=self.page();page.body[ARRAY].append(row)
        with self.assertRaises(SettlementHistoryError): self.normalize([page])

    def test_missing_numbers_are_preserved_not_imputed(self):
        row=self.row();row['exct_amt']='';row['cmsn']=''
        amounts=dict(self.normalize([self.page(row)]).records[0].money_fields)
        self.assertIsNone(amounts['exct_amt'])
        self.assertIsNone(amounts['cmsn'])

    def test_invalid_date_or_out_of_scope_record_is_rejected(self):
        for value in ('20260230','20261007'):
            row=self.row();row['trde_dt']=value
            with self.assertRaises(SettlementHistoryError): self.normalize([self.page(row)])

    def test_failure_response_or_missing_header_is_rejected(self):
        for page in (replace(self.page(),body={'return_code':1,ARRAY:[]}),
                     replace(self.page(),response_cont_yn=''),
                     replace(self.page(),body={ARRAY:[]})):
            with self.assertRaises(SettlementHistoryError): self.normalize([page])

    def test_native_fields_are_detached_from_mutable_raw_input(self):
        page=self.page();batch=self.normalize([page]);page.body[ARRAY][0]['cmsn']='999'
        self.assertEqual(dict(batch.records[0].native_fields)['cmsn'],'1')


if __name__=='__main__': unittest.main()
