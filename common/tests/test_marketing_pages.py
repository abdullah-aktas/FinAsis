# -*- coding: utf-8 -*-
from django.test import TestCase
from django.urls import reverse

ROUTE_NAMES = [
    # products
    'products_yapay_zeka',
    # solutions
    'solutions_enteg',
    'solutions_raporlama',
    'solutions_analitik',
    # legal/policy
    'terms',
    'privacy_policy',
    'cookie_policy',
    'legal',
    'legal_kvkk',
    'risk_warning',
    # resources & training
    'resources_cfo_playbook',
    'resources_compliance_checklist',
    'training_finance_dashboard',
    'training_compliance_engine',
    'training_gamification_students',
    # developer & blog
    'developer_api',
    'blog',
    # favicon is tested via direct path generally
]

class TestMarketingPages(TestCase):

    def test_named_routes_return_ok(self):
        for name in ROUTE_NAMES:
            url = reverse(name)
            resp = self.client.get(url)
            self.assertIn(
                resp.status_code,
                [200, 302],
                msg=f"Route '{name}' at {url} returned {resp.status_code}",
            )

    def test_favicon_redirects(self):
        resp = self.client.get('/favicon.ico')
        self.assertIn(resp.status_code, [200, 301, 302])
