# -*- coding: utf-8 -*-
"""
Rol ve izin kontrol sistemi için veritabanı modelleri.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission as DjangoPermission
from django.core.cache import cache
from django.contrib.auth import get_user_model
from typing import Type
import uuid
from datetime import datetime, timedelta
import re

# User modeli için type alias
# type: ignore
UserModel = get_user_model()

class CacheHelper:
    @staticmethod
    def delete_pattern(pattern):
        """Delete cache keys matching the given pattern."""
        # Django cache backend'i doğrudan pattern silmeyi desteklemediği için
        # tüm cache'i temizliyoruz
        cache.clear()

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('İzin Adı'), max_length=100, unique=True)
    codename = models.CharField(_('Kod Adı'), max_length=100, unique=True)
    module = models.CharField(_('Modül'), max_length=100)
    permission_type = models.CharField(_('İzin Tipi'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        CacheHelper.delete_pattern('permissions:*')

    def delete(self, *args, **kwargs):
        CacheHelper.delete_pattern('permissions:*')
        super().delete(*args, **kwargs)


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
        CacheHelper.delete_pattern('role:*')
        CacheHelper.delete_pattern('user_roles:*')


class UserRole(models.Model):
    """
    Kullanıcı ve rol ilişkisi için model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        UserModel,
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
        UserModel,
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'permissions'
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
        CacheHelper.delete_pattern(f'user_roles:{self.user.id}:*')

    def delete(self, *args, **kwargs):
        CacheHelper.delete_pattern(f'user_roles:{self.user.id}:*')
        super().delete(*args, **kwargs)


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
        UserModel,
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
        app_label = 'permissions'
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
        app_label = 'permissions'
        verbose_name = _('Kaynak')
        verbose_name_plural = _('Kaynaklar')
        ordering = ['name']

    def __str__(self):
        return self.name


class ResourcePermission(models.Model):
    """
    Kaynak ve izin ilişkisi için model.
    """
    class Meta:
        app_label = 'permissions'
        verbose_name = 'Kaynak İzni'
        verbose_name_plural = 'Kaynak İzinleri'

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

    def __str__(self):
        return f"{self.resource.name} - {self.permission.name}"


class PermissionDelegation(models.Model):
    """
    İzin devretme işlemleri için model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delegator = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        verbose_name=_('Devreden'),
        related_name='delegated_permissions'
    )
    delegatee = models.ForeignKey(
        UserModel,
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
        app_label = 'permissions'
        verbose_name = _('İzin Devri')
        verbose_name_plural = _('İzin Devirleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.delegator.username} -> {self.delegatee.username} - {self.permission.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # İzin devir cache'ini temizle
        CacheHelper.delete_pattern(f'delegation:{self.delegatee.id}:*')


class TwoFactorAuth(models.Model):
    """
    İki faktörlü kimlik doğrulama için model.
    """
    class Meta:
        app_label = 'permissions'
        verbose_name = 'İki Faktörlü Doğrulama'
        verbose_name_plural = 'İki Faktörlü Doğrulamalar'

    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE,
        verbose_name=_('Kullanıcı'),
        related_name='two_factor_auth'
    )
    secret_key = models.CharField(_('Gizli Anahtar'), max_length=32)
    backup_codes = models.JSONField(default=list)
    is_enabled = models.BooleanField(_('Aktif'), default=False)
    last_used = models.DateTimeField(
        _('Son Kullanım'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    def __str__(self):
        return f"{self.user.username} - 2FA {'Aktif' if self.is_enabled else 'Pasif'}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 2FA cache'ini temizle
        CacheHelper.delete_pattern(f'2fa_status:{self.user.id}:*')


class IPWhitelist(models.Model):
    """
    IP beyaz listesi için model.
    """
    class Meta:
        app_label = 'permissions'
        verbose_name = 'IP Beyaz Listesi'
        verbose_name_plural = 'IP Beyaz Listeleri'

    ip_address = models.GenericIPAddressField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ip_address} - {'Aktif' if self.is_active else 'Pasif'}"


class KobiUserRole(models.Model):
    """KOBİ kullanıcıları için özel rol modeli"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'KOBİ Kullanıcı Rolü'
        verbose_name_plural = 'KOBİ Kullanıcı Rolleri'

    def __str__(self):
        return self.name


class KobiUserProfile(models.Model):
    """KOBİ kullanıcıları için özel profil modeli"""
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='kobi_profile')
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    role = models.ForeignKey(KobiUserRole, on_delete=models.SET_NULL, null=True)
    is_primary_contact = models.BooleanField(default=False)
    phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    last_training_date = models.DateTimeField(null=True, blank=True)
    preferences = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'KOBİ Kullanıcı Profili'
        verbose_name_plural = 'KOBİ Kullanıcı Profilleri'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name}" 