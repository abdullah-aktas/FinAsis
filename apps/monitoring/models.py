# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ErrorCategory(models.Model):
    """Hata kategorileri"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=(
            ('low', 'Düşük'),
            ('medium', 'Orta'),
            ('high', 'Yüksek'),
            ('critical', 'Kritik')
        ),
        default='medium'
    )
    
    class Meta:
        verbose_name = 'Hata Kategorisi'
        verbose_name_plural = 'Hata Kategorileri'

    def __str__(self):
        return self.name

class ErrorLog(models.Model):
    """Hata logları"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(ErrorCategory, on_delete=models.SET_NULL, null=True)
    error_code = models.CharField(max_length=50)
    error_message = models.TextField()
    stack_trace = models.TextField(null=True, blank=True)
    request_data = models.JSONField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Hata Logu'
        verbose_name_plural = 'Hata Logları'
        indexes = [
            models.Index(fields=['error_code']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.error_code} - {self.created_at}"

class UserErrorPattern(models.Model):
    """Kullanıcı hata örüntüleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    error_code = models.CharField(max_length=50)
    count = models.IntegerField(default=1)
    first_occurrence = models.DateTimeField(auto_now_add=True)
    last_occurrence = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Kullanıcı Hata Örüntüsü'
        verbose_name_plural = 'Kullanıcı Hata Örüntüleri'
        unique_together = ['user', 'error_code']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.error_code}"

class ErrorResolution(models.Model):
    """Hata çözümleri"""
    error_code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    solution = models.TextField()
    prevention_tips = models.TextField()
    video_url = models.URLField(null=True, blank=True)
    document_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hata Çözümü'
        verbose_name_plural = 'Hata Çözümleri'

    def __str__(self):
        return f"{self.error_code} - {self.title}"

class ErrorNotification(models.Model):
    """Hata bildirimleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    error_log = models.ForeignKey(ErrorLog, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Hata Bildirimi'
        verbose_name_plural = 'Hata Bildirimleri'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.error_log.error_code}" 