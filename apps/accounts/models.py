from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Genişletilmiş kullanıcı modeli.
    Kullanıcı rollerini ve sanal şirket kullanıcısı olup olmadığını belirler.
    """
    ROLE_CHOICES = [
        ('business', 'İşletme'),
        ('student', 'Öğrenci'),
        ('teacher', 'Öğretmen'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', verbose_name='Kullanıcı Rolü')
    is_virtual_company_user = models.BooleanField(default=False, verbose_name='Sanal Şirket Kullanıcısı')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar' 