# FinAsis Kullanıcı Senaryoları - Kullanım Kılavuzu

## 📚 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Hızlı Başlangıç](#hızlı-başlangıç)
3. [Demo Veri Oluşturma](#demo-veri-oluşturma)
4. [Senaryo Testleri](#senaryo-testleri)
5. [Kullanıcı Tiplerinin Detayları](#kullanıcı-tiplerinin-detayları)
6. [Sorun Giderme](#sorun-giderme)

---

## 🎯 Genel Bakış

FinAsis platformu 4 farklı kullanıcı tipi için tasarlanmıştır:

| Kullanıcı Tipi | Hedef Kitle | Ana Özellikler |
|----------------|-------------|----------------|
| 📊 **KOBİ** | İşletme sahipleri, muhasebeciler | Fatura, raporlar, AI analiz |
| 🎓 **Eğitimci** | Öğretmenler, içerik üreticiler | Kurs oluşturma, öğrenci takibi |
| 📚 **Öğrenci** | Lise, üniversite öğrencileri | Modüller, testler, sertifikalar |
| 🎮 **Oyuncu** | Oyun severler | 3D oyun, turnuvalar, NFT'ler |

---

## ⚡ Hızlı Başlangıç

### 1. Dokümanları İncele

```bash
# Detaylı senaryolar
docs/kullanici_senaryolari.md

# Hızlı referans
docs/kullanici_senaryolari_ozet.md
```

### 2. Demo Veri Oluştur

```bash
# Tüm kullanıcı tipleri için demo veri
python scripts/create_demo_scenarios.py --type all

# Sadece KOBİ senaryosu
python scripts/create_demo_scenarios.py --type kobi

# Sadece Eğitimci senaryosu
python scripts/create_demo_scenarios.py --type egitimci

# Sadece Öğrenci senaryosu
python scripts/create_demo_scenarios.py --type ogrenci

# Sadece Oyuncu senaryosu
python scripts/create_demo_scenarios.py --type oyuncu
```

### 3. Sunucuyu Başlat

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python manage.py runserver

# Linux/Mac
source .venv/bin/activate
python manage.py runserver
```

### 4. Demo Kullanıcıları ile Giriş Yap

| Kullanıcı | Kullanıcı Adı | Şifre | URL |
|-----------|---------------|-------|-----|
| KOBİ | `kobi_demo` | `Demo123!` | http://127.0.0.1:8000/accounts/login/ |
| Eğitimci | `egitimci_demo` | `Demo123!` | http://127.0.0.1:8000/accounts/login/ |
| Öğrenci | `ogrenci_demo` | `Demo123!` | http://127.0.0.1:8000/accounts/login/ |
| Oyuncu | `oyuncu_demo` | `Demo123!` | http://127.0.0.1:8000/accounts/login/ |

---

## 🗄️ Demo Veri Oluşturma

### KOBİ Kullanıcısı İçin Oluşturulan Veriler

```
✅ Kullanıcı: kobi_demo
✅ Şirket: YazılımTech A.Ş.
✅ 5 Müşteri
✅ 5 Ürün/Hizmet
✅ ~60 Fatura (son 3 ay)
✅ ~24 Gider kaydı (son 3 ay)
✅ 1 Banka hesabı + ~180 işlem
✅ 3 Başarım rozeti
✅ Premium abonelik (30 gün)
```

### Eğitimci Kullanıcısı İçin Oluşturulan Veriler

```
✅ Kullanıcı: egitimci_demo
✅ Premium abonelik (365 gün)
✅ Eğitimci rolü
```

### Öğrenci Kullanıcısı İçin Oluşturulan Veriler

```
✅ Kullanıcı: ogrenci_demo
✅ Eğitim Öğrenci aboneliği (30 gün)
✅ Viewer rolü
```

### Oyuncu Kullanıcısı İçin Oluşturulan Veriler

```
✅ Kullanıcı: oyuncu_demo
✅ Freemium abonelik
✅ Viewer rolü
```

---

## 🧪 Senaryo Testleri

### Test 1: KOBİ - Fatura Yönetimi Senaryosu

**Hedef:** Yeni fatura oluşturup raporlarda görmek

**Adımlar:**
1. `kobi_demo` kullanıcısı ile giriş yap
2. Dashboard'dan "Faturalar" menüsüne git
3. "Yeni Fatura" butonuna tıkla
4. Fatura bilgilerini gir:
   - Müşteri seç (ABC Ltd.)
   - Ürün ekle (Yazılım Geliştirme)
   - Miktar: 1
5. Faturayı kaydet
6. "Finansal Raporlar" > "Gelir Tablosu" sayfasına git
7. Yeni faturanın gelire yansıdığını kontrol et

**Beklenen Sonuç:**
- ✅ Fatura başarıyla oluşturuldu
- ✅ Fatura listesinde görünüyor
- ✅ Gelir tablosunda yansıdı
- ✅ Dashboard'da güncel rakamlar

---

### Test 2: KOBİ - Finansal Raporlama Senaryosu

**Hedef:** Aylık finansal raporları incelemek

**Adımlar:**
1. `kobi_demo` ile giriş
2. "Finansal Raporlar" menüsüne git
3. **Bilanço** sayfasını aç:
   - Aktif/Pasif dengesi kontrol et
   - Grafiği incele
   - "Excel'e Aktar" butonunu test et
4. **Gelir Tablosu** sayfasını aç:
   - Son 3 aylık gelir-gider karşılaştırması
   - Kâr marjını kontrol et
   - PDF'e aktar
5. **Nakit Akış** sayfasını aç:
   - Giriş-çıkış akışını incele
   - Grafikleri kontrol et

**Beklenen Sonuç:**
- ✅ Tüm raporlar doğru verilerle dolu
- ✅ Grafikler çalışıyor
- ✅ Export işlemleri başarılı
- ✅ Ay/yıl filtreleri çalışıyor

---

### Test 3: KOBİ - AI Önerileri Senaryosu

**Hedef:** AI asistanından finansal öneriler almak

**Adımlar:**
1. `kobi_demo` ile giriş
2. Dashboard'da "AI Önerileri" kartını bul
3. "Detaylı Analiz" butonuna tıkla
4. Önerileri oku:
   - Risk analizi
   - Kârlılık değerlendirmesi
   - Gelecek ay tahmini
5. "Otomasyon" sekmesine git (`/accounting/auto-book/`)
6. OCR ve otomatik kayıt önizlemesini incele

**Beklenen Sonuç:**
- ✅ AI önerileri görüntüleniyor
- ✅ Risk skoru hesaplandı
- ✅ Tahminler mantıklı
- ✅ Otomasyon sayfası açıldı

---

### Test 4: Eğitimci - İçerik Oluşturma Senaryosu

**Hedef:** Yeni kurs oluşturmak

**Adımlar:**
1. `egitimci_demo` ile giriş
2. "FinEd" > "Kurslarım" menüsüne git
3. "Yeni Kurs Oluştur" butonuna tıkla
4. Kurs bilgilerini gir:
   - Başlık: "Temel Muhasebe 101"
   - Açıklama: Kurs tanımı
   - Kategori: Muhasebe
5. İlk modülü ekle:
   - Başlık: "Muhasebe Nedir?"
   - İçerik tipi: Video + Metin
6. Test/Quiz ekle (5 soru)
7. Kursu "Taslak" olarak kaydet

**Beklenen Sonuç:**
- ✅ Kurs oluşturuldu
- ✅ Modül eklendi
- ✅ Quiz hazırlandı
- ✅ Kurs listesinde görünüyor

---

### Test 5: Öğrenci - Öğrenme Yolculuğu Senaryosu

**Hedef:** İlk modülü tamamlayıp rozet kazanmak

**Adımlar:**
1. `ogrenci_demo` ile giriş
2. Dashboard'da "Kurslarım" bölümünü incele
3. Bir kursa kaydol (eğer hazırsa)
4. İlk modülü aç
5. Video izle ve notlar al
6. Modül sonunda test yap (5 soru)
7. %70+ başarı ile geç
8. İlk rozetini kazanmayı kontrol et

**Beklenen Sonuç:**
- ✅ Modül tamamlandı
- ✅ Test başarıyla geçildi
- ✅ "Yolculuk Başladı" rozeti kazanıldı
- ✅ Progress bar güncellendi

---

### Test 6: Oyuncu - Oyun Başlangıç Senaryosu

**Hedef:** Sanal şirket kurup ilk görevleri yapmak

**Adımlar:**
1. `oyuncu_demo` ile giriş
2. "FinGame" menüsüne git
3. Tutorial'ı başlat (eğer ilk girişse)
4. Şirket adı ve avatar seç
5. İlk görev: "5 fatura kes"
6. Basit faturalar oluştur
7. Ödül coinlerini topla
8. Liderlik tablosuna bak

**Beklenen Sonuç:**
- ✅ Oyuna giriş yapıldı
- ✅ Şirket kuruldu
- ✅ İlk görev tamamlandı
- ✅ Coinler kazanıldı
- ✅ Liderlik tablosunda sıralama

---

## 👥 Kullanıcı Tiplerinin Detayları


### 📊 KOBİ Kullanıcısı Monografi Senaryosu

#### Karakter: Ahmet Yılmaz (YazılımTech A.Ş. Kurucusu)

**Giriş:**
Ahmet Yılmaz, 38 yaşında, İstanbul'da küçük bir yazılım şirketinin sahibi. Şirketi 3 yıldır faaliyette ve 7 kişilik bir ekibi var. Son dönemde iş hacmi büyüdükçe, finansal süreçlerde karmaşa ve zaman kaybı yaşamaya başladı. Excel dosyaları, e-posta ile gelen faturalar ve manuel raporlar arasında kaybolduğunu hissediyor. Bir arkadaşının önerisiyle FinAsis'i denemeye karar veriyor.

**1. Kayıt ve İlk İzlenim**
Ahmet, www.finasis.com adresine giriyor. Kayıt ekranında "KOBİ" kullanıcı tipini seçiyor. Şirket bilgilerini dolduruyor:
- Şirket Adı: YazılımTech A.Ş.
- Vergi No: 1234567890
- Sektör: Bilişim
- Adres: Maslak, İstanbul
- Telefon: 0212 123 45 67

Kayıt işlemi sonrası "Premium" planı seçiyor. PayTR ile kredi kartından ödeme yapıyor. Ödeme sonrası gelen e-posta ile hoşgeldin mesajı ve ilk adımlar rehberi dikkatini çekiyor.

**2. Şirket Profili ve Ekip Tanımlama**
Dashboard'a ilk girdiğinde, "Şirket Profili" tamamla uyarısı ile karşılaşıyor. Eksik alanları dolduruyor, şirket logosunu yüklüyor. Ardından ekip arkadaşlarını davet ediyor:
- "zeynep@company.com" (Muhasebe)
- "mehmet@company.com" (Satış)

Her davet edilen kullanıcıya otomatik e-posta gidiyor. Zeynep, daveti kabul edip kendi şifresini belirliyor.

**3. İlk Fatura ve Müşteri Kaydı**
Ahmet, ilk iş olarak yeni bir müşteri ekliyor:
- Müşteri: ABC Teknoloji Ltd.
- Vergi No: 9876543210
- E-posta: info@abcteknoloji.com

"Faturalar" menüsünden yeni fatura oluşturuyor:
- Ürün: "Kurumsal Web Sitesi Geliştirme"
- Tutar: 25.000 TL
- KDV: %20
- Açıklama: "Proje teslimi sonrası ödeme"

Faturayı PDF olarak indirip müşterisine e-posta ile gönderiyor. Aynı anda, sistemde e-Fatura entegrasyonu aktif olduğu için, fatura GİB'e otomatik iletiliyor.

**4. Gider ve Banka İşlemleri**
Zeynep, ofis kirası ve maaş ödemelerini sisteme giriyor:
- Gider: Ofis Kirası, 12.000 TL
- Gider: Personel Maaşları, 56.000 TL

"Banka Hesapları" modülünden şirket hesabını tanımlıyor. Banka entegrasyonu ile son 1 ayın hareketleri otomatik olarak sisteme çekiliyor. Ahmet, dashboard'da anlık nakit durumunu ve son işlemleri görebiliyor.

**5. Finansal Raporlama ve AI Analizleri**
Ay sonu geldiğinde, Ahmet "Finansal Raporlar" sekmesine tıklıyor. Bilanço, gelir tablosu ve nakit akışı raporlarını grafiklerle inceliyor. AI asistanı, şu önerileri sunuyor:
- "Giderleriniz geçen aya göre %12 arttı. Özellikle maaş ve kira kalemlerinde artış var."
- "Nakit akışınız pozitif. Yatırım için uygun bir dönem olabilir."

Ahmet, bu analizleri PDF olarak indirip yatırımcı ortağıyla paylaşıyor.

**6. Stok ve Sipariş Yönetimi**
Şirket, yeni bir yazılım lisansı satışı yapıyor. Zeynep, "Stok Yönetimi" modülünden mevcut lisans stokunu güncelliyor. Kritik seviyeye düşen ürünler için sistem otomatik uyarı veriyor. Yeni sipariş oluşturuluyor ve tedarikçiye e-posta ile iletiliyor.

**7. Blockchain ile Şeffaflık**
Bir müşteri, geçmiş bir faturanın doğruluğunu sorguluyor. Ahmet, ilgili faturanın blockchain hash'ini sistemden alıp müşterisiyle paylaşıyor. Müşteri, fatura kaydının değiştirilemez ve güvenli olduğunu kendi ekranında doğruluyor.

**8. Konsolidasyon ve Çoklu Şirket Yönetimi**
Ahmet, yeni bir yan şirket kuruyor. "Şirketlerim" menüsünden ikinci şirketini ekliyor. Her iki şirketin finansal raporlarını tek ekranda karşılaştırabiliyor. Grup bazında konsolide bilanço alıyor.

**9. Sonuç ve Gelişim**
3 ay sonunda Ahmet'in şirketinde finansal süreçler büyük ölçüde otomatize oluyor. Zeynep, manuel iş yükünün %60 azaldığını belirtiyor. Ahmet, FinAsis sayesinde zaman kazandığını, hata oranının düştüğünü ve yatırımcıya daha güvenilir raporlar sunabildiğini vurguluyor.

**Gerçek Hayattan Alıntılar**
> "Daha önce ayda 2 günümü rapor hazırlamaya harcıyordum, şimdi 10 dakikada tüm raporlar elimde."
>  Ahmet Yılmaz

> "Banka entegrasyonu ve otomatik fatura ile iş yüküm çok azaldı."
>  Zeynep (Muhasebe)

**Kısa Notlar**
- Tüm süreçler mobil uygulama üzerinden de yönetilebiliyor.
- AI asistanı, kritik finansal değişikliklerde anlık bildirim gönderiyor.
- Blockchain entegrasyonu, dış denetimlerde büyük kolaylık sağlıyor.


**Erişebileceği Sayfalar:**
```
✅ /dashboard/
✅ /accounting/invoices/
✅ /accounting/expenses/
✅ /accounting/customers/
✅ /accounting/products/
✅ /accounting/finansal/bilanco/
✅ /accounting/finansal/gelir-tablosu/
✅ /accounting/finansal/nakit-akisi/
✅ /accounting/auto-book/
✅ /ai-assistant/
✅ /blockchain/
```

**Temel Özellikleri:**
- ✅ Fatura & Gider yönetimi
- ✅ Müşteri & Ürün takibi
- ✅ Finansal raporlar
- ✅ AI destekli analizler
- ✅ Blockchain şeffaflık
- ✅ E-Fatura entegrasyonu
- ✅ Çok şirketli yönetim

---

### 🛡️ Admin Kullanıcısı

FinAsis'te iki düzey admin profili bulunur:
- Sistem Admin (Platform yöneticisi: tüm tenant/şirketler ve global ayarlar)
- Şirket Admin (Tek bir şirkette tam yetki: kullanıcı/rol/abonelik yönetimi)

Bu bölüm, her iki admin profili için günlük operasyonlardan güvenliğe kadar pratik bir kullanım rehberidir.

#### Erişebileceği Sayfalar
```
✅ /admin/            (Django Admin – Sistem Admin)
✅ /dashboard/admin   (Uygulama yönetim paneli)
✅ /accounts/users/   (Kullanıcı yönetimi)
✅ /tenancy/          (Tenant/Şirket yönetimi – çok şirketli yapı)
✅ /billing/          (Planlar, abonelikler, ödemeler)
✅ /permissions/      (Roller, yetkiler)
✅ /logs/audit/       (Denetim kayıtları, olay günlükleri)
✅ /settings/         (Genel ayarlar, entegrasyon anahtarları)
```

#### Admin Onboarding (İlk Kurulum)
1) Yönetici hesabı ile giriş yapın (Sistem Admin için `/admin/`).
2) Şirket (tenant) kaydını veya mevcut şirket seçimini yapın.
3) Abonelik planlarını seed edin (opsiyonel, sandbox/demoda):
   - `python manage.py seed_billing_plans`
4) Rol ve izinleri oluşturun/seed edin:
   - `python manage.py seed_roles`
5) Şirket Admin ve Muhasebe/İzleyici rollerine kullanıcı atayın.
6) Ödeme entegrasyonu (PayTR) anahtarlarını girin (bkz. `odeme_rehberi.md`).
7) E-fatura/e-defter gibi e-Dönüşüm entegrasyonlarını yapılandırın.

#### Günlük/Haftalık/Aylık Operasyonlar
- Günlük
  - Yeni kullanıcı taleplerini onaylayın, roller verin
  - Başarısız giriş ve olağan dışı hareket loglarını gözden geçirin
  - Ödeme/abonelik bildirimlerini kontrol edin
- Haftalık
  - Finansal raporların üretildiğini ve paylaşım izinlerini doğrulayın
  - AI öneri motoru ve otomasyon kuyruklarını izleyin
  - Yedekleme görevlerinin başarı durumunu kontrol edin
- Aylık
  - Abonelik yenilemelerini ve faturalandırma özetlerini gözden geçirin
  - Rol/izin denetimi (en az ayrıcalık, gereksiz erişimleri kaldırın)
  - KVKK/GDPR bağlamında veri saklama/gizleme politikalarını gözden geçirin

#### Kritik Akışlar (How-To)
1) Kullanıcı Oluşturma ve Rol Atama
   - `/accounts/users/` üzerinden kullanıcı oluşturun
   - Rol seçin: Owner/Admin/Accountant/Viewer veya özel roller
   - Gerekirse şirket atamasını yapın (multi-company)

2) Şirket (Tenant) Yönetimi
   - Yeni tenant oluşturun ve şirket ekleyin
   - Kullanıcıları `UserTenantRole` ile role bağlayın (owner/admin/accountant/viewer)

3) Abonelik ve Plan Yönetimi
   - Planları görüntüleyin/düzenleyin (`/billing/`)
   - Kullanıcı aboneliğini atayın, süre ve plan değişikliği yapın
   - Ödeme akışlarını (PayTR callback/log) izleyin

4) Roller ve İzinler
   - Sistem rollerini gözden geçirin (Admin/Accountant/Auditor/InventoryManager)
   - Özel role yetki ekleyin veya kaldırın (en az ayrıcalık prensibi)
   - Şirket seviyesinde modül-temelli izinleri yönetin (okuma/yazma/rapor/approve)

5) Güvenlik ve Denetim
   - MFA ve parola politikası uygulayın
   - `/logs/audit/` ile hassas işlemleri (fatura silme, rol değişimi) izleyin
   - IP kısıtlama ve HMAC doğrulamalı webhook ayarlarını doğrulayın

6) Veri İhracı ve Yedekleme
   - Raporları CSV/Excel/PDF olarak dışa aktarın
   - Periyodik veritabanı ve medya dosyası yedeği planlayın
   - Geri yükleme testlerini periyodik olarak yapın (disaster recovery tatbikatı)

#### Sık Karşılaşılan Sorunlar ve Çözümleri
- Kullanıcı giriş yapamıyor → Şifre sıfırlayın, hesap kilidi/aktiflik durumunu kontrol edin
- Raporlar boş geliyor → Tarih/şirket filtresi ve demo verileri doğrulayın
- Ödeme başarısız/403 → PayTR sandbox IP/anahtarları ve callback URL kontrol edin
- E-fatura özelliği pasif → İlgili modül lisansı/planı aktif mi kontrol edin
- Yavaşlık/N+1 → Liste görünümlerinde `select_related/prefetch_related` optimizasyonlarını açın

#### Admin Checklist (Önerilen)
- [ ] MFA aktif
- [ ] Seed roller ve planlar uygulandı
- [ ] Owner/Admin rollerine yedek kullanıcı atandı
- [ ] Abonelik planı ve fiyatlar güncel
- [ ] Webhook/IP kısıtlamaları tanımlı
- [ ] Günlük yedekleme raporu alınıyor
- [ ] Denetim logları haftalık inceleniyor
- [ ] KVKK/GDPR süreçleri kayıt altında

#### İlgili Yönetim Komutları (opsiyonel)
```powershell
# Roller seed
python manage.py seed_roles

# Planlar seed
python manage.py seed_billing_plans

# Süper kullanıcı oluşturma (gerekirse)
python manage.py createsuperuser
```

---

### 🎓 Eğitimci Kullanıcısı

**Erişebileceği Sayfalar:**
```
✅ /dashboard/
✅ /education/courses/
✅ /education/students/
✅ /education/assessments/
✅ /education/certificates/
✅ /education/marketplace/
```

**Temel Özellikleri:**
- ✅ Kurs & Modül oluşturma
- ✅ Test & Quiz hazırlama
- ✅ Öğrenci performans takibi
- ✅ Sertifika dağıtımı (NFT)
- ✅ İçerik pazarlama
- ✅ Gelir yönetimi

---

### 📚 Öğrenci Kullanıcısı

**Erişebileceği Sayfalar:**
```
✅ /dashboard/
✅ /education/my-courses/
✅ /education/certificates/
✅ /games/simulations/
✅ /community/forums/
✅ /achievements/
```

**Temel Özellikleri:**
- ✅ İnteraktif öğrenme modülleri
- ✅ Video dersler & testler
- ✅ Gamifikasyon sistemi
- ✅ Sanal şirket simülasyonu
- ✅ Blockchain sertifikalar
- ✅ Topluluk & forum

---

### 🎮 Oyuncu Kullanıcısı

**Erişebileceği Sayfalar:**
```
✅ /dashboard/
✅ /games/fingame/
✅ /games/tournaments/
✅ /games/leaderboard/
✅ /games/clan/
✅ /nft/marketplace/
✅ /achievements/
```

**Temel Özellikleri:**
- ✅ 3D muhasebe oyunu
- ✅ Şirket yönetimi simülasyonu
- ✅ PvP turnuvalar
- ✅ NFT koleksiyonları
- ✅ Clan sistemi
- ✅ Liderlik tablosu

---

## 🔧 Sorun Giderme

### Problem 1: Demo veriler oluşturulmadı

**Çözüm:**
```bash
# Migration'ları çalıştır
python manage.py migrate

# Script'i tekrar çalıştır
python scripts/create_demo_scenarios.py --type all
```

---

### Problem 2: Giriş yapamıyorum

**Çözüm:**
```python
# Django shell'de şifre resetle
python manage.py shell

from src.apps.accounts.models import CustomUser
from django.contrib.auth.hashers import make_password

user = CustomUser.objects.get(username='kobi_demo')
user.password = make_password('Demo123!')
user.save()
```

---

### Problem 3: Şirket bilgisi görünmüyor

**Çözüm:**
```python
# Django shell'de kontrol et
python manage.py shell

from src.apps.accounts.models import CustomUser

user = CustomUser.objects.get(username='kobi_demo')
print(f"Company: {user.company}")

# Eğer None ise, şirket ata
from src.apps.accounting.models import Company
company = Company.objects.first()
user.company = company
user.save()
```

---

### Problem 4: Raporlar boş görünüyor

**Çözüm:**
1. Filtre ayarlarını kontrol et (yıl, ay seçimi)
2. Demo verilerin doğru tarihte oluşturulduğunu kontrol et
3. Script'i tekrar çalıştır:
```bash
python scripts/create_demo_scenarios.py --type kobi
```

---

### Problem 5: AI önerileri çalışmıyor

**Çözüm:**
```bash
# Gerekli paketlerin kurulu olduğunu kontrol et
pip install -r requirements.txt

# AI servislerini test et
python manage.py shell
from src.apps.ai_assistant.services import FinancialAIService
service = FinancialAIService()
# Test çalıştır
```

---

## 📞 Destek ve İletişim

**Teknik Destek:**
- 📧 support@finasis.com
- 📱 +90 850 XXX XX XX
- 💬 Discord: discord.gg/finasis

**Dokümantasyon:**
- 📚 [Kullanıcı Senaryoları](./kullanici_senaryolari.md)
- 📋 [Hızlı Başvuru](./kullanici_senaryolari_ozet.md)
- 🎬 [Demo Rehberi](./demo_senaryosu.md)
- 👥 [Roller ve Yetkiler Kılavuzu](./roller_ve_yetkiler_kilavuzu.md) - **YENİ!**
- 🏢 [Şirket Kayıt İşlem Kılavuzu](./sirket_kayit_islem_kilavuzu.md)

---

## 🚀 Sonraki Adımlar

1. ✅ Demo verileri oluştur
2. ✅ Tüm kullanıcı tiplerini test et
3. ✅ Senaryoları gerçek kullanıcılarla doğrula
4. ✅ Geri bildirim topla
5. ✅ İyileştirmeler yap
6. ✅ Production'a deploy et

---

## 📝 Notlar

- Demo kullanıcıları **sadece test amaçlıdır**
- Production ortamında demo verileri **kullanmayın**
- Güvenlik için demo şifrelerini **mutlaka değiştirin**
- Her yeni versiyonda senaryoları **güncelleyin**

---

*Son güncelleme: Ekim 2025*
*FinAsis Platform - Kullanıcı Senaryoları v1.0*
