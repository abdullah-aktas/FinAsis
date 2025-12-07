# -*- coding: utf-8 -*-
"""
Mali Müşavir Danışmanlık Marketplace Modelleri
FinAsis Mali Müşavir Marketplace Sistemi
"""
import logging
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count

from .models import AdvisorProfile

logger = logging.getLogger(__name__)


class ConsultantProfile(models.Model):
    """
    Mali Müşavir Marketplace Profili
    Sisteme kayıtlı mali müşavirler için genişletilmiş profil
    """

    APPROVAL_STATUS = [
        ("pending", "Onay Bekliyor"),
        ("under_review", "İnceleniyor"),
        ("approved", "Onaylandı"),
        ("rejected", "Reddedildi"),
        ("suspended", "Askıya Alındı"),
        ("banned", "Yasaklandı"),
    ]

    AVAILABILITY_STATUS = [
        ("available", "Müsait"),
        ("busy", "Meşgul"),
        ("on_vacation", "Tatilde"),
        ("limited", "Sınırlı Müsaitlik"),
    ]

    # Ana ilişkiler
    advisor = models.OneToOneField(
        AdvisorProfile,
        on_delete=models.CASCADE,
        related_name="marketplace_profile",
        verbose_name="Danışman Profili",
    )

    # Onay sistemi
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default="pending",
        verbose_name="Onay Durumu",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_consultants",
        verbose_name="Onaylayan",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Onay Tarihi"
    )
    rejection_reason = models.TextField(blank=True, verbose_name="Red Nedeni")

    # Zorunlu Belgeler (Kayıt sırasında)
    diploma_document = models.FileField(
        upload_to="consultant_documents/diplomas/",
        verbose_name="Diploma/Mezuniyet Belgesi",
        help_text="Üniversite diploma veya mezuniyet belgesi (Zorunlu)",
    )
    graduation_document = models.FileField(
        upload_to="consultant_documents/graduation/",
        verbose_name="Mezuniyet Belgesi",
        help_text="Mezuniyet belgesi/transkript (Zorunlu)",
    )
    diploma_verified = models.BooleanField(
        default=False, verbose_name="Diploma Doğrulandı"
    )
    graduation_verified = models.BooleanField(
        default=False, verbose_name="Mezuniyet Doğrulandı"
    )
    documents_verified_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Belge Doğrulama Tarihi"
    )
    documents_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="verified_consultant_documents_set",
        verbose_name="Belgeleri Doğrulayan",
    )

    # Blockchain Anlaşma
    blockchain_contract_address = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Blockchain Sözleşme Adresi",
        help_text="Platform ile mali müşavir arasındaki blockchain anlaşma adresi",
    )
    blockchain_transaction_hash = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Blockchain İşlem Hash",
        help_text="Anlaşmanın blockchain üzerindeki işlem hash'i",
    )
    blockchain_contract_created_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Blockchain Anlaşma Tarihi"
    )
    blockchain_contract_terms = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Anlaşma Şartları",
        help_text="Blockchain'e kaydedilen anlaşma şartları",
    )

    # Profil bilgileri
    display_name = models.CharField(max_length=200, verbose_name="Görünür İsim")
    bio = models.TextField(verbose_name="Biyografi")
    profile_photo = models.ImageField(
        upload_to="consultant_photos/",
        null=True,
        blank=True,
        verbose_name="Profil Fotoğrafı",
    )

    # İletişim
    office_address = models.TextField(blank=True, verbose_name="Ofis Adresi")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    website = models.URLField(blank=True, verbose_name="Website")

    # Uzmanlık alanları
    specializations = models.JSONField(default=list, verbose_name="Uzmanlık Alanları")
    languages = models.JSONField(default=list, verbose_name="Konuşulan Diller")

    # Deneyim
    years_of_experience = models.IntegerField(default=0, verbose_name="Deneyim (Yıl)")
    education = models.JSONField(default=list, verbose_name="Eğitim")
    certifications = models.JSONField(default=list, verbose_name="Sertifikalar")

    # Müsaitlik
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default="available",
        verbose_name="Müsaitlik Durumu",
    )
    working_hours = models.JSONField(
        default=dict,
        verbose_name="Çalışma Saatleri",
        help_text="Haftanın günleri ve saatler",
    )

    # Fiyatlandırma
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Saatlik Ücret",
    )
    currency = models.CharField(max_length=3, default="TRY")

    # Platform ücreti - sistem komisyonu
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("15.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        verbose_name="Komisyon Oranı (%)",
        help_text="FinAsis platform komisyonu",
    )

    # İstatistikler
    total_consultations = models.IntegerField(
        default=0, verbose_name="Toplam Danışmanlık"
    )
    completed_consultations = models.IntegerField(
        default=0, verbose_name="Tamamlanan Danışmanlık"
    )
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Toplam Kazanç",
    )

    # Değerlendirme
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Ortalama Puan",
    )
    total_reviews = models.IntegerField(default=0, verbose_name="Toplam Değerlendirme")

    # Öne çıkarma
    is_featured = models.BooleanField(default=False, verbose_name="Öne Çıkan")
    featured_until = models.DateTimeField(
        null=True, blank=True, verbose_name="Öne Çıkma Süresi"
    )

    # Platform ayarları
    accepts_new_clients = models.BooleanField(
        default=True, verbose_name="Yeni Müşteri Kabul Ediyor"
    )
    instant_booking = models.BooleanField(
        default=False,
        verbose_name="Anında Rezervasyon",
        help_text="Müşteriler onay beklemeden randevu alabilir",
    )

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mali Müşavir Profili (Marketplace)"
        verbose_name_plural = "Mali Müşavir Profilleri (Marketplace)"
        ordering = ["-is_featured", "-average_rating", "display_name"]

    def __str__(self):
        return f"{self.display_name} - {self.city}"

    def is_available(self):
        """Mali müşavirin müsait olup olmadığını kontrol et"""
        return (
            self.approval_status == "approved"
            and self.diploma_verified
            and self.graduation_verified
            and self.blockchain_contract_address
            and self.availability_status  # Blockchain anlaşması yapılmış mı
            == "available"
            and self.accepts_new_clients
        )

    def calculate_commission(self, amount):
        """Belirli bir tutar için komisyon hesapla"""
        return amount * (self.commission_rate / 100)

    def update_rating(self):
        """Ortalama puanı güncelle"""
        ratings = self.reviews.aggregate(avg=Avg("rating"), count=Count("id"))
        self.average_rating = ratings["avg"] or Decimal("0.00")
        self.total_reviews = ratings["count"]
        self.save(update_fields=["average_rating", "total_reviews"])

    def documents_complete(self):
        """Tüm zorunlu belgeler yüklenmiş mi?"""
        return bool(self.diploma_document and self.graduation_document)

    def documents_all_verified(self):
        """Tüm belgeler doğrulanmış mı?"""
        return self.diploma_verified and self.graduation_verified

    def can_be_approved(self):
        """Onaylanabilir mi? (Belge kontrolü)"""
        return self.documents_complete() and self.documents_all_verified()


