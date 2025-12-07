from django.db import models
from django.db.models import QuerySet
from django.conf import settings
from django.core.validators import RegexValidator
from decimal import Decimal
from django.utils.text import slugify

"""
Şirket, müşteri, fatura, ürün, satış, ödeme, banka ve hareket modellerini içerir.
Her modelin başında kısa açıklama ve docstring eklendi.
"""


# Şirket modeli
class CompanyQuerySet(models.QuerySet["Company"]):
    def with_totals(self) -> QuerySet:
        return self


class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Şirket Adı")
    trade_name = models.CharField(
        max_length=255, verbose_name="Ticari Unvan", blank=True, null=True
    )
    tax_number = models.CharField(
        max_length=20,
        verbose_name="Vergi Numarası",
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$", message="Vergi numarası 10 haneli olmalıdır."
            )
        ],
    )
    tax_office = models.CharField(
        max_length=100, verbose_name="Vergi Dairesi", blank=True, null=True
    )
    address = models.TextField(verbose_name="Adres", blank=True, null=True)
    phone = models.CharField(
        max_length=20, verbose_name="Telefon", blank=True, null=True
    )
    email = models.EmailField(verbose_name="E-posta", blank=True, null=True)
    website = models.URLField(verbose_name="Web Sitesi", blank=True, null=True)
    sector = models.CharField(
        max_length=100, verbose_name="Sektör", blank=True, null=True
    )
    logo = models.ImageField(
        upload_to="company_logos/", verbose_name="Logo", blank=True, null=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_companies",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_companies",
        verbose_name="Güncelleyen Kullanıcı",
    )
    country = models.CharField(
        max_length=2,
        verbose_name="Ülke",
        default="TR",
        help_text="ISO ülke kodu (örn: TR, US, DE)",
    )
    base_currency = models.CharField(
        max_length=3,
        verbose_name="Ana Para Birimi",
        default="TRY",
        help_text="ISO para birimi kodu (örn: TRY, USD, EUR)",
    )
    slug = models.SlugField(
        max_length=255, unique=True, blank=True, null=True, verbose_name="SEO Adresi"
    )

    # Custom manager
    objects = CompanyQuerySet.as_manager()

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name) or slugify(self.trade_name or "") or "sirket"
        base_slug = base_slug[:200]
        slug_candidate = base_slug
        counter = 2
        while Company.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
            slug_candidate = f"{base_slug}-{counter}"[:255]
            counter += 1
        return slug_candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        else:
            desired = slugify(self.name) or slugify(self.trade_name or "") or "sirket"
            desired = desired[:200]
            if desired and not self.slug.startswith(desired):
                self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "accounting"
        verbose_name = "Şirket"
        verbose_name_plural = "Şirketler"


# Müşteri modeli
class CustomerQuerySet(models.QuerySet["Customer"]):
    def with_company(self) -> QuerySet:
        return self.select_related("company")


class Customer(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="customers",
        verbose_name="Bağlı Olduğu Şirket",
    )
    first_name = models.CharField(max_length=100, verbose_name="Adı")
    last_name = models.CharField(max_length=100, verbose_name="Soyadı")
    email = models.EmailField(verbose_name="E-posta", blank=True, null=True)
    phone = models.CharField(
        max_length=20, verbose_name="Telefon", blank=True, null=True
    )
    address = models.TextField(verbose_name="Adres", blank=True, null=True)
    tax_number = models.CharField(
        max_length=20, verbose_name="Vergi Numarası", blank=True, null=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_customers",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_customers",
        verbose_name="Güncelleyen Kullanıcı",
    )

    # Custom manager
    objects = CustomerQuerySet.as_manager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        app_label = "accounting"
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"


# Fatura modeli
class InvoiceQuerySet(models.QuerySet["Invoice"]):
    def with_related(self) -> QuerySet:
        return self.select_related("company", "customer")


class Invoice(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name="Şirket",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name="Müşteri",
    )
    invoice_number = models.CharField(
        max_length=50, unique=True, verbose_name="Fatura Numarası"
    )
    issue_date = models.DateField(verbose_name="Fatura Tarihi")
    due_date = models.DateField(verbose_name="Vade Tarihi", blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Toplam Tutar"
    )
    currency = models.CharField(
        max_length=10, default="TRY", verbose_name="Para Birimi"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_invoices",
        verbose_name="Güncelleyen Kullanıcı",
    )
    gib_uuid = models.CharField(
        max_length=64, blank=True, null=True, verbose_name="GİB UUID"
    )
    gib_status = models.CharField(
        max_length=32, blank=True, null=True, verbose_name="GİB Durumu"
    )
    gib_response = models.TextField(blank=True, null=True, verbose_name="GİB Yanıtı")
    gib_sent_at = models.DateTimeField(
        blank=True, null=True, verbose_name="GİB Gönderim Zamanı"
    )
    gib_cancelled_at = models.DateTimeField(
        blank=True, null=True, verbose_name="GİB İptal Zamanı"
    )
    gib_xml = models.FileField(
        upload_to="efatura/xml/", blank=True, null=True, verbose_name="e-Fatura XML"
    )
    gib_pdf = models.FileField(
        upload_to="efatura/pdf/", blank=True, null=True, verbose_name="e-Fatura PDF"
    )
    e_archive = models.BooleanField(default=False, verbose_name="e-Arşiv")
    KDV_RATES = [
        (Decimal("0.01"), "%1"),
        (Decimal("0.10"), "%10"),
        (Decimal("0.20"), "%20"),
    ]
    kdv_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        choices=KDV_RATES,
        default=Decimal("0.20"),
        verbose_name="KDV Oranı",
    )

    # Custom manager
    objects = InvoiceQuerySet.as_manager()

    def __str__(self):
        return f"Fatura {self.invoice_number} - {self.customer}"

    class Meta:
        app_label = "accounting"
        verbose_name = "Fatura"
        verbose_name_plural = "Faturalar"
        ordering = ["-issue_date"]


