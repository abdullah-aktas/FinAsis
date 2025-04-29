# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Scenario(models.Model):
    """Muhasebe senaryosu modeli"""
    DIFFICULTY_LEVELS = (
        ('beginner', _('Başlangıç')),
        ('intermediate', _('Orta Seviye')),
        ('advanced', _('İleri Seviye')),
    )

    CATEGORIES = (
        ('general', _('Genel Muhasebe')),
        ('tax', _('Vergi Uygulamaları')),
        ('cost', _('Maliyet Muhasebesi')),
        ('banking', _('Banka İşlemleri')),
        ('inventory', _('Stok Takibi')),
    )

    title = models.CharField(_('Başlık'), max_length=200)
    description = models.TextField(_('Açıklama'))
    difficulty = models.CharField(
        _('Zorluk Seviyesi'),
        max_length=20,
        choices=DIFFICULTY_LEVELS
    )
    category = models.CharField(
        _('Kategori'),
        max_length=20,
        choices=CATEGORIES
    )
    expected_duration = models.IntegerField(
        _('Tahmini Süre (dakika)'),
        help_text=_('Senaryonun tamamlanması için tahmini süre')
    )
    learning_objectives = models.TextField(
        _('Öğrenme Hedefleri'),
        help_text=_('Bu senaryodan elde edilecek öğrenme çıktıları')
    )
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='required_for',
        verbose_name=_('Ön Koşullar')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scenarios',
        verbose_name=_('Oluşturan')
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Senaryo')
        verbose_name_plural = _('Senaryolar')
        ordering = ['difficulty', 'category', 'title']

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

class ScenarioStep(models.Model):
    """Senaryo adımı modeli"""
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name=_('Senaryo')
    )
    order = models.PositiveIntegerField(_('Sıra'))
    title = models.CharField(_('Başlık'), max_length=200)
    instructions = models.TextField(_('Talimatlar'))
    expected_result = models.TextField(
        _('Beklenen Sonuç'),
        help_text=_('Bu adımın doğru tamamlanması durumunda elde edilecek sonuç')
    )
    hints = models.TextField(
        _('İpuçları'),
        blank=True,
        help_text=_('Öğrenciye yardımcı olacak ipuçları')
    )

    class Meta:
        verbose_name = _('Senaryo Adımı')
        verbose_name_plural = _('Senaryo Adımları')
        ordering = ['scenario', 'order']
        unique_together = ['scenario', 'order']

    def __str__(self):
        return f"{self.scenario.title} - Adım {self.order}: {self.title}"

class CaseStudy(models.Model):
    """Vaka çalışması modeli"""
    title = models.CharField(_('Başlık'), max_length=200)
    description = models.TextField(_('Açıklama'))
    company_profile = models.TextField(
        _('Şirket Profili'),
        help_text=_('Vaka çalışmasındaki şirketin detaylı profili')
    )
    financial_data = models.JSONField(
        _('Finansal Veriler'),
        help_text=_('Şirketin finansal verileri (JSON formatında)')
    )
    questions = models.TextField(
        _('Sorular'),
        help_text=_('Öğrencilerin cevaplaması gereken sorular')
    )
    solution_guide = models.TextField(
        _('Çözüm Rehberi'),
        help_text=_('Vaka çalışmasının çözümü için rehber')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_case_studies',
        verbose_name=_('Oluşturan')
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Vaka Çalışması')
        verbose_name_plural = _('Vaka Çalışmaları')
        ordering = ['-created_at']

    def __str__(self):
        return self.title 