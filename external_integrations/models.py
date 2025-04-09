from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class IntegrationProvider(models.Model):
    """Entegrasyon sağlayıcı modeli"""
    name = models.CharField(_('Sağlayıcı Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True)
    api_base_url = models.URLField(_('API Temel URL'), blank=True)
    api_version = models.CharField(_('API Versiyonu'), max_length=20, blank=True)
    documentation_url = models.URLField(_('Dokümantasyon URL'), blank=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Entegrasyon Sağlayıcısı')
        verbose_name_plural = _('Entegrasyon Sağlayıcıları')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class IntegrationTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('ecommerce', _('E-Ticaret')),
        ('accounting', _('Muhasebe')),
        ('crm', _('CRM')),
        ('erp', _('ERP')),
        ('payment', _('Ödeme')),
        ('shipping', _('Kargo')),
        ('other', _('Diğer')),
    ]

    name = models.CharField(_('Şablon Adı'), max_length=100)
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE, related_name='templates')
    category = models.CharField(_('Kategori'), max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(_('Açıklama'))
    icon = models.ImageField(_('İkon'), upload_to='integration_icons/', blank=True)
    configuration_schema = models.JSONField(_('Yapılandırma Şeması'), help_text=_('JSON Schema formatında yapılandırma şeması'))
    default_settings = models.JSONField(_('Varsayılan Ayarlar'), default=dict)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Entegrasyon Şablonu')
        verbose_name_plural = _('Entegrasyon Şablonları')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"

class Integration(models.Model):
    """Entegrasyon modeli"""
    INTEGRATION_TYPE_CHOICES = [
        ('api', _('API')),
        ('webhook', _('Webhook')),
        ('oauth', _('OAuth')),
        ('custom', _('Özel')),
    ]
    
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE, related_name='integrations')
    template = models.ForeignKey(IntegrationTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='integrations')
    name = models.CharField(_('Entegrasyon Adı'), max_length=100)
    integration_type = models.CharField(_('Entegrasyon Tipi'), max_length=20, choices=INTEGRATION_TYPE_CHOICES)
    api_key = models.CharField(_('API Anahtarı'), max_length=255, blank=True)
    api_secret = models.CharField(_('API Gizli Anahtarı'), max_length=255, blank=True)
    webhook_url = models.URLField(_('Webhook URL'), blank=True)
    settings = models.JSONField(_('Ayarlar'), default=dict)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='integrations')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Entegrasyon')
        verbose_name_plural = _('Entegrasyonlar')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class IntegrationLog(models.Model):
    """Entegrasyon log modeli"""
    LOG_LEVEL_CHOICES = [
        ('info', _('Bilgi')),
        ('warning', _('Uyarı')),
        ('error', _('Hata')),
    ]
    
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='logs')
    log_level = models.CharField(_('Log Seviyesi'), max_length=10, choices=LOG_LEVEL_CHOICES)
    message = models.TextField(_('Mesaj'))
    request_data = models.JSONField(_('İstek Verisi'), null=True, blank=True)
    response_data = models.JSONField(_('Yanıt Verisi'), null=True, blank=True)
    error_traceback = models.TextField(_('Hata İzleme'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Entegrasyon Logu')
        verbose_name_plural = _('Entegrasyon Logları')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.integration.name} - {self.get_log_level_display()} - {self.created_at}"

class WebhookEndpoint(models.Model):
    """Webhook endpoint modeli"""
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='webhook_endpoints')
    name = models.CharField(_('Endpoint Adı'), max_length=100)
    endpoint_url = models.URLField(_('Endpoint URL'))
    secret_key = models.CharField(_('Gizli Anahtar'), max_length=255)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Webhook Endpoint')
        verbose_name_plural = _('Webhook Endpoint\'leri')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class WebhookRequest(models.Model):
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='requests')
    method = models.CharField(_('HTTP Metodu'), max_length=10)
    headers = models.JSONField(_('HTTP Başlıkları'))
    body = models.JSONField(_('İstek Gövdesi'), null=True, blank=True)
    status_code = models.IntegerField(_('Durum Kodu'))
    response = models.JSONField(_('Yanıt'), null=True, blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Webhook İsteği')
        verbose_name_plural = _('Webhook İstekleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.endpoint.name} - {self.method} - {self.status_code} - {self.created_at}"
