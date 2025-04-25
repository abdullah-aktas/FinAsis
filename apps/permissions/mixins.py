"""
Rol tabanlı erişim kontrolü için Django view mixinleri.
"""

from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class RoleRequiredMixin(AccessMixin):
    """
    Belirtilen rollere sahip kullanıcılara erişim izni veren mixin.
    
    Örnek kullanım:
    
    class MyView(RoleRequiredMixin, TemplateView):
        required_roles = ['admin', 'finance_manager']
        template_name = 'my_template.html'
    """
    required_roles = []
    permission_denied_message = "Bu sayfaya erişim izniniz yok."
    permission_denied_url = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        # Süper kullanıcılar her zaman erişebilir
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
            
        # Rol kontrolü
        if not self._has_role(request.user):
            return self.handle_permission_denied()
            
        return super().dispatch(request, *args, **kwargs)
    
    def _has_role(self, user):
        """Kullanıcının gerekli rollerden birine sahip olup olmadığını kontrol eder."""
        if not self.required_roles:
            # Herhangi bir rol belirtilmemişse, erişim izni ver
            return True
            
        # Kullanıcının has_perm_role metodunu kullan
        if hasattr(user, 'has_perm_role'):
            return user.has_perm_role(self.required_roles)
        
        # Eğer has_perm_role metodu yoksa, doğrudan rol kontrolü yap
        return user.role in self.required_roles
    
    def handle_permission_denied(self):
        """Erişim reddedildiğinde yapılacak işlemler."""
        if self.permission_denied_url:
            if self.permission_denied_message:
                messages.error(self.request, self.permission_denied_message)
            return redirect(self.permission_denied_url)
        else:
            return self.handle_no_permission()


class AdminRequiredMixin(RoleRequiredMixin):
    """
    Sadece yönetici rolündeki kullanıcılara erişim izni veren mixin.
    """
    required_roles = ['admin']
    permission_denied_message = "Bu sayfaya erişmek için yönetici rolü gereklidir."
    permission_denied_url = reverse_lazy('home')


class FinanceManagerRequiredMixin(RoleRequiredMixin):
    """
    Finans sorumlusu rolündeki kullanıcılara erişim izni veren mixin.
    """
    required_roles = ['admin', 'finance_manager']
    permission_denied_message = "Bu sayfaya erişmek için finans sorumlusu rolü gereklidir."
    permission_denied_url = reverse_lazy('home')


class AccountingRequiredMixin(RoleRequiredMixin):
    """
    Muhasebe sorumlusu rolündeki kullanıcılara erişim izni veren mixin.
    """
    required_roles = ['admin', 'accounting']
    permission_denied_message = "Bu sayfaya erişmek için muhasebe sorumlusu rolü gereklidir."
    permission_denied_url = reverse_lazy('home')


class StockOperatorRequiredMixin(RoleRequiredMixin):
    """
    Depo yetkilisi rolündeki kullanıcılara erişim izni veren mixin.
    """
    required_roles = ['admin', 'stock_operator']
    permission_denied_message = "Bu sayfaya erişmek için depo yetkilisi rolü gereklidir."
    permission_denied_url = reverse_lazy('home')


class SalesRequiredMixin(RoleRequiredMixin):
    """
    Satış sorumlusu rolündeki kullanıcılara erişim izni veren mixin.
    """
    required_roles = ['admin', 'sales']
    permission_denied_message = "Bu sayfaya erişmek için satış sorumlusu rolü gereklidir."
    permission_denied_url = reverse_lazy('home')


class ManagerRequiredMixin(RoleRequiredMixin):
    """
    Genel müdür rolündeki kullanıcılara erişim izni veren mixin.
    """
    required_roles = ['admin', 'manager']
    permission_denied_message = "Bu sayfaya erişmek için yönetici rolü gereklidir."
    permission_denied_url = reverse_lazy('home')


class BusinessRequiredMixin(RoleRequiredMixin):
    """
    İşletme rolündeki kullanıcılara erişim izni veren mixin.
    """
    required_roles = ['admin', 'business']
    permission_denied_message = "Bu sayfaya erişmek için işletme rolü gereklidir."
    permission_denied_url = reverse_lazy('home')


class AjaxPermissionDeniedMixin:
    """
    AJAX istekleri için erişim reddedildiğinde JSON yanıtı döndüren mixin.
    RoleRequiredMixin ile birlikte kullanılabilir.
    """
    def handle_permission_denied(self):
        """AJAX istekleri için özel işlem."""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'status': 'error',
                'message': self.permission_denied_message
            }, status=403)
        else:
            return super().handle_permission_denied() 