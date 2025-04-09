from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from accounting.models import BaseModel, Account

class Customer(BaseModel):
    """Müşteri modeli"""
    account = models.OneToOneField(Account, on_delete=models.CASCADE, verbose_name=_("Cari Hesap"))
    name = models.CharField(_('Müşteri Adı'), max_length=200, default='')
    tax_number = models.CharField(_('Vergi Numarası'), max_length=20, blank=True)
    tax_office = models.CharField(_('Vergi Dairesi'), max_length=100, blank=True)
    address = models.TextField(_('Adres'), blank=True)
    phone = models.CharField(_('Telefon'), max_length=20, blank=True)
    email = models.EmailField(_('E-posta'), blank=True)
    website = models.URLField(_('Web Sitesi'), blank=True)
    notes = models.TextField(_('Notlar'), blank=True)
    
    class Meta:
        verbose_name = _('Müşteri')
        verbose_name_plural = _('Müşteriler')
        ordering = ['name']
    
    def __str__(self):
        return self.name

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

class Document(BaseModel):
    """Belge modeli"""
    TYPE_CHOICES = [
        ('contract', _('Sözleşme')),
        ('proposal', _('Teklif')),
        ('invoice', _('Fatura')),
        ('other', _('Diğer')),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents', verbose_name=_("Müşteri"))
    name = models.CharField(_('Belge Adı'), max_length=200, default='')
    file = models.FileField(_('Dosya'), upload_to='documents/')
    type = models.CharField(_('Tür'), max_length=20, choices=TYPE_CHOICES, default='other')
    notes = models.TextField(_('Notlar'), blank=True)
    
    class Meta:
        verbose_name = _('Belge')
        verbose_name_plural = _('Belgeler')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.customer.name}"
