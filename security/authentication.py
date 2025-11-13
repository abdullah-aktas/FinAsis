# -*- coding: utf-8 -*-
"""
Authentication Hardening - JWT & Security
Gelişmiş authentication, session yönetimi ve güvenlik
"""

from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from typing import Dict, Any
import logging

# JWT imports - optional, sadece kuruluysa kullan
try:
    from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
    from rest_framework_simplejwt.exceptions import TokenError  # type: ignore
    HAS_JWT = True
except ImportError:
    HAS_JWT = False
    RefreshToken = None  # type: ignore
    TokenError = Exception

User = get_user_model()
logger = logging.getLogger(__name__)


class EnhancedPasswordValidator:
    """
    Gelişmiş şifre doğrulayıcı
    Django'nun default validator'larına ek kontroller
    """
    
    def validate(self, password, user=None):
        """Şifre doğrulama"""
        errors = []
        
        # Minimum uzunluk
        if len(password) < 12:
            errors.append("Şifre en az 12 karakter olmalıdır.")
        
        # Büyük harf kontrolü
        if not any(c.isupper() for c in password):
            errors.append("Şifre en az bir büyük harf içermelidir.")
        
        # Küçük harf kontrolü
        if not any(c.islower() for c in password):
            errors.append("Şifre en az bir küçük harf içermelidir.")
        
        # Rakam kontrolü
        if not any(c.isdigit() for c in password):
            errors.append("Şifre en az bir rakam içermelidir.")
        
        # Özel karakter kontrolü
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(c in special_chars for c in password):
            errors.append("Şifre en az bir özel karakter içermelidir (!@#$%^&* gibi).")
        
        # Ardışık karakterler
        for i in range(len(password) - 2):
            if ord(password[i]) + 1 == ord(password[i+1]) == ord(password[i+2]) - 1:
                errors.append("Şifre ardışık karakterler içeremez (örn: abc, 123).")
                break
        
        # Tekrarlanan karakterler
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                errors.append("Şifre aynı karakteri 3 kez üst üste içeremez.")
                break
        
        # Kullanıcı bilgisi benzerliği
        if user:
            user_attrs = [
                user.username,
                user.email.split('@')[0] if hasattr(user, 'email') else '',
                user.first_name if hasattr(user, 'first_name') else '',
                user.last_name if hasattr(user, 'last_name') else '',
            ]
            
            for attr in user_attrs:
                if attr and len(attr) >= 3 and attr.lower() in password.lower():
                    errors.append("Şifre kullanıcı bilgilerinize benzememelidir.")
                    break
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Yardım metni"""
        return (
            "Şifreniz en az 12 karakter olmalı ve büyük harf, küçük harf, "
            "rakam ve özel karakter içermelidir."
        )


class JWTAuthenticationService:
    """
    JWT token yönetimi için servis sınıfı
    """
    
    @staticmethod
    def create_tokens_for_user(user) -> Dict[str, str]:
        """
        Kullanıcı için JWT token pair oluştur
        
        Returns:
            dict: {'access': str, 'refresh': str}
        """
        if not HAS_JWT or RefreshToken is None:
            raise ImportError("djangorestframework-simplejwt kurulu değil")
        
        refresh = RefreshToken.for_user(user)
        
        # Custom claims ekle
        refresh['username'] = user.username
        refresh['email'] = user.email
        refresh['is_staff'] = user.is_staff
        
        logger.info(f"JWT tokens created for user: {user.username}")
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Refresh token kullanarak yeni access token al
        
        Args:
            refresh_token: Refresh token string
        
        Returns:
            str: Yeni access token
        """
        if not HAS_JWT or RefreshToken is None:
            raise ImportError("djangorestframework-simplejwt kurulu değil")
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            logger.info("Access token refreshed successfully")
            return access_token
            
        except TokenError as e:
            logger.warning(f"Token refresh failed: {e}")
            raise ValidationError("Geçersiz veya süresi dolmuş refresh token")
    
    @staticmethod
    def blacklist_token(refresh_token: str) -> bool:
        """
        Refresh token'ı blacklist'e ekle (logout)
        
        Args:
            refresh_token: Blacklist'e eklenecek refresh token
        """
        if not HAS_JWT or RefreshToken is None:
            raise ImportError("djangorestframework-simplejwt kurulu değil")
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info("Token blacklisted successfully")
            return True
            
        except TokenError as e:
            logger.warning(f"Token blacklist failed: {e}")
            return False


