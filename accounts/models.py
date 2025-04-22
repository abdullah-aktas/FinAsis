from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
import pyotp

class User(AbstractUser):
    """
    Genişletilmiş kullanıcı modeli.
    Kullanıcı rollerini ve sanal şirket kullanıcısı olup olmadığını belirler.
    """
    ROLE_CHOICES = [
        # Yönetim rolleri
        ('admin', 'Yönetici'),
        ('manager', 'Genel Müdür'),
        
        # Departman rolleri
        ('finance_manager', 'Finans Sorumlusu'),
        ('accounting', 'Muhasebe Sorumlusu'),
        ('stock_operator', 'Depo Yetkilisi'),
        ('sales', 'Satış Sorumlusu'),
        ('hr', 'İnsan Kaynakları'),
        
        # Diğer roller
        ('business', 'İşletme'),
        ('student', 'Öğrenci'),
        ('teacher', 'Öğretmen'),
        ('guest', 'Misafir'),
    ]
    
    # Temel bilgiler
    email = models.EmailField(unique=True, verbose_name='E-posta')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', verbose_name='Kullanıcı Rolü')
    is_virtual_company_user = models.BooleanField(default=False, verbose_name='Sanal Şirket Kullanıcısı')
    
    # İletişim bilgileri
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name='Telefon',
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Telefon numarası geçerli bir formatta olmalıdır."
            )
        ]
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True, 
        verbose_name='Profil Resmi'
    )
    
    # Güvenlik alanları
    two_factor_enabled = models.BooleanField(default=False, verbose_name='İki Faktörlü Kimlik Doğrulama')
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='Son Giriş IP Adresi')
    failed_login_attempts = models.PositiveIntegerField(default=0, verbose_name='Başarısız Giriş Denemeleri')
    account_locked_until = models.DateTimeField(blank=True, null=True, verbose_name='Hesap Kilitleme Süresi')
    
    # Kullanıcı tercihleri
    language = models.CharField(max_length=10, default='tr', verbose_name='Dil Tercihi')
    theme = models.CharField(max_length=20, default='light', verbose_name='Tema')
    notifications_enabled = models.BooleanField(default=True, verbose_name='Bildirimler')
    
    # Zaman damgaları
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_password_change = models.DateTimeField(default=timezone.now)
    password_expiry_date = models.DateTimeField(blank=True, null=True)

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