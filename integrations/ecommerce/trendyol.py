# -*- coding: utf-8 -*-
import os
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class TrendyolIntegration:
    """
    Trendyol Marketplace entegrasyonu için ana sınıf.
    Sipariş, ürün ve stok yönetimi işlemlerini gerçekleştirir.
    """
    
    def __init__(self):
        self.api_key = os.getenv('TRENDYOL_API_KEY')
        self.api_secret = os.getenv('TRENDYOL_API_SECRET')
        self.seller_id = os.getenv('TRENDYOL_SELLER_ID')
        self.base_url = 'https://api.trendyol.com/sapigw'
        
        if not all([self.api_key, self.api_secret, self.seller_id]):
            raise ValueError("Trendyol API kimlik bilgileri eksik!")
            
    def _get_headers(self) -> Dict[str, str]:
        """API istekleri için gerekli header'ları oluşturur."""
        return {
            'Authorization': f'Basic {self.api_key}:{self.api_secret}',
            'User-Agent': 'FinAsis/1.0',
            'Content-Type': 'application/json'
        }
        
    def sync_orders(self, start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Belirtilen tarih aralığındaki siparişleri çeker.
        
        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            
        Returns:
            List[Dict]: Sipariş listesi
        """
        try:
            endpoint = f"{self.base_url}/suppliers/{self.seller_id}/orders"
            params = {}
            if start_date:
                params['startDate'] = start_date.isoformat()
            if end_date:
                params['endDate'] = end_date.isoformat()
                
            response = requests.get(endpoint, headers=self._get_headers(), params=params)
            response.raise_for_status()
            
            return response.json()['content']
            
        except Exception as e:
            logger.error(f"Trendyol sipariş senkronizasyonu hatası: {str(e)}")
            return []
            
    def sync_products(self) -> List[Dict]:
        """
        Satıcının tüm ürünlerini çeker.
        
        Returns:
            List[Dict]: Ürün listesi
        """
        try:
            endpoint = f"{self.base_url}/suppliers/{self.seller_id}/products"
            response = requests.get(endpoint, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()['content']
            
        except Exception as e:
            logger.error(f"Trendyol ürün senkronizasyonu hatası: {str(e)}")
            return []
            
    def update_stock(self, barcode: str, quantity: int) -> bool:
        """
        Ürün stok miktarını günceller.
        
        Args:
            barcode: Ürün barkodu
            quantity: Yeni stok miktarı
            
        Returns:
            bool: İşlem başarılı ise True
        """
        try:
            endpoint = f"{self.base_url}/suppliers/{self.seller_id}/products/stock-updates"
            data = {
                "items": [{
                    "barcode": barcode,
                    "quantity": quantity
                }]
            }
            
            response = requests.put(endpoint, headers=self._get_headers(), json=data)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Trendyol stok güncelleme hatası: {str(e)}")
            return False
            
    def push_invoice_data(self, order_number: str, invoice_data: Dict) -> bool:
        """
        Sipariş için fatura bilgilerini gönderir.
        
        Args:
            order_number: Sipariş numarası
            invoice_data: Fatura bilgileri
            
        Returns:
            bool: İşlem başarılı ise True
        """
        try:
            endpoint = f"{self.base_url}/suppliers/{self.seller_id}/orders/{order_number}/invoice"
            response = requests.post(endpoint, headers=self._get_headers(), json=invoice_data)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Trendyol fatura gönderme hatası: {str(e)}")
            return False 