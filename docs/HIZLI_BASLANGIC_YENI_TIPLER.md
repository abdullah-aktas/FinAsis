# Yeni Kullanıcı Tipleri - Hızlı Başlangıç

## 🎯 Özet

3 yeni kullanıcı tipi eklendi:

1. **Muhasebe Elemanı** - Fatura ve muhasebe işlemleri
2. **Satış Elemanı** - Satış yönetimi ve takibi
3. **Depo Elemanı** - Stok ve sevkiyat yönetimi

## 🚀 Kurulum

### Adım 1: Migration'ı Çalıştır

```bash
# Migration dosyasını oluştur
python manage.py makemigrations accounts --empty --name add_new_user_types

# accounts/migrations/add_new_user_types_template.py içeriğini
# yeni oluşan migration dosyasına kopyala

# Migration'ı uygula
python manage.py migrate accounts
```

### Adım 2: Test Kullanıcıları Oluştur

```bash
python manage.py shell
```

```python
from accounts.models import CustomUser, UserType
from accounting.models import Company

# Şirket oluştur (eğer yoksa)
company, _ = Company.objects.get_or_create(
    name='Test Şirketi',
    defaults={
        'tax_number': '1234567890',
        'sector': 'Teknoloji'
    }
)

# User type'ları al
muhasebe_type = UserType.objects.get(code='muhasebe_elemani')
satis_type = UserType.objects.get(code='satis_elemani')
depo_type = UserType.objects.get(code='depo_elemani')

# Test kullanıcıları oluştur
muhasebe_user = CustomUser.objects.create_user(
    username='muhasebe1',
    password='test123',
    email='muhasebe@test.com',
    company=company,
    user_type=muhasebe_type
)

satis_user = CustomUser.objects.create_user(
    username='satis1',
    password='test123',
    email='satis@test.com',
    company=company,
    user_type=satis_type
)

depo_user = CustomUser.objects.create_user(
    username='depo1',
    password='test123',
    email='depo@test.com',
    company=company,
    user_type=depo_type
)

print("✓ Test kullanıcıları oluşturuldu!")
```

### Adım 3: Test Et

1. **Muhasebe Elemanı**:

   ```
   Kullanıcı: muhasebe1
   Şifre: test123
   Beklenen URL: /accounts/muhasebe/modul/
   ```

2. **Satış Elemanı**:

   ```
   Kullanıcı: satis1
   Şifre: test123
   Beklenen URL: /accounts/satis/modul/
   ```

3. **Depo Elemanı**:
   ```
   Kullanıcı: depo1
   Şifre: test123
   Beklenen URL: /accounts/depo/modul/
   ```

## 📋 Özellik Karşılaştırması

| Özellik              | Muhasebe | Satış | Depo |
| -------------------- | -------- | ----- | ---- |
| Fatura Görüntüleme   | ✅       | ✅    | ❌   |
| Fatura Oluşturma     | ✅       | ✅    | ❌   |
| Satış İstatistikleri | ✅       | ✅    | ❌   |
| Müşteri Yönetimi     | ⚠️       | ✅    | ❌   |
| Stok Takibi          | ❌       | ❌    | ✅   |
| Sevkiyat Yönetimi    | ❌       | ⚠️    | ✅   |
| Finans Raporları     | ✅       | ⚠️    | ❌   |

✅ Tam Erişim | ⚠️ Kısıtlı Erişim | ❌ Erişim Yok

## 🔧 Özelleştirme

### Yeni Kullanıcı Tipi Eklemek

1. **`utils_redirect.py`'a ekle**:

```python
elif user_type_code in ['yeni_tip', 'alias']:
    return reverse('accounts:modul_yeni')
```

2. **View oluştur** (`views.py`):

```python
@user_type_required('yeni_tip')
@login_required
def modul_yeni(request):
    return render(request, 'accounts/modul_yeni.html')
```

3. **URL ekle** (`urls.py`):

```python
path('yeni/modul/', views.modul_yeni, name='modul_yeni'),
```

4. **Template oluştur**:

```django
{% extends 'accounts/base_accounts.html' %}
{# İçerik #}
```

## 📊 Dashboard Bileşenleri

### Ortak Bileşenler

- İstatistik kartları (4 adet)
- Hızlı işlemler bölümü
- Son işlemler listesi/tablosu

### Özelleştirilmiş Bileşenler

**Muhasebe**:

- Günlük/haftalık/aylık fatura istatistikleri
- Bekleyen işlemler
- Son 10 fatura

**Satış**:

- Aylık satış tutarı ve adedi
- Performans özeti widget'ı
- İpuçları paneli

**Depo**:

- Düşük stok uyarıları
- Sevkiyat takibi
- Stok hareketi geçmişi

## 🐛 Sorun Giderme

### Hata: "UserType matching query does not exist"

```bash
# Migration'ı kontrol et
python manage.py showmigrations accounts

# Eksikse çalıştır
python manage.py migrate accounts
```

### Hata: "Template does not exist"

```bash
# Template yollarını kontrol et
python manage.py shell
>>> from django.template.loader import get_template
>>> template = get_template('accounts/modul_muhasebe.html')
>>> print(template.origin)
```

### Hata: "Permission denied"

```bash
# User type'ı kontrol et
python manage.py shell
>>> from accounts.models import CustomUser
>>> user = CustomUser.objects.get(username='muhasebe1')
>>> print(user.user_type.code)
```

## 📚 Ek Kaynaklar

- [Detaylı Dokümantasyon](./YENI_KULLANICI_TIPLERI.md)
- [Login Redirect Sistemi](./LOGIN_REDIRECT_SYSTEM.md)
- [Ana README](../YONLENDIRME_SISTEMI_README.md)

## ✅ Kontrol Listesi

- [ ] Migration çalıştırıldı
- [ ] UserType kayıtları oluşturuldu
- [ ] Test kullanıcıları oluşturuldu
- [ ] Her panel test edildi
- [ ] URL'ler doğru çalışıyor
- [ ] Yetkiler kontrol edildi
- [ ] Template'ler render ediliyor

---

**Hazırlayan**: GitHub Copilot  
**Tarih**: 13 Kasım 2025
