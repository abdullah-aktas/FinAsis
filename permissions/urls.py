from django.urls import path
from . import views

app_name = 'permissions'

urlpatterns = [
    # Permission URLs
    path('permissions/', views.PermissionListView.as_view(), name='permission_list'),
    path('permissions/<int:pk>/', views.PermissionDetailView.as_view(), name='permission_detail'),
    path('permissions/create/', views.PermissionCreateView.as_view(), name='permission_create'),
    path('permissions/<int:pk>/update/', views.PermissionUpdateView.as_view(), name='permission_update'),
    path('permissions/<int:pk>/delete/', views.PermissionDeleteView.as_view(), name='permission_delete'),
    
    # Role URLs
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
    path('roles/create/', views.RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/update/', views.RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    
    # UserRole URLs
    path('user-roles/', views.UserRoleListView.as_view(), name='userrole_list'),
    path('user-roles/<int:pk>/', views.UserRoleDetailView.as_view(), name='userrole_detail'),
    path('user-roles/create/', views.UserRoleCreateView.as_view(), name='userrole_create'),
    path('user-roles/<int:pk>/update/', views.UserRoleUpdateView.as_view(), name='userrole_update'),
    path('user-roles/<int:pk>/delete/', views.UserRoleDeleteView.as_view(), name='userrole_delete'),
] 