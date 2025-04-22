import pytest
from django.test import Client
from django.urls import reverse
from ..models import IntegrationConfig, SyncLog, WebhookLog, IntegrationTask
from ..ecommerce.hepsiburada.hepsiburada import HepsiburadaIntegration
from ..ecommerce.shopify.shopify import ShopifyIntegration
from ..payment.iyzico.iyzico import IyzicoIntegration
from ..erp.luca.luca import LucaIntegration

@pytest.mark.django_db
class TestHepsiburadaIntegration:
    def test_authentication(self):
        integration = HepsiburadaIntegration({
            'api_key': 'test_key',
            'access_token': 'test_token'
        })
        result = integration.authenticate()
        assert result['success'] is True

    def test_sync_data(self):
        integration = HepsiburadaIntegration({
            'api_key': 'test_key',
            'access_token': 'test_token'
        })
        result = integration.sync_data()
        assert result['success'] is True
        assert 'orders' in result
        assert 'products' in result
        assert 'inventory' in result

    def test_webhook_handling(self):
        integration = HepsiburadaIntegration({
            'api_key': 'test_key',
            'access_token': 'test_token'
        })
        payload = {
            'event_type': 'order_status_change',
            'order_id': '123',
            'new_status': 'shipped'
        }
        result = integration.handle_webhook(payload)
        assert result['success'] is True

@pytest.mark.django_db
class TestShopifyIntegration:
    def test_authentication(self):
        integration = ShopifyIntegration({
            'shop_url': 'test-shop.myshopify.com',
            'api_key': 'test_key',
            'access_token': 'test_token'
        })
        result = integration.authenticate()
        assert result['success'] is True

    def test_sync_data(self):
        integration = ShopifyIntegration({
            'shop_url': 'test-shop.myshopify.com',
            'api_key': 'test_key',
            'access_token': 'test_token'
        })
        result = integration.sync_data()
        assert result['success'] is True
        assert 'orders' in result
        assert 'products' in result
        assert 'customers' in result

    def test_webhook_handling(self):
        integration = ShopifyIntegration({
            'shop_url': 'test-shop.myshopify.com',
            'api_key': 'test_key',
            'access_token': 'test_token'
        })
        payload = {
            'topic': 'orders/create',
            'order': {
                'id': 123,
                'total_price': '100.00'
            }
        }
        result = integration.handle_webhook(payload)
        assert result['success'] is True

@pytest.mark.django_db
class TestIyzicoIntegration:
    def test_authentication(self):
        integration = IyzicoIntegration({
            'api_key': 'test_key',
            'secret_key': 'test_secret'
        })
        result = integration.authenticate()
        assert result['success'] is True

    def test_payment_creation(self):
        integration = IyzicoIntegration({
            'api_key': 'test_key',
            'secret_key': 'test_secret'
        })
        payment_data = {
            'amount': 100.00,
            'currency': 'TRY',
            'card_number': '5528790000000008',
            'expiry_month': '12',
            'expiry_year': '2030',
            'cvv': '123'
        }
        result = integration.create_payment(payment_data)
        assert result['success'] is True
        assert 'payment_id' in result
        assert 'payment_page_url' in result

    def test_payment_status_check(self):
        integration = IyzicoIntegration({
            'api_key': 'test_key',
            'secret_key': 'test_secret'
        })
        result = integration.check_payment_status('test_payment_id')
        assert result['success'] is True
        assert 'status' in result

@pytest.mark.django_db
class TestLucaIntegration:
    def test_authentication(self):
        integration = LucaIntegration({
            'api_key': 'test_key',
            'access_token': 'test_token',
            'company_id': 'test_company'
        })
        result = integration.authenticate()
        assert result['success'] is True

    def test_invoice_creation(self):
        integration = LucaIntegration({
            'api_key': 'test_key',
            'access_token': 'test_token',
            'company_id': 'test_company'
        })
        invoice_data = {
            'invoice_type': 'SATIS',
            'date': '2024-03-20',
            'customer_tax_number': '1234567890',
            'items': [
                {
                    'name': 'Test Ürün',
                    'quantity': 1,
                    'unit_price': 100.00,
                    'vat_rate': 18
                }
            ]
        }
        result = integration.create_invoice(invoice_data)
        assert result['success'] is True
        assert 'invoice_id' in result
        assert 'invoice_number' in result

    def test_sync_data(self):
        integration = LucaIntegration({
            'api_key': 'test_key',
            'access_token': 'test_token',
            'company_id': 'test_company'
        })
        result = integration.sync_data()
        assert result['success'] is True
        assert 'accounts' in result
        assert 'products' in result
        assert 'receipts' in result

@pytest.mark.django_db
class TestIntegrationAPI:
    def test_dashboard_view(self, client):
        url = reverse('integrations:dashboard')
        response = client.get(url)
        assert response.status_code == 200
        assert 'integrations' in response.context

    def test_save_config(self, client):
        url = reverse('integrations:save_config', args=['hepsiburada'])
        data = {
            'is_active': True,
            'api_key': 'test_key',
            'access_token': 'test_token',
            'sync_frequency': 15
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert IntegrationConfig.objects.filter(
            integration_type='hepsiburada',
            api_key='test_key'
        ).exists()

    def test_run_sync(self, client):
        config = IntegrationConfig.objects.create(
            integration_type='hepsiburada',
            api_key='test_key',
            access_token='test_token',
            is_active=True
        )
        url = reverse('integrations:run_sync', args=[config.id])
        response = client.post(url)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert IntegrationTask.objects.filter(
            integration=config,
            task_type='sync'
        ).exists()

    def test_get_logs(self, client):
        config = IntegrationConfig.objects.create(
            integration_type='hepsiburada',
            api_key='test_key',
            access_token='test_token',
            is_active=True
        )
        SyncLog.objects.create(
            integration=config,
            level='INFO',
            message='Test log message'
        )
        url = reverse('integrations:get_logs', args=[config.id])
        response = client.get(url)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert len(response.json()['logs']) == 1

    def test_get_tasks(self, client):
        config = IntegrationConfig.objects.create(
            integration_type='hepsiburada',
            api_key='test_key',
            access_token='test_token',
            is_active=True
        )
        IntegrationTask.objects.create(
            integration=config,
            task_type='sync',
            status='completed'
        )
        url = reverse('integrations:get_tasks', args=[config.id])
        response = client.get(url)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert len(response.json()['tasks']) == 1

    def test_webhook(self, client):
        url = reverse('integrations:webhook', args=['hepsiburada'])
        payload = {
            'event_type': 'order_status_change',
            'order_id': '123',
            'new_status': 'shipped'
        }
        response = client.post(url, payload, content_type='application/json')
        assert response.status_code == 200
        assert response.json()['success'] is True 