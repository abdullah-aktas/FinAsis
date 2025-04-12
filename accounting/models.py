from django.db import models
from django.conf import settings
from virtual_company.models import VirtualCompany
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
from django.core.validators import MinValueValidator
from django.utils import timezone
import os
from django.core.exceptions import ValidationError

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    virtual_company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, null=True, blank=True)
    currency = models.CharField(max_length=3, default='TRY', choices=[
        ('TRY', 'Türk Lirası'),
        ('USD', 'Amerikan Doları'),
        ('EUR', 'Euro'),
        ('GBP', 'İngiliz Sterlini'),
    ])

    class Meta:
        abstract = True

class ChartOfAccounts(BaseModel):
    """
    Tekdüzen Hesap Planı
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[
        ('asset', 'Varlık'),
        ('liability', 'Yükümlülük'),
        ('equity', 'Özkaynak'),
        ('income', 'Gelir'),
        ('expense', 'Gider'),
    ])
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    level = models.IntegerField(default=1)
    is_leaf = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Hesap Planı'
        verbose_name_plural = 'Hesap Planı'
        ordering = ['code']

class Account(BaseModel):
    """Cari Hesap"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=[
        ('customer', 'Müşteri'),
        ('supplier', 'Tedarikçi'),
        ('employee', 'Çalışan'),
        ('other', 'Diğer'),
    ])
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    # E-belge entegrasyonu için eklenenler
    vkn_tckn = models.CharField(max_length=11, blank=True, null=True, verbose_name="VKN/TCKN")
    tax_office = models.CharField(max_length=100, blank=True, null=True, verbose_name="Vergi Dairesi")
    e_invoice_registered = models.BooleanField(default=False, verbose_name="E-Fatura Mükellefiyeti")
    e_archive_registered = models.BooleanField(default=False, verbose_name="E-Arşiv Mükellefiyeti")

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Cari Hesap'
        verbose_name_plural = 'Cari Hesaplar'

class Invoice(BaseModel):
    """Fatura"""
    number = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    due_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    type = models.CharField(max_length=20, choices=[
        ('sales', 'Satış Faturası'),
        ('purchase', 'Alış Faturası'),
    ])
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    description = models.TextField(blank=True, null=True)
    # E-belge entegrasyonu için eklenenler
    e_invoice_status = models.CharField(max_length=20, choices=[
        ('draft', 'Taslak'),
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
        ('canceled', 'İptal Edildi'),
    ], default='draft', verbose_name="E-Fatura Durumu")
    is_e_invoice = models.BooleanField(default=False, verbose_name="E-Fatura mı?")
    is_e_archive = models.BooleanField(default=False, verbose_name="E-Arşiv mi?")
    e_invoice_id = models.CharField(max_length=36, blank=True, null=True, verbose_name="E-Fatura ID")
    e_invoice_uuid = models.CharField(max_length=36, blank=True, null=True, verbose_name="E-Fatura UUID")
    # E-fatura ilgili alanlar
    is_e_invoice_suitable = models.BooleanField(_('E-Fatura Uygun mu?'), default=False)
    recipient_vkn_tckn = models.CharField(_('VKN/TCKN'), max_length=11, blank=True, null=True)
    recipient_tax_office = models.CharField(_('Vergi Dairesi'), max_length=100, blank=True, null=True)
    recipient_email = models.EmailField(_('E-Posta'), blank=True, null=True)

    def __str__(self):
        return f"{self.number} - {self.account.name}"

    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturalar'

    @property
    def has_e_document(self):
        return hasattr(self, 'e_document')
    
    @property
    def can_create_e_invoice(self):
        """Fatura için e-belge oluşturulabilir mi kontrolü"""
        # İptal edilmiş veya silinmiş faturalar için e-belge oluşturulamaz
        if self.is_deleted:
            return False
        
        # Faturanın e-belgeye uygun olması gerekir
        if hasattr(self, 'is_e_invoice_suitable') and not self.is_e_invoice_suitable:
            return False
        
        # Fatura numarası ve tarihi gibi zorunlu alanların dolu olması lazım
        if not (self.number and self.date and self.account):
            return False
        
        # Fatura kalemlerinin olması gerekir
        if not self.lines.exists():
            return False
        
        # Toplam tutarın sıfırdan büyük olması gerekir
        if self.total <= 0:
            return False
        
        # Zaten e-belge oluşturulmuş mu kontrolü
        if self.edocument_set.exists():
            return False
        
        return True

