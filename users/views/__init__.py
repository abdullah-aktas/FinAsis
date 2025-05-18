# -*- coding: utf-8 -*-
"""
users uygulaması için görünümler (views) modülü
"""

from .generic import *
from .user_views import (
    UserViewSet, UserProfileViewSet, UserPreferencesViewSet,
    UserActivityViewSet, UserNotificationViewSet, UserSessionViewSet,
    UserLoginView, UserLogoutView, UserRegistrationView,
    UserPasswordResetView, UserPasswordChangeView, UserProfileView,
    UserProfileUpdateView, UserSettingsView, TwoFactorSetupView,
    UserActivityView, UserListView, UserDetailView
)

__all__ = [
    'UserViewSet', 'UserProfileViewSet', 'UserPreferencesViewSet',
    'UserActivityViewSet', 'UserNotificationViewSet', 'UserSessionViewSet',
    'UserLoginView', 'UserLogoutView', 'UserRegistrationView',
    'UserPasswordResetView', 'UserPasswordChangeView', 'UserProfileView',
    'UserProfileUpdateView', 'UserSettingsView', 'TwoFactorSetupView',
    'UserActivityView', 'UserListView', 'UserDetailView'
]
