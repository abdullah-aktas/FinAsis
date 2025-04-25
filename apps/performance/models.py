from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class PerformanceMetric(models.Model):
    """Performans metrikleri"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    unit = models.CharField(max_length=20)
    threshold = models.FloatField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Performans Metriği'
        verbose_name_plural = 'Performans Metrikleri'

    def __str__(self):
        return self.name

class UserPerformance(models.Model):
    """Kullanıcı performans kayıtları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metric = models.ForeignKey(PerformanceMetric, on_delete=models.CASCADE)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kullanıcı Performansı'
        verbose_name_plural = 'Kullanıcı Performansları'
        indexes = [
            models.Index(fields=['user', 'metric']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.metric.name}"

class PerformanceAlert(models.Model):
    """Performans uyarıları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metric = models.ForeignKey(PerformanceMetric, on_delete=models.CASCADE)
    value = models.FloatField()
    threshold = models.FloatField()
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Performans Uyarısı'
        verbose_name_plural = 'Performans Uyarıları'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.metric.name}"

class UserActivityLog(models.Model):
    """Kullanıcı aktivite logları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    details = models.JSONField()
    duration = models.IntegerField(help_text='Milisaniye cinsinden süre')
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kullanıcı Aktivite Logu'
        verbose_name_plural = 'Kullanıcı Aktivite Logları'
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.action}"

class PerformanceReport(models.Model):
    """Performans raporları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    metrics = models.JSONField()
    summary = models.TextField()
    recommendations = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Performans Raporu'
        verbose_name_plural = 'Performans Raporları'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.start_date} to {self.end_date}" 