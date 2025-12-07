# -*- coding: utf-8 -*-
"""
Mali Müşavir Marketplace - Kurulum ve Test Senaryoları
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from advisors.models import AdvisorProfile
from advisors.models_marketplace import (
    ConsultantProfile,
    ConsultantService,
    ConsultationBooking,
    ConsultantReview,
)
from decimal import Decimal
from datetime import date, time, timedelta
from django.utils import timezone

User = get_user_model()

# ============================================================================
# KURULUM ADIMLARI
# ============================================================================

"""
1. ADIM: Model Migration
-----------------------
python manage.py makemigrations advisors
python manage.py migrate advisors

2. ADIM: Gerekli Paketleri Yükle
---------------------------------
pip install PyJWT requests google-api-python-client google-auth-httplib2 google-auth-oauthlib pytz

3. ADIM: Settings Yapılandırması
---------------------------------
config/settings.py dosyasına ekle:

# Video Konferans Ayarları
DEFAULT_VIDEO_PROVIDER = 'jitsi'
JITSI_DOMAIN = 'meet.jit.si'

# Opsiyonel: Zoom
ZOOM_API_KEY = 'your-key'
ZOOM_API_SECRET = 'your-secret'
ZOOM_USER_ID = 'your-user-id'

4. ADIM: URL Yapılandırması
----------------------------
Ana urls.py dosyasına ekle:

path('advisors/', include('advisors.urls')),

5. ADIM: Admin Paneli Aktif Et
-------------------------------
advisors/__init__.py veya admin.py dosyasına:

from .admin.marketplace_admin import *

6. ADIM: Superuser Oluştur ve Test
------------------------------------
python manage.py createsuperuser
python manage.py runserver

