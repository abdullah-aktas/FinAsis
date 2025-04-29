# -*- coding: utf-8 -*-
from typing import Any, Dict
import aiohttp
from datetime import datetime, timedelta
from ...base.base_integration import BaseIntegration

class HepsiburadaIntegration(BaseIntegration):
    BASE_URL = "https://marketplace-api.hepsiburada.com"
    
    async def authenticate(self) -> bool:
        """Hepsiburada API kimlik doğrulaması"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(f"{self.BASE_URL}/listings/merchantid", headers=headers) as response:
                    return response.status == 200
        except Exception as e:
            self.log_sync("error", f"Authentication error: {str(e)}")
            return False
    
    async def sync_data(self) -> Dict[str, Any]:
        """Hepsiburada veri senkronizasyonu"""
        try:
            # Siparişleri çek
            orders = await self._fetch_orders()
            # Ürünleri güncelle
            products = await self._sync_products()
            # Stok durumunu güncelle
            inventory = await self._update_inventory()
            
            return {
                "orders": orders,
                "products": products,
                "inventory": inventory
            }
        except Exception as e:
            raise Exception(f"Sync error: {str(e)}")
    
    async def _fetch_orders(self) -> Dict[str, Any]:
        """Son 24 saatteki siparişleri çeker"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            yesterday = datetime.now() - timedelta(days=1)
            params = {
                "startDate": yesterday.strftime("%Y-%m-%d"),
                "endDate": datetime.now().strftime("%Y-%m-%d")
            }
            async with session.get(f"{self.BASE_URL}/orders", headers=headers, params=params) as response:
                return await response.json()
    
    async def _sync_products(self) -> Dict[str, Any]:
        """Ürün bilgilerini senkronize eder"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with session.get(f"{self.BASE_URL}/listings/merchantid", headers=headers) as response:
                return await response.json()
    
    async def _update_inventory(self) -> Dict[str, Any]:
        """Stok durumunu günceller"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with session.get(f"{self.BASE_URL}/inventory", headers=headers) as response:
                return await response.json()
    
    async def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Webhook isteklerini işler"""
        event_type = data.get("eventType")
        if event_type == "ORDER_STATUS_CHANGED":
            return await self._handle_order_status_change(data)
        elif event_type == "PRODUCT_UPDATED":
            return await self._handle_product_update(data)
        return {"status": "error", "message": "Unknown event type"}
    
    async def _handle_order_status_change(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sipariş durumu değişikliklerini işler"""
        order_id = data.get("orderId")
        new_status = data.get("newStatus")
        # Sipariş durumunu güncelle ve muhasebe sistemine aktar
        return {"status": "success", "order_id": order_id, "new_status": new_status}
    
    async def _handle_product_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ürün güncellemelerini işler"""
        product_id = data.get("productId")
        # Ürün bilgilerini güncelle
        return {"status": "success", "product_id": product_id} 