# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Bank(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    branch_code = models.CharField(max_length=20, blank=True, null=True)
    branch_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Check(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Beklemede'),
        ('DEPOSITED', 'Tahsil Edildi'),
        ('BOUNCED', 'Karşılıksız'),
        ('CANCELLED', 'İptal Edildi'),
    )

    TYPE_CHOICES = (
        ('RECEIVABLE', 'Alacak'),
        ('PAYABLE', 'Borç'),
    )

    check_number = models.CharField(max_length=50)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    check_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    drawer_name = models.CharField(max_length=200)
    drawer_tax_number = models.CharField(max_length=20, blank=True, null=True)
    payee_name = models.CharField(max_length=200)
    payee_tax_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.check_number} - {self.amount} TL"

class PromissoryNote(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Beklemede'),
        ('PAID', 'Ödendi'),
        ('PROTESTED', 'Protestolu'),
        ('CANCELLED', 'İptal Edildi'),
    )

    TYPE_CHOICES = (
        ('RECEIVABLE', 'Alacak'),
        ('PAYABLE', 'Borç'),
    )

    note_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    note_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    drawer_name = models.CharField(max_length=200)
    drawer_tax_number = models.CharField(max_length=20, blank=True, null=True)
    payee_name = models.CharField(max_length=200)
    payee_tax_number = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.note_number} - {self.amount} TL"

class CheckTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Tahsilat'),
        ('PAYMENT', 'Ödeme'),
        ('BOUNCE', 'Karşılıksız'),
        ('CANCEL', 'İptal'),
    )

    check = models.ForeignKey(Check, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.check.check_number} - {self.transaction_type}"

class PromissoryNoteTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('PAYMENT', 'Ödeme'),
        ('PROTEST', 'Protesto'),
        ('CANCEL', 'İptal'),
    )

    promissory_note = models.ForeignKey(PromissoryNote, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.promissory_note.note_number} - {self.transaction_type}"

class CheckCategory(models.Model):
    name = models.CharField(_('Kategori Adı'), max_length=100, unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    priority = models.IntegerField(_('Öncelik'), default=0)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Kontrol Kategorisi')
        verbose_name_plural = _('Kontrol Kategorileri')
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

class CheckType(models.Model):
    name = models.CharField(_('Kontrol Tipi'), max_length=100, unique=True)
    code = models.CharField(_('Kod'), max_length=50, unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    category = models.ForeignKey(CheckCategory, on_delete=models.PROTECT, verbose_name=_('Kategori'))
    severity = models.CharField(_('Önem Seviyesi'), max_length=20, choices=[
        ('critical', _('Kritik')),
        ('high', _('Yüksek')),
        ('medium', _('Orta')),
        ('low', _('Düşük')),
    ])
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Kontrol Tipi')
        verbose_name_plural = _('Kontrol Tipleri')
        ordering = ['category', 'severity', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['severity']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"

class CheckRule(models.Model):
    check_type = models.ForeignKey(CheckType, on_delete=models.CASCADE, verbose_name=_('Kontrol Tipi'))
    name = models.CharField(_('Kural Adı'), max_length=100)
    description = models.TextField(_('Açıklama'), blank=True)
    condition = models.TextField(_('Koşul'))
    threshold = models.FloatField(_('Eşik Değeri'), null=True, blank=True)
    weight = models.FloatField(_('Ağırlık'), default=1.0, validators=[
        MinValueValidator(0.0),
        MaxValueValidator(1.0)
    ])
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Kontrol Kuralı')
        verbose_name_plural = _('Kontrol Kuralları')
        ordering = ['check_type', 'weight']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['weight']),
        ]

    def __str__(self):
        return f"{self.check_type.name} - {self.name}"

class CheckResult(models.Model):
    check_type = models.ForeignKey(CheckType, on_delete=models.CASCADE, verbose_name=_('Kontrol Tipi'))
    status = models.CharField(_('Durum'), max_length=20, choices=[
        ('passed', _('Başarılı')),
        ('failed', _('Başarısız')),
        ('warning', _('Uyarı')),
        ('error', _('Hata')),
    ])
    score = models.FloatField(_('Puan'), null=True, blank=True)
    details = models.JSONField(_('Detaylar'), default=dict)
    started_at = models.DateTimeField(_('Başlangıç Zamanı'))
    completed_at = models.DateTimeField(_('Bitiş Zamanı'))
    duration = models.DurationField(_('Süre'), null=True, blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Kontrol Sonucu')
        verbose_name_plural = _('Kontrol Sonuçları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.check_type.name} - {self.get_status_display()}"

class CheckSchedule(models.Model):
    check_type = models.ForeignKey(CheckType, on_delete=models.CASCADE, verbose_name=_('Kontrol Tipi'))
    schedule = models.CharField(_('Zamanlama'), max_length=100)
    is_active = models.BooleanField(_('Aktif'), default=True)
    last_run = models.DateTimeField(_('Son Çalıştırma'), null=True, blank=True)
    next_run = models.DateTimeField(_('Sonraki Çalıştırma'), null=True, blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Kontrol Zamanlaması')
        verbose_name_plural = _('Kontrol Zamanlamaları')
        ordering = ['next_run']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['next_run']),
        ]

    def __str__(self):
        return f"{self.check_type.name} - {self.schedule}"
