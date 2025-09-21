from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.

class FinancialTermCard(models.Model):
    term = models.CharField(max_length=100, verbose_name=_('Terim'))
    description = models.TextField(verbose_name=_('Açıklama'))
    example = models.TextField(verbose_name=_('Örnek'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.term

    class Meta:
        ordering = ['-created_at']

class StudentAnalytics(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics', verbose_name=_('Öğrenci'))
    date = models.DateField(auto_now_add=True, verbose_name=_('Tarih'))
    completed_assignments = models.IntegerField(default=0, verbose_name=_('Tamamlanan Ödev'))
    completed_quizzes = models.IntegerField(default=0, verbose_name=_('Tamamlanan Quiz'))
    success_rate = models.FloatField(default=0, verbose_name=_('Başarı Oranı'))
    weak_topics = models.JSONField(default=list, blank=True, verbose_name=_('Zayıf Konular'))
    strong_topics = models.JSONField(default=list, blank=True, verbose_name=_('Kuvvetli Konular'))
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name=_('Son Aktivite'))

    class Meta:
        verbose_name = _('Öğrenci Analitiği')
        verbose_name_plural = _('Öğrenci Analitikleri')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date}"

class Badge(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Rozet Adı'))
    description = models.TextField(verbose_name=_('Açıklama'))
    icon = models.ImageField(upload_to='badges/', verbose_name=_('İkon'))
    criteria = models.JSONField(default=dict, verbose_name=_('Kazanım Kriterleri'))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='badges', blank=True, verbose_name=_('Rozeti Kazananlar'))

    class Meta:
        verbose_name = _('Rozet')
        verbose_name_plural = _('Rozetler')

    def __str__(self):
        return self.name

class Level(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Seviye Adı'))
    score_required = models.IntegerField(verbose_name=_('Seviye Puanı'))

    class Meta:
        verbose_name = _('Seviye')
        verbose_name_plural = _('Seviyeler')

    def __str__(self):
        return f"{self.name} (>{self.score_required})"

class StudentGamificationProgress(models.Model):
    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gamification', verbose_name=_('Öğrenci'))
    total_score = models.IntegerField(default=0, verbose_name=_('Toplam Puan'))
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Seviye'))
    badges = models.ManyToManyField(Badge, related_name='students', blank=True, verbose_name=_('Kazanılan Rozetler'))

    class Meta:
        verbose_name = _('Oyunlaştırma İlerlemesi')
        verbose_name_plural = _('Oyunlaştırma İlerlemeleri')

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.total_score} puan"

class LearningContent(models.Model):
    CONTENT_TYPES = (
        ('video', _('Video')),
        ('document', _('Doküman')),
        ('image', _('Görsel')),
        ('interactive', _('İnteraktif')),
    )
    title = models.CharField(max_length=200, verbose_name=_('Başlık'))
    description = models.TextField(verbose_name=_('Açıklama'))
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name=_('İçerik Tipi'))
    media_file = models.FileField(upload_to='learning_content/', null=True, blank=True, verbose_name=_('Medya Dosyası'))
    external_url = models.URLField(null=True, blank=True, verbose_name=_('Harici Bağlantı'))
    extra_note = models.TextField(blank=True, verbose_name=_('Ek Açıklama'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_contents', verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))

    class Meta:
        verbose_name = _('Eğitim İçeriği')
        verbose_name_plural = _('Eğitim İçerikleri')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Forum(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Forum Başlığı'))
    description = models.TextField(verbose_name=_('Açıklama'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_forums', verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))

    class Meta:
        verbose_name = _('Forum')
        verbose_name_plural = _('Forumlar')

    def __str__(self):
        return self.title

class ForumTopic(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='topics', verbose_name=_('Forum'))
    title = models.CharField(max_length=200, verbose_name=_('Konu Başlığı'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_topics', verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))

    class Meta:
        verbose_name = _('Forum Konusu')
        verbose_name_plural = _('Forum Konuları')

    def __str__(self):
        return self.title

class ForumPost(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Konu'))
    content = models.TextField(verbose_name=_('İçerik'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='forum_posts', verbose_name=_('Yazar'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))

    class Meta:
        verbose_name = _('Forum Mesajı')
        verbose_name_plural = _('Forum Mesajları')

    def __str__(self):
        return f"{self.author} - {self.created_at}"

class GroupAssignment(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Grup Ödevi Başlığı'))
    description = models.TextField(verbose_name=_('Açıklama'))
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_assignments', verbose_name=_('Üyeler'))
    assignment = models.ForeignKey('teacher_dashboard.Assignment', on_delete=models.CASCADE, related_name='group_assignments', verbose_name=_('Ödev'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_group_assignments', verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))

    class Meta:
        verbose_name = _('Grup Ödevi')
        verbose_name_plural = _('Grup Ödevleri')

    def __str__(self):
        return self.title

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Kullanıcı'))
    message = models.TextField(verbose_name=_('Mesaj'))
    page_url = models.CharField(max_length=300, verbose_name=_('Sayfa URL'))
    email = models.EmailField(max_length=150, null=True, blank=True, verbose_name=_('E-posta'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    is_answered = models.BooleanField(default=False, verbose_name=_('Yanıtlandı mı'))

    class Meta:
        verbose_name = _('Geri Bildirim')
        verbose_name_plural = _('Geri Bildirimler')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user or 'Anonim'} - {self.page_url}"

# ======================
# LMS Core Data Models
# ======================

class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Ders Adı'))
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Ders Kodu'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teaching_courses', verbose_name=_('Öğretmen'))
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', blank=True, verbose_name=_('Öğrenciler'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Ders')
        verbose_name_plural = _('Dersler')

    def __str__(self):
        return f"{self.code} - {self.name}"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name=_('Ders'))
    title = models.CharField(max_length=200, verbose_name=_('Konu Başlığı'))
    content = models.TextField(blank=True, verbose_name=_('İçerik'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Sıra'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Ders Konusu')
        verbose_name_plural = _('Ders Konuları')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class LearningOutcome(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Kazanım Kodu'))
    description = models.TextField(verbose_name=_('Kazanım Açıklaması'))

    class Meta:
        verbose_name = _('Öğrenme Kazanımı')
        verbose_name_plural = _('Öğrenme Kazanımları')

    def __str__(self):
        return self.code


class LessonOutcome(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='outcomes', verbose_name=_('Ders Konusu'))
    outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE, related_name='lessons', verbose_name=_('Kazanım'))

    class Meta:
        verbose_name = _('Ders-Kazanım Eşlemesi')
        verbose_name_plural = _('Ders-Kazanım Eşlemeleri')
        unique_together = ('lesson', 'outcome')

    def __str__(self):
        return f"{self.lesson} -> {self.outcome}"


class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', _('Çoktan Seçmeli')),
        ('text', _('Açık Uçlu')),
        ('bool', _('Doğru/Yanlış')),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions', verbose_name=_('Ders'))
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions', verbose_name=_('Ders Konusu'))
    text = models.TextField(verbose_name=_('Soru'))
    type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='mcq', verbose_name=_('Soru Tipi'))
    points = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('1.00'), verbose_name=_('Puan'))
    choices = models.JSONField(default=list, blank=True, verbose_name=_('Seçenekler'))
    correct_answer = models.JSONField(default=None, null=True, blank=True, verbose_name=_('Doğru Cevap'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_questions', verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Soru')
        verbose_name_plural = _('Sorular')

    def __str__(self):
        return f"Q{self.pk} - {self.type}"


class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams', verbose_name=_('Ders'))
    title = models.CharField(max_length=200, verbose_name=_('Sınav Başlığı'))
    questions = models.ManyToManyField(Question, related_name='exams', verbose_name=_('Sorular'))
    start_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Başlangıç'))
    end_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Bitiş'))
    duration_minutes = models.PositiveIntegerField(default=60, verbose_name=_('Süre (dk)'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Sınav')
        verbose_name_plural = _('Sınavlar')

    def __str__(self):
        return self.title


class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='submissions', verbose_name=_('Sınav'))
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_submissions', verbose_name=_('Öğrenci'))
    submitted_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict, verbose_name=_('Cevaplar'))
    auto_score = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Otomatik Puan'))
    manual_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name=_('Manuel Puan'))
    flags = models.JSONField(default=dict, blank=True, verbose_name=_('İşaretler'))

    class Meta:
        verbose_name = _('Sınav Teslimi')
        verbose_name_plural = _('Sınav Teslimleri')
        unique_together = ('exam', 'student')

    @property
    def total_score(self):
        return (self.manual_score if self.manual_score is not None else 0) + (self.auto_score or 0)


class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions', verbose_name=_('Ders'))
    starts_at = models.DateTimeField(verbose_name=_('Başlangıç'))
    duration_minutes = models.PositiveIntegerField(default=45, verbose_name=_('Süre (dk)'))
    topic = models.CharField(max_length=200, blank=True, verbose_name=_('Konu'))

    class Meta:
        verbose_name = _('Ders Oturumu')
        verbose_name_plural = _('Ders Oturumları')


class AttendanceRecord(models.Model):
    STATUS = (
        ('present', _('Var')),
        ('absent', _('Yok')),
        ('excused', _('İzinli')),
        ('late', _('Geç')),
    )
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendance', verbose_name=_('Oturum'))
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance', verbose_name=_('Öğrenci'))
    status = models.CharField(max_length=10, choices=STATUS, default='present', verbose_name=_('Durum'))
    note = models.CharField(max_length=255, blank=True, verbose_name=_('Not'))

    class Meta:
        verbose_name = _('Yoklama Kaydı')
        verbose_name_plural = _('Yoklama Kayıtları')
        unique_together = ('session', 'student')


class PortfolioItem(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio_items', verbose_name=_('Öğrenci'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='portfolio_items', verbose_name=_('Ders'))
    title = models.CharField(max_length=200, verbose_name=_('Başlık'))
    artifact_file = models.FileField(upload_to='eportfolio/', null=True, blank=True, verbose_name=_('Dosya'))
    artifact_url = models.URLField(null=True, blank=True, verbose_name=_('Bağlantı'))
    reflection = models.TextField(blank=True, verbose_name=_('Yansıtma'))
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_('Puan'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('E-Portfolyo Öğesi')
        verbose_name_plural = _('E-Portfolyo Öğeleri')


class Tournament(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Turnuva Başlığı'))
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='tournaments', verbose_name=_('Ders'))
    starts_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Başlangıç'))
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Bitiş'))
    rules = models.TextField(blank=True, verbose_name=_('Kurallar'))
    standings = models.JSONField(default=list, blank=True, verbose_name=_('Sıralama'))

    class Meta:
        verbose_name = _('Turnuva')
        verbose_name_plural = _('Turnuvalar')


class CheatingIncident(models.Model):
    submission = models.ForeignKey(ExamSubmission, on_delete=models.CASCADE, related_name='incidents', verbose_name=_('Teslim'))
    incident_type = models.CharField(max_length=50, verbose_name=_('İhlal Tipi'))
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_('Benzerlik Skoru'))
    evidence = models.TextField(blank=True, verbose_name=_('Kanıt'))
    resolved = models.BooleanField(default=False, verbose_name=_('Çözüldü'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Kopya/İş Birliği İhlali')
        verbose_name_plural = _('Kopya/İş Birliği İhlalleri')
