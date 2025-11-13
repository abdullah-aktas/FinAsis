# Yeni Kullanıcı Tipleri - Güncellemeler

## 📋 Eklenen Kullanıcı Tipleri

### 1. Muhasebe Elemanı (`muhasebe_elemani`)

**Kod Aliases**: `muhasebe_elemani`, `accounting_staff`, `accountant_staff`

**Dashboard URL**: `/accounts/muhasebe/modul/`

**Yetkiler ve Özellikler**:

- ✅ Fatura oluşturma ve düzenleme
- ✅ Fatura listesini görüntüleme
- ✅ Finans raporlarına erişim
- ✅ Özet raporları görüntüleme
- ✅ Günlük, haftalık ve aylık istatistikler

**Dashboard Bileşenleri**:

- **İstatistik Kartları**:
  - Bugünkü faturalar
  - Bu hafta kesilen faturalar
  - Bu ay kesilen faturalar
  - Bekleyen işlemler
- **Hızlı İşlemler**:
  - Fatura listesi
  - Yeni fatura oluştur
  - Finans raporları
  - Özet rapor
- **Son Faturalar Tablosu**:
  - Fatura numarası
  - Müşteri bilgisi
  - Tarih
  - Tutar
  - Ödeme durumu

---

### 2. Satış Elemanı (`satis_elemani`)

**Kod Aliases**: `satis_elemani`, `sales_staff`, `salesperson`

**Dashboard URL**: `/accounts/satis/modul/`

**Yetkiler ve Özellikler**:

- ✅ Satış faturası oluşturma
- ✅ Satış listesini görüntüleme
- ✅ Müşteri yönetimi
- ✅ Satış performans takibi
- ✅ Tahsilat takibi

**Dashboard Bileşenleri**:

- **Satış İstatistikleri**:
  - Bu ay toplam satış tutarı
  - Satış adedi
  - Bekleyen siparişler
  - Aktif müşteri sayısı
- **Hızlı İşlemler**:
  - Yeni satış
  - Satış listesi
  - Müşteriler
- **Son Satışlar Tablosu**:
  - Müşteri adı
  - Fatura numarası
  - Tarih
  - Tutar
  - Tahsilat durumu
- **Performans Özeti**:
  - Aylık hedef yüzdesi
  - Bu ayın satış sayısı
  - Toplam ciro
- **İpuçları Widget'ı**

---

### 3. Depo Elemanı (`depo_elemani`)

**Kod Aliases**: `depo_elemani`, `warehouse_staff`, `warehouse`

**Dashboard URL**: `/accounts/depo/modul/`

**Yetkiler ve Özellikler**:

- ✅ Stok takibi
- ✅ Stok giriş/çıkış işlemleri
- ✅ Sevkiyat yönetimi
- ✅ Düşük stok uyarıları
- ✅ Stok raporları

**Dashboard Bileşenleri**:

- **Depo İstatistikleri**:
  - Düşük stok uyarıları
  - Bekleyen sevkiyatlar
  - Bugünkü hareketler
  - Toplam ürün sayısı
- **Hızlı İşlemler**:
  - Stok girişi
  - Stok çıkışı
  - Ürün arama
  - Stok raporu
- **Düşük Stok Uyarıları Listesi**
- **Son Hareketler Listesi**:
  - Giriş/Çıkış durumu
  - Ürün adı
  - Miktar
  - Zaman bilgisi

**Not**: Depo modülü, stok yönetimi modülü aktif olduğunda tam işlevseldir. Şu an placeholder görünümler gösterilmektedir.

---

## 🔄 Güncellemeler

### Dosya Değişiklikleri

#### 1. `accounts/utils_redirect.py`

```python
# Yeni eklenen yönlendirmeler:
elif user_type_code in ['muhasebe_elemani', 'accounting_staff', 'accountant_staff']:
    return reverse('accounts:modul_muhasebe')

elif user_type_code in ['satis_elemani', 'sales_staff', 'salesperson']:
    return reverse('accounts:modul_satis')

elif user_type_code in ['depo_elemani', 'warehouse_staff', 'warehouse']:
    return reverse('accounts:modul_depo')
```

#### 2. `accounts/views.py`

Yeni view fonksiyonları eklendi:

- `modul_muhasebe()` - Muhasebe elemanı dashboard
- `modul_satis()` - Satış elemanı dashboard
- `modul_depo()` - Depo elemanı dashboard

Her view:

- ✅ `@user_type_required` decorator ile korunmuş
- ✅ `@login_required` ile kimlik doğrulama kontrolü
- ✅ Şirket bazlı veri filtreleme
- ✅ İstatistik hesaplamaları
- ✅ Context verisi hazırlama

#### 3. `accounts/urls.py`

Yeni URL pattern'leri:

```python
path('muhasebe/modul/', views.modul_muhasebe, name='modul_muhasebe'),
path('satis/modul/', views.modul_satis, name='modul_satis'),
path('depo/modul/', views.modul_depo, name='modul_depo'),
```

#### 4. Template Dosyaları

Oluşturulan yeni template'ler:

- `accounts/templates/accounts/modul_muhasebe.html`
- `accounts/templates/accounts/modul_satis.html`
- `accounts/templates/accounts/modul_depo.html`

---

## 🎨 UI/UX Özellikleri

### Ortak Tasarım Dili

Tüm paneller aynı tasarım dili ile oluşturulmuştur:

- **Responsive Grid Layout**: Bootstrap 5.3
- **İstatistik Kartları**:
  - Border-left vurgusu ile renklendirilmiş
  - İkon + Değer + Label yapısı
  - Hover animasyonları
