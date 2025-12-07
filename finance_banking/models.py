from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


# ============================================================================
# FINANCE BANKING MODELS
# ============================================================================


class BankTransaction(models.Model):
    """Banka işlemleri"""

    TRANSACTION_TYPES = [
        ("DEPOSIT", _("Para Yatırma")),
        ("WITHDRAWAL", _("Para Çekme")),
        ("TRANSFER", _("Transfer")),
        ("FEE", _("Banka Ücreti")),
        ("INTEREST", _("Faiz")),
        ("CHECK", _("Çek")),
        ("ATM", _("ATM İşlemi")),
        ("POS", _("POS İşlemi")),
        ("OTHER", _("Diğer")),
    ]

    STATUS_CHOICES = [
        ("PENDING", _("Beklemede")),
        ("COMPLETED", _("Tamamlandı")),
        ("FAILED", _("Başarısız")),
        ("CANCELLED", _("İptal Edildi")),
    ]

    bank_account = models.ForeignKey(
        "finance.BankAccount",
        on_delete=models.CASCADE,
        related_name="banking_transactions",
        verbose_name=_("Banka Hesabı"),
    )

    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, verbose_name=_("İşlem Tipi")
    )
    transaction_date = models.DateTimeField(verbose_name=_("İşlem Tarihi"))
    value_date = models.DateField(verbose_name=_("Valör Tarihi"))

    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Tutar")
    )
    balance_after = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("İşlem Sonrası Bakiye")
    )

    reference_number = models.CharField(
        max_length=100, blank=True, verbose_name=_("Referans Numarası")
    )
    description = models.TextField(verbose_name=_("Açıklama"))

    # Taraflar
    sender_name = models.CharField(
        max_length=200, blank=True, verbose_name=_("Gönderen")
    )
    sender_account = models.CharField(
        max_length=50, blank=True, verbose_name=_("Gönderen Hesap")
    )
    recipient_name = models.CharField(
        max_length=200, blank=True, verbose_name=_("Alıcı")
    )
    recipient_account = models.CharField(
        max_length=50, blank=True, verbose_name=_("Alıcı Hesap")
    )

    # Durum
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="COMPLETED",
        verbose_name=_("Durum"),
    )

    # Mutabakat
    is_reconciled = models.BooleanField(default=False, verbose_name=_("Mutabık"))
    reconciliation_date = models.DateField(
        null=True, blank=True, verbose_name=_("Mutabakat Tarihi")
    )

    # Kategori
    category = models.ForeignKey(
        "finance.TransactionCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Kategori"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Banka İşlemi")
        verbose_name_plural = _("Banka İşlemleri")
        ordering = ["-transaction_date"]
        app_label = "finance_banking"

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} TL ({self.transaction_date})"


