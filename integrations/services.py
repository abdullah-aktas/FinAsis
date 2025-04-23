from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
import requests
import json
import logging
import time
from typing import Any, Dict, Optional
from .base import BaseAPIIntegration

logger = logging.getLogger(__name__)

class IntegrationService:
    """Entegrasyon servisleri için yardımcı sınıf"""
    
    @staticmethod
    def get_integration_config(integration_name: str) -> Dict[str, Any]:
        """Entegrasyon yapılandırmasını al"""
        return getattr(settings, f"{integration_name.upper()}_CONFIG", {})
    
    @staticmethod
    def validate_response(response: requests.Response) -> Dict[str, Any]:
        """API yanıtını doğrula"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Hatası: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON Ayrıştırma Hatası: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Beklenmeyen Hata: {str(e)}")
            raise
    
    @staticmethod
    def handle_rate_limit(response: requests.Response) -> None:
        """Rate limit kontrolü yap"""
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limit aşıldı. {retry_after} saniye bekleniyor...")
            time.sleep(retry_after)
    
    @staticmethod
    def log_integration_error(integration_name: str, error: Exception) -> None:
        """Entegrasyon hatasını logla"""
        logger.error(
            f"{integration_name} entegrasyon hatası: {str(error)}",
            extra={
                'integration': integration_name,
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
        )
    
    @staticmethod
    def cache_integration_data(
        integration_name: str,
        key: str,
        data: Any,
        timeout: int = 300
    ) -> None:
        """Entegrasyon verisini önbelleğe al"""
        cache_key = f"integration:{integration_name}:{key}"
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def get_cached_integration_data(
        integration_name: str,
        key: str
    ) -> Optional[Any]:
        """Önbellekten entegrasyon verisini al"""
        cache_key = f"integration:{integration_name}:{key}"
        return cache.get(cache_key)
    
    @staticmethod
    def clear_integration_cache(integration_name: str, key: str = None) -> None:
        """Entegrasyon önbelleğini temizle"""
        if key:
            cache_key = f"integration:{integration_name}:{key}"
            cache.delete(cache_key)
        else:
            cache.delete_pattern(f"integration:{integration_name}:*")

class APIService(BaseAPIIntegration):
    """Genel API servisi"""
    
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        super().__init__()
        self.base_url = base_url
        self.headers = headers or {}
        self.session = requests.Session()
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """API isteği yap"""
        url = f"{self.base_url}{endpoint}"
        headers = {**self.headers, **kwargs.pop('headers', {})}
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            IntegrationService.handle_rate_limit(response)
            return IntegrationService.validate_response(response)
            
        except Exception as e:
            IntegrationService.log_integration_error(self.__class__.__name__, e)
            raise
    
    def authenticate(self) -> Dict[str, Any]:
        """Kimlik doğrulama"""
        # Alt sınıflar bu metodu override edebilir
        return {}
    
    def validate_credentials(self) -> bool:
        """Kimlik bilgilerini doğrula"""
        try:
            self.authenticate()
            return True
        except Exception:
            return False

class WebhookService:
    """Webhook servisi"""
    
    @staticmethod
    def verify_signature(
        payload: str,
        signature: str,
        secret_key: str
    ) -> bool:
        """Webhook imzasını doğrula"""
        # Alt sınıflar bu metodu override edebilir
        return True
    
    @staticmethod
    def process_webhook(
        integration_name: str,
        payload: Dict[str, Any]
    ) -> None:
        """Webhook verilerini işle"""
        try:
            # Webhook verilerini işle
            logger.info(
                f"{integration_name} webhook verisi alındı",
                extra={'payload': payload}
            )
        except Exception as e:
            IntegrationService.log_integration_error(integration_name, e)
            raise

class FileService:
    """Dosya servisi"""
    
    @staticmethod
    def validate_file_type(
        file_path: str,
        allowed_types: list
    ) -> bool:
        """Dosya tipini doğrula"""
        file_extension = file_path.split('.')[-1].lower()
        return file_extension in allowed_types
    
    @staticmethod
    def process_file(
        integration_name: str,
        file_path: str,
        processor: callable
    ) -> Dict[str, Any]:
        """Dosyayı işle"""
        try:
            result = processor(file_path)
            logger.info(
                f"{integration_name} dosya işleme başarılı",
                extra={'file_path': file_path}
            )
            return result
        except Exception as e:
            IntegrationService.log_integration_error(integration_name, e)
            raise 