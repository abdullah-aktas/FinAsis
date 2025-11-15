# Mali Müşavir Danışmanlık Marketplace Sistemi

## 📋 Genel Bakış

FinAsis Mali Müşavir Danışmanlık Marketplace, mükelleflerin online ortamda mali müşavirlerle buluşmasını, randevu almasını ve danışmanlık hizmeti almasını sağlayan kapsamlı bir platformdur.

### 🎯 Temel Özellikler

- ✅ Mali müşavir profil yönetimi ve onay sistemi
- ✅ Online randevu ve görüşme sistemi
- ✅ Video konferans entegrasyonu (Zoom, Jitsi, Google Meet)
- ✅ Ödeme ve komisyon yönetimi
- ✅ Sözleşme oluşturma ve dijital imza
- ✅ Değerlendirme ve inceleme sistemi
- ✅ Mali müşavir müsaitlik takvimi
- ✅ Dashboard ve istatistikler
- ✅ Belge doğrulama sistemi

## 🏗️ Mimari

### Modeller

#### 1. ConsultantProfile

Mali müşavir marketplace profili. Temel `AdvisorProfile` modeline ek olarak marketplace özellikleri içerir.

**Önemli Alanlar:**

- `approval_status`: Onay durumu (pending, approved, rejected, etc.)
- `hourly_rate`: Saatlik ücret
- `commission_rate`: Platform komisyon oranı (%)
- `average_rating`: Ortalama puan
- `specializations`: Uzmanlık alanları (JSON)

#### 2. ConsultantService

Mali müşavirlerin sunduğu hizmet paketleri.

#### 3. ConsultationBooking

Danışmanlık randevuları. Müşteri ve mali müşavir arasındaki görüşme rezervasyonları.

#### 4. ConsultationPayment

Ödeme kayıtları. Müşteriden alınan ve mali müşavire yapılan ödemeler.

#### 5. ConsultantContract

Mali müşavir-müşteri sözleşmeleri. Dijital imza destekli.

#### 6. ConsultantReview

Müşteri değerlendirmeleri ve mali müşavir yanıtları.

#### 7. ConsultantAvailability

Mali müşavir müsaitlik takvimi.

## 🚀 Kurulum

### 1. Model Migration

```bash
python manage.py makemigrations advisors
python manage.py migrate advisors
```

### 2. URL Yapılandırması

`advisors/urls.py` dosyasına ekleyin:

```python
from advisors.urls.marketplace_urls import urlpatterns as marketplace_urls

urlpatterns = [
    # ... mevcut URL'ler
    path('marketplace/', include(marketplace_urls)),
]
```

### 3. Admin Kaydı

`advisors/admin.py` dosyasına ekleyin:

```python
from advisors.admin.marketplace_admin import *
```

### 4. Video Konferans Ayarları

`config/settings.py` dosyasına ekleyin:

```python
# Video Konferans Ayarları
DEFAULT_VIDEO_PROVIDER = 'jitsi'  # 'zoom', 'jitsi', 'google_meet'

# Zoom Ayarları (Opsiyonel)
ZOOM_API_KEY = 'your-zoom-api-key'
ZOOM_API_SECRET = 'your-zoom-api-secret'
ZOOM_USER_ID = 'your-zoom-user-id'

# Jitsi Ayarları (Varsayılan)
JITSI_DOMAIN = 'meet.jit.si'
JITSI_APP_ID = ''  # Opsiyonel
JITSI_APP_SECRET = ''  # Opsiyonel

# Google Meet Ayarları (Opsiyonel)
GOOGLE_SERVICE_ACCOUNT_FILE = 'path/to/service-account.json'
```

### 5. Gerekli Paketler

```bash
pip install PyJWT requests google-api-python-client google-auth-httplib2 google-auth-oauthlib pytz
```

## 📚 API Kullanımı

### Endpoint'ler

#### Mali Müşavir İşlemleri

