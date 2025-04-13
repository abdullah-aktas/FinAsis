import requests
from database import DatabaseManager
import json
from datetime import datetime
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from queue import Queue
import threading

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SyncManager')

@dataclass
class SyncStatus:
    """Senkronizasyon durumunu takip eden sınıf"""
    last_sync: Optional[datetime] = None
    is_syncing: bool = False
    error_count: int = 0
    success_count: int = 0
    pending_items: int = 0

class SyncManager:
    def __init__(self, base_url="http://localhost:8000/api", batch_size=50):
        self.base_url = base_url
        self.db = DatabaseManager()
        self.batch_size = batch_size
        self.status = SyncStatus()
        self.sync_queue = Queue()
        self.offline_mode = False
        self._sync_thread = None
        self._stop_event = threading.Event()
        
        # Senkronizasyon thread'ini başlat
        self._start_sync_thread()
    
    def _start_sync_thread(self):
        """Arka planda senkronizasyon yapan thread'i başlatır"""
        self._sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self._sync_thread.start()
    
    def _sync_worker(self):
        """Arka planda senkronizasyon işlemlerini yürüten worker"""
        while not self._stop_event.is_set():
            if not self.offline_mode and not self.sync_queue.empty():
                try:
                    item = self.sync_queue.get()
                    if item['type'] == 'transaction':
                        self._sync_transaction(item['data'])
                    elif item['type'] == 'customer':
                        self._sync_customer(item['data'])
                    self.sync_queue.task_done()
                except Exception as e:
                    logger.error(f"Senkronizasyon hatası: {str(e)}")
                    self.status.error_count += 1
            
            time.sleep(1)  # CPU kullanımını azalt
    
    def _sync_transaction(self, transaction) -> bool:
        """Tek bir işlemi senkronize eder"""
        try:
            data = {
                "description": transaction.description,
                "amount": transaction.amount,
                "type": transaction.type,
                "category": transaction.category,
                "date": transaction.date.isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/transactions/",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 201:
                self.db.mark_transaction_synced(transaction.id)
                self.status.success_count += 1
                logger.info(f"İşlem senkronize edildi: {transaction.id}")
                return True
            else:
                logger.error(f"İşlem senkronizasyon hatası: {response.text}")
                self.status.error_count += 1
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Bağlantı hatası: {str(e)}")
            self.status.error_count += 1
            return False
    
    def _sync_customer(self, customer) -> bool:
        """Tek bir müşteriyi senkronize eder"""
        try:
            data = {
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "address": customer.address
            }
            
            response = requests.post(
                f"{self.base_url}/customers/",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 201:
                self.db.mark_customer_synced(customer.id)
                self.status.success_count += 1
                logger.info(f"Müşteri senkronize edildi: {customer.id}")
                return True
            else:
                logger.error(f"Müşteri senkronizasyon hatası: {response.text}")
                self.status.error_count += 1
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Bağlantı hatası: {str(e)}")
            self.status.error_count += 1
            return False
    
    def sync_transactions(self) -> bool:
        """İşlemleri toplu olarak senkronize eder"""
        if self.offline_mode:
            logger.info("Çevrimdışı mod aktif, senkronizasyon yapılamıyor")
            return False
            
        self.status.is_syncing = True
        self.status.last_sync = datetime.now()
        
        try:
            unsynced = self.db.get_unsynced_transactions()
            self.status.pending_items = len(unsynced)
            
            # İşlemleri kuyruğa ekle
            for transaction in unsynced:
                self.sync_queue.put({
                    'type': 'transaction',
                    'data': transaction
                })
            
            # Tüm işlemlerin tamamlanmasını bekle
            self.sync_queue.join()
            
            return True
            
        except Exception as e:
            logger.error(f"İşlem senkronizasyonu hatası: {str(e)}")
            return False
            
        finally:
            self.status.is_syncing = False
    
    def sync_customers(self) -> bool:
        """Müşterileri toplu olarak senkronize eder"""
        if self.offline_mode:
            logger.info("Çevrimdışı mod aktif, senkronizasyon yapılamıyor")
            return False
            
        self.status.is_syncing = True
        self.status.last_sync = datetime.now()
        
        try:
            unsynced = self.db.get_unsynced_customers()
            self.status.pending_items = len(unsynced)
            
            # Müşterileri kuyruğa ekle
            for customer in unsynced:
                self.sync_queue.put({
                    'type': 'customer',
                    'data': customer
                })
            
            # Tüm müşterilerin tamamlanmasını bekle
            self.sync_queue.join()
            
            return True
            
        except Exception as e:
            logger.error(f"Müşteri senkronizasyonu hatası: {str(e)}")
            return False
            
        finally:
            self.status.is_syncing = False
    
    def sync_all(self) -> bool:
        """Tüm verileri senkronize eder"""
        if self.offline_mode:
            logger.info("Çevrimdışı mod aktif, senkronizasyon yapılamıyor")
            return False
            
        transactions_success = self.sync_transactions()
        customers_success = self.sync_customers()
        
        return transactions_success and customers_success
    
    def check_connection(self) -> bool:
        """Sunucu bağlantısını kontrol eder"""
        try:
            response = requests.get(f"{self.base_url}/health/", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Bağlantı kontrolü hatası: {str(e)}")
            return False
    
    def get_status(self) -> Dict:
        """Senkronizasyon durumunu döndürür"""
        return {
            "last_sync": self.status.last_sync,
            "is_syncing": self.status.is_syncing,
            "error_count": self.status.error_count,
            "success_count": self.status.success_count,
            "pending_items": self.status.pending_items,
            "offline_mode": self.offline_mode
        }
    
    def set_offline_mode(self, offline: bool):
        """Çevrimdışı modu ayarlar"""
        self.offline_mode = offline
        logger.info(f"Çevrimdışı mod {'aktif' if offline else 'deaktif'}")
    
    def stop(self):
        """Senkronizasyon thread'ini durdurur"""
        self._stop_event.set()
        if self._sync_thread:
            self._sync_thread.join() 