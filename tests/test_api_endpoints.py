# -*- coding: utf-8 -*-
"""
Finans modülü ve entegrasyonlar için API Endpoint testleri.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
import pytest
import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch
from rest_framework.test import APIClient
from integrations.bank_integration.models import IntegratedBankAccount

User = get_user_model()

class InvoiceAPITests(APITestCase):
    """Fatura API endpoint testleri."""
    
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # İlgili modelleri import et
        from finance.accounting.models import Invoice, Customer
        
        # Test müşterisi oluştur
        self.customer = Customer.objects.create(
            name="Test Müşteri",
            tax_id="1234567890",
            address="Test Adres"
        )
        
        # Test faturası oluştur
        self.invoice = Invoice.objects.create(
            customer=self.customer,
            invoice_number="INV-2023-001",
            issue_date=datetime.now().date(),
            due_date=datetime.now().date(),
            total_amount=Decimal("1180.00"),
            status="DRAFT"
        )
    
    def test_get_invoices_list(self):
        """Fatura listesi alma testi."""
        url = reverse('invoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_invoice_detail(self):
        """Fatura detayı alma testi."""
        url = reverse('invoice-detail', kwargs={'pk': self.invoice.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['invoice_number'], "INV-2023-001")
        self.assertEqual(response.data['total_amount'], '1180.00')
    
    def test_create_invoice(self):
        """Fatura oluşturma testi."""
        url = reverse('invoice-list')
        data = {
            'customer': self.customer.id,
            'invoice_number': 'INV-2023-002',
            'issue_date': datetime.now().date().isoformat(),
            'due_date': datetime.now().date().isoformat(),
            'total_amount': '2360.00',
            'status': 'DRAFT',
            'items': [
                {
                    'description': 'Test Ürün 1',
                    'quantity': 2,
                    'unit_price': '1000.00',
                    'tax_rate': '18.00'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['invoice_number'], 'INV-2023-002')
    
    def test_update_invoice(self):
        """Fatura güncelleme testi."""
        url = reverse('invoice-detail', kwargs={'pk': self.invoice.id})
        data = {
            'customer': self.customer.id,
            'invoice_number': self.invoice.invoice_number,
            'issue_date': self.invoice.issue_date.isoformat(),
            'due_date': self.invoice.due_date.isoformat(),
            'total_amount': self.invoice.total_amount,
            'status': 'APPROVED'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'APPROVED')


class BankIntegrationAPITests(APITestCase):
    """Banka entegrasyonu API endpoint testleri."""
    
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # İlgili modelleri import et
        from integrations.bank_integration.models import IntegratedBankAccount
        
        # Test banka hesabı oluştur
        self.bank_account = IntegratedBankAccount.objects.create(
            name="Test Hesabı",
            account_number="TR123456789012345678901234",
            currency="TRY"
        )
    
    def test_get_account_list(self):
        """Banka hesap listesi alma testi."""
        url = reverse('bank-account-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    @patch('integrations.bank_integration.services.BankAPIClient')
    def test_get_account_balance(self, mock_api_client):
        """Hesap bakiyesi alma API testi."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_balance.return_value = {"balance": 5000, "currency": "TRY"}
        
        url = reverse('bank-account-balance', kwargs={'pk': self.bank_account.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 5000)
        self.assertEqual(response.data['currency'], 'TRY')
    
    @patch('integrations.bank_integration.services.BankAPIClient')
    def test_initiate_transfer(self, mock_api_client):
        """Para transferi başlatma API testi."""
        mock_instance = mock_api_client.return_value
        mock_instance.transfer.return_value = {"status": "success", "transaction_id": "12345"}
        
        url = reverse('bank-transfer')
        data = {
            'from_account': self.bank_account.id,
            'to_account': "TR987654321098765432109876",
            'amount': '1000.00',
            'description': 'Test Transfer'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['transaction_id'], '12345')


class EFaturaAPITests(APITestCase):
    """E-fatura API endpoint testleri."""
    
    def setUp(self):
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        # İlgili modelleri import et
        from integrations.efatura.models import EInvoice
        
        # Test e-fatura oluştur
        self.einvoice = EInvoice.objects.create(
            invoice_number="INV-2023-001",
            issue_date=datetime.now().date(),
            due_date=datetime.now().date(),
            total_amount=Decimal("1000.00"),
            tax_amount=Decimal("180.00"),
            customer_name="Test Müşteri",
            customer_tax_id="1234567890"
        )
    
    def test_get_einvoice_list(self):
        """E-fatura listesi alma testi."""
        url = reverse('einvoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    @patch('integrations.efatura.services.EInvoiceProvider')
    def test_send_einvoice(self, mock_provider):
        """E-fatura gönderme API testi."""
        mock_instance = mock_provider.return_value
        mock_instance.send_invoice.return_value = {
            "status": "success", 
            "document_id": "12345678-1234-1234-1234-123456789012"
        }
        
        url = reverse('einvoice-send', kwargs={'pk': self.einvoice.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['document_id'], '12345678-1234-1234-1234-123456789012')
    
    @patch('integrations.efatura.services.EInvoiceProvider')
    def test_get_einvoice_status(self, mock_provider):
        """E-fatura durumu sorgulama API testi."""
        mock_instance = mock_provider.return_value
        mock_instance.get_invoice_status.return_value = {
            "status": "delivered", 
            "timestamp": "2023-06-15T14:30:00Z"
        }
        
        # Önce faturanın bir document_id'si olduğunu varsayalım
        self.einvoice.document_id = "12345678-1234-1234-1234-123456789012"
        self.einvoice.save()
        
        url = reverse('einvoice-status', kwargs={'pk': self.einvoice.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'delivered')
        self.assertEqual(response.data['timestamp'], '2023-06-15T14:30:00Z')

@pytest.mark.django_db
class TestAPIEndpoints:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_health_check(self, api_client):
        response = api_client.get(reverse('api:health-check'))
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'services' in data

    def test_authentication_required(self, api_client):
        response = api_client.get(reverse('api:protected-endpoint'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_rate_limiting(self, api_client):
        for _ in range(100):
            response = api_client.get(reverse('api:rate-limited'))
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_input_validation(self, api_client):
        invalid_data = {'invalid_field': 'value'}
        response = api_client.post(
            reverse('api:create-resource'),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.json()

    def test_pagination(self, api_client):
        response = api_client.get(reverse('api:list-resources'))
        data = response.json()
        assert 'count' in data
        assert 'next' in data
        assert 'previous' in data
        assert 'results' in data
        assert len(data['results']) <= 10  # Sayfa başına maksimum 10 sonuç

    def test_error_handling(self, api_client):
        response = api_client.get(reverse('api:error-endpoint'))
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert 'error' in data
        assert 'message' in data
        assert 'code' in data

    def test_cors_headers(self, api_client):
        response = api_client.get(reverse('api:health-check'))
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers 