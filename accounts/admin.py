# FinAsis Accounts App admin ayarları
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser,
    Achievement,
    UserSettings,
    UserType,
    SubscriptionType,
    SubscriptionLog,
    UserProfile,
    UserActivity,
    LoginHistory,
)

# YENİ ROL SİSTEMİ İMPORTLARI
from .admin_roles_fixed import (
    UserRoleAdmin,
    SubscriptionPlanAdmin,
    UserSubscriptionAdmin,
    UserProfileAdmin as RoleUserProfileAdmin,
    EnhancedUserAdmin,
)
from .role_models import (
    UserRole,
    SubscriptionPlan,
    UserSubscription,
    RoleBasedUserProfile as RoleUserProfile,
)

# Yeni rol sistemi modellerini kaydet
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
admin.site.register(RoleUserProfile, RoleUserProfileAdmin)

# Mevcut User admin'ini kaldır ve yenisini ekle (role sistemi ile)
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

# Yeni rol destekli User admin'i kaydet
admin.site.register(CustomUser, EnhancedUserAdmin)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        "username",
        "email",
        "get_user_type_display",
        "company",
        "role",
        "is_staff",
        "is_active",
    ]
    list_filter = ["user_type", "role", "is_staff", "is_active", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]

    def get_user_type_display(self, obj):
        """Kullanıcı tipini güzel göster"""
        if obj.user_type:
            return obj.user_type.name
        return "-"

    # Django admin için doğru syntax
    get_user_type_display.short_description = "Kullanıcı Tipi"  # type: ignore
    get_user_type_display.admin_order_field = "user_type__name"  # type: ignore

    def get_fieldsets(self, request, obj=None):
        base = super().get_fieldsets(request, obj)
        fieldsets = list(base) if not isinstance(base, list) else base
        fieldsets.append(
            (
                "FinAsis Bilgileri",
                {
                    "fields": ("company", "role", "user_type"),
                    "description": "Kullanıcının şirketi, sistem rolü ve kullanıcı tipi",
                },
            )
        )
        return fieldsets

    def save_model(self, request, obj, form, change):
        # Admin arayüzünde company alanı boş string olarak gelebilir; None'a çevir.
        if form and not form.cleaned_data.get("company"):
            obj.company = None
        super().save_model(request, obj, form, change)


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "default_subscription"]
    search_fields = ["code", "name"]


@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "audience",
        "period_options",
        "monthly_price",
        "yearly_price",
        "user_limit",
    ]
    search_fields = ["code", "name"]
    list_filter = ["audience", "period_options"]


@admin.register(SubscriptionLog)
class SubscriptionLogAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "old_subscription",
        "new_subscription",
        "changed_at",
        "note",
    ]
    list_filter = ["old_subscription", "new_subscription", "changed_at"]
    search_fields = ["user__username", "note"]


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "points", "is_active", "user_count", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "code", "description")
    readonly_fields = ("user_count", "created_at", "updated_at")
    
    fieldsets = (
        (_("Temel Bilgiler"), {
            "fields": ("name", "code", "category", "description")
        }),
        (_("Ödül"), {
            "fields": ("points", "badge_icon", "badge_color")
        }),
        (_("Durum"), {
            "fields": ("is_active", "user_count")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def user_count(self, obj):
        """Bu başarımı kazanan kullanıcı sayısı"""
        return obj.userachievement_set.count() if hasattr(obj, 'userachievement_set') else 0
    user_count.short_description = "Kazanan Kullanıcı"


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "theme", "language", "timezone", "email_notifications", "updated_at")
    list_filter = ("theme", "language", "timezone", "email_notifications", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        (_("Kullanıcı"), {
            "fields": ("user",)
        }),
        (_("Görünüm"), {
            "fields": ("theme", "language", "timezone")
        }),
        (_("Bildirimler"), {
            "fields": ("email_notifications", "push_notifications", "sms_notifications")
        }),
        (_("Güvenlik"), {
            "fields": ("two_factor_enabled", "session_timeout")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


# ============================================================================
# YENİ KULLANICI YÖNETİM MODELLERİ - ADMIN KAYITLARI
# ============================================================================
from .models import (  # noqa: E402
    UserNotification,
    TwoFactorAuth,
    PasswordHistory,
    UserSession,
    UserPreference,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "city",
        "country",
        "language",
        "profile_views",
        "last_profile_update",
    )
    search_fields = ("user__username", "phone", "city", "bio")
    list_filter = ("country", "language", "timezone")
    readonly_fields = ("profile_views", "last_profile_update", "created_at")


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "module", "ip_address", "created_at")
    search_fields = ("user__username", "description", "module")
    list_filter = ("activity_type", "module", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status",
        "ip_address",
        "device_type",
        "browser",
        "country",
        "two_factor_used",
        "login_at",
    )
    search_fields = ("user__username", "ip_address", "device_type", "browser")
    list_filter = ("status", "two_factor_used", "device_type", "login_at")
    date_hierarchy = "login_at"
    readonly_fields = ("login_at", "session_duration")


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "notification_type",
        "priority",
        "is_read",
        "category",
        "created_at",
    )
    search_fields = ("user__username", "title", "message")
    list_filter = (
        "notification_type",
        "priority",
        "is_read",
        "category",
        "module",
        "created_at",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "read_at")
    actions = ["mark_as_read"]

    def mark_as_read(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{updated} bildirim okundu olarak işaretlendi.")

    mark_as_read.short_description = "Seçili bildirimleri okundu olarak işaretle"  # type: ignore


@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "is_enabled",
        "method",
        "enabled_at",
        "last_used_at",
        "total_uses",
    )
    search_fields = ("user__username",)
    list_filter = ("is_enabled", "method", "enabled_at")
    readonly_fields = ("enabled_at", "last_used_at", "total_uses", "created_at")


@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "changed_by", "change_reason", "ip_address", "changed_at")
    search_fields = ("user__username", "changed_by__username", "change_reason")
    list_filter = ("changed_at",)
    date_hierarchy = "changed_at"
    readonly_fields = ("password_hash", "changed_at")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ip_address",
        "device_name",
        "is_active",
        "last_activity",
        "created_at",
        "expires_at",
    )
    search_fields = ("user__username", "ip_address", "device_name", "session_key")
    list_filter = ("is_active", "created_at", "expires_at")
    date_hierarchy = "created_at"
    readonly_fields = ("last_activity", "created_at")
    actions = ["terminate_sessions"]

    def terminate_sessions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} oturum sonlandırıldı.")

    terminate_sessions.short_description = "Seçili oturumları sonlandır"  # type: ignore


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "theme",
        "email_notifications",
        "push_notifications",
        "session_timeout",
        "items_per_page",
    )
    search_fields = ("user__username",)
    list_filter = (
        "theme",
        "email_notifications",
        "push_notifications",
        "require_password_change",
    )
    readonly_fields = ("created_at", "updated_at")