# Masraf modeli
class ExpenseQuerySet(models.QuerySet["Expense"]):
    def with_company(self) -> QuerySet:
        return self.select_related("company")


class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ("KIRA", "Kira"),
        ("MAAS", "Maaş"),
        ("OFIS", "Ofis Gideri"),
        ("YOL", "Yol / Ulaşım"),
        ("DIGER", "Diğer"),
    ]
    EXPENSE_CATEGORIES_DICT = dict(EXPENSE_CATEGORIES)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="Şirket",
    )
    category = models.CharField(
        max_length=20, choices=EXPENSE_CATEGORIES, verbose_name="Gider Türü"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    expense_date = models.DateField(verbose_name="Gider Tarihi")
    paid = models.BooleanField(default=False, verbose_name="Ödendi mi?")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_expenses",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_expenses",
        verbose_name="Güncelleyen Kullanıcı",
    )

    # Custom manager
    objects = ExpenseQuerySet.as_manager()

    def __str__(self):
        # Django run-time'da display helper ekler; type checker'a ipucu verelim
        from typing import cast

        display = cast(str, getattr(self, "get_category_display")())
        return f"{display} - {self.amount}₺"

    class Meta:
        app_label = "accounting"
        verbose_name = "Gider"
        verbose_name_plural = "Giderler"
        ordering = ["-expense_date"]


# Ürün modeli
class ProductQuerySet(models.QuerySet["Product"]):
    def with_company(self) -> QuerySet:
        return self.select_related("company")


class Product(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Şirket",
    )
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Birim Fiyat"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stok Miktarı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_products",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_products",
        verbose_name="Güncelleyen Kullanıcı",
    )

    # Custom manager
    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} ({self.price}₺)"

    class Meta:
        app_label = "accounting"
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"


#
class SaleQuerySet(models.QuerySet["Sale"]):
    def with_related(self) -> QuerySet:
        return self.select_related("company", "customer", "product")


class Sale(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="sales", verbose_name="Şirket"
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="sales", verbose_name="Müşteri"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sales", verbose_name="Ürün"
    )
    quantity = models.PositiveIntegerField(verbose_name="Adet")
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Birim Fiyat"
    )
    total_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Toplam Tutar", editable=False
    )
    sale_date = models.DateField(verbose_name="Satış Tarihi", auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_sales",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_sales",
        verbose_name="Güncelleyen Kullanıcı",
    )

    # Custom manager
    objects = SaleQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} → {self.product} ({self.quantity})"

    class Meta:
        app_label = "accounting"
        verbose_name = "Satış"
        verbose_name_plural = "Satışlar"
        ordering = ["-sale_date"]


# Ödeme modeli
class PaymentQuerySet(models.QuerySet["Payment"]):
    def with_related(self) -> QuerySet:
        return self.select_related("company", "customer", "related_invoice")


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("NAKIT", "Nakit"),
        ("KREDIKARTI", "Kredi Kartı"),
        ("BANKA", "Banka Transferi"),
        ("CEK", "Çek"),
        ("DIGER", "Diğer"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Şirket",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Müşteri",
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Ödeme Tutarı"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, verbose_name="Ödeme Yöntemi"
    )
    related_invoice = models.ForeignKey(
        "Invoice",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="payments",
        verbose_name="İlgili Fatura",
    )
    payment_date = models.DateField(verbose_name="Ödeme Tarihi", auto_now_add=True)
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_payments",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_payments",
        verbose_name="Güncelleyen Kullanıcı",
    )

    def __str__(self):
        return f"{self.customer} - {self.amount}₺"

    class Meta:
        app_label = "accounting"
        verbose_name = "Ödeme"
        verbose_name_plural = "Ödemeler"
        ordering = ["-payment_date"]

    # Basit onay alanları
    approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_payments",
        verbose_name="Onaylayan",
    )
    approved_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Onay Zamanı"
    )

    # Custom manager
    objects = PaymentQuerySet.as_manager()


