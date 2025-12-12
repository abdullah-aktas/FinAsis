# accounts/models.py içine eklenecek rol sistemi modelleri

from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
import uuid


class UserRole(models.Model):
    """Kullanıcı rolleri sistemi"""

    ROLE_CHOICES = [
        ("super_admin", "Süper Yönetici"),
        ("admin", "Sistem Yöneticisi"),
        ("finance_manager", "Finans Müdürü"),
        ("kobi_owner", "KOBİ Sahibi"),
        ("kobi_employee", "KOBİ Çalışanı"),
        ("accountant", "Muhasebeci"),
        ("financial_advisor", "Mali Müşavir"),
        ("auditor", "Denetçi"),
        ("teacher", "Eğitimci"),
        ("student", "Öğrenci"),
        ("player", "Oyuncu"),
        ("viewer", "Görüntüleyici"),
    ]

    name = models.CharField(
        max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name="Rol Adı"
    )
    display_name = models.CharField(max_length=100, verbose_name="Görünen Ad")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    hierarchy_level = models.IntegerField(
        default=10,
        help_text="Düşük değer = Yüksek yetki (0=Süper Admin, 10=En düşük)",
        verbose_name="Hiyerarşi Seviyesi",
    )

    # İzinler
    can_manage_users = models.BooleanField(
        default=False, verbose_name="Kullanıcı Yönetimi"
    )
    can_manage_companies = models.BooleanField(
        default=False, verbose_name="Şirket Yönetimi"
    )
    can_view_all_finances = models.BooleanField(
        default=False, verbose_name="Tüm Mali Verileri Görme"
    )
    can_edit_finances = models.BooleanField(
        default=False, verbose_name="Mali Düzenleme"
    )
    can_approve_transactions = models.BooleanField(
        default=False, verbose_name="İşlem Onaylama"
    )
    can_generate_reports = models.BooleanField(
        default=False, verbose_name="Rapor Oluşturma"
    )
    can_access_ai = models.BooleanField(default=True, verbose_name="AI Asistan Erişimi")
    can_use_education = models.BooleanField(default=True, verbose_name="Eğitim Modülü")
    can_play_games = models.BooleanField(default=True, verbose_name="Oyun Modülü")
    can_use_blockchain = models.BooleanField(
        default=False, verbose_name="Blockchain Modülü"
    )

    # Limit ayarları
    max_companies = models.IntegerField(
        default=1,
        help_text="Bu role sahip kullanıcı kaç şirket yönetebilir (-1=sınırsız)",
        verbose_name="Maksimum Şirket Sayısı",
    )
    max_transactions_per_month = models.IntegerField(
        default=100,
        help_text="Aylık maksimum işlem sayısı (-1=sınırsız)",
        verbose_name="Aylık Max İşlem",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı Rolü"
        verbose_name_plural = "Kullanıcı Rolleri"
        ordering = ["hierarchy_level", "name"]

    def __str__(self):
        return self.display_name

    def clean(self):
        # Süper admin kontrolü
        if self.name == "super_admin" and self.hierarchy_level != 0:
            raise ValidationError("Süper admin hiyerarşi seviyesi 0 olmalıdır.")


class SubscriptionPlan(models.Model):
    """Abonelik planları"""

    PLAN_TYPES = [
        ("free", "Ücretsiz"),
        ("basic", "Temel"),
        ("professional", "Profesyonel"),
        ("enterprise", "Kurumsal"),
        ("custom", "Özel"),
    ]

    name = models.CharField(
        max_length=50, choices=PLAN_TYPES, unique=True, verbose_name="Plan Adı"
    )
    display_name = models.CharField(max_length=100, verbose_name="Görünen Ad")
    description = models.TextField(verbose_name="Plan Açıklaması")
    price_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Aylık Ücret (₺)",
    )
    price_yearly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Yıllık Ücret (₺)",
    )

    # Plan Limitleri
    max_users = models.IntegerField(
        default=1,
        help_text="Plan kapsamındaki maksimum kullanıcı sayısı",
        verbose_name="Max Kullanıcı",
    )
    max_companies = models.IntegerField(default=1, verbose_name="Max Şirket")
    max_transactions = models.IntegerField(default=100, verbose_name="Aylık Max İşlem")
    storage_gb = models.IntegerField(default=1, verbose_name="Depolama (GB)")

    # Özellik Erişimleri
    has_accounting = models.BooleanField(default=True, verbose_name="Muhasebe Modülü")
    has_finance = models.BooleanField(default=False, verbose_name="Finans Modülü")
    has_ai_assistant = models.BooleanField(default=False, verbose_name="AI Asistan")
    has_education = models.BooleanField(default=True, verbose_name="Eğitim")
    has_games = models.BooleanField(default=True, verbose_name="Oyunlar")
    has_blockchain = models.BooleanField(default=False, verbose_name="Blockchain")
    has_api_access = models.BooleanField(default=False, verbose_name="API Erişimi")
    has_priority_support = models.BooleanField(
        default=False, verbose_name="Öncelikli Destek"
    )

    # Plan Durumu
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_popular = models.BooleanField(default=False, verbose_name="Popüler Plan")
    order = models.IntegerField(default=0, verbose_name="Sıralama")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Abonelik Planı"
        verbose_name_plural = "Abonelik Planları"
        ordering = ["order", "price_monthly"]

    def __str__(self):
        return f"{self.display_name} - ₺{self.price_monthly}/ay"

    @property
    def yearly_discount(self):
        """Yıllık planda indirim yüzdesi"""
        if self.price_monthly > 0 and self.price_yearly > 0:
            monthly_total = self.price_monthly * 12
            return round(((monthly_total - self.price_yearly) / monthly_total) * 100)
        return 0


