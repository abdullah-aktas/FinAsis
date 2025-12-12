from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid

# Create your models here.


class FinancialTermCard(models.Model):
    term = models.CharField(max_length=100, verbose_name=_("Terim"))
    description = models.TextField(verbose_name=_("Açıklama"))
    example = models.TextField(verbose_name=_("Örnek"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.term

    class Meta:
        ordering = ["-created_at"]


class StudentAnalytics(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analytics",
        verbose_name=_("Öğrenci"),
    )
    date = models.DateField(auto_now_add=True, verbose_name=_("Tarih"))
    completed_assignments = models.IntegerField(
        default=0, verbose_name=_("Tamamlanan Ödev")
    )
    completed_quizzes = models.IntegerField(
        default=0, verbose_name=_("Tamamlanan Quiz")
    )
    success_rate = models.FloatField(default=0, verbose_name=_("Başarı Oranı"))
    weak_topics = models.JSONField(
        default=list, blank=True, verbose_name=_("Zayıf Konular")
    )
    strong_topics = models.JSONField(
        default=list, blank=True, verbose_name=_("Kuvvetli Konular")
    )
    last_activity = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Son Aktivite")
    )

    class Meta:
        verbose_name = _("Öğrenci Analitiği")
        verbose_name_plural = _("Öğrenci Analitikleri")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date}"


class Badge(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Rozet Adı"))
    description = models.TextField(verbose_name=_("Açıklama"))
    icon = models.ImageField(upload_to="badges/", verbose_name=_("İkon"))
    criteria = models.JSONField(default=dict, verbose_name=_("Kazanım Kriterleri"))
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="badges",
        blank=True,
        verbose_name=_("Rozeti Kazananlar"),
    )

    class Meta:
        verbose_name = _("Eğitim Rozeti")
        verbose_name_plural = _("Eğitim Rozetleri")

    def __str__(self):
        return self.name


class Level(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Seviye Adı"))
    score_required = models.IntegerField(verbose_name=_("Seviye Puanı"))

    class Meta:
        verbose_name = _("Seviye")
        verbose_name_plural = _("Seviyeler")

    def __str__(self):
        return f"{self.name} (>{self.score_required})"


class StudentGamificationProgress(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gamification",
        verbose_name=_("Öğrenci"),
    )
    total_score = models.IntegerField(default=0, verbose_name=_("Toplam Puan"))
    level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Seviye"),
    )
    badges = models.ManyToManyField(
        Badge, related_name="students", blank=True, verbose_name=_("Kazanılan Rozetler")
    )

    class Meta:
        verbose_name = _("Oyunlaştırma İlerlemesi")
        verbose_name_plural = _("Oyunlaştırma İlerlemeleri")

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.total_score} puan"


