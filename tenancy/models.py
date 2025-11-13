from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Tenant(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

class Company(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.tenant.code})"

class UserTenantRole(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('accountant', 'Accountant'),
        ('viewer', 'Viewer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_roles')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='user_roles')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tenant', 'role')

    def __str__(self):
        return f"{self.user_id}:{self.tenant_id}:{self.role}"


# ============================================================================
# GENİŞLETİLMİŞ MULTI-TENANCY SİSTEMİ
# ============================================================================

class TenantSettings(models.Model):
    """Tenant ayarları - her tenant için özel ayarlar"""
    
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='settings', verbose_name='Tenant')
    
    # Branding
    logo = models.ImageField(upload_to='tenant_logos/', null=True, blank=True, verbose_name='Logo')
    primary_color = models.CharField(max_length=7, default='#007bff', verbose_name='Ana Renk')
    secondary_color = models.CharField(max_length=7, default='#6c757d', verbose_name='İkincil Renk')
    
    # Özellikler
    enabled_modules = models.JSONField(default=list, verbose_name='Aktif Modüller')
    feature_limits = models.JSONField(default=dict, verbose_name='Özellik Limitleri', help_text='{"users": 50, "invoices": 1000}')
    
    # Kotalar
    max_users = models.IntegerField(default=10, verbose_name='Maksimum Kullanıcı')
    max_storage_mb = models.IntegerField(default=1024, verbose_name='Maksimum Depolama (MB)')
    max_api_calls_per_day = models.IntegerField(default=10000, verbose_name='Günlük Maksimum API Çağrısı')
    
    # İletişim
    contact_email = models.EmailField(blank=True, verbose_name='İletişim E-posta')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='İletişim Telefon')
    
    # Lokasyon
    timezone = models.CharField(max_length=50, default='Europe/Istanbul', verbose_name='Zaman Dilimi')
    language = models.CharField(max_length=10, default='tr', verbose_name='Varsayılan Dil')
    
    # Güvenlik
    ip_whitelist = models.JSONField(default=list, blank=True, verbose_name='IP Beyaz Liste')
    require_2fa = models.BooleanField(default=False, verbose_name='2FA Zorunlu')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tenant Ayarları'
        verbose_name_plural = 'Tenant Ayarları'
    
    def __str__(self):
        return f"{self.tenant.name} - Settings"


class TenantUsage(models.Model):
    """Tenant kullanım istatistikleri"""
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='usage_stats', verbose_name='Tenant')
    date = models.DateField(verbose_name='Tarih')
    
    # Kullanıcı istatistikleri
    active_users = models.IntegerField(default=0, verbose_name='Aktif Kullanıcı')
    total_users = models.IntegerField(default=0, verbose_name='Toplam Kullanıcı')
    
    # Kaynak kullanımı
    storage_used_mb = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Kullanılan Depolama (MB)')
    api_calls = models.IntegerField(default=0, verbose_name='API Çağrısı')
    
    # İşlem istatistikleri
    invoices_created = models.IntegerField(default=0, verbose_name='Oluşturulan Fatura')
    transactions_created = models.IntegerField(default=0, verbose_name='Oluşturulan İşlem')
    reports_generated = models.IntegerField(default=0, verbose_name='Oluşturulan Rapor')
    
    # Modül kullanımı
    module_usage = models.JSONField(default=dict, blank=True, verbose_name='Modül Kullanımı')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tenant Kullanımı'
        verbose_name_plural = 'Tenant Kullanımları'
        ordering = ['-date']
        unique_together = ['tenant', 'date']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.date}"


class TenantBilling(models.Model):
    """Tenant faturalandırma"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Beklemede'),
        ('PAID', 'Ödendi'),
        ('OVERDUE', 'Vadesi Geçti'),
        ('CANCELLED', 'İptal Edildi'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='billings', verbose_name='Tenant')
    
    # Fatura bilgisi
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name='Fatura Numarası')
    billing_period_start = models.DateField(verbose_name='Fatura Dönemi Başlangıç')
    billing_period_end = models.DateField(verbose_name='Fatura Dönemi Bitiş')
    
    # Tutarlar
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Taban Tutar')
    usage_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Kullanım Tutarı')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Toplam Tutar')
    
    # Detaylar
    billing_details = models.JSONField(default=dict, verbose_name='Fatura Detayları')
    
    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name='Durum')
    due_date = models.DateField(verbose_name='Vade Tarihi')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Ödeme Tarihi')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tenant Faturalandırma'
        verbose_name_plural = 'Tenant Faturalandırmalar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.invoice_number}"


class TenantAudit(models.Model):
    """Tenant denetim logları"""
    
    ACTION_TYPES = [
        ('CREATE', 'Oluşturuldu'),
        ('UPDATE', 'Güncellendi'),
        ('DELETE', 'Silindi'),
        ('ACTIVATE', 'Aktif Edildi'),
        ('DEACTIVATE', 'Pasif Edildi'),
        ('SETTINGS_CHANGE', 'Ayar Değiştirildi'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='audit_logs', verbose_name='Tenant')
    action = models.CharField(max_length=30, choices=ACTION_TYPES, verbose_name='Aksiyon')
    
    # Değişiklik
    field_name = models.CharField(max_length=100, blank=True, verbose_name='Alan Adı')
    old_value = models.TextField(blank=True, verbose_name='Eski Değer')
    new_value = models.TextField(blank=True, verbose_name='Yeni Değer')
    
    # Kullanıcı
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Kullanıcı')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Adresi')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tenant Denetim Logu'
        verbose_name_plural = 'Tenant Denetim Logları'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.action}"