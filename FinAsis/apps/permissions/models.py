# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission as DjangoPermission
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ActiveManager(models.Manager):
    """
    Sadece aktif objeleri döndüren custom manager.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Permission(models.Model):
    """
    Özel yetki modeli. Django native Permission ile eşleşebilir.
    """
    name = models.CharField(_('İsim'), max_length=255)
    codename = models.CharField(_('Kod adı'), max_length=100)
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        verbose_name=_('İçerik tipi'),
        related_name='custom_permissions'
    )
    description = models.TextField(_('Açıklama'), blank=True, max_length=500)
    is_active = models.BooleanField(_('Aktif mi?'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)
    django_permission = models.OneToOneField(
        DjangoPermission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Django Yetkisi'),
        help_text=_('Django native permission ile eşleşir.')
    )

    objects = models.Manager()  # default
    active = ActiveManager()    # sadece aktifler

    class Meta:
        app_label = 'permissions'
        verbose_name = _('Yetki')
        verbose_name_plural = _('Yetkiler')
        unique_together = [['content_type', 'codename']]
        ordering = ['content_type__app_label', 'content_type__model', 'codename']

    def __str__(self):
        return f"{self.content_type.app_label}.{self.codename}"

class Role(models.Model):
    """
    Rol modeli. Hiyerarşik yapı için parent eklenmiştir.
    """
    SYSTEM = 'SYSTEM'
    GAME = 'GAME'
    CUSTOM = 'CUSTOM'
    ROLE_TYPE_CHOICES = [
        (SYSTEM, _('Sistem')),
        (GAME, _('Oyun')),
        (CUSTOM, _('Özel')),
    ]
    OYUNCU = 'Oyuncu'
    name = models.CharField(_('İsim'), max_length=255)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('Yetkiler'),
        blank=True,
    )
    description = models.TextField(_('Açıklama'), blank=True, max_length=500)
    type = models.CharField(_('Rol Tipi'), max_length=10, choices=ROLE_TYPE_CHOICES, default=CUSTOM)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', verbose_name=_('Üst Rol'))
    is_active = models.BooleanField(_('Aktif mi?'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        app_label = 'permissions'
        verbose_name = _('Rol')
        verbose_name_plural = _('Roller')
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def create_game_role(cls):
        """Oyun için özel rolü oluşturur veya döner."""
        obj, created = cls.objects.get_or_create(name=cls.OYUNCU, defaults={
            'description': 'Sadece oyun modülüne erişimi olan kullanıcı rolü.'
        })
        return obj

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
    is_active = models.BooleanField(_('Aktif mi?'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        app_label = 'permissions'
        verbose_name = _('Kullanıcı rolü')
        verbose_name_plural = _('Kullanıcı rolleri')
        unique_together = [['user', 'role']]
        ordering = ['user__username', 'role__name']

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

# Kullanıcıya doğrudan yetki atama için ek model (isteğe bağlı)
class UserPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_user_permissions', verbose_name=_('Kullanıcı'))
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='custom_permission_permissions', verbose_name=_('Yetki'))
    is_active = models.BooleanField(_('Aktif mi?'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme tarihi'), auto_now=True)

    class Meta:
        app_label = 'permissions'
        verbose_name = _('Kullanıcı Yetkisi')
        verbose_name_plural = _('Kullanıcı Yetkileri')
        unique_together = [['user', 'permission']]
        ordering = ['user__username', 'permission__codename']

    def __str__(self):
        return f"{self.user.username} - {self.permission}" 