# Banka Hesabı modeli
class BankAccountQuerySet(models.QuerySet["BankAccount"]):
    def with_company(self) -> QuerySet:
        return self.select_related("company")


class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ("VADESIZ", "Vadesiz Hesap"),
        ("VADELİ", "Vadeli Hesap"),
        ("KREDI", "Kredi Hesabı"),
        ("DIGER", "Diğer"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        verbose_name="Şirket",
    )
    bank_name = models.CharField(max_length=100, verbose_name="Banka Adı")
    iban = models.CharField(
        max_length=34,
        unique=True,
        verbose_name="IBAN",
        validators=[
            RegexValidator(
                regex=r"^TR\d{2}[0-9A-Z]{1,30}$",
                message="Geçerli bir IBAN giriniz (TR ile başlamalıdır).",
            )
        ],
    )
    account_name = models.CharField(max_length=100, verbose_name="Hesap Sahibinin Adı")
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPES, verbose_name="Hesap Türü"
    )
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"), verbose_name="Bakiye"
    )
    currency = models.CharField(
        max_length=10, default="TRY", verbose_name="Para Birimi"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_bankaccounts",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_bankaccounts",
        verbose_name="Güncelleyen Kullanıcı",
    )

    # Custom manager
    objects = BankAccountQuerySet.as_manager()

    def __str__(self):
        return f"{self.bank_name} ({self.iban})"

    class Meta:
        app_label = "accounting"
        verbose_name = "Banka Hesabı"
        verbose_name_plural = "Banka Hesapları"


# Fatura Kalemi modeli
class InvoiceItemQuerySet(models.QuerySet["InvoiceItem"]):
    def with_related(self) -> QuerySet:
        return self.select_related("invoice", "product", "invoice__company")


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="items", verbose_name="Fatura"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ürün"
    )
    description = models.CharField(
        max_length=255, verbose_name="Açıklama", blank=True, null=True
    )
    quantity = models.PositiveIntegerField(verbose_name="Adet")
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Birim Fiyat"
    )
    total_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Toplam Tutar", editable=False
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    # Custom manager
    objects = InvoiceItemQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice.invoice_number} → {self.product or self.description} ({self.quantity})"

    class Meta:
        app_label = "accounting"
        verbose_name = "Fatura Kalemi"
        verbose_name_plural = "Fatura Kalemleri"


class BankTransactionQuerySet(models.QuerySet["BankTransaction"]):
    def with_related(self) -> QuerySet:
        return self.select_related("account", "account__company")


class BankTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("IN", "Giriş"),
        ("OUT", "Çıkış"),
    ]
    account = models.ForeignKey(
        "BankAccount",
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Banka Hesabı",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar")
    description = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Açıklama"
    )
    transaction_type = models.CharField(
        max_length=3, choices=TRANSACTION_TYPES, verbose_name="İşlem Türü"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="İşlem Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    # Custom manager
    objects = BankTransactionQuerySet.as_manager()

    def __str__(self):
        from typing import cast

        txn_disp = cast(str, getattr(self, "get_transaction_type_display")())
        return f"{self.account} - {self.amount} ({txn_disp})"

    class Meta:
        app_label = "accounting"
        verbose_name = "Banka Hareketi"
        verbose_name_plural = "Banka Hareketleri"
        ordering = ["-date"]


class BankStatement(models.Model):
    """Banka ekstresi başlığı."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="bank_statements",
        verbose_name="Şirket",
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="statements",
        verbose_name="Banka Hesabı",
    )
    period_start = models.DateField(verbose_name="Dönem Başlangıç")
    period_end = models.DateField(verbose_name="Dönem Bitiş")
    opening_balance = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Açılış Bakiyesi"
    )
    closing_balance = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Kapanış Bakiyesi"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Banka Ekstresi"
        verbose_name_plural = "Banka Ekstreleri"
        ordering = ["-period_start"]

    def __str__(self):
        return f"{self.bank_account} [{self.period_start} - {self.period_end}]"


class BankStatementLine(models.Model):
    """Banka ekstresi satırı (mutabakat için)."""

    statement = models.ForeignKey(
        BankStatement,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Ekstre",
    )
    date = models.DateField(verbose_name="Tarih")
    description = models.CharField(
        max_length=255, verbose_name="Açıklama", blank=True, null=True
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Tutar")
    matched_transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matched_statement_lines",
        verbose_name="Eşleşen Hareket",
    )

    class Meta:
        app_label = "accounting"
        verbose_name = "Banka Ekstresi Satırı"
        verbose_name_plural = "Banka Ekstresi Satırları"
        ordering = ["date", "id"]

    def __str__(self):
        return f"{self.date} - {self.amount}"


class CompanyDeleteLog(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    reason = models.TextField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.user} - {self.deleted_at}"


class EDefter(models.Model):
    """e-Defter (Yevmiye/Kebir) kayıtları."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="edefters",
        verbose_name="Şirket",
    )
    year = models.PositiveIntegerField(verbose_name="Yıl")
    month = models.PositiveIntegerField(verbose_name="Ay")
    type = models.CharField(
        max_length=10,
        choices=[("yevmiye", "Yevmiye"), ("kebir", "Kebir")],
        verbose_name="Defter Türü",
    )
    xml_file = models.FileField(
        upload_to="edefter/xml/", blank=True, null=True, verbose_name="XML Dosyası"
    )
    berat_file = models.FileField(
        upload_to="edefter/berat/", blank=True, null=True, verbose_name="Berat Dosyası"
    )
    zip_file = models.FileField(
        upload_to="edefter/zip/", blank=True, null=True, verbose_name="ZIP Paketi"
    )
    status = models.CharField(max_length=20, default="taslak", verbose_name="Durum")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        app_label = "accounting"
        verbose_name = "e-Defter"
        verbose_name_plural = "e-Defterler"
        ordering = ["-year", "-month"]
        unique_together = [["company", "year", "month", "type"]]

    def __str__(self):
        return f"{self.company.name} - {self.year}-{self.month:02d} {self.type}"


