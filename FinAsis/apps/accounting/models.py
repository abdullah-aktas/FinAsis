import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinAsis.settings')
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

"""
Şirket, müşteri, fatura, ürün, satış, ödeme, banka ve hareket modellerini içerir.
Her modelin başında kısa açıklama ve docstring eklendi.
"""

# Şirket modeli
class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Şirket Adı")
    trade_name = models.CharField(max_length=255, verbose_name="Ticari Unvan", blank=True, null=True)
    tax_number = models.CharField(
        max_length=20,
        verbose_name="Vergi Numarası",
        unique=True,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Vergi numarası 10 haneli olmalıdır.")]
    )
    tax_office = models.CharField(max_length=100, verbose_name="Vergi Dairesi", blank=True, null=True)
    address = models.TextField(verbose_name="Adres", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="Telefon", blank=True, null=True)
    email = models.EmailField(verbose_name="E-posta", blank=True, null=True)
    website = models.URLField(verbose_name="Web Sitesi", blank=True, null=True)
    sector = models.CharField(max_length=100, verbose_name="Sektör", blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', verbose_name="Logo", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_companies', verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_companies', verbose_name="Güncelleyen Kullanıcı"
    )
    country = models.CharField(max_length=2, verbose_name="Ülke", default="TR", help_text="ISO ülke kodu (örn: TR, US, DE)")
    base_currency = models.CharField(max_length=3, verbose_name="Ana Para Birimi", default="TRY", help_text="ISO para birimi kodu (örn: TRY, USD, EUR)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Şirket"
        verbose_name_plural = "Şirketler"

# Müşteri modeli    
class Customer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='customers', verbose_name="Bağlı Olduğu Şirket")
    first_name = models.CharField(max_length=100, verbose_name="Adı")
    last_name = models.CharField(max_length=100, verbose_name="Soyadı")
    email = models.EmailField(verbose_name="E-posta", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="Telefon", blank=True, null=True)
    address = models.TextField(verbose_name="Adres", blank=True, null=True)
    tax_number = models.CharField(max_length=20, verbose_name="Vergi Numarası", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_customers', verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_customers', verbose_name="Güncelleyen Kullanıcı"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"

# Fatura modeli
class Invoice(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invoices', verbose_name="Şirket")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices', verbose_name="Müşteri")
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Fatura Numarası")
    issue_date = models.DateField(verbose_name="Fatura Tarihi")
    due_date = models.DateField(verbose_name="Vade Tarihi", blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam Tutar")
    currency = models.CharField(max_length=10, default="TRY", verbose_name="Para Birimi")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_invoices', verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_invoices', verbose_name="Güncelleyen Kullanıcı"
    )
    gib_uuid = models.CharField(max_length=64, blank=True, null=True, verbose_name="GİB UUID")
    gib_status = models.CharField(max_length=32, blank=True, null=True, verbose_name="GİB Durumu")
    gib_response = models.TextField(blank=True, null=True, verbose_name="GİB Yanıtı")
    gib_sent_at = models.DateTimeField(blank=True, null=True, verbose_name="GİB Gönderim Zamanı")
    gib_cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name="GİB İptal Zamanı")
    gib_xml = models.FileField(upload_to='efatura/xml/', blank=True, null=True, verbose_name="e-Fatura XML")
    gib_pdf = models.FileField(upload_to='efatura/pdf/', blank=True, null=True, verbose_name="e-Fatura PDF")
    e_archive = models.BooleanField(default=False, verbose_name="e-Arşiv")
    KDV_RATES = [
        (0.01, '%1'),
        (0.10, '%10'),
        (0.20, '%20'),
    ]
    kdv_rate = models.DecimalField(max_digits=4, decimal_places=2, choices=KDV_RATES, default=0.20, verbose_name="KDV Oranı")

    def __str__(self):
        return f"Fatura {self.invoice_number} - {self.customer}"

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturalar"
        ordering = ["-issue_date"]

# Masraf modeli
class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('KIRA', 'Kira'),
        ('MAAS', 'Maaş'),
        ('OFIS', 'Ofis Gideri'),
        ('YOL', 'Yol / Ulaşım'),
        ('DIGER', 'Diğer'),
    ]
    EXPENSE_CATEGORIES_DICT = dict(EXPENSE_CATEGORIES)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses', verbose_name="Şirket")
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, verbose_name="Gider Türü")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    expense_date = models.DateField(verbose_name="Gider Tarihi")
    paid = models.BooleanField(default=False, verbose_name="Ödendi mi?")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_expenses', verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_expenses', verbose_name="Güncelleyen Kullanıcı"
    )

    def __str__(self):
        return f"{self.get_category_display()} - {self.amount}₺"

    class Meta:
        verbose_name = "Gider"
        verbose_name_plural = "Giderler"
        ordering = ['-expense_date']

#Ürün modeli
class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products', verbose_name="Şirket")
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stok Miktarı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_products', verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_products', verbose_name="Güncelleyen Kullanıcı"
    )

    def __str__(self):
        return f"{self.name} ({self.price}₺)"

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

