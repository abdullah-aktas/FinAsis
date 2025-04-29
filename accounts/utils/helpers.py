# -*- coding: utf-8 -*-
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import logging
import pyotp
from ..models import User

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """İstemci IP adresini döndürür"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def handle_failed_login(username, ip_address):
    """Başarısız giriş denemelerini yönetir"""
    cache_key = f'login_attempts_{username}'
    attempts = cache.get(cache_key, 0) + 1
    cache.set(cache_key, attempts, timeout=900)  # 15 dakika
    
    if attempts >= 5:
        try:
            user = User.objects.get(username=username)
            user.failed_login_attempts = attempts
            user.account_locked_until = timezone.now() + timezone.timedelta(minutes=15)
            user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
            logger.warning(f"Hesap kilitlendi: {username} (IP: {ip_address})")
        except User.DoesNotExist:
            pass

def generate_two_factor_secret():
    """İki faktörlü kimlik doğrulama için yeni bir secret oluşturur"""
    return pyotp.random_base32()

def verify_two_factor_code(secret, code):
    """İki faktörlü kimlik doğrulama kodunu doğrular"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def get_password_expiry_date():
    """Şifre süre sonu tarihini döndürür"""
    return timezone.now() + timezone.timedelta(
        days=getattr(settings, 'PASSWORD_EXPIRY_DAYS', 90)
    )

def send_password_expiry_notification(user):
    """Şifre süre sonu bildirimi gönderir"""
    if user.is_password_expired():
        logger.warning(f"Kullanıcı şifresi süresi doldu: {user.username}")
        # Burada e-posta gönderme işlemi yapılabilir
        # from django.core.mail import send_mail
        # send_mail(...)

def check_account_security(user, request):
    """Hesap güvenliğini kontrol eder"""
    security_checks = []
    
    # Şifre süresi kontrolü
    if user.is_password_expired():
        security_checks.append({
            'type': 'password_expired',
            'message': 'Şifrenizin süresi dolmuş. Lütfen değiştirin.'
        })
    
    # İki faktörlü kimlik doğrulama kontrolü
    if not user.two_factor_enabled:
        security_checks.append({
            'type': 'two_factor_disabled',
            'message': 'İki faktörlü kimlik doğrulama etkin değil.'
        })
    
    # IP değişikliği kontrolü
    if user.last_login_ip and user.last_login_ip != get_client_ip(request):
        security_checks.append({
            'type': 'ip_changed',
            'message': 'Son giriş IP adresiniz değişti.'
        })
    
    return security_checks 