```
GET    /marketplace/api/consultants/              # Tüm mali müşavirleri listele
GET    /marketplace/api/consultants/{id}/         # Mali müşavir detayı
POST   /marketplace/api/consultants/              # Yeni profil oluştur
PUT    /marketplace/api/consultants/{id}/         # Profil güncelle
GET    /marketplace/api/consultants/featured/     # Öne çıkan mali müşavirler
GET    /marketplace/api/consultants/top_rated/    # En yüksek puanlı
GET    /marketplace/api/consultants/{id}/reviews/ # Değerlendirmeler
GET    /marketplace/api/consultants/{id}/services/ # Hizmetler
```

#### Randevu İşlemleri

```
GET    /marketplace/api/bookings/              # Randevuları listele
POST   /marketplace/api/bookings/              # Yeni randevu oluştur
GET    /marketplace/api/bookings/{id}/         # Randevu detayı
POST   /marketplace/api/bookings/{id}/confirm/ # Randevuyu onayla (mali müşavir)
POST   /marketplace/api/bookings/{id}/complete/ # Randevuyu tamamla
POST   /marketplace/api/bookings/{id}/cancel/  # Randevuyu iptal et
GET    /marketplace/api/bookings/upcoming/     # Yaklaşan randevular
GET    /marketplace/api/bookings/past/         # Geçmiş randevular
```

#### Değerlendirme İşlemleri

```
GET    /marketplace/api/reviews/               # Tüm değerlendirmeler
POST   /marketplace/api/reviews/               # Yeni değerlendirme
POST   /marketplace/api/reviews/{id}/respond/  # Değerlendirmeye yanıt ver
POST   /marketplace/api/reviews/{id}/mark_helpful/ # Faydalı işaretle
```

#### Dashboard

```
GET    /marketplace/api/consultant/dashboard/stats/ # Mali müşavir dashboard
GET    /marketplace/api/client/dashboard/stats/     # Müşteri dashboard
```

### Örnek API Çağrıları

#### 1. Mali Müşavir Listesi (Filtreleme ile)

```python
import requests

url = "http://localhost:8000/marketplace/api/consultants/"
params = {
    'city': 'İstanbul',
    'specialization': 'tax_consulting',
    'min_rate': 500,
    'max_rate': 1500,
    'available_only': 'true',
    'ordering': '-average_rating'
}

response = requests.get(url, params=params)
consultants = response.json()
```

#### 2. Randevu Oluşturma

```python
import requests

url = "http://localhost:8000/marketplace/api/bookings/"
headers = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}

data = {
    "consultant": 1,
    "service": 5,
    "meeting_type": "online",
    "scheduled_date": "2025-11-20",
    "scheduled_time": "14:00:00",
    "duration_minutes": 60,
    "subject": "Vergi Danışmanlığı",
    "description": "KDV beyanı hakkında danışmak istiyorum.",
    "quoted_price": 750.00
}

response = requests.post(url, headers=headers, json=data)
booking = response.json()

# Randevu oluşturuldu, meeting_url otomatik oluşturuldu
print(f"Randevu No: {booking['booking_number']}")
print(f"Görüşme Linki: {booking['meeting_url']}")
```

#### 3. Randevuyu Onaylama (Mali Müşavir)

```python
url = f"http://localhost:8000/marketplace/api/bookings/{booking_id}/confirm/"
headers = {'Authorization': 'Bearer CONSULTANT_TOKEN'}

response = requests.post(url, headers=headers)
```

#### 4. Değerlendirme Yapma

```python
url = "http://localhost:8000/marketplace/api/reviews/"
headers = {
    'Authorization': 'Bearer CLIENT_TOKEN',
    'Content-Type': 'application/json'
}

data = {
    "booking": 123,
    "rating": 5,
    "professionalism_rating": 5,
    "communication_rating": 5,
    "expertise_rating": 5,
    "value_rating": 4,
    "title": "Çok Profesyonel",
    "comment": "Mali müşavir çok yardımcı oldu, kesinlikle tavsiye ederim."
}

response = requests.post(url, headers=headers, json=data)
```

## 🔐 Yetkilendirme ve İzinler

### Roller