class ConsultantService(models.Model):
    """
    Mali Müşavir Hizmet Paketleri
    """

    SERVICE_CATEGORIES = [
        ("tax_consulting", "Vergi Danışmanlığı"),
        ("accounting", "Muhasebe Hizmetleri"),
        ("audit", "Denetim"),
        ("financial_planning", "Mali Planlama"),
        ("business_advisory", "İş Danışmanlığı"),
        ("compliance", "Uyumluluk"),
        ("payroll", "Bordrolama"),
        ("bookkeeping", "Defter Tutma"),
        ("tax_filing", "Vergi Beyanı"),
        ("financial_analysis", "Mali Analiz"),
    ]

    PRICING_TYPE = [
        ("hourly", "Saatlik"),
        ("fixed", "Sabit Fiyat"),
        ("monthly", "Aylık Paket"),
        ("project", "Proje Bazlı"),
    ]

    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="Mali Müşavir",
    )

    # Hizmet detayları
    title = models.CharField(max_length=200, verbose_name="Hizmet Başlığı")
    category = models.CharField(
        max_length=30, choices=SERVICE_CATEGORIES, verbose_name="Kategori"
    )
    description = models.TextField(verbose_name="Açıklama")

    # Fiyatlandırma
    pricing_type = models.CharField(
        max_length=20, choices=PRICING_TYPE, verbose_name="Fiyatlandırma Tipi"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Fiyat",
    )
    currency = models.CharField(max_length=3, default="TRY")

    # Süre
    duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Süre (Dakika)",
        help_text="Saatlik hizmetler için",
    )
    estimated_delivery_days = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Tahmini Teslim (Gün)",
        help_text="Proje bazlı hizmetler için",
    )

    # Dahil olan hizmetler
    includes = models.JSONField(default=list, verbose_name="Dahil Olanlar")

    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    # İstatistikler
    total_orders = models.IntegerField(default=0, verbose_name="Toplam Sipariş")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mali Müşavir Hizmeti"
        verbose_name_plural = "Mali Müşavir Hizmetleri"
        ordering = ["consultant", "category", "title"]

    def __str__(self):
        return f"{self.consultant.display_name} - {self.title}"