Admin panele gir: http://localhost:8000/admin/
"""

# ============================================================================
# TEST SENARYOLARI
# ============================================================================


class MarketplaceSetupTest(TestCase):
    """Marketplace kurulum testi"""

    def setUp(self):
        """Test verilerini hazırla"""
        # Admin kullanıcı
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@finasis.com", password="admin123"
        )

        # Mali müşavir kullanıcısı
        self.consultant_user = User.objects.create_user(
            username="ahmet_yilmaz",
            email="ahmet@example.com",
            password="test123",
            first_name="Ahmet",
            last_name="Yılmaz",
        )

        # AdvisorProfile oluştur
        self.advisor_profile = AdvisorProfile.objects.create(
            user=self.consultant_user,
            type="SMMM",
            chamber_no="123456",
            verified_at=timezone.now(),
        )

        # Müşteri kullanıcısı
        self.client_user = User.objects.create_user(
            username="mehmet_demir",
            email="mehmet@example.com",
            password="test123",
            first_name="Mehmet",
            last_name="Demir",
        )

    def test_01_create_consultant_profile(self):
        """Mali müşavir profili oluşturma"""
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor_profile,
            display_name="Ahmet Yılmaz SMMM",
            bio="15 yıllık deneyime sahip mali müşavir",
            city="İstanbul",
            phone="05321234567",
            specializations=["tax_consulting", "accounting", "audit"],
            languages=["Türkçe", "İngilizce"],
            years_of_experience=15,
            hourly_rate=Decimal("750.00"),
            commission_rate=Decimal("15.00"),
            approval_status="approved",
            approved_by=self.admin,
            approved_at=timezone.now(),
        )

        self.assertEqual(consultant.display_name, "Ahmet Yılmaz SMMM")
        self.assertTrue(consultant.is_available())
        print("✅ Test 1: Mali müşavir profili başarıyla oluşturuldu")

    def test_02_create_consultant_service(self):
        """Hizmet paketi oluşturma"""
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor_profile,
            display_name="Ahmet Yılmaz SMMM",
            city="İstanbul",
            hourly_rate=Decimal("750.00"),
            approval_status="approved",
        )

        service = ConsultantService.objects.create(
            consultant=consultant,
            title="Vergi Danışmanlığı Paketi",
            category="tax_consulting",
            description="KDV, Stopaj ve Gelir Vergisi danışmanlığı",
            pricing_type="hourly",
            price=Decimal("750.00"),
            duration_minutes=60,
            includes=[
                "Vergi mevzuatı danışmanlığı",
                "Beyanname kontrolü",
                "Optimizasyon önerileri",
            ],
        )

        self.assertEqual(service.title, "Vergi Danışmanlığı Paketi")
        print("✅ Test 2: Hizmet paketi başarıyla oluşturuldu")

    def test_03_create_booking(self):
        """Randevu oluşturma"""
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor_profile,
            display_name="Ahmet Yılmaz SMMM",
            city="İstanbul",
            hourly_rate=Decimal("750.00"),
            approval_status="approved",
            instant_booking=True,
        )

        booking = ConsultationBooking.objects.create(
            booking_number="BK-TEST001",
            client=self.client_user,
            consultant=consultant,
            meeting_type="online",
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
            duration_minutes=60,
            subject="KDV Beyanı Danışmanlığı",
            description="KDV beyanı ile ilgili sorularım var",
            quoted_price=Decimal("750.00"),
            status="confirmed",  # instant_booking=True olduğu için
        )

        # Komisyon hesapla
        booking.calculate_commission()

        self.assertEqual(booking.status, "confirmed")
        self.assertEqual(booking.commission_amount, Decimal("112.50"))  # %15
        self.assertEqual(booking.consultant_earning, Decimal("637.50"))
        print("✅ Test 3: Randevu başarıyla oluşturuldu ve komisyon hesaplandı")

    def test_04_booking_workflow(self):
        """Randevu iş akışı testi"""
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor_profile,
            display_name="Ahmet Yılmaz SMMM",
            city="İstanbul",
            hourly_rate=Decimal("750.00"),
            approval_status="approved",
        )

        # 1. Randevu oluştur (pending)
        booking = ConsultationBooking.objects.create(
            booking_number="BK-TEST002",
            client=self.client_user,
            consultant=consultant,
            meeting_type="online",
            scheduled_date=date.today() + timedelta(days=3),
            scheduled_time=time(10, 0),
            duration_minutes=60,
            subject="Mali Tablo İncelemesi",
            description="Şirket mali tablolarımı incelemek istiyorum",
            quoted_price=Decimal("1000.00"),
        )

        self.assertEqual(booking.status, "pending")

        # 2. Mali müşavir onayla
        booking.confirm()
        self.assertEqual(booking.status, "confirmed")

        # 3. Görüşmeyi başlat
        booking.actual_start_time = timezone.now()
        booking.save()

        # 4. Görüşmeyi tamamla
        booking.actual_end_time = timezone.now() + timedelta(hours=1)
        booking.consultant_notes = (
            "Müşterinin mali tabloları incelendi. Öneriler verildi."
        )
        booking.complete()

        self.assertEqual(booking.status, "completed")
        self.assertEqual(consultant.completed_consultations, 1)
        print("✅ Test 4: Randevu iş akışı başarıyla tamamlandı")

    def test_05_create_review(self):
        """Değerlendirme oluşturma"""
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor_profile,
            display_name="Ahmet Yılmaz SMMM",
            city="İstanbul",
            hourly_rate=Decimal("750.00"),
            approval_status="approved",
        )

        booking = ConsultationBooking.objects.create(
            booking_number="BK-TEST003",
            client=self.client_user,
            consultant=consultant,
            meeting_type="online",
            scheduled_date=date.today(),
            scheduled_time=time(14, 0),
            duration_minutes=60,
            subject="Danışmanlık",
            description="Test",
            quoted_price=Decimal("750.00"),
            status="completed",
        )

        ConsultantReview.objects.create(
            consultant=consultant,
            client=self.client_user,
            booking=booking,
            rating=5,
            professionalism_rating=5,
            communication_rating=5,
            expertise_rating=5,
            value_rating=4,
            title="Harika Deneyim",
            comment="Çok profesyonel ve yardımcı oldu. Kesinlikle tavsiye ederim.",
        )

        # Rating otomatik güncellendi mi?
        consultant.refresh_from_db()
        self.assertEqual(consultant.total_reviews, 1)
        self.assertGreater(consultant.average_rating, Decimal("0"))
        print("✅ Test 5: Değerlendirme başarıyla oluşturuldu")

    def test_06_commission_calculation(self):
        """Komisyon hesaplama testi"""
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor_profile,
            display_name="Ahmet Yılmaz SMMM",
            city="İstanbul",
            hourly_rate=Decimal("750.00"),
            commission_rate=Decimal("15.00"),
            approval_status="approved",
        )

        test_cases = [
            (Decimal("1000.00"), Decimal("150.00")),  # %15
            (Decimal("500.00"), Decimal("75.00")),
            (Decimal("2000.00"), Decimal("300.00")),
        ]

        for amount, expected_commission in test_cases:
            commission = consultant.calculate_commission(amount)
            self.assertEqual(commission, expected_commission)

        print("✅ Test 6: Komisyon hesaplamaları doğru çalışıyor")

    def test_07_availability_check(self):
        """Müsaitlik kontrolü"""
        # Onaylı ve müsait
        consultant1 = ConsultantProfile.objects.create(
            advisor=self.advisor_profile,
            display_name="Müsait Mali Müşavir",
            city="İstanbul",
            hourly_rate=Decimal("750.00"),
            approval_status="approved",
            availability_status="available",
            accepts_new_clients=True,
        )
        self.assertTrue(consultant1.is_available())

        # Onaysız
        consultant2 = ConsultantProfile.objects.create(
            advisor=AdvisorProfile.objects.create(
                user=User.objects.create_user("test2", "test2@test.com", "test"),
                type="SMMM",
            ),
            display_name="Onaysız Mali Müşavir",
            city="İstanbul",
            hourly_rate=Decimal("750.00"),
            approval_status="pending",
        )
        self.assertFalse(consultant2.is_available())

        print("✅ Test 7: Müsaitlik kontrolü doğru çalışıyor")


class MarketplaceAPITest(TestCase):
    """API endpoint testleri"""

    def setUp(self):
        self.client = Client()

        # Test kullanıcıları oluştur
        self.consultant_user = User.objects.create_user(
            username="consultant", password="test123"
        )

        self.advisor_profile = AdvisorProfile.objects.create(
            user=self.consultant_user, type="SMMM"
        )

        self.consultant = ConsultantProfile.objects.create(
            advisor=self.advisor_profile,
            display_name="Test Consultant",
            city="İstanbul",
            hourly_rate=Decimal("750.00"),
            approval_status="approved",
        )

        self.client_user = User.objects.create_user(
            username="client", password="test123"
        )

    def test_consultant_list_api(self):
        """Mali müşavir listesi API"""
        response = self.client.get("/advisors/marketplace/api/consultants/")
        self.assertEqual(response.status_code, 200)
        print("✅ API Test 1: Consultant list endpoint çalışıyor")

    def test_consultant_detail_api(self):
        """Mali müşavir detay API"""
        response = self.client.get(
            f"/advisors/marketplace/api/consultants/{self.consultant.id}/"
        )
        self.assertEqual(response.status_code, 200)
        print("✅ API Test 2: Consultant detail endpoint çalışıyor")


# ============================================================================
# MANUEL TEST SENARYOLARI
# ============================================================================

"""
SENARYO 1: Mali Müşavir Kaydı ve Onayı
---------------------------------------