1. **Mali Müşavir (Consultant)**

   - Kendi profilini yönetir
   - Hizmetlerini tanımlar
   - Randevuları onayla/tamamla
   - Değerlendirmelere yanıt ver
   - Müsaitlik takvimini ayarla

2. **Müşteri (Client)**

   - Mali müşavirleri ara ve filtrele
   - Randevu oluştur
   - Ödeme yap
   - Değerlendirme yap
   - Sözleşme imzala

3. **Admin**
   - Mali müşavirleri onayla/reddet
   - Belgeleri doğrula
   - Ödemeleri yönet
   - Platformu yönet

## 💰 Ödeme ve Komisyon Sistemi

### Komisyon Hesaplama

```python
# Randevu oluşturulduğunda otomatik hesaplanır
booking.calculate_commission()

# Örnek:
# quoted_price = 1000 TL
# commission_rate = 15%
# commission_amount = 150 TL
# consultant_earning = 850 TL
```

### Ödeme Akışı

1. **Müşteri Ödemesi**: Müşteri randevu için ödeme yapar

   ```python
   payment = ConsultationPayment.objects.create(
       booking=booking,
       client=client,
       consultant=consultant,
       amount=1000,
       commission=150,
       consultant_amount=850,
       payment_method='credit_card'
   )
   ```

2. **Platform Kesintisi**: Sistem otomatik olarak komisyonu keser

3. **Mali Müşavir Ödemesi**: Belirli aralıklarla mali müşavire ödeme yapılır
   ```python
   payout = ConsultantPayout.objects.create(
       consultant=consultant,
       amount=8500,  # 10 randevunun toplamı
       period_start='2025-11-01',
       period_end='2025-11-30',
       bank_name='...',
       iban='...'
   )
   ```

## 📹 Video Konferans Kullanımı

### Randevu için Otomatik Toplantı Oluşturma

```python
from advisors.services.video_conference import create_meeting_for_booking

# Randevu oluşturulduğunda
booking = ConsultationBooking.objects.create(...)
meeting_data = create_meeting_for_booking(booking)

# meeting_data içeriği:
# {
#     'meeting_id': '...',
#     'meeting_url': 'https://meet.jit.si/FinAsis_...',
#     'password': '...',
#     'provider': 'jitsi'
# }
```

### Manuel Toplantı Oluşturma

```python
from advisors.services.video_conference import VideoConferenceFactory
from datetime import datetime, timedelta

provider = VideoConferenceFactory.get_provider('zoom')  # veya 'jitsi', 'google_meet'

meeting = provider.create_meeting(
    topic="Vergi Danışmanlığı",
    start_time=datetime.now() + timedelta(hours=2),
    duration_minutes=60,
    timezone='Europe/Istanbul'
)
```

## 📊 Dashboard ve İstatistikler

### Mali Müşavir Dashboard

```python
# API çağrısı
GET /marketplace/api/consultant/dashboard/stats/

# Yanıt
{
    "total_earnings": "25000.00",
    "pending_earnings": "3500.00",
    "this_month_earnings": "5000.00",
    "total_consultations": 45,
    "completed_consultations": 42,
    "upcoming_bookings": 5,
    "pending_bookings": 2,
    "average_rating": "4.85",
    "total_reviews": 38,
    "active_clients": 12,
    "total_clients": 35
}
```

### Müşteri Dashboard

```python
# API çağrısı
GET /marketplace/api/client/dashboard/stats/

# Yanıt
{
    "total_bookings": 8,
    "completed_bookings": 6,
    "upcoming_bookings": 2,
    "total_spent": "4500.00",
    "this_month_spent": "1500.00",
    "active_contracts": 1,
    "favorite_consultants": [
        {"name": "Ahmet Yılmaz", "booking_count": 3},
        {"name": "Ayşe Demir", "booking_count": 2}
    ]
}
```

## 🔔 Bildirim Sistemi (Gelecek Geliştirme)

### Planlanan Bildirimler

- Randevu onaylandığında
- Randevu 24 saat öncesi hatırlatması
- Randevu 1 saat öncesi hatırlatması
- Ödeme alındığında
- Değerlendirme yapıldığında
- Sözleşme imzalandığında

