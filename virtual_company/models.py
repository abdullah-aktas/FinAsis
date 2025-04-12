from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils.timezone import now, timedelta
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import json

User = get_user_model()

class VirtualCompany(models.Model):
    """Sanal şirket modeli"""
    name = models.CharField(_('Şirket Adı'), max_length=255, default='Yeni Şirket')
    description = models.TextField(_('Açıklama'), blank=True, default='')
    logo = models.ImageField(_('Logo'), upload_to='virtual_companies/logos/', blank=True, null=True)
    industry = models.CharField(_('Sektör'), max_length=100, default='Teknoloji')
    founded_date = models.DateField(_('Kuruluş Tarihi'), default=timezone.now)
    website = models.URLField(_('Website'), blank=True, default='')
    email = models.EmailField(_('E-posta'), default='info@finasis.com')
    phone = models.CharField(_('Telefon'), max_length=20, default='5555555555')
    address = models.TextField(_('Adres'), default='Varsayılan Adres')
    tax_number = models.CharField(_('Vergi Numarası'), max_length=20, default='1234567890')
    tax_office = models.CharField(_('Vergi Dairesi'), max_length=100, default='Merkez')
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_companies')
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
    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='virtual_departments', verbose_name='Şirket')
    name = models.CharField(max_length=100, verbose_name='Departman Adı')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='virtual_managed_departments', verbose_name='Yönetici')
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Bütçe')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Departman'
        verbose_name_plural = 'Departmanlar'
        ordering = ['company', 'name']

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

class ModuleSetting(models.Model):
    """Modül ayarları modeli"""
    module = models.CharField(_('Modül'), max_length=100)
    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, 
                              related_name='module_settings', null=True, blank=True)
    key = models.CharField(_('Anahtar'), max_length=100)
    value = models.TextField(_('Değer'))
    is_global = models.BooleanField(_('Global'), default=False, 
                                 help_text=_('Global ayarlar tüm şirketler için geçerlidir.'))
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Modül Ayarı')
        verbose_name_plural = _('Modül Ayarları')
        unique_together = ('module', 'company', 'key')
        ordering = ['module', 'key']

    def __str__(self):
        company_name = self.company.name if self.company else 'Global'
        return f"{self.module} - {self.key} ({company_name})"

class DailyTask(models.Model):
    CATEGORY_CHOICES = (
        ('FINANS', 'Finans'),
        ('MUHASEBE', 'Muhasebe'),
        ('EKONOMI', 'Ekonomi'),
        ('YATIRIM', 'Yatırım'),
        ('TEKNOLOJI', 'Teknoloji'),
        ('DIGER', 'Diğer'),
    )
    
    DIFFICULTY_CHOICES = (
        ('KOLAY', 'Kolay'),
        ('ORTA', 'Orta'),
        ('ZOR', 'Zor'),
    )
    
    title = models.CharField(max_length=255, verbose_name='Başlık')
    description = models.TextField(verbose_name='Açıklama')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Kategori')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name='Zorluk')
    xp_reward = models.PositiveIntegerField(verbose_name='XP Ödülü')
    money_reward = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Para Ödülü')
    knowledge_reward = models.JSONField(default=dict, blank=True, verbose_name='Bilgi Ödülü')
    steps = models.JSONField(default=list, verbose_name='Adımlar')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Günlük Görev'
        verbose_name_plural = 'Günlük Görevler'

class UserDailyTask(models.Model):
    STATUS_CHOICES = (
        ('BASLAMADI', 'Başlamadı'),
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('TAMAMLANDI', 'Tamamlandı'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='virtual_daily_tasks', verbose_name='Kullanıcı')
    task = models.ForeignKey(DailyTask, on_delete=models.CASCADE, related_name='virtual_user_tasks', verbose_name='Görev')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BASLAMADI', verbose_name='Durum')
    completed_steps = models.JSONField(default=list, verbose_name='Tamamlanan Adımlar')
    notes = models.TextField(blank=True, null=True, verbose_name='Notlar')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Başlama Tarihi')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tamamlanma Tarihi')
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title}"
    
    def start_task(self):
        if self.status == 'BASLAMADI':
            self.status = 'DEVAM_EDIYOR'
            self.started_at = timezone.now()
            self.save()
    
    def complete_step(self, step_index):
        completed_steps = self.completed_steps or []
        
        if str(step_index) not in completed_steps:
            completed_steps.append(str(step_index))
            self.completed_steps = completed_steps
            self.save()
            
            # Tüm adımlar tamamlandıysa görevi bitir
            task_steps = self.task.steps
            if len(completed_steps) >= len(task_steps):
                self.complete_task()
                
            return True
        return False
    
    def complete_task(self):
        if self.status != 'TAMAMLANDI':
            self.status = 'TAMAMLANDI'
            self.completed_at = timezone.now()
            self.save()
            return True
        return False
    
    def is_step_completed(self, step_index):
        completed_steps = self.completed_steps or []
        return str(step_index) in completed_steps
    
    class Meta:
        verbose_name = 'Kullanıcı Günlük Görevi'
        verbose_name_plural = 'Kullanıcı Günlük Görevleri'
        unique_together = ('user', 'task')

class KnowledgeBase(models.Model):
    """Bilgi Bankası modeli"""
    CATEGORY_CHOICES = [
        ('finance', _('Finans')),
        ('accounting', _('Muhasebe')),
        ('management', _('Yönetim')),
        ('operations', _('Operasyonlar')),
        ('hr', _('İnsan Kaynakları')),
        ('other', _('Diğer')),
    ]

    title = models.CharField(_('Başlık'), max_length=255)
    content = models.TextField(_('İçerik'))
    category = models.CharField(_('Kategori'), max_length=20, choices=CATEGORY_CHOICES)
    tags = models.CharField(_('Etiketler'), max_length=255, blank=True)
    file = models.FileField(_('Dosya'), upload_to='virtual_companies/knowledge_base/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_knowledge')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Bilgi Bankası')
        verbose_name_plural = _('Bilgi Bankası')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class KnowledgeBaseRelatedItem(models.Model):
    """Bilgi Bankası İlişkili Öğe modeli"""
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='related_items')
    title = models.CharField(_('Başlık'), max_length=255)
    url = models.URLField(_('URL'), blank=True)
    description = models.TextField(_('Açıklama'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('İlişkili Öğe')
        verbose_name_plural = _('İlişkili Öğeler')
        ordering = ['title']

    def __str__(self):
        return self.title 