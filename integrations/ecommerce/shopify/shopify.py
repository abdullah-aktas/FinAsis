# -*- coding: utf-8 -*-
from typing import Any, Dict
import shopify
from datetime import datetime, timedelta
from ...base.base_integration import BaseIntegration

class ShopifyIntegration(BaseIntegration):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.shop_url = config.get('shop_url')
        self.api_version = config.get('api_version', '2024-01')
        self._setup_session()
    
    def _setup_session(self):
        """Shopify API oturumunu yapılandırır"""
        shopify.Session.setup(api_key=self.api_key, secret=self.access_token)
        self.session = shopify.Session(self.shop_url, self.api_version, self.access_token)
        shopify.ShopifyResource.activate_session(self.session)
    
    async def authenticate(self) -> bool:
        """Shopify API kimlik doğrulaması"""
        try:
            shop = shopify.Shop.current()
            return bool(shop)
        except Exception as e:
            self.log_sync("error", f"Authentication error: {str(e)}")
            return False
    
    async def sync_data(self) -> Dict[str, Any]:
        """Shopify veri senkronizasyonu"""
        try:
            # Siparişleri çek
            orders = await self._fetch_orders()
            # Ürünleri senkronize et
            products = await self._sync_products()
            # Müşteri verilerini güncelle
            customers = await self._sync_customers()
            
            return {
                "orders": orders,
                "products": products,
                "customers": customers
            }
        except Exception as e:
            raise Exception(f"Sync error: {str(e)}")
    
    async def _fetch_orders(self) -> Dict[str, Any]:
        """Son 24 saatteki siparişleri çeker"""
        yesterday = datetime.now() - timedelta(days=1)
        orders = shopify.Order.find(
            created_at_min=yesterday.isoformat(),
            status='any'
        )
        return [order.to_dict() for order in orders]
    
    async def _sync_products(self) -> Dict[str, Any]:
        """Ürün bilgilerini senkronize eder"""
        products = shopify.Product.find()
        return [product.to_dict() for product in products]
    
    async def _sync_customers(self) -> Dict[str, Any]:
        """Müşteri verilerini senkronize eder"""
        customers = shopify.Customer.find()
        return [customer.to_dict() for customer in customers]
    
    async def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Webhook isteklerini işler"""
        topic = data.get("topic")
        if topic == "orders/create":
            return await self._handle_new_order(data)
        elif topic == "products/update":
            return await self._handle_product_update(data)
        return {"status": "error", "message": "Unknown webhook topic"}
    
    async def _handle_new_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Yeni sipariş webhook'unu işler"""
        order_data = data.get("order", {})
        order_id = order_data.get("id")
        # Siparişi muhasebe sistemine aktar
        # Stok güncellemesi yap
        return {"status": "success", "order_id": order_id}
    
    async def _handle_product_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ürün güncelleme webhook'unu işler"""
        product_data = data.get("product", {})
        product_id = product_data.get("id")
        # Ürün bilgilerini güncelle
        return {"status": "success", "product_id": product_id}
    
    def __del__(self):
        """Oturumu temizle"""
        shopify.ShopifyResource.clear_session() 