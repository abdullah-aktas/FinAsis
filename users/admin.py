# -*- coding: utf-8 -*-
"""
Users Modülü - Admin
---------------------
Bu dosya, Users modülünün admin sınıflarını içerir.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, UserProfile, UserPreferences, UserActivity,
    UserNotification, UserSession, TwoFactorAuth,
    UserSettings, UserPermission
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Kişisel Bilgiler'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('İletişim Bilgileri'), {'fields': ('phone', 'address', 'city', 'country')}),
        (_('İzinler'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Önemli tarihler'), {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('created_at', 'updated_at')

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'timezone', 'theme')
    list_filter = ('language', 'timezone', 'theme')
    search_fields = ('user__username', 'user__email')

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'user__email', 'action')

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'last_activity')
    list_filter = ('last_activity', 'created_at')
    search_fields = ('user__username', 'user__email', 'session_key', 'ip_address')

@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    list_display = ('user', 'method', 'is_enabled', 'created_at')
    list_filter = ('method', 'is_enabled', 'created_at')
    search_fields = ('user__username', 'user__email')

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'push_notifications', 'dark_mode')
    list_filter = ('email_notifications', 'push_notifications', 'dark_mode')
    search_fields = ('user__username', 'user__email')

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'permission', 'granted_by', 'is_active', 'granted_at')
    list_filter = ('is_active', 'granted_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'permission__name') 