class BankStatement(models.Model):
    """Banka ekstreleri"""

    bank_account = models.ForeignKey(
        "finance.BankAccount",
        on_delete=models.CASCADE,
        related_name="statements",
        verbose_name=_("Banka Hesabı"),
    )

    statement_date = models.DateField(verbose_name=_("Ekstre Tarihi"))
    period_start = models.DateField(verbose_name=_("Dönem Başlangıç"))
    period_end = models.DateField(verbose_name=_("Dönem Bitiş"))

    # Bakiyeler
    opening_balance = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Açılış Bakiyesi")
    )
    closing_balance = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Kapanış Bakiyesi")
    )

    # İşlemler
    total_deposits = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Gelen"),
    )
    total_withdrawals = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Toplam Giden"),
    )
    transaction_count = models.IntegerField(default=0, verbose_name=_("İşlem Sayısı"))

    # Dosya
    statement_file = models.FileField(
        upload_to="bank_statements/",
        null=True,
        blank=True,
        verbose_name=_("Ekstre Dosyası"),
    )

    # Mutabakat
    is_reconciled = models.BooleanField(default=False, verbose_name=_("Mutabık"))
    reconciliation = models.ForeignKey(
        "finance.Reconciliation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Mutabakat"),
    )

    notes = models.TextField(blank=True, verbose_name=_("Notlar"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Banka Ekstresi")
        verbose_name_plural = _("Banka Ekstreleri")
        ordering = ["-statement_date"]
        app_label = "finance_banking"
        unique_together = [["bank_account", "statement_date"]]

    def __str__(self):
        return f"{self.bank_account} - {self.statement_date}"


class PaymentMethod(models.Model):
    """Ödeme yöntemleri"""

    METHOD_TYPES = [
        ("CASH", _("Nakit")),
        ("BANK_TRANSFER", _("Banka Havalesi")),
        ("CREDIT_CARD", _("Kredi Kartı")),
        ("DEBIT_CARD", _("Banka Kartı")),
        ("CHECK", _("Çek")),
        ("MOBILE_PAYMENT", _("Mobil Ödeme")),
        ("ONLINE_PAYMENT", _("Online Ödeme")),
        ("OTHER", _("Diğer")),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Yöntem Adı"))
    method_type = models.CharField(
        max_length=20, choices=METHOD_TYPES, verbose_name=_("Yöntem Tipi")
    )

    # İlişkili hesap
    bank_account = models.ForeignKey(
        "finance.BankAccount",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Banka Hesabı"),
    )

    # Detaylar
    description = models.TextField(blank=True, verbose_name=_("Açıklama"))
    fees = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("İşlem Ücreti (%)"),
    )

    # Limitler
    min_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimum Tutar"),
    )
    max_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maximum Tutar"),
    )

    # Durum
    is_active = models.BooleanField(default=True, verbose_name=_("Aktif"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Ödeme Yöntemi")
        verbose_name_plural = _("Ödeme Yöntemleri")
        ordering = ["name"]
        app_label = "finance_banking"

    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"


class BankTransfer(models.Model):
    """Banka transferleri - havale ve EFT"""

    TRANSFER_TYPES = [
        ("INTERNAL", _("Hesaplar Arası")),
        ("DOMESTIC", _("Yurtiçi (EFT)")),
        ("FAST", _("Hızlı (FAST)")),
        ("INTERNATIONAL", _("Yurtdışı (SWIFT)")),
    ]

    STATUS_CHOICES = [
        ("PENDING", _("Beklemede")),
        ("PROCESSING", _("İşleniyor")),
        ("COMPLETED", _("Tamamlandı")),
        ("FAILED", _("Başarısız")),
        ("CANCELLED", _("İptal Edildi")),
    ]

    transfer_type = models.CharField(
        max_length=20, choices=TRANSFER_TYPES, verbose_name=_("Transfer Tipi")
    )

    # Gönderen
    sender_account = models.ForeignKey(
        "finance.BankAccount",
        on_delete=models.PROTECT,
        related_name="sent_transfers",
        verbose_name=_("Gönderen Hesap"),
    )

    # Alıcı
    recipient_name = models.CharField(max_length=200, verbose_name=_("Alıcı Adı"))
    recipient_iban = models.CharField(max_length=34, verbose_name=_("Alıcı IBAN"))
    recipient_bank = models.CharField(max_length=100, verbose_name=_("Alıcı Bankası"))

    # Tutar
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Tutar")
    )
    currency = models.CharField(
        max_length=3, default="TRY", verbose_name=_("Para Birimi")
    )

    # Transfer fee
    transfer_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Transfer Ücreti"),
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Toplam Tutar")
    )

    # Açıklama
    description = models.TextField(verbose_name=_("Açıklama"))

    # Tarihler
    transfer_date = models.DateField(verbose_name=_("Transfer Tarihi"))
    value_date = models.DateField(verbose_name=_("Valör Tarihi"))

    # Durum ve referans
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name=_("Durum"),
    )
    reference_number = models.CharField(
        max_length=100, unique=True, verbose_name=_("Referans Numarası")
    )

    # İlişkili işlem
    bank_transaction = models.OneToOneField(
        BankTransaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Banka İşlemi"),
    )

    # Onay
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiated_transfers",
        verbose_name=_("Başlatan"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_transfers",
        verbose_name=_("Onaylayan"),
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Onay Tarihi")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Banka Transferi")
        verbose_name_plural = _("Banka Transferleri")
        ordering = ["-transfer_date"]
        app_label = "finance_banking"

    def __str__(self):
        return f"{self.recipient_name} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        # Toplam tutarı hesapla
        self.total_amount = self.amount + self.transfer_fee
        super().save(*args, **kwargs)


