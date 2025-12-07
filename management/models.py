from django.db import models
from django.conf import settings


class ActionLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    detail = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp:%Y-%m-%d %H:%M}"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Bildirim: {self.user} - {self.message[:30]}"


class HelpContent(models.Model):
    ROLE_CHOICES = [
        ("genel", "Genel Kullanıcı"),
        ("admin", "Yönetici"),
        ("muhasebeci", "Muhasebeci"),
        ("calisan", "Çalışan"),
        ("ogrenci", "Öğrenci"),
        ("ogretmen", "Öğretmen"),
    ]
    title = models.CharField(max_length=100)
    content = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="genel")
    page_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Yardımın hangi sayfada gösterileceği (isteğe bağlı)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_role_display()}] {self.title}"


# ============================================================================
# GENİŞLETİLMİŞ YÖNETİM VE MONİTORİNG SİSTEMİ
# ============================================================================


class SystemHealth(models.Model):
    """Sistem sağlığı monitoring"""

    STATUS_CHOICES = [
        ("HEALTHY", "Sağlıklı"),
        ("WARNING", "Uyarı"),
        ("CRITICAL", "Kritik"),
        ("DOWN", "Çalışmıyor"),
    ]

    # Sistem metrikleri
    cpu_usage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="CPU Kullanımı (%)"
    )
    memory_usage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="RAM Kullanımı (%)"
    )
    disk_usage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Disk Kullanımı (%)"
    )

    # Database metrikleri
    db_connections = models.IntegerField(verbose_name="Aktif DB Bağlantı")
    db_response_time_ms = models.IntegerField(verbose_name="DB Yanıt Süresi (ms)")

    # Uygulama metrikleri
    active_users = models.IntegerField(verbose_name="Aktif Kullanıcı")
    requests_per_minute = models.IntegerField(verbose_name="Dakika Başı İstek")
    error_count = models.IntegerField(default=0, verbose_name="Hata Sayısı")

    # Durum
    overall_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="HEALTHY",
        verbose_name="Genel Durum",
    )
    status_message = models.TextField(blank=True, verbose_name="Durum Mesajı")

    # Timestamp
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name="Kontrol Zamanı")

    class Meta:
        verbose_name = "Sistem Sağlığı"
        verbose_name_plural = "Sistem Sağlık Kayıtları"
        ordering = ["-checked_at"]
        indexes = [
            models.Index(fields=["-checked_at"]),
            models.Index(fields=["overall_status", "-checked_at"]),
        ]

    def __str__(self):
        return f"{self.overall_status} - {self.checked_at}"


class PerformanceMetric(models.Model):
    """Performans metrikleri - uygulama performansı"""

    METRIC_TYPES = [
        ("RESPONSE_TIME", "Yanıt Süresi"),
        ("THROUGHPUT", "İşlem Hacmi"),
        ("ERROR_RATE", "Hata Oranı"),
        ("UPTIME", "Çalışma Süresi"),
        ("API_LATENCY", "API Gecikmesi"),
    ]

    metric_type = models.CharField(
        max_length=30, choices=METRIC_TYPES, verbose_name="Metrik Tipi"
    )
    metric_name = models.CharField(max_length=100, verbose_name="Metrik Adı")

    # Değer
    value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Değer")
    unit = models.CharField(
        max_length=20, verbose_name="Birim", help_text="ms, %, requests/sec, vs."
    )

    # Hedef ve durum
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Hedef Değer",
    )
    is_healthy = models.BooleanField(default=True, verbose_name="Sağlıklı")

    # Metadata
    endpoint = models.CharField(max_length=200, blank=True, verbose_name="Endpoint")
    module = models.CharField(max_length=50, blank=True, verbose_name="Modül")

    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Zamanı")

    class Meta:
        verbose_name = "Performans Metriği"
        verbose_name_plural = "Performans Metrikleri"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["metric_type", "-recorded_at"]),
            models.Index(fields=["module", "-recorded_at"]),
        ]

    def __str__(self):
        return f"{self.metric_name}: {self.value} {self.unit}"


