from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class HelpCategory(models.Model):
    """Yardım kategorileri"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Yardım Kategorisi'
        verbose_name_plural = 'Yardım Kategorileri'
        ordering = ['order']

    def __str__(self):
        return self.name

class HelpArticle(models.Model):
    """Yardım makaleleri"""
    category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Yardım Makalesi'
        verbose_name_plural = 'Yardım Makaleleri'

    def __str__(self):
        return self.title

class SupportTicket(models.Model):
    """Destek talepleri"""
    STATUS_CHOICES = (
        ('open', 'Açık'),
        ('in_progress', 'İşlemde'),
        ('resolved', 'Çözüldü'),
        ('closed', 'Kapandı')
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Destek Talebi'
        verbose_name_plural = 'Destek Talepleri'

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class TicketComment(models.Model):
    """Destek talebi yorumları"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Talep Yorumu'
        verbose_name_plural = 'Talep Yorumları'

    def __str__(self):
        return f"Yorum #{self.id} - {self.ticket.title}"

class UserFeedback(models.Model):
    """Kullanıcı geri bildirimleri"""
    RATING_CHOICES = (
        (1, 'Çok Kötü'),
        (2, 'Kötü'),
        (3, 'Orta'),
        (4, 'İyi'),
        (5, 'Çok İyi')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    page_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kullanıcı Geri Bildirimi'
        verbose_name_plural = 'Kullanıcı Geri Bildirimleri'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_rating_display()}" 