class LearningContent(models.Model):
    CONTENT_TYPES = (
        ("video", _("Video")),
        ("document", _("Doküman")),
        ("image", _("Görsel")),
        ("interactive", _("İnteraktif")),
    )
    title = models.CharField(max_length=200, verbose_name=_("Başlık"))
    description = models.TextField(verbose_name=_("Açıklama"))
    content_type = models.CharField(
        max_length=20, choices=CONTENT_TYPES, verbose_name=_("İçerik Tipi")
    )
    media_file = models.FileField(
        upload_to="learning_content/",
        null=True,
        blank=True,
        verbose_name=_("Medya Dosyası"),
    )
    external_url = models.URLField(
        null=True, blank=True, verbose_name=_("Harici Bağlantı")
    )
    extra_note = models.TextField(blank=True, verbose_name=_("Ek Açıklama"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_contents",
        verbose_name=_("Oluşturan"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )

    class Meta:
        verbose_name = _("Eğitim İçeriği")
        verbose_name_plural = _("Eğitim İçerikleri")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Forum(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Forum Başlığı"))
    description = models.TextField(verbose_name=_("Açıklama"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_forums",
        verbose_name=_("Oluşturan"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )

    class Meta:
        verbose_name = _("Forum")
        verbose_name_plural = _("Forumlar")

    def __str__(self):
        return self.title


class ForumTopic(models.Model):
    forum = models.ForeignKey(
        Forum, on_delete=models.CASCADE, related_name="topics", verbose_name=_("Forum")
    )
    title = models.CharField(max_length=200, verbose_name=_("Konu Başlığı"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_topics",
        verbose_name=_("Oluşturan"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )

    class Meta:
        verbose_name = _("Forum Konusu")
        verbose_name_plural = _("Forum Konuları")

    def __str__(self):
        return self.title


class ForumPost(models.Model):
    topic = models.ForeignKey(
        ForumTopic,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Konu"),
    )
    content = models.TextField(verbose_name=_("İçerik"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="forum_posts",
        verbose_name=_("Yazar"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )

    class Meta:
        verbose_name = _("Forum Mesajı")
        verbose_name_plural = _("Forum Mesajları")

    def __str__(self):
        return f"{self.author} - {self.created_at}"


class GroupAssignment(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Grup Ödevi Başlığı"))
    description = models.TextField(verbose_name=_("Açıklama"))
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="group_assignments",
        verbose_name=_("Üyeler"),
    )
    assignment = models.ForeignKey(
        "teacher_dashboard.Assignment",
        on_delete=models.CASCADE,
        related_name="group_assignments",
        verbose_name=_("Ödev"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_group_assignments",
        verbose_name=_("Oluşturan"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )

    class Meta:
        verbose_name = _("Grup Ödevi")
        verbose_name_plural = _("Grup Ödevleri")

    def __str__(self):
        return self.title


class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Kullanıcı"),
    )
    message = models.TextField(verbose_name=_("Mesaj"))
    page_url = models.CharField(max_length=300, verbose_name=_("Sayfa URL"))
    email = models.EmailField(
        max_length=150, null=True, blank=True, verbose_name=_("E-posta")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )
    is_answered = models.BooleanField(default=False, verbose_name=_("Yanıtlandı mı"))

    class Meta:
        verbose_name = _("Geri Bildirim")
        verbose_name_plural = _("Geri Bildirimler")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user or 'Anonim'} - {self.page_url}"


# ======================
# LMS Core Data Models
# ======================


class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Ders Adı"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Ders Kodu"))
    description = models.TextField(blank=True, verbose_name=_("Açıklama"))
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teaching_courses",
        verbose_name=_("Öğretmen"),
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_courses",
        blank=True,
        verbose_name=_("Öğrenciler"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Ders")
        verbose_name_plural = _("Dersler")

    def __str__(self):
        return f"{self.code} - {self.name}"


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name=_("Ders")
    )
    title = models.CharField(max_length=200, verbose_name=_("Konu Başlığı"))
    content = models.TextField(blank=True, verbose_name=_("İçerik"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Sıra"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Ders Konusu")
        verbose_name_plural = _("Ders Konuları")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class LearningOutcome(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Kazanım Kodu"))
    description = models.TextField(verbose_name=_("Kazanım Açıklaması"))

    class Meta:
        verbose_name = _("Öğrenme Kazanımı")
        verbose_name_plural = _("Öğrenme Kazanımları")

    def __str__(self):
        return self.code


class LessonOutcome(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="outcomes",
        verbose_name=_("Ders Konusu"),
    )
    outcome = models.ForeignKey(
        LearningOutcome,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Kazanım"),
    )

    class Meta:
        verbose_name = _("Ders-Kazanım Eşlemesi")
        verbose_name_plural = _("Ders-Kazanım Eşlemeleri")
        unique_together = ("lesson", "outcome")

    def __str__(self):
        return f"{self.lesson} -> {self.outcome}"


class Question(models.Model):
    QUESTION_TYPES = (
        ("mcq", _("Çoktan Seçmeli")),
        ("text", _("Açık Uçlu")),
        ("bool", _("Doğru/Yanlış")),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("Ders"),
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
        verbose_name=_("Ders Konusu"),
    )
    text = models.TextField(verbose_name=_("Soru"))
    type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES,
        default="mcq",
        verbose_name=_("Soru Tipi"),
    )
    points = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("1.00"), verbose_name=_("Puan")
    )
    choices = models.JSONField(default=list, blank=True, verbose_name=_("Seçenekler"))
    correct_answer = models.JSONField(
        default=None, null=True, blank=True, verbose_name=_("Doğru Cevap")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_questions",
        verbose_name=_("Oluşturan"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Soru")
        verbose_name_plural = _("Sorular")

    def __str__(self):
        return f"Q{self.pk} - {self.type}"


class Exam(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="exams", verbose_name=_("Ders")
    )
    title = models.CharField(max_length=200, verbose_name=_("Sınav Başlığı"))
    questions = models.ManyToManyField(
        Question, related_name="exams", verbose_name=_("Sorular")
    )
    start_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Başlangıç"))
    end_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Bitiş"))
    duration_minutes = models.PositiveIntegerField(
        default=60, verbose_name=_("Süre (dk)")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Sınav")
        verbose_name_plural = _("Sınavlar")

    def __str__(self):
        return self.title


class ExamSubmission(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name=_("Sınav"),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_submissions",
        verbose_name=_("Öğrenci"),
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict, verbose_name=_("Cevaplar"))
    auto_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Otomatik Puan"),
    )
    manual_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Manuel Puan"),
    )
    flags = models.JSONField(default=dict, blank=True, verbose_name=_("İşaretler"))

    class Meta:
        verbose_name = _("Sınav Teslimi")
        verbose_name_plural = _("Sınav Teslimleri")
        unique_together = ("exam", "student")

    @property
    def total_score(self):
        return (self.manual_score if self.manual_score is not None else 0) + (
            self.auto_score or 0
        )


class ClassSession(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("Ders"),
    )
    starts_at = models.DateTimeField(verbose_name=_("Başlangıç"))
    duration_minutes = models.PositiveIntegerField(
        default=45, verbose_name=_("Süre (dk)")
    )
    topic = models.CharField(max_length=200, blank=True, verbose_name=_("Konu"))

    class Meta:
        verbose_name = _("Ders Oturumu")
        verbose_name_plural = _("Ders Oturumları")


class AttendanceRecord(models.Model):
    STATUS = (
        ("present", _("Var")),
        ("absent", _("Yok")),
        ("excused", _("İzinli")),
        ("late", _("Geç")),
    )
    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name="attendance",
        verbose_name=_("Oturum"),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance",
        verbose_name=_("Öğrenci"),
    )
    status = models.CharField(
        max_length=10, choices=STATUS, default="present", verbose_name=_("Durum")
    )
    note = models.CharField(max_length=255, blank=True, verbose_name=_("Not"))

    class Meta:
        verbose_name = _("Yoklama Kaydı")
        verbose_name_plural = _("Yoklama Kayıtları")
        unique_together = ("session", "student")


class PortfolioItem(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolio_items",
        verbose_name=_("Öğrenci"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="portfolio_items",
        verbose_name=_("Ders"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Başlık"))
    artifact_file = models.FileField(
        upload_to="eportfolio/", null=True, blank=True, verbose_name=_("Dosya")
    )
    artifact_url = models.URLField(null=True, blank=True, verbose_name=_("Bağlantı"))
    reflection = models.TextField(blank=True, verbose_name=_("Yansıtma"))
    score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name=_("Puan")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("E-Portfolyo Öğesi")
        verbose_name_plural = _("E-Portfolyo Öğeleri")


class Tournament(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Turnuva Başlığı"))
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tournaments",
        verbose_name=_("Ders"),
    )
    starts_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Başlangıç"))
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Bitiş"))
    rules = models.TextField(blank=True, verbose_name=_("Kurallar"))
    standings = models.JSONField(default=list, blank=True, verbose_name=_("Sıralama"))

    class Meta:
        verbose_name = _("Eğitim Turnuvası")
        verbose_name_plural = _("Eğitim Turnuvaları")


class CheatingIncident(models.Model):
    submission = models.ForeignKey(
        ExamSubmission,
        on_delete=models.CASCADE,
        related_name="incidents",
        verbose_name=_("Teslim"),
    )
    incident_type = models.CharField(max_length=50, verbose_name=_("İhlal Tipi"))
    similarity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Benzerlik Skoru"),
    )
    evidence = models.TextField(blank=True, verbose_name=_("Kanıt"))
    resolved = models.BooleanField(default=False, verbose_name=_("Çözüldü"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Kopya/İş Birliği İhlali")
        verbose_name_plural = _("Kopya/İş Birliği İhlalleri")


# ======================
# Remote Meeting Models
# ======================


class Meeting(models.Model):
    MEETING_TYPE_CHOICES = (
        ("online", _("Çevrimiçi")),
        ("in_person", _("Yüz Yüze")),
    )
    STATUS_CHOICES = (
        ("scheduled", _("Planlandı")),
        ("completed", _("Tamamlandı")),
        ("canceled", _("İptal")),
    )

    title = models.CharField(max_length=200, verbose_name=_("Başlık"))
    description = models.TextField(blank=True, verbose_name=_("Açıklama"))
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_meetings",
        verbose_name=_("Düzenleyen"),
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="meetings",
        blank=True,
        verbose_name=_("Katılımcılar"),
    )
    meeting_type = models.CharField(
        max_length=20,
        choices=MEETING_TYPE_CHOICES,
        default="online",
        verbose_name=_("Toplantı Tipi"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled",
        verbose_name=_("Durum"),
    )
    start_time = models.DateTimeField(verbose_name=_("Başlangıç"))
    end_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Bitiş"))
    join_url = models.URLField(
        blank=True, verbose_name=_("Toplantı Bağlantısı (Zoom/Meet vb.)")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Oluşturulma Tarihi")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Güncellenme Tarihi")
    )
    # Atanan sunucu (presenter) — ekran paylaşma ve bazı kontroller için yetkili kişi
    presenter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="presented_meetings",
        verbose_name=_("Sunum Yapan"),
    )

    class Meta:
        ordering = ["-start_time"]
        verbose_name = _("Toplantı")
        verbose_name_plural = _("Toplantılar")

    def __str__(self) -> str:
        return self.title

    def clean(self):
        if self.end_time and self.end_time < self.start_time:
            raise ValidationError(
                {"end_time": _("Bitiş tarihi başlangıçtan önce olamaz.")}
            )


def generate_invitation_token() -> str:
    return uuid.uuid4().hex


class MeetingInvitation(models.Model):
    RSVP_STATUS = (
        ("pending", _("Beklemede")),
        ("accepted", _("Kabul")),
        ("declined", _("Reddet")),
        ("canceled", _("İptal")),
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name=_("Toplantı"),
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meeting_invitations",
        verbose_name=_("Davetli"),
    )
    email = models.EmailField(blank=True, verbose_name=_("E-posta"))
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_meeting_invitations",
        verbose_name=_("Davet Eden"),
    )
    token = models.CharField(
        max_length=64, unique=True, default=generate_invitation_token
    )
    status = models.CharField(
        max_length=20, choices=RSVP_STATUS, default="pending", verbose_name=_("Durum")
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Gönderim Tarihi"))
    responded_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Yanıt Tarihi")
    )

    class Meta:
        verbose_name = _("Toplantı Daveti")
        verbose_name_plural = _("Toplantı Davetleri")
        indexes = [
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"{self.meeting.title} -> {self.email or (self.invitee and self.invitee.email) or 'unknown'}"


class MeetingPresence(models.Model):
    """Per-user presence log for a Meeting.
    Records multiple sessions per user if they reconnect.
    """

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="presences",
        verbose_name=_("Toplantı"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meeting_presences",
        verbose_name=_("Kullanıcı"),
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Katılım"))
    left_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Ayrılış"))
    client_id = models.CharField(
        max_length=64, blank=True, verbose_name=_("İstemci Kimliği")
    )

    class Meta:
        verbose_name = _("Toplantı Varlığı")
        verbose_name_plural = _("Toplantı Varlıkları")
        indexes = [
            models.Index(fields=["meeting", "user", "joined_at"]),
        ]

    def __str__(self):
        mid = getattr(self, "meeting_id", None) or (self.meeting and self.meeting.pk)
        uid = getattr(self, "user_id", None) or (self.user and self.user.pk)
        return f"{mid}::{uid} {self.joined_at} -> {self.left_at or '-'}"


class MeetingRecording(models.Model):
    """Uploaded meeting recording files (client-side captured)."""

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="recordings",
        verbose_name=_("Toplantı"),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meeting_recordings",
        verbose_name=_("Yükleyen"),
    )
    file = models.FileField(
        upload_to="meeting_recordings/", verbose_name=_("Kayıt Dosyası")
    )
    kind = models.CharField(
        max_length=20, blank=True, verbose_name=_("Tür")
    )  # screen|camera
    duration_ms = models.BigIntegerField(
        null=True, blank=True, verbose_name=_("Süre (ms)")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Yükleme Zamanı")
    )
    title = models.CharField(
        max_length=200, blank=True, default="", verbose_name=_("Başlık")
    )

    class Meta:
        verbose_name = _("Toplantı Kaydı")
        verbose_name_plural = _("Toplantı Kayıtları")

    def __str__(self) -> str:  # pragma: no cover
        return f"rec:{self.pk} meeting:{getattr(self.meeting,'pk',None)}"


# ============================================================================
# GENİŞLETİLMİŞ LMS ÖZELLİKLERİ
# ============================================================================


class CourseCategory(models.Model):
    """Ders kategorileri - dersler için kategori sistemi"""

    name = models.CharField(max_length=100, unique=True, verbose_name=_("Kategori Adı"))
    description = models.TextField(blank=True, verbose_name=_("Açıklama"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("İkon"))
    color = models.CharField(max_length=7, default="#007bff", verbose_name=_("Renk"))
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name=_("Üst Kategori"),
    )
    order = models.IntegerField(default=0, verbose_name=_("Sıra"))

    class Meta:
        verbose_name = _("Ders Kategorisi")
        verbose_name_plural = _("Ders Kategorileri")
        ordering = ["order", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class EnhancedCourse(models.Model):
    """Gelişmiş ders bilgileri - Course modelini genişletir"""

    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name="enhanced_info",
        verbose_name=_("Ders"),
    )
    category = models.ForeignKey(
        CourseCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="courses",
        verbose_name=_("Kategori"),
    )

    # Görsel ve medya
    thumbnail = models.ImageField(
        upload_to="course_thumbnails/",
        null=True,
        blank=True,
        verbose_name=_("Kapak Görseli"),
    )
    video_intro = models.URLField(blank=True, verbose_name=_("Tanıtım Videosu"))

    # Detaylar
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", _("Başlangıç")),
            ("intermediate", _("Orta")),
            ("advanced", _("İleri")),
            ("expert", _("Uzman")),
        ],
        default="beginner",
        verbose_name=_("Zorluk Seviyesi"),
    )

    estimated_hours = models.IntegerField(
        default=0, verbose_name=_("Tahmini Süre (saat)")
    )
    prerequisites = models.ManyToManyField(
        Course,
        blank=True,
        related_name="required_for",
        verbose_name=_("Ön Koşul Dersler"),
    )

    # İstatistikler
    total_enrolled = models.IntegerField(default=0, verbose_name=_("Toplam Kayıt"))
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Ortalama Puan"),
    )
    total_reviews = models.IntegerField(
        default=0, verbose_name=_("Toplam Değerlendirme")
    )

    # Yayın durumu
    is_published = models.BooleanField(default=True, verbose_name=_("Yayında"))
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Yayın Tarihi")
    )

    class Meta:
        verbose_name = _("Gelişmiş Ders Bilgisi")
        verbose_name_plural = _("Gelişmiş Ders Bilgileri")

    def __str__(self):
        return f"{self.course.name} - Enhanced"


class LearningPath(models.Model):
    """Öğrenme yolları - belirli bir hedef için ders sıralaması"""

    title = models.CharField(max_length=200, verbose_name=_("Yol Başlığı"))
    description = models.TextField(verbose_name=_("Açıklama"))
    thumbnail = models.ImageField(
        upload_to="learning_paths/", null=True, blank=True, verbose_name=_("Görsel")
    )
    courses = models.ManyToManyField(
        Course,
        through="PathCourse",
        related_name="learning_paths",
        verbose_name=_("Dersler"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_paths",
        verbose_name=_("Oluşturan"),
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_paths",
        blank=True,
        verbose_name=_("Kayıtlı Öğrenciler"),
    )

    # Metadata
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", _("Başlangıç")),
            ("intermediate", _("Orta")),
            ("advanced", _("İleri")),
        ],
        default="beginner",
    )
    estimated_weeks = models.IntegerField(
        default=0, verbose_name=_("Tahmini Süre (hafta)")
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Aktif"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Öğrenme Yolu")
        verbose_name_plural = _("Öğrenme Yolları")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PathCourse(models.Model):
    """Öğrenme yolu - ders eşlemesi"""

    path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE, related_name="path_courses"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="path_memberships"
    )
    order = models.IntegerField(default=0, verbose_name=_("Sıra"))
    is_optional = models.BooleanField(default=False, verbose_name=_("İsteğe Bağlı"))

    class Meta:
        verbose_name = _("Yol Dersi")
        verbose_name_plural = _("Yol Dersleri")
        ordering = ["order"]
        unique_together = ("path", "course")

    def __str__(self):
        return f"{self.path.title} - {self.course.name}"


class Certificate(models.Model):
    """Sertifikalar - ders tamamlama sertifikaları"""

    CERTIFICATE_TYPES = [
        ("completion", _("Tamamlama")),
        ("achievement", _("Başarı")),
        ("excellence", _("Mükemmellik")),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("Öğrenci"),
    )
    course = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("Ders"),
    )
    learning_path = models.ForeignKey(
        LearningPath,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("Öğrenme Yolu"),
    )

    certificate_type = models.CharField(
        max_length=20, choices=CERTIFICATE_TYPES, default="completion"
    )
    certificate_id = models.CharField(
        max_length=50, unique=True, verbose_name=_("Sertifika No")
    )

    # Puanlama
    final_score = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Final Puanı")
    )
    grade = models.CharField(max_length=5, blank=True, verbose_name=_("Harf Notu"))

    # Dosya
    file = models.FileField(
        upload_to="certificates/", null=True, blank=True, verbose_name=_("PDF Dosyası")
    )

    # Metadata
    issued_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Veriliş Tarihi")
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="issued_certificates",
        verbose_name=_("Veren"),
    )

    # Doğrulama
    verification_code = models.CharField(
        max_length=100, blank=True, verbose_name=_("Doğrulama Kodu")
    )
    is_revoked = models.BooleanField(default=False, verbose_name=_("İptal Edildi"))
    revoked_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("İptal Tarihi")
    )

    class Meta:
        verbose_name = _("Sertifika")
        verbose_name_plural = _("Sertifikalar")
        ordering = ["-issued_at"]

    def __str__(self):
        course_name = self.course.name if self.course else self.learning_path.title
        return f"{self.certificate_id} - {self.student.get_full_name()} - {course_name}"