class ErrorLog(models.Model):
    """Hata logları - detaylı hata takibi"""

    SEVERITY_LEVELS = [
        ("DEBUG", "Debug"),
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    severity = models.CharField(
        max_length=20, choices=SEVERITY_LEVELS, default="ERROR", verbose_name="Ciddiyet"
    )

    # Hata detayları
    error_type = models.CharField(max_length=100, verbose_name="Hata Tipi")
    error_message = models.TextField(verbose_name="Hata Mesajı")
    stack_trace = models.TextField(blank=True, verbose_name="Stack Trace")

    # Konum
    module = models.CharField(max_length=100, blank=True, verbose_name="Modül")
    function = models.CharField(max_length=100, blank=True, verbose_name="Fonksiyon")
    file_path = models.CharField(max_length=500, blank=True, verbose_name="Dosya Yolu")
    line_number = models.IntegerField(
        null=True, blank=True, verbose_name="Satır Numarası"
    )

    # Request bilgisi
    request_path = models.CharField(
        max_length=500, blank=True, verbose_name="İstek Yolu"
    )
    request_method = models.CharField(
        max_length=10, blank=True, verbose_name="HTTP Metodu"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Kullanıcı",
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP Adresi"
    )

    # Extra data
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Ek Veri")

    # Çözüm
    is_resolved = models.BooleanField(default=False, verbose_name="Çözüldü")
    resolved_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Çözüm Zamanı"
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_errors",
        verbose_name="Çözen",
    )

    occurred_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşma Zamanı")

    class Meta:
        verbose_name = "Hata Logu"
        verbose_name_plural = "Hata Logları"
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["severity", "-occurred_at"]),
            models.Index(fields=["is_resolved", "-occurred_at"]),
            models.Index(fields=["module", "-occurred_at"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.error_type} ({self.occurred_at})"


class BackupLog(models.Model):
    """Yedekleme logları"""

    BACKUP_TYPES = [
        ("FULL", "Tam Yedekleme"),
        ("INCREMENTAL", "Artırımlı"),
        ("DIFFERENTIAL", "Farksal"),
        ("DATABASE", "Veritabanı"),
        ("FILES", "Dosyalar"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Beklemede"),
        ("RUNNING", "Çalışıyor"),
        ("COMPLETED", "Tamamlandı"),
        ("FAILED", "Başarısız"),
    ]

    backup_name = models.CharField(max_length=200, verbose_name="Yedekleme Adı")
    backup_type = models.CharField(
        max_length=20, choices=BACKUP_TYPES, verbose_name="Yedekleme Tipi"
    )

    # Dosya bilgisi
    file_path = models.CharField(max_length=500, verbose_name="Dosya Yolu")
    file_size_mb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Dosya Boyutu (MB)",
    )

    # Durum
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="Durum"
    )

    # Zamanlama
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Başlangıç")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş")
    duration_seconds = models.IntegerField(
        null=True, blank=True, verbose_name="Süre (saniye)"
    )

    # Sonuç
    success_message = models.TextField(blank=True, verbose_name="Başarı Mesajı")
    error_message = models.TextField(blank=True, verbose_name="Hata Mesajı")

    # İstatistikler
    items_backed_up = models.IntegerField(
        null=True, blank=True, verbose_name="Yedeklenen Öğe Sayısı"
    )

    # Metadata
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Başlatan",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Yedekleme Logu"
        verbose_name_plural = "Yedekleme Logları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.backup_name} - {self.status}"


class SystemAudit(models.Model):
    """Sistem denetim kayıtları"""

    AUDIT_TYPES = [
        ("SECURITY", "Güvenlik Denetimi"),
        ("COMPLIANCE", "Uyumluluk Denetimi"),
        ("PERFORMANCE", "Performans Denetimi"),
        ("DATA", "Veri Denetimi"),
        ("ACCESS", "Erişim Denetimi"),
    ]

    STATUS_CHOICES = [
        ("PASSED", "Geçti"),
        ("FAILED", "Başarısız"),
        ("WARNING", "Uyarı"),
        ("PENDING", "Beklemede"),
    ]

    audit_name = models.CharField(max_length=200, verbose_name="Denetim Adı")
    audit_type = models.CharField(
        max_length=30, choices=AUDIT_TYPES, verbose_name="Denetim Tipi"
    )

    # Denetim detayları
    description = models.TextField(verbose_name="Açıklama")
    audit_criteria = models.JSONField(
        default=dict, blank=True, verbose_name="Denetim Kriterleri"
    )

    # Sonuçlar
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="Durum"
    )
    findings = models.JSONField(default=list, blank=True, verbose_name="Bulgular")
    issues_found = models.IntegerField(default=0, verbose_name="Bulunan Sorun Sayısı")

    # Skorlama
    compliance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Uyumluluk Skoru (%)",
    )

    # Öneriler
    recommendations = models.TextField(blank=True, verbose_name="Öneriler")
    action_items = models.JSONField(
        default=list, blank=True, verbose_name="Aksiyon Maddeleri"
    )

    # Zamanlama
    audit_date = models.DateField(verbose_name="Denetim Tarihi")
    next_audit_date = models.DateField(
        null=True, blank=True, verbose_name="Sonraki Denetim"
    )

    # Metadata
    audited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Denetleyen"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sistem Denetimi"
        verbose_name_plural = "Sistem Denetimleri"
        ordering = ["-audit_date"]

    def __str__(self):
        return f"{self.audit_name} - {self.status}"


