from django.db import models
from django.conf import settings
from decimal import Decimal


class AdvisorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="advisor_profile",
    )
    type = models.CharField(max_length=10, choices=(("SMMM", "SMMM"), ("YMM", "YMM")))
    chamber_no = models.CharField(max_length=50, blank=True)
    mersis_no = models.CharField(max_length=50, blank=True)
    e_signature_serial = models.CharField(max_length=128, blank=True)
    mali_muhur_fingerprint = models.CharField(max_length=128, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.type})"


class AdvisorRegistrySource(models.Model):
    source = models.CharField(max_length=50)
    external_id = models.CharField(max_length=100, blank=True)
    data = models.JSONField(default=dict, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)


class TaxpayerProfile(models.Model):
    # Minimal taxpayer profile; can be linked to tenancy/company later
    name = models.CharField(max_length=255)
    vkn_tckn = models.CharField(max_length=20)
    mersis_no = models.CharField(max_length=50, blank=True)
    # Optional alignment with tenancy Company; backfilled progressively
    company = models.ForeignKey(
        "tenancy.Company",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="taxpayers",
    )

    def __str__(self):
        return f"{self.name} ({self.vkn_tckn})"


class Engagement(models.Model):
    advisor = models.ForeignKey(
        AdvisorProfile, on_delete=models.CASCADE, related_name="engagements"
    )
    taxpayer = models.ForeignKey(
        TaxpayerProfile, on_delete=models.CASCADE, related_name="engagements"
    )
    scope = models.CharField(
        max_length=30,
        choices=(("defter", "e-Defter"), ("beyan", "e-Beyan"), ("both", "Her ikisi")),
    )
    status = models.CharField(
        max_length=20,
        choices=(("pending", "Beklemede"), ("active", "Aktif"), ("revoked", "İptal")),
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("advisor", "taxpayer", "scope"),)

    def __str__(self):
        return f"{self.advisor} -> {self.taxpayer} ({self.scope})"


# ============================================================================
# GENİŞLETİLMİŞ DANIŞMAN SİSTEMİ
# ============================================================================


class AdvisorService(models.Model):
    """Danışman hizmetleri - sunulan hizmet paketleri"""

    SERVICE_TYPES = [
        ("tax_consulting", "Vergi Danışmanlığı"),
        ("financial_advisory", "Mali Müşavirlik"),
        ("audit", "Bağımsız Denetim"),
        ("accounting", "Muhasebe Hizmetleri"),
        ("payroll", "Bordro Hizmetleri"),
        ("compliance", "Uyumluluk Danışmanlığı"),
        ("business_consulting", "İş Danışmanlığı"),
        ("legal", "Hukuki Danışmanlık"),
    ]

    PRICING_MODELS = [
        ("hourly", "Saatlik"),
        ("monthly", "Aylık Sabit"),
        ("per_transaction", "İşlem Başı"),
        ("project_based", "Proje Bazlı"),
    ]

    advisor = models.ForeignKey(
        AdvisorProfile, on_delete=models.CASCADE, related_name="services"
    )
    service_type = models.CharField(
        max_length=30, choices=SERVICE_TYPES, verbose_name="Hizmet Tipi"
    )
    service_name = models.CharField(max_length=200, verbose_name="Hizmet Adı")
    description = models.TextField(verbose_name="Açıklama")
    pricing_model = models.CharField(
        max_length=20, choices=PRICING_MODELS, default="monthly"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    currency = models.CharField(max_length=3, default="TRY")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Danışman Hizmeti"
        verbose_name_plural = "Danışman Hizmetleri"
        ordering = ["service_type", "service_name"]

    def __str__(self):
        return f"{self.service_name} - {self.price} {self.currency}"


class ConsultationSession(models.Model):
    """Danışmanlık oturumları - müşteri görüşmeleri"""

    SESSION_TYPES = [
        ("initial", "İlk Görüşme"),
        ("regular", "Rutin Danışmanlık"),
        ("urgent", "Acil Danışmanlık"),
        ("review", "İnceleme/Review"),
        ("planning", "Planlama"),
        ("training", "Eğitim"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Planlandı"),
        ("in_progress", "Devam Ediyor"),
        ("completed", "Tamamlandı"),
        ("cancelled", "İptal Edildi"),
        ("rescheduled", "Ertelendi"),
    ]

    advisor = models.ForeignKey(
        AdvisorProfile, on_delete=models.CASCADE, related_name="sessions"
    )
    taxpayer = models.ForeignKey(
        TaxpayerProfile, on_delete=models.CASCADE, related_name="sessions"
    )
    session_type = models.CharField(
        max_length=20, choices=SESSION_TYPES, default="regular"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )

    # Zamanlama
    scheduled_date = models.DateField(verbose_name="Planlanan Tarih")
    scheduled_time = models.TimeField(verbose_name="Planlanan Saat")
    duration_minutes = models.IntegerField(default=60, verbose_name="Süre (dakika)")
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)

    # İçerik
    agenda = models.TextField(blank=True, verbose_name="Gündem")
    notes = models.TextField(blank=True, verbose_name="Görüşme Notları")
    action_items = models.JSONField(default=list, blank=True, verbose_name="Aksiyonlar")
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)

    # Faturalandırma
    billable = models.BooleanField(default=True)
    billing_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    invoice_generated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Danışmanlık Oturumu"
        verbose_name_plural = "Danışmanlık Oturumları"
        ordering = ["-scheduled_date", "-scheduled_time"]

    def __str__(self):
        return f"{self.get_session_type_display()} - {self.taxpayer.name} ({self.scheduled_date})"


