"""
Rol ve izin kontrol sistemi için veritabanı modelleri.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group, Permission
from django.core.cache import cache
import uuid
from datetime import datetime, timedelta

class Permission(models.Model):
    """
    İzin modeli. 
    Her izin, bir ad ve bir kod adına sahiptir. Ayrıca açıklama eklenebilir.
    """
    PERMISSION_TYPES = [
        ('create', _('Oluşturma')),
        ('view', _('Görüntüleme')),
        ('update', _('Güncelleme')),
        ('delete', _('Silme')),
        ('approve', _('Onaylama')),
        ('export', _('Dışa Aktarma')),
        ('import', _('İçe Aktarma')),
        ('report', _('Raporlama')),
    ]

    MODULE_CHOICES = [
        ('accounting', _('Muhasebe')),
        ('finance', _('Finans')),
        ('crm', _('Müşteri İlişkileri')),
        ('stock', _('Stok Yönetimi')),
        ('hr', _('İnsan Kaynakları')),
        ('reports', _('Raporlar')),
        ('settings', _('Ayarlar')),
        ('system', _('Sistem')),
        ('users', _('Kullanıcılar')),
        ('permissions', _('İzinler')),
        ('virtual_company', _('Sanal Şirket')),
    ]

    name = models.CharField(_('İzin Adı'), max_length=100, unique=True)
    codename = models.CharField(_('Kod Adı'), max_length=100, unique=True)
    module = models.CharField(_('Modül'), max_length=50, choices=MODULE_CHOICES)
    permission_type = models.CharField(_('İzin Türü'), max_length=20, choices=PERMISSION_TYPES)
    description = models.TextField(_('Açıklama'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        app_label = 'permissions'
        verbose_name = _('İzin')
        verbose_name_plural = _('İzinler')
        unique_together = ('module', 'permission_type')
        ordering = ['module', 'permission_type']

    def __str__(self):
        return f"{self.name} ({self.module}.{self.permission_type})"


class Role(models.Model):
    """
    Kullanıcı rolleri için model.
    """
    ROLE_TYPES = (
        ('system', _('Sistem Rolü')),
        ('custom', _('Özel Rol')),
    )

    name = models.CharField(_('Rol Adı'), max_length=100, unique=True)
    code = models.CharField(_('Rol Kodu'), max_length=50, unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('İzinler'),
        related_name='roles',
        blank=True
    )
    is_active = models.BooleanField(_('Aktif'), default=True)
    role_type = models.CharField(
        _('Rol Türü'),
        max_length=20,
        choices=ROLE_TYPES,
        default='custom'
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        app_label = 'permissions'
        verbose_name = _('Rol')
        verbose_name_plural = _('Roller')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Rol cache'ini temizle
        cache.delete_pattern('role:*')
        cache.delete_pattern('user_roles:*')


class UserRole(models.Model):
    """
    Kullanıcı ve rol ilişkisi için model.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Kullanıcı'),
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name=_('Rol'),
        related_name='user_roles'
    )
    is_primary = models.BooleanField(
        _('Birincil Rol'),
        default=False,
        help_text=_('Kullanıcının birincil rolü')
    )
    assigned_at = models.DateTimeField(_('Atanma Tarihi'), auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_('Atayan'),
        related_name='assigned_roles',
        null=True,
        blank=True
    )
    expires_at = models.DateTimeField(
        _('Bitiş Tarihi'),
        null=True,
        blank=True,
        help_text=_('Rol geçerliliği bitiş tarihi (boş ise süresiz)')
    )

    class Meta:
        verbose_name = _('Kullanıcı Rolü')
        verbose_name_plural = _('Kullanıcı Rolleri')
        unique_together = ('user', 'role')
        ordering = ['-is_primary', 'assigned_at']

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

    def save(self, *args, **kwargs):
        # Eğer bir rol birincil olarak ayarlanırsa, diğer rolleri birincil olmaktan çıkar
        if self.is_primary:
            UserRole.objects.filter(user=self.user, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)
        # Kullanıcı rol cache'ini temizle
        cache.delete_pattern(f'user_roles:{self.user.id}:*')


