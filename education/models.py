from django.db import models
from django.conf import settings
from virtual_company.models import VirtualCompany
from django.utils.translation import gettext_lazy as _
from accounting.models import BaseModel

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    virtual_company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

class Course(BaseModel):
    """Kurs"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'Başlangıç'),
        ('intermediate', 'Orta'),
        ('advanced', 'İleri'),
    ])
    duration = models.IntegerField(help_text='Dakika cinsinden süre')
    thumbnail = models.ImageField(upload_to='courses/', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Kurs'
        verbose_name_plural = 'Kurslar'

class Lesson(BaseModel):
    """Ders"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField(default=0)
    video_url = models.URLField(null=True, blank=True)
    duration = models.IntegerField(help_text='Dakika cinsinden süre')

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        verbose_name = 'Ders'
        verbose_name_plural = 'Dersler'
        ordering = ['order']

class Quiz(BaseModel):
    """Test"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    time_limit = models.IntegerField(help_text='Dakika cinsinden süre', null=True, blank=True)
    passing_score = models.FloatField(default=60.0)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Testler'

class QuizQuestion(BaseModel):
    """Test Sorusu"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    question_type = models.CharField(max_length=20, choices=[
        ('multiple_choice', 'Çoktan Seçmeli'),
        ('true_false', 'Doğru/Yanlış'),
        ('short_answer', 'Kısa Cevap'),
    ])
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.question[:50]

    class Meta:
        verbose_name = 'Test Sorusu'
        verbose_name_plural = 'Test Soruları'

class Assignment(BaseModel):
    """Ödev"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_score = models.FloatField(default=100.0)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    class Meta:
        verbose_name = 'Ödev'
        verbose_name_plural = 'Ödevler'

class StudentSubmission(BaseModel):
    """Öğrenci Ödev Teslimi"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.assignment.title} - {self.student.username}"

    class Meta:
        verbose_name = 'Ödev Teslimi'
        verbose_name_plural = 'Ödev Teslimleri'

class PerformanceTracking(BaseModel):
    """Performans Takibi"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completion = models.BooleanField(default=False)
    quiz_score = models.FloatField(default=0)
    assignment_score = models.FloatField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

    class Meta:
        verbose_name = 'Performans Takibi'
        verbose_name_plural = 'Performans Takibi'

class Badge(BaseModel):
    """Rozet"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    criteria = models.TextField(help_text='Rozet kazanma kriterleri')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Rozet'
        verbose_name_plural = 'Rozetler'

class UserBadge(BaseModel):
    """Kullanıcı Rozeti"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

    class Meta:
        verbose_name = 'Kullanıcı Rozeti'
        verbose_name_plural = 'Kullanıcı Rozetleri'

class LearningModule(BaseModel):
    """Öğrenme Modülü"""
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'))
    difficulty_level = models.CharField(_('Zorluk Seviyesi'), max_length=20, choices=[
        ('beginner', 'Başlangıç'),
        ('intermediate', 'Orta'),
        ('advanced', 'İleri'),
    ])
    estimated_duration = models.IntegerField(_('Tahmini Süre (dakika)'))
    points = models.IntegerField(_('Kazanılacak Puan'), default=10)
    order = models.IntegerField(_('Sıralama'), default=0)
    is_active = models.BooleanField(_('Aktif'), default=True)

    class Meta:
        verbose_name = _('Öğrenme Modülü')
        verbose_name_plural = _('Öğrenme Modülleri')
        ordering = ['order']

    def __str__(self):
        return self.title

class LearningContent(BaseModel):
    """Öğrenme İçeriği"""
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(_('Başlık'), max_length=255)
    content_type = models.CharField(_('İçerik Tipi'), max_length=20, choices=[
        ('text', 'Metin'),
        ('video', 'Video'),
        ('quiz', 'Quiz'),
        ('exercise', 'Alıştırma'),
        ('simulation', 'Simülasyon'),
    ])
    content = models.TextField(_('İçerik'))
    order = models.IntegerField(_('Sıralama'), default=0)
    is_required = models.BooleanField(_('Zorunlu mu?'), default=True)

    class Meta:
        verbose_name = _('Öğrenme İçeriği')
        verbose_name_plural = _('Öğrenme İçerikleri')
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

class VirtualCompanySimulation(BaseModel):
    """Sanal Şirket Simülasyonu"""
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'))
    initial_balance = models.DecimalField(_('Başlangıç Bakiyesi'), max_digits=12, decimal_places=2)
    scenario = models.JSONField(_('Senaryo'))
    difficulty_level = models.CharField(_('Zorluk Seviyesi'), max_length=20, choices=[
        ('beginner', 'Başlangıç'),
        ('intermediate', 'Orta'),
        ('advanced', 'İleri'),
    ])
    learning_objectives = models.TextField(_('Öğrenme Hedefleri'))
    success_criteria = models.JSONField(_('Başarı Kriterleri'))
    is_active = models.BooleanField(_('Aktif'), default=True)

    class Meta:
        verbose_name = _('Sanal Şirket Simülasyonu')
        verbose_name_plural = _('Sanal Şirket Simülasyonları')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class UserProgress(BaseModel):
    """Kullanıcı İlerlemesi"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_progress')
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE)
    content = models.ForeignKey(LearningContent, on_delete=models.CASCADE)
    status = models.CharField(_('Durum'), max_length=20, choices=[
        ('not_started', 'Başlanmadı'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
    ], default='not_started')
    completion_date = models.DateTimeField(_('Tamamlanma Tarihi'), null=True, blank=True)
    score = models.IntegerField(_('Puan'), null=True, blank=True)
    feedback = models.TextField(_('Geri Bildirim'), blank=True)

    class Meta:
        verbose_name = _('Kullanıcı İlerlemesi')
        verbose_name_plural = _('Kullanıcı İlerlemeleri')
        unique_together = ('user', 'module', 'content')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {self.content.title}"

class SimulationProgress(BaseModel):
    """Simülasyon İlerlemesi"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='simulation_progress')
    simulation = models.ForeignKey(VirtualCompanySimulation, on_delete=models.CASCADE)
    current_state = models.JSONField(_('Mevcut Durum'))
    progress = models.FloatField(_('İlerleme Yüzdesi'), default=0)
    score = models.IntegerField(_('Puan'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Tamamlanma Tarihi'), null=True, blank=True)
    feedback = models.TextField(_('Geri Bildirim'), blank=True)

    class Meta:
        verbose_name = _('Simülasyon İlerlemesi')
        verbose_name_plural = _('Simülasyon İlerlemeleri')
        unique_together = ('user', 'simulation')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.simulation.title}"