class SessionSecurityService:
    """
    Session güvenliği için yardımcı fonksiyonlar
    """
    
    @staticmethod
    def create_secure_session(request, user):
        """
        Güvenli session oluştur
        
        Args:
            request: HTTP request
            user: Authenticate edilmiş kullanıcı
        """
        from django.contrib.auth import login
        
        # Session'ı başlat
        login(request, user)
        
        # Session metadata ekle
        request.session['ip_address'] = SessionSecurityService._get_client_ip(request)
        request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:200]
        request.session['login_timestamp'] = str(timedelta(seconds=0))
        
        # Session regenerate (session fixation saldırılarına karşı)
        request.session.cycle_key()
        
        logger.info(
            f"Secure session created for user: {user.username}",
            extra={'ip': request.session['ip_address']}
        )
    
    @staticmethod
    def validate_session_security(request):
        """
        Session güvenliğini doğrula
        IP ve user agent değişikliklerini kontrol et
        
        Returns:
            bool: Session güvenli mi
        """
        if not request.user.is_authenticated:
            return True
        
        current_ip = SessionSecurityService._get_client_ip(request)
        current_ua = request.META.get('HTTP_USER_AGENT', '')[:200]
        
        session_ip = request.session.get('ip_address', '')
        session_ua = request.session.get('user_agent', '')
        
        # IP değişikliği kontrolü (strict mode)
        if session_ip and current_ip != session_ip:
            logger.warning(
                f"Session IP mismatch for user {request.user.username}: "
                f"{session_ip} -> {current_ip}"
            )
            return False
        
        # User agent değişikliği kontrolü
        if session_ua and current_ua != session_ua:
            logger.warning(
                f"Session User-Agent mismatch for user {request.user.username}"
            )
            return False
        
        return True
    
    @staticmethod
    def _get_client_ip(request):
        """Client IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TwoFactorAuthService:
    """
    2FA hazırlık servisi
    django-otp ile entegrasyon için temel yapı
    """
    
    @staticmethod
    def is_2fa_enabled(user):
        """
        Kullanıcı için 2FA aktif mi kontrol et
        
        Returns:
            bool: 2FA aktif mi
        """
        # TODO: django-otp entegrasyonu eklenecek
        return False
    
    @staticmethod
    def generate_2fa_qr_code(user):
        """
        2FA için QR kod oluştur
        
        Returns:
            str: QR kod data URL
        """
        # TODO: django-otp ile TOTP QR kod oluşturulacak
        pass
    
    @staticmethod
    def verify_2fa_token(user, token):
        """
        2FA token doğrula
        
        Args:
            user: Kullanıcı
            token: 6 haneli TOTP token
        
        Returns:
            bool: Token geçerli mi
        """
        # TODO: django-otp ile token doğrulama yapılacak
        pass


def enforce_password_change(user, days=90):
    """
    Şifre değişikliği zorunluluğu kontrol et
    
    Args:
        user: Kullanıcı
        days: Kaç günde bir şifre değişikliği gerekli
    
    Returns:
        bool: Şifre değişikliği gerekli mi
    """
    if not hasattr(user, 'last_password_change'):
        return False
    
    if not user.last_password_change:
        return True
    
    from django.utils import timezone
    days_since_change = (timezone.now() - user.last_password_change).days
    
    return days_since_change >= days
