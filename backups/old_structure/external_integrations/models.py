# -*- coding: utf-8 -*-
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

class EInvoice(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Taslak'),
        ('PENDING', 'Beklemede'),
        ('SENT', 'Gönderildi'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sent_invoices')
    receiver_vkn = models.CharField(max_length=11)
    receiver_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    pdf_file = models.FileField(upload_to='invoices/pdf/', null=True, blank=True)
    xml_file = models.FileField(upload_to='invoices/xml/', null=True, blank=True)

    class Meta:
        verbose_name = 'E-Fatura'
        verbose_name_plural = 'E-Faturalar'

class EArchive(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Taslak'),
        ('ARCHIVED', 'Arşivlendi'),
        ('ERROR', 'Hata'),
    ]

    archive_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    document_type = models.CharField(max_length=50)
    document_date = models.DateField()
    document_owner = models.ForeignKey(User, on_delete=models.PROTECT)
    file = models.FileField(upload_to='archive/')
    ocr_content = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'E-Arşiv'
        verbose_name_plural = 'E-Arşiv'

class APIProvider(models.Model):
    """API Sağlayıcı Modeli"""
    name = models.CharField(_('Sağlayıcı Adı'), max_length=100)
    api_type = models.CharField(_('API Tipi'), max_length=20, choices=[
        ('bank', _('Banka API')),
        ('edevlet', _('E-Devlet API')),
        ('efatura', _('E-Fatura API')),
        ('other', _('Diğer'))
    ])
    api_base_url = models.URLField(_('API Temel URL'))
    api_version = models.CharField(_('API Versiyonu'), max_length=20)
    auth_type = models.CharField(_('Kimlik Doğrulama Tipi'), max_length=20, choices=[
        ('apikey', _('API Anahtarı')),
        ('oauth2', _('OAuth 2.0')),
        ('jwt', _('JWT')),
        ('basic', _('Temel Kimlik Doğrulama'))
    ])
    api_key = models.CharField(_('API Anahtarı'), max_length=255, blank=True, null=True)
    client_id = models.CharField(_('İstemci ID'), max_length=100, blank=True, null=True)
    client_secret = models.CharField(_('İstemci Şifresi'), max_length=255, blank=True, null=True)
    username = models.CharField(_('Kullanıcı Adı'), max_length=100, blank=True, null=True)
    password = models.CharField(_('Şifre'), max_length=100, blank=True, null=True)
    documentation_url = models.URLField(_('Dokümantasyon URL'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    test_mode = models.BooleanField(_('Test Modu'), default=True)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('API Sağlayıcı')
        verbose_name_plural = _('API Sağlayıcılar')
        ordering = ['name']

class APIEndpoint(models.Model):
    """API Endpoint Modeli"""
    provider = models.ForeignKey(APIProvider, on_delete=models.CASCADE, related_name='endpoints')
    name = models.CharField(_('Endpoint Adı'), max_length=100)
    endpoint_path = models.CharField(_('Endpoint Yolu'), max_length=255)
    http_method = models.CharField(_('HTTP Metodu'), max_length=10, choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH')
    ])
    request_format = models.CharField(_('İstek Formatı'), max_length=10, choices=[
        ('json', 'JSON'),
        ('xml', 'XML'),
        ('form', 'Form Data')
    ], default='json')
    response_format = models.CharField(_('Yanıt Formatı'), max_length=10, choices=[
        ('json', 'JSON'),
        ('xml', 'XML'),
        ('csv', 'CSV'),
        ('pdf', 'PDF')
    ], default='json')
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    example_request = models.TextField(_('Örnek İstek'), blank=True, null=True)
    example_response = models.TextField(_('Örnek Yanıt'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    def __str__(self):
        return f"{self.provider.name} - {self.name}"

    class Meta:
        verbose_name = _('API Endpoint')
        verbose_name_plural = _('API Endpointler')
        ordering = ['provider', 'name']

    def get_full_url(self):
        return f"{self.provider.api_base_url.rstrip('/')}/{self.endpoint_path.lstrip('/')}"

class APIParameter(models.Model):
    """API Parametreleri Modeli"""
    endpoint = models.ForeignKey(APIEndpoint, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(_('Parametre Adı'), max_length=100)
    data_type = models.CharField(_('Veri Tipi'), max_length=20, choices=[
        ('string', _('Metin')),
        ('integer', _('Tam Sayı')),
        ('float', _('Ondalıklı Sayı')),
        ('boolean', _('Mantıksal')),
        ('date', _('Tarih')),
        ('datetime', _('Tarih/Saat')),
        ('object', _('Nesne')),
        ('array', _('Dizi')),
        ('file', _('Dosya')),
    ])
    required = models.BooleanField(_('Zorunlu'), default=False)
    description = models.CharField(_('Açıklama'), max_length=255, blank=True, null=True)
    location = models.CharField(_('Konum'), max_length=20, choices=[
        ('query', _('Sorgu Parametresi')),
        ('path', _('Yol Parametresi')),
        ('body', _('Gövde Parametresi')),
        ('header', _('Başlık Parametresi')),
    ], default='body')
    default_value = models.CharField(_('Varsayılan Değer'), max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.endpoint.name} - {self.name}"

    class Meta:
        verbose_name = _('API Parametre')
        verbose_name_plural = _('API Parametreler')
        ordering = ['endpoint', 'name']

class APIResponse(models.Model):
    """API Yanıt Modeli"""
    endpoint = models.ForeignKey(APIEndpoint, on_delete=models.CASCADE, related_name='responses')
    status_code = models.IntegerField(_('Durum Kodu'))
    description = models.CharField(_('Açıklama'), max_length=255)
    schema = models.TextField(_('Şema'), blank=True, null=True)
    example = models.TextField(_('Örnek'), blank=True, null=True)

    def __str__(self):
        return f"{self.endpoint.name} - {self.status_code}"

    class Meta:
        verbose_name = _('API Yanıt')
        verbose_name_plural = _('API Yanıtlar')
        ordering = ['endpoint', 'status_code']

class BankIntegration(models.Model):
    """Banka Entegrasyon Modeli"""
    api_provider = models.ForeignKey(APIProvider, on_delete=models.CASCADE, related_name='bank_integrations')
    bank_name = models.CharField(_('Banka Adı'), max_length=100)
    bank_code = models.CharField(_('Banka Kodu'), max_length=20)
    account_number = models.CharField(_('Hesap Numarası'), max_length=30)
    iban = models.CharField(_('IBAN'), max_length=34)
    account_type = models.CharField(_('Hesap Tipi'), max_length=20, choices=[
        ('checking', _('Vadesiz Hesap')),
        ('savings', _('Vadeli Hesap')),
        ('credit', _('Kredi Hesabı')),
        ('other', _('Diğer'))
    ])
    currency = models.CharField(_('Para Birimi'), max_length=3, choices=[
        ('TRY', _('Türk Lirası')),
        ('USD', _('Amerikan Doları')),
        ('EUR', _('Euro')),
        ('GBP', _('İngiliz Sterlini'))
    ])
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

    class Meta:
        verbose_name = _('Banka Entegrasyonu')
        verbose_name_plural = _('Banka Entegrasyonları')
        ordering = ['bank_name']

class EDevletIntegration(models.Model):
    """E-Devlet Entegrasyon Modeli"""
    api_provider = models.ForeignKey(APIProvider, on_delete=models.CASCADE, related_name='edevlet_integrations')
    system_name = models.CharField(_('Sistem Adı'), max_length=100)
    system_code = models.CharField(_('Sistem Kodu'), max_length=50)
    service_type = models.CharField(_('Servis Tipi'), max_length=20, choices=[
        ('tax', _('Vergi Hizmetleri')),
        ('social_security', _('SGK Hizmetleri')),
        ('company_registry', _('Şirket Sicil Hizmetleri')),
        ('other', _('Diğer'))
    ])
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    def __str__(self):
        return f"{self.system_name} - {self.service_type}"

    class Meta:
        verbose_name = _('E-Devlet Entegrasyonu')
        verbose_name_plural = _('E-Devlet Entegrasyonları')
        ordering = ['system_name']

class APIDocumentation(models.Model):
    """API Dokümantasyon Modeli"""
    title = models.CharField(_('Başlık'), max_length=100)
    version = models.CharField(_('Versiyon'), max_length=20)
    description = models.TextField(_('Açıklama'))
    base_url = models.URLField(_('Temel URL'))
    auth_description = models.TextField(_('Kimlik Doğrulama Açıklaması'))
    is_published = models.BooleanField(_('Yayınlandı'), default=False)
    requires_api_key = models.BooleanField(_('API Anahtarı Gerekli'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    def __str__(self):
        return f"{self.title} v{self.version}"

    class Meta:
        verbose_name = _('API Dokümantasyonu')
        verbose_name_plural = _('API Dokümantasyonları')
        ordering = ['-version']

class APISection(models.Model):
    """API Dokümantasyon Bölümü Modeli"""
    documentation = models.ForeignKey(APIDocumentation, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(_('Başlık'), max_length=100)
    description = models.TextField(_('Açıklama'))
    order = models.PositiveIntegerField(_('Sıra'), default=0)

    def __str__(self):
        return f"{self.documentation.title} - {self.title}"

    class Meta:
        verbose_name = _('API Bölümü')
        verbose_name_plural = _('API Bölümleri')
        ordering = ['documentation', 'order']

class APIExample(models.Model):
    """API Örnek Modeli"""
    section = models.ForeignKey(APISection, on_delete=models.CASCADE, related_name='examples')
    title = models.CharField(_('Başlık'), max_length=100)
    language = models.CharField(_('Programlama Dili'), max_length=20, choices=[
        ('curl', 'cURL'),
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('php', 'PHP'),
        ('csharp', 'C#'),
        ('java', 'Java'),
    ])
    code = models.TextField(_('Kod'))
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    order = models.PositiveIntegerField(_('Sıra'), default=0)

    def __str__(self):
        return f"{self.section.title} - {self.title}"

    class Meta:
        verbose_name = _('API Örneği')
        verbose_name_plural = _('API Örnekleri')
        ordering = ['section', 'order']

class DeveloperAPIKey(models.Model):
    """Geliştirici API Anahtarı Modeli"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    api_key = models.CharField(_('API Anahtarı'), max_length=64, unique=True)
    name = models.CharField(_('İsim'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    rate_limit = models.PositiveIntegerField(_('İstek Limiti (günlük)'), default=1000)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Geçerlilik Süresi'), null=True, blank=True)
    last_used_at = models.DateTimeField(_('Son Kullanım'), null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        verbose_name = _('Geliştirici API Anahtarı')
        verbose_name_plural = _('Geliştirici API Anahtarları')
        ordering = ['-created_at']

    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

class APIUsageLog(models.Model):
    """API Kullanım Logu Modeli"""
    api_key = models.ForeignKey(DeveloperAPIKey, on_delete=models.CASCADE, related_name='usage_logs')
    endpoint = models.CharField(_('Endpoint'), max_length=255)
    method = models.CharField(_('Metot'), max_length=10)
    ip_address = models.GenericIPAddressField(_('IP Adresi'))
    status_code = models.PositiveIntegerField(_('Durum Kodu'))
    response_time = models.PositiveIntegerField(_('Yanıt Süresi (ms)'))
    request_data = models.TextField(_('İstek Verisi'), blank=True, null=True)
    timestamp = models.DateTimeField(_('Zaman'), auto_now_add=True)

    def __str__(self):
        return f"{self.api_key.name} - {self.endpoint}"

    class Meta:
        verbose_name = _('API Kullanım Logu')
        verbose_name_plural = _('API Kullanım Logları')
        ordering = ['-timestamp']

class APIWebhook(models.Model):
    """API Webhook Modeli"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhooks')
    name = models.CharField(_('İsim'), max_length=100)
    url = models.URLField(_('Webhook URL'))
    events = models.JSONField(_('Olaylar'), help_text=_('Tetiklenecek olaylar listesi'))
    is_active = models.BooleanField(_('Aktif'), default=True)
    secret_key = models.CharField(_('Gizli Anahtar'), max_length=64)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        verbose_name = _('API Webhook')
        verbose_name_plural = _('API Webhooklar')
        ordering = ['-created_at']

class WebhookDelivery(models.Model):
    """Webhook Teslimat Modeli"""
    webhook = models.ForeignKey(APIWebhook, on_delete=models.CASCADE, related_name='deliveries')
    event = models.CharField(_('Olay'), max_length=100)
    payload = models.TextField(_('Veri'))
    response = models.TextField(_('Yanıt'), blank=True, null=True)
    status_code = models.PositiveIntegerField(_('Durum Kodu'), null=True, blank=True)
    success = models.BooleanField(_('Başarılı'), default=False)
    attempt_count = models.PositiveIntegerField(_('Deneme Sayısı'), default=1)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    def __str__(self):
        return f"{self.webhook.name} - {self.event}"

    class Meta:
        verbose_name = _('Webhook Teslimatı')
        verbose_name_plural = _('Webhook Teslimatları')
        ordering = ['-created_at']