class UserSubscription(models.Model):
    """Kullanıcı abonelikleri"""

    PAYMENT_STATUS = [
        ("pending", "Beklemede"),
        ("active", "Aktif"),
        ("cancelled", "İptal Edildi"),
        ("expired", "Süresi Doldu"),
        ("suspended", "Askıya Alındı"),
    ]

    BILLING_PERIOD = [
        ("monthly", "Aylık"),
        ("yearly", "Yıllık"),
        ("lifetime", "Yaşam Boyu"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "accounts.CustomUser",  # Mevcut CustomUser modeli
        on_delete=models.CASCADE,
        related_name="role_subscription",  # Çakışmayı önlemek için değiştirdim
        verbose_name="Kullanıcı",
    )
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.PROTECT, verbose_name="Abonelik Planı"
    )
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default="pending", verbose_name="Durum"
    )
    billing_period = models.CharField(
        max_length=20,
        choices=BILLING_PERIOD,
        default="monthly",
        verbose_name="Faturalama Dönemi",
    )

    # Tarihler
    start_date = models.DateTimeField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateTimeField(verbose_name="Bitiş Tarihi")
    next_billing_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Sonraki Faturalama"
    )

    # Ödeme Bilgileri
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Ödenen Tutar",
    )
    currency = models.CharField(max_length=3, default="TRY", verbose_name="Para Birimi")

    # Kullanım İstatistikleri
    current_month_transactions = models.IntegerField(
        default=0, verbose_name="Bu Ay İşlem Sayısı"
    )
    total_transactions = models.IntegerField(default=0, verbose_name="Toplam İşlem")
    storage_used_mb = models.IntegerField(
        default=0, verbose_name="Kullanılan Depolama (MB)"
    )

    # Metadata
    auto_renew = models.BooleanField(default=True, verbose_name="Otomatik Yenileme")
    notes = models.TextField(blank=True, verbose_name="Notlar")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı Aboneliği"
        verbose_name_plural = "Kullanıcı Abonelikleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.plan.display_name}"

    @property
    def is_active(self):
        """Abonelik aktif mi?"""
        from django.utils import timezone

        return self.status == "active" and self.end_date > timezone.now()

    @property
    def days_remaining(self):
        """Kalan gün sayısı"""
        from django.utils import timezone

        if self.end_date:
            delta = self.end_date - timezone.now()
            return max(0, delta.days)
        return 0

    def can_perform_action(self, action_type):
        """Belirli bir eylemi gerçekleştirebilir mi?"""
        if not self.is_active:
            return False

        # İşlem sayısı kontrolü
        if action_type == "transaction":
            return (
                self.plan.max_transactions == -1
                or self.current_month_transactions < self.plan.max_transactions
            )

        return True


class RoleBasedUserProfile(models.Model):
    """Genişletilmiş kullanıcı profili (Role sistemi için)"""

    user = models.OneToOneField(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="role_profile",
        verbose_name="Kullanıcı",
    )
    role = models.ForeignKey(
        UserRole, on_delete=models.PROTECT, verbose_name="Kullanıcı Rolü"
    )

    # Kişisel Bilgiler
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    tc_no = models.CharField(max_length=11, blank=True, verbose_name="TC Kimlik No")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Doğum Tarihi")

    # Profesyonel Bilgiler
    company_name = models.CharField(
        max_length=200, blank=True, verbose_name="Şirket Adı"
    )
    job_title = models.CharField(max_length=100, blank=True, verbose_name="İş Unvanı")
    license_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Mali müşavir ruhsat numarası vb.",
        verbose_name="Ruhsat/Lisans No",
    )

    # Hesap Ayarları
    timezone = models.CharField(
        max_length=50, default="Europe/Istanbul", verbose_name="Saat Dilimi"
    )
    language = models.CharField(
        max_length=10,
        default="tr",
        choices=[("tr", "Türkçe"), ("en", "English")],
        verbose_name="Dil",
    )

    # Güvenlik
    two_factor_enabled = models.BooleanField(
        default=False, verbose_name="İki Faktörlü Doğrulama"
    )
    last_password_change = models.DateTimeField(
        auto_now_add=True, verbose_name="Son Şifre Değişikliği"
    )
    login_attempts = models.IntegerField(
        default=0, verbose_name="Başarısız Giriş Denemeleri"
    )
    is_locked = models.BooleanField(default=False, verbose_name="Hesap Kilitli")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rol Tabanlı Kullanıcı Profili"
        verbose_name_plural = "Rol Tabanlı Kullanıcı Profilleri"

    def __str__(self):
        return f"{self.user.username} - {self.role.display_name}"

    def can_manage_user(self, target_user):
        """Bu kullanıcı hedef kullanıcıyı yönetebilir mi?"""
        try:
            target_profile = target_user.profile
            return (
                self.role.can_manage_users
                and self.role.hierarchy_level < target_profile.role.hierarchy_level
            )
        except (AttributeError, Exception):
            return False

    def get_accessible_modules(self):
        """Erişebileceği modüllerin listesi"""
        modules = []

        if self.role.can_view_all_finances or self.role.can_edit_finances:
            modules.append("accounting")

        if self.role.can_view_all_finances:
            modules.append("finance")

        if self.role.can_access_ai:
            modules.append("ai_assistant")

        if self.role.can_use_education:
            modules.append("education")

        if self.role.can_play_games:
            modules.append("games")

        if self.role.can_use_blockchain:
            modules.append("blockchain")

        return modules
