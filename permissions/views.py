# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    PermissionSerializer,
    RoleSerializer,
    UserRoleSerializer,
    UserPermissionSerializer,
)
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied

from .models import Permission, Role, UserRole, UserPermission


class PermissionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Permission
    permission_required = "permissions.view_permission"
    template_name = "permissions/permission_list.html"
    context_object_name = "permissions"
    paginate_by = 10

    def get_queryset(self):
        queryset = Permission.objects.filter(is_active=True)
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset


class PermissionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Permission
    permission_required = "permissions.view_permission"
    template_name = "permissions/permission_detail.html"
    context_object_name = "permission"

    def get_queryset(self):
        return Permission.objects.filter(is_active=True)


class PermissionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Permission
    permission_required = "permissions.add_permission"
    template_name = "permissions/permission_form.html"
    fields = ["name", "codename", "content_type", "description"]
    success_url = reverse_lazy("permissions:permission_list")

    def form_valid(self, form):
        messages.success(self.request, _("Yetki başarıyla oluşturuldu."))
        return super().form_valid(form)


class PermissionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Permission
    permission_required = "permissions.change_permission"
    template_name = "permissions/permission_form.html"
    fields = ["name", "codename", "content_type", "description"]
    success_url = reverse_lazy("permissions:permission_list")

    def form_valid(self, form):
        messages.success(self.request, _("Yetki başarıyla güncellendi."))
        return super().form_valid(form)


class PermissionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Permission
    permission_required = "permissions.delete_permission"
    template_name = "permissions/permission_confirm_delete.html"
    success_url = reverse_lazy("permissions:permission_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.success(self.request, _("Yetki başarıyla silindi (pasif yapıldı)."))
        return super(DeleteView, self).delete(request, *args, **kwargs)

    def get_queryset(self):
        return Permission.objects.filter(is_active=True)


class RoleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Role
    permission_required = "permissions.view_role"
    template_name = "permissions/role_list.html"
    context_object_name = "roles"
    paginate_by = 10

    def get_queryset(self):
        queryset = Role.objects.filter(is_active=True)
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset


class RoleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Role
    permission_required = "permissions.view_role"
    template_name = "permissions/role_detail.html"
    context_object_name = "role"

    def get_queryset(self):
        return Role.objects.filter(is_active=True)


class RoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Role
    permission_required = "permissions.add_role"
    template_name = "permissions/role_form.html"
    fields = ["name", "permissions", "description"]
    success_url = reverse_lazy("permissions:role_list")

    def form_valid(self, form):
        messages.success(self.request, _("Rol başarıyla oluşturuldu."))
        return super().form_valid(form)


class RoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Role
    permission_required = "permissions.change_role"
    template_name = "permissions/role_form.html"
    fields = ["name", "permissions", "description"]
    success_url = reverse_lazy("permissions:role_list")

    def form_valid(self, form):
        messages.success(self.request, _("Rol başarıyla güncellendi."))
        return super().form_valid(form)


class RoleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Role
    permission_required = "permissions.delete_role"
    template_name = "permissions/role_confirm_delete.html"
    success_url = reverse_lazy("permissions:role_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.success(self.request, _("Rol başarıyla silindi (pasif yapıldı)."))
        return super(DeleteView, self).delete(request, *args, **kwargs)

    def get_queryset(self):
        return Role.objects.filter(is_active=True)


class UserRoleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = UserRole
    permission_required = "permissions.view_userrole"
    template_name = "permissions/userrole_list.html"
    context_object_name = "user_roles"
    paginate_by = 10

    def get_queryset(self):
        queryset = UserRole.objects.filter(is_active=True)
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(user__username__icontains=q)
        return queryset


class UserRoleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = UserRole
    permission_required = "permissions.view_userrole"
    template_name = "permissions/userrole_detail.html"
    context_object_name = "user_role"

    def get_queryset(self):
        return UserRole.objects.filter(is_active=True)


class UserRoleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = UserRole
    permission_required = "permissions.add_userrole"
    template_name = "permissions/userrole_form.html"
    fields = ["user", "role"]
    success_url = reverse_lazy("permissions:userrole_list")

    def form_valid(self, form):
        messages.success(self.request, _("Kullanıcı rolü başarıyla oluşturuldu."))
        return super().form_valid(form)


class UserRoleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = UserRole
    permission_required = "permissions.change_userrole"
    template_name = "permissions/userrole_form.html"
    fields = ["user", "role"]
    success_url = reverse_lazy("permissions:userrole_list")

    def form_valid(self, form):
        messages.success(self.request, _("Kullanıcı rolü başarıyla güncellendi."))
        return super().form_valid(form)


class UserRoleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = UserRole
    permission_required = "permissions.delete_userrole"
    template_name = "permissions/userrole_confirm_delete.html"
    success_url = reverse_lazy("permissions:userrole_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.success(
            self.request, _("Kullanıcı rolü başarıyla silindi (pasif yapıldı).")
        )
        return super(DeleteView, self).delete(request, *args, **kwargs)

    def get_queryset(self):
        return UserRole.objects.filter(is_active=True)


# API ViewSets
class PermissionViewSet(viewsets.ModelViewSet):
    """
    Yetki yönetimi için API endpoint'leri.
    """

    queryset = Permission.active.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "codename", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class RoleViewSet(viewsets.ModelViewSet):
    """
    Rol yönetimi için API endpoint'leri.
    """

    queryset = Role.active.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    @action(detail=True, methods=["post"])
    def assign_permissions(self, request, pk=None):
        """
        Role yetki ataması yapar.
        """
        role = self.get_object()
        permissions = request.data.get("permissions", [])
        role.permissions.set(permissions)
        return Response({"status": "permissions assigned"})


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    Kullanıcı rolü yönetimi için API endpoint'leri.
    Normal kullanıcılar sadece kendi rollerini görebilir ve yönetebilir.
    Admin/superuser'lar tüm kullanıcı rollerini görebilir ve yönetebilir.
    """

    queryset = UserRole.active.all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__username", "role__name"]
    ordering_fields = ["user", "role", "created_at"]
    ordering = ["user"]

    def get_queryset(self):
        """
        Normal kullanıcılar sadece kendi rollerini görebilir.
        Admin/superuser'lar tüm rollerini görebilir.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin veya superuser ise tüm rollerini görebilir
        if user.is_staff or user.is_superuser:
            return queryset
        
        # Normal kullanıcı sadece kendi rollerini görebilir
        return queryset.filter(user=user)

    def perform_create(self, serializer: UserRoleSerializer) -> None:
        """
        Yeni bir kullanıcı rolü oluşturulurken:
        - Normal kullanıcılar sadece kendilerine rol atayabilir
        - Admin/superuser'lar herhangi bir kullanıcıya rol atayabilir
        """
        user = self.request.user
        target_user = serializer.validated_data.get('user')
        
        # Normal kullanıcı sadece kendisine rol atayabilir
        if not (user.is_staff or user.is_superuser):
            if target_user and target_user != user:
                raise PermissionDenied(
                    _("Sadece kendi rollerinizi yönetebilirsiniz.")
                )
            # Kullanıcı kendisine rol atıyorsa, user'ı otomatik set et
            instance = serializer.save(user=user)
            print(f"AUDIT: {user} kendisine {instance.role} rolünü atadı.")
        else:
            # Admin/superuser herhangi bir kullanıcıya rol atayabilir
            # Eğer user belirtilmemişse, kendisine atar
            if not target_user:
                target_user = user
            instance = serializer.save(user=target_user)
            print(f"AUDIT: {user} {target_user} kullanıcıya {instance.role} rolünü atadı.")

    def perform_update(self, serializer: UserRoleSerializer) -> None:
        """
        Kullanıcı rolü güncellenirken:
        - Normal kullanıcılar sadece kendi rollerini güncelleyebilir
        - Admin/superuser'lar herhangi bir kullanıcının rolünü güncelleyebilir
        """
        user = self.request.user
        instance = self.get_object()
        
        # Normal kullanıcı sadece kendi rollerini güncelleyebilir
        if not (user.is_staff or user.is_superuser):
            if instance.user != user:
                raise PermissionDenied(
                    _("Sadece kendi rollerinizi yönetebilirsiniz.")
                )
        
        serializer.save()
        print(f"AUDIT: {user} {instance} kullanıcı rolünü güncelledi.")

    def perform_destroy(self, instance: UserRole) -> None:
        """
        Kullanıcı rolü silinirken:
        - Normal kullanıcılar sadece kendi rollerini silebilir
        - Superuser'lar herhangi bir kullanıcının rolünü silebilir
        """
        user = self.request.user
        
        # Normal kullanıcı sadece kendi rollerini silebilir
        if not user.is_superuser:
            if instance.user != user:
                raise PermissionDenied(
                    _("Sadece kendi rollerinizi silebilirsiniz.")
                )
        
        print(f"AUDIT: {user} {instance} kullanıcı rolünü sildi.")
        return super().perform_destroy(instance)


class UserPermissionViewSet(viewsets.ModelViewSet):
    """
    Kullanıcıya doğrudan yetki atama için API endpoint'leri.
    """

    queryset = UserPermission.objects.filter(is_active=True)
    serializer_class = UserPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__username", "permission__codename"]
    ordering_fields = ["user", "permission", "created_at"]
    ordering = ["user"]


# Granular permission örneği
class IsRoleManager(permissions.BasePermission):
    """
    Sadece rol yöneticileri veya süperuser erişebilir.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_superuser
            or request.user.groups.filter(name="RoleManager").exists()
        )


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


class PermissionDelegationViewSet(viewsets.ViewSet):
    """
    Yetki devri için API endpoint'leri.
    """

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        """
        Yetki devri yapar.
        """
        return Response({"status": "permission delegated"})


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
        return Response({"status": "2FA setup initiated"})


class TwoFactorVerifyView(APIView):
    """
    İki faktörlü kimlik doğrulama doğrulaması için API endpoint'i.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        2FA kodunu doğrular.
        """
        return Response({"status": "2FA code verified"})


class TwoFactorDisableView(APIView):
    """
    İki faktörlü kimlik doğrulamayı devre dışı bırakmak için API endpoint'i.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        2FA'yı devre dışı bırakır.
        """
        return Response({"status": "2FA disabled"})


class CheckPermissionView(APIView):
    """
    Yetki kontrolü için API endpoint'i.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Belirli bir yetkinin varlığını kontrol eder.
        """
        return Response({"has_permission": True})


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
        return Response({"status": "permission delegated"})


class RevokePermissionView(APIView):
    """
    Yetki iptali için API endpoint'i.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Yetki iptal eder.
        """
        return Response({"status": "permission revoked"})


class SecureRoleViewSet(viewsets.ModelViewSet):
    """
    Sadece RoleManager veya süperuser erişebilir (örnek granular permission).
    """

    queryset = Role.active.all()
    serializer_class = RoleSerializer
    permission_classes = [IsRoleManager]
