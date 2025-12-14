from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PressRelease(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    summary = models.TextField(blank=True)
    url = models.URLField(blank=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Basın Bülteni"
        verbose_name_plural = "Basın Bültenleri"

    def __str__(self):
        return f"{self.date} - {self.title}"


class InvestorDocument(models.Model):
    name = models.CharField(max_length=200)
    file_url = models.URLField()
    kind = models.CharField(
        max_length=50, choices=[("deck", "Sunum"), ("report", "Rapor")]
    )
    published_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "name"]
        verbose_name = "Yatırımcı Belgesi"
        verbose_name_plural = "Yatırımcı Belgeleri"

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    department = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Ekip Üyesi"
        verbose_name_plural = "Ekip Üyeleri"

    def __str__(self):
        return f"{self.name} - {self.role}"


class PartnerCategory(models.Model):
    """Marketplace üzerinde partnerlerin gruplanacağı kategori."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=80, blank=True, help_text=_("Bootstrap ikon adı veya özel sınıf.")
    )
    highlight_color = models.CharField(
        max_length=32, blank=True, help_text=_("Örn. #0AAE94 veya tailwind sınıfı.")
    )
    priority = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("priority", "name")
        verbose_name = _("Kurumsal Partner Kategorisi")
        verbose_name_plural = _("Kurumsal Partner Kategorileri")

    def __str__(self) -> str:
        return self.name


class PartnerListing(models.Model):
    """Partner marketplace vitrininde yayınlanan içerik."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Taslak")
        REVIEW = "review", _("İncelemede")
        PUBLISHED = "published", _("Yayında")
        ARCHIVED = "archived", _("Arşivlendi")

    category = models.ForeignKey(
        PartnerCategory,
        on_delete=models.PROTECT,
        related_name="partners",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    tagline = models.CharField(max_length=180, blank=True)
    summary = models.TextField(blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    logo_url = models.URLField(
        blank=True, help_text=_("CDN veya medya kütüphanesi URL'si.")
    )
    badge_label = models.CharField(max_length=60, blank=True)
    capabilities = models.JSONField(default=list, blank=True)
    regions = models.JSONField(default=list, blank=True)
    integrations = models.JSONField(default=list, blank=True)
    cta_label = models.CharField(max_length=80, default=_("Demo Talep Et"))
    cta_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    is_featured = models.BooleanField(default=False)
    feature_order = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("feature_order", "name")
        verbose_name = _("Partner Liste Kaydı")
        verbose_name_plural = _("Partner Liste Kayıtları")

    def __str__(self) -> str:
        return self.name

    @property
    def badge(self) -> str:
        if self.badge_label:
            return self.badge_label
        if self.category:
            return self.category.name
        return ""

    def is_published(self) -> bool:
        return self.status == self.Status.PUBLISHED


class PartnerApplication(models.Model):
    """Partner ekosistemine katılmak isteyen şirketlerden gelen başvurular."""

    class Status(models.TextChoices):
        NEW = "new", _("Yeni")
        IN_REVIEW = "in_review", _("İncelemede")
        APPROVED = "approved", _("Onaylandı")
        WAITLIST = "waitlist", _("Beklemede")
        REJECTED = "rejected", _("Reddedildi")

    company_name = models.CharField(max_length=180)
    brand_name = models.CharField(max_length=160, blank=True)
    contact_name = models.CharField(max_length=150)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=50, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    country = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    team_size = models.CharField(max_length=60, blank=True)
    primary_category = models.ForeignKey(
        PartnerCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_applications",
    )
    categories = models.ManyToManyField(
        PartnerCategory, related_name="applications", blank=True
    )
    integration_focus = models.JSONField(default=list, blank=True)
    product_notes = models.TextField(blank=True)
    message = models.TextField(blank=True)
    go_live_timeline = models.CharField(max_length=120, blank=True)
    revenue_model = models.CharField(max_length=120, blank=True)
    sandbox_needs = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partner_applications",
    )
    decision_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Kurumsal Partner Başvurusu")
        verbose_name_plural = _("Kurumsal Partner Başvuruları")

    def __str__(self) -> str:
        return f"{self.company_name} - {self.get_status_display()}"


class PartnerApplicationEvent(models.Model):
    """Başvuru süreç logu."""

    application = models.ForeignKey(
        PartnerApplication,
        on_delete=models.CASCADE,
        related_name="events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partner_application_events",
    )
    action = models.CharField(max_length=60)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Partner Başvuru Logu")
        verbose_name_plural = _("Partner Başvuru Logları")

    def __str__(self) -> str:
        return f"{self.application.company_name} · {self.action}"


class ContactMessage(models.Model):
    """
    Kurumsal iletişim formundan gelen mesajlar.

    Amaç:
    - İletişime geçen kişilerin ad, e-posta, telefon ve mesajlarını
      veritabanında saklamak
    - Django admin üzerinden hızlıca filtreleyip yanıtlayabilmek
    """

    class Subject(models.TextChoices):
        DEMO = "demo", _("Demo Talebi")
        SALES = "sales", _("Satış Bilgisi")
        SUPPORT = "support", _("Teknik Destek")
        COMPLIANCE = "compliance", _("Uyumluluk Danışmanlığı")
        PARTNERSHIP = "partnership", _("Partnerlik")
        OTHER = "other", _("Diğer")

    name = models.CharField(_("Ad Soyad"), max_length=150)
    email = models.EmailField(_("E-posta"))
    company = models.CharField(_("Şirket"), max_length=200, blank=True)
    phone = models.CharField(_("Telefon"), max_length=50, blank=True)
    subject = models.CharField(
        _("Konu"), max_length=32, choices=Subject.choices, default=Subject.OTHER
    )
    message = models.TextField(_("Mesaj"))
    consent_gdpr = models.BooleanField(_("KVKK onayı"), default=False)
    source = models.CharField(
        _("Kaynak"),
        max_length=100,
        blank=True,
        help_text=_("Formun gönderildiği sayfa veya kampanya kodu."),
    )
    created_at = models.DateTimeField(_("Oluşturulma"), auto_now_add=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handled_contact_messages",
        verbose_name=_("İlgilenen kullanıcı"),
    )
    handled_at = models.DateTimeField(_("İlgilenme zamanı"), null=True, blank=True)
    is_resolved = models.BooleanField(_("Tamamlandı"), default=False)
    notes = models.TextField(_("İç notlar"), blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("İletişim Mesajı")
        verbose_name_plural = _("İletişim Mesajları")

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> - {self.get_subject_display()}"