1. Admin panelden yeni AdvisorProfile oluştur
2. Mali müşavir kullanıcı olarak giriş yap
3. Marketplace profili oluştur:
   - /advisors/marketplace/api/consultants/ (POST)
   - Profil bilgilerini doldur
4. Belgeleri yükle (Oda kayıt, diploma, vs.)
5. Admin panelden profili onayla
6. Mali müşavir profili artık listede görünür

SENARYO 2: Müşteri Randevu Alma
-------------------------------

1. Müşteri olarak giriş yap
2. Mali müşavirleri listele ve filtrele:
   GET /advisors/marketplace/api/consultants/?city=İstanbul&specialization=tax_consulting
3. Mali müşavir detayını incele
4. Hizmetlerini ve müsaitlik takvimini gör
5. Randevu oluştur:
   POST /advisors/marketplace/api/bookings/
   {
       "consultant": 1,
       "scheduled_date": "2025-11-20",
       "scheduled_time": "14:00:00",
       "subject": "Vergi Danışmanlığı",
       ...
   }
6. Ödeme yap (integration gerekli)
7. Randevu onayını bekle veya anında onayla (instant_booking)

SENARYO 3: Mali Müşavir Randevu Yönetimi
----------------------------------------

1. Mali müşavir olarak giriş yap
2. Bekleyen randevuları görüntüle:
   GET /advisors/marketplace/api/bookings/?status=pending