class AdvisorReport(models.Model):
    """Danışman raporları - müşteriye sunulan raporlar"""

    REPORT_TYPES = [
        ("tax_analysis", "Vergi Analizi"),
        ("financial_review", "Mali İnceleme"),
        ("compliance_check", "Uyumluluk Kontrolü"),
        ("business_valuation", "İşletme Değerleme"),
        ("budget_planning", "Bütçe Planlama"),
        ("audit_report", "Denetim Raporu"),
        ("monthly_summary", "Aylık Özet"),
        ("custom", "Özel Rapor"),
    ]

    advisor = models.ForeignKey(
        AdvisorProfile, on_delete=models.CASCADE, related_name="reports"
    )
    taxpayer = models.ForeignKey(
        TaxpayerProfile, on_delete=models.CASCADE, related_name="advisor_reports"
    )
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200, verbose_name="Rapor Başlığı")

    # İçerik
    executive_summary = models.TextField(verbose_name="Yönetici Özeti")
    detailed_content = models.TextField(verbose_name="Detaylı İçerik")
    findings = models.JSONField(default=list, blank=True, verbose_name="Bulgular")
    recommendations = models.JSONField(
        default=list, blank=True, verbose_name="Öneriler"
    )

    # Dönem
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    # Dosyalar
    report_file = models.FileField(upload_to="advisor_reports/", null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True)

    # Onay ve teslimat
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_advisor_reports",
    )
    delivered_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Danışman Raporu"
        verbose_name_plural = "Danışman Raporları"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.taxpayer.name}"


class ClientContract(models.Model):
    """Müşteri sözleşmeleri - danışman-müşteri arası anlaşmalar"""

    CONTRACT_TYPES = [
        ("monthly_retainer", "Aylık Sabit Ücret"),
        ("annual", "Yıllık Sözleşme"),
        ("project", "Proje Bazlı"),
        ("hourly", "Saatlik"),
    ]

    STATUS_CHOICES = [
        ("draft", "Taslak"),
        ("pending_signature", "İmza Bekliyor"),
        ("active", "Aktif"),
        ("expired", "Süresi Doldu"),
        ("terminated", "Feshedildi"),
    ]

    advisor = models.ForeignKey(
        AdvisorProfile, on_delete=models.CASCADE, related_name="contracts"
    )
    taxpayer = models.ForeignKey(
        TaxpayerProfile, on_delete=models.CASCADE, related_name="contracts"
    )
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    contract_number = models.CharField(max_length=50, unique=True)

    # Sözleşme detayları
    title = models.CharField(max_length=200, verbose_name="Sözleşme Başlığı")
    scope_of_work = models.TextField(verbose_name="İş Kapsamı")
    terms_and_conditions = models.TextField(verbose_name="Şartlar ve Koşullar")

    # Ücret
    contract_value = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Sözleşme Bedeli"
    )
    payment_terms = models.CharField(max_length=100, verbose_name="Ödeme Koşulları")

    # Tarihler
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")
    renewal_date = models.DateField(
        null=True, blank=True, verbose_name="Yenileme Tarihi"
    )

    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    signed_at = models.DateTimeField(null=True, blank=True)

    # Dosyalar
    contract_file = models.FileField(
        upload_to="advisor_contracts/", null=True, blank=True
    )
    signed_contract = models.FileField(
        upload_to="advisor_contracts/signed/", null=True, blank=True
    )

    # Auto-renewal
    auto_renew = models.BooleanField(default=False)
    renewal_notice_days = models.IntegerField(
        default=30, verbose_name="Yenileme Bildirimi (gün)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Müşteri Sözleşmesi"
        verbose_name_plural = "Müşteri Sözleşmeleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.contract_number} - {self.taxpayer.name}"


class AdvisorTimeTracking(models.Model):
    """Danışman zaman takibi - faturalama için"""

    advisor = models.ForeignKey(
        AdvisorProfile, on_delete=models.CASCADE, related_name="time_entries"
    )
    taxpayer = models.ForeignKey(
        TaxpayerProfile, on_delete=models.CASCADE, related_name="time_entries"
    )
    session = models.ForeignKey(
        ConsultationSession,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="time_entries",
    )

    date = models.DateField(verbose_name="Tarih")
    start_time = models.TimeField(verbose_name="Başlangıç")
    end_time = models.TimeField(verbose_name="Bitiş")
    duration_minutes = models.IntegerField(verbose_name="Süre (dakika)")

    # İş detayı
    task_description = models.TextField(verbose_name="Yapılan İş")
    service_category = models.CharField(max_length=50, verbose_name="Hizmet Kategorisi")

    # Faturalandırma
    billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Saatlik Ücret"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Toplam Tutar"
    )
    invoiced = models.BooleanField(default=False)
    invoice_reference = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Zaman Kaydı"
        verbose_name_plural = "Zaman Kayıtları"
        ordering = ["-date", "-start_time"]

    def save(self, *args, **kwargs):
        # Toplam tutarı otomatik hesapla
        if self.duration_minutes and self.hourly_rate:
            hours = self.duration_minutes / 60
            self.total_amount = self.hourly_rate * Decimal(str(hours))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.advisor.user.username} - {self.date} ({self.duration_minutes}dk)"


