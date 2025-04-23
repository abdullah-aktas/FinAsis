from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import uuid

class Employee(models.Model):
    GENDER_CHOICES = (
        ('M', _('Erkek')),
        ('F', _('Kadın')),
        ('O', _('Diğer')),
    )
    
    MARITAL_STATUS_CHOICES = (
        ('S', _('Bekar')),
        ('M', _('Evli')),
        ('D', _('Boşanmış')),
        ('W', _('Dul')),
    )

    EMPLOYMENT_STATUS_CHOICES = (
        ('F', _('Tam Zamanlı')),
        ('P', _('Yarı Zamanlı')),
        ('C', _('Sözleşmeli')),
        ('I', _('Stajyer')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_('Ad'), max_length=100)
    last_name = models.CharField(_('Soyad'), max_length=100)
    identity_number = models.CharField(_('TC Kimlik No'), max_length=11, unique=True)
    birth_date = models.DateField(_('Doğum Tarihi'))
    gender = models.CharField(_('Cinsiyet'), max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(_('Medeni Hal'), max_length=1, choices=MARITAL_STATUS_CHOICES)
    address = models.TextField(_('Adres'))
    phone = models.CharField(_('Telefon'), max_length=20)
    email = models.EmailField(_('E-posta'))
    emergency_contact = models.CharField(_('Acil Durum İletişim'), max_length=100)
    emergency_phone = models.CharField(_('Acil Durum Telefon'), max_length=20)
    hire_date = models.DateField(_('İşe Başlama Tarihi'))
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, verbose_name=_('Departman'))
    position = models.CharField(_('Pozisyon'), max_length=100)
    employment_status = models.CharField(_('Çalışma Durumu'), max_length=1, choices=EMPLOYMENT_STATUS_CHOICES)
    bank_account = models.CharField(_('Banka Hesabı'), max_length=26, blank=True)
    iban = models.CharField(_('IBAN'), max_length=34, blank=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Çalışan')
        verbose_name_plural = _('Çalışanlar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['identity_number']),
            models.Index(fields=['email']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Departman Adı'), max_length=100)
    code = models.CharField(_('Departman Kodu'), max_length=20, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Üst Departman'))
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_department', verbose_name=_('Departman Müdürü'))
    budget = models.DecimalField(_('Bütçe'), max_digits=15, decimal_places=2, default=0)
    description = models.TextField(_('Açıklama'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Departman')
        verbose_name_plural = _('Departmanlar')
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name

class Salary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Çalışan'))
    base_salary = models.DecimalField(_('Baz Maaş'), max_digits=10, decimal_places=2)
    effective_date = models.DateField(_('Geçerlilik Tarihi'))
    currency = models.CharField(_('Para Birimi'), max_length=3, default='TRY')
    payment_frequency = models.CharField(_('Ödeme Sıklığı'), max_length=20, choices=[
        ('M', _('Aylık')),
        ('B', _('İki Haftalık')),
        ('W', _('Haftalık')),
    ], default='M')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Maaş')
        verbose_name_plural = _('Maaşlar')
        ordering = ['-effective_date']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['effective_date']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.base_salary} {self.currency}"

class Payroll(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('P', _('Beklemede')),
        ('A', _('Onaylandı')),
        ('R', _('Reddedildi')),
        ('C', _('Ödendi')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Çalışan'))
    period_start = models.DateField(_('Dönem Başlangıcı'))
    period_end = models.DateField(_('Dönem Bitişi'))
    base_salary = models.DecimalField(_('Baz Maaş'), max_digits=10, decimal_places=2)
    overtime_hours = models.DecimalField(_('Fazla Mesai Saati'), max_digits=5, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(_('Fazla Mesai Ücreti'), max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(_('Bonus'), max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(_('Kesintiler'), max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(_('Net Maaş'), max_digits=10, decimal_places=2)
    gross_salary = models.DecimalField(_('Brüt Maaş'), max_digits=10, decimal_places=2)
    payment_date = models.DateField(_('Ödeme Tarihi'))
    payment_status = models.CharField(_('Ödeme Durumu'), max_length=1, choices=PAYMENT_STATUS_CHOICES, default='P')
    payment_reference = models.CharField(_('Ödeme Referansı'), max_length=50, blank=True)
    notes = models.TextField(_('Notlar'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Bordro')
        verbose_name_plural = _('Bordrolar')
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['payment_date']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.period_start} to {self.period_end}"

class Leave(models.Model):
    LEAVE_TYPES = (
        ('ANNUAL', _('Yıllık İzin')),
        ('SICK', _('Hastalık İzni')),
        ('MATERNITY', _('Doğum İzni')),
        ('PATERNITY', _('Babalık İzni')),
        ('UNPAID', _('Ücretsiz İzin')),
        ('COMPASSIONATE', _('Vefat İzni')),
        ('EDUCATION', _('Eğitim İzni')),
    )

    LEAVE_STATUS_CHOICES = (
        ('P', _('Beklemede')),
        ('A', _('Onaylandı')),
        ('R', _('Reddedildi')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('Çalışan'))
    leave_type = models.CharField(_('İzin Tipi'), max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    total_days = models.IntegerField(_('Toplam Gün'))
    reason = models.TextField(_('Sebep'), blank=True, null=True)
    status = models.CharField(_('Durum'), max_length=1, choices=LEAVE_STATUS_CHOICES, default='P')
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name=_('Onaylayan'))
    approved_at = models.DateTimeField(_('Onay Tarihi'), null=True, blank=True)
    rejection_reason = models.TextField(_('Red Sebebi'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('İzin')
        verbose_name_plural = _('İzinler')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['leave_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})" 