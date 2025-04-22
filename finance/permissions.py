from rest_framework import permissions
from django.utils.translation import gettext_lazy as _

class CanManageAccounts(permissions.BasePermission):
    """Hesap yönetimi yetkisi"""
    message = _('Hesap yönetimi yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.manage_accounts')

class CanManageTransactions(permissions.BasePermission):
    """İşlem yönetimi yetkisi"""
    message = _('İşlem yönetimi yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.manage_transactions')

class CanManageBudgets(permissions.BasePermission):
    """Bütçe yönetimi yetkisi"""
    message = _('Bütçe yönetimi yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.manage_budgets')

class CanManageReports(permissions.BasePermission):
    """Rapor yönetimi yetkisi"""
    message = _('Rapor yönetimi yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.manage_reports')

class CanManageTaxes(permissions.BasePermission):
    """Vergi yönetimi yetkisi"""
    message = _('Vergi yönetimi yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.manage_taxes')

class CanViewFinancialData(permissions.BasePermission):
    """Finansal veri görüntüleme yetkisi"""
    message = _('Finansal veri görüntüleme yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.view_financial_data')

class CanExportFinancialData(permissions.BasePermission):
    """Finansal veri dışa aktarma yetkisi"""
    message = _('Finansal veri dışa aktarma yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.export_financial_data')

class CanApproveTransactions(permissions.BasePermission):
    """İşlem onaylama yetkisi"""
    message = _('İşlem onaylama yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.approve_transactions')

class CanManageFinancialSettings(permissions.BasePermission):
    """Finansal ayarlar yönetimi yetkisi"""
    message = _('Finansal ayarlar yönetimi yetkiniz bulunmamaktadır.')

    def has_permission(self, request, view):
        return request.user.has_perm('finance.manage_financial_settings') 