class ConsultationBooking(models.Model):
    """
    Danışmanlık Randevuları
    """

    STATUS_CHOICES = [
        ("pending", "Onay Bekliyor"),
        ("confirmed", "Onaylandı"),
        ("cancelled_by_client", "Müşteri İptal Etti"),
        ("cancelled_by_consultant", "Mali Müşavir İptal Etti"),
        ("completed", "Tamamlandı"),
        ("no_show", "Katılmadı"),
        ("rescheduled", "Ertelendi"),
    ]

    MEETING_TYPE = [
        ("online", "Online Görüşme"),
        ("in_person", "Yüz Yüze"),
        ("phone", "Telefon"),
    ]

    VIDEO_PROVIDER_CHOICES = [
        ("finasis", "FinAsis (Dahili)"),
        ("jitsi", "Jitsi"),
        ("zoom", "Zoom"),
        ("google_meet", "Google Meet"),
    ]

    # Taraflar
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultant_bookings",
        verbose_name="Müşteri",
    )
    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Mali Müşavir",
    )
    service = models.ForeignKey(
        ConsultantService,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Hizmet",
    )

    # Randevu detayları
    booking_number = models.CharField(
        max_length=50, unique=True, verbose_name="Randevu No"
    )
    meeting_type = models.CharField(
        max_length=20, choices=MEETING_TYPE, default="online"
    )
    video_provider = models.CharField(
        max_length=30,
        choices=VIDEO_PROVIDER_CHOICES,
        default="finasis",
        verbose_name="Video Sağlayıcısı",
    )

    # Zamanlama
    scheduled_date = models.DateField(verbose_name="Randevu Tarihi")
    scheduled_time = models.TimeField(verbose_name="Randevu Saati")
    duration_minutes = models.IntegerField(default=60, verbose_name="Süre (Dakika)")
    timezone = models.CharField(max_length=50, default="Europe/Istanbul")

    # Durum
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")

    # Görüşme bilgileri
    subject = models.CharField(max_length=200, verbose_name="Konu")
    description = models.TextField(verbose_name="Detaylar")

    # Online görüşme
    meeting_url = models.URLField(blank=True, verbose_name="Görüşme Linki")
    meeting_id = models.CharField(max_length=200, blank=True, verbose_name="Görüşme ID")
    meeting_password = models.CharField(max_length=100, blank=True)
    education_meeting = models.OneToOneField(
        "education.Meeting",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="consultation_booking",
        verbose_name="FinAsis Toplantısı",
    )

    # Fiziksel görüşme
    meeting_address = models.TextField(blank=True, verbose_name="Görüşme Adresi")

    # Görüşme kayıtları
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    consultant_notes = models.TextField(blank=True, verbose_name="Mali Müşavir Notları")

    # Fiyatlandırma
    quoted_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Teklif Edilen Fiyat"
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Nihai Fiyat",
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Komisyon Tutarı",
    )
    consultant_earning = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Mali Müşavir Kazancı",
    )

    # Ödeme
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Ödeme Bekliyor"),
            ("paid", "Ödendi"),
            ("refunded", "İade Edildi"),
        ],
        default="pending",
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    # Hatırlatmalar
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    # İptal
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Danışmanlık Randevusu"
        verbose_name_plural = "Danışmanlık Randevuları"
        ordering = ["-scheduled_date", "-scheduled_time"]
        indexes = [
            models.Index(fields=["consultant", "scheduled_date", "status"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["booking_number"]),
        ]

    def __str__(self):
        return f"{self.booking_number} - {self.client.username} → {self.consultant.display_name}"

    def calculate_commission(self):
        """Komisyon hesapla"""
        if self.final_price:
            price = self.final_price
        else:
            price = self.quoted_price

        self.commission_amount = self.consultant.calculate_commission(price)
        self.consultant_earning = price - self.commission_amount
        self.save(update_fields=["commission_amount", "consultant_earning"])

    def confirm(self):
        """Randevuyu onayla"""
        self.status = "confirmed"
        self.save(update_fields=["status"])
        self.ensure_online_meeting()

    def complete(self):
        """Randevuyu tamamla"""
        self.status = "completed"
        if not self.actual_end_time:
            self.actual_end_time = timezone.now()
        self.save(update_fields=["status", "actual_end_time"])

        # İstatistikleri güncelle
        self.consultant.completed_consultations += 1
        self.consultant.total_consultations += 1
        self.consultant.save(
            update_fields=["completed_consultations", "total_consultations"]
        )
        self._sync_meeting_status("completed")

    # ------------------------------------------------------------------
    # Video toplantı yardımcıları
    # ------------------------------------------------------------------
    def ensure_online_meeting(
        self, provider_name: str | None = None, force: bool = False
    ) -> None:
        """
        Online randevu için FinAsis içi toplantı oluşturur.
        """
        if self.meeting_type != "online":
            return
        if not force and self.meeting_url:
            return
        from advisors.services.video_conference import create_meeting_for_booking

        try:
            create_meeting_for_booking(
                self,
                provider_name=provider_name or getattr(self, "video_provider", None),
            )
        except Exception:
            logger.exception(
                "Randevu için toplantı oluşturulamadı (booking=%s)", self.pk
            )

    def cancel_online_meeting(self) -> None:
        """Online toplantıyı iptal eder."""
        if not self.meeting_id:
            return
        from advisors.services.video_conference import cancel_meeting_for_booking

        try:
            cancel_meeting_for_booking(
                self, provider_name=getattr(self, "video_provider", None)
            )
        except Exception:
            logger.exception(
                "Randevu toplantısı iptal edilirken hata oluştu (booking=%s)", self.pk
            )

    def _sync_meeting_status(self, status: str) -> None:
        """Education.Meeting kaydını eşitle."""
        meeting = getattr(self, "education_meeting", None)
        if not meeting:
            return
        try:
            if meeting.status != status:
                meeting.status = status
                if status == "completed" and not meeting.end_time:
                    meeting.end_time = timezone.now()
                meeting.save(update_fields=["status", "end_time"])
        except Exception:
            logger.exception(
                "Education toplantı durumu güncellenemedi (meeting=%s)",
                getattr(meeting, "pk", None),
            )


class ConsultationPayment(models.Model):
    """
    Danışmanlık Ödemeleri
    Müşteriden alınan ödemeler ve mali müşavire yapılan ödemeler
    """

    PAYMENT_TYPE = [
        ("booking", "Randevu Ödemesi"),
        ("service", "Hizmet Ödemesi"),
        ("package", "Paket Ödemesi"),
    ]

    PAYMENT_STATUS = [
        ("pending", "Bekliyor"),
        ("processing", "İşleniyor"),
        ("completed", "Tamamlandı"),
        ("failed", "Başarısız"),
        ("refunded", "İade Edildi"),
        ("partially_refunded", "Kısmi İade"),
    ]

    PAYMENT_METHOD = [
        ("credit_card", "Kredi Kartı"),
        ("debit_card", "Banka Kartı"),
        ("bank_transfer", "Havale/EFT"),
        ("wallet", "Cüzdan"),
    ]

    # İlişkiler
    booking = models.OneToOneField(
        ConsultationBooking,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name="Randevu",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultation_payments",
        verbose_name="Müşteri",
    )
    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="received_payments",
        verbose_name="Mali Müşavir",
    )

    # Ödeme detayları
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE, default="booking"
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)

    # Tutarlar
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tutar")
    commission = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Komisyon"
    )
    consultant_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Mali Müşavir Tutarı"
    )
    currency = models.CharField(max_length=3, default="TRY")

    # Durum
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")

    # Gateway bilgileri
    gateway_name = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(
        max_length=200, blank=True, verbose_name="İşlem ID"
    )
    gateway_response = models.JSONField(default=dict, blank=True)

    # Zaman damgaları
    paid_at = models.DateTimeField(null=True, blank=True)
    payout_to_consultant_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Mali Müşavire Ödeme Tarihi"
    )

    # İade
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="İade Tutarı",
    )
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Danışmanlık Ödemesi"
        verbose_name_plural = "Danışmanlık Ödemeleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.booking.booking_number} - {self.amount} {self.currency}"

    def process_payment(self):
        """Ödemeyi işle"""
        self.status = "completed"
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])

        # Randevu durumunu güncelle
        self.booking.payment_status = "paid"
        self.booking.paid_at = self.paid_at
        self.booking.save(update_fields=["payment_status", "paid_at"])