#
class Sale(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="sales", verbose_name="Şirket")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="sales", verbose_name="Müşteri")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales", verbose_name="Ürün")
    quantity = models.PositiveIntegerField(verbose_name="Adet")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam Tutar", editable=False)
    sale_date = models.DateField(verbose_name="Satış Tarihi", auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_sales', verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_sales', verbose_name="Güncelleyen Kullanıcı"
    )

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} → {self.product} ({self.quantity})"

    class Meta:
        verbose_name = "Satış"
        verbose_name_plural = "Satışlar"
        ordering = ['-sale_date']

#Ödeme modeli
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('NAKIT', 'Nakit'),
        ('KREDIKARTI', 'Kredi Kartı'),
        ('BANKA', 'Banka Transferi'),
        ('CEK', 'Çek'),
        ('DIGER', 'Diğer'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="payments", verbose_name="Şirket")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="payments", verbose_name="Müşteri")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ödeme Tutarı")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Ödeme Yöntemi")
    related_invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, blank=True, null=True, related_name="payments", verbose_name="İlgili Fatura")
    payment_date = models.DateField(verbose_name="Ödeme Tarihi", auto_now_add=True)
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_payments', verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_payments', verbose_name="Güncelleyen Kullanıcı"
    )

    def __str__(self):
        return f"{self.customer} - {self.amount}₺"

    class Meta:
        verbose_name = "Ödeme"
        verbose_name_plural = "Ödemeler"
        ordering = ['-payment_date']

#Banka Hesabı modeli
class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('VADESIZ', 'Vadesiz Hesap'),
        ('VADELİ', 'Vadeli Hesap'),
        ('KREDI', 'Kredi Hesabı'),
        ('DIGER', 'Diğer'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="bank_accounts", verbose_name="Şirket")
    bank_name = models.CharField(max_length=100, verbose_name="Banka Adı")
    iban = models.CharField(
        max_length=34,
        unique=True,
        verbose_name="IBAN",
        validators=[RegexValidator(regex=r'^TR\d{2}[0-9A-Z]{1,30}$', message="Geçerli bir IBAN giriniz (TR ile başlamalıdır).")]
    )
    account_name = models.CharField(max_length=100, verbose_name="Hesap Sahibinin Adı")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name="Hesap Türü")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Bakiye")
    currency = models.CharField(max_length=10, default="TRY", verbose_name="Para Birimi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bankaccounts', verbose_name="Oluşturan Kullanıcı"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_bankaccounts', verbose_name="Güncelleyen Kullanıcı"
    )

    def __str__(self):
        return f"{self.bank_name} ({self.iban})"

    class Meta:
        verbose_name = "Banka Hesabı"
        verbose_name_plural = "Banka Hesapları"

#Fatura Kalemi modeli
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name="Fatura")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ürün")
    description = models.CharField(max_length=255, verbose_name="Açıklama", blank=True, null=True)
    quantity = models.PositiveIntegerField(verbose_name="Adet")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam Tutar", editable=False)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice.invoice_number} → {self.product or self.description} ({self.quantity})"

    class Meta:
        verbose_name = "Fatura Kalemi"
        verbose_name_plural = "Fatura Kalemleri"

class BankTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Giriş'),
        ('OUT', 'Çıkış'),
    ]
    account = models.ForeignKey('BankAccount', on_delete=models.CASCADE, related_name='transactions', verbose_name="Banka Hesabı")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Açıklama")
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, verbose_name="İşlem Türü")
    date = models.DateTimeField(auto_now_add=True, verbose_name="İşlem Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    def __str__(self):
        return f"{self.account} - {self.amount} ({self.get_transaction_type_display()})"

    class Meta:
        verbose_name = "Banka Hareketi"
        verbose_name_plural = "Banka Hareketleri"
        ordering = ['-date']

class CompanyDeleteLog(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.user} - {self.deleted_at}"

class EDefter(models.Model):
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    type = models.CharField(max_length=10, choices=[('yevmiye', 'Yevmiye'), ('kebir', 'Kebir')])
    xml_file = models.FileField(upload_to='edefter/xml/')
    berat_file = models.FileField(upload_to='edefter/berat/')
    status = models.CharField(max_length=20, default='taslak')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.year}-{self.month} {self.type}"

class Declaration(models.Model):
    DECLARATION_TYPES = [
        ("KDV", "KDV Beyannamesi"),
        ("MUHTASAR", "Muhtasar Beyanname"),
        ("BABS", "BA/BS Formu"),
    ]
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    declaration_type = models.CharField(max_length=16, choices=DECLARATION_TYPES)
    period = models.CharField(max_length=7, help_text="YYYY-MM")
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='beyanname/', blank=True, null=True)
    status = models.CharField(max_length=16, default='draft')
    response = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Beyanname"
        verbose_name_plural = "Beyannameler"

    def __str__(self):
        return f"{self.company} - {self.declaration_type} - {self.period}"
