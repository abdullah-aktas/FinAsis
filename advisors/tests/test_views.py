# -*- coding: utf-8 -*-
"""
Mali Müşavirlik Modülü View Testleri
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from advisors.models import (
    AdvisorProfile,
    TaxpayerProfile,
    Engagement,
)

User = get_user_model()


class AdvisorDashboardTestCase(TestCase):
    """Advisor dashboard view testleri"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_advisor',
            email='advisor@test.com',
            password='testpass123'
        )
        self.advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='SMMM',
            chamber_no='12345'
        )

    def test_dashboard_requires_login(self):
        """Dashboard giriş gerektirir"""
        response = self.client.get(reverse('advisors:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_accessible(self):
        """Dashboard erişilebilir"""
        self.client.login(username='test_advisor', password='testpass123')
        response = self.client.get(reverse('advisors:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dashboard')

    def test_dashboard_with_clients(self):
        """Dashboard müşterilerle"""
        self.client.login(username='test_advisor', password='testpass123')
        taxpayer = TaxpayerProfile.objects.create(
            name='Test Şirketi',
            vkn_tckn='1234567890'
        )
        Engagement.objects.create(
            advisor=self.advisor,
            taxpayer=taxpayer,
            scope='both',
            status='active'
        )
        response = self.client.get(reverse('advisors:dashboard'))
        self.assertEqual(response.status_code, 200)


class ClientListTestCase(TestCase):
    """Client list view testleri"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_advisor',
            email='advisor@test.com',
            password='testpass123'
        )
        self.advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='SMMM',
            chamber_no='12345'
        )

    def test_client_list_requires_login(self):
        """Client list giriş gerektirir"""
        response = self.client.get(reverse('advisors:client_list'))
        self.assertEqual(response.status_code, 302)

    def test_client_list_accessible(self):
        """Client list erişilebilir"""
        self.client.login(username='test_advisor', password='testpass123')
        response = self.client.get(reverse('advisors:client_list'))
        self.assertEqual(response.status_code, 200)


class DeclarationListTestCase(TestCase):
    """Declaration list view testleri"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_advisor',
            email='advisor@test.com',
            password='testpass123'
        )
        self.advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='SMMM',
            chamber_no='12345'
        )

    def test_declaration_list_requires_login(self):
        """Declaration list giriş gerektirir"""
        response = self.client.get(reverse('advisors:declaration_list'))
        self.assertEqual(response.status_code, 302)

    def test_declaration_list_accessible(self):
        """Declaration list erişilebilir"""
        self.client.login(username='test_advisor', password='testpass123')
        response = self.client.get(reverse('advisors:declaration_list'))
        self.assertEqual(response.status_code, 200)


class InvoiceListTestCase(TestCase):
    """Invoice list view testleri"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_advisor',
            email='advisor@test.com',
            password='testpass123'
        )
        self.advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='SMMM',
            chamber_no='12345'
        )

    def test_invoice_list_requires_login(self):
        """Invoice list giriş gerektirir"""
        response = self.client.get(reverse('advisors:invoice_list'))
        self.assertEqual(response.status_code, 302)

    def test_invoice_list_accessible(self):
        """Invoice list erişilebilir"""
        self.client.login(username='test_advisor', password='testpass123')
        response = self.client.get(reverse('advisors:invoice_list'))
        self.assertEqual(response.status_code, 200)

