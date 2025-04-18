from django.db import models
from django.conf import settings

class Company(models.Model):
    """Şirket modeli"""
    name = models.CharField(max_length=200, verbose_name='Şirket Adı')
    tax_number = models.CharField(max_length=20, unique=True, verbose_name='Vergi Numarası')
    tax_office = models.CharField(max_length=100, verbose_name='Vergi Dairesi')
    address = models.TextField(verbose_name='Adres')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(verbose_name='E-posta')
    website = models.URLField(blank=True, verbose_name='Web Sitesi')
    logo = models.ImageField(upload_to='company_logos/', blank=True, verbose_name='Logo')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Şirket'
        verbose_name_plural = 'Şirketler'
        ordering = ['name']

    def __str__(self):
        return self.name

class Department(models.Model):
    """Departman modeli"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments', verbose_name='Şirket')
    name = models.CharField(max_length=100, verbose_name='Departman Adı')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_managed_departments', verbose_name='Yönetici')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Departman'
        verbose_name_plural = 'Departmanlar'
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"

class Employee(models.Model):
    """Çalışan modeli"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Kullanıcı')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees', verbose_name='Şirket')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees', verbose_name='Departman')
    position = models.CharField(max_length=100, verbose_name='Pozisyon')
    hire_date = models.DateField(verbose_name='İşe Başlama Tarihi')
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Maaş')
    notes = models.TextField(blank=True, verbose_name='Notlar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Çalışan'
        verbose_name_plural = 'Çalışanlar'
        ordering = ['company', 'department', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name}"
