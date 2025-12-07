from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager
from accounting.models import Company


class CustomUserQuerySet(models.QuerySet["CustomUser"]):
    """Kullanıcı listelerinde N+1'ı önlemek için ilişkileri hazırla."""

    def with_related(self):
        return self.select_related("company").prefetch_related(
            "groups", "user_permissions"
        )


# from_queryset ile dinamik oluşturulan manager'lar migration sırasında serileştirilemediği
# için adlandırılmış bir sınıf olarak tanımlıyoruz.
class CustomUserManager(UserManager):
    def get_queryset(self):
        return CustomUserQuerySet(self.model, using=self._db)

    # Manager üzerinden de aynı API'yi sunalım
    def with_related(self):
        return self.get_queryset().with_related()


class UserType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    default_subscription = models.ForeignKey(
        "SubscriptionType", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name


class SubscriptionType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    audience = models.CharField(
        max_length=20,
        choices=[
            ("sme", "KOBİ"),
            ("edu_student", "Öğrenci"),
            ("edu_teacher", "Öğretmen"),
            ("edu_campus", "Kampüs/Okul"),
        ],
        default="sme",
    )
    period_options = models.CharField(
        max_length=20,
        choices=[
            ("monthly", "Aylık"),
            ("yearly", "Yıllık"),
            ("monthly_yearly", "Aylık/Yıllık"),
        ],
        default="monthly",
    )
    monthly_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    yearly_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    user_limit = models.IntegerField(null=True, blank=True)  # None/sınırsız
    features = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    role = models.CharField(
        max_length=50,
        choices=[("admin", "Yönetici"), ("staff", "Çalışan"), ("viewer", "İzleyici")],
        default="staff",
    )
    user_type = models.ForeignKey(
        UserType, on_delete=models.SET_NULL, null=True, blank=True
    )
    # Varsayılan manager: adlandırılmış CustomUserManager kullan
    objects = CustomUserManager()
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class Achievement(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name="Şirket",
    )
    title = models.CharField(max_length=100, verbose_name="Başlık")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    icon = models.CharField(
        max_length=50, default="bi-trophy", verbose_name="İkon (Bootstrap)"
    )
    date_earned = models.DateField(auto_now_add=True, verbose_name="Kazanılma Tarihi")

    def __str__(self):
        return f"{self.title} ({self.company})"

    class Meta:
        verbose_name = "Başarım"
        verbose_name_plural = "Başarımlar"
        ordering = ["-date_earned"]


class UserSettings(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name="Kullanıcı",
    )
    email_notifications = models.BooleanField(
        default=True, verbose_name="E-posta Bildirimleri"
    )
    dark_mode = models.BooleanField(default=False, verbose_name="Koyu Tema Tercihi")

    def __str__(self):
        return f"Ayarlar: {self.user.username}"

    class Meta:
        verbose_name = "Kullanıcı Ayarları"
        verbose_name_plural = "Kullanıcı Ayarları"


class Subscription(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="subscription"
    )
    subscription_type = models.ForeignKey(
        SubscriptionType, on_delete=models.SET_NULL, null=True
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"


class SubscriptionLog(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="subscription_logs"
    )
    old_subscription = models.ForeignKey(
        SubscriptionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="old_logs",
    )
    new_subscription = models.ForeignKey(
        SubscriptionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="new_logs",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.old_subscription} → {self.new_subscription} ({self.changed_at:%Y-%m-%d %H:%M})"


# Create your models here.

# Not: Invoice modeli accounting uygulamasında tanımlı ve Company ile ilişkilidir.


# ============================================================================
# GENİŞLETİLMİŞ KULLANICI YÖNETİMİ
# ============================================================================


class UserProfile(models.Model):
    """Genişletilmiş kullanıcı profili"""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Kullanıcı",
    )

    # Kişisel bilgiler
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    bio = models.TextField(blank=True, verbose_name="Hakkında")
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, verbose_name="Profil Fotoğrafı"
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")

    # Adres
    address = models.TextField(blank=True, verbose_name="Adres")
    city = models.CharField(max_length=100, blank=True, verbose_name="Şehir")
    country = models.CharField(max_length=100, default="Turkey", verbose_name="Ülke")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="Posta Kodu")

    # Sosyal medya
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter")
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    website_url = models.URLField(blank=True, verbose_name="Website")

    # İstatistikler
    profile_views = models.IntegerField(default=0, verbose_name="Profil Görüntüleme")
    last_profile_update = models.DateTimeField(
        auto_now=True, verbose_name="Son Güncelleme"
    )

    # Tercihler
    language = models.CharField(
        max_length=10,
        choices=[("tr", "Türkçe"), ("en", "English"), ("de", "Deutsch")],
        default="tr",
        verbose_name="Dil",
    )
    timezone = models.CharField(
        max_length=50, default="Europe/Istanbul", verbose_name="Zaman Dilimi"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"

    def __str__(self):
        return f"{self.user.username} - Profile"


class UserActivity(models.Model):
    """Kullanıcı aktivite kaydı"""

    ACTIVITY_TYPES = [
        ("login", "Giriş Yaptı"),
        ("logout", "Çıkış Yaptı"),
        ("profile_update", "Profil Güncelledi"),
        ("password_change", "Şifre Değiştirdi"),
        ("document_upload", "Doküman Yükledi"),
        ("invoice_create", "Fatura Oluşturdu"),
        ("report_generate", "Rapor Oluşturdu"),
        ("settings_change", "Ayar Değiştirdi"),
        ("module_access", "Modül Erişti"),
        ("api_call", "API Çağrısı"),
        ("other", "Diğer"),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Kullanıcı",
    )
    activity_type = models.CharField(
        max_length=30, choices=ACTIVITY_TYPES, verbose_name="Aktivite Tipi"
    )
    description = models.TextField(verbose_name="Açıklama")

    # Metadata
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP Adresi"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    module = models.CharField(max_length=50, blank=True, verbose_name="Modül")

    # Extra data (JSON)
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Ek Veri")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")

    class Meta:
        verbose_name = "Kullanıcı Aktivitesi"
        verbose_name_plural = "Kullanıcı Aktiviteleri"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} ({self.created_at})"


