# -*- coding: utf-8 -*-
"""
RBAC Middleware
Her HTTP isteğinde otomatik yetki kontrolü yapar
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .permissions import check_url_permission, get_user_role_category
import logging
import re

logger = logging.getLogger(__name__)


class RBACMiddleware(MiddlewareMixin):
    """
    Role-Based Access Control Middleware
    Her isteği role göre kontrol eder
    """
    
    # Bu URL'ler kontrol edilmez (herkes erişebilir)
    EXEMPT_URLS = [
        r'^/$',  # Ana sayfa
        r'^/accounts/login',
        r'^/accounts/logout',
        r'^/accounts/register',
        r'^/accounts/password',
        r'^/static/',
        r'^/media/',
        r'^/health/',
        r'^/api/public/',
        r'^/legal/',
        r'^/privacy/',
        r'^/terms/',
        r'^/contact/',
        r'^/about/',
        r'^/__debug__/',  # Django Debug Toolbar
    ]
    
    # Bu URL'ler özel kontrol gerektirir (logged in olmalı ama role göre değil)
    AUTH_REQUIRED_URLS = [
        r'^/accounts/profile',
        r'^/accounts/settings',
        r'^/dashboard',
    ]
    
    def process_request(self, request):
        """
        Her request'te çalışır
        """
        # Middleware'i devre dışı bırakma (test için)
        if getattr(request, '_rbac_exempt', False):
            return None
        
        # URL kontrolü
        path = request.path
        
        # Exempt URL'leri kontrol et
        if self._is_exempt_url(path):
            return None
        
        # Kullanıcı giriş yapmamışsa
        if not request.user.is_authenticated:
            # Auth required URL'lerde login'e yönlendir
            if self._is_auth_required_url(path):
                messages.info(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
                return HttpResponseRedirect(reverse('accounts:login') + f'?next={path}')
            # Diğerlerinde izin ver (public pages)
            return None
        
        # Kullanıcı giriş yapmışsa, URL permission kontrolü
        if not check_url_permission(request.user, path):
            user_role = get_user_role_category(request.user)
            
            # Log kaydet
            logger.warning(
                f"RBAC: Yetkisiz erişim engellendi | "
                f"User: {request.user.username} | "
                f"Role: {user_role} | "
                f"Path: {path} | "
                f"Method: {request.method} | "
                f"IP: {self._get_client_ip(request)}"
            )
            
            # AJAX request ise JSON döndür
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'error': True,
                    'message': 'Bu işlemi yapmaya yetkiniz yok.',
                    'code': 'PERMISSION_DENIED'
                }, status=403)
            
            # Normal request ise mesaj göster ve dashboard'a yönlendir
            messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
            return HttpResponseRedirect(reverse('accounts:dashboard'))
        
        # Yetki varsa devam et
        return None
    
    def _is_exempt_url(self, path: str) -> bool:
        """URL exempt mi kontrol et"""
        for pattern in self.EXEMPT_URLS:
            if re.match(pattern, path):
                return True
        return False
    
    def _is_auth_required_url(self, path: str) -> bool:
        """URL auth gerektiriyor mu kontrol et"""
        for pattern in self.AUTH_REQUIRED_URLS:
            if re.match(pattern, path):
                return True
        return False
    
    def _get_client_ip(self, request) -> str:
        """Client IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RoleLoggingMiddleware(MiddlewareMixin):
    """
    Rol bazlı işlem loglama middleware'i
    Tüm önemli işlemleri loglar
    """
    
    # Bu method'lar loglanır
    LOGGED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # Bu URL'ler loglanır
    LOGGED_URL_PATTERNS = [
        r'^/accounting/',
        r'^/finance/',
        r'^/management/',
        r'^/blockchain/',
        r'^/audit/',
        r'^/billing/',
    ]
    
    def process_response(self, request, response):
        """
        Response işlendikten sonra çalışır
        """
        # Sadece authenticated user'lar için
        if not request.user.is_authenticated:
            return response
        
        # Sadece belirli method'lar için
        if request.method not in self.LOGGED_METHODS:
            return response
        
        # Sadece belirli URL'ler için
        if not self._should_log_url(request.path):
            return response
        
        # Success response'lar için log
        if 200 <= response.status_code < 400:
            user_role = get_user_role_category(request.user)
            
            logger.info(
                f"RBAC Action | "
                f"User: {request.user.username} | "
                f"Role: {user_role} | "
                f"Method: {request.method} | "
                f"Path: {request.path} | "
                f"Status: {response.status_code} | "
                f"IP: {self._get_client_ip(request)}"
            )
            
            # Audit log'a da kaydet (varsa)
            try:
                from audit.utils import log_action
                log_action(
                    user=request.user,
                    action=f"{request.method} {request.path}",
                    object_type='URL',
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    extra_data={
                        'role': user_role,
                        'status_code': response.status_code
                    }
                )
            except Exception as e:
                logger.debug(f"Audit log failed: {e}")
        
        return response
    
    def _should_log_url(self, path: str) -> bool:
        """URL loglanmalı mı kontrol et"""
        for pattern in self.LOGGED_URL_PATTERNS:
            if re.match(pattern, path):
                return True
        return False
    
    def _get_client_ip(self, request) -> str:
        """Client IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