class AuditLog(models.Model):
    """
    Denetim kayıtları için model.
    """
    ACTION_TYPES = (
        ('create', _('Oluşturma')),
        ('update', _('Güncelleme')),
        ('delete', _('Silme')),
        ('assign', _('Atama')),
        ('revoke', _('İptal')),
        ('login', _('Giriş')),
        ('logout', _('Çıkış')),
        ('access', _('Erişim')),
        ('permission_denied', _('İzin Reddi')),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_('Kullanıcı'),
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(
        _('İşlem'),
        max_length=20,
        choices=ACTION_TYPES
    )
    model = models.CharField(_('Model'), max_length=50)
    object_id = models.CharField(_('Nesne ID'), max_length=100)
    details = models.JSONField(_('Detaylar'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(
        _('IP Adresi'),
        null=True,
        blank=True
    )
    user_agent = models.TextField(_('Kullanıcı Ajanı'), blank=True)
    created_at = models.DateTimeField(_('Tarih'), auto_now_add=True)

    class Meta:
        verbose_name = _('Denetim Kaydı')
        verbose_name_plural = _('Denetim Kayıtları')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model} - {self.created_at}"


class Resource(models.Model):
    """
    Sistem kaynakları için model.
    """
    name = models.CharField(_('Kaynak Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Kaynak')
        verbose_name_plural = _('Kaynaklar')
        ordering = ['name']

    def __str__(self):
        return self.name


class ResourcePermission(models.Model):
    """
    Kaynak ve izin ilişkisi için model.
    """
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        verbose_name=_('Kaynak'),
        related_name='resource_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        verbose_name=_('İzin'),
        related_name='resource_permissions'
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Kaynak İzni')
        verbose_name_plural = _('Kaynak İzinleri')
        unique_together = ('resource', 'permission')
        ordering = ['resource', 'permission']

    def __str__(self):
        return f"{self.resource.name} - {self.permission.name}"


class PermissionDelegation(models.Model):
    """
    İzin devretme işlemleri için model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delegator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Devreden'),
        related_name='delegated_permissions'
    )
    delegatee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Devralan'),
        related_name='received_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        verbose_name=_('İzin')
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    expires_at = models.DateTimeField(
        _('Bitiş Tarihi'),
        null=True,
        blank=True
    )
    is_active = models.BooleanField(_('Aktif'), default=True)

    class Meta:
        verbose_name = _('İzin Devri')
        verbose_name_plural = _('İzin Devirleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.delegator.username} -> {self.delegatee.username} - {self.permission.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # İzin devir cache'ini temizle
        cache.delete_pattern(f'delegation:{self.delegatee.id}:*')


class TwoFactorAuth(models.Model):
    """
    İki faktörlü kimlik doğrulama için model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Kullanıcı'),
        related_name='two_factor_auth'
    )
    secret = models.CharField(_('Gizli Anahtar'), max_length=32)
    is_enabled = models.BooleanField(_('Aktif'), default=False)
    last_used = models.DateTimeField(
        _('Son Kullanım'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('İki Faktörlü Kimlik Doğrulama')
        verbose_name_plural = _('İki Faktörlü Kimlik Doğrulamalar')

    def __str__(self):
        return f"{self.user.username} - 2FA {'Aktif' if self.is_enabled else 'Pasif'}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 2FA cache'ini temizle
        cache.delete_pattern(f'2fa_status:{self.user.id}:*')


class IPWhitelist(models.Model):
    """
    IP beyaz listesi için model.
    """
    ip_address = models.GenericIPAddressField(
        _('IP Adresi'),
        unique=True
    )
    description = models.CharField(
        _('Açıklama'),
        max_length=255,
        blank=True
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_('Oluşturan'),
        null=True
    )

    class Meta:
        verbose_name = _('IP Beyaz Listesi')
        verbose_name_plural = _('IP Beyaz Listeleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ip_address} - {self.description}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # IP beyaz liste cache'ini temizle
        cache.delete_pattern('ip_whitelist:*') 