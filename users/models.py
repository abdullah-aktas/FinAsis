from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Özel kullanıcı yönetici sınıfı"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Normal kullanıcı oluştur"""
        if not email:
            raise ValueError(_('E-posta adresi zorunludur'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Süper kullanıcı oluştur"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Süper kullanıcı için is_staff=True olmalıdır'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Süper kullanıcı için is_superuser=True olmalıdır'))
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Özelleştirilmiş kullanıcı modeli"""
    
    email = models.EmailField(_('e-posta adresi'), unique=True)
    username = models.CharField(_('kullanıcı adı'), max_length=150, unique=True)
    first_name = models.CharField(_('adı'), max_length=150)
    last_name = models.CharField(_('soyadı'), max_length=150)
    date_joined = models.DateTimeField(_('kayıt tarihi'), auto_now_add=True)
    is_active = models.BooleanField(_('aktif'), default=True)
    is_staff = models.BooleanField(_('personel durumu'), default=False)
    phone_number = models.CharField(_('telefon numarası'), max_length=15, blank=True, null=True)
    profile_image = models.ImageField(_('profil resmi'), upload_to='profile_images/', blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('kullanıcı')
        verbose_name_plural = _('kullanıcılar')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name

class UserProfile(models.Model):
    """Kullanıcı profil bilgileri"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('biyografi'), blank=True, null=True)
    birth_date = models.DateField(_('doğum tarihi'), blank=True, null=True)
    address = models.TextField(_('adres'), blank=True, null=True)
    company_name = models.CharField(_('şirket adı'), max_length=255, blank=True, null=True)
    job_title = models.CharField(_('iş unvanı'), max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = _('kullanıcı profili')
        verbose_name_plural = _('kullanıcı profilleri')
    
    def __str__(self):
        return f"{self.user.get_full_name()} Profili" 