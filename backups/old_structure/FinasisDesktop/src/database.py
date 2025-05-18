# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import sqlite3

Base = declarative_base()

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    description = Column(String)
    amount = Column(Float)
    type = Column(String)  # gelir/gider
    category = Column(String)
    is_synced = Column(Boolean, default=False)

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    is_synced = Column(Boolean, default=False)

class DatabaseManager:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), 'finasis.db')
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_transaction(self, description, amount, type, category):
        transaction = Transaction(
            description=description,
            amount=amount,
            type=type,
            category=category
        )
        self.session.add(transaction)
        self.session.commit()
        return transaction
    
    def add_customer(self, name, email, phone, address):
        customer = Customer(
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        self.session.add(customer)
        self.session.commit()
        return customer
    
    def get_unsynced_transactions(self):
        return self.session.query(Transaction).filter_by(is_synced=False).all()
    
    def get_unsynced_customers(self):
        return self.session.query(Customer).filter_by(is_synced=False).all()
    
    def mark_transaction_synced(self, transaction_id):
        transaction = self.session.query(Transaction).get(transaction_id)
        if transaction:
            transaction.is_synced = True
            self.session.commit()
    
    def mark_customer_synced(self, customer_id):
        customer = self.session.query(Customer).get(customer_id)
        if customer:
            customer.is_synced = True
            self.session.commit()
    
    def get_transactions_by_date_range(self, start_date, end_date):
        """Belirli bir tarih aralığındaki işlemleri getirir"""
        return self.session.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).order_by(Transaction.date.desc()).all()
    
    def get_transactions_by_category(self, category):
        """Belirli bir kategorideki işlemleri getirir"""
        return self.session.query(Transaction).filter_by(category=category).all()
    
    def get_total_income(self, start_date=None, end_date=None):
        """Belirli bir tarih aralığındaki toplam geliri hesaplar"""
        query = self.session.query(Transaction).filter_by(type="gelir")
        if start_date and end_date:
            query = query.filter(
                and_(
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            )
        return sum(t.amount for t in query.all())
    
    def get_total_expense(self, start_date=None, end_date=None):
        """Belirli bir tarih aralığındaki toplam gideri hesaplar"""
        query = self.session.query(Transaction).filter_by(type="gider")
        if start_date and end_date:
            query = query.filter(
                and_(
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            )
        return sum(t.amount for t in query.all())
    
    def get_category_summary(self, start_date=None, end_date=None):
        """Kategori bazlı gelir-gider özetini hesaplar"""
        query = self.session.query(Transaction)
        if start_date and end_date:
            query = query.filter(
                and_(
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            )
        
        categories = {}
        for trans in query.all():
            if trans.category not in categories:
                categories[trans.category] = {"gelir": 0, "gider": 0}
            
            if trans.type == "gelir":
                categories[trans.category]["gelir"] += trans.amount
            else:
                categories[trans.category]["gider"] += trans.amount
        
        return categories
    
    def close(self):
        self.session.close()

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        
    def connect(self):
        """Veritabanına bağlanır"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        
    def close(self):
        """Veritabanı bağlantısını kapatır"""
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """Veritabanı tablolarını oluşturur"""
        cursor = self.conn.cursor()
        
        # Müşteriler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # İşlemler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        # Değişiklikler tablosu (senkronizasyon için)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                operation TEXT NOT NULL,
                change_data TEXT NOT NULL,
                change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Senkronizasyon bilgisi tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_info (
                id INTEGER PRIMARY KEY,
                last_sync TIMESTAMP
            )
        """)
        
        # Trigger'lar
        # Müşteri güncellendiğinde
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS customer_update_trigger
            AFTER UPDATE ON customers
            BEGIN
                INSERT INTO changes (table_name, record_id, operation, change_data)
                VALUES ('customers', NEW.id, 'UPDATE', json_object(
                    'id', NEW.id,
                    'name', NEW.name,
                    'email', NEW.email,
                    'phone', NEW.phone,
                    'address', NEW.address,
                    'notes', NEW.notes
                ));
            END;
        """)
        
        # Yeni müşteri eklendiğinde
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS customer_insert_trigger
            AFTER INSERT ON customers
            BEGIN
                INSERT INTO changes (table_name, record_id, operation, change_data)
                VALUES ('customers', NEW.id, 'INSERT', json_object(
                    'id', NEW.id,
                    'name', NEW.name,
                    'email', NEW.email,
                    'phone', NEW.phone,
                    'address', NEW.address,
                    'notes', NEW.notes
                ));
            END;
        """)
        
        # Müşteri silindiğinde
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS customer_delete_trigger
            AFTER DELETE ON customers
            BEGIN
                INSERT INTO changes (table_name, record_id, operation, change_data)
                VALUES ('customers', OLD.id, 'DELETE', json_object('id', OLD.id));
            END;
        """)
        
        # İşlem güncellendiğinde
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transaction_update_trigger
            AFTER UPDATE ON transactions
            BEGIN
                INSERT INTO changes (table_name, record_id, operation, change_data)
                VALUES ('transactions', NEW.id, 'UPDATE', json_object(
                    'id', NEW.id,
                    'customer_id', NEW.customer_id,
                    'type', NEW.type,
                    'amount', NEW.amount,
                    'description', NEW.description,
                    'date', NEW.date
                ));
            END;
        """)
        
        # Yeni işlem eklendiğinde
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transaction_insert_trigger
            AFTER INSERT ON transactions
            BEGIN
                INSERT INTO changes (table_name, record_id, operation, change_data)
                VALUES ('transactions', NEW.id, 'INSERT', json_object(
                    'id', NEW.id,
                    'customer_id', NEW.customer_id,
                    'type', NEW.type,
                    'amount', NEW.amount,
                    'description', NEW.description,
                    'date', NEW.date
                ));
            END;
        """)
        
        # İşlem silindiğinde
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS transaction_delete_trigger
            AFTER DELETE ON transactions
            BEGIN
                INSERT INTO changes (table_name, record_id, operation, change_data)
                VALUES ('transactions', OLD.id, 'DELETE', json_object('id', OLD.id));
            END;
        """)
        
        self.conn.commit()
        
    def initialize(self):
        """Veritabanını başlatır"""
        self.connect()
        self.create_tables()
        
        # İlk senkronizasyon kaydını oluştur
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO sync_info (id, last_sync)
            VALUES (1, ?)
        """, [datetime.now().isoformat()])
        self.conn.commit() 