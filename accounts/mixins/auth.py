# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from ..models import User

class RoleRequiredMixin:
    """Belirli bir role sahip olmayı gerektiren mixin"""
    role_required = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if self.role_required and not request.user.has_role(self.role_required):
            raise PermissionDenied("Bu sayfaya erişim yetkiniz yok.")
        
        return super().dispatch(request, *args, **kwargs)

class PasswordExpiryMixin:
    """Şifre süresi kontrolü yapan mixin"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_password_expired():
            from django.contrib import messages
            messages.warning(request, 'Şifrenizin süresi dolmuş. Lütfen şifrenizi değiştirin.')
            from django.urls import reverse_lazy
            from django.shortcuts import redirect
            return redirect(reverse_lazy('accounts:password_change'))
        return super().dispatch(request, *args, **kwargs)

class TwoFactorRequiredMixin:
    """İki faktörlü kimlik doğrulama gerektiren mixin"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.two_factor_enabled:
            from django.contrib import messages
            messages.warning(request, 'Bu sayfaya erişmek için iki faktörlü kimlik doğrulama gereklidir.')
            from django.urls import reverse_lazy
            from django.shortcuts import redirect
            return redirect(reverse_lazy('accounts:settings'))
        return super().dispatch(request, *args, **kwargs)

class VirtualCompanyMixin:
    """Sanal şirket kullanıcısı kontrolü yapan mixin"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_virtual_company_user:
            from django.contrib import messages
            messages.warning(request, 'Bu sayfaya erişmek için sanal şirket kullanıcısı olmanız gerekmektedir.')
            from django.urls import reverse_lazy
            from django.shortcuts import redirect
            return redirect(reverse_lazy('home'))
        return super().dispatch(request, *args, **kwargs) 