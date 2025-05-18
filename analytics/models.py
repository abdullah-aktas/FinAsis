# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class AnalyticsDashboard(models.Model):
    """Analitik dashboard modeli"""
    name = models.CharField(_('Dashboard Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Oluşturan'))
    is_public = models.BooleanField(_('Herkese Açık'), default=False)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Analitik Dashboard')
        verbose_name_plural = _('Analitik Dashboardlar')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class DashboardWidget(models.Model):
    """Dashboard widget modeli"""
    WIDGET_TYPES = [
        ('line_chart', _('Çizgi Grafik')),
        ('bar_chart', _('Sütun Grafik')),
        ('pie_chart', _('Pasta Grafik')),
        ('table', _('Tablo')),
        ('metric', _('Metrik')),
        ('gauge', _('Gösterge')),
    ]

    dashboard = models.ForeignKey(AnalyticsDashboard, on_delete=models.CASCADE, verbose_name=_('Dashboard'))
    title = models.CharField(_('Başlık'), max_length=100)
    widget_type = models.CharField(_('Widget Tipi'), max_length=20, choices=WIDGET_TYPES)
    data_source = models.CharField(_('Veri Kaynağı'), max_length=200)
    position = models.JSONField(_('Pozisyon'))
    size = models.JSONField(_('Boyut'))
    settings = models.JSONField(_('Ayarlar'), default=dict)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgetları')
        ordering = ['position']

    def __str__(self):
        return f"{self.title} - {self.dashboard.name}"

class AnalyticsReport(models.Model):
    """Analitik rapor modeli"""
    REPORT_TYPES = [
        ('financial', _('Finansal')),
        ('operational', _('Operasyonel')),
        ('customer', _('Müşteri')),
        ('performance', _('Performans')),
    ]

    title = models.CharField(_('Başlık'), max_length=200)
    report_type = models.CharField(_('Rapor Tipi'), max_length=20, choices=REPORT_TYPES)
    description = models.TextField(_('Açıklama'), blank=True)
    query = models.TextField(_('Sorgu'))
    parameters = models.JSONField(_('Parametreler'), default=dict)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Oluşturan'))
    is_scheduled = models.BooleanField(_('Zamanlanmış'), default=False)
    schedule = models.JSONField(_('Zamanlama'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Analitik Rapor')
        verbose_name_plural = _('Analitik Raporlar')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class DataSource(models.Model):
    """Veri kaynağı modeli"""
    SOURCE_TYPES = [
        ('database', _('Veritabanı')),
        ('api', _('API')),
        ('file', _('Dosya')),
        ('stream', _('Veri Akışı')),
    ]

    name = models.CharField(_('İsim'), max_length=100)
    source_type = models.CharField(_('Kaynak Tipi'), max_length=20, choices=SOURCE_TYPES)
    connection_details = models.JSONField(_('Bağlantı Detayları'))
    is_active = models.BooleanField(_('Aktif'), default=True)
    last_sync = models.DateTimeField(_('Son Senkronizasyon'), null=True, blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Veri Kaynağı')
        verbose_name_plural = _('Veri Kaynakları')
        ordering = ['name']

    def __str__(self):
        return self.name
