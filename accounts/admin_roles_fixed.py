# accounts/admin_roles_fixed.py - Düzeltilmiş admin entegrasyonu

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.contrib.admin import ModelAdmin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import models

from .role_models import (
    UserRole, 
    SubscriptionPlan, 
    UserSubscription, 
    RoleBasedUserProfile as UserProfile
)

User = get_user_model()

# Model registrationlarını kaldırıyoruz - admin.py'de yapılacak
# @admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = [
        'display_name', 'name', 'hierarchy_level', 'user_count', 
        'permission_summary', 'is_active'
    ]
    list_filter = ['is_active', 'hierarchy_level', 'can_manage_users', 'can_edit_finances']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['hierarchy_level', 'name']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'display_name', 'description', 'is_active', 'hierarchy_level')
        }),
        ('Yönetim İzinleri', {
            'fields': (
                'can_manage_users', 
                'can_manage_companies', 
                'can_approve_transactions'
            ),
            'classes': ('collapse',)
        }),
        ('Mali İzinler', {
            'fields': (
                'can_view_all_finances', 
                'can_edit_finances', 
                'can_generate_reports'
            ),
            'classes': ('collapse',)
        }),
        ('Modül Erişimleri', {
            'fields': (
                'can_access_ai', 
                'can_use_education', 
                'can_play_games', 
                'can_use_blockchain'
            ),
            'classes': ('collapse',)
        }),
        ('Limitler', {
            'fields': ('max_companies', 'max_transactions_per_month'),
            'classes': ('collapse',)
        }),
    )
    
    def user_count(self, obj):
        """Bu role sahip kullanıcı sayısı"""
        try:
            count = UserProfile.objects.filter(role=obj).count()
            if count > 0:
                url = reverse('admin:accounts_userprofile_changelist')
                return format_html(
                    '<a href="{}?role__id__exact={}">{} kullanıcı</a>',
                    url, obj.id, count
                )
            return "0 kullanıcı"
        except:
            return "N/A"
    
    def permission_summary(self, obj):
        """İzin özeti"""
        permissions = []
        if obj.can_manage_users:
            permissions.append('<span class="badge badge-danger">👥 Kullanıcı Yön.</span>')
        if obj.can_edit_finances:
            permissions.append('<span class="badge badge-success">💰 Mali Düzen.</span>')
        if obj.can_access_ai:
            permissions.append('<span class="badge badge-info">🤖 AI</span>')
        if obj.can_use_blockchain:
            permissions.append('<span class="badge badge-warning">⛓️ Blockchain</span>')
        
        return mark_safe(' '.join(permissions)) if permissions else "Temel izinler"
    
    def save_model(self, request, obj, form, change):
        """Rol kaydederken kontroller"""
        if obj.name == 'super_admin' and obj.hierarchy_level != 0:
            messages.warning(request, "Süper admin hiyerarşi seviyesi 0 olarak ayarlandı.")
            obj.hierarchy_level = 0
        
        super().save_model(request, obj, form, change)
        
        if change:
            # Değişiklik varsa ilgili kullanıcılara bildirim gönder
            affected_users = User.objects.filter(userprofile__role=obj).count()
            if affected_users > 0:
                messages.info(
                    request, 
                    f"Bu rolün değişiklikleri {affected_users} kullanıcıyı etkileyecek."
                )

# Django admin method tanımlamaları
UserRoleAdmin.user_count.short_description = "Kullanıcı Sayısı"  # type: ignore
UserRoleAdmin.permission_summary.short_description = "İzin Özeti"  # type: ignore