class Announcement(models.Model):
    """Duyurular - ders duyuruları"""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="announcements",
        verbose_name=_("Ders"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Başlık"))
    content = models.TextField(verbose_name=_("İçerik"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="announcements",
        verbose_name=_("Yazar"),
    )

    # Önem seviyesi
    priority = models.CharField(
        max_length=20,
        choices=[
            ("low", _("Düşük")),
            ("normal", _("Normal")),
            ("high", _("Yüksek")),
            ("urgent", _("Acil")),
        ],
        default="normal",
        verbose_name=_("Öncelik"),
    )

    # Yayın
    is_published = models.BooleanField(default=True, verbose_name=_("Yayında"))
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Yayın Tarihi")
    )

    # Bildirim
    send_notification = models.BooleanField(
        default=True, verbose_name=_("Bildirim Gönder")
    )
    notification_sent = models.BooleanField(
        default=False, verbose_name=_("Bildirim Gönderildi")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Duyuru")
        verbose_name_plural = _("Duyurular")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class LessonResource(models.Model):
    """Ders kaynakları - her ders için ek kaynaklar"""

    RESOURCE_TYPES = [
        ("pdf", _("PDF")),
        ("video", _("Video")),
        ("link", _("Bağlantı")),
        ("presentation", _("Sunum")),
        ("code", _("Kod Örneği")),
        ("quiz", _("Alıştırma")),
        ("other", _("Diğer")),
    ]

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="resources",
        verbose_name=_("Ders"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Başlık"))
    resource_type = models.CharField(
        max_length=20, choices=RESOURCE_TYPES, default="pdf"
    )

    # Dosya veya bağlantı
    file = models.FileField(
        upload_to="lesson_resources/", null=True, blank=True, verbose_name=_("Dosya")
    )
    external_url = models.URLField(blank=True, verbose_name=_("Harici Bağlantı"))

    description = models.TextField(blank=True, verbose_name=_("Açıklama"))
    order = models.IntegerField(default=0, verbose_name=_("Sıra"))

    # Erişim kontrolü
    is_downloadable = models.BooleanField(default=True, verbose_name=_("İndirilebilir"))
    requires_completion = models.BooleanField(
        default=False, verbose_name=_("Tamamlama Gerektirir")
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_resources",
        verbose_name=_("Yükleyen"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Ders Kaynağı")
        verbose_name_plural = _("Ders Kaynakları")
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class StudentGoal(models.Model):
    """Öğrenci hedefleri - kişisel öğrenme hedefleri"""

    GOAL_TYPES = [
        ("course_completion", _("Ders Tamamlama")),
        ("skill_mastery", _("Beceri Kazanımı")),
        ("grade_achievement", _("Not Hedefi")),
        ("time_management", _("Zaman Yönetimi")),
        ("custom", _("Özel")),
    ]

    STATUS_CHOICES = [
        ("not_started", _("Başlanmadı")),
        ("in_progress", _("Devam Ediyor")),
        ("completed", _("Tamamlandı")),
        ("abandoned", _("Terk Edildi")),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_goals",
        verbose_name=_("Öğrenci"),
    )
    goal_type = models.CharField(max_length=30, choices=GOAL_TYPES, default="custom")
    title = models.CharField(max_length=200, verbose_name=_("Hedef Başlığı"))
    description = models.TextField(blank=True, verbose_name=_("Açıklama"))

    # Hedef detayları
    course = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="student_goals",
        verbose_name=_("Ders"),
    )
    target_date = models.DateField(verbose_name=_("Hedef Tarihi"))
    target_metric = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Hedef Metrik"),
    )
    current_progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Mevcut İlerleme"),
    )

    # Durum
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Tamamlanma Tarihi")
    )

    # Hatırlatıcılar
    reminder_enabled = models.BooleanField(
        default=True, verbose_name=_("Hatırlatıcı Aktif")
    )
    reminder_frequency = models.CharField(
        max_length=20,
        choices=[
            ("daily", _("Günlük")),
            ("weekly", _("Haftalık")),
            ("monthly", _("Aylık")),
        ],
        default="weekly",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Öğrenci Hedefi")
        verbose_name_plural = _("Öğrenci Hedefleri")
        ordering = ["target_date", "-created_at"]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.title}"


class CourseReview(models.Model):
    """Ders değerlendirmeleri - öğrencilerin ders yorumları"""

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("Ders")
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_reviews",
        verbose_name=_("Öğrenci"),
    )

    # Puanlama (1-5)
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], verbose_name=_("Puan")
    )

    # Detaylı puanlama
    content_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name=_("İçerik"),
    )
    instructor_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name=_("Eğitmen"),
    )
    difficulty_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name=_("Zorluk"),
    )

    # Yorum
    title = models.CharField(max_length=200, verbose_name=_("Başlık"))
    comment = models.TextField(verbose_name=_("Yorum"))

    # Onay ve yayın
    is_approved = models.BooleanField(default=False, verbose_name=_("Onaylandı"))
    is_published = models.BooleanField(default=True, verbose_name=_("Yayında"))

    # Faydalı bulma
    helpful_count = models.IntegerField(default=0, verbose_name=_("Faydalı Sayısı"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Ders Değerlendirmesi")
        verbose_name_plural = _("Ders Değerlendirmeleri")
        ordering = ["-created_at"]
        unique_together = ("course", "student")

    def __str__(self):
        return f"{self.course.name} - {self.student.get_full_name()} ({self.rating}★)"


class StudySession(models.Model):
    """Çalışma oturumları - öğrenci çalışma zamanı takibi"""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_sessions",
        verbose_name=_("Öğrenci"),
    )
    course = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="study_sessions",
        verbose_name=_("Ders"),
    )
    lesson = models.ForeignKey(
        Lesson,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="study_sessions",
        verbose_name=_("Konu"),
    )

    # Zaman
    started_at = models.DateTimeField(verbose_name=_("Başlangıç"))
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Bitiş"))
    duration_minutes = models.IntegerField(
        null=True, blank=True, verbose_name=_("Süre (dk)")
    )

    # Notlar
    notes = models.TextField(blank=True, verbose_name=_("Notlar"))
    focus_score = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name=_("Konsantrasyon"),
    )

    # Device/Platform
    device_type = models.CharField(max_length=50, blank=True, verbose_name=_("Cihaz"))

    class Meta:
        verbose_name = _("Çalışma Oturumu")
        verbose_name_plural = _("Çalışma Oturumları")
        ordering = ["-started_at"]

    def save(self, *args, **kwargs):
        if self.ended_at and self.started_at:
            delta = self.ended_at - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
