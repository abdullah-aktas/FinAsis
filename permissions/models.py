from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Permission(models.Model):
    """
    Özel yetki modeli.
    """
    name = models.CharField(_('İsim'), max_length=255)
    codename = models.CharField(_('Kod adı'), max_length=100)
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        verbose_name=_('İçerik tipi'),
        related_name='custom_permissions'
    )
    description = models.TextField(_('Açıklama'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Yetki')
        verbose_name_plural = _('Yetkiler')
        unique_together = [['content_type', 'codename']]
        ordering = ['content_type__app_label', 'content_type__model', 'codename']

    def __str__(self):
        return f"{self.content_type.app_label}.{self.codename}"

class Role(models.Model):
    """
    Rol modeli.
    """
    name = models.CharField(_('İsim'), max_length=255)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('Yetkiler'),
        blank=True,
    )
    description = models.TextField(_('Açıklama'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Rol')
        verbose_name_plural = _('Roller')
        ordering = ['name']

    def __str__(self):
        return self.name

class UserRole(models.Model):
    """
    Kullanıcı rol ilişkisi modeli.
    """
    user = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name=_('Kullanıcı'),
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        models.CASCADE,
        verbose_name=_('Rol'),
        related_name='user_roles'
    )
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Kullanıcı rolü')
        verbose_name_plural = _('Kullanıcı rolleri')
        unique_together = [['user', 'role']]
        ordering = ['user__username', 'role__name']

    def __str__(self):
        return f"{self.user.username} - {self.role.name}" 