# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class BaseIntegration(ABC):
    """Tüm entegrasyonlar için temel sınıf"""
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'INTEGRATION_CACHE_TIMEOUT', 300)
        self.retry_count = getattr(settings, 'INTEGRATION_RETRY_COUNT', 3)
        self.retry_delay = getattr(settings, 'INTEGRATION_RETRY_DELAY', 1)
    
    @abstractmethod
    def authenticate(self) -> Dict[str, Any]:
        """Entegrasyon için kimlik doğrulama"""
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Kimlik bilgilerinin doğruluğunu kontrol et"""
        pass
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Önbellekten veri al"""
        return cache.get(f"{self.__class__.__name__}:{key}")
    
    def set_cached_data(self, key: str, value: Any) -> None:
        """Veriyi önbelleğe kaydet"""
        cache.set(f"{self.__class__.__name__}:{key}", value, self.cache_timeout)
    
    def clear_cache(self, key: str = None) -> None:
        """Önbelleği temizle"""
        if key:
            cache.delete(f"{self.__class__.__name__}:{key}")
        else:
            cache.delete_pattern(f"{self.__class__.__name__}:*")
    
    def retry_on_failure(self, func, *args, **kwargs):
        """Hata durumunda yeniden deneme"""
        last_exception = None
        for attempt in range(self.retry_count):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Entegrasyon hatası (deneme {attempt + 1}/{self.retry_count}): {str(e)}"
                )
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
        raise last_exception

class BaseAPIIntegration(BaseIntegration):
    """API tabanlı entegrasyonlar için temel sınıf"""
    
    def __init__(self):
        super().__init__()
        self.base_url = None
        self.headers = {}
        self.session = None
    
    @abstractmethod
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """API isteği yap"""
        pass
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET isteği yap"""
        return self.make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST isteği yap"""
        return self.make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT isteği yap"""
        return self.make_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE isteği yap"""
        return self.make_request('DELETE', endpoint, **kwargs)

class BaseWebhookIntegration(BaseIntegration):
    """Webhook tabanlı entegrasyonlar için temel sınıf"""
    
    def __init__(self):
        super().__init__()
        self.webhook_url = None
        self.secret_key = None
    
    @abstractmethod
    def verify_webhook(self, request) -> bool:
        """Webhook isteğinin doğruluğunu kontrol et"""
        pass
    
    @abstractmethod
    def process_webhook(self, data: Dict[str, Any]) -> None:
        """Webhook verilerini işle"""
        pass
    
    def generate_signature(self, data: Dict[str, Any]) -> str:
        """Webhook imzası oluştur"""
        pass

class BaseFileIntegration(BaseIntegration):
    """Dosya tabanlı entegrasyonlar için temel sınıf"""
    
    def __init__(self):
        super().__init__()
        self.storage_path = None
        self.allowed_extensions = []
    
    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """Dosyanın geçerliliğini kontrol et"""
        pass
    
    @abstractmethod
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Dosyayı işle"""
        pass
    
    def get_file_extension(self, file_path: str) -> str:
        """Dosya uzantısını al"""
        return file_path.split('.')[-1].lower()
    
    def is_allowed_extension(self, file_path: str) -> bool:
        """Dosya uzantısının izin verilenler arasında olup olmadığını kontrol et"""
        return self.get_file_extension(file_path) in self.allowed_extensions 