from django.db import models
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
