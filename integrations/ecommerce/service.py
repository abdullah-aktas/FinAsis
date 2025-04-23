from typing import Dict, Any, List, Optional
from datetime import datetime
from django.conf import settings
from ..base import BaseAPIIntegration
from ..services import IntegrationService, APIService

class EcommerceService(APIService):
    """E-ticaret entegrasyonu servisi"""
    
    def __init__(self):
        config = IntegrationService.get_integration_config('ecommerce')
        super().__init__(
            base_url=config.get('base_url'),
            headers={
                'Authorization': f"Bearer {config.get('api_key')}",
                'Content-Type': 'application/json'
            }
        )
    
    def get_products(
        self,
        page: int = 1,
        per_page: int = 50,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ürünleri listele"""
        endpoint = "/products"
        params = {
            'page': page,
            'per_page': per_page
        }
        if category:
            params['category'] = category
        if search:
            params['search'] = search
        return self.get(endpoint, params=params)
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Ürün detaylarını al"""
        endpoint = f"/products/{product_id}"
        return self.get(endpoint)
    
    def create_order(
        self,
        customer_id: str,
        items: List[Dict[str, Any]],
        shipping_address: Dict[str, Any],
        billing_address: Dict[str, Any],
        payment_method: str
    ) -> Dict[str, Any]:
        """Sipariş oluştur"""
        endpoint = "/orders"
        data = {
            'customer_id': customer_id,
            'items': items,
            'shipping_address': shipping_address,
            'billing_address': billing_address,
            'payment_method': payment_method
        }
        return self.post(endpoint, json=data)
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Sipariş durumunu kontrol et"""
        endpoint = f"/orders/{order_id}/status"
        return self.get(endpoint)
    
    def update_order_status(
        self,
        order_id: str,
        status: str,
        tracking_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sipariş durumunu güncelle"""
        endpoint = f"/orders/{order_id}/status"
        data = {'status': status}
        if tracking_number:
            data['tracking_number'] = tracking_number
        return self.put(endpoint, json=data)
    
    def get_customer_orders(
        self,
        customer_id: str,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Müşteri siparişlerini listele"""
        endpoint = f"/customers/{customer_id}/orders"
        params = {
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def get_categories(self) -> Dict[str, Any]:
        """Kategorileri listele"""
        endpoint = "/categories"
        return self.get(endpoint)
    
    def get_inventory_status(self, product_id: str) -> Dict[str, Any]:
        """Stok durumunu kontrol et"""
        endpoint = f"/products/{product_id}/inventory"
        return self.get(endpoint)
    
    def update_inventory(
        self,
        product_id: str,
        quantity: int,
        operation: str = 'add'
    ) -> Dict[str, Any]:
        """Stok güncelle"""
        endpoint = f"/products/{product_id}/inventory"
        data = {
            'quantity': quantity,
            'operation': operation
        }
        return self.put(endpoint, json=data)
    
    def get_promotions(
        self,
        active_only: bool = True,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Kampanyaları listele"""
        endpoint = "/promotions"
        params = {'active_only': active_only}
        if category:
            params['category'] = category
        return self.get(endpoint, params=params)
    
    def apply_promotion(
        self,
        order_id: str,
        promotion_code: str
    ) -> Dict[str, Any]:
        """Kampanya uygula"""
        endpoint = f"/orders/{order_id}/apply-promotion"
        data = {'promotion_code': promotion_code}
        return self.post(endpoint, json=data)
    
    def get_shipping_methods(
        self,
        country: str,
        postal_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Kargo yöntemlerini listele"""
        endpoint = "/shipping-methods"
        params = {'country': country}
        if postal_code:
            params['postal_code'] = postal_code
        return self.get(endpoint, params=params)
    
    def calculate_shipping_cost(
        self,
        items: List[Dict[str, Any]],
        shipping_address: Dict[str, Any],
        shipping_method: str
    ) -> Dict[str, Any]:
        """Kargo ücretini hesapla"""
        endpoint = "/shipping/calculate"
        data = {
            'items': items,
            'shipping_address': shipping_address,
            'shipping_method': shipping_method
        }
        return self.post(endpoint, json=data)
    
    def get_payment_methods(self) -> Dict[str, Any]:
        """Ödeme yöntemlerini listele"""
        endpoint = "/payment-methods"
        return self.get(endpoint)
    
    def process_payment(
        self,
        order_id: str,
        payment_method: str,
        payment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ödeme işlemi yap"""
        endpoint = f"/orders/{order_id}/process-payment"
        data = {
            'payment_method': payment_method,
            'payment_details': payment_details
        }
        return self.post(endpoint, json=data)
    
    def get_order_history(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sipariş geçmişini al"""
        endpoint = "/orders/history"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        if status:
            params['status'] = status
        return self.get(endpoint, params=params)
    
    def get_sales_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """Satış raporu al"""
        endpoint = "/reports/sales"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'type': report_type
        }
        return self.get(endpoint, params=params)
    
    def get_customer_details(self, customer_id: str) -> Dict[str, Any]:
        """Müşteri detaylarını al"""
        endpoint = f"/customers/{customer_id}"
        return self.get(endpoint)
    
    def update_customer_details(
        self,
        customer_id: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Müşteri bilgilerini güncelle"""
        endpoint = f"/customers/{customer_id}"
        return self.put(endpoint, json=details)
    
    def get_customer_addresses(self, customer_id: str) -> Dict[str, Any]:
        """Müşteri adreslerini listele"""
        endpoint = f"/customers/{customer_id}/addresses"
        return self.get(endpoint)
    
    def add_customer_address(
        self,
        customer_id: str,
        address: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Müşteri adresi ekle"""
        endpoint = f"/customers/{customer_id}/addresses"
        return self.post(endpoint, json=address)
    
    def get_product_reviews(
        self,
        product_id: str,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Ürün yorumlarını listele"""
        endpoint = f"/products/{product_id}/reviews"
        params = {
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def add_product_review(
        self,
        product_id: str,
        customer_id: str,
        rating: int,
        comment: str
    ) -> Dict[str, Any]:
        """Ürün yorumu ekle"""
        endpoint = f"/products/{product_id}/reviews"
        data = {
            'customer_id': customer_id,
            'rating': rating,
            'comment': comment
        }
        return self.post(endpoint, json=data) 