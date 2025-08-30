from django.db import models
from django.conf import settings

class ActionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    detail = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp:%Y-%m-%d %H:%M}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Bildirim: {self.user} - {self.message[:30]}"

class HelpContent(models.Model):
    ROLE_CHOICES = [
        ('genel', 'Genel Kullanıcı'),
        ('admin', 'Yönetici'),
        ('muhasebeci', 'Muhasebeci'),
        ('calisan', 'Çalışan'),
        ('ogrenci', 'Öğrenci'),
        ('ogretmen', 'Öğretmen'),
    ]
    title = models.CharField(max_length=100)
    content = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='genel')
    page_key = models.CharField(max_length=100, blank=True, null=True, help_text="Yardımın hangi sayfada gösterileceği (isteğe bağlı)")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_role_display()}] {self.title}" 