class Declaration(models.Model):
    DECLARATION_TYPES = [
        ("KDV", "KDV Beyannamesi"),
        ("MUHTASAR", "Muhtasar Beyanname"),
        ("BABS", "BA/BS Formu"),
    ]
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    declaration_type = models.CharField(max_length=16, choices=DECLARATION_TYPES)
    period = models.CharField(max_length=7, help_text="YYYY-MM")
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="beyanname/", blank=True, null=True)
    status = models.CharField(max_length=16, default="draft")
    response = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Beyanname"
        verbose_name_plural = "Beyannameler"

    def __str__(self):
        return f"{self.company} - {self.declaration_type} - {self.period}"


# --- Accounts Payable (AP) Modelleri ---
class Vendor(models.Model):
    """Tedarikçi modeli (AP)."""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="vendors", verbose_name="Şirket"
    )
    name = models.CharField(max_length=255, verbose_name="Tedarikçi Adı")
    tax_number = models.CharField(
        max_length=20, verbose_name="Vergi Numarası", blank=True, null=True
    )
    email = models.EmailField(verbose_name="E-posta", blank=True, null=True)
    phone = models.CharField(
        max_length=20, verbose_name="Telefon", blank=True, null=True
    )
    address = models.TextField(verbose_name="Adres", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_vendors",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_vendors",
        verbose_name="Güncelleyen Kullanıcı",
    )

    class Meta:
        app_label = "accounting"
        verbose_name = "Tedarikçi"
        verbose_name_plural = "Tedarikçiler"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PurchaseInvoice(models.Model):
    """Tedarikçi faturası (AP faturası)."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="purchase_invoices",
        verbose_name="Şirket",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="purchase_invoices",
        verbose_name="Tedarikçi",
    )
    invoice_number = models.CharField(
        max_length=50, unique=True, verbose_name="Fatura Numarası"
    )
    issue_date = models.DateField(verbose_name="Fatura Tarihi")
    due_date = models.DateField(verbose_name="Vade Tarihi", blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Toplam Tutar"
    )
    currency = models.CharField(
        max_length=10, default="TRY", verbose_name="Para Birimi"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    status = models.CharField(
        max_length=20,
        choices=[
            ("DRAFT", "Taslak"),
            ("APPROVED", "Onaylandı"),
            ("PAID", "Ödendi"),
            ("CANCELED", "İptal Edildi"),
        ],
        default="DRAFT",
        verbose_name="Durum",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_purchase_invoices",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_purchase_invoices",
        verbose_name="Güncelleyen Kullanıcı",
    )

    class Meta:
        app_label = "accounting"
        verbose_name = "Alış Faturası"
        verbose_name_plural = "Alış Faturaları"
        ordering = ["-issue_date"]

    def __str__(self):
        return f"Alış Faturası {self.invoice_number} - {self.vendor}"


class VendorPayment(models.Model):
    """Tedarikçi ödemesi (AP ödeme)."""

    PAYMENT_METHODS = [
        ("NAKIT", "Nakit"),
        ("KREDIKARTI", "Kredi Kartı"),
        ("BANKA", "Banka Transferi"),
        ("CEK", "Çek"),
        ("DIGER", "Diğer"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="vendor_payments",
        verbose_name="Şirket",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Tedarikçi",
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Ödeme Tutarı"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, verbose_name="Ödeme Yöntemi"
    )
    related_invoice = models.ForeignKey(
        "PurchaseInvoice",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="payments",
        verbose_name="İlgili Fatura",
    )
    payment_date = models.DateField(verbose_name="Ödeme Tarihi", auto_now_add=True)
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_vendor_payments",
        verbose_name="Oluşturan Kullanıcı",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_vendor_payments",
        verbose_name="Güncelleyen Kullanıcı",
    )

    class Meta:
        app_label = "accounting"
        verbose_name = "Tedarikçi Ödemesi"
        verbose_name_plural = "Tedarikçi Ödemeleri"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"{self.vendor} - {self.amount}₺"


class AuditLog(models.Model):
    """Basit denetim kaydı (GRC temel)."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        verbose_name="Şirket",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Kullanıcı",
        related_name="accounting_audit_logs",
    )
    action = models.CharField(max_length=100, verbose_name="Aksiyon")
    entity = models.CharField(max_length=100, verbose_name="Nesne")
    entity_id = models.CharField(max_length=100, verbose_name="Nesne ID")
    metadata = models.JSONField(default=dict, verbose_name="Ek Veri")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")

    class Meta:
        app_label = "accounting"
        verbose_name = "Denetim Kaydı"
        verbose_name_plural = "Denetim Kayıtları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company} {self.action} {self.entity}:{self.entity_id}"