## 🧪 Test

### Örnek Test Senaryoları

```python
# tests/test_marketplace.py

from django.test import TestCase
from advisors.models_marketplace import ConsultantProfile, ConsultationBooking

class ConsultantProfileTest(TestCase):
    def test_consultant_availability(self):
        consultant = ConsultantProfile.objects.create(...)
        self.assertTrue(consultant.is_available())

    def test_commission_calculation(self):
        consultant = ConsultantProfile.objects.create(
            commission_rate=15.0
        )
        amount = 1000
        commission = consultant.calculate_commission(amount)
        self.assertEqual(commission, 150)

class BookingTest(TestCase):
    def test_booking_creation(self):
        booking = ConsultationBooking.objects.create(...)
        self.assertEqual(booking.status, 'pending')

    def test_booking_confirmation(self):
        booking = ConsultationBooking.objects.create(...)
        booking.confirm()
        self.assertEqual(booking.status, 'confirmed')
```

## 📈 Performans Optimizasyonu

### Database İndeksler

Modellerde tanımlı indeksler:

```python
class Meta:
    indexes = [
        models.Index(fields=['consultant', 'scheduled_date', 'status']),
        models.Index(fields=['client', 'status']),
        models.Index(fields=['booking_number']),
    ]
```

### Query Optimizasyonu

```python
# İlişkili nesneleri önceden yükle
consultants = ConsultantProfile.objects.select_related(
    'advisor__user'
).prefetch_related(
    'services',
    'reviews'
)

# Aggregation kullan
from django.db.models import Avg, Count
stats = ConsultationBooking.objects.filter(
    consultant=consultant
).aggregate(
    total=Count('id'),
    avg_rating=Avg('review__rating')
)
```

## 🔒 Güvenlik

### API Güvenliği

- JWT token bazlı authentication
- Rate limiting (DRF throttling)
- CORS yapılandırması
- SQL injection koruması (Django ORM)
- XSS koruması

### Veri Güvenliği

- Mali müşavir belgelerinin şifrelenmesi
- Hassas bilgilerin loglanmaması
- GDPR uyumluluğu
- Kişisel verilerin anonimleştirilmesi

## 📱 Frontend Entegrasyonu

### React Örneği

```javascript
// ConsultantList.js
import React, { useEffect, useState } from "react";
import axios from "axios";

const ConsultantList = () => {
  const [consultants, setConsultants] = useState([]);

  useEffect(() => {
    axios
      .get("/marketplace/api/consultants/")
      .then((res) => setConsultants(res.data));
  }, []);

  return (
    <div>
      {consultants.map((consultant) => (
        <div key={consultant.id}>
          <h3>{consultant.display_name}</h3>
          <p>
            ⭐ {consultant.average_rating} ({consultant.total_reviews}{" "}
            değerlendirme)
          </p>
          <p>💰 {consultant.hourly_rate} TL/saat</p>
          <p>📍 {consultant.city}</p>
        </div>
      ))}
    </div>
  );
};
```

## 🚧 Gelecek Geliştirmeler

- [ ] Canlı sohbet (WebSocket)
- [ ] Dosya paylaşımı sistemi
- [ ] Otomatik randevu hatırlatıcıları
- [ ] E-posta bildirimleri
- [ ] SMS bildirimleri
- [ ] Mobil uygulama API'leri
- [ ] Mali müşavir portfolyosu
- [ ] Müşteri referans sistemi
- [ ] Hediye çeki/kupon sistemi
- [ ] Multi-currency desteği
- [ ] Fatura otomasyonu

## 📞 Destek

Sorularınız için:

- Email: support@finasis.com
- Dokümantasyon: https://docs.finasis.com
- GitHub Issues: https://github.com/finasis/finasis/issues

## 📄 Lisans

Bu proje FinAsis'e aittir. Tüm hakları saklıdır.

---

**Versiyon:** 1.0.0  
**Son Güncelleme:** Kasım 2025  
**Yazar:** FinAsis Development Team
