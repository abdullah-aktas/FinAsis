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


# ============================================================================
# GENİŞLETİLMİŞ YETKİ YÖNETİM SİSTEMİ
# ============================================================================

class PermissionGroup(models.Model):
    """Yetki grupları - izinlerin gruplanması"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Grup Adı'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    permissions = models.ManyToManyField(Permission, related_name='groups', blank=True, verbose_name=_('Yetkiler'))
    
    # Metadata
    is_system = models.BooleanField(default=False, verbose_name=_('Sistem Grubu'))
    is_active = models.BooleanField(default=True, verbose_name=_('Aktif'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'permissions'
        verbose_name = _('Yetki Grubu')
        verbose_name_plural = _('Yetki Grupları')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RoleHierarchy(models.Model):
    """Rol hiyerarşisi - rol miras sistemi"""
    
    parent_role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='child_hierarchies', verbose_name=_('Üst Rol'))
    child_role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='parent_hierarchies', verbose_name=_('Alt Rol'))
    
    # İzin miras kuralları
    inherit_permissions = models.BooleanField(default=True, verbose_name=_('Yetkileri Miras Al'))
    additional_permissions = models.ManyToManyField(Permission, blank=True, related_name='hierarchy_additions', verbose_name=_('Ek Yetkiler'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'permissions'
        verbose_name = _('Rol Hiyerarşisi')
        verbose_name_plural = _('Rol Hiyerarşileri')
        unique_together = ['parent_role', 'child_role']
    
    def __str__(self):
        return f"{self.parent_role} → {self.child_role}"


class TemporaryPermission(models.Model):
    """Geçici yetkiler - süreli erişim"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temporary_permissions', verbose_name=_('Kullanıcı'))
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name=_('Yetki'))
    
    # Süre
    valid_from = models.DateTimeField(verbose_name=_('Geçerlilik Başlangıcı'))
    valid_until = models.DateTimeField(verbose_name=_('Geçerlilik Bitişi'))
    
    # Sebep
    reason = models.TextField(verbose_name=_('Sebep'))
    
    # Onay
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_temp_permissions', verbose_name=_('Onaylayan'))
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name=_('Aktif'))
    is_revoked = models.BooleanField(default=False, verbose_name=_('İptal Edildi'))
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name=_('İptal Tarihi'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'permissions'
        verbose_name = _('Geçici Yetki')
        verbose_name_plural = _('Geçici Yetkiler')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.permission} (geçici)"
    
    def is_valid(self):
        """Yetkinin hala geçerli olup olmadığını kontrol et"""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and 
            not self.is_revoked and 
            self.valid_from <= now <= self.valid_until
        )


class PermissionAudit(models.Model):
    """Yetki denetim logları"""
    
    ACTION_CHOICES = [
        ('GRANTED', _('Verildi')),
        ('REVOKED', _('İptal Edildi')),
        ('MODIFIED', _('Değiştirildi')),
        ('CHECKED', _('Kontrol Edildi')),
        ('DENIED', _('Reddedildi')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_audits', verbose_name=_('Kullanıcı'))
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name=_('Yetki'))
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name=_('Aksiyon'))
    
    # Detaylar
    resource = models.CharField(max_length=200, blank=True, verbose_name=_('Kaynak'))
    result = models.CharField(max_length=20, choices=[
        ('ALLOWED', _('İzin Verildi')),
        ('DENIED', _('Reddedildi'))
    ], blank=True, verbose_name=_('Sonuç'))
    
    # İstek bilgisi
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP Adresi'))
    user_agent = models.TextField(blank=True, verbose_name=_('User Agent'))
    
    # Metadata
    performed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='performed_permission_audits', verbose_name=_('Gerçekleştiren'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'permissions'
        verbose_name = _('Yetki Denetim Logu')
        verbose_name_plural = _('Yetki Denetim Logları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.permission}" 