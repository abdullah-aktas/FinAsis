from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()

class VirtualCompany(models.Model):
    """Sanal şirket modeli"""
    name = models.CharField(_('Şirket Adı'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    logo = models.ImageField(_('Logo'), upload_to='virtual_companies/logos/', blank=True, null=True)
    industry = models.CharField(_('Sektör'), max_length=100)
    founded_date = models.DateField(_('Kuruluş Tarihi'))
    website = models.URLField(_('Website'), blank=True)
    email = models.EmailField(_('E-posta'))
    phone = models.CharField(_('Telefon'), max_length=20)
    address = models.TextField(_('Adres'))
    tax_number = models.CharField(_('Vergi Numarası'), max_length=20)
    tax_office = models.CharField(_('Vergi Dairesi'), max_length=100)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_companies')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Sanal Şirket')
        verbose_name_plural = _('Sanal Şirketler')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Department(models.Model):
    """Departman modeli"""
    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(_('Departman Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_departments')
    budget = models.DecimalField(_('Bütçe'), max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Departman')
        verbose_name_plural = _('Departmanlar')
        ordering = ['name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"

class Employee(models.Model):
    """Çalışan modeli"""
    ROLE_CHOICES = [
        ('manager', _('Yönetici')),
        ('employee', _('Çalışan')),
        ('intern', _('Stajyer')),
    ]

    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='employees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_roles')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    role = models.CharField(_('Rol'), max_length=20, choices=ROLE_CHOICES)
    position = models.CharField(_('Pozisyon'), max_length=100)
    salary = models.DecimalField(_('Maaş'), max_digits=10, decimal_places=2)
    hire_date = models.DateField(_('İşe Başlama Tarihi'))
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Çalışan')
        verbose_name_plural = _('Çalışanlar')
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"

class Project(models.Model):
    """Proje modeli"""
    STATUS_CHOICES = [
        ('planned', _('Planlandı')),
        ('in_progress', _('Devam Ediyor')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    ]

    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(_('Proje Adı'), max_length=255)
    description = models.TextField(_('Açıklama'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='projects')
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    budget = models.DecimalField(_('Bütçe'), max_digits=15, decimal_places=2)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='planned')
    progress = models.IntegerField(_('İlerleme'), validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Proje')
        verbose_name_plural = _('Projeler')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.name} - {self.name}"

class Task(models.Model):
    """Görev modeli"""
    PRIORITY_CHOICES = [
        ('low', _('Düşük')),
        ('medium', _('Orta')),
        ('high', _('Yüksek')),
        ('urgent', _('Acil')),
    ]

    STATUS_CHOICES = [
        ('todo', _('Yapılacak')),
        ('in_progress', _('Devam Ediyor')),
        ('review', _('İncelemede')),
        ('completed', _('Tamamlandı')),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'))
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    priority = models.CharField(_('Öncelik'), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='todo')
    start_date = models.DateField(_('Başlangıç Tarihi'))
    due_date = models.DateField(_('Bitiş Tarihi'))
    completed_date = models.DateField(_('Tamamlanma Tarihi'), null=True, blank=True)
    progress = models.IntegerField(_('İlerleme'), validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Görev')
        verbose_name_plural = _('Görevler')
        ordering = ['priority', 'due_date']

    def __str__(self):
        return f"{self.project.name} - {self.title}"

class Budget(models.Model):
    """Bütçe modeli"""
    TYPE_CHOICES = [
        ('income', _('Gelir')),
        ('expense', _('Gider')),
    ]

    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='budgets')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='budgets')
    type = models.CharField(_('Tür'), max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(_('Miktar'), max_digits=15, decimal_places=2)
    description = models.TextField(_('Açıklama'))
    date = models.DateField(_('Tarih'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_budgets')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Bütçe')
        verbose_name_plural = _('Bütçeler')
        ordering = ['-date']

    def __str__(self):
        return f"{self.company.name} - {self.get_type_display()} - {self.amount}"

class Report(models.Model):
    """Rapor modeli"""
    TYPE_CHOICES = [
        ('financial', _('Finansal')),
        ('operational', _('Operasyonel')),
        ('project', _('Proje')),
        ('performance', _('Performans')),
    ]

    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(_('Başlık'), max_length=255)
    type = models.CharField(_('Tür'), max_length=20, choices=TYPE_CHOICES)
    content = models.TextField(_('İçerik'))
    file = models.FileField(_('Dosya'), upload_to='virtual_companies/reports/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Rapor')
        verbose_name_plural = _('Raporlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.name} - {self.title}"

# Stok Yönetimi Modelleri
class Product(models.Model):
    name = models.CharField(_('Ürün Adı'), max_length=200)
    code = models.CharField(_('Ürün Kodu'), max_length=50, unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(_('Stok Miktarı'), default=0)
    min_stock_level = models.IntegerField(_('Minimum Stok Seviyesi'), default=10)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Ürün')
        verbose_name_plural = _('Ürünler')

    def __str__(self):
        return f"{self.name} ({self.code})"

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', _('Giriş')),
        ('out', _('Çıkış')),
        ('transfer', _('Transfer')),
        ('adjustment', _('Düzeltme')),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(_('Hareket Tipi'), max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(_('Miktar'))
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2)
    reference = models.CharField(_('Referans'), max_length=100)
    notes = models.TextField(_('Notlar'), blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Stok Hareketi')
        verbose_name_plural = _('Stok Hareketleri')

# Üretim Yönetimi Modelleri
class ProductionOrder(models.Model):
    STATUS_CHOICES = (
        ('planned', _('Planlandı')),
        ('in_progress', _('Üretimde')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    )

    order_number = models.CharField(_('Üretim Emri No'), max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='production_orders')
    quantity = models.IntegerField(_('Üretim Miktarı'))
    planned_start_date = models.DateField(_('Planlanan Başlangıç'))
    planned_end_date = models.DateField(_('Planlanan Bitiş'))
    actual_start_date = models.DateField(_('Gerçek Başlangıç'), null=True, blank=True)
    actual_end_date = models.DateField(_('Gerçek Bitiş'), null=True, blank=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(_('Notlar'), blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Üretim Emri')
        verbose_name_plural = _('Üretim Emirleri')

class BillOfMaterials(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_masters')
    component = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom_components')
    quantity = models.DecimalField(_('Miktar'), max_digits=10, decimal_places=3)
    unit = models.CharField(_('Birim'), max_length=20)
    notes = models.TextField(_('Notlar'), blank=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Ürün Ağacı')
        verbose_name_plural = _('Ürün Ağaçları')
        unique_together = ('product', 'component')

class QualityControl(models.Model):
    RESULT_CHOICES = (
        ('passed', _('Geçti')),
        ('failed', _('Başarısız')),
        ('conditional', _('Şartlı Kabul')),
    )

    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='quality_controls')
    inspection_date = models.DateTimeField(_('Kontrol Tarihi'))
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    result = models.CharField(_('Sonuç'), max_length=20, choices=RESULT_CHOICES)
    notes = models.TextField(_('Notlar'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Kalite Kontrol')
        verbose_name_plural = _('Kalite Kontroller') 