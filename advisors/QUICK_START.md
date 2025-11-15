# Mali Müşavir Marketplace - Hızlı Başlangıç

## 🚀 5 Dakikada Kurulum

### Adım 1: Database Migration

```bash
cd d:\FinAsis
python manage.py makemigrations advisors
python manage.py migrate
```

### Adım 2: Admin Kullanıcısı Oluştur

```bash
python manage.py createsuperuser
# Username, email ve şifre girin
```

### Adım 3: URL Yapılandırması

`advisors/urls.py` dosyasını açın ve ekleyin:

```python
from django.urls import path, include

urlpatterns = [
    # Mevcut URL'ler...

    # Marketplace API endpoints
    path('marketplace/api/', include('advisors.urls.marketplace_urls')),
]
```

### Adım 4: Settings Güncellemesi

`config/settings.py` veya ana `settings.py` dosyasına ekleyin:

```python
# REST Framework (eğer yoksa)
INSTALLED_APPS = [
    # ... mevcut apps
    'rest_framework',
    'django_filters',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Video Conference Ayarları
VIDEO_CONFERENCE_DEFAULT_PROVIDER = 'jitsi'  # Ücretsiz, kurulum gerektirmez
JITSI_DOMAIN = 'meet.jit.si'

# Opsiyonel: Zoom
# ZOOM_API_KEY = 'your-api-key'
# ZOOM_API_SECRET = 'your-api-secret'

# Opsiyonel: Google Meet
# GOOGLE_MEET_SERVICE_ACCOUNT = 'path/to/service-account.json'

# Marketplace
MARKETPLACE_DEFAULT_COMMISSION_RATE = 15  # %15 platform komisyonu
```

### Adım 5: Sunucuyu Başlat

```bash
python manage.py runserver
```

## ✅ Test Et

### 1. Admin Paneli

- Tarayıcıda açın: http://127.0.0.1:8000/admin/
- Giriş yapın (superuser)
- Sol menüden "Advisors" > "Consultant profiles" seçin
- ✅ Marketplace admin paneli çalışıyor!

### 2. API Endpointleri

```bash
# Mali Müşavir Listesi (GET)
curl http://127.0.0.1:8000/advisors/marketplace/api/consultants/

# Hizmetler (GET)
curl http://127.0.0.1:8000/advisors/marketplace/api/services/

# Randevular (GET - authentication gerekli)
curl http://127.0.0.1:8000/advisors/marketplace/api/bookings/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 3. Test Senaryosu

#### A. Mali Müşavir Kaydı (POST)

```bash
curl -X POST http://127.0.0.1:8000/advisors/marketplace/api/consultants/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "display_name": "Ahmet Yılmaz",
    "bio": "15 yıllık deneyimli mali müşavir",
    "hourly_rate": 500,
    "specializations": ["Vergi Danışmanlığı", "Finansal Planlama"],
    "languages": ["tr", "en"],
    "diploma_document": "BASE64_ENCODED_FILE",
    "graduation_document": "BASE64_ENCODED_FILE"
  }'
```

#### B. Admin Onayı

1. Admin paneline git: http://127.0.0.1:8000/admin/advisors/consultantprofile/
2. Kayıt bekleyen profili seç
3. "Seçili mali müşavirleri onayla ve blockchain anlaşması yap" aksiyonunu çalıştır
4. ✅ Blockchain anlaşması oluşturuldu!

#### C. Randevu Oluşturma

```bash
curl -X POST http://127.0.0.1:8000/advisors/marketplace/api/bookings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "consultant": 1,
    "service": 1,
    "scheduled_date": "2024-12-20",
    "scheduled_time": "14:00:00",
    "duration": 60,
    "meeting_type": "video",
    "notes": "Vergi danışmanlığı almak istiyorum"
  }'
```

## 🎯 İlk Kullanım Kontrol Listesi

- [ ] Database migration tamamlandı
- [ ] Admin kullanıcısı oluşturuldu
- [ ] URL yapılandırması eklendi
- [ ] Settings güncellendi
- [ ] Sunucu başlatıldı
- [ ] Admin paneli açıldı
- [ ] API endpoints erişilebilir
- [ ] Test mali müşavir kaydı oluşturuldu
- [ ] Onay ve blockchain anlaşması test edildi
- [ ] Test randevusu oluşturuldu

## 🔍 Sorun Giderme

### Hata: "No migrations to apply"

```bash
# Migration dosyalarını sil ve yeniden oluştur
rm -rf advisors/migrations/0*marketplace*.py
python manage.py makemigrations advisors
python manage.py migrate
```

### Hata: "Module not found: rest_framework"

```bash
pip install djangorestframework django-filter djangorestframework-simplejwt
```

### Hata: "Relation does not exist"

```bash
# Database'i sıfırla (DİKKAT: Tüm veriler silinir!)
python manage.py migrate advisors zero
python manage.py migrate advisors
```

### Hata: "advisor_profile attribute not found"

Bu bir type checking uyarısıdır, runtime'da çalışır. Görmezden gelebilirsiniz.

### Hata: Blockchain service bulunamadı

```python
# advisors/services/consultant_blockchain.py dosyasını kontrol edin
# virtual_company ve blockchain app'lerin yüklü olduğundan emin olun
INSTALLED_APPS = [
    # ...
    'virtual_company',
    'blockchain',
]
```

## 📚 Daha Fazla Bilgi

- **Detaylı Dokümantasyon**: `MARKETPLACE_README.md`
- **Sistem Durumu**: `MARKETPLACE_STATUS.md`
- **Blockchain Detayları**: `BLOCKCHAIN_AGREEMENT_UPDATE.md`
- **Test Senaryoları**: `MARKETPLACE_SETUP.py`

## 🎉 Başarılı Kurulum!

Artık sistemin temel özellikleri çalışıyor:

✅ Mali müşavir kayıt sistemi  
✅ Belge yükleme ve onaylama  
✅ Blockchain anlaşma sistemi  
✅ Video konferans entegrasyonu  
✅ Randevu yönetimi  
✅ Komisyon hesaplama (%15 platform, %85 mali müşavir)  
✅ Ödeme takibi  
✅ Değerlendirme sistemi  
✅ Admin panel

---

**İyi Çalışmalar! 🚀**

Sorular için: `MARKETPLACE_README.md` dosyasını inceleyin.