class CheckTransaction(models.Model):
    """Çek işlemleri"""

    CHECK_TYPES = [
        ("ISSUED", _("Verilen Çek")),
        ("RECEIVED", _("Alınan Çek")),
    ]

    STATUS_CHOICES = [
        ("ISSUED", _("Keşide Edildi")),
        ("DEPOSITED", _("Bankaya Verildi")),
        ("CLEARED", _("Tahsil Edildi")),
        ("BOUNCED", _("Karşılıksız")),
        ("CANCELLED", _("İptal Edildi")),
    ]

    check_type = models.CharField(
        max_length=20, choices=CHECK_TYPES, verbose_name=_("Çek Tipi")
    )
    check_number = models.CharField(max_length=50, verbose_name=_("Çek Numarası"))

    # Hesap
    bank_account = models.ForeignKey(
        "finance.BankAccount", on_delete=models.PROTECT, verbose_name=_("Banka Hesabı")
    )

    # Taraflar
    drawer_name = models.CharField(max_length=200, verbose_name=_("Keşideci Adı"))
    payee_name = models.CharField(max_length=200, verbose_name=_("Lehtar Adı"))

    # Tutar ve tarih
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Tutar")
    )
    issue_date = models.DateField(verbose_name=_("Keşide Tarihi"))
    due_date = models.DateField(verbose_name=_("Vade Tarihi"))

    # Durum
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ISSUED", verbose_name=_("Durum")
    )
    cleared_date = models.DateField(
        null=True, blank=True, verbose_name=_("Tahsil Tarihi")
    )

    # İlişkili işlem
    bank_transaction = models.OneToOneField(
        BankTransaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Banka İşlemi"),
    )

    notes = models.TextField(blank=True, verbose_name=_("Notlar"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Çek İşlemi")
        verbose_name_plural = _("Çek İşlemleri")
        ordering = ["-due_date"]
        app_label = "finance_banking"
        unique_together = [["check_number", "bank_account"]]

    def __str__(self):
        return f"{self.check_number} - {self.amount} TL"


class DirectDebit(models.Model):
    """Otomatik ödeme talimatları"""

    bank_account = models.ForeignKey(
        "finance.BankAccount",
        on_delete=models.CASCADE,
        related_name="direct_debits",
        verbose_name=_("Banka Hesabı"),
    )

    payee_name = models.CharField(max_length=200, verbose_name=_("Alıcı Adı"))
    payee_account = models.CharField(max_length=50, verbose_name=_("Alıcı Hesap"))

    # Tutar
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Tutar")
    )
    is_fixed_amount = models.BooleanField(default=True, verbose_name=_("Sabit Tutar"))
    max_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maksimum Tutar"),
    )

    # Zamanlama
    start_date = models.DateField(verbose_name=_("Başlangıç Tarihi"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Bitiş Tarihi"))
    frequency = models.CharField(
        max_length=20,
        choices=[
            ("monthly", _("Aylık")),
            ("quarterly", _("3 Aylık")),
            ("annually", _("Yıllık")),
        ],
        default="monthly",
        verbose_name=_("Sıklık"),
    )

    # Durum
    is_active = models.BooleanField(default=True, verbose_name=_("Aktif"))
    last_execution_date = models.DateField(
        null=True, blank=True, verbose_name=_("Son Çalıştırma")
    )
    next_execution_date = models.DateField(verbose_name=_("Sonraki Çalıştırma"))

    description = models.TextField(verbose_name=_("Açıklama"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Otomatik Ödeme")
        verbose_name_plural = _("Otomatik Ödemeler")
        ordering = ["next_execution_date"]
        app_label = "finance_banking"

    def __str__(self):
        return f"{self.payee_name} - {self.amount} TL"
