from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseIntegration(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.access_token = config.get('access_token')
        self.is_active = config.get('is_active', True)
        self.last_sync = None
        
    @abstractmethod
    async def authenticate(self) -> bool:
        """API kimlik doğrulaması yapar"""
        pass
    
    @abstractmethod
    async def sync_data(self) -> Dict[str, Any]:
        """Veri senkronizasyonu yapar"""
        pass
    
    @abstractmethod
    async def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Webhook isteklerini işler"""
        pass
    
    def log_sync(self, status: str, error_message: Optional[str] = None) -> None:
        """Senkronizasyon loglarını kaydeder"""
        logger.info(f"Sync completed for {self.__class__.__name__}")
        logger.info(f"Status: {status}")
        if error_message:
            logger.error(f"Error: {error_message}")
        self.last_sync = datetime.now()
    
    def validate_config(self) -> bool:
        """Konfigürasyon doğrulaması yapar"""
        required_fields = ['api_key', 'access_token']
        return all(field in self.config for field in required_fields)
    
    async def execute_sync(self) -> Dict[str, Any]:
        """Senkronizasyon işlemini yürütür"""
        if not self.is_active:
            return {"status": "error", "message": "Integration is not active"}
            
        if not self.validate_config():
            return {"status": "error", "message": "Invalid configuration"}
            
        try:
            if not await self.authenticate():
                return {"status": "error", "message": "Authentication failed"}
                
            result = await self.sync_data()
            self.log_sync("success")
            return {"status": "success", "data": result}
            
        except Exception as e:
            error_message = str(e)
            self.log_sync("error", error_message)
            return {"status": "error", "message": error_message} 