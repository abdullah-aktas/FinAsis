# FinAsis Roller ve Yetkiler Kılavuzu

Bu kılavuz, FinAsis platformunda farklı rollerdeki kullanıcılar için yetki kapsamları, sorumluluklar ve günlük iş akışlarını detaylı olarak açıklar.

---

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Şirket Sahibi (Owner)](#-şirket-sahibi-owner)
3. [Yönetici (Admin)](#-yönetici-admin)
4. [Mali Müşavir](#-mali-müşavir)
5. [Muhasebeci (Accountant)](#-muhasebeci-accountant)
6. [Denetçi (Auditor)](#-denetçi-auditor)
7. [Stok/Depo Sorumlusu](#-stokdepo-sorumlusu)
8. [Satış Temsilcisi](#-satış-temsilcisi)
9. [İzleyici (Viewer)](#-izleyici-viewer)
10. [Rol Karşılaştırma Tablosu](#-rol-karşılaştırma-tablosu)
11. [Rol Atama ve Yönetimi](#-rol-atama-ve-yönetimi)
12. [Sık Sorulan Sorular](#-sık-sorulan-sorular)

---

## 🎯 Genel Bakış

FinAsis platformu, şirket içindeki farklı görev ve sorumluluklar için rol tabanlı erişim kontrolü (RBAC) kullanır.

### Rol Hiyerarşisi

```
┌─────────────────────────────────────┐
│      Şirket Sahibi (Owner)          │  ← Tam Yetki
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       Yönetici (Admin)              │  ← Yüksek Yetki
└─────────────────────────────────────┘
              ↓
┌──────────────────┬──────────────────┐
│  Mali Müşavir    │   Muhasebeci     │  ← Orta Yetki
└──────────────────┴──────────────────┘
              ↓
┌──────────────────┬──────────────────┬──────────────────┐
│    Denetçi       │  Stok Sorumlusu  │  Satış Temsilcisi│  ← Sınırlı Yetki
└──────────────────┴──────────────────┴──────────────────┘
              ↓
┌─────────────────────────────────────┐
│        İzleyici (Viewer)            │  ← Sadece Görüntüleme
└─────────────────────────────────────┘
```

### Temel Yetki Seviyeleri

| Seviye | Açıklama | Örnek İşlemler |
|--------|----------|----------------|
| **CREATE** | Yeni kayıt oluşturma | Fatura, gider, müşteri ekleme |
| **READ** | Görüntüleme | Raporları, faturaları görme |
| **UPDATE** | Düzenleme | Mevcut kayıtları güncelleme |
| **DELETE** | Silme | Kayıtları silme |
| **APPROVE** | Onaylama | Giderleri, faturaları onaylama |
| **EXPORT** | Dışa aktarma | Excel, PDF export |
| **REPORT** | Raporlama | Finansal rapor üretme |
| **ADMIN** | Yönetim | Kullanıcı, ayar yönetimi |

---

## 👑 Şirket Sahibi (Owner)

### Rol Tanımı
Şirketin yasal sahibi veya ortağı. Tüm sistemde tam yetkiye sahip, stratejik kararları alır.

### Yetki Kapsamı
```
✅ TÜM YETKİLER (CREATE, READ, UPDATE, DELETE, APPROVE, EXPORT, REPORT, ADMIN)
```

### Erişebileceği Sayfalar
```
✅ /dashboard/                    # Ana Panel
✅ /accounting/*                  # Tüm Muhasebe Modülleri
✅ /finance/*                     # Tüm Finans Modülleri
✅ /billing/subscriptions/        # Abonelik Yönetimi
✅ /settings/*                    # Tüm Ayarlar
✅ /accounts/users/               # Kullanıcı Yönetimi
✅ /accounts/roles/               # Rol Yönetimi
✅ /permissions/                  # İzin Yönetimi
✅ /tenancy/companies/            # Şirket Yönetimi
✅ /blockchain/                   # Blockchain Kayıtları
✅ /ai-assistant/                 # AI Asistan
✅ /audit/logs/                   # Denetim Logları
```

### Günlük İş Akışı

#### Sabah Rutini (09:00-10:00)
1. Dashboard'u kontrol et
   - Günlük nakit durumu
   - Bekleyen ödemeler
   - Kritik uyarılar
2. AI önerilerini incele
   - Risk analizi
   - Tahminler
   - Optimizasyon önerileri
3. Onay bekleyen işlemleri gözden geçir
   - Büyük giderler
   - Önemli faturalar

#### Haftalık Görevler (Her Pazartesi)
- Haftalık finansal özet raporunu incele
- Nakit akış projeksiyonunu kontrol et
- Ekip performansını değerlendir
- Yeni kullanıcı ve rol taleplerini onayla

#### Aylık Görevler (Ay başı)
- Aylık bilanço ve gelir tablosunu incele
- Bütçe-gerçekleşme karşılaştırması yap
- Yatırımcı/ortak raporlarını hazırla
- Abonelik ve maliyet analizi

#### Stratejik Kararlar
- Plan yükseltme/değiştirme
- Yeni modül aktivasyonu
- Çoklu şirket ekleme
- Entegrasyon onayları

### Önemli Notlar
> **⚠️ Dikkat:** Şirket sahibi yetkilerini dikkatli paylaşın. Kritik işlemler için MFA (çok faktörlü doğrulama) aktif olmalı.

> **💡 İpucu:** Yedek bir Owner hesabı oluşturun. Acil durumlar için güvenilir bir ortağa veya yöneticiye Owner yetkisi verilebilir.

---

## 🔑 Yönetici (Admin)

### Rol Tanımı
Şirketin operasyonel yöneticisi. Günlük işleri yönetir, kullanıcıları organize eder, ancak kritik mali kararlar için Owner onayı gerekir.

### Yetki Kapsamı
```
✅ CREATE, READ, UPDATE (kısıtlı DELETE, APPROVE)
✅ Kullanıcı yönetimi (Owner rolü hariç)
✅ Tüm raporlara erişim
⛔ Abonelik değiştirme
⛔ Şirket silme
⛔ Blockchain kayıt silme
```

### Erişebileceği Sayfalar
```
✅ /dashboard/
✅ /accounting/invoices/          # Faturalar (tüm işlemler)
✅ /accounting/expenses/          # Giderler (onaylama dahil)
✅ /accounting/customers/         # Müşteriler
✅ /accounting/products/          # Ürünler
✅ /finance/reports/              # Finansal Raporlar
✅ /accounts/users/               # Kullanıcı Yönetimi (sınırlı)
✅ /settings/general/             # Genel Ayarlar
⛔ /billing/subscriptions/       # Abonelik (sadece görüntüleme)
⛔ /settings/integrations/       # Entegrasyonlar (sadece görüntüleme)
```

### Günlük İş Akışı

#### Sabah Kontrolleri (09:00-09:30)
1. Dashboard'da günlük özeti incele
2. Ekip üyelerinin günlük raporlarını kontrol et
3. Bekleyen onay işlemlerini gözden geçir
4. Kritik uyarıları (stok, ödeme, vade) takip et

#### Gün İçi Görevler
- Yeni fatura ve gider kayıtlarını onaylama
- Müşteri ve tedarikçi kayıtlarını yönetme
- Ürün/hizmet güncellemeleri yapma
- Ekip sorularına cevap verme
- Raporları paylaşma

#### Haftalık Görevler
- Haftalık ekip toplantısı
- Kullanıcı izinlerini gözden geçirme
- Performans raporları hazırlama
- Veri tutarlılığı kontrolü

#### Aylık Görevler
- Aylık kapanış kontrolü
- Muhasebeci ile koordinasyon
- İyileştirme önerileri sunma

### Tipik Senaryolar

**Senaryo 1: Yeni Kullanıcı Ekleme**
```
1. Ayarlar > Kullanıcılar > "Yeni Kullanıcı Davet Et"
2. E-posta ve rolü belirle (Muhasebeci, Satış, vb.)
3. Modül erişimlerini ayarla
4. Davet gönder
5. Yeni kullanıcının ilk girişini takip et
```

**Senaryo 2: Büyük Tutarlı Gider Onaylama**
```
1. Muhasebe > Giderler > "Onay Bekleyenler"
2. Gider detaylarını incele
3. Belge/fatura ekli mi kontrol et
4. Bütçe uygunluğunu kontrol et
5. Onayla veya reddet (not ekle)
```

---

## 💼 Mali Müşavir

### Rol Tanımı
Şirketin dışarıdan danışmanlık veren mali müşaviri. Vergi beyannameleri, mali raporlar ve yasal uyumluluk konularında uzman.

### Yetki Kapsamı
```
✅ READ (tüm finansal veriler)
✅ EXPORT (raporlar, vergi dosyaları)
✅ REPORT (özel raporlar oluşturma)
✅ UPDATE (muhasebe kayıtları - onay gerektirir)
⛔ DELETE (kayıt silme yok)
⛔ Kullanıcı yönetimi
⛔ Ayar değişikliği
```

### Erişebileceği Sayfalar
```
✅ /dashboard/                    # Ana Panel (özet bilgiler)
✅ /accounting/invoices/          # Faturalar (görüntüleme + düzeltme önerisi)
✅ /accounting/expenses/          # Giderler
✅ /accounting/customers/         # Müşteriler (görüntüleme)
✅ /accounting/bank-accounts/     # Banka hesapları
✅ /finance/reports/*             # Tüm Finansal Raporlar
✅ /finance/bilanco/              # Bilanço
✅ /finance/gelir-tablosu/        # Gelir Tablosu
✅ /finance/mizan/                # Mizan
✅ /edoc/efatura/                 # e-Fatura kayıtları
✅ /edoc/edefter/                 # e-Defter
✅ /audit/tax-reports/            # Vergi raporları
⛔ /accounts/users/               # Kullanıcı yönetimi yok
⛔ /settings/                     # Ayarlar yok
```

### Aylık İş Akışı

#### Ay Başı (1-5 arası)
1. Önceki ayın kapanış raporlarını al
2. Geçici mizan çek
3. KDV beyannamesi için veri hazırlığı
4. Stopaj hesaplamaları
5. Muhtasar beyanname hazırlığı

#### Ay Ortası (10-15 arası)
1. Cari durumu kontrol et
2. Alacak-borç mutabakatları
3. Gelir-gider analizleri
4. Bütçe sapma raporu

#### Ay Sonu (25-30 arası)
1. Final bilançosu hazırlama
2. Gelir tablosu kontrolü
3. Dipnotlar ve açıklamalar
4. Şirket yönetimine sunum hazırlığı

#### Üç Aylık Dönemler
- Geçici vergi beyannamesi
- Sosyal güvenlik bildirgeleri
- Damga vergisi beyanı

#### Yıllık Görevler
- Yıllık gelir/kurumlar vergisi beyanı
- Bilanço ve dipnotlar
- Defter kapama işlemleri
- e-Defter beratı hazırlama

### Özel Raporlar

Mali müşavirler için hazır raporlar:
- **Mizan:** Hesap bazlı dönem sonu bakiyeleri
- **KDV Raporu:** Hesaplanan, indirilecek, ödenecek KDV
- **Gider Analizi:** Kategori bazlı gider dağılımı
- **Alacak-Borç Durum:** Müşteri/tedarikçi cari hesap özeti
- **Kâr-Zarar:** Aylık/üç aylık/yıllık kârlılık analizi

### Tipik Senaryolar

**Senaryo 1: Aylık KDV Beyannamesi Hazırlama**
```
1. Finans > Raporlar > "KDV Raporu"
2. Dönem seçimi: Önceki ay
3. Hesaplanan KDV: Satış faturalarından
4. İndirilecek KDV: Alış faturalarından
5. Excel'e aktar
6. GİB portalına veri girişi
```

**Senaryo 2: Muhasebe Hatası Düzeltme**
```
1. Muhasebe > Faturalar > Hatalı kaydı bul
2. "Düzeltme Öner" butonuna tıkla
3. Düzeltme notunu yaz
4. Muhasebeciye veya Admin'e bildirim gönder
5. Onay sonrası düzeltme yapılır
```

**Senaryo 3: Yıllık Bilanço Hazırlama**
```
1. Finans > Bilanço
2. Dönem: Yıllık (01.01.YYYY - 31.12.YYYY)
3. Aktif/Pasif dengesini kontrol et
4. Detaylı PDF rapor al
5. Dipnotları ekle
6. e-Defter beratına aktar
```

---

## 📊 Muhasebeci (Accountant)

### Rol Tanımı
Şirketin günlük muhasebe işlemlerini yürüten kişi. Fatura, gider, banka işlemlerini kaydeder ve raporlar.

### Yetki Kapsamı
```
✅ CREATE (fatura, gider, müşteri, ürün)
✅ READ (tüm muhasebe verileri)
✅ UPDATE (kendi oluşturduğu kayıtlar)
✅ EXPORT (raporlar)
⛔ DELETE (sadece kendi taslakları)
⛔ APPROVE (onaylama yetkisi yok, önerir)
⛔ Kullanıcı yönetimi
⛔ Ayar değişikliği
```

### Erişebileceği Sayfalar
```
✅ /dashboard/
✅ /accounting/invoices/          # Faturalar (CREATE, UPDATE)
✅ /accounting/expenses/          # Giderler (CREATE, UPDATE)
✅ /accounting/customers/         # Müşteriler
✅ /accounting/suppliers/         # Tedarikçiler
✅ /accounting/products/          # Ürünler
✅ /accounting/bank-accounts/     # Banka Hesapları
✅ /accounting/bank-transactions/ # Banka İşlemleri
✅ /finance/reports/              # Raporlar (görüntüleme)
✅ /edoc/efatura/                 # e-Fatura (gönderim)
⛔ /billing/                      # Abonelik yönetimi yok
⛔ /accounts/users/               # Kullanıcı yönetimi yok
⛔ /settings/                     # Ayarlar yok
```

### Günlük İş Akışı

#### Sabah Rutini (09:00-10:00)
1. Dashboard'u aç
2. Dün oluşturulan kayıtları kontrol et
3. E-posta ile gelen faturaları sisteme kaydet
4. Banka hareketlerini senkronize et (API varsa)
5. Bekleyen tahsilat ve ödemeleri kontrol et

#### Gün İçi İşlemler
- **Fatura Kesme:**
  - Satış ekibinden gelen talepleri işle
  - Müşteri bilgilerini doğrula
  - Ürün/hizmet detaylarını ekle
  - e-Fatura olarak gönder (GİB)
  - PDF'i müşteriye mail at

- **Gider Kaydetme:**
  - Tedarikçi faturalarını sisteme gir
  - Belge/dekont yükle
  - Kategori ve KDV bilgilerini doğrula
  - Onaya gönder (Admin/Owner'a)

- **Banka Mutabakatı:**
  - Banka ekstresini indir
  - Sisteme manuel kayıtları gir
  - Fatura ödemeleriyle eşleştir
  - Uyumsuzlukları not al

#### Haftalık Görevler
- Haftalık gelir-gider özeti hazırla
- Müşteri ödemelerini takip et (vadesi geçenler)
- Tedarikçi ödemelerini planla
- Stok durumunu kontrol et (eğer varsa)

#### Aylık Görevler
- Ay sonu kapanışı için veri hazırlığı
- Alacak-borç listelerini güncelle
- Mali müşavire rapor gönder
- Muhasebecilik arşivleme

### Tipik Senaryolar

**Senaryo 1: Satış Faturası Kesme**
```
1. Muhasebe > Faturalar > "Yeni Fatura"
2. Müşteri seç: "ABC Teknoloji Ltd."
3. Fatura tipi: e-Fatura (müşteri e-fatura kullanıcısı)
4. Ürün ekle: "Web Sitesi Geliştirme" - 1 adet - 25.000 TL
5. KDV %20 otomatik hesaplanır
6. Açıklama: "Proje teslimi - Sözleşme No: 2025/001"
7. "Kaydet ve Gönder" → GİB'e otomatik iletilir
8. PDF'i e-posta ile müşteriye gönder
```

**Senaryo 2: Gider Kaydı**
```
1. Muhasebe > Giderler > "Yeni Gider"
2. Kategori: Ofis Kirası
3. Tedarikçi: "XYZ Gayrimenkul A.Ş."
4. Tutar: 12.000 TL (KDV dahil)
5. Fatura No: 2025/0045
6. Fatura tarih: 01.01.2025
7. Belge yükle: kira_faturasi_ocak.pdf
8. "Onaya Gönder" → Admin'e bildirim gider
```

**Senaryo 3: Banka İşlemi Girişi**
```
1. Muhasebe > Banka Hesapları > "İş Bankası Ticari"
2. "Yeni İşlem" butonuna tıkla
3. Tipi: Gelen (Para Girişi)
4. Tutar: 25.000 TL
5. Açıklama: "ABC Teknoloji - Fatura No: 2025/001 ödemesi"
6. İlişkilendir: Fatura bul ve eşleştir
7. Dekont yükle: dekont_20250115.pdf
8. Kaydet → Fatura otomatik "Ödendi" olarak işaretlenir
```

---

## 🔍 Denetçi (Auditor)

### Rol Tanımı
İç denetim veya compliance görevlisi. Tüm işlemleri görüntüler, raporlar ama değişiklik yapamaz. Uyumsuzlukları tespit eder.

### Yetki Kapsamı
```
✅ READ (tüm veriler)
✅ EXPORT (denetim raporları)
✅ REPORT (özel denetim raporları)
⛔ CREATE, UPDATE, DELETE yok
⛔ APPROVE yok
```

### Erişebileceği Sayfalar
```
✅ /dashboard/
✅ /accounting/* (sadece görüntüleme)
✅ /finance/* (sadece görüntüleme)
✅ /audit/logs/                   # Denetim Logları
✅ /audit/reports/                # Denetim Raporları
✅ /blockchain/verify/            # Blockchain Doğrulama
✅ /permissions/audit/            # Yetki Geçmişi
⛔ Herhangi bir değişiklik/silme işlemi yok
```

### Aylık/Üç Aylık İş Akışı

#### Rutin Kontroller
1. Tüm faturaların e-Fatura ile tutarlılığını kontrol et
2. Gider onaylarının prosedüre uygun olduğunu doğrula
3. Banka mutabakatı uyumsuzluklarını raporla
4. Yetkisiz erişim denemelerini tespit et
5. Blockchain kayıtlarını doğrula

#### Denetim Raporları
- **İşlem Hacmi Raporu:** Aylık fatura/gider sayısı ve tutarları
- **Yetki Değişikliği Raporu:** Rol ve izin güncellemeleri
- **Uyumsuzluk Raporu:** Hatalı/eksik kayıtlar
- **Güvenlik Raporu:** Başarısız giriş denemeleri, şüpheli aktiviteler

### Tipik Senaryolar

**Senaryo 1: Aylık Denetim Raporu Hazırlama**
```
1. Denetim > Raporlar > "Aylık Denetim"
2. Dönem seç: Ocak 2025
3. Kontrol listesi:
   - ✅ Tüm faturalar e-Fatura ile uyumlu
   - ✅ Gider onayları prosedüre uygun
   - ⚠️ 3 adet eksik belge tespit edildi
   - ⚠️ 2 faturada KDV hesaplama hatası
4. Rapor oluştur ve yönetime gönder
```

---

## 📦 Stok/Depo Sorumlusu

### Rol Tanımı
Envanter ve stok yönetiminden sorumlu. Ürün giriş-çıkışlarını takip eder, kritik seviyeleri izler.

### Yetki Kapsamı
```
✅ CREATE (stok hareketi)
✅ READ (ürünler, stok, depolar)
✅ UPDATE (stok miktarları)
⛔ Fatura kesme yok (sadece sevkiyat bildirimi)
⛔ Finansal raporlar yok
```

### Erişebileceği Sayfalar
```
✅ /dashboard/
✅ /accounting/products/          # Ürünler
✅ /inventory/stock/              # Stok Durumu
✅ /inventory/warehouses/         # Depolar
✅ /inventory/movements/          # Stok Hareketleri
✅ /inventory/alerts/             # Kritik Stok Uyarıları
⛔ /accounting/invoices/ (sadece görüntüleme)
⛔ /finance/* (erişim yok)
```

### Günlük İş Akışı

#### Sabah Kontrolleri
1. Dashboard'da kritik stok uyarılarını kontrol et
2. Dün gerçekleşen giriş-çıkışları gözden geçir
3. Bugünkü planlı sevkiyatları listele

#### Gün İçi İşlemler
- Mal kabul (tedarikçi teslimatları)
- Stok girişi kaydetme
- Sevkiyat hazırlama
- Stok sayımı (periyodik)

---

## 💰 Satış Temsilcisi

### Rol Tanımı
Müşteri ilişkileri ve satış süreçlerinden sorumlu. Teklif hazırlar, fatura talebinde bulunur.

### Yetki Kapsamı
```
✅ READ (müşteriler, ürünler, fiyat listeleri)
✅ CREATE (teklif, fatura talebi)
⛔ Fatura kesme yok (muhasebeci keser)
⛔ Finansal raporlar yok
```

### Erişebileceği Sayfalar
```
✅ /dashboard/
✅ /sales/customers/              # Müşteriler
✅ /sales/quotations/             # Teklifler
✅ /sales/orders/                 # Siparişler
✅ /accounting/products/          # Ürünler (fiyatlar)
⛔ /accounting/invoices/ (sadece kendi müşterilerinin faturaları)
⛔ /finance/* (erişim yok)
```

---

## 👀 İzleyici (Viewer)

### Rol Tanımı
Sadece raporları görüntüleyebilen kullanıcı. Ortak, yatırımcı, dış danışman vb. olabilir.

### Yetki Kapsamı
```
✅ READ (sadece özet raporlar)
⛔ Hiçbir değişiklik yapamaz
```

### Erişebileceği Sayfalar
```
✅ /dashboard/                    # Ana Panel (özet)
✅ /finance/reports/              # Finansal Raporlar (sadece özet)
⛔ Detaylı kayıtlara erişim yok
⛔ Export yok
```

---

## 📊 Rol Karşılaştırma Tablosu

| Özellik | Owner | Admin | Mali Müşavir | Muhasebeci | Denetçi | Stok | Satış | İzleyici |
|---------|-------|-------|--------------|------------|---------|------|-------|----------|
| **Fatura Oluşturma** | ✅ | ✅ | ⚠️ Önerir | ✅ | ❌ | ❌ | ⚠️ Talep | ❌ |
| **Fatura Silme** | ✅ | ⚠️ Onay | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Gider Kaydetme** | ✅ | ✅ | ⚠️ Önerir | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Gider Onaylama** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Finansal Raporlar** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ⚠️ Özet |
| **Excel Export** | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ Stok | ❌ | ❌ |
| **Kullanıcı Ekleme** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Rol Atama** | ✅ | ⚠️ Owner hariç | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Abonelik Yönetimi** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Ayarlar** | ✅ | ⚠️ Kısıtlı | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Denetim Logları** | ✅ | ✅ | ⚠️ Görür | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Stok Yönetimi** | ✅ | ✅ | ❌ | ⚠️ Görür | ⚠️ Görür | ✅ | ⚠️ Görür | ❌ |
| **e-Fatura Gönderimi** | ✅ | ✅ | ⚠️ Kontrol | ✅ | ❌ | ❌ | ❌ | ❌ |

**Semboller:**
- ✅ Tam yetki
- ⚠️ Kısıtlı/Onay gerektirir
- ❌ Erişim yok

---

## 🔧 Rol Atama ve Yönetimi

### Yeni Kullanıcıya Rol Atama

**Adım 1: Kullanıcı Davet Etme**
```
1. Ayarlar > Kullanıcılar > "Yeni Kullanıcı Davet Et"
2. E-posta adresini gir
3. Rol seçimi yap (dropdown'dan)
4. "Davet Gönder" butonuna tıkla
```

**Adım 2: Özel İzinler Tanımlama**
```
1. Kullanıcı listesinde ilgili kullanıcıya tıkla
2. "İzinler" sekmesine geç
3. Modül bazlı izinleri özelleştir:
   - Faturalar: ☑️ Okuma ☑️ Yazma ☐ Silme
   - Giderler: ☑️ Okuma ☑️ Yazma ☐ Onaylama
   - Raporlar: ☑️ Okuma ☑️ Export
4. Kaydet
```

### Özel Rol Oluşturma

Hazır roller yetmiyorsa özel rol oluşturabilirsiniz:

```
1. Ayarlar > Roller > "Yeni Rol Oluştur"
2. Rol adı: Örn. "Satış Müdürü"
3. İzinleri seç:
   Modül: Müşteriler
   - ☑️ CREATE (Yeni müşteri ekleme)
   - ☑️ READ (Müşteri görüntüleme)
   - ☑️ UPDATE (Müşteri güncelleme)
   - ☐ DELETE
   
   Modül: Faturalar
   - ☐ CREATE
   - ☑️ READ (Sadece kendi müşterilerinin faturaları)
   - ☐ UPDATE
   - ☐ DELETE
   
   Modül: Raporlar
   - ☑️ READ (Satış raporları)
   - ☑️ EXPORT
4. Kaydet
5. İstediğiniz kullanıcıya bu rolü atayın
```

---

## ❓ Sık Sorulan Sorular

### Rol ve Yetki Yönetimi

**S: Bir kullanıcının birden fazla rolü olabilir mi?**
C: Evet, bir kullanıcıya birden fazla rol atanabilir. İzinler birleştirilir (en geniş yetki geçerli olur).

**S: Rol değişikliği anında geçerli olur mu?**
C: Evet, rol değişiklikleri anında yansır. Kullanıcı sayfayı yenilediğinde yeni yetkileri görür.

**S: Silinen kullanıcının kayıtları ne olur?**
C: Kullanıcının oluşturduğu kayıtlar silinmez, ancak "Silinmiş Kullanıcı" olarak işaretlenir.

### Fatura ve Muhasebe

**S: Muhasebeci kestiği faturayı silebilir mi?**
C: Hayır. Sadece "Taslak" durumundaki kendi faturalarını silebilir. Kesinleşmiş faturaları sadece Owner/Admin silebilir.

**S: Mali müşavir neden fatura kesemiyor?**
C: Mali müşavir danışman rolündedir. Fatura kesmek yerine hatalı kayıtlar için "Düzeltme Önerisi" gönderir.

**S: Gider onayı zorunlu mu?**
C: Bu ayarlanabilir. Belirli tutarın üzerindeki giderler için onay zorunlu hale getirilebilir.

### Raporlama ve Denetim

**S: Denetçi hangi raporları görebilir?**
C: Denetçi tüm finansal raporları, denetim loglarını ve blockchain kayıtlarını görüntüleyebilir. Ancak hiçbir değişiklik yapamaz.

**S: Raporları kimler dışa aktarabilir?**
C: Owner, Admin, Mali Müşavir, Muhasebeci ve Denetçi. Diğer roller sadece ekranda görüntüleyebilir.

### Güvenlik

**S: Yetkisiz erişim denemelerini nasıl görebilirim?**
C: Denetim > Güvenlik Logları sayfasından başarısız giriş denemeleri ve şüpheli aktiviteleri izleyebilirsiniz.

**S: Bir kullanıcının geçmişte yaptığı işlemleri görebilir miyim?**
C: Evet. Denetim > Kullanıcı Aktiviteleri sayfasından tüm işlem geçmişini görebilirsiniz (Owner/Admin/Denetçi).

---

## 📞 Destek ve İletişim

**Teknik Destek:**
- 📧 E-posta: destek@finasis.com.tr
- 📱 Telefon: +90 850 XXX XX XX
- 💬 Canlı Destek: Dashboard (Profesyonel ve üzeri)

**Rol Yönetimi Danışmanlığı:**
- 📧 E-posta: danismanlik@finasis.com.tr
- 🌐 Web: https://www.finasis.com.tr/support

---

## 📚 İlgili Kaynaklar

- [Şirket Kayıt İşlem Kılavuzu](./sirket_kayit_islem_kilavuzu.md)
- [Admin Kullanma Kılavuzu](./admin_kullanici_kilavuzu.md)
- [Kullanıcı Senaryoları](./kullanici_senaryolari.md)
- [Ödeme Rehberi](./odeme_rehberi.md)

---

## ✅ Rol Atama Kontrol Listesi

Yeni bir kullanıcı eklerken kontrol edin:

- [ ] E-posta adresi doğru
- [ ] Doğru rol seçildi
- [ ] Gerekli modül izinleri verildi
- [ ] Deneme girişi yapıldı
- [ ] Kullanıcı eğitim aldı
- [ ] MFA aktif (kritik roller için)
- [ ] Yedek iletişim bilgisi kaydedildi

---

**Son güncelleme:** 15 Ekim 2025  
**Versiyon:** 1.0  
**FinAsis Platform** - Roller ve Yetkiler Kılavuzu

---

💼 **FinAsis ile güvenli ve organize ekip yönetimi!**  
🌐 [www.finasis.com.tr](https://www.finasis.com.tr)  
📧 [destek@finasis.com.tr](mailto:destek@finasis.com.tr)
