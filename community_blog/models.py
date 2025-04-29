# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Tag(models.Model):
    name = models.CharField(_('Etiket Adı'), max_length=50, unique=True)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Etiket')
        verbose_name_plural = _('Etiketler')
        ordering = ['name']

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', _('Taslak')),
        ('pending', _('Onay Bekliyor')),
        ('published', _('Yayınlandı')),
        ('rejected', _('Reddedildi')),
    )

    title = models.CharField(_('Başlık'), max_length=200)
    content = models.TextField(_('İçerik'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
    status = models.CharField(_('Durum'), max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    published_at = models.DateTimeField(_('Yayınlanma Tarihi'), null=True, blank=True)
    view_count = models.PositiveIntegerField(_('Görüntülenme Sayısı'), default=0)
    language = models.CharField(_('Dil'), max_length=10, choices=[
        ('tr', 'Türkçe'),
        ('en', 'English'),
        ('ku', 'Kurdî'),
        ('ar', 'العربية'),
    ], default='tr')

    class Meta:
        verbose_name = _('Gönderi')
        verbose_name_plural = _('Gönderiler')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField(_('Yorum'))
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_answer = models.BooleanField(_('Cevap mı?'), default=False)

    class Meta:
        verbose_name = _('Yorum')
        verbose_name_plural = _('Yorumlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} - {self.post.title}"

class Vote(models.Model):
    VOTE_CHOICES = (
        ('up', _('Beğen')),
        ('down', _('Beğenme')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    vote_type = models.CharField(_('Oylama Tipi'), max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Oy')
        verbose_name_plural = _('Oylar')
        unique_together = [['user', 'post'], ['user', 'comment']]

    def __str__(self):
        return f"{self.user.username} - {self.vote_type}"

class Badge(models.Model):
    name = models.CharField(_('Rozet Adı'), max_length=50)
    description = models.TextField(_('Açıklama'))
    icon = models.CharField(_('İkon'), max_length=50)
    requirements = models.JSONField(_('Gereksinimler'), default=dict)

    class Meta:
        verbose_name = _('Rozet')
        verbose_name_plural = _('Rozetler')

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    badges = models.ManyToManyField(Badge, related_name='users', blank=True)
    points = models.PositiveIntegerField(_('Puan'), default=0)
    expertise_level = models.CharField(_('Uzmanlık Seviyesi'), max_length=20, choices=[
        ('beginner', _('Başlangıç')),
        ('intermediate', _('Orta Seviye')),
        ('expert', _('Uzman')),
    ], default='beginner')
    preferred_language = models.CharField(_('Tercih Edilen Dil'), max_length=10, choices=[
        ('tr', 'Türkçe'),
        ('en', 'English'),
        ('ku', 'Kurdî'),
        ('ar', 'العربية'),
    ], default='tr')

    class Meta:
        verbose_name = _('Kullanıcı Profili')
        verbose_name_plural = _('Kullanıcı Profilleri')

    def __str__(self):
        return f"{self.user.username} - {self.expertise_level}" 