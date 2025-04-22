from django.contrib.auth.models import AbstractUser
from django.db import models

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
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', verbose_name='Kullanıcı Rolü')
    is_virtual_company_user = models.BooleanField(default=False, verbose_name='Sanal Şirket Kullanıcısı')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefon')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name='Profil Resmi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='Son Giriş IP Adresi')
    failed_login_attempts = models.PositiveIntegerField(default=0, verbose_name='Başarısız Giriş Denemeleri')
    account_locked_until = models.DateTimeField(blank=True, null=True, verbose_name='Hesap Kilitleme Süresi')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        
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