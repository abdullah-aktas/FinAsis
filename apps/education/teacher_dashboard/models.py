from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Classroom(models.Model):
    """Sınıf modeli"""
    name = models.CharField(_('Sınıf Adı'), max_length=100)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='classrooms',
        verbose_name=_('Öğretmen')
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Sınıf')
        verbose_name_plural = _('Sınıflar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.teacher.get_full_name()}"

class Assignment(models.Model):
    """Ödev modeli"""
    SCENARIO_TYPES = (
        ('basic', _('Temel Muhasebe')),
        ('intermediate', _('Orta Seviye Muhasebe')),
        ('advanced', _('İleri Seviye Muhasebe')),
        ('tax', _('Vergi Uygulamaları')),
        ('cost', _('Maliyet Muhasebesi')),
    )

    title = models.CharField(_('Başlık'), max_length=200)
    description = models.TextField(_('Açıklama'))
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('Öğretmen')
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name=_('Sınıf')
    )
    scenario_type = models.CharField(
        _('Senaryo Tipi'),
        max_length=20,
        choices=SCENARIO_TYPES
    )
    due_date = models.DateTimeField(_('Teslim Tarihi'))
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Ödev')
        verbose_name_plural = _('Ödevler')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.classroom.name}"

class StudentProgress(models.Model):
    """Öğrenci ilerleme modeli"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name=_('Öğrenci')
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='student_progress',
        verbose_name=_('Ödev')
    )
    completion_percentage = models.DecimalField(
        _('Tamamlanma Yüzdesi'),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    grade = models.DecimalField(
        _('Not'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    feedback = models.TextField(_('Geri Bildirim'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Öğrenci İlerlemesi')
        verbose_name_plural = _('Öğrenci İlerlemeleri')
        ordering = ['-updated_at']
        unique_together = ['student', 'assignment']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}" 