# -*- coding: utf-8 -*-
from django.urls import path
from .views.generic import (
    LoginView, TwoFactorView, register_view, logout_view,
    profile_view, settings_view, CustomPasswordResetView,
    CustomPasswordResetDoneView, CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView, CustomPasswordChangeView
)

app_name = 'accounts'

urlpatterns = [
    # Kimlik doğrulama
    path('login/', LoginView.as_view(), name='login'),
    path('two-factor/', TwoFactorView.as_view(), name='two_factor'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Profil ve ayarlar
    path('profile/', profile_view, name='profile'),
    path('settings/', settings_view, name='settings'),
    
    # Şifre işlemleri
    path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
] 