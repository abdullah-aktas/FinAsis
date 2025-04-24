from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    """Özelleştirilmiş kullanıcı modeli."""
    
    # Temel bilgiler
    email = models.EmailField(_('E-posta'), unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Telefon numarası geçerli bir formatta olmalıdır.')
    )
    phone = models.CharField(_('Telefon'), validators=[phone_regex], max_length=17, blank=True)
    
    # Profil ilişkisi
    profile = models.OneToOneField('UserProfile', on_delete=models.CASCADE, related_name='user_profile', null=True, blank=True)
    
    # Profil bilgileri
    profile_picture = models.ImageField(_('Profil Resmi'), upload_to='profile_pictures/', blank=True)
    bio = models.TextField(_('Hakkımda'), max_length=500, blank=True)
    birth_date = models.DateField(_('Doğum Tarihi'), null=True, blank=True)
    
    # İletişim bilgileri
    address = models.TextField(_('Adres'), max_length=200, blank=True)
    city = models.CharField(_('Şehir'), max_length=100, blank=True)
    country = models.CharField(_('Ülke'), max_length=100, blank=True)
    
    # Güvenlik
    two_factor_enabled = models.BooleanField(_('İki Faktörlü Doğrulama'), default=False)
    two_factor_secret = models.CharField(max_length=100, blank=True)
    last_device_id = models.CharField(max_length=100, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    fcm_token = models.CharField(max_length=200, blank=True)
    last_password_change = models.DateTimeField(_('Son Şifre Değişikliği'), auto_now=True)
    
    # Ayarlar
    language = models.CharField(_('Dil'), max_length=10, choices=settings.LANGUAGES, default='tr')
    timezone = models.CharField(_('Zaman Dilimi'), max_length=50, default='Europe/Istanbul')
    
    # Meta bilgileri
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Kullanıcı')
        verbose_name_plural = _('Kullanıcılar')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'username': self.username})

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(_('telefon numarası'), max_length=20, blank=True)
    address = models.TextField(_('adres'), blank=True)
    city = models.CharField(_('şehir'), max_length=100, blank=True)
    country = models.CharField(_('ülke'), max_length=100, blank=True)
    postal_code = models.CharField(_('posta kodu'), max_length=20, blank=True)
    birth_date = models.DateField(_('doğum tarihi'), null=True, blank=True)
    GENDER_CHOICES = [
        ('M', _('Erkek')),
        ('F', _('Kadın')),
        ('O', _('Diğer')),
    ]
    gender = models.CharField(_('cinsiyet'), max_length=1, choices=GENDER_CHOICES, blank=True)
    avatar = models.ImageField(_('profil resmi'), upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(_('biyografi'), blank=True)
    website = models.URLField(_('web sitesi'), blank=True)
    created_at = models.DateTimeField(_('oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('güncellenme tarihi'), auto_now=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=100, blank=True)
    last_device_id = models.CharField(max_length=100, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    fcm_token = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _('kullanıcı profili')
        verbose_name_plural = _('kullanıcı profilleri')

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'profile_{self.user.id}')

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    LANGUAGE_CHOICES = [
        ('tr', _('Türkçe')),
        ('en', _('İngilizce')),
    ]
    language = models.CharField(_('dil'), max_length=2, choices=LANGUAGE_CHOICES, default='tr')
    TIMEZONE_CHOICES = [
        ('Europe/Istanbul', _('İstanbul')),
        ('UTC', _('UTC')),
    ]
    timezone = models.CharField(_('saat dilimi'), max_length=50, choices=TIMEZONE_CHOICES, default='Europe/Istanbul')
    THEME_CHOICES = [
        ('light', _('Açık')),
        ('dark', _('Koyu')),
        ('system', _('Sistem')),
    ]
    theme = models.CharField(_('tema'), max_length=10, choices=THEME_CHOICES, default='light')
    notifications_enabled = models.BooleanField(_('bildirimler aktif'), default=True)
    email_notifications = models.BooleanField(_('e-posta bildirimleri'), default=True)
    push_notifications = models.BooleanField(_('anlık bildirimler'), default=True)
    created_at = models.DateTimeField(_('oluşturulma tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('güncellenme tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('kullanıcı tercihi')
        verbose_name_plural = _('kullanıcı tercihleri')

    def __str__(self):
        return f"{self.user.get_full_name()}'s Preferences"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'preferences_{self.user.id}')

class UserActivity(models.Model):
    """Kullanıcı aktivite modeli."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(_('Aksiyon'), max_length=100)
    ip_address = models.GenericIPAddressField(_('IP Adresi'))
    user_agent = models.TextField(_('Tarayıcı Bilgisi'))
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Kullanıcı Aktivitesi')
        verbose_name_plural = _('Kullanıcı Aktiviteleri')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.action}"

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(_('başlık'), max_length=200)
    message = models.TextField(_('mesaj'))
    TYPE_CHOICES = [
        ('info', _('Bilgi')),
        ('success', _('Başarılı')),
        ('warning', _('Uyarı')),
        ('error', _('Hata')),
    ]
    type = models.CharField(_('tip'), max_length=10, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(_('okundu'), default=False)
    created_at = models.DateTimeField(_('oluşturulma tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('kullanıcı bildirimi')
        verbose_name_plural = _('kullanıcı bildirimleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'notifications_{self.user.id}')

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(_('oturum anahtarı'), max_length=40)
    ip_address = models.GenericIPAddressField(_('IP adresi'), null=True, blank=True)
    user_agent = models.TextField(_('tarayıcı bilgisi'), blank=True)
    last_activity = models.DateTimeField(_('son aktivite'), auto_now=True)
    created_at = models.DateTimeField(_('oluşturulma tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('kullanıcı oturumu')
        verbose_name_plural = _('kullanıcı oturumları')
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.session_key}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'sessions_{self.user.id}')

class UserSettings(models.Model):
    """Kullanıcı ayarları modeli."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    email_notifications = models.BooleanField(_('E-posta Bildirimleri'), default=True)
    push_notifications = models.BooleanField(_('Push Bildirimleri'), default=True)
    dark_mode = models.BooleanField(_('Karanlık Mod'), default=False)
    newsletter_subscription = models.BooleanField(_('Bülten Aboneliği'), default=False)
    
    class Meta:
        verbose_name = _('Kullanıcı Ayarı')
        verbose_name_plural = _('Kullanıcı Ayarları')
    
    def __str__(self):
        return f"{self.user.username} Ayarları" 