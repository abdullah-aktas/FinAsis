from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import pyotp

class User(AbstractUser):
    """Özel kullanıcı modeli"""
    
    ROLE_CHOICES = [
        ('admin', 'Yönetici'),
        ('user', 'Kullanıcı'),
        ('manager', 'Yönetici'),
        ('analyst', 'Analist'),
    ]
    
    role = models.CharField(
        _('Rol'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    password_expiry_date = models.DateTimeField(null=True, blank=True)
    last_password_change = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
        ]
        
    def has_role(self, role):
        """Kullanıcının belirli bir role sahip olup olmadığını kontrol eder."""
        return self.role == role
    
    def has_perm_role(self, perm_roles):
        """Kullanıcının izin verilen rollerden birine sahip olup olmadığını kontrol eder."""
        if self.is_superuser:
            return True
        if isinstance(perm_roles, str):
            return self.role == perm_roles
        return self.role in perm_roles

    def generate_two_factor_secret(self):
        """İki faktörlü kimlik doğrulama için yeni bir secret oluşturur."""
        self.two_factor_secret = pyotp.random_base32()
        self.save()
        return self.two_factor_secret

    def verify_two_factor_code(self, code):
        """İki faktörlü kimlik doğrulama kodunu doğrular."""
        if not self.two_factor_enabled or not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code)

    def is_password_expired(self):
        """Şifrenin süresi dolmuş mu kontrol eder."""
        if not self.password_expiry_date:
            return False
        return timezone.now() > self.password_expiry_date

    def set_password(self, raw_password):
        """Şifre değiştirildiğinde son değişiklik tarihini günceller."""
        super().set_password(raw_password)
        self.last_password_change = timezone.now()
        # Şifre süresini 90 gün olarak ayarla
        self.password_expiry_date = timezone.now() + timezone.timedelta(days=90) 