3. Randevuyu onayla:
   POST /advisors/marketplace/api/bookings/{id}/confirm/
4. Video toplantı linki otomatik oluşturuldu
5. Randevu zamanı geldiğinde görüşmeyi başlat
6. Görüşme sonrası notları ekle ve tamamla:
   POST /advisors/marketplace/api/bookings/{id}/complete/

SENARYO 4: Değerlendirme ve Puan Sistemi
----------------------------------------

1. Müşteri olarak tamamlanmış randevu için değerlendirme yap:
   POST /advisors/marketplace/api/reviews/
   {
       "booking": 123,
       "rating": 5,
       "professionalism_rating": 5,
       "communication_rating": 5,
       "expertise_rating": 5,
       "value_rating": 4,
       "title": "Harika",
       "comment": "Çok memnun kaldım"
   }
2. Mali müşavir puanı otomatik güncellenir
3. Mali müşavir değerlendirmeye yanıt verebilir:
   POST /advisors/marketplace/api/reviews/{id}/respond/

SENARYO 5: Ödeme ve Komisyon
----------------------------

1. Müşteri randevu için ödeme yapar
2. Sistem komisyonu otomatik keser (%15)
3. Mali müşavir kazancı hesaplanır
4. Belirli periyotlarda (aylık) mali müşavire ödeme yapılır:
   - Admin panelden ConsultantPayout oluştur
   - Banka bilgilerini ekle
   - Ödemeyi işaretle ve tamamla

SENARYO 6: Dashboard İstatistikleri
-----------------------------------

1. Mali müşavir dashboard:
   GET /advisors/marketplace/api/consultant/dashboard/stats/
   
   Gösterilen bilgiler:
   - Toplam kazanç
   - Bekleyen kazanç
   - Bu ay kazanç
   - Toplam/tamamlanan randevular
   - Ortalama puan
   - Toplam müşteri sayısı

2. Müşteri dashboard:
   GET /advisors/marketplace/api/client/dashboard/stats/
   
   Gösterilen bilgiler:
   - Toplam/tamamlanan randevular
   - Toplam harcama
   - Aktif sözleşmeler
   - Favori mali müşavirler
"""

# ============================================================================
# PERFORMANS VE GÜVENLİK TESTLERİ
# ============================================================================

"""
PERFORMANS TESTİ
---------------

1. Load Testing:
   - 100 eşzamanlı mali müşavir listesi isteği
   - Response time < 500ms olmalı

2. Database Query Optimizasyonu:
   - select_related ve prefetch_related kullanımı
   - N+1 query problemi kontrolü

3. Caching:
   - Mali müşavir listesi için cache (5 dakika)
   - Redis kullanımı önerilir

GÜVENLİK TESTİ
-------------

1. Authentication:
   - JWT token kontrolü
   - Token expiry testi

2. Authorization:
   - Sadece kendi randevularını görebilme
   - Admin yetkisi gerektiren işlemler

3. Input Validation:
   - SQL Injection testi
   - XSS testi
   - CSRF token kontrolü

4. Rate Limiting:
   - API endpoint'lerine rate limit uygula
   - DRF throttling kullan
"""

if __name__ == "__main__":
    print("=" * 80)
    print("FINASIS MALİ MÜŞAVİR MARKETPLACE - KURULUM VE TEST")
    print("=" * 80)
    print("\n1. Migration komutlarını çalıştır")
    print("2. Test senaryolarını çalıştır: python manage.py test advisors.tests")
    print("3. Manuel test senaryolarını uygula")
    print("4. Admin panelden sistem ayarlarını kontrol et")
    print("\nDetaylı bilgi için: advisors/MARKETPLACE_README.md")
    print("=" * 80)
