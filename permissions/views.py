from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Permission, Role, UserRole

class PermissionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Permission
    permission_required = 'permissions.view_permission'
    template_name = 'permissions/permission_list.html'
    context_object_name = 'permissions'
    paginate_by = 10

class PermissionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Permission
    permission_required = 'permissions.view_permission'
    template_name = 'permissions/permission_detail.html'
    context_object_name = 'permission'

class PermissionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Permission
    permission_required = 'permissions.add_permission'
    template_name = 'permissions/permission_form.html'
    fields = ['name', 'codename', 'content_type', 'description']
    success_url = reverse_lazy('permissions:permission_list')

    def form_valid(self, form):
        messages.success(self.request, _('Yetki başarıyla oluşturuldu.'))
        return super().form_valid(form)

class PermissionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Permission
    permission_required = 'permissions.change_permission'
    template_name = 'permissions/permission_form.html'
    fields = ['name', 'codename', 'content_type', 'description']
    success_url = reverse_lazy('permissions:permission_list')

    def form_valid(self, form):
        messages.success(self.request, _('Yetki başarıyla güncellendi.'))
        return super().form_valid(form)

class PermissionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Permission
    permission_required = 'permissions.delete_permission'
    template_name = 'permissions/permission_confirm_delete.html'
    success_url = reverse_lazy('permissions:permission_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Yetki başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)

class RoleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Role
    permission_required = 'permissions.view_role'
    template_name = 'permissions/role_list.html'
    context_object_name = 'roles'
    paginate_by = 10

class RoleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Role
    permission_required = 'permissions.view_role'
    template_name = 'permissions/role_detail.html'
    context_object_name = 'role'

class RoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Role
    permission_required = 'permissions.add_role'
    template_name = 'permissions/role_form.html'
    fields = ['name', 'permissions', 'description']
    success_url = reverse_lazy('permissions:role_list')

    def form_valid(self, form):
        messages.success(self.request, _('Rol başarıyla oluşturuldu.'))
        return super().form_valid(form)

class RoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Role
    permission_required = 'permissions.change_role'
    template_name = 'permissions/role_form.html'
    fields = ['name', 'permissions', 'description']
    success_url = reverse_lazy('permissions:role_list')

    def form_valid(self, form):
        messages.success(self.request, _('Rol başarıyla güncellendi.'))
        return super().form_valid(form)

class RoleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Role
    permission_required = 'permissions.delete_role'
    template_name = 'permissions/role_confirm_delete.html'
    success_url = reverse_lazy('permissions:role_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Rol başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)

class UserRoleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = UserRole
    permission_required = 'permissions.view_userrole'
    template_name = 'permissions/userrole_list.html'
    context_object_name = 'user_roles'
    paginate_by = 10

class UserRoleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = UserRole
    permission_required = 'permissions.view_userrole'
    template_name = 'permissions/userrole_detail.html'
    context_object_name = 'user_role'

class UserRoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = UserRole
    permission_required = 'permissions.add_userrole'
    template_name = 'permissions/userrole_form.html'
    fields = ['user', 'role']
    success_url = reverse_lazy('permissions:userrole_list')

    def form_valid(self, form):
        messages.success(self.request, _('Kullanıcı rolü başarıyla oluşturuldu.'))
        return super().form_valid(form)

class UserRoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = UserRole
    permission_required = 'permissions.change_userrole'
    template_name = 'permissions/userrole_form.html'
    fields = ['user', 'role']
    success_url = reverse_lazy('permissions:userrole_list')

    def form_valid(self, form):
        messages.success(self.request, _('Kullanıcı rolü başarıyla güncellendi.'))
        return super().form_valid(form)

class UserRoleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = UserRole
    permission_required = 'permissions.delete_userrole'
    template_name = 'permissions/userrole_confirm_delete.html'
    success_url = reverse_lazy('permissions:userrole_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Kullanıcı rolü başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)

# API ViewSets
class RoleViewSet(viewsets.ModelViewSet):
    """
    Rol yönetimi için API endpoint'leri.
    """
    queryset = Role.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """
        Role yetki ataması yapar.
        """
        role = self.get_object()
        permissions = request.data.get('permissions', [])
        role.permissions.set(permissions)
        return Response({'status': 'permissions assigned'})

class ResourceViewSet(viewsets.ViewSet):
    """
    Kaynak yönetimi için API endpoint'leri.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Tüm kaynakları listeler.
        """
        return Response([])

class PermissionViewSet(viewsets.ModelViewSet):
    """
    Yetki yönetimi için API endpoint'leri.
    """
    queryset = Permission.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class PermissionDelegationViewSet(viewsets.ViewSet):
    """
    Yetki devri için API endpoint'leri.
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        """
        Yetki devri yapar.
        """
        return Response({'status': 'permission delegated'})

class AuditLogViewSet(viewsets.ViewSet):
    """
    Denetim günlüğü için API endpoint'leri.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Denetim günlüklerini listeler.
        """
        return Response([])

class IPWhitelistViewSet(viewsets.ViewSet):
    """
    IP beyaz listesi için API endpoint'leri.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        IP beyaz listesini listeler.
        """
        return Response([])

class TwoFactorSetupView(APIView):
    """
    İki faktörlü kimlik doğrulama kurulumu için API endpoint'i.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        2FA kurulumunu başlatır.
        """
        return Response({'status': '2FA setup initiated'})

class TwoFactorVerifyView(APIView):
    """
    İki faktörlü kimlik doğrulama doğrulaması için API endpoint'i.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        2FA kodunu doğrular.
        """
        return Response({'status': '2FA code verified'})

class TwoFactorDisableView(APIView):
    """
    İki faktörlü kimlik doğrulamayı devre dışı bırakmak için API endpoint'i.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        2FA'yı devre dışı bırakır.
        """
        return Response({'status': '2FA disabled'})

class CheckPermissionView(APIView):
    """
    Yetki kontrolü için API endpoint'i.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Belirli bir yetkinin varlığını kontrol eder.
        """
        return Response({'has_permission': True})

class UserPermissionsView(APIView):
    """
    Kullanıcı yetkilerini görüntülemek için API endpoint'i.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Kullanıcının tüm yetkilerini listeler.
        """
        return Response([])

class DelegatePermissionView(APIView):
    """
    Yetki devri için API endpoint'i.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Yetki devreder.
        """
        return Response({'status': 'permission delegated'})

class RevokePermissionView(APIView):
    """
    Yetki iptali için API endpoint'i.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Yetki iptal eder.
        """
        return Response({'status': 'permission revoked'}) 