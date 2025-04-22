from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import json

User = get_user_model()

class IntegrationConfig(models.Model):
    """Entegrasyon konfigürasyonları"""
    INTEGRATION_TYPES = [
        ('hepsiburada', 'Hepsiburada'),
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('magento', 'Magento'),
        ('iyzico', 'İyzico'),
        ('paytr', 'PayTR'),
        ('payu', 'PayU'),
        ('luca', 'Luca'),
        ('mikro', 'Mikro'),
        ('logo', 'Logo'),
        ('netsis', 'Netsis')
    ]
    
    type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Entegrasyon Konfigürasyonu'
        verbose_name_plural = 'Entegrasyon Konfigürasyonları'
        unique_together = ['type']
        
    def __str__(self):
        return f"{self.get_type_display()} Entegrasyonu"
        
    def clean(self):
        """Konfigürasyon doğrulaması"""
        required_fields = {
            'hepsiburada': ['api_key', 'access_token'],
            'shopify': ['api_key', 'access_token', 'shop_url'],
            'woocommerce': ['api_key', 'api_secret', 'store_url'],
            'magento': ['api_key', 'api_secret', 'store_url'],
            'iyzico': ['api_key', 'secret_key', 'api_url'],
            'paytr': ['merchant_id', 'merchant_key', 'merchant_salt'],
            'payu': ['merchant_id', 'secret_key'],
            'luca': ['api_key', 'access_token', 'company_id'],
            'mikro': ['api_key', 'company_id'],
            'logo': ['api_key', 'company_id'],
            'netsis': ['api_key', 'company_id']
        }
        
        if self.type in required_fields:
            missing_fields = [field for field in required_fields[self.type] 
                            if field not in self.config]
            if missing_fields:
                raise ValidationError(f"Eksik alanlar: {', '.join(missing_fields)}")

class SyncLog(models.Model):
    """Senkronizasyon logları"""
    STATUS_CHOICES = [
        ('success', 'Başarılı'),
        ('error', 'Hata'),
        ('warning', 'Uyarı')
    ]
    
    integration = models.ForeignKey(IntegrationConfig, on_delete=models.CASCADE,
                                  related_name='sync_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Senkronizasyon Logu'
        verbose_name_plural = 'Senkronizasyon Logları'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.integration} - {self.status} - {self.created_at}"

class WebhookLog(models.Model):
    """Webhook logları"""
    integration = models.ForeignKey(IntegrationConfig, on_delete=models.CASCADE,
                                  related_name='webhook_logs')
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    response = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Webhook Logu'
        verbose_name_plural = 'Webhook Logları'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.integration} - {self.event_type} - {self.created_at}"

class IntegrationTask(models.Model):
    """Entegrasyon görevleri"""
    TASK_TYPES = [
        ('sync', 'Senkronizasyon'),
        ('webhook', 'Webhook'),
        ('payment', 'Ödeme'),
        ('invoice', 'Fatura')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız')
    ]
    
    integration = models.ForeignKey(IntegrationConfig, on_delete=models.CASCADE,
                                  related_name='tasks')
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payload = models.JSONField(default=dict)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Entegrasyon Görevi'
        verbose_name_plural = 'Entegrasyon Görevleri'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.integration} - {self.get_task_type_display()} - {self.status}"
        
    def mark_as_running(self):
        """Görevi çalışıyor olarak işaretle"""
        self.status = 'running'
        self.save()
        
    def mark_as_completed(self, result=None):
        """Görevi tamamlandı olarak işaretle"""
        self.status = 'completed'
        self.result = result
        self.completed_at = timezone.now()
        self.save()
        
    def mark_as_failed(self, error_message):
        """Görevi başarısız olarak işaretle"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save() 