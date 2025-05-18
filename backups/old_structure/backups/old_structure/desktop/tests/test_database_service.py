# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
from pathlib import Path
from services.DatabaseService import DatabaseService

class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        """Her test öncesi çalışacak hazırlık fonksiyonu"""
        # Geçici bir veritabanı dosyası oluştur
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db_service = DatabaseService(str(self.db_path))
    
    def tearDown(self):
        """Her test sonrası çalışacak temizlik fonksiyonu"""
        # Veritabanı bağlantısını kapat
        self.db_service.close()
        # Geçici dosyaları temizle
        if self.db_path.exists():
            self.db_path.unlink()
        os.rmdir(self.temp_dir)
    
    def test_create_tables(self):
        """Tablo oluşturma işlemini test et"""
        # Tabloların varlığını kontrol et
        tables = self.db_service.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [table['name'] for table in tables]
        
        self.assertIn('transactions', table_names)
        self.assertIn('budgets', table_names)
        self.assertIn('categories', table_names)
    
    def test_add_transaction(self):
        """İşlem ekleme işlemini test et"""
        # Test verisi
        transaction = {
            'type': 'expense',
            'amount': 150.50,
            'description': 'Test işlemi',
            'category': 'test_category',
            'date': '2023-06-15'
        }
        
        # İşlemi ekle
        result = self.db_service.add_transaction(transaction)
        self.assertTrue(result)
        
        # Eklenen işlemi kontrol et
        transactions = self.db_service.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['amount'], 150.50)
        self.assertEqual(transactions[0]['description'], 'Test işlemi')
    
    def test_update_transaction(self):
        """İşlem güncelleme işlemini test et"""
        # Önce bir işlem ekle
        transaction = {
            'type': 'expense',
            'amount': 150.50,
            'description': 'Test işlemi',
            'category': 'test_category',
            'date': '2023-06-15'
        }
        self.db_service.add_transaction(transaction)
        
        # İşlemi güncelle
        updates = {
            'amount': 175.25,
            'description': 'Güncellenmiş işlem'
        }
        transactions = self.db_service.get_transactions()
        transaction_id = transactions[0]['id']
        
        result = self.db_service.update_transaction(transaction_id, updates)
        self.assertTrue(result)
        
        # Güncellenmiş işlemi kontrol et
        updated_transactions = self.db_service.get_transactions()
        self.assertEqual(updated_transactions[0]['amount'], 175.25)
        self.assertEqual(updated_transactions[0]['description'], 'Güncellenmiş işlem')
    
    def test_add_budget(self):
        """Bütçe ekleme işlemini test et"""
        # Test verisi
        budget = {
            'month': '06',
            'year': 2023,
            'amount': 5000.00
        }
        
        # Bütçeyi ekle
        result = self.db_service.add_budget(budget)
        self.assertTrue(result)
        
        # Eklenen bütçeyi kontrol et
        budgets = self.db_service.get_budgets()
        self.assertEqual(len(budgets), 1)
        self.assertEqual(budgets[0]['amount'], 5000.00)
        self.assertEqual(budgets[0]['month'], '06')
    
    def test_update_budget(self):
        """Bütçe güncelleme işlemini test et"""
        # Önce bir bütçe ekle
        budget = {
            'month': '06',
            'year': 2023,
            'amount': 5000.00
        }
        self.db_service.add_budget(budget)
        
        # Bütçeyi güncelle
        updates = {
            'amount': 5500.00
        }
        budgets = self.db_service.get_budgets()
        budget_id = budgets[0]['id']
        
        result = self.db_service.update_budget(budget_id, updates)
        self.assertTrue(result)
        
        # Güncellenmiş bütçeyi kontrol et
        updated_budgets = self.db_service.get_budgets()
        self.assertEqual(updated_budgets[0]['amount'], 5500.00)
    
    def test_get_pending_sync_items(self):
        """Senkronizasyon bekleyen öğeleri getirme işlemini test et"""
        # Test verisi ekle
        transaction = {
            'type': 'expense',
            'amount': 150.50,
            'description': 'Test işlemi',
            'category': 'test_category',
            'date': '2023-06-15'
        }
        self.db_service.add_transaction(transaction)
        
        # Senkronizasyon bekleyen öğeleri kontrol et
        pending_items = self.db_service.get_pending_sync_items('transactions')
        self.assertEqual(len(pending_items), 1)
        self.assertEqual(pending_items[0]['amount'], 150.50)
    
    def test_mark_as_synced(self):
        """Senkronize edildi olarak işaretleme işlemini test et"""
        # Test verisi ekle
        transaction = {
            'type': 'expense',
            'amount': 150.50,
            'description': 'Test işlemi',
            'category': 'test_category',
            'date': '2023-06-15'
        }
        self.db_service.add_transaction(transaction)
        
        # Öğeyi senkronize edildi olarak işaretle
        transactions = self.db_service.get_transactions()
        transaction_id = transactions[0]['id']
        
        result = self.db_service.mark_as_synced('transactions', transaction_id)
        self.assertTrue(result)
        
        # Senkronizasyon durumunu kontrol et
        pending_items = self.db_service.get_pending_sync_items('transactions')
        self.assertEqual(len(pending_items), 0)

if __name__ == '__main__':
    unittest.main() 