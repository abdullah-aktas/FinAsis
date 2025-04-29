# -*- coding: utf-8 -*-
"""
Users Modülü - URL Desenleri
---------------------
Bu dosya, Users modülünün URL desenlerini içerir.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserProfileViewSet, UserPreferencesViewSet,
    UserActivityViewSet, UserNotificationViewSet, UserSessionViewSet,
    UserLoginView, UserLogoutView, UserRegistrationView,
    UserPasswordResetView, UserPasswordChangeView, UserProfileView,
    UserProfileUpdateView, UserSettingsView, TwoFactorSetupView,
    UserActivityView, UserListView, UserDetailView
)

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'preferences', UserPreferencesViewSet)
router.register(r'activities', UserActivityViewSet)
router.register(r'notifications', UserNotificationViewSet)
router.register(r'sessions', UserSessionViewSet)

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Authentication
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # Password management
    path('password/reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password/change/', UserPasswordChangeView.as_view(), name='password_change'),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('settings/', UserSettingsView.as_view(), name='settings'),
    
    # Two-factor authentication
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='two_factor_setup'),
    
    # Activity and notifications
    path('activity/', UserActivityView.as_view(), name='activity'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
] 