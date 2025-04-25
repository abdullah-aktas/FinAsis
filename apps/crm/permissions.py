from rest_framework import permissions
from django.contrib.auth.models import Group

class IsAdminOrReadOnly(permissions.BasePermission):
    """Sadece admin kullanıcılar yazabilir, diğerleri sadece okuyabilir"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsCustomerOwner(permissions.BasePermission):
    """Sadece müşteri sahibi veya admin kullanıcılar yazabilir"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or obj.owner == request.user

class CanManageContacts(permissions.BasePermission):
    """İletişim kişilerini yönetme izni"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_perm('crm.manage_contacts')

class CanManageOpportunities(permissions.BasePermission):
    """Fırsatları yönetme izni"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_perm('crm.manage_opportunities')

class CanManageActivities(permissions.BasePermission):
    """Aktiviteleri yönetme izni"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_perm('crm.manage_activities')

class CanManageDocuments(permissions.BasePermission):
    """Dokümanları yönetme izni"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_perm('crm.manage_documents')

class CanManageCommunications(permissions.BasePermission):
    """İletişim kayıtlarını yönetme izni"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_perm('crm.manage_communications')

class CanViewCustomerDetails(permissions.BasePermission):
    """Müşteri detaylarını görüntüleme izni"""
    def has_permission(self, request, view):
        return request.user.has_perm('crm.view_customer_details')

class CanViewOpportunityDetails(permissions.BasePermission):
    """Fırsat detaylarını görüntüleme izni"""
    def has_permission(self, request, view):
        return request.user.has_perm('crm.view_opportunity_details')

class CanViewActivityDetails(permissions.BasePermission):
    """Aktivite detaylarını görüntüleme izni"""
    def has_permission(self, request, view):
        return request.user.has_perm('crm.view_activity_details')

class CanViewDocumentDetails(permissions.BasePermission):
    """Doküman detaylarını görüntüleme izni"""
    def has_permission(self, request, view):
        return request.user.has_perm('crm.view_document_details')

class CanViewCommunicationDetails(permissions.BasePermission):
    """İletişim kaydı detaylarını görüntüleme izni"""
    def has_permission(self, request, view):
        return request.user.has_perm('crm.view_communication_details')

class IsInSalesTeam(permissions.BasePermission):
    """Satış ekibinde olma izni"""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Sales Team').exists()

class IsInCustomerServiceTeam(permissions.BasePermission):
    """Müşteri hizmetleri ekibinde olma izni"""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Customer Service Team').exists()

class IsInManagementTeam(permissions.BasePermission):
    """Yönetim ekibinde olma izni"""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Management Team').exists()

class CanExportData(permissions.BasePermission):
    """Veri dışa aktarma izni"""
    def has_permission(self, request, view):
        if view.action == 'export':
            return request.user.has_perm('crm.export_data')
        return True

class CanImportData(permissions.BasePermission):
    """Veri içe aktarma izni"""
    def has_permission(self, request, view):
        if view.action == 'import':
            return request.user.has_perm('crm.import_data')
        return True

class CanDeleteRecords(permissions.BasePermission):
    """Kayıt silme izni"""
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user.has_perm('crm.delete_records')
        return True

class CanViewReports(permissions.BasePermission):
    """Raporları görüntüleme izni"""
    def has_permission(self, request, view):
        if view.action in ['reports', 'statistics']:
            return request.user.has_perm('crm.view_reports')
        return True

class CanManageSettings(permissions.BasePermission):
    """Ayarları yönetme izni"""
    def has_permission(self, request, view):
        if view.action in ['settings', 'configurations']:
            return request.user.has_perm('crm.manage_settings')
        return True 