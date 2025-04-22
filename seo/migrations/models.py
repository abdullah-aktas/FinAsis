from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class SeoMetadata(models.Model):
    """SEO meta verilerini saklayan model"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    title = models.CharField(_('Başlık'), max_length=60, blank=True)
    description = models.TextField(_('Açıklama'), max_length=160, blank=True)
    keywords = models.CharField(_('Anahtar Kelimeler'), max_length=255, blank=True)
    canonical_url = models.URLField(_('Canonical URL'), blank=True)
    og_title = models.CharField(_('OG Başlık'), max_length=60, blank=True)
    og_description = models.TextField(_('OG Açıklama'), max_length=160, blank=True)
    og_image = models.ImageField(_('OG Görsel'), upload_to='seo/og_images/', blank=True)
    twitter_title = models.CharField(_('Twitter Başlık'), max_length=60, blank=True)
    twitter_description = models.TextField(_('Twitter Açıklama'), max_length=160, blank=True)
    twitter_image = models.ImageField(_('Twitter Görsel'), upload_to='seo/twitter_images/', blank=True)
    
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('SEO Meta Verisi')
        verbose_name_plural = _('SEO Meta Verileri')
        unique_together = ('content_type', 'object_id')
    
    def __str__(self):
        return f"{self.content_type} - {self.object_id}"


class SeoAnalysis(models.Model):
    """SEO analiz sonuçlarını saklayan model"""
    url = models.URLField(_('URL'))
    title = models.CharField(_('Başlık'), max_length=255)
    score = models.IntegerField(_('SEO Puanı'))
    word_count = models.IntegerField(_('Kelime Sayısı'))
    heading_count = models.IntegerField(_('Başlık Sayısı'))
    image_count = models.IntegerField(_('Görsel Sayısı'))
    images_without_alt = models.IntegerField(_('Alt Etiketi Olmayan Görseller'))
    link_count = models.IntegerField(_('Bağlantı Sayısı'))
    internal_link_count = models.IntegerField(_('İç Bağlantı Sayısı'))
    external_link_count = models.IntegerField(_('Dış Bağlantı Sayısı'))
    keyword_density = models.JSONField(_('Anahtar Kelime Yoğunluğu'), default=dict)
    suggestions = models.JSONField(_('Öneriler'), default=list)
    
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('SEO Analizi')
        verbose_name_plural = _('SEO Analizleri')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.url} - {self.score}"


class KeywordRanking(models.Model):
    """Anahtar kelime sıralamalarını takip eden model"""
    keyword = models.CharField(_('Anahtar Kelime'), max_length=100)
    url = models.URLField(_('URL'))
    position = models.IntegerField(_('Sıralama'))
    search_volume = models.IntegerField(_('Arama Hacmi'), null=True, blank=True)
    difficulty = models.IntegerField(_('Zorluk'), null=True, blank=True)
    cpc = models.DecimalField(_('Tıklama Başına Maliyet'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Anahtar Kelime Sıralaması')
        verbose_name_plural = _('Anahtar Kelime Sıralamaları')
        unique_together = ('keyword', 'url')
        ordering = ['keyword', '-position']
    
    def __str__(self):
        return f"{self.keyword} - {self.url} - {self.position}"


class CompetitorAnalysis(models.Model):
    """Rakip analizlerini saklayan model"""
    competitor_url = models.URLField(_('Rakip URL'))
    keyword = models.CharField(_('Anahtar Kelime'), max_length=100)
    position = models.IntegerField(_('Sıralama'))
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    word_count = models.IntegerField(_('Kelime Sayısı'))
    heading_count = models.IntegerField(_('Başlık Sayısı'))
    image_count = models.IntegerField(_('Görsel Sayısı'))
    link_count = models.IntegerField(_('Bağlantı Sayısı'))
    backlink_count = models.IntegerField(_('Geri Bağlantı Sayısı'), null=True, blank=True)
    domain_authority = models.IntegerField(_('Domain Otoritesi'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Rakip Analizi')
        verbose_name_plural = _('Rakip Analizleri')
        unique_together = ('competitor_url', 'keyword')
        ordering = ['keyword', 'position']
    
    def __str__(self):
        return f"{self.competitor_url} - {self.keyword} - {self.position}" 