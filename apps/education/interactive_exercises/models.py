from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class InteractiveExercise(models.Model):
    """Etkileşimli alıştırma modeli"""
    EXERCISE_TYPES = (
        ('quiz', _('Sınav')),
        ('matching', _('Eşleştirme')),
        ('fill_blank', _('Boşluk Doldurma')),
        ('calculation', _('Hesaplama')),
        ('journal_entry', _('Muhasebe Fişi')),
        ('financial_statement', _('Finansal Tablo')),
    )

    title = models.CharField(_('Başlık'), max_length=200)
    description = models.TextField(_('Açıklama'))
    exercise_type = models.CharField(
        _('Alıştırma Tipi'),
        max_length=20,
        choices=EXERCISE_TYPES
    )
    content = models.JSONField(
        _('İçerik'),
        help_text=_('Alıştırmanın içeriği (JSON formatında)')
    )
    correct_answers = models.JSONField(
        _('Doğru Cevaplar'),
        help_text=_('Doğru cevaplar (JSON formatında)')
    )
    time_limit = models.IntegerField(
        _('Süre Limiti (dakika)'),
        null=True,
        blank=True,
        help_text=_('Alıştırmanın tamamlanması için süre limiti')
    )
    max_attempts = models.IntegerField(
        _('Maksimum Deneme Sayısı'),
        default=3,
        help_text=_('Öğrencinin alıştırmayı kaç kez deneyebileceği')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_exercises',
        verbose_name=_('Oluşturan')
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Etkileşimli Alıştırma')
        verbose_name_plural = _('Etkileşimli Alıştırmalar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_exercise_type_display()})"

class ExerciseAttempt(models.Model):
    """Alıştırma deneme modeli"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_attempts',
        verbose_name=_('Öğrenci')
    )
    exercise = models.ForeignKey(
        InteractiveExercise,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_('Alıştırma')
    )
    answers = models.JSONField(
        _('Cevaplar'),
        help_text=_('Öğrencinin verdiği cevaplar (JSON formatında)')
    )
    score = models.DecimalField(
        _('Puan'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    feedback = models.TextField(
        _('Geri Bildirim'),
        blank=True,
        help_text=_('Öğrenciye verilecek geri bildirim')
    )
    started_at = models.DateTimeField(_('Başlangıç Zamanı'), auto_now_add=True)
    completed_at = models.DateTimeField(_('Tamamlanma Zamanı'), null=True, blank=True)

    class Meta:
        verbose_name = _('Alıştırma Denemesi')
        verbose_name_plural = _('Alıştırma Denemeleri')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.exercise.title}"

class ExerciseGroup(models.Model):
    """Alıştırma grubu modeli"""
    title = models.CharField(_('Başlık'), max_length=200)
    description = models.TextField(_('Açıklama'))
    exercises = models.ManyToManyField(
        InteractiveExercise,
        related_name='groups',
        verbose_name=_('Alıştırmalar')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_exercise_groups',
        verbose_name=_('Oluşturan')
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Alıştırma Grubu')
        verbose_name_plural = _('Alıştırma Grupları')
        ordering = ['-created_at']

    def __str__(self):
        return self.title 