class ConsultantContract(models.Model):
    """
    Mali Müşavir - Müşteri Sözleşmeleri
    """

    CONTRACT_TYPE = [
        ("one_time", "Tek Seferlik"),
        ("monthly", "Aylık"),
        ("quarterly", "Üç Aylık"),
        ("annual", "Yıllık"),
        ("project", "Proje Bazlı"),
    ]

    STATUS_CHOICES = [
        ("draft", "Taslak"),
        ("sent", "Gönderildi"),
        ("signed", "İmzalandı"),
        ("active", "Aktif"),
        ("completed", "Tamamlandı"),
        ("terminated", "Feshedildi"),
        ("expired", "Süresi Doldu"),
    ]

    # Taraflar
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultant_contracts",
        verbose_name="Müşteri",
    )
    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="client_contracts",
        verbose_name="Mali Müşavir",
    )

    # Sözleşme bilgileri
    contract_number = models.CharField(
        max_length=50, unique=True, verbose_name="Sözleşme No"
    )
    contract_type = models.CharField(
        max_length=20, choices=CONTRACT_TYPE, verbose_name="Sözleşme Tipi"
    )

    # İçerik
    title = models.CharField(max_length=200, verbose_name="Başlık")
    scope_of_work = models.TextField(verbose_name="İş Kapsamı")
    terms_and_conditions = models.TextField(verbose_name="Şartlar ve Koşullar")
    deliverables = models.JSONField(default=list, verbose_name="Teslim Edilecekler")

    # Finansal
    contract_value = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Sözleşme Bedeli"
    )
    payment_terms = models.TextField(verbose_name="Ödeme Koşulları")
    payment_schedule = models.JSONField(default=list, verbose_name="Ödeme Planı")

    # Tarihler
    start_date = models.DateField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateField(verbose_name="Bitiş Tarihi")

    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # İmzalar
    client_signed_at = models.DateTimeField(null=True, blank=True)
    consultant_signed_at = models.DateTimeField(null=True, blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    consultant_ip = models.GenericIPAddressField(null=True, blank=True)

    # Dosyalar
    contract_document = models.FileField(
        upload_to="consultant_contracts/",
        null=True,
        blank=True,
        verbose_name="Sözleşme Belgesi",
    )
    signed_document = models.FileField(
        upload_to="consultant_contracts/signed/",
        null=True,
        blank=True,
        verbose_name="İmzalı Sözleşme",
    )
    attachments = models.JSONField(default=list, verbose_name="Ekler")

    # Otomatik yenileme
    auto_renew = models.BooleanField(default=False, verbose_name="Otomatik Yenileme")
    renewal_notice_days = models.IntegerField(default=30)

    # Fesih
    termination_reason = models.TextField(blank=True)
    terminated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="terminated_consultant_contracts",
    )
    terminated_at = models.DateTimeField(null=True, blank=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mali Müşavir Sözleşmesi"
        verbose_name_plural = "Mali Müşavir Sözleşmeleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.contract_number} - {self.client.username} ↔ {self.consultant.display_name}"

    def is_fully_signed(self):
        """Sözleşme her iki tarafça da imzalandı mı?"""
        return (
            self.client_signed_at is not None and self.consultant_signed_at is not None
        )

    def activate(self):
        """Sözleşmeyi aktif et"""
        if self.is_fully_signed():
            self.status = "active"
            self.save(update_fields=["status"])


class ConsultantReview(models.Model):
    """
    Mali Müşavir Değerlendirmeleri
    """

    # İlişkiler
    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Mali Müşavir",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultant_reviews",
        verbose_name="Müşteri",
    )
    booking = models.OneToOneField(
        ConsultationBooking,
        on_delete=models.CASCADE,
        related_name="review",
        verbose_name="Randevu",
    )

    # Değerlendirme
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Puan"
    )

    # Detaylı puanlar
    professionalism_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Profesyonellik",
    )
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="İletişim"
    )
    expertise_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Uzmanlık"
    )
    value_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Fiyat/Performans",
    )

    # Yorum
    title = models.CharField(max_length=200, verbose_name="Başlık")
    comment = models.TextField(verbose_name="Yorum")

    # Mali müşavir yanıtı
    consultant_response = models.TextField(
        blank=True, verbose_name="Mali Müşavir Yanıtı"
    )
    consultant_responded_at = models.DateTimeField(null=True, blank=True)

    # Durum
    is_verified = models.BooleanField(default=True, verbose_name="Doğrulanmış")
    is_featured = models.BooleanField(default=False, verbose_name="Öne Çıkan")
    is_published = models.BooleanField(default=True, verbose_name="Yayında")

    # Faydalılık
    helpful_count = models.IntegerField(default=0, verbose_name="Faydalı Sayısı")
    not_helpful_count = models.IntegerField(default=0, verbose_name="Faydasız Sayısı")

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mali Müşavir Değerlendirmesi"
        verbose_name_plural = "Mali Müşavir Değerlendirmeleri"
        ordering = ["-created_at"]
        unique_together = [("booking", "client")]

    def __str__(self):
        return (
            f"{self.consultant.display_name} - {self.rating}★ by {self.client.username}"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Danışman puanını güncelle
        self.consultant.update_rating()


class ConsultantAvailability(models.Model):
    """
    Mali Müşavir Müsaitlik Takvimi
    """

    DAY_OF_WEEK = [
        (0, "Pazartesi"),
        (1, "Salı"),
        (2, "Çarşamba"),
        (3, "Perşembe"),
        (4, "Cuma"),
        (5, "Cumartesi"),
        (6, "Pazar"),
    ]

    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="availability_slots",
        verbose_name="Mali Müşavir",
    )

    # Zaman
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK, verbose_name="Gün")
    start_time = models.TimeField(verbose_name="Başlangıç Saati")
    end_time = models.TimeField(verbose_name="Bitiş Saati")

    # Özel tarih (tekrarlı olmayan)
    specific_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Özel Tarih",
        help_text="Belirli bir tarih için (opsiyonel)",
    )

    # Müsaitlik
    is_available = models.BooleanField(default=True, verbose_name="Müsait")

    # Tekrarlama
    is_recurring = models.BooleanField(
        default=True, verbose_name="Tekrarlı", help_text="Her hafta tekrarlanır"
    )

    class Meta:
        verbose_name = "Mali Müşavir Müsaitlik"
        verbose_name_plural = "Mali Müşavir Müsaitlikleri"
        ordering = ["consultant", "day_of_week", "start_time"]

    def __str__(self):
        if self.specific_date:
            return f"{self.consultant.display_name} - {self.specific_date} {self.start_time}-{self.end_time}"
        return f"{self.consultant.display_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class ConsultantDocument(models.Model):
    """
    Mali Müşavir Belgeleri
    Sertifikalar, diplomalar, kimlik belgeleri vs.
    """

    DOCUMENT_TYPE = [
        ("id_card", "Kimlik"),
        ("diploma", "Diploma"),
        ("certificate", "Sertifika"),
        ("license", "Lisans/Ruhsat"),
        ("chamber_registration", "Oda Kayıt Belgesi"),
        ("tax_certificate", "Vergi Levhası"),
        ("other", "Diğer"),
    ]

    VERIFICATION_STATUS = [
        ("pending", "Beklemede"),
        ("verified", "Doğrulandı"),
        ("rejected", "Reddedildi"),
    ]

    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Mali Müşavir",
    )

    # Belge bilgisi
    document_type = models.CharField(
        max_length=30, choices=DOCUMENT_TYPE, verbose_name="Belge Tipi"
    )
    title = models.CharField(max_length=200, verbose_name="Başlık")
    description = models.TextField(blank=True, verbose_name="Açıklama")

    # Dosya
    file = models.FileField(upload_to="consultant_documents/", verbose_name="Dosya")
    file_size = models.IntegerField(null=True, blank=True)

    # Doğrulama
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default="pending",
        verbose_name="Doğrulama Durumu",
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="verified_consultant_documents",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Geçerlilik
    issue_date = models.DateField(
        null=True, blank=True, verbose_name="Düzenlenme Tarihi"
    )
    expiry_date = models.DateField(
        null=True, blank=True, verbose_name="Geçerlilik Tarihi"
    )

    # Meta
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mali Müşavir Belgesi"
        verbose_name_plural = "Mali Müşavir Belgeleri"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.consultant.display_name} - {self.get_document_type_display()}"

    def is_expired(self):
        """Belgenin süresi dolmuş mu?"""
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False


