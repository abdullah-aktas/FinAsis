from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import Group


class Plan(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    audience = models.CharField(
        max_length=10,
        choices=[("sme", "KOBİ"), ("edu", "Eğitim"), ("games", "Oyuncu")],
        default="sme",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EnterpriseInquiry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.plan.name if self.plan else "Plan belirtilmedi"
        return f"Teklif Talebi: {self.name} → {target}"


class Price(models.Model):
    PERIOD_CHOICES = [
        ("month", "Aylık"),
        ("year", "Yıllık"),
    ]
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="prices")
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="month")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="TRY")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("plan", "period", "currency")

    def __str__(self):
        return f"{self.plan.name} {self.period} {self.amount} {self.currency}"


class Module(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PlanModule(models.Model):
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name="plan_modules"
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("plan", "module")


class PlanGroup(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="plan_groups")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("plan", "group")


class SubscriptionStatus(models.TextChoices):
    TRIAL = "trial", "Trial"
    ACTIVE = "active", "Active"
    PAST_DUE = "past_due", "Past Due"
    CANCELED = "canceled", "Canceled"


class SubscriptionProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="billing_profile",
    )
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIAL,
    )
    current_period_end = models.DateTimeField(null=True, blank=True)
    provider = models.CharField(max_length=20, default="paytr")
    external_customer_id = models.CharField(max_length=100, blank=True, default="")
    external_subscription_id = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    METHOD_CHOICES = [
        ("paytr", "PayTR"),
        ("bank", "Banka Havale/EFT"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="billing_transactions",
    )
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="TRY")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, default="initiated")
    external_id = models.CharField(max_length=200, blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class BankTransfer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="TRY")
    reference_code = models.CharField(max_length=20, unique=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def confirm(self):
        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=["is_confirmed", "confirmed_at"])


# ============================================================================
# GENİŞLETİLMİŞ FATURALANDIRMA SİSTEMİ
# ============================================================================


class Invoice(models.Model):
    """Abonelik faturaları"""

    STATUS_CHOICES = [
        ("DRAFT", "Taslak"),
        ("SENT", "Gönderildi"),
        ("PAID", "Ödendi"),
        ("OVERDUE", "Vadesi Geçti"),
        ("CANCELLED", "İptal Edildi"),
        ("REFUNDED", "İade Edildi"),
    ]

    subscription = models.ForeignKey(
        SubscriptionProfile,
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name="Abonelik",
    )

    # Fatura bilgisi
    invoice_number = models.CharField(
        max_length=50, unique=True, verbose_name="Fatura No"
    )
    invoice_date = models.DateField(verbose_name="Fatura Tarihi")
    due_date = models.DateField(verbose_name="Vade Tarihi")

    # Dönem
    billing_period_start = models.DateField(verbose_name="Dönem Başlangıç")
    billing_period_end = models.DateField(verbose_name="Dönem Bitiş")

    # Tutarlar
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Ara Toplam"
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Vergi"
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="İndirim"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Toplam"
    )

    # Kalemler
    line_items = models.JSONField(default=list, verbose_name="Fatura Kalemleri")

    # Durum
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="DRAFT", verbose_name="Durum"
    )

    # Ödeme
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Ödeme Tarihi")
    payment_method = models.CharField(
        max_length=50, blank=True, verbose_name="Ödeme Yöntemi"
    )
    transaction = models.OneToOneField(
        Transaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="İşlem",
    )

    # Notlar
    notes = models.TextField(blank=True, verbose_name="Notlar")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturalar"
        ordering = ["-invoice_date"]

    def __str__(self):
        return f"{self.invoice_number} - {self.total_amount} {self.subscription.plan.name if self.subscription.plan else ''}"


class PaymentGateway(models.Model):
    """Ödeme gateway yapılandırması"""

    GATEWAY_TYPES = [
        ("PAYTR", "PayTR"),
        ("IYZICO", "Iyzico"),
        ("STRIPE", "Stripe"),
        ("PAYPAL", "PayPal"),
        ("BANK", "Banka"),
    ]

    name = models.CharField(max_length=100, verbose_name="Gateway Adı")
    gateway_type = models.CharField(
        max_length=20, choices=GATEWAY_TYPES, verbose_name="Gateway Tipi"
    )

    # API ayarları
    api_key = models.CharField(max_length=200, verbose_name="API Key")
    api_secret = models.CharField(max_length=200, verbose_name="API Secret")
    merchant_id = models.CharField(
        max_length=100, blank=True, verbose_name="Merchant ID"
    )

    # Endpoint
    base_url = models.URLField(verbose_name="Base URL")
    webhook_url = models.URLField(blank=True, verbose_name="Webhook URL")

    # Ayarlar
    is_test_mode = models.BooleanField(default=True, verbose_name="Test Modu")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    # İstatistikler
    total_transactions = models.IntegerField(default=0, verbose_name="Toplam İşlem")
    successful_transactions = models.IntegerField(
        default=0, verbose_name="Başarılı İşlem"
    )
    failed_transactions = models.IntegerField(default=0, verbose_name="Başarısız İşlem")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ödeme Gateway"
        verbose_name_plural = "Ödeme Gatewayleri"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({'Test' if self.is_test_mode else 'Prod'})"


