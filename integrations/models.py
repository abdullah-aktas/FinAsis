from django.db import models
from django.contrib.auth.models import User

class IntegrationProvider(models.Model):
    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=50, choices=[
        ('E_INVOICE', 'E-Fatura'),
        ('E_ARCHIVE', 'E-Arşiv'),
        ('BANK', 'Banka'),
        ('SMS', 'SMS'),
        ('EMAIL', 'E-posta'),
        ('PAYMENT', 'Ödeme')
    ])
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.provider_type}"

class IntegrationLog(models.Model):
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=50)
    request_data = models.JSONField()
    response_data = models.JSONField()
    status = models.CharField(max_length=50, choices=[
        ('SUCCESS', 'Başarılı'),
        ('FAILED', 'Başarısız'),
        ('PENDING', 'Beklemede')
    ])
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider.name} - {self.request_type} - {self.created_at}"

class IntegrationConfig(models.Model):
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.TextField()
    is_encrypted = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('provider', 'key')

    def __str__(self):
        return f"{self.provider.name} - {self.key}" 