class InvoiceLine(BaseModel):
    """Fatura Kalemi"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    product = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.invoice.number} - {self.product}"

    class Meta:
        verbose_name = 'Fatura Kalemi'
        verbose_name_plural = 'Fatura Kalemleri'

class Transaction(BaseModel):
    """Yevmiye Kaydı"""
    date = models.DateField()
    number = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.number} - {self.date}"

    class Meta:
        verbose_name = 'Yevmiye Kaydı'
        verbose_name_plural = 'Yevmiye Kayıtları'

class TransactionLine(BaseModel):
    """Yevmiye Kaydı Kalemi"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='lines')
    account_code = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.transaction.number} - {self.account_code}"

    class Meta:
        verbose_name = 'Yevmiye Kaydı Kalemi'
        verbose_name_plural = 'Yevmiye Kaydı Kalemleri'

class CashBox(BaseModel):
    """
    Kasa
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Kasa'
        verbose_name_plural = 'Kasalar'

class Bank(BaseModel):
    """
    Banka
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    account_number = models.CharField(max_length=50)
    iban = models.CharField(max_length=50, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Banka'
        verbose_name_plural = 'Bankalar'

class Stock(BaseModel):
    """
    Stok
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    unit = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Stok'
        verbose_name_plural = 'Stoklar'

class StockTransaction(BaseModel):
    """
    Stok Hareketi
    """
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name='transactions')
    date = models.DateField()
    type = models.CharField(max_length=20, choices=[
        ('income', 'Giriş'),
        ('expense', 'Çıkış'),
    ])
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.stock.code} - {self.date} - {self.type}"

    class Meta:
        verbose_name = 'Stok Hareketi'
        verbose_name_plural = 'Stok Hareketleri'
        ordering = ['-date', '-created_at']

# E-Belge Entegrasyon modelleri
class EInvoiceSettings(BaseModel):
    """E-Fatura Entegrasyon Ayarları"""
    INTEGRATION_TYPES = [
        ('GIB', 'GİB'),
        ('EFATURA', 'E-Fatura'),
        ('EFINANS', 'E-Finans'),
        ('TEFATURA', 'Türk E-Fatura'),
        ('CUSTOM', 'Özel Entegrasyon'),
    ]
    
    integration_type = models.CharField(
        max_length=20,
        choices=INTEGRATION_TYPES,
        default='GIB',
        verbose_name="Entegrasyon Tipi"
    )
    api_key = models.CharField(max_length=255, verbose_name="API Anahtarı")
    username = models.CharField(max_length=100, verbose_name="Kullanıcı Adı")
    password = models.CharField(max_length=100, verbose_name="Şifre")
    service_url = models.URLField(verbose_name="Servis URL")
    company_name = models.CharField(max_length=255, verbose_name="Firma Adı")
    tax_office = models.CharField(max_length=100, verbose_name="Vergi Dairesi")
    tax_number = models.CharField(max_length=11, verbose_name="Vergi Numarası")
    is_test_mode = models.BooleanField(default=True, verbose_name="Test Modu")
    is_active = models.BooleanField(default=False, verbose_name="Aktif")
    
    # Yeni alanlar
    auto_send = models.BooleanField(default=False, verbose_name="Otomatik Gönderim")
    auto_archive = models.BooleanField(default=False, verbose_name="Otomatik Arşivleme")
    notification_email = models.EmailField(blank=True, verbose_name="Bildirim E-posta")
    retry_count = models.IntegerField(default=3, verbose_name="Yeniden Deneme Sayısı")
    retry_interval = models.IntegerField(default=300, verbose_name="Yeniden Deneme Aralığı (sn)")
    
    def __str__(self):
        return f"{self.company_name} E-Fatura Ayarları"
    
    class Meta:
        verbose_name = 'E-Fatura Ayarları'
        verbose_name_plural = 'E-Fatura Ayarları'
        
    def clean(self):
        """Model doğrulama"""
        if self.is_active and not self.api_key:
            raise ValidationError({'api_key': 'API anahtarı gereklidir.'})
        
        if self.integration_type in ['EFATURA', 'EFINANS', 'TEFATURA'] and not self.username:
            raise ValidationError({'username': 'Kullanıcı adı gereklidir.'})
            
    def save(self, *args, **kwargs):
        """Kaydetmeden önce doğrulama yap"""
        self.clean()
        super().save(*args, **kwargs)

class EInvoiceLog(BaseModel):
    """E-Fatura İşlem Kayıtları"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='e_invoice_logs')
    action = models.CharField(max_length=50, choices=[
        ('send', 'Gönderim'),
        ('query', 'Sorgulama'),
        ('cancel', 'İptal'),
        ('accept', 'Kabul'),
        ('reject', 'Red'),
    ], verbose_name="İşlem")
    status = models.CharField(max_length=50, choices=[
        ('success', 'Başarılı'),
        ('error', 'Hata'),
        ('pending', 'Beklemede'),
    ], verbose_name="Durum")
    message = models.TextField(blank=True, null=True, verbose_name="Mesaj")
    request_data = models.TextField(blank=True, null=True, verbose_name="İstek Verisi")
    response_data = models.TextField(blank=True, null=True, verbose_name="Yanıt Verisi")
    
    def __str__(self):
        return f"{self.invoice.number} - {self.get_action_display()} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = 'E-Fatura Log'
        verbose_name_plural = 'E-Fatura Logları'
        ordering = ['-created_at']

class EDocumentTemplate(BaseModel):
    """E-Belge Şablonları"""
    name = models.CharField(max_length=100, verbose_name="Şablon Adı")
    type = models.CharField(max_length=20, choices=[
        ('e_invoice', 'E-Fatura'),
        ('e_archive', 'E-Arşiv'),
        ('e_dispatch', 'E-İrsaliye'),
    ], verbose_name="Belge Türü")
    template_html = models.TextField(verbose_name="HTML Şablonu")
    is_default = models.BooleanField(default=False, verbose_name="Varsayılan mı?")
    
    def __str__(self):
        return f"{self.name} - {self.get_type_display()}"
    
    class Meta:
        verbose_name = 'E-Belge Şablonu'
        verbose_name_plural = 'E-Belge Şablonları'

# E-Belge Durum Seçenekleri
E_DOCUMENT_STATUS_CHOICES = [
    ('PENDING', 'Bekliyor'),
    ('SENT', 'Gönderildi'),
    ('DELIVERED', 'Teslim Edildi'),
    ('ACCEPTED', 'Kabul Edildi'),
    ('REJECTED', 'Reddedildi'),
    ('CANCELED', 'İptal Edildi'),
    ('ERROR', 'Hata'),
]

# E-Belge Tipleri
E_DOCUMENT_TYPE_CHOICES = [
    ('INVOICE', 'e-Fatura'),
    ('ARCHIVE_INVOICE', 'e-Arşiv Fatura'),
    ('DISPATCH', 'e-İrsaliye'),
    ('RECEIPT', 'e-Makbuz'),
]

class EDocumentSettings(BaseModel):
    """E-belge entegrasyonu için ayarlar"""
    
    INTEGRATION_TYPE_CHOICES = (
        ('GIB', _('GİB Portal')),
        ('EFATURA', _('E-Fatura Entegratörü')),
        ('EFINANS', _('E-Finans')),
        ('TEFATURA', _('T.C. E-Fatura')),
        ('CUSTOM', _('Özel Entegrasyon')),
    )
    
    company_name = models.CharField(_('Şirket Adı'), max_length=255)
    vkn_tckn = models.CharField(_('VKN/TCKN'), max_length=11)
    tax_office = models.CharField(_('Vergi Dairesi'), max_length=100)
    address = models.TextField(_('Adres'))
    phone = models.CharField(_('Telefon'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('E-posta'), blank=True, null=True)
    
    integration_type = models.CharField(_('Entegrasyon Tipi'), max_length=20, choices=INTEGRATION_TYPE_CHOICES)
    service_url = models.URLField(_('Servis URL'), blank=True, null=True)
    api_key = models.CharField(_('API Anahtarı'), max_length=255, blank=True, null=True)
    username = models.CharField(_('Kullanıcı Adı'), max_length=100, blank=True, null=True)
    password = models.CharField(_('Şifre'), max_length=100, blank=True, null=None)
    
    is_test_mode = models.BooleanField(_('Test Modu'), default=True)
    is_active = models.BooleanField(_('Aktif'), default=False)
    
    # Yeni alanlar
    auto_send = models.BooleanField(_('Otomatik Gönderim'), default=False, 
                                   help_text=_('E-belgeler oluşturulduğunda otomatik olarak gönderilsin'))
    auto_archive = models.BooleanField(_('Otomatik Arşivleme'), default=False,
                                      help_text=_('E-belgeler onaylandığında otomatik olarak arşivlensin'))
    notification_email = models.EmailField(_('Bildirim E-posta'), blank=True, null=True,
                                         help_text=_('E-belge durumu değiştiğinde bildirim gönderilecek e-posta'))
    retry_count = models.IntegerField(_('Yeniden Deneme Sayısı'), default=3,
                                    help_text=_('Başarısız e-belge işlemleri için yeniden deneme sayısı'))
    retry_interval = models.IntegerField(_('Yeniden Deneme Aralığı (sn)'), default=300,
                                       help_text=_('Başarısız e-belge işlemleri arasındaki bekleme süresi (saniye)'))
    
    class Meta:
        verbose_name = _('E-Belge Ayarları')
        verbose_name_plural = _('E-Belge Ayarları')
    
    def __str__(self):
        return self.company_name
    
    def get_settings_dict(self):
        return {
            'company_name': self.company_name,
            'vkn_tckn': self.vkn_tckn,
            'tax_office': self.tax_office,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'service_url': self.service_url,
            'api_key': self.api_key,
            'username': self.username,
            'password': self.password,
            'is_test_mode': self.is_test_mode,
        }

class EDocument(BaseModel):
    """
    E-Belge (E-Fatura, E-Arşiv)
    """
    DOCUMENT_TYPES = [
        ('EINVOICE', 'E-Fatura'),
        ('EARCHIVE', 'E-Arşiv Fatura'),
        ('EDISPATCH', 'E-İrsaliye'),
        ('ERECEIPT', 'E-Makbuz'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Taslak'),
        ('PENDING', 'Beklemede'),
        ('SENT', 'Gönderildi'),
        ('DELIVERED', 'Teslim Edildi'),
        ('ACCEPTED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
        ('CANCELED', 'İptal Edildi'),
        ('ERROR', 'Hata'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='edocument_set')
    document_type = models.CharField(max_length=15, choices=DOCUMENT_TYPES, verbose_name="Belge Türü")
    document_uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name="UUID")
    document_number = models.CharField(max_length=30, blank=True, null=True, verbose_name="Belge Numarası")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT', verbose_name="Durum")
    status_message = models.TextField(blank=True, null=True, verbose_name="Durum Açıklaması")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name="Gönderim Tarihi")
    accepted_at = models.DateTimeField(blank=True, null=True, verbose_name="Onay Tarihi")
    external_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Dış Sistem ID")
    pdf_file = models.FileField(upload_to='e_documents/pdf/', blank=True, null=True, verbose_name="PDF Dosyası")
    xml_file = models.FileField(upload_to='e_documents/xml/', blank=True, null=True, verbose_name="XML Dosyası")
    xml_content = models.TextField(blank=True, null=True, verbose_name="XML İçeriği")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")
    
    # Yeni alanlar
    target_vkn_tckn = models.CharField(_('Hedef VKN/TCKN'), max_length=11, blank=True, null=True)
    target_name = models.CharField(_('Hedef Adı'), max_length=255, blank=True, null=True)
    retry_count = models.IntegerField(_('Yeniden Deneme Sayısı'), default=0)
    last_retry_at = models.DateTimeField(_('Son Deneme Tarihi'), blank=True, null=True)
    
    def __str__(self):
        return f"{self.document_type} - {self.document_number} - {self.status}"
    
    class Meta:
        verbose_name = 'E-Belge'
        verbose_name_plural = 'E-Belgeler'
        ordering = ['-created_at']
        
    def check_status(self):
        """E-belge durumunu entegratörden kontrol eder"""
        from .services.e_document_service import EDocumentService
        service = EDocumentService()
        return service.check_document_status(self)
        
    def download_pdf(self):
        """E-belge PDF dosyasını indirir"""
        from .services.e_document_service import EDocumentService
        service = EDocumentService()
        return service.download_document_pdf(self)
        
    def cancel(self, reason=None):
        """E-belgeyi iptal eder"""
        from .services.e_document_service import EDocumentService
        service = EDocumentService()
        return service.cancel_document(self, reason)
        
    @property
    def is_finalized(self):
        """E-belgenin kesinleşip kesinleşmediğini kontrol eder"""
        return self.status in ['ACCEPTED', 'REJECTED', 'CANCELED']
        
    @property 
    def can_be_canceled(self):
        """E-belgenin iptal edilebilir olup olmadığını kontrol eder"""
        return self.status == 'ACCEPTED'
    
    def save_pdf(self, pdf_content):
        """PDF içeriğini kaydeder"""
        from django.core.files.base import ContentFile
        filename = f"{self.document_number}.pdf"
        self.pdf_file.save(filename, ContentFile(pdf_content))
        self.save()
    
    def save_xml(self, xml_content):
        """XML içeriğini kaydeder"""
        from django.core.files.base import ContentFile
        filename = f"{self.document_number}.xml"
        self.xml_file.save(filename, ContentFile(xml_content.encode('utf-8')))
        self.xml_content = xml_content
        self.save()

class DailyTask(models.Model):
    """Günlük görevler modeli"""
    
    CATEGORY_CHOICES = (
        ('accounting', _('Muhasebe')),
        ('finance', _('Finans')),
        ('tax', _('Vergi')),
        ('investments', _('Yatırımlar')),
        ('budgeting', _('Bütçeleme')),
        ('business', _('İş Dünyası')),
        ('economics', _('Ekonomi')),
    )
    
    DIFFICULTY_CHOICES = (
        ('beginner', _('Başlangıç')),
        ('intermediate', _('Orta')),
        ('advanced', _('İleri')),
    )
    
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'))
    learning_objective = models.TextField(_('Öğrenim Hedefi'), blank=True, null=True, 
                                        help_text=_('Bu görev tamamlandığında kullanıcının öğreneceği kavram veya beceri'))
    completion_hints = models.TextField(_('Tamamlama İpuçları'), blank=True, null=True,
                                      help_text=_('Görevi tamamlamak için yardımcı ipuçları'))
    resources = models.TextField(_('İlgili Kaynaklar'), blank=True, null=True,
                               help_text=_('Görevle ilgili faydalı bağlantılar ve kaynaklar'))
    category = models.CharField(_('Kategori'), max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(_('Zorluk'), max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    points = models.PositiveIntegerField(_('Puanlar'), default=10)
    estimated_time = models.PositiveIntegerField(_('Tahmini Süre (dakika)'), default=15)
    active = models.BooleanField(_('Aktif'), default=True)
    knowledge_required = models.ManyToManyField('KnowledgeBase', related_name='related_tasks', blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    
    class Meta:
        verbose_name = _('Günlük Görev')
        verbose_name_plural = _('Günlük Görevler')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class UserDailyTask(models.Model):
    """Kullanıcı günlük görev ilişkisi modeli"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_tasks')
    task = models.ForeignKey(DailyTask, on_delete=models.CASCADE, related_name='user_tasks')
    completed = models.BooleanField(_('Tamamlandı'), default=False)
    completion_date = models.DateTimeField(_('Tamamlanma Tarihi'), null=True, blank=True)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Kullanıcı Görevi')
        verbose_name_plural = _('Kullanıcı Görevleri')
        unique_together = ('user', 'task')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title}"
    
    def complete_task(self):
        """Görevi tamamla"""
        if not self.completed:
            self.completed = True
            self.completion_date = timezone.now()
            self.save()
            return True
        return False

class KnowledgeBase(models.Model):
    """Bilgi bankası modeli"""
    
    CATEGORY_CHOICES = (
        ('accounting', _('Muhasebe')),
        ('finance', _('Finans')),
        ('tax', _('Vergi')),
        ('investments', _('Yatırımlar')),
        ('budgeting', _('Bütçeleme')),
        ('business', _('İş Dünyası')),
        ('economics', _('Ekonomi')),
    )
    
    LEVEL_CHOICES = (
        ('beginner', _('Başlangıç')),
        ('intermediate', _('Orta')),
        ('advanced', _('İleri')),
    )
    
    title = models.CharField(_('Başlık'), max_length=255)
    content = models.TextField(_('İçerik'))
    summary = models.TextField(_('Özet'), blank=True, null=True)
    category = models.CharField(_('Kategori'), max_length=20, choices=CATEGORY_CHOICES)
    level = models.CharField(_('Seviye'), max_length=20, choices=LEVEL_CHOICES, default='beginner')
    image = models.ImageField(_('Görsel'), upload_to='knowledge_base/', blank=True, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)
    tags = models.CharField(_('Etiketler'), max_length=255, blank=True, null=True, 
                          help_text=_('Virgülle ayrılmış etiketler'))
    active = models.BooleanField(_('Aktif'), default=True)
    is_featured = models.BooleanField(_('Öne Çıkan'), default=False)
    
    class Meta:
        verbose_name = _('Bilgi Bankası')
        verbose_name_plural = _('Bilgi Bankası')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """Etiketleri liste olarak döndürür"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

class KnowledgeBaseRelatedItem(models.Model):
    """Bilgi bankası ilişkili öğeler modeli"""
    
    RESOURCE_TYPE_CHOICES = (
        ('article', _('Makale')),
        ('video', _('Video')),
        ('document', _('Döküman')),
        ('website', _('Web Sitesi')),
        ('tool', _('Araç')),
    )
    
    knowledge_base = models.ForeignKey(
        KnowledgeBase, 
        on_delete=models.CASCADE, 
        related_name='related_items',
        verbose_name=_('Bilgi Bankası')
    )
    title = models.CharField(_('Başlık'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True, null=True)
    url = models.URLField(_('URL'), blank=True, null=True)
    resource_type = models.CharField(
        _('Kaynak Tipi'), 
        max_length=20, 
        choices=RESOURCE_TYPE_CHOICES,
        default='article'
    )
    order = models.PositiveIntegerField(_('Sıralama'), default=0)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('İlişkili Öğe')
        verbose_name_plural = _('İlişkili Öğeler')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.knowledge_base.title} - {self.title}"

class UserKnowledgeRead(models.Model):
    """Kullanıcının okuduğu bilgi bankası kayıtları"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='knowledge_reads')
    knowledge = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='user_reads')
    read_date = models.DateTimeField(_('Okuma Tarihi'), auto_now_add=True)
    read_count = models.PositiveIntegerField(_('Okuma Sayısı'), default=1)
    last_read = models.DateTimeField(_('Son Okuma'), auto_now=True)
    
    class Meta:
        verbose_name = _('Kullanıcı Okuması')
        verbose_name_plural = _('Kullanıcı Okumaları')
        unique_together = ('user', 'knowledge')
        ordering = ['-last_read']
    
    def __str__(self):
        return f"{self.user.username} - {self.knowledge.title}"

class Budget(BaseModel):
    """Bütçe Planı"""
    name = models.CharField(max_length=100, verbose_name="Bütçe Adı")
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam Tutar")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Taslak'),
        ('active', 'Aktif'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ], default='draft', verbose_name="Durum")

    class Meta:
        verbose_name = 'Bütçe'
        verbose_name_plural = 'Bütçeler'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

class BudgetLine(BaseModel):
    """Bütçe Kalemi"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT)
    planned_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Planlanan Tutar")
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Gerçekleşen Tutar")
    variance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Fark")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")

    class Meta:
        verbose_name = 'Bütçe Kalemi'
        verbose_name_plural = 'Bütçe Kalemleri'
        ordering = ['account__code']

    def __str__(self):
        return f"{self.budget.name} - {self.account.name}"

    def calculate_variance(self):
        """Fark hesaplama"""
        self.variance = self.actual_amount - self.planned_amount
        self.save()

class CashFlow(BaseModel):
    """Nakit Akışı"""
    date = models.DateField(verbose_name="Tarih")
    type = models.CharField(max_length=20, choices=[
        ('inflow', 'Giriş'),
        ('outflow', 'Çıkış'),
    ], verbose_name="Tip")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar")
    category = models.CharField(max_length=50, verbose_name="Kategori")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    is_recurring = models.BooleanField(default=False, verbose_name="Tekrarlayan mı?")
    recurrence_period = models.CharField(max_length=20, choices=[
        ('daily', 'Günlük'),
        ('weekly', 'Haftalık'),
        ('monthly', 'Aylık'),
        ('yearly', 'Yıllık'),
    ], blank=True, null=True, verbose_name="Tekrarlama Periyodu")

    class Meta:
        verbose_name = 'Nakit Akışı'
        verbose_name_plural = 'Nakit Akışları'
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.get_type_display()} - {self.amount} {self.currency}"
