import requests
import json
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import time
from functools import lru_cache

class ApiService:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """API servisini başlat"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Oturum ayarları
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
        
        # Yeniden deneme ayarları
        self.max_retries = 3
        self.retry_delay = 1  # saniye
    
    @lru_cache(maxsize=100)
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """API isteği gönder"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    timeout=10
                )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logging.error(f"API isteği başarısız: {e}")
                    raise
                
                time.sleep(self.retry_delay * (attempt + 1))
    
    def sync_transactions(self, transactions: List[Dict[str, Any]]) -> bool:
        """İşlemleri senkronize et"""
        try:
            response = self._make_request('POST', '/transactions/sync', {
                'transactions': transactions
            })
            return response.get('success', False)
        except Exception as e:
            logging.error(f"İşlem senkronizasyon hatası: {e}")
            return False
    
    def sync_budgets(self, budgets: List[Dict[str, Any]]) -> bool:
        """Bütçeleri senkronize et"""
        try:
            response = self._make_request('POST', '/budgets/sync', {
                'budgets': budgets
            })
            return response.get('success', False)
        except Exception as e:
            logging.error(f"Bütçe senkronizasyon hatası: {e}")
            return False
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Kategorileri getir"""
        try:
            response = self._make_request('GET', '/categories')
            return response.get('categories', [])
        except Exception as e:
            logging.error(f"Kategori getirme hatası: {e}")
            return []
    
    def get_user_settings(self) -> Dict[str, Any]:
        """Kullanıcı ayarlarını getir"""
        try:
            response = self._make_request('GET', '/settings')
            return response.get('settings', {})
        except Exception as e:
            logging.error(f"Ayar getirme hatası: {e}")
            return {}
    
    def update_user_settings(self, settings: Dict[str, Any]) -> bool:
        """Kullanıcı ayarlarını güncelle"""
        try:
            response = self._make_request('PUT', '/settings', settings)
            return response.get('success', False)
        except Exception as e:
            logging.error(f"Ayar güncelleme hatası: {e}")
            return False
    
    def close(self):
        """API oturumunu kapat"""
        self.session.close() 