# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
import uuid

User = get_user_model()

class AssistantCapability(models.Model):
    name = models.CharField(_('Yetenek Adı'), max_length=100)
    code = models.CharField(_('Yetenek Kodu'), max_length=50, unique=True)
    description = models.TextField(_('Açıklama'))
    is_active = models.BooleanField(_('Aktif'), default=True)
    priority = models.IntegerField(_('Öncelik'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Asistan Yeteneği')
        verbose_name_plural = _('Asistan Yetenekleri')
        ordering = ['-priority', 'name']

    def __str__(self):
        return self.name

class UserPreference(models.Model):
    LANGUAGES = (
        ('tr', _('Türkçe')),
        ('en', _('İngilizce')),
        ('de', _('Almanca')),
        ('fr', _('Fransızca')),
    )

    VOICE_STYLES = (
        ('professional', _('Profesyonel')),
        ('casual', _('Günlük')),
        ('friendly', _('Arkadaşça')),
        ('formal', _('Resmi')),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='assistant_preferences')
    language = models.CharField(_('Dil'), max_length=2, choices=LANGUAGES, default='tr')
    voice_style = models.CharField(_('Ses Stili'), max_length=20, choices=VOICE_STYLES, default='professional')
    response_speed = models.IntegerField(
        _('Yanıt Hızı'),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    enabled_capabilities = models.ManyToManyField(
        AssistantCapability,
        verbose_name=_('Etkin Yetenekler'),
        related_name='enabled_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Kullanıcı Tercihi')
        verbose_name_plural = _('Kullanıcı Tercihleri')

    def __str__(self):
        return f"{self.user.get_full_name()} - Tercihler"

class ChatSession(models.Model):
    STATUS_CHOICES = (
        ('active', _('Aktif')),
        ('paused', _('Duraklatıldı')),
        ('completed', _('Tamamlandı')),
        ('archived', _('Arşivlendi')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(_('Başlık'), max_length=200, blank=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='active')
    context = models.JSONField(_('Bağlam'), default=dict)
    metadata = models.JSONField(_('Meta Veri'), default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(_('Son Aktivite'), auto_now=True)

    class Meta:
        verbose_name = _('Sohbet Oturumu')
        verbose_name_plural = _('Sohbet Oturumları')
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title or 'Sohbet'}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', _('Metin')),
        ('code', _('Kod')),
        ('image', _('Resim')),
        ('file', _('Dosya')),
        ('system', _('Sistem')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(_('İçerik'))
    message_type = models.CharField(_('Mesaj Türü'), max_length=20, choices=MESSAGE_TYPES, default='text')
    is_user = models.BooleanField(_('Kullanıcı Mesajı'), default=True)
    metadata = models.JSONField(_('Meta Veri'), default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Sohbet Mesajı')
        verbose_name_plural = _('Sohbet Mesajları')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['message_type']),
        ]

    def __str__(self):
        return f"{self.session.user.get_full_name()} - {self.content[:50]}"

class PagePrompt(models.Model):
    PAGE_TYPES = (
        ('dashboard', _('Gösterge Paneli')),
        ('report', _('Rapor')),
        ('form', _('Form')),
        ('list', _('Liste')),
        ('detail', _('Detay')),
        ('custom', _('Özel')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page_path = models.CharField(_('Sayfa Yolu'), max_length=255)
    page_type = models.CharField(_('Sayfa Türü'), max_length=20, choices=PAGE_TYPES)
    title = models.CharField(_('Başlık'), max_length=200)
    prompt_template = models.TextField(_('Prompt Şablonu'))
    context_variables = models.JSONField(_('Bağlam Değişkenleri'), default=list)
    is_active = models.BooleanField(_('Aktif'), default=True)
    priority = models.IntegerField(_('Öncelik'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Sayfa Promptu')
        verbose_name_plural = _('Sayfa Promptları')
        unique_together = ['page_path']
        ordering = ['-priority', 'page_path']
        indexes = [
            models.Index(fields=['page_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} - {self.page_path}"

class AssistantPerformance(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='performance_metrics')
    response_time = models.FloatField(_('Yanıt Süresi (ms)'))
    token_count = models.IntegerField(_('Token Sayısı'))
    capability_used = models.ForeignKey(AssistantCapability, on_delete=models.SET_NULL, null=True)
    user_feedback = models.IntegerField(
        _('Kullanıcı Geri Bildirimi'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Asistan Performansı')
        verbose_name_plural = _('Asistan Performansları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['capability_used']),
        ]

    def __str__(self):
        return f"{self.session.user.get_full_name()} - {self.created_at}" 