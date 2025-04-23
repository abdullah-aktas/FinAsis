from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserPreferences, UserActivity, UserNotification, UserSession

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('profil bilgileri')
    fk_name = 'user'

class UserPreferencesInline(admin.StackedInline):
    model = UserPreferences
    can_delete = False
    verbose_name_plural = _('tercihler')
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, UserPreferencesInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'email_verified', 'last_activity')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'email_verified', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Kişisel Bilgiler'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('İzinler'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Önemli Tarihler'), {'fields': ('last_login', 'date_joined', 'last_activity')}),
        (_('Doğrulama'), {'fields': ('email_verified',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country', 'gender', 'created_at', 'updated_at')
    list_filter = ('gender', 'country', 'city')
    search_fields = ('user__username', 'user__email', 'phone', 'city', 'country')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'timezone', 'theme', 'notifications_enabled', 'created_at', 'updated_at')
    list_filter = ('language', 'timezone', 'theme', 'notifications_enabled')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'user__email', 'action', 'details', 'ip_address')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'last_activity', 'created_at')
    list_filter = ('last_activity', 'created_at')
    search_fields = ('user__username', 'user__email', 'session_key', 'ip_address')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'last_activity')
    date_hierarchy = 'last_activity'

# Özel kullanıcı admin sınıfını kaydet
admin.site.register(User, CustomUserAdmin) 