class ClientDocument(models.Model):
    """Müşteri dokümanları - evraklar, belgeler"""

    DOCUMENT_TYPES = [
        ("contract", "Sözleşme"),
        ("tax_return", "Beyanname"),
        ("financial_statement", "Mali Tablo"),
        ("invoice", "Fatura"),
        ("receipt", "Fiş/Makbuz"),
        ("correspondence", "Yazışma"),
        ("report", "Rapor"),
        ("certificate", "Sertifika"),
        ("other", "Diğer"),
    ]

    taxpayer = models.ForeignKey(
        TaxpayerProfile, on_delete=models.CASCADE, related_name="documents"
    )
    uploaded_by = models.ForeignKey(
        AdvisorProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents",
    )

    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200, verbose_name="Başlık")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    file = models.FileField(upload_to="client_documents/", verbose_name="Dosya")
    file_size = models.IntegerField(
        null=True, blank=True, verbose_name="Dosya Boyutu (bytes)"
    )

    # Metadata
    document_date = models.DateField(null=True, blank=True, verbose_name="Belge Tarihi")
    tags = models.JSONField(default=list, blank=True, verbose_name="Etiketler")

    # Güvenlik
    is_confidential = models.BooleanField(default=True)
    access_log = models.JSONField(default=list, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Müşteri Dokümanı"
        verbose_name_plural = "Müşteri Dokümanları"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title} - {self.taxpayer.name}"


class AdvisorTask(models.Model):
    """Danışman görevleri - yapılacaklar listesi"""

    TASK_TYPES = [
        ("tax_filing", "Vergi Beyanı"),
        ("report_preparation", "Rapor Hazırlama"),
        ("document_review", "Doküman İnceleme"),
        ("client_meeting", "Müşteri Görüşmesi"),
        ("follow_up", "Takip"),
        ("research", "Araştırma"),
        ("admin", "İdari İş"),
    ]

    PRIORITY_LEVELS = [
        ("low", "Düşük"),
        ("medium", "Orta"),
        ("high", "Yüksek"),
        ("urgent", "Acil"),
    ]

    advisor = models.ForeignKey(
        AdvisorProfile, on_delete=models.CASCADE, related_name="tasks"
    )
    taxpayer = models.ForeignKey(
        TaxpayerProfile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="advisor_tasks",
    )

    task_type = models.CharField(max_length=30, choices=TASK_TYPES)
    title = models.CharField(max_length=200, verbose_name="Görev Başlığı")
    description = models.TextField(verbose_name="Açıklama")
    priority = models.CharField(
        max_length=20, choices=PRIORITY_LEVELS, default="medium"
    )

    # Tarihler
    due_date = models.DateField(verbose_name="Termin Tarihi")
    completed_at = models.DateTimeField(null=True, blank=True)

    # Durum
    is_completed = models.BooleanField(default=False)
    completion_notes = models.TextField(blank=True)

    # Bildirimler
    reminder_sent = models.BooleanField(default=False)
    reminder_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Danışman Görevi"
        verbose_name_plural = "Danışman Görevleri"
        ordering = ["due_date", "-priority"]

    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
