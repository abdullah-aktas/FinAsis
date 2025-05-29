# FinAsis Accounts App admin ayarları
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Achievement, UserSettings, UserType, SubscriptionType, SubscriptionLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'company', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ("Şirket Bilgisi", {"fields": ("company", "role")}),
    )

@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'default_subscription']
    search_fields = ['code', 'name']

@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'description']
    search_fields = ['code', 'name']

@admin.register(SubscriptionLog)
class SubscriptionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'old_subscription', 'new_subscription', 'changed_at', 'note']
    list_filter = ['old_subscription', 'new_subscription', 'changed_at']
    search_fields = ['user__username', 'note']

admin.site.register(Achievement)
admin.site.register(UserSettings)
