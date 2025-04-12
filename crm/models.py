from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounting.models import BaseModel, Account
from decimal import Decimal

User = get_user_model()

class Customer(BaseModel):
    """Müşteri bilgilerini tutan model"""
    CUSTOMER_TYPES = (
        ('individual', _('Bireysel')),
        ('corporate', _('Kurumsal')),
    )
    
    account = models.OneToOneField(Account, on_delete=models.CASCADE, verbose_name=_("Cari Hesap"))
    name = models.CharField(_('İsim/Unvan'), max_length=255)
    contact_person = models.CharField(_('İletişim Kişisi'), max_length=255, blank=True, null=True)
    email = models.EmailField(_('E-posta'), blank=True, null=True)
    phone = models.CharField(_('Telefon'), max_length=20, blank=True, null=True)
    tax_number = models.CharField(_('Vergi Numarası'), max_length=20, blank=True, null=True)
    tax_office = models.CharField(_('Vergi Dairesi'), max_length=100, blank=True, null=True)
    address = models.TextField(_('Adres'), blank=True, null=True)
    customer_type = models.CharField(_('Müşteri Tipi'), max_length=20, choices=CUSTOMER_TYPES, default='individual')
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    # E-belge ve muhasebe entegrasyonu için yeni alanlar
    is_e_invoice_user = models.BooleanField(_('E-Fatura Kullanıcısı'), default=False)
    is_e_archive_user = models.BooleanField(_('E-Arşiv Kullanıcısı'), default=False)
    e_invoice_last_check = models.DateTimeField(_('Son E-Fatura Kontrolü'), null=True, blank=True)
    accounting_reference = models.CharField(_('Muhasebe Referansı'), max_length=50, blank=True, null=True, 
                                          help_text=_('Muhasebe sistemindeki cari hesap kodu'))
    default_payment_method = models.CharField(_('Varsayılan Ödeme Yöntemi'), max_length=50, blank=True, null=True,
                                            choices=(
                                                ('cash', _('Nakit')),
                                                ('credit_card', _('Kredi Kartı')),
                                                ('bank_transfer', _('Banka Havalesi')),
                                                ('check', _('Çek')),
                                            ))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Müşteri')
        verbose_name_plural = _('Müşteriler')
        ordering = ['-created_at']

class Contact(BaseModel):
    """İletişim kişisi modeli"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts', verbose_name=_("Müşteri"))
    name = models.CharField(_('İletişim Kişisi'), max_length=200, default='')
    position = models.CharField(_('Pozisyon'), max_length=100, blank=True)
    phone = models.CharField(_('Telefon'), max_length=20, blank=True)
    email = models.EmailField(_('E-posta'), blank=True)
    notes = models.TextField(_('Notlar'), blank=True)
    
    class Meta:
        verbose_name = _('İletişim Kişisi')
        verbose_name_plural = _('İletişim Kişileri')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.customer.name}"

class Opportunity(BaseModel):
    """Satış fırsatı modeli"""
    STATUS_CHOICES = [
        ('new', _('Yeni')),
        ('qualified', _('Nitelikli')),
        ('proposal', _('Teklif')),
        ('negotiation', _('Görüşme')),
        ('closed_won', _('Kazanıldı')),
        ('closed_lost', _('Kaybedildi')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Düşük')),
        ('medium', _('Orta')),
        ('high', _('Yüksek')),
        ('urgent', _('Acil')),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='opportunities', verbose_name=_("Müşteri"))
    name = models.CharField(_('Fırsat Adı'), max_length=200, default='')
    amount = models.DecimalField(_('Tutar'), max_digits=15, decimal_places=2, default=0)
    probability = models.IntegerField(_('Olasılık (%)'), default=0)
    expected_close_date = models.DateField(_('Beklenen Kapanış Tarihi'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(_("Öncelik"), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_opportunities', verbose_name=_("Atanan Kişi"))
    notes = models.TextField(_('Notlar'), blank=True)
    
    class Meta:
        verbose_name = _('Fırsat')
        verbose_name_plural = _('Fırsatlar')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.customer.name}"

class Activity(BaseModel):
    """Aktivite modeli"""
    TYPE_CHOICES = [
        ('call', _('Telefon Görüşmesi')),
        ('meeting', _('Toplantı')),
        ('email', _('E-posta')),
        ('task', _('Görev')),
    ]
    
    STATUS_CHOICES = [
        ('planned', _('Planlandı')),
        ('in_progress', _('Devam Ediyor')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='activities', verbose_name=_("Müşteri"))
    type = models.CharField(_('Tür'), max_length=20, choices=TYPE_CHOICES, default='task')
    subject = models.CharField(_('Konu'), max_length=200, default='')
    description = models.TextField(_('Açıklama'), blank=True)
    due_date = models.DateField(_('Bitiş Tarihi'))
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='planned')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_activities', verbose_name=_("Atanan Kişi"))
    notes = models.TextField(_('Notlar'), blank=True)
    
    class Meta:
        verbose_name = _('Aktivite')
        verbose_name_plural = _('Aktiviteler')
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.subject}"

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
    
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='sales', verbose_name=_('Müşteri'))
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
    
    def __str__(self):
        return f"{self.number} - {self.customer.name}"
    
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

class Document(models.Model):
    """Elektronik belgeleri ve ilgili dosyaları tutan model"""
    DOCUMENT_TYPES = (
        ('e_invoice', _('E-Fatura')),
        ('e_archive', _('E-Arşiv Fatura')),
        ('e_dispatch', _('E-İrsaliye')),
        ('contract', _('Sözleşme')),
        ('other', _('Diğer')),
    )
    
    title = models.CharField(_('Başlık'), max_length=255)
    document_type = models.CharField(_('Belge Tipi'), max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(_('Belge Numarası'), max_length=50, blank=True, null=True)
    issue_date = models.DateField(_('Düzenleme Tarihi'))
    file = models.FileField(_('Dosya'), upload_to='documents/%Y/%m/')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, related_name='documents', null=True, blank=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    uuid = models.CharField(_('UUID'), max_length=36, blank=True, null=True,
                          help_text=_('E-belge sistemindeki ETTN/UUID değeri'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document_number or self.title}"
    
    class Meta:
        verbose_name = _('Belge')
        verbose_name_plural = _('Belgeler')
        ordering = ['-issue_date']
