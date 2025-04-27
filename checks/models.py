from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Check(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('processing', _('İşleniyor')),
        ('completed', _('Tamamlandı')),
        ('failed', _('Başarısız')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Kullanıcı'))
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        app_label = 'checks'
        verbose_name = _('Kontrol')
        verbose_name_plural = _('Kontroller')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