class PlanningScenario(models.Model):
    """Basit FP&A senaryo modeli (gelir/gider çarpanları ile)."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="planning_scenarios",
        verbose_name="Şirket",
    )
    name = models.CharField(max_length=100, verbose_name="Senaryo Adı")
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")
    revenue_multiplier = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("1.00"),
        verbose_name="Gelir Çarpanı",
    )
    expense_multiplier = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("1.00"),
        verbose_name="Gider Çarpanı",
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Planlama Senaryosu"
        verbose_name_plural = "Planlama Senaryoları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company} - {self.name} ({self.start_date} - {self.end_date})"


# --- Genel Muhasebe (GL) ve Döviz ---
class GLAccount(models.Model):
    """Tek Düzen Hesap Planı (özet subset)."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="gl_accounts",
        verbose_name="Şirket",
    )
    code = models.CharField(max_length=20, verbose_name="Hesap Kodu")
    name = models.CharField(max_length=255, verbose_name="Hesap Adı")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Üst Hesap",
    )
    category = models.CharField(
        max_length=32,
        choices=[
            ("ASSET", "Varlık"),
            ("LIAB", "Yükümlülük"),
            ("EQUITY", "Özkaynak"),
            ("INCOME", "Gelir"),
            ("EXPENSE", "Gider"),
            ("OFFBS", "Nazım"),
        ],
        verbose_name="Kategori",
    )
    is_leaf = models.BooleanField(default=True, verbose_name="Alt Hesap Yok")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    currency = models.CharField(
        max_length=3, default="TRY", verbose_name="Defter Para Birimi"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "GL Hesap"
        verbose_name_plural = "GL Hesaplar"
        unique_together = ("company", "code")
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} {self.name}"


class ExchangeRate(models.Model):
    """Günlük kur tablosu: base->quote oranı (1 base = rate quote)."""

    base_currency = models.CharField(max_length=3, verbose_name="Baz PB")
    quote_currency = models.CharField(max_length=3, verbose_name="Karşı PB")
    date = models.DateField()
    rate = models.DecimalField(max_digits=18, decimal_places=8, verbose_name="Kur")
    source = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Kaynak"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Kur"
        verbose_name_plural = "Kurlar"
        unique_together = ("base_currency", "quote_currency", "date")
        ordering = ["-date", "base_currency", "quote_currency"]

    def __str__(self):
        return f"{self.date} {self.base_currency}/{self.quote_currency}={self.rate}"


