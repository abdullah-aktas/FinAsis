"""
Rol ve izin kontrol sistemi için veritabanı modelleri.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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
        verbose_name = _('İzin')
        verbose_name_plural = _('İzinler')
        unique_together = ('module', 'permission_type')
        ordering = ['module', 'permission_type']

    def __str__(self):
        return f"{self.name} ({self.module}.{self.permission_type})"


class Role(models.Model):
    """
    Rol modeli.
    Her rol, bir ad ve bir grup izine sahiptir.
    """
    ROLE_TYPES = [
        ('system', _('Sistem Rolü')),
        ('custom', _('Özel Rol')),
    ]

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
    role_type = models.CharField(_('Rol Türü'), max_length=20, choices=ROLE_TYPES, default='custom')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        verbose_name=_('Oluşturan'),
        related_name='created_roles',
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = _('Rol')
        verbose_name_plural = _('Roller')
        ordering = ['name']

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Kullanıcı rol ilişkisi.
    Bir kullanıcının birden fazla rolü olabilir, ancak her biri farklı olmalıdır.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
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
    is_primary = models.BooleanField(_('Birincil Rol'), default=False, help_text=_('Kullanıcının birincil rolü'))
    assigned_at = models.DateTimeField(_('Atanma Tarihi'), auto_now_add=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        verbose_name=_('Atayan'),
        related_name='assigned_roles',
        null=True, 
        blank=True
    )
    expires_at = models.DateTimeField(_('Bitiş Tarihi'), null=True, blank=True, help_text=_('Rol geçerliliği bitiş tarihi (boş ise süresiz)'))

    class Meta:
        verbose_name = _('Kullanıcı Rolü')
        verbose_name_plural = _('Kullanıcı Rolleri')
        unique_together = ('user', 'role')
        ordering = ['-is_primary', 'assigned_at']

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

    def save(self, *args, **kwargs):
        # Eğer bir rol birincil olarak ayarlanırsa, aynı kullanıcının diğer rolleri birincil olmaktan çıkarılır
        if self.is_primary:
            UserRole.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    """
    Denetim günlüğü.
    İzin ve rol değişikliklerini ve kullanımlarını izlemek için kullanılır.
    """
    ACTION_TYPES = [
        ('create', _('Oluşturma')),
        ('update', _('Güncelleme')),
        ('delete', _('Silme')),
        ('assign', _('Atama')),
        ('revoke', _('İptal')),
        ('login', _('Giriş')),
        ('logout', _('Çıkış')),
        ('access', _('Erişim')),
        ('permission_denied', _('İzin Reddi')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        verbose_name=_('Kullanıcı'),
        null=True,
        related_name='permission_audit_logs'
    )
    action = models.CharField(_('İşlem'), max_length=20, choices=ACTION_TYPES)
    model = models.CharField(_('Model'), max_length=50)
    object_id = models.CharField(_('Nesne ID'), max_length=100)
    details = models.JSONField(_('Detaylar'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('IP Adresi'), null=True, blank=True)
    user_agent = models.TextField(_('Kullanıcı Ajanı'), blank=True)
    created_at = models.DateTimeField(_('Tarih'), auto_now_add=True)

    class Meta:
        verbose_name = _('Denetim Günlüğü')
        verbose_name_plural = _('Denetim Günlükleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model} - {self.created_at}" 