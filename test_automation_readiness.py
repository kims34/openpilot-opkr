import builtins
import os
import socket
import sqlite3
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from automation_readiness import attach,readiness,PATH


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.app=FastAPI();attach(self.app)
        self.client=TestClient(self.app)

    def test_get_reports_unavailable_without_network_db_files_or_account_reads(self):
        with (patch.object(socket.socket,'connect',side_effect=AssertionError('network')),
            patch.object(sqlite3,'connect',side_effect=AssertionError('database')),
            patch.object(builtins,'open',side_effect=AssertionError('file'))):
            response=self.client.get(PATH)
        self.assertEqual(response.status_code,200)
        body=response.json()
        self.assertEqual(body['status'],'BROKER_AUTOMATION_UNAVAILABLE')
        self.assertEqual(body['mode'],'MASTER_OFF')
        for key in ('live_ordering_authorized','broker_order_submission_implemented',
            'independent_gate_admission_evaluated','account_or_capital_snapshot_observed',
            'orders_requested','funds_movement_attempted','database_or_file_mutation_attempted'):
            self.assertIs(body[key],False)

    def test_query_or_environment_flags_never_enable_or_emit_private_values(self):
        with patch.dict(os.environ,{'KIWOOM_ENV':'REAL','KIWOOM_ORDERING_ENABLED':'true',
            'KIWOOM_APP_SECRET':'private-secret','INDEXALERT_LIVE_ENABLED':'true'}):
            response=self.client.get(PATH,params={'live_ordering_authorized':'true','account':'private-account'})
        self.assertEqual(response.json(),readiness())
        self.assertNotIn('private-',response.text)

    def test_mutation_methods_are_not_exposed(self):
        for method in ('post','put','patch','delete'):
            with self.subTest(method=method):
                response=getattr(self.client,method)(PATH)
                self.assertEqual(response.status_code,405)
        self.assertFalse(self.client.get(PATH).json()['live_ordering_authorized'])

    def test_attach_is_idempotent_and_does_not_replace_other_routes(self):
        self.app.add_api_route('/unrelated',lambda:{'unchanged':True},methods=['GET'])
        attach(self.app)
        self.assertEqual(len([r for r in self.app.router.routes if r.path==PATH]),1)
        self.assertEqual(self.client.get('/unrelated').json(),{'unchanged':True})

    def test_conflicting_route_is_not_silently_overridden(self):
        app=FastAPI();app.add_api_route(PATH,lambda:{'live_ordering_authorized':True},methods=['GET'])
        with self.assertRaisesRegex(RuntimeError,'conflicting'):attach(app)

    def test_previously_cached_schema_includes_new_readonly_route(self):
        app=FastAPI();app.openapi();attach(app)
        self.assertEqual(set(app.openapi()['paths'][PATH]),{'get'})


if __name__=='__main__':unittest.main()
