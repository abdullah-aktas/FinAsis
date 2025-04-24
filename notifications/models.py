from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Notification(models.Model):
    """
    Kullanıcı bildirimleri için model.
    """
    NOTIFICATION_TYPES = (
        ('info', _('Bilgi')),
        ('success', _('Başarılı')),
        ('warning', _('Uyarı')),
        ('error', _('Hata')),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Kullanıcı')
    )
    title = models.CharField(_('Başlık'), max_length=255)
    message = models.TextField(_('Mesaj'))
    notification_type = models.CharField(
        _('Bildirim Tipi'),
        max_length=10,
        choices=NOTIFICATION_TYPES,
        default='info'
    )
    is_read = models.BooleanField(_('Okundu'), default=False)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    related_object_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('İlişkili Nesne Tipi')
    )
    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('İlişkili Nesne ID')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Bildirim')
        verbose_name_plural = _('Bildirimler')

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Bildirimi okundu olarak işaretler."""
        if not self.is_read:
            self.is_read = True
            self.save()

    def mark_as_unread(self):
        """Bildirimi okunmadı olarak işaretle"""
        self.is_read = False
        self.save(update_fields=['is_read', 'updated_at']) 