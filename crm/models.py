# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounting.models import BaseModel, Account
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Lead(models.Model):
    """Potansiyel müşteri/aday modeli"""
    LEAD_STATUS_CHOICES = [
        ('new', 'Yeni'),
        ('contacted', 'İletişime Geçildi'),
        ('qualified', 'Kalifiye'),
        ('proposal', 'Teklif Verildi'),
        ('negotiation', 'Pazarlık Aşamasında'),
        ('won', 'Kazanıldı'),
        ('lost', 'Kaybedildi'),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name='Ad')
    last_name = models.CharField(max_length=100, verbose_name='Soyad')
    email = models.EmailField(verbose_name='E-posta')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    company = models.CharField(max_length=200, blank=True, verbose_name='Şirket')
    position = models.CharField(max_length=100, blank=True, verbose_name='Pozisyon')
    source = models.CharField(max_length=100, blank=True, verbose_name='Kaynak')
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new', verbose_name='Durum')
    notes = models.TextField(blank=True, verbose_name='Notlar')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads', verbose_name='Atanan Kişi')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Aday'
        verbose_name_plural = 'Adaylar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Customer(models.Model):
    """Müşteri modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    company_name = models.CharField(_('Şirket Adı'), max_length=255)
    tax_number = models.CharField(_('Vergi Numarası'), max_length=20, unique=True)
    tax_office = models.CharField(_('Vergi Dairesi'), max_length=100)
    address = models.TextField(_('Adres'))
    phone = models.CharField(_('Telefon'), max_length=20)
    email = models.EmailField(_('E-posta'))
    website = models.URLField(_('Web Sitesi'), blank=True)
    industry = models.CharField(_('Sektör'), max_length=100)
    employee_count = models.IntegerField(_('Çalışan Sayısı'), validators=[MinValueValidator(1)])
    annual_revenue = models.DecimalField(_('Yıllık Gelir'), max_digits=15, decimal_places=2)
    credit_score = models.IntegerField(_('Kredi Skoru'), validators=[MinValueValidator(0), MaxValueValidator(1000)])
    risk_level = models.CharField(_('Risk Seviyesi'), max_length=20, choices=[
        ('LOW', _('Düşük')),
        ('MEDIUM', _('Orta')),
        ('HIGH', _('Yüksek')),
    ])
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Müşteri')
        verbose_name_plural = _('Müşteriler')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['tax_number']),
            models.Index(fields=['email']),
            models.Index(fields=['risk_level']),
        ]

    def __str__(self):
        return f"{self.company_name} ({self.tax_number})"

    def clean(self):
        if self.credit_score < 0 or self.credit_score > 1000:
            raise ValidationError(_('Kredi skoru 0-1000 arasında olmalıdır.'))

    @property
    def total_revenue(self):
        return self.invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')

class Contact(models.Model):
    """İletişim kişisi modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(_('Ad'), max_length=100)
    last_name = models.CharField(_('Soyad'), max_length=100)
    position = models.CharField(_('Pozisyon'), max_length=100)
    department = models.CharField(_('Departman'), max_length=100, null=True, blank=True)
    phone = models.CharField(_('Telefon'), max_length=20)
    mobile = models.CharField(_('Cep Telefonu'), max_length=20)
    email = models.EmailField(_('E-posta'))
    is_primary = models.BooleanField(_('Birincil İletişim'), default=False)
    notes = models.TextField(_('Notlar'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('İletişim Kişisi')
        verbose_name_plural = _('İletişim Kişileri')
        ordering = ['-is_primary', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['email']),
            models.Index(fields=['is_primary']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

class Opportunity(models.Model):
    """Fırsat modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'))
    amount = models.DecimalField(_('Tutar'), max_digits=15, decimal_places=2)
    probability = models.IntegerField(_('Olasılık'), validators=[MinValueValidator(0), MaxValueValidator(100)])
    stage = models.CharField(_('Aşama'), max_length=20, choices=[
        ('PROSPECTING', _('Araştırma')),
        ('QUALIFICATION', _('Nitelendirme')),
        ('NEEDS_ANALYSIS', _('İhtiyaç Analizi')),
        ('VALUE_PROPOSITION', _('Değer Önerisi')),
        ('ID_DECISION_MAKERS', _('Karar Vericiler')),
        ('PERCEPTION_ANALYSIS', _('Algı Analizi')),
        ('PROPOSAL_PRICE_QUOTE', _('Teklif')),
        ('NEGOTIATION_REVIEW', _('Pazarlık')),
        ('CLOSED_WON', _('Kazanıldı')),
        ('CLOSED_LOST', _('Kaybedildi')),
    ])
    expected_close_date = models.DateField(_('Beklenen Kapanış Tarihi'))
    actual_close_date = models.DateField(_('Gerçekleşen Kapanış Tarihi'), null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='opportunities')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Fırsat')
        verbose_name_plural = _('Fırsatlar')
        ordering = ['-expected_close_date']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['stage']),
            models.Index(fields=['owner']),
            models.Index(fields=['expected_close_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.customer.company_name}"

    def clean(self):
        if self.probability < 0 or self.probability > 100:
            raise ValidationError(_('Olasılık 0-100 arasında olmalıdır.'))

class Activity(models.Model):
    """Aktivite modeli"""
    TYPE_CHOICES = [
        ('call', _('Telefon')),
        ('meeting', _('Toplantı')),
        ('email', _('E-posta')),
        ('task', _('Görev'))
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.CharField(_('Konu'), max_length=255)
    description = models.TextField(_('Açıklama'))
    due_date = models.DateTimeField(_('Bitiş Tarihi'))
    completed = models.BooleanField(_('Tamamlandı'), default=False)
    completed_at = models.DateTimeField(_('Tamamlanma Tarihi'), null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activities')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Aktivite')
        verbose_name_plural = _('Aktiviteler')
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['opportunity']),
            models.Index(fields=['type']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.subject}"

class Document(models.Model):
    """Doküman modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    file = models.FileField(_('Dosya'), upload_to='documents/')
    type = models.CharField(_('Tür'), max_length=20, choices=[
        ('CONTRACT', _('Sözleşme')),
        ('PROPOSAL', _('Teklif')),
        ('INVOICE', _('Fatura')),
        ('REPORT', _('Rapor')),
        ('OTHER', _('Diğer')),
    ])
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='documents')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Doküman')
        verbose_name_plural = _('Dokümanlar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['type']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"{self.title} - {self.customer.company_name}"

class Communication(models.Model):
    """İletişim kaydı modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='communications')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, related_name='communications')
    type = models.CharField(_('Tür'), max_length=20, choices=[
        ('CALL', _('Telefon Görüşmesi')),
        ('EMAIL', _('E-posta')),
        ('MEETING', _('Toplantı')),
        ('CHAT', _('Sohbet')),
        ('LETTER', _('Mektup')),
    ])
    subject = models.CharField(_('Konu'), max_length=255)
    content = models.TextField(_('İçerik'))
    direction = models.CharField(_('Yön'), max_length=10, choices=[
        ('INBOUND', _('Gelen')),
        ('OUTBOUND', _('Giden')),
    ])
    status = models.CharField(_('Durum'), max_length=20, choices=[
        ('PENDING', _('Beklemede')),
        ('COMPLETED', _('Tamamlandı')),
        ('FAILED', _('Başarısız')),
    ])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='communications')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('İletişim Kaydı')
        verbose_name_plural = _('İletişim Kayıtları')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['contact']),
            models.Index(fields=['type']),
            models.Index(fields=['direction']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.subject}"

class Note(models.Model):
    """Not modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(_('Başlık'), max_length=255)
    content = models.TextField(_('İçerik'))
    is_private = models.BooleanField(_('Özel'), default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notes')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Not')
        verbose_name_plural = _('Notlar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_private']),
        ]

    def __str__(self):
        return f"{self.title} - {self.customer.company_name}"

class CustomerNote(models.Model):
    """Müşteri notu modeli"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes', verbose_name='Müşteri')
    title = models.CharField(max_length=200, verbose_name='Başlık')
    content = models.TextField(verbose_name='İçerik')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Müşteri Notu'
        verbose_name_plural = 'Müşteri Notları'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.company_name} - {self.title}"

class CustomerDocument(models.Model):
    """Müşteri belgesi modeli"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_documents', verbose_name='Müşteri')
    title = models.CharField(max_length=200, verbose_name='Başlık')
    file = models.FileField(upload_to='customer_documents/', verbose_name='Dosya')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Müşteri Belgesi'
        verbose_name_plural = 'Müşteri Belgeleri'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.company_name} - {self.title}"

