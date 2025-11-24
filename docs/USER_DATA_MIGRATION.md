# Kullanıcı Verilerini Yerelden Canlıya Aktarma Kılavuzu

Bu kılavuz, yerel ortamdaki kullanıcı türleri ve kullanıcı bilgilerini canlı ortama (production) nasıl aktaracağınızı açıklar.

## 📋 İçindekiler

1. [Hazırlık](#hazırlık)
2. [Export İşlemi (Yerel Ortam)](#export-işlemi-yerel-ortam)
3. [Import İşlemi (Canlı Ortam)](#import-işlemi-canlı-ortam)
4. [Güvenlik Notları](#güvenlik-notları)
5. [Sorun Giderme](#sorun-giderme)

## 🚀 Hazırlık

### Gereksinimler

- Django projesi çalışır durumda
- Her iki ortamda da (yerel ve canlı) aynı veritabanı yapısı
- Canlı ortamda yazma izinleri

### Export Edilecek Veriler

- **UserType**: Kullanıcı türleri (KOBİ, Eğitimci, Öğrenci, vb.)
- **SubscriptionType**: Abonelik türleri
- **CustomUser**: Kullanıcı bilgileri (şifreler opsiyonel)
- **Company**: Şirket bilgileri (opsiyonel)

## 📤 Export İşlemi (Yerel Ortam)

### 1. Temel Export (Şifreler Olmadan)

```bash
python manage.py export_users_data --output users_export.json
```

Bu komut:
- Tüm UserType'ları export eder
- Tüm SubscriptionType'ları export eder
- Tüm kullanıcıları export eder (şifreler hariç)
- `users_export.json` dosyasına kaydeder

### 2. Şifrelerle Export (Dikkatli Kullanın!)

```bash
python manage.py export_users_data --output users_export.json --include-passwords
```

⚠️ **UYARI**: Şifreler hash'lenmiş şekilde export edilir, ancak güvenlik riski oluşturabilir.

### 3. Şirket Bilgileriyle Export

```bash
python manage.py export_users_data --output users_export.json --include-companies
```

### 4. Tüm Verilerle Export

```bash
python manage.py export_users_data --output users_export.json --include-passwords --include-companies
```

### Export Dosyası Yapısı

Export edilen JSON dosyası şu yapıda olacaktır:

```json
{
  "export_date": "2025-01-15T10:30:00",
  "version": "1.0",
  "user_types": [
    {
      "code": "kobi",
      "name": "KOBİ Sahibi",
      "default_subscription_code": "basic"
    }
  ],
  "subscription_types": [
    {
      "code": "basic",
      "name": "Temel Plan",
      "description": "...",
      "audience": "sme",
      "period_options": "monthly",
      "monthly_price": "99.00",
      "yearly_price": "990.00",
      "user_limit": null,
      "features": []
    }
  ],
  "users": [
    {
      "username": "kullanici1",
      "email": "kullanici1@example.com",
      "first_name": "Ad",
      "last_name": "Soyad",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "role": "staff",
      "user_type_code": "kobi",
      "company_id": 1,
      "groups": ["group1", "group2"]
    }
  ],
  "companies": [...]
}
```

## 📥 Import İşlemi (Canlı Ortam)

### 1. Dosyayı Canlı Ortama Aktarın

Export edilen JSON dosyasını canlı sunucuya yükleyin:

```bash
# Cloud Shell kullanıyorsanız
gcloud cloud-shell scp local users_export.json cloudshell:~/FinAsis/

# veya doğrudan Cloud Shell'de
# Dosyayı Cloud Shell editörüne yükleyin
```

### 2. Dry Run (Test Modu)

Önce ne yapılacağını görmek için dry run yapın:

```bash
cd FinAsis
python manage.py import_users_data users_export.json --dry-run
```

Bu komut:
- Değişiklik yapmaz
- Sadece ne yapılacağını gösterir
- Hataları tespit eder

### 3. Yeni Kullanıcıları Ekle (Mevcutları Güncelleme)

```bash
python manage.py import_users_data users_export.json
```

Bu komut:
- Yeni UserType'ları ekler
- Yeni SubscriptionType'ları ekler
- Yeni kullanıcıları ekler
- Mevcut kullanıcıları **güncellemez** (atlar)

### 4. Mevcut Kullanıcıları da Güncelle

```bash
python manage.py import_users_data users_export.json --update-existing
```

Bu komut:
- Yeni kullanıcıları ekler
- Mevcut kullanıcıları günceller
- Kullanıcı bilgilerini (email, isim, vb.) günceller

### 5. Şifreleri Import Etme

Şifreleri import etmek istemiyorsanız (güvenlik için önerilir):

```bash
python manage.py import_users_data users_export.json --skip-passwords
```

Bu durumda:
- Kullanıcılar oluşturulur
- Geçici şifre atanır: `TempPassword123!`
- Kullanıcılar şifre sıfırlama yapmalı

### 6. Tam Import (Tüm Seçenekler)

```bash
python manage.py import_users_data users_export.json --update-existing
```

## 🔒 Güvenlik Notları

### ⚠️ Önemli Uyarılar

1. **Şifreler**: 
   - Şifreler hash'lenmiş şekilde export edilir
   - Ancak yine de güvenlik riski oluşturabilir
   - Mümkünse `--skip-passwords` kullanın

2. **Kişisel Veriler (PII)**:
   - Export dosyası kişisel veri içerir
   - Dosyayı güvenli bir şekilde aktarın
   - İşlemden sonra dosyayı silin

3. **Canlı Ortam**:
   - Import işleminden önce veritabanı yedeği alın
   - Dry run yaparak test edin
   - İşlemi düşük trafik saatlerinde yapın

4. **İzinler**:
   - Canlı ortamda yazma izinleriniz olduğundan emin olun
   - Superuser yetkisi gerekebilir

## 🛠️ Sorun Giderme

### Hata: "UserType bulunamadı"

**Sebep**: SubscriptionType'lar önce import edilmeli.

**Çözüm**: Import işlemi otomatik olarak sırayı takip eder, ancak manuel kontrol edin:

```bash
python manage.py import_users_data users_export.json --dry-run
```

### Hata: "Company bulunamadı"

**Sebep**: Şirket bilgileri export edilmemiş.

**Çözüm**: Export işlemini `--include-companies` ile tekrar yapın:

```bash
python manage.py export_users_data --output users_export.json --include-companies
```

### Hata: "Permission denied"

**Sebep**: Canlı ortamda yazma izni yok.

**Çözüm**: 
- Cloud Run'da gerekli IAM izinlerini kontrol edin
- Veritabanı bağlantı bilgilerini kontrol edin

### Kullanıcılar Şifre ile Giriş Yapamıyor

**Sebep**: Şifreler import edilmemiş veya geçici şifre atanmış.

**Çözüm**:
1. Şifre sıfırlama linki gönderin
2. Veya şifreleri tekrar import edin (güvenli değil)

## 📊 İşlem Sonrası Kontrol

Import işleminden sonra kontrol edin:

```bash
# Kullanıcı sayısını kontrol et
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.count()

# UserType'ları kontrol et
>>> from accounts.models import UserType
>>> UserType.objects.all()

# Belirli bir kullanıcıyı kontrol et
>>> user = User.objects.get(username='kullanici1')
>>> user.user_type
>>> user.company
```

## 🔄 Geri Alma (Rollback)

Eğer bir hata oluşursa:

1. **Veritabanı yedeğinden geri yükleme**:
   ```bash
   # Cloud SQL yedeğinden geri yükle
   gcloud sql backups restore BACKUP_ID --backup-instance=INSTANCE_NAME
   ```

2. **Manuel temizleme** (dikkatli!):
   ```bash
   python manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> # İstenmeyen kullanıcıları sil
   >>> User.objects.filter(username__startswith='test_').delete()
   ```

## 📝 Örnek Senaryolar

### Senaryo 1: Sadece UserType'ları Aktarma

```bash
# Export (sadece UserType'lar otomatik dahil)
python manage.py export_users_data --output user_types.json

# Import
python manage.py import_users_data user_types.json
```

### Senaryo 2: Test Kullanıcılarını Canlıya Aktarma

```bash
# Export (şifrelerle)
python manage.py export_users_data --output test_users.json --include-passwords

# Import (dry run önce)
python manage.py import_users_data test_users.json --dry-run

# Gerçek import
python manage.py import_users_data test_users.json
```

### Senaryo 3: Tüm Verileri Güncelleme

```bash
# Export
python manage.py export_users_data --output full_export.json --include-companies

# Import (mevcutları güncelle)
python manage.py import_users_data full_export.json --update-existing
```

## 📞 Destek

Sorun yaşarsanız:
1. Dry run çıktısını kontrol edin
2. Log dosyalarını inceleyin
3. Veritabanı yedeğinden geri yükleyin

---

**Son Güncelleme**: 2025-01-15