class Discount(models.Model):
    """İndirim kuponları ve promosyonlar"""

    DISCOUNT_TYPES = [
        ("PERCENTAGE", "Yüzde"),
        ("FIXED", "Sabit Tutar"),
        ("FREE_TRIAL", "Ücretsiz Deneme"),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="İndirim Kodu")
    name = models.CharField(max_length=200, verbose_name="İndirim Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")

    # İndirim tipi
    discount_type = models.CharField(
        max_length=20, choices=DISCOUNT_TYPES, verbose_name="İndirim Tipi"
    )
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="İndirim Değeri"
    )

    # Geçerlilik
    valid_from = models.DateTimeField(verbose_name="Geçerlilik Başlangıcı")
    valid_until = models.DateTimeField(verbose_name="Geçerlilik Bitişi")

    # Kullanım limitleri
    max_uses = models.IntegerField(
        null=True, blank=True, verbose_name="Maksimum Kullanım"
    )
    max_uses_per_user = models.IntegerField(
        default=1, verbose_name="Kullanıcı Başına Maks. Kullanım"
    )

    # İstatistikler
    times_used = models.IntegerField(default=0, verbose_name="Kullanım Sayısı")

    # Hedef planlar
    applicable_plans = models.ManyToManyField(
        Plan, blank=True, related_name="discounts", verbose_name="Geçerli Planlar"
    )

    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Oluşturan"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "İndirim Kuponu"
        verbose_name_plural = "İndirim Kuponları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'PERCENTAGE' else ' TL'}"

    def is_valid(self):
        """Kuponun geçerli olup olmadığını kontrol et"""
        from django.utils import timezone

        now = timezone.now()

        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses and self.times_used >= self.max_uses:
            return False

        return True


class DiscountUsage(models.Model):
    """İndirim kullanım kayıtları"""

    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name="usages",
        verbose_name="İndirim",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Kullanıcı"
    )
    subscription = models.ForeignKey(
        SubscriptionProfile, on_delete=models.CASCADE, verbose_name="Abonelik"
    )

    # İndirim detayı
    original_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Orijinal Tutar"
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="İndirim Tutarı"
    )
    final_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Final Tutar"
    )

    used_at = models.DateTimeField(auto_now_add=True, verbose_name="Kullanım Zamanı")

    class Meta:
        verbose_name = "İndirim Kullanımı"
        verbose_name_plural = "İndirim Kullanımları"
        ordering = ["-used_at"]

    def __str__(self):
        return f"{self.discount.code} - {self.user.username}"


class PaymentAttempt(models.Model):
    """Ödeme denemeleri - başarılı/başarısız tracking"""

    STATUS_CHOICES = [
        ("INITIATED", "Başlatıldı"),
        ("PROCESSING", "İşleniyor"),
        ("SUCCESS", "Başarılı"),
        ("FAILED", "Başarısız"),
        ("CANCELLED", "İptal Edildi"),
    ]

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="İşlem",
    )

    # Deneme bilgisi
    attempt_number = models.IntegerField(default=1, verbose_name="Deneme Numarası")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Durum"
    )

    # Gateway
    gateway = models.ForeignKey(
        "PaymentGateway",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Gateway",
    )

    # İstek/Yanıt
    request_data = models.JSONField(default=dict, verbose_name="İstek Verisi")
    response_data = models.JSONField(default=dict, verbose_name="Yanıt Verisi")
    response_code = models.CharField(
        max_length=50, blank=True, verbose_name="Yanıt Kodu"
    )

    # Hata
    error_message = models.TextField(blank=True, verbose_name="Hata Mesajı")

    # Metadata
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP Adresi"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")

    attempted_at = models.DateTimeField(auto_now_add=True, verbose_name="Deneme Zamanı")

    class Meta:
        verbose_name = "Ödeme Denemesi"
        verbose_name_plural = "Ödeme Denemeleri"
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"{self.transaction.id} - Attempt #{self.attempt_number} ({self.status})"
