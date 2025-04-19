import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from apps.integrations.ecommerce.trendyol import TrendyolIntegration

class TestTrendyolIntegration(unittest.TestCase):
    def setUp(self):
        """Test öncesi hazırlık"""
        self.integration = TrendyolIntegration()
        
    @patch('requests.get')
    def test_sync_orders(self, mock_get):
        """Sipariş senkronizasyonu testi"""
        # Mock response hazırla
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'content': [
                {'orderNumber': '123', 'status': 'Created'},
                {'orderNumber': '124', 'status': 'Shipped'}
            ]
        }
        mock_get.return_value = mock_response
        
        # Test tarih aralığı
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        # Testi çalıştır
        orders = self.integration.sync_orders(start_date, end_date)
        
        # Sonuçları kontrol et
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0]['orderNumber'], '123')
        self.assertEqual(orders[1]['orderNumber'], '124')
        
    @patch('requests.get')
    def test_sync_products(self, mock_get):
        """Ürün senkronizasyonu testi"""
        # Mock response hazırla
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'content': [
                {'barcode': '123456', 'title': 'Test Ürün 1'},
                {'barcode': '789012', 'title': 'Test Ürün 2'}
            ]
        }
        mock_get.return_value = mock_response
        
        # Testi çalıştır
        products = self.integration.sync_products()
        
        # Sonuçları kontrol et
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]['barcode'], '123456')
        self.assertEqual(products[1]['barcode'], '789012')
        
    @patch('requests.put')
    def test_update_stock(self, mock_put):
        """Stok güncelleme testi"""
        # Mock response hazırla
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        # Testi çalıştır
        result = self.integration.update_stock('123456', 10)
        
        # Sonuçları kontrol et
        self.assertTrue(result)
        mock_put.assert_called_once()
        
    @patch('requests.post')
    def test_push_invoice_data(self, mock_post):
        """Fatura gönderme testi"""
        # Mock response hazırla
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test verisi
        invoice_data = {
            'invoiceNumber': 'INV001',
            'invoiceDate': '2024-01-01',
            'totalAmount': 100.00
        }
        
        # Testi çalıştır
        result = self.integration.push_invoice_data('123', invoice_data)
        
        # Sonuçları kontrol et
        self.assertTrue(result)
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main() 