class GLJournalEntry(models.Model):
    """Yevmiye fişi."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="journal_entries",
        verbose_name="Şirket",
    )
    number = models.CharField(max_length=30, verbose_name="Fiş No")
    date = models.DateField(verbose_name="Tarih")
    description = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Açıklama"
    )
    source_type = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Kaynak Türü"
    )
    source_id = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Kaynak ID"
    )
    currency = models.CharField(
        max_length=3, default="TRY", verbose_name="Fiş Para Birimi"
    )
    total_debit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Toplam Borç",
    )
    total_credit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Toplam Alacak",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    posted_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Mizan Onay Zamanı"
    )

    class Meta:
        app_label = "accounting"
        verbose_name = "Yevmiye Fişi"
        verbose_name_plural = "Yevmiye Fişleri"
        unique_together = ("company", "number")
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.number} - {self.date}"

    def recalc_totals(self):
        # Reverse relation 'lines' exists at runtime; to satisfy type checker, query via manager
        sums = GLJournalLine.objects.filter(entry=self).aggregate(
            d=models.Sum("debit"), c=models.Sum("credit")
        )
        self.total_debit = sums.get("d") or 0
        self.total_credit = sums.get("c") or 0
        super().save(update_fields=["total_debit", "total_credit"])


class GLJournalLine(models.Model):
    entry = models.ForeignKey(
        GLJournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Fiş",
    )
    account = models.ForeignKey(
        GLAccount,
        on_delete=models.PROTECT,
        related_name="journal_lines",
        verbose_name="Hesap",
    )
    description = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Açıklama"
    )
    debit = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0"), verbose_name="Borç"
    )
    credit = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0"), verbose_name="Alacak"
    )
    currency = models.CharField(max_length=3, default="TRY", verbose_name="Satır PB")
    fx_rate = models.DecimalField(
        max_digits=18, decimal_places=8, default=Decimal("1"), verbose_name="Kur"
    )
    amount_base = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Tutar (Baz PB)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Yevmiye Satırı"
        verbose_name_plural = "Yevmiye Satırları"
        ordering = ["id"]

    def __str__(self):
        side = "B" if self.debit else "A"
        return f"{self.entry.number} {self.account.code} {side} {self.debit or self.credit}"

    def save(self, *args, **kwargs):
        # Baz para birimi dönüşümü
        raw = self.debit if self.debit else self.credit
        self.amount_base = raw * self.fx_rate if raw else 0
        super().save(*args, **kwargs)
        # Fiş toplamlarını güncelle
        self.entry.recalc_totals()


# ============================================================================
# MALİYET MUHASEBESİ (COST ACCOUNTING)
# ============================================================================


class CostCenter(models.Model):
    """Maliyet merkezi - departman, proje veya ürün bazlı maliyet takibi"""

    COST_CENTER_TYPES = [
        ("department", "Departman"),
        ("project", "Proje"),
        ("product", "Ürün"),
        ("service", "Hizmet"),
        ("location", "Lokasyon"),
        ("custom", "Özel"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="accounting_cost_centers",
        verbose_name="Şirket",
    )
    code = models.CharField(max_length=20, verbose_name="Maliyet Merkezi Kodu")
    name = models.CharField(max_length=200, verbose_name="Maliyet Merkezi Adı")
    center_type = models.CharField(
        max_length=20, choices=COST_CENTER_TYPES, verbose_name="Tip"
    )
    description = models.TextField(blank=True, verbose_name="Açıklama")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sub_centers",
        verbose_name="Üst Maliyet Merkezi",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    budget_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Bütçe"
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_cost_centers",
        verbose_name="Sorumlu",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Maliyet Merkezi"
        verbose_name_plural = "Maliyet Merkezleri"
        unique_together = ["company", "code"]
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class CostAllocation(models.Model):
    """Maliyet dağıtımı - giderlerin maliyet merkezlerine atanması"""

    ALLOCATION_METHODS = [
        ("direct", "Direkt Dağıtım"),
        ("proportional", "Oransal Dağıtım"),
        ("activity_based", "Faaliyet Bazlı"),
        ("manual", "Manuel Dağıtım"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="cost_allocations",
        verbose_name="Şirket",
    )
    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name="Maliyet Merkezi",
    )
    allocation_date = models.DateField(verbose_name="Dağıtım Tarihi")
    allocation_method = models.CharField(
        max_length=20, choices=ALLOCATION_METHODS, default="direct"
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Tutar")
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Dağıtım Yüzdesi",
    )
    description = models.TextField(blank=True, verbose_name="Açıklama")

    # Kaynak bilgisi
    source_expense = models.ForeignKey(
        Expense,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cost_allocations",
    )
    source_transaction = models.ForeignKey(
        BankTransaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cost_allocations",
    )

    allocated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Maliyet Dağıtımı"
        verbose_name_plural = "Maliyet Dağıtımları"
        ordering = ["-allocation_date", "-created_at"]

    def __str__(self):
        return f"{self.cost_center.code} - {self.amount} TL ({self.allocation_date})"


class CostReport(models.Model):
    """Maliyet raporları - maliyet merkezi bazlı analiz"""

    REPORT_TYPES = [
        ("monthly", "Aylık Maliyet Raporu"),
        ("quarterly", "Çeyreklik Maliyet Raporu"),
        ("project_cost", "Proje Maliyet Raporu"),
        ("product_cost", "Ürün Maliyet Raporu"),
        ("variance", "Varyans Analizi"),
        ("profitability", "Karlılık Analizi"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="cost_reports",
        verbose_name="Şirket",
    )
    report_type = models.CharField(
        max_length=30, choices=REPORT_TYPES, verbose_name="Rapor Tipi"
    )
    title = models.CharField(max_length=200, verbose_name="Rapor Başlığı")
    period_start = models.DateField(verbose_name="Başlangıç Tarihi")
    period_end = models.DateField(verbose_name="Bitiş Tarihi")

    # Analiz sonuçları
    total_costs = models.DecimalField(
        max_digits=18, decimal_places=2, default=0, verbose_name="Toplam Maliyetler"
    )
    budgeted_costs = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Bütçelenen Maliyetler",
    )
    variance = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="Varyans"
    )
    variance_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Varyans %"
    )

    # Detay veriler (JSON)
    cost_breakdown = models.JSONField(
        default=dict, blank=True, verbose_name="Maliyet Dağılımı"
    )
    center_analysis = models.JSONField(
        default=list, blank=True, verbose_name="Merkez Bazlı Analiz"
    )
    recommendations = models.JSONField(
        default=list, blank=True, verbose_name="Öneriler"
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Maliyet Raporu"
        verbose_name_plural = "Maliyet Raporları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.period_start} - {self.period_end})"


# ============================================================================
# MUHASEBE DENETİMİ (ACCOUNTING AUDIT)
# ============================================================================


class AccountingAudit(models.Model):
    """Muhasebe denetimi - finansal tabloların ve kayıtların denetimi"""

    AUDIT_TYPES = [
        ("internal", "İç Denetim"),
        ("external", "Dış Denetim"),
        ("tax", "Vergi Denetimi"),
        ("compliance", "Uyumluluk Denetimi"),
        ("financial_statement", "Mali Tablo Denetimi"),
        ("operational", "Operasyonel Denetim"),
    ]

    STATUS_CHOICES = [
        ("planning", "Planlanıyor"),
        ("in_progress", "Devam Ediyor"),
        ("fieldwork", "Saha Çalışması"),
        ("reporting", "Raporlama"),
        ("completed", "Tamamlandı"),
        ("suspended", "Askıya Alındı"),
    ]

    OPINION_CHOICES = [
        ("unqualified", "Olumlu Görüş"),
        ("qualified", "Şartlı Olumlu Görüş"),
        ("adverse", "Olumsuz Görüş"),
        ("disclaimer", "Görüş Bildirmekten Kaçınma"),
        ("pending", "Henüz Belirlenmedi"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="accounting_audits",
        verbose_name="Denetlenen Şirket",
    )
    audit_type = models.CharField(
        max_length=30, choices=AUDIT_TYPES, verbose_name="Denetim Tipi"
    )
    audit_name = models.CharField(max_length=200, verbose_name="Denetim Adı")
    fiscal_year = models.IntegerField(verbose_name="Mali Yıl")
    fiscal_period = models.CharField(
        max_length=10, blank=True, verbose_name="Dönem"
    )  # Q1, Q2, vb.

    # Denetim ekibi
    lead_auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="led_audits",
        verbose_name="Baş Denetçi",
    )
    audit_team = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="audit_participations",
        blank=True,
        verbose_name="Denetim Ekibi",
    )

    # Tarihler
    planned_start = models.DateField(verbose_name="Planlanan Başlangıç")
    planned_end = models.DateField(verbose_name="Planlanan Bitiş")
    actual_start = models.DateField(
        null=True, blank=True, verbose_name="Gerçekleşen Başlangıç"
    )
    actual_end = models.DateField(
        null=True, blank=True, verbose_name="Gerçekleşen Bitiş"
    )

    # Durum ve sonuç
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planning")
    audit_opinion = models.CharField(
        max_length=20,
        choices=OPINION_CHOICES,
        default="pending",
        verbose_name="Denetim Görüşü",
    )
    overall_score = models.IntegerField(
        null=True, blank=True, verbose_name="Genel Skor (0-100)"
    )

    # Rapor ve bulgular
    executive_summary = models.TextField(blank=True, verbose_name="Yönetici Özeti")
    detailed_findings = models.TextField(blank=True, verbose_name="Detaylı Bulgular")
    recommendations = models.JSONField(
        default=list, blank=True, verbose_name="Öneriler"
    )

    # Dosyalar
    audit_report = models.FileField(
        upload_to="audit_reports/", null=True, blank=True, verbose_name="Denetim Raporu"
    )
    working_papers = models.FileField(
        upload_to="audit_workpapers/",
        null=True,
        blank=True,
        verbose_name="Çalışma Kağıtları",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Muhasebe Denetimi"
        verbose_name_plural = "Muhasebe Denetimleri"
        ordering = ["-fiscal_year", "-created_at"]
        indexes = [
            models.Index(fields=["company", "fiscal_year"]),
            models.Index(fields=["status", "audit_type"]),
        ]

    def __str__(self):
        return f"{self.audit_name} - {self.fiscal_year} ({self.get_status_display()})"


class AuditFinding(models.Model):
    """Denetim bulgusu - denetim sırasında tespit edilen sorunlar"""

    FINDING_TYPES = [
        ("error", "Hata"),
        ("irregularity", "Usulsüzlük"),
        ("weakness", "Zayıflık"),
        ("noncompliance", "Uyumsuzluk"),
        ("risk", "Risk"),
        ("observation", "Gözlem"),
    ]

    SEVERITY_LEVELS = [
        ("low", "Düşük"),
        ("medium", "Orta"),
        ("high", "Yüksek"),
        ("critical", "Kritik"),
    ]

    STATUS_CHOICES = [
        ("open", "Açık"),
        ("in_remediation", "Düzeltiliyor"),
        ("resolved", "Çözüldü"),
        ("accepted", "Kabul Edildi"),
        ("disputed", "İtiraz Edildi"),
    ]

    audit = models.ForeignKey(
        AccountingAudit,
        on_delete=models.CASCADE,
        related_name="findings",
        verbose_name="Denetim",
    )
    finding_number = models.CharField(max_length=20, verbose_name="Bulgu No")
    finding_type = models.CharField(
        max_length=20, choices=FINDING_TYPES, verbose_name="Bulgu Tipi"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default="medium",
        verbose_name="Önem Derecesi",
    )

    # Bulgu detayları
    title = models.CharField(max_length=200, verbose_name="Bulgu Başlığı")
    description = models.TextField(verbose_name="Bulgu Açıklaması")
    criteria = models.TextField(verbose_name="Denetim Kriteri/Standardı")
    condition = models.TextField(verbose_name="Mevcut Durum")
    cause = models.TextField(blank=True, verbose_name="Sebep")
    effect = models.TextField(blank=True, verbose_name="Etki")

    # Finansal etki
    financial_impact = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Mali Etki"
    )

    # İlişkili kayıtlar
    related_account = models.ForeignKey(
        GLAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="İlgili Hesap",
    )
    related_invoice = models.ForeignKey(
        Invoice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="İlgili Fatura",
    )
    related_expense = models.ForeignKey(
        Expense,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="İlgili Gider",
    )

    # Düzeltici aksiyon
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    corrective_action = models.TextField(blank=True, verbose_name="Düzeltici Aksiyon")
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="responsible_findings",
        verbose_name="Sorumlu Kişi",
    )
    target_resolution_date = models.DateField(
        null=True, blank=True, verbose_name="Hedef Çözüm Tarihi"
    )
    actual_resolution_date = models.DateField(
        null=True, blank=True, verbose_name="Gerçekleşen Çözüm Tarihi"
    )

    identified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="identified_findings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Denetim Bulgusu"
        verbose_name_plural = "Denetim Bulguları"
        ordering = ["-severity", "-created_at"]
        unique_together = ["audit", "finding_number"]

    def __str__(self):
        return f"{self.finding_number} - {self.title} ({self.get_severity_display()})"


class AuditEvidence(models.Model):
    """Denetim kanıtı - bulguları destekleyen belgeler ve veriler"""

    EVIDENCE_TYPES = [
        ("document", "Doküman"),
        ("screenshot", "Ekran Görüntüsü"),
        ("report", "Rapor"),
        ("email", "E-posta"),
        ("database_query", "Veritabanı Sorgusu"),
        ("interview", "Görüşme Notu"),
        ("photo", "Fotoğraf"),
        ("other", "Diğer"),
    ]

    finding = models.ForeignKey(
        AuditFinding,
        on_delete=models.CASCADE,
        related_name="evidences",
        verbose_name="Bulgu",
    )
    evidence_type = models.CharField(
        max_length=20, choices=EVIDENCE_TYPES, verbose_name="Kanıt Tipi"
    )
    title = models.CharField(max_length=200, verbose_name="Kanıt Başlığı")
    description = models.TextField(blank=True, verbose_name="Açıklama")

    # Dosya
    file = models.FileField(
        upload_to="audit_evidence/", null=True, blank=True, verbose_name="Kanıt Dosyası"
    )

    # Metadata
    source = models.CharField(max_length=200, blank=True, verbose_name="Kaynak")
    collection_date = models.DateField(verbose_name="Toplama Tarihi")
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="collected_evidence",
    )

    # Güvenilirlik
    reliability_score = models.IntegerField(
        default=5, verbose_name="Güvenilirlik (1-10)"
    )
    notes = models.TextField(blank=True, verbose_name="Notlar")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Denetim Kanıtı"
        verbose_name_plural = "Denetim Kanıtları"
        ordering = ["-collection_date"]

    def __str__(self):
        return f"{self.title} - {self.get_evidence_type_display()}"


class CostVarianceAnalysis(models.Model):
    """Maliyet varyans analizi - bütçe vs gerçekleşen"""

    cost_center = models.ForeignKey(
        CostCenter, on_delete=models.CASCADE, related_name="variance_analyses"
    )
    analysis_period = models.CharField(
        max_length=20, verbose_name="Analiz Dönemi"
    )  # 2024-01, 2024-Q1

    # Bütçe
    budgeted_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Bütçelenen"
    )
    actual_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Gerçekleşen"
    )

    # Varyans
    variance_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Varyans Tutarı"
    )
    variance_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Varyans %"
    )
    variance_type = models.CharField(
        max_length=20, verbose_name="Varyans Tipi"
    )  # favorable, unfavorable

    # Analiz
    cause_analysis = models.TextField(blank=True, verbose_name="Sebep Analizi")
    corrective_actions = models.JSONField(
        default=list, blank=True, verbose_name="Düzeltici Aksiyonlar"
    )

    analyzed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "accounting"
        verbose_name = "Varyans Analizi"
        verbose_name_plural = "Varyans Analizleri"
        ordering = ["-analysis_period"]

    def save(self, *args, **kwargs):
        # Varyansı otomatik hesapla
        self.variance_amount = self.actual_amount - self.budgeted_amount

        if self.budgeted_amount != 0:
            self.variance_percentage = (
                self.variance_amount / self.budgeted_amount
            ) * 100
        else:
            self.variance_percentage = 0

        # Favorable/Unfavorable belirleme (maliyet için unfavorable = fazla harcama)
        self.variance_type = "favorable" if self.variance_amount < 0 else "unfavorable"

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.cost_center.name} - {self.analysis_period} ({self.variance_type})"
        )
