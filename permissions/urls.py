"""
permissions uygulaması URL yapılandırmaları
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'resources', views.ResourceViewSet, basename='resource')
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'delegations', views.PermissionDelegationViewSet, basename='delegation')
router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-log')
router.register(r'ip-whitelist', views.IPWhitelistViewSet, basename='ip-whitelist')

urlpatterns = [
    path('', include(router.urls)),
    path('two-factor/setup/', views.TwoFactorSetupView.as_view(), name='two-factor-setup'),
    path('two-factor/verify/', views.TwoFactorVerifyView.as_view(), name='two-factor-verify'),
    path('two-factor/disable/', views.TwoFactorDisableView.as_view(), name='two-factor-disable'),
    path('check-permission/', views.CheckPermissionView.as_view(), name='check-permission'),
    path('user-permissions/', views.UserPermissionsView.as_view(), name='user-permissions'),
    path('delegate-permission/', views.DelegatePermissionView.as_view(), name='delegate-permission'),
    path('revoke-permission/', views.RevokePermissionView.as_view(), name='revoke-permission'),
]
