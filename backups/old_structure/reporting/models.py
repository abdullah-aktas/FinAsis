from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Report(models.Model):
    """Rapor modeli"""
    REPORT_TYPES = [
        ('financial', 'Finansal Rapor'),
        ('operational', 'Operasyonel Rapor'),
        ('analytical', 'Analitik Rapor'),
        ('custom', 'Özel Rapor'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    name = models.CharField(_('Rapor Adı'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    report_type = models.CharField(_('Rapor Tipi'), max_length=20, choices=REPORT_TYPES)
    format = models.CharField(_('Format'), max_length=10, choices=FORMAT_CHOICES, default='pdf')
    parameters = models.JSONField(_('Parametreler'), default=dict, blank=True)
    schedule = models.CharField(_('Zamanlama'), max_length=100, blank=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reporting_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Rapor')
        verbose_name_plural = _('Raporlar')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class ReportExecution(models.Model):
    """Rapor çalıştırma kaydı"""
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    result_file = models.FileField(_('Sonuç Dosyası'), upload_to='reports/', null=True, blank=True)
    error_message = models.TextField(_('Hata Mesajı'), blank=True)
    parameters = models.JSONField(_('Parametreler'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Rapor Çalıştırma')
        verbose_name_plural = _('Rapor Çalıştırmaları')
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.report.name} - {self.started_at}"

class Dashboard(models.Model):
    """Dashboard modeli"""
    name = models.CharField(_('Dashboard Adı'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    layout = models.JSONField(_('Düzen'), default=dict)
    is_public = models.BooleanField(_('Herkese Açık'), default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dashboards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboardlar')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class DashboardWidget(models.Model):
    """Dashboard widget modeli"""
    WIDGET_TYPES = [
        ('chart', 'Grafik'),
        ('table', 'Tablo'),
        ('metric', 'Metrik'),
        ('text', 'Metin'),
    ]
    
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    name = models.CharField(_('Widget Adı'), max_length=255)
    widget_type = models.CharField(_('Widget Tipi'), max_length=20, choices=WIDGET_TYPES)
    configuration = models.JSONField(_('Konfigürasyon'), default=dict)
    position = models.JSONField(_('Pozisyon'), default=dict)
    refresh_interval = models.IntegerField(_('Yenileme Aralığı (saniye)'), default=300)
    
    class Meta:
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgetları')
        ordering = ['dashboard', 'position']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.name}"