class Opportunity(models.Model):
    """Fırsat modeli"""
    OPPORTUNITY_STATUS_CHOICES = [
        ('open', 'Açık'),
        ('won', 'Kazanıldı'),
        ('lost', 'Kaybedildi'),
        ('dormant', 'Uyuyan'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Fırsat Adı')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='opportunities', verbose_name='Müşteri')
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Değer')
    expected_close_date = models.DateField(verbose_name='Tahmini Kapanış Tarihi')
    status = models.CharField(max_length=20, choices=OPPORTUNITY_STATUS_CHOICES, default='open', verbose_name='Durum')
    probability = models.IntegerField(default=50, verbose_name='Olasılık (%)')
    notes = models.TextField(blank=True, verbose_name='Notlar')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_opportunities', verbose_name='Atanan Kişi')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Fırsat'
        verbose_name_plural = 'Fırsatlar'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Sale(models.Model):
    """Müşteri satış kaydı modeli"""
    
    STATUS_CHOICES = (
        ('draft', _('Taslak')),
        ('confirmed', _('Onaylandı')),
        ('cancelled', _('İptal Edildi')),
    )
    
    PAYMENT_CHOICES = (
        ('cash', _('Nakit')),
        ('credit', _('Kredi Kartı')),
        ('bank', _('Banka Transferi')),
        ('other', _('Diğer')),
    )
    
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='sales', verbose_name=_('Müşteri'))
    date = models.DateField(_('Satış Tarihi'), default=timezone.now)
    number = models.CharField(_('Satış Numarası'), max_length=50, unique=True)
    description = models.TextField(_('Açıklama'), blank=True)
    amount = models.DecimalField(_('Tutar'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('Vergi Tutarı'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(_('Toplam Tutar'), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_('Ödeme Yöntemi'), max_length=20, choices=PAYMENT_CHOICES, default='cash')
    payment_date = models.DateField(_('Ödeme Tarihi'), blank=True, null=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='draft')
    invoice_created = models.BooleanField(_('Fatura Oluşturuldu'), default=False)
    accounting_synced = models.BooleanField(_('Muhasebe Entegrasyonu'), default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sales', verbose_name=_('Oluşturan'))
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Satış')
        verbose_name_plural = _('Satışlar')
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_method']),
        ]
    
    def __str__(self):
        return f"{self.number} - {self.customer.company_name}"
    
    def save(self, *args, **kwargs):
        # Satış numarası otomatik oluşturma
        if not self.number:
            last_sale = Sale.objects.order_by('-id').first()
            if last_sale:
                last_number = int(last_sale.number.split('-')[1])
                self.number = f"SLS-{last_number + 1:05d}"
            else:
                self.number = "SLS-00001"
        super().save(*args, **kwargs)
    
    @property
    def is_editable(self):
        return self.status == 'draft'
    
    @property
    def is_confirmed(self):
        return self.status == 'confirmed'


class SaleItem(models.Model):
    """Satış kalemi modeli"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name=_('Satış'))
    product_name = models.CharField(_('Ürün Adı'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    quantity = models.DecimalField(_('Miktar'), max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(_('Birim Fiyat'), max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(_('Vergi Oranı (%)'), max_digits=5, decimal_places=2, default=18.0)
    amount = models.DecimalField(_('Tutar'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('Vergi Tutarı'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(_('Toplam Tutar'), max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = _('Satış Kalemi')
        verbose_name_plural = _('Satış Kalemleri')
    
    def __str__(self):
        return f"{self.product_name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Tutarları hesapla
        self.amount = self.quantity * self.unit_price
        self.tax_amount = self.amount * (self.tax_rate / 100)
        self.total_amount = self.amount + self.tax_amount
        super().save(*args, **kwargs)


class EDocumentStatus(models.Model):
    """E-belge durum takibi"""
    DOCUMENT_TYPES = (
        ('einvoice', _('E-Fatura')),
        ('earchive', _('E-Arşiv')),
        ('edespatch', _('E-İrsaliye')),
        ('ereceipt', _('E-Serbest Meslek Makbuzu')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('Beklemede')),
        ('processing', _('İşleniyor')),
        ('sent', _('Gönderildi')),
        ('delivered', _('Teslim Edildi')),
        ('accepted', _('Kabul Edildi')),
        ('rejected', _('Reddedildi')),
        ('error', _('Hata')),
    )
    
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='e_documents', verbose_name=_('Satış'))
    document_type = models.CharField(_('Belge Tipi'), max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(_('Belge Numarası'), max_length=50, blank=True)
    external_id = models.CharField(_('Harici ID'), max_length=100, blank=True)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    status_message = models.TextField(_('Durum Mesajı'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('E-Belge Durumu')
        verbose_name_plural = _('E-Belge Durumları')
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document_number}"

class CustomerAcquisitionAnalytics(models.Model):
    """Müşteri edinme analitikleri modeli"""
    
    CHANNEL_CHOICES = [
        ('google_ads', 'Google Ads'),
        ('facebook_ads', 'Facebook Ads'),
        ('referral', 'Referans'),
        ('organic', 'Organik'),
        ('direct', 'Doğrudan'),
        ('email', 'E-posta'),
        ('social', 'Sosyal Medya'),
        ('other', 'Diğer')
    ]
    
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        verbose_name="Edinme Kanalı"
    )
    total_customers = models.IntegerField(
        default=0,
        verbose_name="Toplam Müşteri"
    )
    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Dönüşüm Oranı (%)"
    )
    acquisition_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Edinme Maliyeti"
    )
    average_lifetime_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Ortalama Yaşam Boyu Değer"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Son Güncelleme"
    )
    
    class Meta:
        verbose_name = "Müşteri Edinme Analitiği"
        verbose_name_plural = "Müşteri Edinme Analitikleri"
        ordering = ['-total_customers']
    
    def __str__(self):
        return f"{self.get_channel_display()} - {self.total_customers} müşteri"
    
    def update_metrics(self):
        """Metrikleri günceller"""
        # Dönüşüm oranını hesapla
        total_trials = Customer.objects.filter(
            acquisition_channel=self.channel,
            is_trial=True
        ).count()
        
        if total_trials > 0:
            self.conversion_rate = (self.total_customers / total_trials) * 100
        
        # Ortalama yaşam boyu değeri hesapla
        customers = Customer.objects.filter(acquisition_channel=self.channel)
        total_value = sum(customer.total_revenue for customer in customers)
        
        if self.total_customers > 0:
            self.average_lifetime_value = total_value / self.total_customers
        
        self.save()

class Campaign(models.Model):
    CAMPAIGN_TYPES = [
        ('student', 'Öğrenci İndirimi'),
        ('startup', 'Startup Paketi'),
        ('referral', 'Referans Programı'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
        ('expired', 'Süresi Dolmuş'),
    ]
    
    name = models.CharField(_('Kampanya Adı'), max_length=100)
    campaign_type = models.CharField(_('Kampanya Tipi'), max_length=20, choices=CAMPAIGN_TYPES)
    description = models.TextField(_('Açıklama'))
    discount_rate = models.DecimalField(_('İndirim Oranı'), max_digits=5, decimal_places=2, null=True, blank=True)
    bonus_amount = models.DecimalField(_('Bonus Miktarı'), max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Kampanya')
        verbose_name_plural = _('Kampanyalar')
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    def calculate_discount(self, amount):
        if self.discount_rate:
            return amount * (self.discount_rate / Decimal('100'))
        return Decimal('0')

class CampaignUsage(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='usages')
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='campaign_usages')
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE, related_name='campaign_usages')
    discount_amount = models.DecimalField(_('İndirim Miktarı'), max_digits=10, decimal_places=2)
    bonus_amount = models.DecimalField(_('Bonus Miktarı'), max_digits=10, decimal_places=2, null=True, blank=True)
    used_at = models.DateTimeField(_('Kullanım Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Kampanya Kullanımı')
        verbose_name_plural = _('Kampanya Kullanımları')
    
    def __str__(self):
        return f"{self.campaign.name} - {self.customer.company_name}"

class ReferralProgram(models.Model):
    referrer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='referrals_given')
    referred = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='referrals_received')
    bonus_amount = models.DecimalField(_('Bonus Miktarı'), max_digits=10, decimal_places=2)
    status = models.CharField(_('Durum'), max_length=20, choices=[
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('paid', 'Ödendi'),
    ], default='pending')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    paid_at = models.DateTimeField(_('Ödeme Tarihi'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Referans Programı')
        verbose_name_plural = _('Referans Programları')
    
    def __str__(self):
        return f"{self.referrer.company_name} -> {self.referred.company_name}"

class PremiumPackage(models.Model):
    """Premium paket modeli"""
    PACKAGE_TYPES = [
        ('basic', 'Temel Paket'),
        ('professional', 'Profesyonel Paket'),
        ('enterprise', 'Kurumsal Paket'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Aylık'),
        ('yearly', 'Yıllık'),
    ]
    
    name = models.CharField(_('Paket Adı'), max_length=100)
    package_type = models.CharField(_('Paket Tipi'), max_length=20, choices=PACKAGE_TYPES)
    description = models.TextField(_('Açıklama'))
    price = models.DecimalField(_('Fiyat'), max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(_('Fatura Döngüsü'), max_length=20, choices=BILLING_CYCLES)
    features = models.JSONField(_('Özellikler'), default=dict)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Premium Paket')
        verbose_name_plural = _('Premium Paketler')
    
    def __str__(self):
        return f"{self.name} - {self.get_package_type_display()}"

class BaseService(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        abstract = True

class ConsultingService(BaseService):
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    min_hours = models.PositiveIntegerField()

class TrainingProgram(models.Model):
    """Kurumsal eğitim programı modeli"""
    PROGRAM_TYPES = [
        ('workshop', 'Workshop'),
        ('certification', 'Sertifikasyon'),
        ('custom', 'Özel Program'),
    ]
    
    name = models.CharField(_('Program Adı'), max_length=100)
    program_type = models.CharField(_('Program Tipi'), max_length=20, choices=PROGRAM_TYPES)
    description = models.TextField(_('Açıklama'))
    duration = models.IntegerField(_('Süre (Saat)'))
    price_per_person = models.DecimalField(_('Kişi Başı Fiyat'), max_digits=10, decimal_places=2)
    min_participants = models.IntegerField(_('Minimum Katılımcı'), default=5)
    max_participants = models.IntegerField(_('Maksimum Katılımcı'), default=20)
    materials_included = models.BooleanField(_('Materyal Dahil'), default=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Eğitim Programı')
        verbose_name_plural = _('Eğitim Programları')
    
    def __str__(self):
        return f"{self.name} - {self.get_program_type_display()}"

class APIPricing(models.Model):
    """API kullanım bazlı fiyatlandırma modeli"""
    PRICING_TIERS = [
        ('free', 'Ücretsiz'),
        ('basic', 'Temel'),
        ('premium', 'Premium'),
        ('enterprise', 'Kurumsal'),
    ]
    
    tier = models.CharField(_('Fiyatlandırma Kademesi'), max_length=20, choices=PRICING_TIERS)
    requests_per_month = models.IntegerField(_('Aylık İstek Limiti'))
    price_per_request = models.DecimalField(_('İstek Başı Ücret'), max_digits=10, decimal_places=4)
    base_price = models.DecimalField(_('Temel Ücret'), max_digits=10, decimal_places=2)
    features = models.JSONField(_('Özellikler'), default=dict)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('API Fiyatlandırması')
        verbose_name_plural = _('API Fiyatlandırmaları')
    
    def __str__(self):
        return f"{self.get_tier_display()} - {self.requests_per_month} istek/ay"

class ServiceSubscription(models.Model):
    """Hizmet aboneliği modeli"""
    SUBSCRIPTION_TYPES = [
        ('package', 'Premium Paket'),
        ('consulting', 'Danışmanlık'),
        ('training', 'Eğitim'),
        ('api', 'API'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('cancelled', 'İptal Edildi'),
        ('expired', 'Süresi Doldu'),
    ]
    
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='subscriptions')
    subscription_type = models.CharField(_('Abonelik Tipi'), max_length=20, choices=SUBSCRIPTION_TYPES)
    package = models.ForeignKey(PremiumPackage, on_delete=models.SET_NULL, null=True, blank=True)
    consulting_service = models.ForeignKey(ConsultingService, on_delete=models.SET_NULL, null=True, blank=True)
    training_program = models.ForeignKey(TrainingProgram, on_delete=models.SET_NULL, null=True, blank=True)
    api_pricing = models.ForeignKey(APIPricing, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='active')
    monthly_fee = models.DecimalField(_('Aylık Ücret'), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Hizmet Aboneliği')
        verbose_name_plural = _('Hizmet Abonelikleri')
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.get_subscription_type_display()}"
    
    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    def calculate_monthly_revenue(self):
        """Aylık gelir hesaplama"""
        if self.subscription_type == 'package':
            return self.monthly_fee
        elif self.subscription_type == 'consulting':
            return self.consulting_service.hourly_rate * self.consulting_service.min_hours
        elif self.subscription_type == 'training':
            return self.training_program.price_per_person * self.training_program.min_participants
        elif self.subscription_type == 'api':
            return self.api_pricing.base_price + (self.api_pricing.price_per_request * self.api_pricing.requests_per_month)
        return Decimal('0')

class LoyaltyProgram(models.Model):
    """Müşteri sadakat programı modeli"""
    LEVEL_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    name = models.CharField(_('Program Adı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    points_per_purchase = models.DecimalField(_('Alışveriş Başına Puan'), max_digits=10, decimal_places=2)
    points_to_currency = models.DecimalField(_('Puan/TL Oranı'), max_digits=10, decimal_places=2)
    min_purchase_for_points = models.DecimalField(_('Minimum Alışveriş Tutarı'), max_digits=10, decimal_places=2)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sadakat Programı')
        verbose_name_plural = _('Sadakat Programları')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name

class LoyaltyLevel(models.Model):
    """Sadakat programı seviye modeli"""
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='levels')
    level = models.CharField(_('Seviye'), max_length=20, choices=LoyaltyProgram.LEVEL_CHOICES)
    min_points = models.IntegerField(_('Minimum Puan'))
    benefits = models.JSONField(_('Avantajlar'), default=dict)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Sadakat Seviyesi')
        verbose_name_plural = _('Sadakat Seviyeleri')
    
    def __str__(self):
        return f"{self.program.name} - {self.get_level_display()}"

class CustomerLoyalty(models.Model):
    """Müşteri sadakat bilgileri modeli"""
    customer = models.ForeignKey('crm.Customer', on_delete=models.CASCADE, related_name='loyalty_info')
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)
    current_level = models.ForeignKey(LoyaltyLevel, on_delete=models.SET_NULL, null=True)
    total_points = models.IntegerField(_('Toplam Puan'), default=0)
    points_expiry_date = models.DateField(_('Puan Son Kullanma Tarihi'), null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Müşteri Sadakat Bilgisi')
        verbose_name_plural = _('Müşteri Sadakat Bilgileri')
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['total_points']),
            models.Index(fields=['points_expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.customer.company_name} - {self.program.name}"

class SeasonalCampaign(models.Model):
    """Sezonsal kampanya modeli"""
    CAMPAIGN_TYPES = [
        ('summer', 'Yaz Kampanyası'),
        ('winter', 'Kış Kampanyası'),
        ('spring', 'Bahar Kampanyası'),
        ('autumn', 'Sonbahar Kampanyası'),
        ('holiday', 'Tatil Kampanyası'),
    ]
    
    name = models.CharField(_('Kampanya Adı'), max_length=100)
    campaign_type = models.CharField(_('Kampanya Tipi'), max_length=20, choices=CAMPAIGN_TYPES)
    description = models.TextField(_('Açıklama'))
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    discount_rate = models.DecimalField(_('İndirim Oranı'), max_digits=5, decimal_places=2, null=True)
    min_purchase_amount = models.DecimalField(_('Minimum Alışveriş Tutarı'), max_digits=10, decimal_places=2, null=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Sezonsal Kampanya')
        verbose_name_plural = _('Sezonsal Kampanyalar')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['campaign_type']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_campaign_type_display()}"

class PartnershipProgram(models.Model):
    """İş ortaklığı programı modeli"""
    PARTNER_TYPES = [
        ('reseller', 'Bayi'),
        ('consultant', 'Danışman'),
        ('affiliate', 'Affiliate'),
        ('strategic', 'Stratejik Ortak'),
    ]
    
    name = models.CharField(_('Program Adı'), max_length=100)
    partner_type = models.CharField(_('Ortak Tipi'), max_length=20, choices=PARTNER_TYPES)
    description = models.TextField(_('Açıklama'))
    commission_rate = models.DecimalField(_('Komisyon Oranı'), max_digits=5, decimal_places=2)
    min_sales_target = models.DecimalField(_('Minimum Satış Hedefi'), max_digits=10, decimal_places=2)
    benefits = models.JSONField(_('Avantajlar'), default=dict)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('İş Ortaklığı Programı')
        verbose_name_plural = _('İş Ortaklığı Programları')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['partner_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_partner_type_display()}"

class Partner(models.Model):
    """İş ortağı modeli"""
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('active', 'Aktif'),
        ('suspended', 'Askıya Alındı'),
        ('terminated', 'Sonlandırıldı'),
    ]
    
    program = models.ForeignKey(PartnershipProgram, on_delete=models.CASCADE, related_name='partners')
    company_name = models.CharField(_('Şirket Adı'), max_length=200)
    contact_person = models.CharField(_('İletişim Kişisi'), max_length=100)
    email = models.EmailField(_('E-posta'))
    phone = models.CharField(_('Telefon'), max_length=20)
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='pending')
    total_sales = models.DecimalField(_('Toplam Satış'), max_digits=10, decimal_places=2, default=0)
    total_commission = models.DecimalField(_('Toplam Komisyon'), max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('İş Ortağı')
        verbose_name_plural = _('İş Ortakları')
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['status']),
            models.Index(fields=['program']),
        ]
    
    def __str__(self):
        return f"{self.company_name} - {self.program.name}"

class InteractionLog(models.Model):
    """Müşteri etkileşim kaydı modeli"""
    INTERACTION_TYPES = [
        ('call', 'Telefon'),
        ('email', 'E-posta'),
        ('meeting', 'Toplantı'),
        ('note', 'Not'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions', verbose_name='Müşteri')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES, verbose_name='Etkileşim Tipi')
    subject = models.CharField(max_length=200, verbose_name='Konu')
    notes = models.TextField(verbose_name='Notlar')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Tarih')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    
    class Meta:
        verbose_name = 'Etkileşim Kaydı'
        verbose_name_plural = 'Etkileşim Kayıtları'
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.customer.company_name} - {self.get_interaction_type_display()} - {self.subject}"
