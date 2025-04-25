from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class TrainingCategory(models.Model):
    """Eğitim kategorileri"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    color = models.CharField(max_length=7, default='#000000')
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Eğitim Kategorisi'
        verbose_name_plural = 'Eğitim Kategorileri'
        ordering = ['order']

    def __str__(self):
        return self.name

class TrainingModule(models.Model):
    """Eğitim modülleri"""
    category = models.ForeignKey(TrainingCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text='Dakika cinsinden süre')
    video_url = models.URLField(null=True, blank=True)
    document_url = models.URLField(null=True, blank=True)
    quiz = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=(
            ('beginner', 'Başlangıç'),
            ('intermediate', 'Orta'),
            ('advanced', 'İleri')
        ),
        default='beginner'
    )
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Eğitim Modülü'
        verbose_name_plural = 'Eğitim Modülleri'

    def __str__(self):
        return self.title

class UserTrainingProgress(models.Model):
    """Kullanıcı eğitim ilerlemesi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=(
            ('not_started', 'Başlanmadı'),
            ('in_progress', 'Devam Ediyor'),
            ('completed', 'Tamamlandı')
        ),
        default='not_started'
    )
    progress = models.IntegerField(default=0)
    quiz_score = models.IntegerField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    favorite = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Kullanıcı Eğitim İlerlemesi'
        verbose_name_plural = 'Kullanıcı Eğitim İlerlemeleri'
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.module.title}"

class TrainingCertificate(models.Model):
    """Eğitim sertifikaları"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    pdf_url = models.URLField()
    share_url = models.URLField(null=True, blank=True)
    is_verified = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Eğitim Sertifikası'
        verbose_name_plural = 'Eğitim Sertifikaları'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.module.title} - {self.certificate_number}"

class TrainingBadge(models.Model):
    """Eğitim rozetleri"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    criteria = models.JSONField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Eğitim Rozeti'
        verbose_name_plural = 'Eğitim Rozetleri'

    def __str__(self):
        return self.name

class UserTrainingBadge(models.Model):
    """Kullanıcı eğitim rozetleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(TrainingBadge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kullanıcı Eğitim Rozeti'
        verbose_name_plural = 'Kullanıcı Eğitim Rozetleri'
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.badge.name}"

class TrainingFeedback(models.Model):
    """Eğitim geri bildirimleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Eğitim Geri Bildirimi'
        verbose_name_plural = 'Eğitim Geri Bildirimleri'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.module.title} - {self.rating}" 