import os
import sqlite3
import logging
import json
from pathlib import Path
import threading
from datetime import datetime
import time

class DatabaseService:
    def __init__(self, db_name="finasis.db"):
        self.logger = logging.getLogger(__name__)
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.lock = threading.Lock()
        
        # Veritabanı dosyasının yolu
        self.db_path = Path.home() / ".finasis" / "data" / db_name
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Veritabanı bağlantısını oluştur
        self.connect()
        
        # Tabloları oluştur
        self.create_tables()
    
    def connect(self):
        """Veritabanı bağlantısını oluşturur"""
        try:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Dict-like rows
            self.cursor = self.connection.cursor()
            
            # Performans optimizasyonları
            self.cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            self.cursor.execute("PRAGMA synchronous=NORMAL")  # Daha hızlı yazma
            self.cursor.execute("PRAGMA cache_size=10000")  # Önbellek boyutunu artır
            self.cursor.execute("PRAGMA temp_store=MEMORY")  # Geçici tabloları bellekte tut
            
            self.logger.info(f"Veritabanı bağlantısı başarılı: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Veritabanı bağlantısı başarısız: {str(e)}")
            raise
    
    def create_tables(self):
        """Gerekli tabloları oluşturur"""
        try:
            with self.lock:
                # İşlemler tablosu
                self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    category TEXT,
                    date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    sync_status TEXT DEFAULT 'pending',
                    metadata TEXT
                )
                """)
                
                # Bütçeler tablosu
                self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id TEXT PRIMARY KEY,
                    month TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    spent REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    sync_status TEXT DEFAULT 'pending',
                    metadata TEXT,
                    UNIQUE(month, year)
                )
                """)
                
                # Kategoriler tablosu
                self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    color TEXT,
                    icon TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    sync_status TEXT DEFAULT 'pending'
                )
                """)
                
                # İndeksler oluştur
                self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)")
                self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)")
                self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_sync ON transactions(sync_status)")
                self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_budgets_month_year ON budgets(month, year)")
                self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_budgets_sync ON budgets(sync_status)")
                
                self.connection.commit()
                self.logger.info("Veritabanı tabloları oluşturuldu")
        except Exception as e:
            self.logger.error(f"Tablo oluşturma hatası: {str(e)}")
            raise
    
    def execute_query(self, query, params=None, fetch=True):
        """SQL sorgusunu çalıştırır"""
        try:
            with self.lock:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                
                if fetch:
                    result = self.cursor.fetchall()
                    return [dict(row) for row in result]
                else:
                    self.connection.commit()
                    return self.cursor.rowcount
        except Exception as e:
            self.logger.error(f"Sorgu hatası: {str(e)}")
            self.connection.rollback()
            raise
    
    def add_transaction(self, transaction):
        """Yeni işlem ekler"""
        now = datetime.now().isoformat()
        
        # Metadata'yı JSON'a dönüştür
        if 'metadata' in transaction and transaction['metadata']:
            transaction['metadata'] = json.dumps(transaction['metadata'])
        
        query = """
        INSERT INTO transactions 
        (id, type, amount, description, category, date, created_at, updated_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            transaction.get('id'),
            transaction.get('type'),
            transaction.get('amount'),
            transaction.get('description'),
            transaction.get('category'),
            transaction.get('date'),
            now,
            now,
            transaction.get('metadata')
        )
        
        return self.execute_query(query, params, fetch=False)
    
    def update_transaction(self, transaction_id, updates):
        """İşlem günceller"""
        now = datetime.now().isoformat()
        
        # Metadata'yı JSON'a dönüştür
        if 'metadata' in updates and updates['metadata']:
            updates['metadata'] = json.dumps(updates['metadata'])
        
        # Güncelleme alanlarını oluştur
        update_fields = []
        params = []
        
        for key, value in updates.items():
            if key != 'id':  # ID'yi güncelleme
                update_fields.append(f"{key} = ?")
                params.append(value)
        
        # updated_at alanını ekle
        update_fields.append("updated_at = ?")
        params.append(now)
        
        # transaction_id'yi ekle
        params.append(transaction_id)
        
        query = f"""
        UPDATE transactions 
        SET {', '.join(update_fields)}
        WHERE id = ?
        """
        
        return self.execute_query(query, params, fetch=False)
    
    def get_transactions(self, filters=None, limit=100, offset=0):
        """İşlemleri filtrelerle getirir"""
        query = "SELECT * FROM transactions"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    conditions.append(f"{key} = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        return self.execute_query(query, params)
    
    def add_budget(self, budget):
        """Yeni bütçe ekler"""
        now = datetime.now().isoformat()
        
        # Metadata'yı JSON'a dönüştür
        if 'metadata' in budget and budget['metadata']:
            budget['metadata'] = json.dumps(budget['metadata'])
        
        query = """
        INSERT INTO budgets 
        (id, month, year, amount, spent, created_at, updated_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            budget.get('id'),
            budget.get('month'),
            budget.get('year'),
            budget.get('amount'),
            budget.get('spent', 0),
            now,
            now,
            budget.get('metadata')
        )
        
        return self.execute_query(query, params, fetch=False)
    
    def update_budget(self, budget_id, updates):
        """Bütçe günceller"""
        now = datetime.now().isoformat()
        
        # Metadata'yı JSON'a dönüştür
        if 'metadata' in updates and updates['metadata']:
            updates['metadata'] = json.dumps(updates['metadata'])
        
        # Güncelleme alanlarını oluştur
        update_fields = []
        params = []
        
        for key, value in updates.items():
            if key != 'id':  # ID'yi güncelleme
                update_fields.append(f"{key} = ?")
                params.append(value)
        
        # updated_at alanını ekle
        update_fields.append("updated_at = ?")
        params.append(now)
        
        # budget_id'yi ekle
        params.append(budget_id)
        
        query = f"""
        UPDATE budgets 
        SET {', '.join(update_fields)}
        WHERE id = ?
        """
        
        return self.execute_query(query, params, fetch=False)
    
    def get_budgets(self, filters=None, limit=100, offset=0):
        """Bütçeleri filtrelerle getirir"""
        query = "SELECT * FROM budgets"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    conditions.append(f"{key} = ?")
                    params.append(value)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY year DESC, month DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        return self.execute_query(query, params)
    
    def get_pending_sync_items(self, table_name):
        """Senkronizasyon bekleyen öğeleri getirir"""
        query = f"SELECT * FROM {table_name} WHERE sync_status = 'pending'"
        return self.execute_query(query)
    
    def mark_as_synced(self, table_name, item_id):
        """Öğeyi senkronize edildi olarak işaretler"""
        query = f"UPDATE {table_name} SET sync_status = 'synced' WHERE id = ?"
        return self.execute_query(query, [item_id], fetch=False)
    
    def vacuum(self):
        """Veritabanını optimize eder"""
        try:
            with self.lock:
                self.cursor.execute("VACUUM")
                self.connection.commit()
                self.logger.info("Veritabanı optimize edildi")
        except Exception as e:
            self.logger.error(f"Veritabanı optimizasyon hatası: {str(e)}")
    
    def backup(self, backup_path=None):
        """Veritabanı yedeği alır"""
        if backup_path is None:
            backup_path = self.db_path.parent / f"{self.db_name}.backup"
        
        try:
            with self.lock:
                # Mevcut bağlantıyı kapat
                self.connection.close()
                
                # Yedekleme işlemi
                import shutil
                shutil.copy2(self.db_path, backup_path)
                
                # Bağlantıyı yeniden aç
                self.connect()
                
                self.logger.info(f"Veritabanı yedeği alındı: {backup_path}")
                return str(backup_path)
        except Exception as e:
            self.logger.error(f"Veritabanı yedekleme hatası: {str(e)}")
            # Bağlantıyı yeniden aç
            self.connect()
            raise
    
    def close(self):
        """Veritabanı bağlantısını kapatır"""
        if self.connection:
            self.connection.close()
            self.logger.info("Veritabanı bağlantısı kapatıldı") 