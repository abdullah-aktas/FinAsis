# FinAsis Accounts App admin ayarları
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Achievement, UserSettings, UserType, SubscriptionType, SubscriptionLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'company', 'role', 'is_staff']

    def get_fieldsets(self, request, obj=None):
        base = super().get_fieldsets(request, obj)
        fieldsets = list(base) if not isinstance(base, list) else base
        fieldsets.append(("Şirket Bilgisi", {"fields": ("company", "role")}))
        return fieldsets

    def save_model(self, request, obj, form, change):
        # Admin arayüzünde company alanı boş string olarak gelebilir; None'a çevir.
        if form and not form.cleaned_data.get('company'):
            obj.company = None
        super().save_model(request, obj, form, change)

@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'default_subscription']
    search_fields = ['code', 'name']

@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'audience', 'period_options', 'monthly_price', 'yearly_price', 'user_limit']
    search_fields = ['code', 'name']
    list_filter = ['audience', 'period_options']

@admin.register(SubscriptionLog)
class SubscriptionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'old_subscription', 'new_subscription', 'changed_at', 'note']
    list_filter = ['old_subscription', 'new_subscription', 'changed_at']
    search_fields = ['user__username', 'note']

admin.site.register(Achievement)
admin.site.register(UserSettings)