class ConsultantPayout(models.Model):
    """
    Mali Müşavir Ödemeleri (FinAsis'ten Mali Müşavire)
    """

    STATUS_CHOICES = [
        ("pending", "Bekliyor"),
        ("processing", "İşleniyor"),
        ("completed", "Tamamlandı"),
        ("failed", "Başarısız"),
        ("cancelled", "İptal Edildi"),
    ]

    consultant = models.ForeignKey(
        ConsultantProfile,
        on_delete=models.CASCADE,
        related_name="payouts",
        verbose_name="Mali Müşavir",
    )

    # Tutar
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar")
    currency = models.CharField(max_length=3, default="TRY")

    # Dönem
    period_start = models.DateField(verbose_name="Dönem Başlangıç")
    period_end = models.DateField(verbose_name="Dönem Bitiş")

    # Dahil edilen ödemeler
    included_payments = models.JSONField(
        default=list,
        verbose_name="Dahil Edilen Ödemeler",
        help_text="ConsultationPayment ID'leri",
    )

    # Banka bilgileri
    bank_name = models.CharField(max_length=100, verbose_name="Banka")
    account_holder = models.CharField(max_length=200, verbose_name="Hesap Sahibi")
    iban = models.CharField(max_length=34, verbose_name="IBAN")

    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # İşlem
    transaction_reference = models.CharField(max_length=200, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Notlar
    notes = models.TextField(blank=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mali Müşavir Ödemesi"
        verbose_name_plural = "Mali Müşavir Ödemeleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.consultant.display_name} - {self.amount} {self.currency} ({self.get_status_display()})"
