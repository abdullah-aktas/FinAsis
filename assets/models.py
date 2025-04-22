from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.conf import settings

class AssetCategory(models.Model):
    name = models.CharField(_('Kategori Adı'), max_length=100)
    code = models.CharField(_('Kategori Kodu'), max_length=20, unique=True)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    depreciation_period = models.IntegerField(_('Amortisman Süresi (ay)'), help_text="Amortisman süresi (ay)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Varlık Kategorisi')
        verbose_name_plural = _('Varlık Kategorileri')
        ordering = ['name']

    def __str__(self):
        return self.name

class Asset(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', _('Aktif')),
        ('MAINTENANCE', _('Bakımda')),
        ('RETIRED', _('Emekli')),
        ('SOLD', _('Satıldı')),
        ('RENTED', _('Kirada')),
    )

    name = models.CharField(_('Varlık Adı'), max_length=200)
    code = models.CharField(_('Varlık Kodu'), max_length=50, unique=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, verbose_name=_('Kategori'))
    purchase_date = models.DateField(_('Satın Alma Tarihi'))
    purchase_cost = models.DecimalField(_('Satın Alma Maliyeti'), max_digits=12, decimal_places=2)
    current_value = models.DecimalField(_('Güncel Değer'), max_digits=12, decimal_places=2)
    salvage_value = models.DecimalField(_('Hurda Değeri'), max_digits=12, decimal_places=2)
    location = models.CharField(_('Konum'), max_length=200)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    serial_number = models.CharField(_('Seri Numarası'), max_length=100, blank=True, null=True)
    warranty_end_date = models.DateField(_('Garanti Bitiş Tarihi'), null=True, blank=True)
    qr_code = models.CharField(_('QR Kod'), max_length=100, unique=True, blank=True, null=True)
    barcode = models.CharField(_('Barkod'), max_length=100, unique=True, blank=True, null=True)
    image = models.ImageField(_('Resim'), upload_to='assets/images/', null=True, blank=True,
                            validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, blank=True, verbose_name=_('Atanan Kişi'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Varlık')
        verbose_name_plural = _('Varlıklar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

class Depreciation(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_('Varlık'))
    period_start = models.DateField(_('Dönem Başlangıcı'))
    period_end = models.DateField(_('Dönem Bitişi'))
    depreciation_amount = models.DecimalField(_('Amortisman Tutarı'), max_digits=12, decimal_places=2)
    accumulated_depreciation = models.DecimalField(_('Birikmiş Amortisman'), max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Amortisman')
        verbose_name_plural = _('Amortismanlar')
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.asset.name} - {self.period_start} to {self.period_end}"

class Maintenance(models.Model):
    MAINTENANCE_TYPES = (
        ('PREVENTIVE', _('Önleyici Bakım')),
        ('CORRECTIVE', _('Düzeltici Bakım')),
        ('INSPECTION', _('Kontrol')),
    )

    STATUS_CHOICES = (
        ('PENDING', _('Beklemede')),
        ('IN_PROGRESS', _('Devam Ediyor')),
        ('COMPLETED', _('Tamamlandı')),
        ('CANCELLED', _('İptal Edildi')),
    )

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_('Varlık'))
    maintenance_type = models.CharField(_('Bakım Türü'), max_length=20, choices=MAINTENANCE_TYPES)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(_('Açıklama'))
    cost = models.DecimalField(_('Maliyet'), max_digits=12, decimal_places=2)
    maintenance_date = models.DateField(_('Bakım Tarihi'))
    next_maintenance_date = models.DateField(_('Sonraki Bakım Tarihi'), null=True, blank=True)
    performed_by = models.CharField(_('Bakımı Yapan'), max_length=200)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Bakım')
        verbose_name_plural = _('Bakımlar')
        ordering = ['-maintenance_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['maintenance_type']),
        ]

    def __str__(self):
        return f"{self.asset.name} - {self.maintenance_type} ({self.maintenance_date})"

class AssetTransfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_('Varlık'))
    from_location = models.CharField(_('Kaynak Konum'), max_length=200)
    to_location = models.CharField(_('Hedef Konum'), max_length=200)
    transfer_date = models.DateField(_('Transfer Tarihi'))
    reason = models.TextField(_('Neden'))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, verbose_name=_('Onaylayan'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Varlık Transferi')
        verbose_name_plural = _('Varlık Transferleri')
        ordering = ['-transfer_date']

    def __str__(self):
        return f"{self.asset.name} - {self.from_location} -> {self.to_location}"

class AssetDisposal(models.Model):
    DISPOSAL_TYPES = (
        ('SALE', _('Satış')),
        ('SCRAP', _('Hurdaya Ayırma')),
        ('DONATION', _('Bağış')),
        ('OTHER', _('Diğer')),
    )

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_('Varlık'))
    disposal_type = models.CharField(_('İmha Türü'), max_length=20, choices=DISPOSAL_TYPES)
    disposal_date = models.DateField(_('İmha Tarihi'))
    disposal_value = models.DecimalField(_('İmha Değeri'), max_digits=12, decimal_places=2)
    reason = models.TextField(_('Neden'))
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, verbose_name=_('Onaylayan'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Varlık İmhası')
        verbose_name_plural = _('Varlık İmhaları')
        ordering = ['-disposal_date']

    def __str__(self):
        return f"{self.asset.name} - {self.disposal_type} ({self.disposal_date})"

class AssetRental(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', _('Aktif')),
        ('COMPLETED', _('Tamamlandı')),
        ('CANCELLED', _('İptal Edildi')),
    )

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_('Varlık'))
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             verbose_name=_('Kiracı'))
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    rental_fee = models.DecimalField(_('Kira Ücreti'), max_digits=12, decimal_places=2)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Varlık Kiralama')
        verbose_name_plural = _('Varlık Kiralamaları')
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['renter']),
        ]

    def __str__(self):
        return f"{self.asset.name} - {self.renter} ({self.start_date} - {self.end_date})"
