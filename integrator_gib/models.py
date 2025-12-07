from django.db import models


class IntegratorConfig(models.Model):
    name = models.CharField(max_length=100, default="Default Integrator")
    base_url = models.URLField()
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=200)
    certificate_alias = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)


class AccessToken(models.Model):
    integrator = models.ForeignKey(
        IntegratorConfig, on_delete=models.CASCADE, related_name="tokens"
    )
    token = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


# ============================================================================
# GENİŞLETİLMİŞ GİB ENTEGRASYON MODELLERİ
# ============================================================================


class GIBSubmissionLog(models.Model):
    """GİB gönderim logları - detaylı tracking"""

    STATUS_CHOICES = [
        ("PENDING", "Beklemede"),
        ("SENT", "Gönderildi"),
        ("ACCEPTED", "Kabul Edildi"),
        ("REJECTED", "Reddedildi"),
        ("ERROR", "Hata"),
    ]

    # Gönderim bilgisi
    submission_id = models.CharField(
        max_length=100, unique=True, verbose_name="Gönderim ID"
    )
    declaration_code = models.CharField(max_length=50, verbose_name="Beyan Kodu")
    period = models.CharField(max_length=20, verbose_name="Dönem")
    taxpayer_vkn = models.CharField(max_length=20, verbose_name="VKN/TCKN")

    # İstek
    request_payload = models.JSONField(default=dict, verbose_name="İstek Verisi")
    request_xml = models.TextField(blank=True, verbose_name="İstek XML")

    # Yanıt
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="Durum"
    )
    response_data = models.JSONField(
        default=dict, blank=True, verbose_name="Yanıt Verisi"
    )
    response_xml = models.TextField(blank=True, verbose_name="Yanıt XML")

    # GİB referans
    gib_reference_number = models.CharField(
        max_length=100, blank=True, verbose_name="GİB Referans No"
    )
    gib_tracking_id = models.CharField(
        max_length=100, blank=True, verbose_name="GİB Takip No"
    )

    # Hata
    error_code = models.CharField(max_length=50, blank=True, verbose_name="Hata Kodu")
    error_message = models.TextField(blank=True, verbose_name="Hata Mesajı")

    # Zamanlama
    submitted_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Gönderim Zamanı"
    )
    processed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="İşlenme Zamanı"
    )

    # Metadata
    integrator = models.ForeignKey(
        IntegratorConfig,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Entegratör",
    )

    class Meta:
        verbose_name = "GİB Gönderim Logu"
        verbose_name_plural = "GİB Gönderim Logları"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.submission_id} - {self.status}"


class GIBCertificate(models.Model):
    """GİB sertifikaları - e-imza ve mali mühür"""

    CERTIFICATE_TYPES = [
        ("E_SIGNATURE", "E-İmza"),
        ("TAX_SEAL", "Mali Mühür"),
    ]

    name = models.CharField(max_length=200, verbose_name="Sertifika Adı")
    certificate_type = models.CharField(
        max_length=20, choices=CERTIFICATE_TYPES, verbose_name="Sertifika Tipi"
    )

    # Sertifika bilgisi
    serial_number = models.CharField(
        max_length=100, unique=True, verbose_name="Seri Numarası"
    )
    alias = models.CharField(max_length=200, verbose_name="Alias")

    # Dosya
    certificate_file = models.FileField(
        upload_to="gib_certificates/", verbose_name="Sertifika Dosyası"
    )
    password_hash = models.CharField(
        max_length=255, blank=True, verbose_name="Şifre Hash"
    )

    # Geçerlilik
    valid_from = models.DateTimeField(verbose_name="Geçerlilik Başlangıcı")
    valid_until = models.DateTimeField(verbose_name="Geçerlilik Bitişi")

    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    # Kullanım
    last_used_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Son Kullanım"
    )
    usage_count = models.IntegerField(default=0, verbose_name="Kullanım Sayısı")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "GİB Sertifikası"
        verbose_name_plural = "GİB Sertifikaları"
        ordering = ["-valid_until"]

    def __str__(self):
        return f"{self.name} ({self.serial_number})"