# @admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    list_display = [
        'display_name', 'name', 'price_display', 'user_count', 
        'feature_summary', 'is_active', 'is_popular'
    ]
    list_filter = [
        'is_active', 'is_popular', 'has_ai_assistant', 
        'has_blockchain', 'has_priority_support'
    ]
    search_fields = ['name', 'display_name', 'description']
    ordering = ['order', 'price_monthly']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': (
                'name', 'display_name', 'description', 
                'is_active', 'is_popular', 'order'
            )
        }),
        ('Fiyatlandırma', {
            'fields': ('price_monthly', 'price_yearly'),
            'classes': ('wide',)
        }),
        ('Limitler', {
            'fields': (
                'max_users', 'max_companies', 'max_transactions', 'storage_gb'
            ),
            'classes': ('wide',)
        }),
        ('Modül Erişimleri', {
            'fields': (
                'has_accounting', 'has_finance', 'has_ai_assistant',
                'has_education', 'has_games', 'has_blockchain'
            ),
            'classes': ('collapse',)
        }),
        ('Premium Özellikler', {
            'fields': ('has_api_access', 'has_priority_support'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """Fiyat görüntüleme"""
        if obj.price_monthly == 0:
            return "📞 Ücretsiz"
        
        yearly_discount = obj.yearly_discount
        yearly_info = f" (Yıllık: ₺{obj.price_yearly} - %{yearly_discount} indirim)" if yearly_discount > 0 else ""
        
        return format_html(
            '<strong>₺{}/ay</strong>{}', 
            obj.price_monthly, 
            yearly_info
        )
    
    def user_count(self, obj):
        """Bu plana sahip kullanıcı sayısı"""
        try:
            count = UserSubscription.objects.filter(plan=obj, status='active').count()
            if count > 0:
                url = reverse('admin:accounts_usersubscription_changelist')
                return format_html(
                    '<a href="{}?plan__id__exact={}">{} abonə</a>',
                    url, obj.id, count
                )
            return "0 abonə"
        except:
            return "N/A"
    
    def feature_summary(self, obj):
        """Özellik özeti"""
        features = []
        if obj.has_ai_assistant:
            features.append('🤖 AI')
        if obj.has_blockchain:
            features.append('⛓️ Blockchain')
        if obj.has_api_access:
            features.append('🔌 API')
        if obj.has_priority_support:
            features.append('🎧 Öncelik Destek')
        
        return ' '.join(features) if features else "Temel özellikler"

# Django admin method tanımlamaları
SubscriptionPlanAdmin.price_display.short_description = "Fiyat"  # type: ignore
SubscriptionPlanAdmin.user_count.short_description = "Aktif Abonə"  # type: ignore
SubscriptionPlanAdmin.feature_summary.short_description = "Özellikler"  # type: ignore


# @admin.register(UserSubscription)
class UserSubscriptionAdmin(ModelAdmin):
    list_display = [
        'user_link', 'plan', 'status', 'billing_period', 
        'days_remaining_display', 'usage_summary', 'amount_paid'
    ]
    list_filter = [
        'status', 'billing_period', 'plan', 'auto_renew',
        'start_date', 'end_date'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name'
    ]
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    
    readonly_fields = ['id', 'created_at', 'updated_at', 'usage_display']
    
    fieldsets = (
        ('Abonelik Bilgileri', {
            'fields': ('user', 'plan', 'status', 'billing_period')
        }),
        ('Tarihler', {
            'fields': (
                'start_date', 'end_date', 'next_billing_date',
                'created_at', 'updated_at'
            ),
            'classes': ('wide',)
        }),
        ('Ödeme', {
            'fields': ('amount_paid', 'currency', 'auto_renew')
        }),
        ('Kullanım İstatistikleri', {
            'fields': (
                'current_month_transactions', 'total_transactions',
                'storage_used_mb', 'usage_display'
            ),
            'classes': ('collapse',)
        }),
        ('Notlar', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Kullanıcı linki"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.get_full_name() or obj.user.username
        )
    
    def days_remaining_display(self, obj):
        """Kalan gün gösterimi"""
        days = obj.days_remaining
        if obj.status != 'active':
            return f"❌ {obj.get_status_display()}"
        elif days <= 7:
            return format_html('<span style="color: red;">⚠️ {} gün</span>', days)
        elif days <= 30:
            return format_html('<span style="color: orange;">⏰ {} gün</span>', days)
        else:
            return f"✅ {days} gün"
    
    def usage_summary(self, obj):
        """Kullanım özeti"""
        if obj.plan.max_transactions == -1:
            transaction_pct = "Sınırsız"
        else:
            transaction_pct = f"{obj.current_month_transactions}/{obj.plan.max_transactions}"
        
        storage_pct = f"{obj.storage_used_mb//1024}GB/{obj.plan.storage_gb}GB"
        
        return format_html(
            '📊 {}<br/>💾 {}',
            transaction_pct,
            storage_pct
        )
    
    def usage_display(self, obj):
        """Detaylı kullanım gösterimi (readonly)"""
        plan_limits = f"""
        <table style="width:100%;">
            <tr><th>Özellik</th><th>Kullanım</th><th>Limit</th><th>Durum</th></tr>
            <tr>
                <td>Aylık İşlem</td>
                <td>{obj.current_month_transactions}</td>
                <td>{'Sınırsız' if obj.plan.max_transactions == -1 else obj.plan.max_transactions}</td>
                <td>{'✅' if obj.can_perform_action('transaction') else '❌'}</td>
            </tr>
            <tr>
                <td>Depolama</td>
                <td>{obj.storage_used_mb} MB</td>
                <td>{obj.plan.storage_gb * 1024} MB</td>
                <td>{'✅' if obj.storage_used_mb < (obj.plan.storage_gb * 1024) else '❌'}</td>
            </tr>
        </table>
        """
        return format_html(plan_limits)
    
    actions = ['activate_subscription', 'suspend_subscription', 'send_renewal_reminder']
    
    def activate_subscription(self, request, queryset):
        """Aboneliği aktifleştir"""
        updated = queryset.filter(status__in=['pending', 'suspended']).update(status='active')
        self.message_user(
            request, 
            f"{updated} abonelik aktifleştirildi.", 
            messages.SUCCESS
        )
    
    def suspend_subscription(self, request, queryset):
        """Aboneliği askıya al"""
        updated = queryset.filter(status='active').update(status='suspended')
        self.message_user(
            request, 
            f"{updated} abonelik askıya alındı.", 
            messages.WARNING
        )

# Django admin method tanımlamaları
UserSubscriptionAdmin.user_link.short_description = "Kullanıcı"  # type: ignore
UserSubscriptionAdmin.days_remaining_display.short_description = "Kalan Süre"  # type: ignore
UserSubscriptionAdmin.usage_summary.short_description = "Kullanım"  # type: ignore
UserSubscriptionAdmin.usage_display.short_description = "Kullanım Detayları"  # type: ignore
UserSubscriptionAdmin.activate_subscription.short_description = "Seçilen abonelikleri aktifleştir"  # type: ignore
UserSubscriptionAdmin.suspend_subscription.short_description = "Seçilen abonelikleri askıya al"  # type: ignore


# @admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = [
        'user_link', 'role_badge', 'company_name', 'job_title',
        'subscription_status', 'last_login_display', 'security_status'
    ]
    list_filter = [
        'role', 'two_factor_enabled', 'is_locked', 'user__is_active',
        'timezone', 'language'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'company_name', 'job_title', 'phone', 'tc_no'
    ]
    ordering = ['-user__last_login']
    
    fieldsets = (
        ('Kullanıcı & Rol', {
            'fields': ('user', 'role')
        }),
        ('Kişisel Bilgiler', {
            'fields': ('phone', 'tc_no', 'birth_date'),
            'classes': ('wide',)
        }),
        ('Profesyonel Bilgiler', {
            'fields': ('company_name', 'job_title', 'license_number'),
            'classes': ('collapse',)
        }),
        ('Hesap Ayarları', {
            'fields': ('timezone', 'language'),
            'classes': ('collapse',)
        }),
        ('Güvenlik', {
            'fields': (
                'two_factor_enabled', 'last_password_change',
                'login_attempts', 'is_locked'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_password_change', 'created_at', 'updated_at']
    
    def user_link(self, obj):
        """Kullanıcı linki"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        full_name = obj.user.get_full_name() or obj.user.username
        
        # Durum indikatorü
        status_icon = "🟢" if obj.user.is_active else "🔴"
        
        return format_html(
            '<a href="{}">{} {}</a>',
            url, status_icon, full_name
        )
    
    def role_badge(self, obj):
        """Rol rozeti"""
        role = obj.role
        color_map = {
            'super_admin': '#dc2626',
            'admin': '#ea580c',
            'finance_manager': '#4c1d95',
            'financial_advisor': '#0891b2',
            'accountant': '#059669',
            'kobi_owner': '#7c3aed',
            'kobi_employee': '#6b7280',
            'auditor': '#4338ca',
            'teacher': '#2563eb',
            'student': '#374151',
            'player': '#0f766e',
            'viewer': '#9ca3af'
        }
        
        color = color_map.get(role.name, '#6b7280')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color,
            role.display_name
        )
    
    def subscription_status(self, obj):
        """Abonelik durumu"""
        try:
            subscription = obj.user.usersubscription
            if subscription.is_active:
                return format_html(
                    '<span style="color: green;">✅ {} - {} gün</span>',
                    subscription.plan.display_name,
                    subscription.days_remaining
                )
            else:
                return format_html(
                    '<span style="color: red;">❌ {}</span>',
                    subscription.get_status_display()
                )
        except:
            return "❓ Abonelik yok"
    
    def last_login_display(self, obj):
        """Son giriş gösterimi"""
        if obj.user.last_login:
            from django.utils.timesince import timesince
            return f"{timesince(obj.user.last_login)} önce"
        return "Hiç giriş yapmamış"
    
    def security_status(self, obj):
        """Güvenlik durumu"""
        indicators = []
        if obj.two_factor_enabled:
            indicators.append("🔐 2FA")
        if obj.is_locked:
            indicators.append("🔒 Kilitli")
        if obj.login_attempts > 3:
            indicators.append("⚠️ Riskli")
        
        return " ".join(indicators) if indicators else "✅ Normal"
    
    actions = ['enable_2fa', 'disable_2fa', 'unlock_users', 'reset_login_attempts']
    
    def enable_2fa(self, request, queryset):
        """2FA'yi aktifleştir"""
        updated = queryset.update(two_factor_enabled=True)
        self.message_user(
            request, 
            f"{updated} kullanıcı için 2FA aktifleştirildi.", 
            messages.SUCCESS
        )
    
    def unlock_users(self, request, queryset):
        """Kullanıcı hesaplarının kilidini aç"""
        updated = queryset.update(is_locked=False, login_attempts=0)
        self.message_user(
            request, 
            f"{updated} kullanıcı hesabının kilidi açıldı.", 
            messages.SUCCESS
        )

# Django admin method tanımlamaları
UserProfileAdmin.user_link.short_description = "Kullanıcı"  # type: ignore
UserProfileAdmin.role_badge.short_description = "Rol"  # type: ignore
UserProfileAdmin.subscription_status.short_description = "Abonelik"  # type: ignore
UserProfileAdmin.last_login_display.short_description = "Son Giriş"  # type: ignore
UserProfileAdmin.security_status.short_description = "Güvenlik"  # type: ignore
UserProfileAdmin.enable_2fa.short_description = "2FA'yi aktifleştir"  # type: ignore
UserProfileAdmin.unlock_users.short_description = "Hesap kilidini aç"  # type: ignore


# User modelini genişlet
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Role Profil'
    
    fieldsets = (
        ('Rol & Şirket', {
            'fields': ('role', 'company_name', 'job_title')
        }),
        ('İletişim', {
            'fields': ('phone',)
        }),
        ('Güvenlik', {
            'fields': ('two_factor_enabled', 'is_locked'),
            'classes': ('collapse',)
        }),
    )


class UserSubscriptionInline(admin.StackedInline):
    model = UserSubscription
    can_delete = False
    verbose_name_plural = 'Abonelik'
    extra = 0
    
    fields = ('plan', 'status', 'end_date', 'auto_renew')
    readonly_fields = ('id', 'created_at')


# Enhanced User Admin
class EnhancedUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)  # UserSubscriptionInline'ı kaldırdık çakışma olmaması için
    
    list_display = [
        'username', 'email', 'get_full_name', 'user_role', 
        'subscription_plan', 'is_active', 'date_joined'
    ]
    
    # Django admin list filter için uygun format
    list_filter = list(BaseUserAdmin.list_filter) + [
        'is_active', 'date_joined'
    ]
    
    def user_role(self, obj):
        """Kullanıcı rolü"""
        try:
            return obj.role_profile.role.display_name
        except:
            return "❓ Rol atanmamış"
    
    def subscription_plan(self, obj):
        """Abonelik planı"""
        try:
            return obj.subscription.plan.display_name
        except:
            return "❓ Abonelik yok"

# Django admin method tanımlamaları
EnhancedUserAdmin.user_role.short_description = "Rol"  # type: ignore
EnhancedUserAdmin.subscription_plan.short_description = "Plan"  # type: ignore


# Admin paneli özelleştirmeleri
admin.site.site_header = "FinAsis Yönetim Paneli"
admin.site.site_title = "FinAsis Admin"
admin.site.index_title = "Sistem Yönetimi"


# Özel admin görünümleri
def role_statistics_view(request):
    """Rol istatistikleri görünümü"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Yetki yok'}, status=403)
    
    stats = UserRole.objects.annotate(
        user_count=Count('userprofile')
    ).values('display_name', 'user_count', 'hierarchy_level')
    
    return JsonResponse({'stats': list(stats)})


def subscription_analytics_view(request):
    """Abonelik analitik görünümü"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Yetki yok'}, status=403)
    
    from django.db.models import Sum
    
    analytics = SubscriptionPlan.objects.annotate(
        active_subscribers=Count('usersubscription', filter=models.Q(usersubscription__status='active')),
        total_revenue=Sum('usersubscription__amount_paid')
    ).values('display_name', 'active_subscribers', 'total_revenue')
    
    return JsonResponse({'analytics': list(analytics)})