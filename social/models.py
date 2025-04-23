from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.conf import settings
import uuid

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    notification_settings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Kullanıcı Profili')
        verbose_name_plural = _('Kullanıcı Profilleri')
        indexes = [
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_private']),
        ]

    def __str__(self):
        return f"{self.user.username} Profili"

    def get_follower_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.user.following.count()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Etiket')
        verbose_name_plural = _('Etiketler')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(validators=[MinLengthValidator(1), MaxLengthValidator(5000)])
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    video = models.FileField(upload_to='posts/videos/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    is_active = models.BooleanField(default=True)
    is_edited = models.BooleanField(default=False)
    is_sponsored = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Gönderi')
        verbose_name_plural = _('Gönderiler')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_sponsored']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.author.username} - {self.created_at}"

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def get_like_count(self):
        return self.likes.count()

    def get_comment_count(self):
        return self.comments.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[MinLengthValidator(1), MaxLengthValidator(1000)])
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Yorum')
        verbose_name_plural = _('Yorumlar')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.author.username} - {self.created_at}"

    def get_like_count(self):
        return self.likes.count()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', _('Beğeni')),
        ('comment', _('Yorum')),
        ('follow', _('Takip')),
        ('mention', _('Etiketleme')),
        ('share', _('Paylaşım')),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Bildirim')
        verbose_name_plural = _('Bildirimler')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username} - {self.notification_type} - {self.recipient.username}"

class Report(models.Model):
    REPORT_TYPES = (
        ('spam', _('Spam')),
        ('inappropriate', _('Uygunsuz İçerik')),
        ('harassment', _('Taciz')),
        ('other', _('Diğer')),
    )

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Rapor')
        verbose_name_plural = _('Raporlar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.reporter.username} - {self.report_type} - {self.created_at}" 