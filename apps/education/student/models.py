from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class StudentProfile(models.Model):
    """Öğrenci profili modeli"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name=_('Kullanıcı')
    )
    student_number = models.CharField(
        _('Öğrenci Numarası'),
        max_length=20,
        unique=True
    )
    department = models.CharField(
        _('Bölüm'),
        max_length=100,
        help_text=_('Öğrencinin okuduğu bölüm')
    )
    grade = models.CharField(
        _('Sınıf'),
        max_length=10,
        help_text=_('Öğrencinin sınıfı')
    )
    enrollment_date = models.DateField(
        _('Kayıt Tarihi'),
        auto_now_add=True
    )
    graduation_date = models.DateField(
        _('Mezuniyet Tarihi'),
        null=True,
        blank=True
    )
    gpa = models.DecimalField(
        _('Genel Not Ortalaması'),
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    completed_credits = models.IntegerField(
        _('Tamamlanan Krediler'),
        default=0
    )
    total_credits = models.IntegerField(
        _('Toplam Krediler'),
        default=240
    )

    class Meta:
        verbose_name = _('Öğrenci Profili')
        verbose_name_plural = _('Öğrenci Profilleri')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_number}"

class StudentAssignment(models.Model):
    """Öğrenci ödev modeli"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_assignments',
        verbose_name=_('Öğrenci')
    )
    assignment = models.ForeignKey(
        'teacher_dashboard.Assignment',
        on_delete=models.CASCADE,
        related_name='student_assignments',
        verbose_name=_('Ödev')
    )
    status = models.CharField(
        _('Durum'),
        max_length=20,
        choices=(
            ('not_started', _('Başlanmadı')),
            ('in_progress', _('Devam Ediyor')),
            ('completed', _('Tamamlandı')),
            ('submitted', _('Teslim Edildi')),
            ('graded', _('Notlandırıldı'))
        ),
        default='not_started'
    )
    submission_date = models.DateTimeField(
        _('Teslim Tarihi'),
        null=True,
        blank=True
    )
    last_activity = models.DateTimeField(
        _('Son Aktivite'),
        auto_now=True
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
    feedback = models.TextField(
        _('Geri Bildirim'),
        blank=True
    )

    class Meta:
        verbose_name = _('Öğrenci Ödevi')
        verbose_name_plural = _('Öğrenci Ödevleri')
        unique_together = ['student', 'assignment']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}"

class StudentProgress(models.Model):
    """Öğrenci ilerleme modeli"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name=_('Öğrenci')
    )
    course = models.ForeignKey(
        'education.Course',
        on_delete=models.CASCADE,
        related_name='student_progress',
        verbose_name=_('Ders')
    )
    attendance = models.DecimalField(
        _('Devam Durumu'),
        max_digits=5,
        decimal_places=2,
        default=100
    )
    midterm_grade = models.DecimalField(
        _('Vize Notu'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    final_grade = models.DecimalField(
        _('Final Notu'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    average_grade = models.DecimalField(
        _('Ortalama Not'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    letter_grade = models.CharField(
        _('Harf Notu'),
        max_length=2,
        null=True,
        blank=True
    )
    status = models.CharField(
        _('Durum'),
        max_length=20,
        choices=(
            ('active', _('Aktif')),
            ('passed', _('Geçti')),
            ('failed', _('Kaldı')),
            ('incomplete', _('Eksik'))
        ),
        default='active'
    )

    class Meta:
        verbose_name = _('Öğrenci İlerlemesi')
        verbose_name_plural = _('Öğrenci İlerlemeleri')
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.name}"

    def calculate_average(self):
        """Ortalama notu hesapla"""
        if self.midterm_grade and self.final_grade:
            self.average_grade = (self.midterm_grade * 0.4) + (self.final_grade * 0.6)
            self.save()
            return self.average_grade
        return None

    def calculate_letter_grade(self):
        """Harf notunu hesapla"""
        if self.average_grade:
            if self.average_grade >= 90:
                self.letter_grade = 'AA'
            elif self.average_grade >= 85:
                self.letter_grade = 'BA'
            elif self.average_grade >= 80:
                self.letter_grade = 'BB'
            elif self.average_grade >= 75:
                self.letter_grade = 'CB'
            elif self.average_grade >= 70:
                self.letter_grade = 'CC'
            elif self.average_grade >= 65:
                self.letter_grade = 'DC'
            elif self.average_grade >= 60:
                self.letter_grade = 'DD'
            else:
                self.letter_grade = 'FF'
            self.save()
            return self.letter_grade
        return None 