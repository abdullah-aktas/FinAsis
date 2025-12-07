# Security models are imported from data_security_compliance.py
from finance.data_security_compliance import *  # noqa: F403

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


# ============================================================================
# GÜVENLİK YÖNETİM MODELLERİ
# ============================================================================


class SecurityPolicy(models.Model):
    """Güvenlik politikaları"""

    POLICY_TYPES = [
        ("PASSWORD", _("Şifre Politikası")),
        ("SESSION", _("Oturum Politikası")),
        ("ACCESS", _("Erişim Politikası")),
        ("DATA", _("Veri Politikası")),
        ("API", _("API Politikası")),
    ]

    name = models.CharField(max_length=200, verbose_name=_("Politika Adı"))
    policy_type = models.CharField(
        max_length=20, choices=POLICY_TYPES, verbose_name=_("Politika Tipi")
    )
    description = models.TextField(verbose_name=_("Açıklama"))

    # Kurallar (JSON)
    rules = models.JSONField(default=dict, verbose_name=_("Kurallar"))

    # Durum
    is_active = models.BooleanField(default=True, verbose_name=_("Aktif"))
    is_enforced = models.BooleanField(default=False, verbose_name=_("Zorunlu"))

    # Öncelik
    priority = models.IntegerField(default=0, verbose_name=_("Öncelik"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Güvenlik Politikası")
        verbose_name_plural = _("Güvenlik Politikaları")
        ordering = ["-priority", "name"]

    def __str__(self):
        return self.name


class SecurityIncident(models.Model):
    """Güvenlik olayları"""

    INCIDENT_TYPES = [
        ("UNAUTHORIZED_ACCESS", _("Yetkisiz Erişim")),
        ("BRUTE_FORCE", _("Brute Force Saldırısı")),
        ("SQL_INJECTION", _("SQL Injection")),
        ("XSS", _("XSS Saldırısı")),
        ("CSRF", _("CSRF Saldırısı")),
        ("DATA_BREACH", _("Veri İhlali")),
        ("SUSPICIOUS_ACTIVITY", _("Şüpheli Aktivite")),
        ("OTHER", _("Diğer")),
    ]

    SEVERITY_LEVELS = [
        ("LOW", _("Düşük")),
        ("MEDIUM", _("Orta")),
        ("HIGH", _("Yüksek")),
        ("CRITICAL", _("Kritik")),
    ]

    incident_type = models.CharField(
        max_length=30, choices=INCIDENT_TYPES, verbose_name=_("Olay Tipi")
    )
    severity = models.CharField(
        max_length=20, choices=SEVERITY_LEVELS, verbose_name=_("Ciddiyet")
    )

    # Detaylar
    title = models.CharField(max_length=200, verbose_name=_("Başlık"))
    description = models.TextField(verbose_name=_("Açıklama"))

    # Hedef
    affected_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="security_incidents",
        verbose_name=_("Etkilenen Kullanıcı"),
    )
    affected_resource = models.CharField(
        max_length=200, blank=True, verbose_name=_("Etkilenen Kaynak")
    )

    # Kaynak
    source_ip = models.GenericIPAddressField(verbose_name=_("Kaynak IP"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))

    # İstatistikler
    attempt_count = models.IntegerField(default=1, verbose_name=_("Deneme Sayısı"))

    # Müdahale
    is_resolved = models.BooleanField(default=False, verbose_name=_("Çözüldü"))
    resolved_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Çözüm Zamanı")
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_incidents",
        verbose_name=_("Çözen"),
    )
    resolution_notes = models.TextField(blank=True, verbose_name=_("Çözüm Notları"))

    # Aksiyonlar
    action_taken = models.TextField(blank=True, verbose_name=_("Alınan Aksiyon"))

    detected_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Tespit Tarihi")
    )

    class Meta:
        verbose_name = _("Güvenlik Olayı")
        verbose_name_plural = _("Güvenlik Olayları")
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["severity", "-detected_at"]),
            models.Index(fields=["is_resolved", "-detected_at"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.title}"


class IPWhitelist(models.Model):
    """IP beyaz liste - güvenli IP adresleri"""

    ip_address = models.GenericIPAddressField(unique=True, verbose_name=_("IP Adresi"))
    description = models.CharField(max_length=200, verbose_name=_("Açıklama"))

    # Hedef
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Kullanıcı"),
    )

    # Durum
    is_active = models.BooleanField(default=True, verbose_name=_("Aktif"))

    # İstatistikler
    last_used_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Son Kullanım")
    )
    usage_count = models.IntegerField(default=0, verbose_name=_("Kullanım Sayısı"))

    # Geçerlilik
    valid_until = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Geçerlilik Süresi")
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_whitelists",
        verbose_name=_("Oluşturan"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("IP Beyaz Liste")
        verbose_name_plural = _("IP Beyaz Listeler")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ip_address} - {self.description}"


class IPBlacklist(models.Model):
    """IP kara liste - engellenmiş IP adresleri"""

    BLOCK_REASONS = [
        ("BRUTE_FORCE", _("Brute Force")),
        ("MALICIOUS", _("Kötü Niyetli Aktivite")),
        ("SPAM", _("Spam")),
        ("MANUAL", _("Manuel Engelleme")),
        ("AUTOMATED", _("Otomatik Engelleme")),
    ]

    ip_address = models.GenericIPAddressField(unique=True, verbose_name=_("IP Adresi"))
    reason = models.CharField(
        max_length=30, choices=BLOCK_REASONS, verbose_name=_("Engelleme Sebebi")
    )
    description = models.TextField(blank=True, verbose_name=_("Açıklama"))

    # İstatistikler
    blocked_attempts = models.IntegerField(
        default=0, verbose_name=_("Engellenen Deneme")
    )
    first_blocked_at = models.DateTimeField(verbose_name=_("İlk Engelleme"))
    last_attempt_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Son Deneme")
    )

    # Durum
    is_active = models.BooleanField(default=True, verbose_name=_("Aktif"))
    auto_unblock_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Otomatik Kaldırma Zamanı")
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Oluşturan"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("IP Kara Liste")
        verbose_name_plural = _("IP Kara Listeler")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ip_address} - {self.get_reason_display()}"


class SecurityAuditLog(models.Model):
    """Kritik güvenlik aksiyonlarının merkezi audit log'u."""

    action = models.CharField(max_length=120)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="security_audit_logs",
    )
    resource = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=True)
    occurred_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Güvenlik Audit Logu")
        verbose_name_plural = _("Güvenlik Audit Logları")
        ordering = ("-occurred_at",)
        indexes = [
            models.Index(fields=("action", "occurred_at")),
            models.Index(fields=("actor", "occurred_at")),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.action} ({self.occurred_at:%Y-%m-%d %H:%M})"