class MaintenanceWindow(models.Model):
    """Bakım pencereleri - planlı bakım zamanları"""

    STATUS_CHOICES = [
        ("SCHEDULED", "Planlandı"),
        ("IN_PROGRESS", "Devam Ediyor"),
        ("COMPLETED", "Tamamlandı"),
        ("CANCELLED", "İptal Edildi"),
    ]

    title = models.CharField(max_length=200, verbose_name="Bakım Başlığı")
    description = models.TextField(verbose_name="Açıklama")

    # Zamanlama
    start_time = models.DateTimeField(verbose_name="Başlangıç Zamanı")
    end_time = models.DateTimeField(verbose_name="Bitiş Zamanı")
    estimated_duration_minutes = models.IntegerField(
        verbose_name="Tahmini Süre (dakika)"
    )

    # Durum
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="SCHEDULED", verbose_name="Durum"
    )
    actual_start_time = models.DateTimeField(
        null=True, blank=True, verbose_name="Gerçek Başlangıç"
    )
    actual_end_time = models.DateTimeField(
        null=True, blank=True, verbose_name="Gerçek Bitiş"
    )

    # Etkilenen servisler
    affected_modules = models.JSONField(
        default=list, blank=True, verbose_name="Etkilenen Modüller"
    )

    # Bildirim
    notify_users = models.BooleanField(
        default=True, verbose_name="Kullanıcılara Bildir"
    )
    notification_sent = models.BooleanField(
        default=False, verbose_name="Bildirim Gönderildi"
    )

    # Sonuç
    completion_notes = models.TextField(blank=True, verbose_name="Tamamlanma Notları")
    issues_encountered = models.TextField(
        blank=True, verbose_name="Karşılaşılan Sorunlar"
    )

    # Metadata
    scheduled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scheduled_maintenances",
        verbose_name="Planlayan",
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="performed_maintenances",
        verbose_name="Gerçekleştiren",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bakım Penceresi"
        verbose_name_plural = "Bakım Pencereleri"
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.title} ({self.start_time})"


class UsageStatistics(models.Model):
    """Kullanım istatistikleri - modül ve özellik kullanımı"""

    # Dönem
    period_date = models.DateField(verbose_name="Dönem Tarihi")
    period_type = models.CharField(
        max_length=20,
        choices=[
            ("DAILY", "Günlük"),
            ("WEEKLY", "Haftalık"),
            ("MONTHLY", "Aylık"),
        ],
        default="DAILY",
        verbose_name="Dönem Tipi",
    )

    # Kullanıcı istatistikleri
    total_users = models.IntegerField(default=0, verbose_name="Toplam Kullanıcı")
    active_users = models.IntegerField(default=0, verbose_name="Aktif Kullanıcı")
    new_users = models.IntegerField(default=0, verbose_name="Yeni Kullanıcı")

    # Oturum istatistikleri
    total_sessions = models.IntegerField(default=0, verbose_name="Toplam Oturum")
    average_session_duration = models.IntegerField(
        default=0, verbose_name="Ortalama Oturum Süresi (dk)"
    )

    # İşlem istatistikleri
    total_transactions = models.IntegerField(default=0, verbose_name="Toplam İşlem")
    total_invoices = models.IntegerField(default=0, verbose_name="Toplam Fatura")
    total_reports = models.IntegerField(default=0, verbose_name="Toplam Rapor")

    # Modül kullanımı
    module_usage = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Modül Kullanımı",
        help_text="{'accounting': 150, 'finance': 200, ...}",
    )

    # Feature kullanımı
    feature_usage = models.JSONField(
        default=dict, blank=True, verbose_name="Özellik Kullanımı"
    )

    # API istatistikleri
    api_calls = models.IntegerField(default=0, verbose_name="API Çağrısı")
    api_errors = models.IntegerField(default=0, verbose_name="API Hataları")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kullanım İstatistiği"
        verbose_name_plural = "Kullanım İstatistikleri"
        ordering = ["-period_date"]
        unique_together = ["period_date", "period_type"]

    def __str__(self):
        return f"{self.period_type} - {self.period_date}"


