# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings

class SEOMetadata(models.Model):
    """SEO meta verilerini yöneten model"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    title = models.CharField(
        _('Başlık'),
        max_length=60,
        validators=[
            MinLengthValidator(30),
            MaxLengthValidator(60)
        ],
        help_text=_('Sayfa başlığı (30-60 karakter)')
    )
    
    meta_description = models.TextField(
        _('Meta Açıklama'),
        max_length=160,
        validators=[
            MinLengthValidator(120),
            MaxLengthValidator(160)
        ],
        help_text=_('Meta açıklama (120-160 karakter)')
    )
    
    meta_keywords = models.CharField(
        _('Meta Anahtar Kelimeler'),
        max_length=255,
        help_text=_('Virgülle ayrılmış anahtar kelimeler')
    )
    
    canonical_url = models.URLField(
        _('Canonical URL'),
        max_length=255,
        blank=True,
        help_text=_('Canonical URL (boş bırakılırsa otomatik oluşturulur)')
    )
    
    robots_meta = models.CharField(
        _('Robots Meta'),
        max_length=50,
        default='index, follow',
        help_text=_('Robots meta etiketi')
    )
    
    og_title = models.CharField(
        _('Open Graph Başlık'),
        max_length=60,
        blank=True,
        help_text=_('Open Graph başlığı')
    )
    
    og_description = models.TextField(
        _('Open Graph Açıklama'),
        max_length=160,
        blank=True,
        help_text=_('Open Graph açıklaması')
    )
    
    og_image = models.ImageField(
        _('Open Graph Görsel'),
        upload_to='seo/og_images/',
        blank=True,
        help_text=_('Open Graph görseli (1200x630 piksel önerilir)')
    )
    
    twitter_card = models.CharField(
        _('Twitter Card Tipi'),
        max_length=20,
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary Large Image'),
            ('app', 'App'),
            ('player', 'Player')
        ],
        default='summary_large_image',
        help_text=_('Twitter Card tipi')
    )
    
    structured_data = models.JSONField(
        _('Yapılandırılmış Veri'),
        blank=True,
        null=True,
        help_text=_('JSON-LD formatında yapılandırılmış veri')
    )
    
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('SEO Meta Verisi')
        verbose_name_plural = _('SEO Meta Verileri')
        unique_together = ('content_type', 'object_id')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.content_type} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.canonical_url:
            self.canonical_url = self.generate_canonical_url()
        super().save(*args, **kwargs)
    
    def generate_canonical_url(self):
        """Canonical URL oluştur"""
        if hasattr(self.content_object, 'get_absolute_url'):
            return settings.SITE_URL + self.content_object.get_absolute_url()
        return ''

class SEORedirect(models.Model):
    """301 yönlendirmelerini yöneten model"""
    old_path = models.CharField(
        _('Eski Yol'),
        max_length=255,
        unique=True,
        help_text=_('Yönlendirilecek eski URL yolu')
    )
    
    new_path = models.CharField(
        _('Yeni Yol'),
        max_length=255,
        help_text=_('Yönlendirilecek yeni URL yolu')
    )
    
    is_permanent = models.BooleanField(
        _('Kalıcı Yönlendirme'),
        default=True,
        help_text=_('301 (kalıcı) veya 302 (geçici) yönlendirme')
    )
    
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('SEO Yönlendirmesi')
        verbose_name_plural = _('SEO Yönlendirmeleri')
        indexes = [
            models.Index(fields=['old_path']),
        ]
    
    def __str__(self):
        return f"{self.old_path} -> {self.new_path}"

class SEOKeyword(models.Model):
    """Anahtar kelime takibini yöneten model"""
    keyword = models.CharField(
        _('Anahtar Kelime'),
        max_length=100,
        unique=True,
        help_text=_('Takip edilecek anahtar kelime')
    )
    
    search_volume = models.IntegerField(
        _('Arama Hacmi'),
        default=0,
        help_text=_('Aylık ortalama arama hacmi')
    )
    
    difficulty = models.IntegerField(
        _('Zorluk Seviyesi'),
        default=0,
        help_text=_('1-100 arası zorluk seviyesi')
    )
    
    cpc = models.DecimalField(
        _('Tıklama Başı Maliyet'),
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_('Ortalama tıklama başı maliyet')
    )
    
    competition = models.IntegerField(
        _('Rekabet Seviyesi'),
        default=0,
        help_text=_('1-100 arası rekabet seviyesi')
    )
    
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('SEO Anahtar Kelimesi')
        verbose_name_plural = _('SEO Anahtar Kelimeleri')
        indexes = [
            models.Index(fields=['keyword']),
            models.Index(fields=['search_volume']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return self.keyword

class SEOAnalytics(models.Model):
    """SEO analiz verilerini yöneten model"""
    date = models.DateField(_('Tarih'))
    
    organic_traffic = models.IntegerField(
        _('Organik Trafik'),
        default=0,
        help_text=_('Günlük organik trafik')
    )
    
    average_position = models.FloatField(
        _('Ortalama Sıralama'),
        default=0,
        help_text=_('Ortalama SERP sıralaması')
    )
    
    impressions = models.IntegerField(
        _('Görüntülenme'),
        default=0,
        help_text=_('Günlük görüntülenme sayısı')
    )
    
    clicks = models.IntegerField(
        _('Tıklanma'),
        default=0,
        help_text=_('Günlük tıklanma sayısı')
    )
    
    ctr = models.FloatField(
        _('Tıklanma Oranı'),
        default=0,
        help_text=_('Tıklanma oranı (%)')
    )
    
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('SEO Analiz Verisi')
        verbose_name_plural = _('SEO Analiz Verileri')
        unique_together = ('date',)
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"SEO Analiz - {self.date}"
    
    def save(self, *args, **kwargs):
        if self.impressions > 0:
            self.ctr = (self.clicks / self.impressions) * 100
        super().save(*args, **kwargs)
