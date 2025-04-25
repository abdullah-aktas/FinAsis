"""
Users Modülü - URL Desenleri
---------------------
Bu dosya, Users modülünün URL desenlerini içerir.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'preferences', views.UserPreferencesViewSet)
router.register(r'activities', views.UserActivityViewSet)
router.register(r'notifications', views.UserNotificationViewSet)
router.register(r'sessions', views.UserSessionViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Authentication
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # Password management
    path('password/reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('password/change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    
    # Two-factor authentication
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='two_factor_setup'),
    
    # Activity and notifications
    path('activity/', views.UserActivityView.as_view(), name='activity'),
    path('notifications/', views.UserNotificationListView.as_view(), name='notifications'),
    path('sessions/', views.UserSessionListView.as_view(), name='sessions'),
    
    # User management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
] 