- **Hızlı İşlemler Bölümü**:
  - Büyük butonlar
  - İkonlu gösterim
  - Grid düzeni
- **Veri Tabloları**:
  - Striped hover efekti
  - Responsive tasarım
  - Action butonları
- **Modals**: Bootstrap modal component'leri

### Renk Kodları

- **Muhasebe**: Mavi (`primary`) ve Yeşil (`success`)
- **Satış**: Yeşil (`success`) ve Turuncu (`warning`)
- **Depo**: Mavi (`info`) ve Kırmızı (`danger`)

---

## 📊 Veritabanı Gereksinimleri

### UserType Kayıtları

Yeni kullanıcı tiplerini veritabanına eklemek için:

```python
from accounts.models import UserType

# Muhasebe Elemanı
UserType.objects.get_or_create(
    code='muhasebe_elemani',
    defaults={
        'name': 'Muhasebe Elemanı',
        'default_subscription': None  # veya uygun bir SubscriptionType
    }
)

# Satış Elemanı
UserType.objects.get_or_create(
    code='satis_elemani',
    defaults={
        'name': 'Satış Elemanı',
        'default_subscription': None
    }
)

# Depo Elemanı
UserType.objects.get_or_create(
    code='depo_elemani',
    defaults={
        'name': 'Depo Elemanı',
        'default_subscription': None
    }
)
```

### Migration Scripti

```python
# migrations/XXXX_add_new_user_types.py
from django.db import migrations

def create_user_types(apps, schema_editor):
    UserType = apps.get_model('accounts', 'UserType')

    user_types = [
        {'code': 'muhasebe_elemani', 'name': 'Muhasebe Elemanı'},
        {'code': 'satis_elemani', 'name': 'Satış Elemanı'},
        {'code': 'depo_elemani', 'name': 'Depo Elemanı'},
    ]

    for ut_data in user_types:
        UserType.objects.get_or_create(
            code=ut_data['code'],
            defaults={'name': ut_data['name']}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', 'XXXX_previous_migration'),
    ]

    operations = [
        migrations.RunPython(create_user_types),
    ]
```

---

## 🧪 Test Senaryoları

### 1. Muhasebe Elemanı Testi

```python
def test_accounting_staff_redirect():
    user = create_user(user_type_code='muhasebe_elemani')
    client.force_login(user)
    response = client.get('/accounts/login/')
    assert response.url == '/accounts/muhasebe/modul/'
```

### 2. Satış Elemanı Testi

```python
def test_sales_staff_redirect():
    user = create_user(user_type_code='satis_elemani')
    client.force_login(user)
    response = client.get('/accounts/login/')
    assert response.url == '/accounts/satis/modul/'
```

### 3. Depo Elemanı Testi

```python
def test_warehouse_staff_redirect():
    user = create_user(user_type_code='depo_elemani')
    client.force_login(user)
    response = client.get('/accounts/login/')
    assert response.url == '/accounts/depo/modul/'
```

---

## 🔐 Güvenlik ve Yetkiler

### Decorator Kullanımı

Tüm modül view'ları `@user_type_required` decorator ile korunmuştur:

```python
@user_type_required('muhasebe_elemani')
@login_required
def modul_muhasebe(request):
    # ...
```

Bu sayede:

- ✅ Sadece ilgili user_type'a sahip kullanıcılar erişebilir
- ✅ Kimlik doğrulaması zorunlu
- ✅ Yetkisiz erişim engellenmiş

---

## 📈 Performans Notları

### Veritabanı Sorguları

Tüm dashboard'larda optimize edilmiş sorgular kullanılmıştır:

- `select_related()` ile ilişkili modeller
- `aggregate()` ile toplu hesaplamalar
- `[:10]` ile limit uygulaması
- Gereksiz N+1 sorgu problemi yok

### Cache Önerileri

Yüksek trafikli sistemlerde:

```python
from django.core.cache import cache

# İstatistikleri cache'le
stats_key = f'dashboard_stats_{user.id}_{today}'
stats = cache.get(stats_key)
if not stats:
    stats = calculate_stats()
    cache.set(stats_key, stats, timeout=300)  # 5 dakika
```

---

## 🚀 Sonraki Adımlar

### Öncelikli Geliştirmeler

1. **Stok Modülü Entegrasyonu**: Depo elemanı için tam işlevsellik
2. **Müşteri Yönetimi**: Satış elemanı için CRM özellikleri
3. **Raporlama**: Detaylı ve dışa aktarılabilir raporlar
4. **Bildirimler**: Gerçek zamanlı bildirim sistemi
5. **Performans Dashboard'ları**: Grafik ve chart'lar

### İyileştirme Fikirleri

- Dashboard widget'larını özelleştirilebilir yapma
- Drag & drop ile widget yerleşimi
- Kişiselleştirilmiş KPI'lar
- Export to PDF/Excel özelliği
- Mobil uygulama desteği

---

## 📞 Yardım ve Destek

### Sorun Giderme

**Problem**: Kullanıcı giriş sonrası yönlendirilmiyor

```bash
# UserType kontrolü
python manage.py shell
>>> from accounts.models import CustomUser
>>> user = CustomUser.objects.get(username='test')
>>> print(user.user_type.code if user.user_type else None)
```

**Problem**: Template bulunamıyor

```bash
# Template yolunu kontrol et
python manage.py findstatic accounts/modul_muhasebe.html
```

**Problem**: Permission denied hatası

```bash
# Decorator'ı kontrol et
# @user_type_required('muhasebe_elemani') doğru mu?
```

---

**Güncelleme Tarihi**: 13 Kasım 2025  
**Versiyon**: 1.1.0  
**Güncelleyen**: GitHub Copilot AI Assistant
