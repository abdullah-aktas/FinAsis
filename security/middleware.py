# -*- coding: utf-8 -*-
"""
OWASP Top 10 Security Middleware ve Validators
Django uygulaması için kapsamlı güvenlik kontrolleri
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.exceptions import ValidationError
import re
import html
import json
import logging
from urllib.parse import urlencode
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.shortcuts import resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django_otp import devices_for_user

logger = logging.getLogger(__name__)


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """
    SQL Injection saldırılarına karşı ek koruma katmanı.
    Django ORM zaten koruma sağlar, bu ek bir savunma katmanıdır.
    """

    # Yaygın SQL injection pattern'leri
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\binsert\b.*\binto\b.*\bvalues\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(;.*\b(drop|delete|insert|update)\b)",
        r"(\bor\b.*\b=\b.*\b--)",
        r"(\'\s*or\s*\'1\'\s*=\s*\'1)",
        r"(\"\s*or\s*\"1\"\s*=\s*\"1)",
    ]

    def process_request(self, request):
        """Request parametrelerinde SQL injection kontrolü"""
        # GET parametrelerini kontrol et
        for key, value in request.GET.items():
            if self._contains_sql_injection(str(value)):
                logger.warning(
                    f"SQL Injection attempt detected in GET parameter '{key}': {value}",
                    extra={"ip": self._get_client_ip(request)},
                )
                return HttpResponseForbidden("Güvenlik ihlali tespit edildi.")

        # POST parametrelerini kontrol et
        if request.method == "POST":
            try:
                # JSON body için
                if request.content_type == "application/json":
                    body = json.loads(request.body)
                    if self._check_dict_for_sql_injection(body):
                        logger.warning(
                            "SQL Injection attempt detected in POST body",
                            extra={"ip": self._get_client_ip(request)},
                        )
                        return HttpResponseForbidden("Güvenlik ihlali tespit edildi.")
                # Form data için
                else:
                    for key, value in request.POST.items():
                        if self._contains_sql_injection(str(value)):
                            logger.warning(
                                f"SQL Injection attempt detected in POST parameter '{key}': {value}",
                                extra={"ip": self._get_client_ip(request)},
                            )
                            return HttpResponseForbidden(
                                "Güvenlik ihlali tespit edildi."
                            )
            except Exception as e:
                logger.error(f"Error checking SQL injection: {e}")

        return None

    def _contains_sql_injection(self, value: str) -> bool:
        """String'de SQL injection pattern'i var mı kontrol et"""
        value_lower = value.lower()
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False

    def _check_dict_for_sql_injection(self, data: dict) -> bool:
        """Dictionary içinde recursive olarak SQL injection kontrol et"""
        for key, value in data.items():
            if isinstance(value, str):
                if self._contains_sql_injection(value):
                    return True
            elif isinstance(value, dict):
                if self._check_dict_for_sql_injection(value):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        if self._contains_sql_injection(item):
                            return True
                    elif isinstance(item, dict):
                        if self._check_dict_for_sql_injection(item):
                            return True
        return False

    def _get_client_ip(self, request) -> str:
        """Client IP adresini al"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class XSSProtectionMiddleware(MiddlewareMixin):
    """
    Cross-Site Scripting (XSS) saldırılarına karşı koruma.
    Kullanıcı girdilerini sanitize eder.
    """

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>",
    ]

    def process_request(self, request):
        """Request'te XSS pattern'lerini kontrol et"""
        # GET parametrelerini kontrol et
        for key, value in request.GET.items():
            if self._contains_xss(str(value)):
                logger.warning(
                    f"XSS attempt detected in GET parameter '{key}': {value}",
                    extra={"ip": self._get_client_ip(request)},
                )
                return HttpResponseForbidden("XSS saldırısı tespit edildi.")

        # POST parametrelerini kontrol et (sadece uyarı ver, sanitize et)
        if request.method == "POST":
            for key, value in request.POST.items():
                if self._contains_xss(str(value)):
                    logger.warning(
                        f"Potential XSS in POST parameter '{key}': {value}",
                        extra={"ip": self._get_client_ip(request)},
                    )
                    # POST için sanitize yap ama reddetme
                    # Template'lerde |escape kullanılmalı

        return None

    def _contains_xss(self, value: str) -> bool:
        """String'de XSS pattern'i var mı kontrol et"""
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def _get_client_ip(self, request) -> str:
        """Client IP adresini al"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class SecureHeadersMiddleware(MiddlewareMixin):
    """
    Güvenlik başlıklarını response'a ekler.
    OWASP önerilerine uygun header'lar.
    """

    def process_response(self, request, response):
        """Response'a güvenlik başlıklarını ekle"""

        # X-Content-Type-Options: MIME type sniffing'i engelle
        response["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Clickjacking saldırılarını engelle
        response["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Tarayıcı XSS korumasını aktifleştir
        response["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Referrer bilgisi sızmasını engelle
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Tarayıcı özelliklerini kısıtla
        response["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

        return response


def sanitize_input(value: str, allow_html: bool = False) -> str:
    """
    Kullanıcı girdisini güvenli hale getirir.

    Args:
        value: Temizlenecek string
        allow_html: HTML'e izin verilsin mi

    Returns:
        Temizlenmiş string
    """
    if not isinstance(value, str):
        return value

    # HTML escape (XSS koruması)
    if not allow_html:
        value = html.escape(value)

    # SQL injection riski olan karakterleri temizle
    # Django ORM kullanıldığı için ekstra önlem
    dangerous_chars = ["--", "/*", "*/", "xp_", "sp_"]
    for char in dangerous_chars:
        value = value.replace(char, "")

    return value.strip()


def validate_email_security(email: str) -> bool:
    """
    Email adresinin güvenli olup olmadığını kontrol eder.
    Disposable email servislerini engeller.
    """
    # Temel email format kontrolü
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ValidationError("Geçersiz email formatı")

    # Yasaklı domain'leri kontrol et
    banned_domains = [
        "tempmail.com",
        "throwaway.email",
        "10minutemail.com",
        "guerrillamail.com",
        "mailinator.com",
        "trashmail.com",
    ]

    domain = email.split("@")[1].lower()
    if domain in banned_domains:
        raise ValidationError("Bu email sağlayıcısı kabul edilmiyor")

    return True


def validate_password_strength(password: str) -> dict:
    """
    Şifre gücünü kontrol eder ve detaylı rapor döner.

    Returns:
        {
            'valid': bool,
            'score': int (0-100),
            'issues': list,
            'suggestions': list
        }
    """
    issues = []
    suggestions = []
    score = 0

    # Minimum uzunluk
    if len(password) < 8:
        issues.append("Şifre en az 8 karakter olmalıdır")
    elif len(password) >= 12:
        score += 25
    elif len(password) >= 8:
        score += 15

    # Büyük harf kontrolü
    if not re.search(r"[A-Z]", password):
        issues.append("En az bir büyük harf içermelidir")
    else:
        score += 20

    # Küçük harf kontrolü
    if not re.search(r"[a-z]", password):
        issues.append("En az bir küçük harf içermelidir")
    else:
        score += 20

    # Rakam kontrolü
    if not re.search(r"\d", password):
        issues.append("En az bir rakam içermelidir")
    else:
        score += 20

    # Özel karakter kontrolü
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("En az bir özel karakter içermelidir")
        suggestions.append("Özel karakter ekleyin (!@#$%^&* gibi)")
    else:
        score += 15

    # Yaygın şifreleri kontrol et
    common_passwords = [
        "123456",
        "password",
        "12345678",
        "qwerty",
        "123456789",
        "password123",
        "1234567",
        "admin",
        "letmein",
        "welcome",
    ]
    if password.lower() in common_passwords:
        issues.append("Yaygın kullanılan bir şifre")
        suggestions.append("Daha benzersiz bir şifre kullanın")
        score = max(0, score - 50)

    # Ardışık karakter kontrolü
    if re.search(
        r"(012|123|234|345|456|567|678|789|890|abc|bcd|cde)", password.lower()
    ):
        suggestions.append("Ardışık karakterlerden kaçının")
        score = max(0, score - 10)

    # Tekrarlanan karakterler
    if re.search(r"(.)\1{2,}", password):
        suggestions.append("Aynı karakteri art arda çok kullanmayın")
        score = max(0, score - 10)

    return {
        "valid": len(issues) == 0,
        "score": min(100, score),
        "issues": issues,
        "suggestions": suggestions,
    }


class InputSanitizer:
    """
    Çeşitli input tiplerini güvenli hale getiren utility class
    """

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Dosya adını güvenli hale getirir"""
        # Sadece güvenli karakterlere izin ver
        filename = re.sub(r"[^\w\s.-]", "", filename)
        # Directory traversal saldırılarını engelle
        filename = filename.replace("..", "").replace("/", "").replace("\\", "")
        # Uzunluğu sınırla
        return filename[:255]

    @staticmethod
    def sanitize_url(url: str) -> str:
        """URL'yi güvenli hale getirir"""
        # javascript: ve data: protokollerini engelle
        if re.match(r"^(javascript|data|vbscript):", url, re.IGNORECASE):
            raise ValidationError("Güvenli olmayan URL protokolü")

        # Sadece http/https'e izin ver
        if not re.match(r"^https?://", url, re.IGNORECASE):
            raise ValidationError("Sadece HTTP/HTTPS URL'leri kabul edilir")

        return url

    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Telefon numarasını temizler"""
        # Sadece rakamları al
        phone = re.sub(r"\D", "", phone)

        # Türkiye telefon numarası formatı (10-11 haneli)
        if len(phone) < 10 or len(phone) > 11:
            raise ValidationError("Geçersiz telefon numarası formatı")

        return phone

    @staticmethod
    def sanitize_turkish_id(tc_no: str) -> str:
        """TC Kimlik numarasını doğrular ve temizler"""
        # Sadece rakamları al
        tc_no = re.sub(r"\D", "", tc_no)

        # 11 haneli olmalı
        if len(tc_no) != 11:
            raise ValidationError("TC Kimlik numarası 11 haneli olmalıdır")

        # İlk hane 0 olamaz
        if tc_no[0] == "0":
            raise ValidationError("Geçersiz TC Kimlik numarası")

        # Algoritma kontrolü
        if not InputSanitizer._validate_tc_checksum(tc_no):
            raise ValidationError("Geçersiz TC Kimlik numarası")

        return tc_no

    @staticmethod
    def _validate_tc_checksum(tc_no: str) -> bool:
        """TC Kimlik numarası checksum kontrolü"""
        if len(tc_no) != 11:
            return False

        digits = [int(d) for d in tc_no]

        # 10. hane kontrolü
        sum_odd = sum(digits[0:9:2])
        sum_even = sum(digits[1:8:2])
        digit_10 = (sum_odd * 7 - sum_even) % 10

        if digits[9] != digit_10:
            return False

        # 11. hane kontrolü
        digit_11 = sum(digits[0:10]) % 10

        return digits[10] == digit_11


class SessionIdleTimeoutMiddleware(MiddlewareMixin):
    """
    Kullanıcı oturumunu belirli bir süre hareketsiz kaldığında sonlandırır.
    """

    session_key_name = "_last_activity_ts"

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        timeout = getattr(settings, "SESSION_IDLE_TIMEOUT", 0)
        if timeout <= 0:
            return None

        current_ts = timezone.now().timestamp()
        last_activity = request.session.get(self.session_key_name)
        if last_activity is not None:
            idle_seconds = current_ts - last_activity
            if idle_seconds > timeout:
                actor = request.user
                try:
                    from common.services.audit_logger import log_security_event

                    log_security_event(
                        action="session.timeout",
                        actor=actor,
                        request=request,
                        resource=f"user:{actor.pk}",
                        metadata={"idle_seconds": int(idle_seconds)},
                        success=True,
                    )
                except (
                    Exception
                ):  # pragma: no cover - audit log hataları session'ı engellemesin
                    logger.exception("Session timeout audit log kaydedilemedi.")

                logout(request)
                request.session.flush()
                login_url = reverse("accounts:login")
                return HttpResponseRedirect(f"{login_url}?timeout=1")

        request.session[self.session_key_name] = current_ts
        return None


class ConcurrentSessionControlMiddleware(MiddlewareMixin):
    """
    Bir kullanıcının eş zamanlı oturum sayısını sınırlar.
    """

    cache_key_template = "user:sessions:{user_id}"

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        limit = getattr(settings, "SESSION_CONCURRENT_LIMIT", 0)
        if limit <= 0:
            return None

        if not request.session.session_key:
            request.session.save()

        session_key = request.session.session_key
        cache_key = self.cache_key_template.format(user_id=request.user.pk)
        sessions = cache.get(cache_key, [])

        if session_key in sessions:
            sessions.remove(session_key)
        sessions.append(session_key)

        removed = []
        if len(sessions) > limit:
            removed = sessions[:-limit]
            sessions = sessions[-limit:]
            for key in removed:
                Session.objects.filter(session_key=key).delete()

        cache.set(
            cache_key, sessions, getattr(settings, "SESSION_COOKIE_AGE", 60 * 60 * 12)
        )

        if removed:
            try:
                from common.services.audit_logger import log_security_event

                log_security_event(
                    action="session.limit_exceeded",
                    actor=request.user,
                    request=request,
                    resource=f"user:{request.user.pk}",
                    metadata={"terminated_session_keys": removed},
                    success=True,
                )
            except Exception:  # pragma: no cover
                logger.exception("Concurrent session audit log kaydedilemedi.")

        return None


class OTPEnforcementMiddleware(MiddlewareMixin):
    """
    MFA cihazı bulunan kullanıcıların doğrulama yapmadan uygulamaya erişmesini engeller.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.exempt_paths = None

    def _build_exempt_paths(self):
        return {
            resolve_url("accounts:otp_verify"),
            resolve_url("accounts:otp_setup"),
            resolve_url("accounts:otp_disable"),
            resolve_url("accounts:logout"),
            resolve_url("accounts:login"),
        }

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        if self.exempt_paths is None:
            self.exempt_paths = self._build_exempt_paths()

        path = request.path
        if path.startswith("/static/") or path.startswith("/media/"):
            return None

        if path in self.exempt_paths:
            return None

        confirmed_devices = list(devices_for_user(request.user, confirmed=True))
        if not confirmed_devices:
            return None

        if getattr(request, "otp_device", None) is not None:
            return None

        next_url = request.get_full_path()
        if not url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            next_url = resolve_url(settings.LOGIN_REDIRECT_URL)

        params = urlencode({"next": next_url})
        verify_url = f"{resolve_url('accounts:otp_verify')}?{params}"
        return HttpResponseRedirect(verify_url)