class DatabaseSnapshot(models.Model):
    """Veritabanı snapshot - boyut ve kayıt sayıları"""

    snapshot_date = models.DateField(verbose_name="Snapshot Tarihi")

    # Database boyutları
    total_size_mb = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Toplam Boyut (MB)"
    )
    data_size_mb = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Veri Boyutu (MB)"
    )
    index_size_mb = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="İndeks Boyutu (MB)"
    )

    # Tablo istatistikleri
    table_count = models.IntegerField(verbose_name="Tablo Sayısı")
    total_rows = models.BigIntegerField(verbose_name="Toplam Satır")

    # Model istatistikleri (JSON)
    model_statistics = models.JSONField(
        default=dict,
        verbose_name="Model İstatistikleri",
        help_text="{'User': 1500, 'Invoice': 35000, ...}",
    )

    # Performans
    avg_query_time_ms = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Ortalama Sorgu Süresi (ms)",
    )
    slow_queries_count = models.IntegerField(
        default=0, verbose_name="Yavaş Sorgu Sayısı"
    )

    # Fragmentation
    fragmentation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Fragmentation (%)",
    )

    # Öneriler
    optimization_needed = models.BooleanField(
        default=False, verbose_name="Optimizasyon Gerekli"
    )
    recommendations = models.TextField(blank=True, verbose_name="Öneriler")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Veritabanı Snapshot"
        verbose_name_plural = "Veritabanı Snapshotları"
        ordering = ["-snapshot_date"]

    def __str__(self):
        return f"DB Snapshot - {self.snapshot_date} ({self.total_size_mb} MB)"


class FeatureFlag(models.Model):
    """Özellik bayrakları - feature toggle sistemi"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Özellik Adı")
    key = models.SlugField(max_length=100, unique=True, verbose_name="Anahtar")
    description = models.TextField(verbose_name="Açıklama")

    # Durum
    is_enabled = models.BooleanField(default=False, verbose_name="Aktif")

    # Hedefleme
    enabled_for_all = models.BooleanField(default=False, verbose_name="Herkes İçin")
    enabled_for_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="enabled_features",
        verbose_name="Aktif Kullanıcılar",
    )
    enabled_for_roles = models.JSONField(
        default=list, blank=True, verbose_name="Aktif Roller"
    )

    # Percentage rollout
    rollout_percentage = models.IntegerField(
        default=0, verbose_name="Kullanıma Sunma Yüzdesi", help_text="0-100"
    )

    # Metadata
    module = models.CharField(max_length=50, blank=True, verbose_name="Modül")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Oluşturan"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Özellik Bayrağı"
        verbose_name_plural = "Özellik Bayrakları"
        ordering = ["module", "name"]

    def __str__(self):
        status = "Aktif" if self.is_enabled else "Pasif"
        return f"{self.name} ({status})"

    def is_enabled_for_user(self, user):
        """Kullanıcı için aktif mi kontrol et"""
        if not self.is_enabled:
            return False
        if self.enabled_for_all:
            return True
        if user in self.enabled_for_users.all():
            return True
        # Rol kontrolü
        if hasattr(user, "role") and user.role in self.enabled_for_roles:
            return True
        # Percentage rollout
        if self.rollout_percentage > 0:
            # Hash-based deterministic rollout
            import hashlib

            hash_value = int(
                hashlib.md5(  # noqa: B324
                    f"{user.id}{self.key}".encode(), usedforsecurity=False
                ).hexdigest(),
                16,
            )
            return (hash_value % 100) < self.rollout_percentage
        return False