class LoginHistory(models.Model):
    """Kullanıcı giriş geçmişi - güvenlik takibi"""

    STATUS_CHOICES = [
        ("success", "Başarılı"),
        ("failed", "Başarısız"),
        ("blocked", "Engellendi"),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="login_history",
        verbose_name="Kullanıcı",
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="success", verbose_name="Durum"
    )

    # Cihaz bilgisi
    ip_address = models.GenericIPAddressField(verbose_name="IP Adresi")
    user_agent = models.TextField(verbose_name="User Agent")
    device_type = models.CharField(max_length=50, blank=True, verbose_name="Cihaz Tipi")
    browser = models.CharField(max_length=50, blank=True, verbose_name="Tarayıcı")
    os = models.CharField(max_length=50, blank=True, verbose_name="İşletim Sistemi")

    # Lokasyon
    country = models.CharField(max_length=100, blank=True, verbose_name="Ülke")
    city = models.CharField(max_length=100, blank=True, verbose_name="Şehir")

    # Başarısız girişler için
    failure_reason = models.CharField(
        max_length=200, blank=True, verbose_name="Başarısızlık Sebebi"
    )

    # 2FA
    two_factor_used = models.BooleanField(default=False, verbose_name="2FA Kullanıldı")

    login_at = models.DateTimeField(auto_now_add=True, verbose_name="Giriş Zamanı")
    logout_at = models.DateTimeField(null=True, blank=True, verbose_name="Çıkış Zamanı")
    session_duration = models.IntegerField(
        null=True, blank=True, verbose_name="Oturum Süresi (dakika)"
    )

    class Meta:
        verbose_name = "Giriş Geçmişi"
        verbose_name_plural = "Giriş Geçmişleri"
        ordering = ["-login_at"]
        indexes = [
            models.Index(fields=["user", "-login_at"]),
            models.Index(fields=["ip_address", "-login_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.status} ({self.login_at})"


class UserNotification(models.Model):
    """Kullanıcı bildirimleri"""

    NOTIFICATION_TYPES = [
        ("info", "Bilgilendirme"),
        ("success", "Başarılı"),
        ("warning", "Uyarı"),
        ("error", "Hata"),
        ("system", "Sistem"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Düşük"),
        ("normal", "Normal"),
        ("high", "Yüksek"),
        ("urgent", "Acil"),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_notifications",
        verbose_name="Kullanıcı",
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default="info", verbose_name="Tip"
    )
    priority = models.CharField(
        max_length=20, choices=PRIORITY_LEVELS, default="normal", verbose_name="Öncelik"
    )

    # İçerik
    title = models.CharField(max_length=200, verbose_name="Başlık")
    message = models.TextField(verbose_name="Mesaj")
    action_url = models.CharField(
        max_length=500, blank=True, verbose_name="Aksiyon URL"
    )

    # Durum
    is_read = models.BooleanField(default=False, verbose_name="Okundu")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Okunma Zamanı")

    # Kategori/Modül
    category = models.CharField(max_length=50, blank=True, verbose_name="Kategori")
    module = models.CharField(max_length=50, blank=True, verbose_name="Modül")

    # Geçerlilik
    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Geçerlilik Süresi"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")

    class Meta:
        verbose_name = "Bildirim"
        verbose_name_plural = "Bildirimler"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class TwoFactorAuth(models.Model):
    """İki faktörlü kimlik doğrulama"""

    METHOD_CHOICES = [
        ("totp", "Authenticator App (TOTP)"),
        ("sms", "SMS"),
        ("email", "E-posta"),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="two_factor_auth",
        verbose_name="Kullanıcı",
    )
    is_enabled = models.BooleanField(default=False, verbose_name="Aktif")
    method = models.CharField(
        max_length=10, choices=METHOD_CHOICES, default="totp", verbose_name="Yöntem"
    )

    # TOTP için
    secret_key = models.CharField(max_length=100, blank=True, verbose_name="Secret Key")

    # Yedek kodlar
    backup_codes = models.JSONField(
        default=list, blank=True, verbose_name="Yedek Kodlar"
    )

    # İstatistikler
    enabled_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Aktif Edilme"
    )
    last_used_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Son Kullanım"
    )
    total_uses = models.IntegerField(default=0, verbose_name="Toplam Kullanım")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "İki Faktörlü Doğrulama"
        verbose_name_plural = "İki Faktörlü Doğrulamalar"

    def __str__(self):
        status = "Aktif" if self.is_enabled else "Pasif"
        return f"{self.user.username} - 2FA ({status})"


class PasswordHistory(models.Model):
    """Şifre değişiklik geçmişi"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="password_history",
        verbose_name="Kullanıcı",
    )
    password_hash = models.CharField(max_length=255, verbose_name="Şifre Hash")

    # Değişiklik bilgisi
    changed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="password_changes_made",
        verbose_name="Değiştiren",
    )
    change_reason = models.CharField(
        max_length=200, blank=True, verbose_name="Değişiklik Sebebi"
    )

    # Güvenlik
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP Adresi"
    )

    changed_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Değişiklik Tarihi"
    )

    class Meta:
        verbose_name = "Şifre Geçmişi"
        verbose_name_plural = "Şifre Geçmişleri"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.user.username} - Şifre Değişikliği ({self.changed_at})"


class UserSession(models.Model):
    """Aktif kullanıcı oturumları"""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_sessions",
        verbose_name="Kullanıcı",
    )
    session_key = models.CharField(
        max_length=100, unique=True, verbose_name="Session Key"
    )

    # Cihaz bilgisi
    ip_address = models.GenericIPAddressField(verbose_name="IP Adresi")
    user_agent = models.TextField(verbose_name="User Agent")
    device_name = models.CharField(max_length=100, blank=True, verbose_name="Cihaz Adı")

    # Oturum durumu
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Son Aktivite")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    expires_at = models.DateTimeField(verbose_name="Geçerlilik Süresi")

    class Meta:
        verbose_name = "Kullanıcı Oturumu"
        verbose_name_plural = "Kullanıcı Oturumları"
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["session_key"]),
        ]

    def __str__(self):
        return f"{self.user.username} - Session ({self.created_at})"


class UserPreference(models.Model):
    """Gelişmiş kullanıcı tercihleri"""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="preferences",
        verbose_name="Kullanıcı",
    )

    # Bildirim tercihleri
    email_notifications = models.BooleanField(
        default=True, verbose_name="E-posta Bildirimleri"
    )
    push_notifications = models.BooleanField(
        default=True, verbose_name="Push Bildirimleri"
    )
    sms_notifications = models.BooleanField(
        default=False, verbose_name="SMS Bildirimleri"
    )

    # Bildirim kategorileri
    invoice_notifications = models.BooleanField(
        default=True, verbose_name="Fatura Bildirimleri"
    )
    payment_notifications = models.BooleanField(
        default=True, verbose_name="Ödeme Bildirimleri"
    )
    report_notifications = models.BooleanField(
        default=True, verbose_name="Rapor Bildirimleri"
    )
    system_notifications = models.BooleanField(
        default=True, verbose_name="Sistem Bildirimleri"
    )
    marketing_notifications = models.BooleanField(
        default=False, verbose_name="Pazarlama Bildirimleri"
    )

    # Görünüm tercihleri
    theme = models.CharField(
        max_length=20,
        choices=[("light", "Açık Tema"), ("dark", "Koyu Tema"), ("auto", "Otomatik")],
        default="light",
        verbose_name="Tema",
    )

    sidebar_collapsed = models.BooleanField(
        default=False, verbose_name="Kenar Çubuğu Daraltılmış"
    )
    items_per_page = models.IntegerField(
        default=25,
        choices=[(10, "10"), (25, "25"), (50, "50"), (100, "100")],
        verbose_name="Sayfa Başına Öğe",
    )

    # Güvenlik tercihleri
    session_timeout = models.IntegerField(
        default=30, verbose_name="Oturum Zaman Aşımı (dakika)"
    )
    require_password_change = models.BooleanField(
        default=False, verbose_name="Şifre Değişikliği Gerekli"
    )
    password_change_interval = models.IntegerField(
        default=90, verbose_name="Şifre Değişim Aralığı (gün)"
    )

    # Diğer
    default_dashboard = models.CharField(
        max_length=50, blank=True, verbose_name="Varsayılan Dashboard"
    )
    custom_settings = models.JSONField(
        default=dict, blank=True, verbose_name="Özel Ayarlar"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kullanıcı Tercihi"
        verbose_name_plural = "Kullanıcı Tercihleri"

    def __str__(self):
        return f"{self.user.username} - Preferences"
