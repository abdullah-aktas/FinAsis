from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class PermissionError(PermissionDenied):
    """
    İzin hatası için özel istisna
    """
    def __init__(self, message, code=None):
        self.code = code
        super().__init__(message)
        logger.warning(f"İzin hatası: {message} (Kod: {code})")

class RoleError(PermissionDenied):
    """
    Rol hatası için özel istisna
    """
    def __init__(self, message, role_code=None):
        self.role_code = role_code
        super().__init__(message)
        logger.warning(f"Rol hatası: {message} (Rol: {role_code})")

class IPWhitelistError(PermissionDenied):
    """
    IP beyaz listesi hatası için özel istisna
    """
    def __init__(self, message, ip_address=None):
        self.ip_address = ip_address
        super().__init__(message)
        logger.warning(f"IP beyaz listesi hatası: {message} (IP: {ip_address})")

class TwoFactorAuthError(PermissionDenied):
    """
    İki faktörlü kimlik doğrulama hatası için özel istisna
    """
    def __init__(self, message, user=None):
        self.user = user
        super().__init__(message)
        logger.warning(f"2FA hatası: {message} (Kullanıcı: {user})")

class PermissionDelegationError(PermissionDenied):
    """
    İzin devri hatası için özel istisna
    """
    def __init__(self, message, delegator=None, delegatee=None):
        self.delegator = delegator
        self.delegatee = delegatee
        super().__init__(message)
        logger.warning(f"İzin devri hatası: {message} (Devreden: {delegator}, Devralan: {delegatee})")

class AuditLogError(APIException):
    """
    Denetim kaydı hatası için özel istisna
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Denetim kaydı oluşturulurken bir hata oluştu.'
    default_code = 'audit_log_error'

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)
        logger.error(f"Denetim kaydı hatası: {detail} (Kod: {code})")

class CacheError(APIException):
    """
    Önbellek hatası için özel istisna
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Önbellek işlemi sırasında bir hata oluştu.'
    default_code = 'cache_error'

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)
        logger.error(f"Önbellek hatası: {detail} (Kod: {code})") 