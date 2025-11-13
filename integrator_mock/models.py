from django.db import models
from django.conf import settings


# ============================================================================
# MOCK INTEGRATOR MODELS - TEST VE DEVELOPMENT İÇİN
# ============================================================================

class MockIntegration(models.Model):
    """Mock entegrasyon kayıtları - test amaçlı"""
    
    INTEGRATION_TYPES = [
        ('GIB', 'GİB (Gelir İdaresi)'),
        ('BANK', 'Banka'),
        ('PAYMENT', 'Ödeme Gateway'),
        ('SMS', 'SMS Provider'),
        ('EMAIL', 'Email Provider'),
        ('OTHER', 'Diğer'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Entegrasyon Adı")
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPES, verbose_name="Entegrasyon Tipi")
    
    # Endpoint
    mock_endpoint = models.URLField(verbose_name="Mock Endpoint")
    
    # Yanıt ayarları
    default_response = models.JSONField(default=dict, verbose_name="Varsayılan Yanıt")
    response_delay_ms = models.IntegerField(default=100, verbose_name="Yanıt Gecikmesi (ms)")
    
    # Başarı oranı
    success_rate = models.IntegerField(default=100, verbose_name="Başarı Oranı (%)", help_text="0-100")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mock Entegrasyon"
        verbose_name_plural = "Mock Entegrasyonlar"
        ordering = ['integration_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.integration_type})"


class MockRequest(models.Model):
    """Mock istek logları"""
    
    integration = models.ForeignKey(MockIntegration, on_delete=models.CASCADE, related_name='requests', verbose_name="Entegrasyon")
    
    # İstek
    request_method = models.CharField(max_length=10, verbose_name="HTTP Metodu")
    request_path = models.CharField(max_length=500, verbose_name="İstek Yolu")
    request_headers = models.JSONField(default=dict, verbose_name="İstek Headers")
    request_body = models.JSONField(default=dict, verbose_name="İstek Body")
    
    # Yanıt
    response_status = models.IntegerField(verbose_name="HTTP Durum Kodu")
    response_body = models.JSONField(default=dict, verbose_name="Yanıt Body")
    response_time_ms = models.IntegerField(verbose_name="Yanıt Süresi (ms)")
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Kullanıcı")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mock İstek"
        verbose_name_plural = "Mock İstekler"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_method} {self.request_path} → {self.response_status}"


class MockScenario(models.Model):
    """Mock senaryolar - test senaryoları"""
    
    name = models.CharField(max_length=200, verbose_name="Senaryo Adı")
    description = models.TextField(verbose_name="Açıklama")
    integration = models.ForeignKey(MockIntegration, on_delete=models.CASCADE, related_name='scenarios', verbose_name="Entegrasyon")
    
    # Koşullar
    conditions = models.JSONField(default=dict, verbose_name="Koşullar")
    
    # Yanıt
    response_data = models.JSONField(default=dict, verbose_name="Yanıt Verisi")
    response_code = models.IntegerField(default=200, verbose_name="HTTP Durum Kodu")
    
    # Öncelik
    priority = models.IntegerField(default=0, verbose_name="Öncelik")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # İstatistik
    usage_count = models.IntegerField(default=0, verbose_name="Kullanım Sayısı")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mock Senaryo"
        verbose_name_plural = "Mock Senaryolar"
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} (Priority: {self.priority})"

