from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_('Kategori Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True)

    class Meta:
        verbose_name = _('Kategori')
        verbose_name_plural = _('Kategoriler')

    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', _('Başlangıç')),
        ('intermediate', _('Orta')),
        ('advanced', _('İleri')),
    ]
    title = models.CharField(_('Başlık'), max_length=200)
    description = models.TextField(_('Açıklama'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    level = models.CharField(_('Seviye'), max_length=20, choices=LEVEL_CHOICES)
    duration = models.PositiveIntegerField(_('Süre (saat)'))
    image = models.ImageField(_('Görsel'), upload_to='courses/', blank=True, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme'), auto_now=True)

    class Meta:
        verbose_name = _('Kurs')
        verbose_name_plural = _('Kurslar')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(_('Başlık'), max_length=200)
    content = models.TextField(_('İçerik'))
    order = models.PositiveIntegerField(_('Sıra'))
    video_url = models.URLField(_('Video'), blank=True, null=True)

    class Meta:
        verbose_name = _('Ders')
        verbose_name_plural = _('Dersler')
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(_('Kayıt Tarihi'), auto_now_add=True)
    completed = models.BooleanField(_('Tamamlandı'), default=False)

    class Meta:
        verbose_name = _('Kayıt')
        verbose_name_plural = _('Kayıtlar')
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title}"
