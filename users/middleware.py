# -*- coding: utf-8 -*-
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.conf import settings
from ipware import get_client_ip
from .models import UserActivity, UserSession, IPWhitelist

User = get_user_model()

class UserActivityMiddleware(MiddlewareMixin):
    """Kullanıcı aktivitelerini kaydeden ara yazılım"""
    def process_request(self, request):
        if request.user.is_authenticated:
            # Son aktivite zamanını güncelle
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
            
            # Aktivite kaydı oluştur
            UserActivity.objects.create(
                user=request.user,
                action=request.path,
                details=f"{request.method} {request.path}",
                ip_address=get_client_ip(request)[0],
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

class UserSessionMiddleware(MiddlewareMixin):
    """Kullanıcı oturumlarını yöneten ara yazılım"""
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request, 'session'):
            # Oturum bilgilerini güncelle
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.update_or_create(
                    session_key=session_key,
                    defaults={
                        'user': request.user,
                        'ip_address': get_client_ip(request)[0],
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'last_activity': timezone.now()
                    }
                )

class IPWhitelistMiddleware(MiddlewareMixin):
    """IP beyaz listesi kontrolü yapan ara yazılım"""
    def process_request(self, request):
        # Admin paneline erişim kontrolü
        if request.path.startswith('/admin/'):
            client_ip = get_client_ip(request)[0]
            if not IPWhitelist.objects.filter(ip_address=client_ip).exists():
                return HttpResponseForbidden("Bu IP adresinden erişim izniniz yok.")

class CacheControlMiddleware(MiddlewareMixin):
    """Önbellek kontrolü yapan ara yazılım"""
    def process_response(self, request, response):
        if request.user.is_authenticated:
            # Kullanıcı önbelleğini güncelle
            cache_key = f'user_{request.user.id}'
            cache.set(cache_key, request.user, timeout=3600)
            
            # Profil ve tercih önbelleklerini güncelle
            if hasattr(request.user, 'profile'):
                cache.set(f'profile_{request.user.id}', request.user.profile, timeout=3600)
            if hasattr(request.user, 'preferences'):
                cache.set(f'preferences_{request.user.id}', request.user.preferences, timeout=3600)
        
        return response

class TwoFactorAuthMiddleware(MiddlewareMixin):
    """İki faktörlü kimlik doğrulama kontrolü yapan ara yazılım"""
    def process_request(self, request):
        if request.user.is_authenticated:
            # İki faktörlü kimlik doğrulama gerektiren yollar
            protected_paths = [
                '/admin/',
                '/api/',
                '/settings/',
            ]
            
            if any(request.path.startswith(path) for path in protected_paths):
                if not request.user.two_factor_enabled:
                    # İki faktörlü kimlik doğrulama gerekli
                    return HttpResponseForbidden("Bu sayfaya erişmek için iki faktörlü kimlik doğrulama gereklidir.")

class NotificationMiddleware(MiddlewareMixin):
    """Bildirim yönetimi yapan ara yazılım"""
    def process_template_response(self, request, response):
        if request.user.is_authenticated:
            # Okunmamış bildirimleri kontrol et
            unread_count = UserNotification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
            
            # Template context'e ekle
            if hasattr(response, 'context_data'):
                response.context_data['unread_notifications_count'] = unread_count
        
        return response

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Güvenlik başlıklarını ekleyen ara yazılım"""
    def process_response(self, request, response):
        # Güvenlik başlıklarını ekle
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'"
        
        return response 