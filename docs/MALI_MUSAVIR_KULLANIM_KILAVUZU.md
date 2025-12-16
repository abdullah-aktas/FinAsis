# Mali Müşavirlik Modülü - Kullanım Kılavuzu

## 📋 İçindekiler

1. [Giriş](#giriş)
2. [Mali Müşavir Kaydı](#mali-müşavir-kaydı)
3. [Müşteri Yönetimi](#müşteri-yönetimi)
4. [Beyanname Yönetimi](#beyanname-yönetimi)
5. [Fatura Yönetimi](#fatura-yönetimi)
6. [Danışmanlık Oturumları](#danışmanlık-oturumları)
7. [Marketplace](#marketplace)
8. [Raporlama](#raporlama)
9. [Sık Sorulan Sorular](#sık-sorulan-sorular)

---

## 🚀 Giriş

Mali müşavirlik modülü, SMMM ve YMM'ler için tasarlanmış kapsamlı bir müşteri yönetimi platformudur.

**Erişim:** `https://finasis.com.tr/advisors/` veya `https://finasis.com.tr/products/mali-musavir/`

### Gereksinimler

- FinAsis hesabı
- `financial_advisor` veya `mali_musavir` rolü
- Veya `AdvisorProfile` kaydı

---

## 👤 Mali Müşavir Kaydı

### 1. Profil Oluşturma

#### Temel Profil (AdvisorProfile)

1. Admin panelinden veya API ile oluşturulur
2. Gerekli bilgiler:
   - Kullanıcı hesabı
   - Tip (SMMM veya YMM)
   - Oda numarası (chamber_no)
   - MERSIS numarası (opsiyonel)

#### Marketplace Profili (ConsultantProfile)

Marketplace'de hizmet sunmak için:

1. **Advisors > Marketplace > Profil Oluştur** menüsüne gidin
2. Zorunlu bilgileri doldurun:
   - Görünür isim
   - Biyografi
   - Şehir
   - Telefon
   - Saatlik ücret
3. **Zorunlu Belgeler:**
   - Diploma/Mezuniyet belgesi
   - Mezuniyet belgesi/Transkript
4. **Uzmanlık Alanları:** JSON formatında
5. **Çalışma Saatleri:** JSON formatında

**Örnek Uzmanlık Alanları:**
```json
["Vergi Danışmanlığı", "Muhasebe Hizmetleri", "Denetim"]
```

**Örnek Çalışma Saatleri:**
```json
{
  "monday": {"start": "09:00", "end": "18:00"},
  "tuesday": {"start": "09:00", "end": "18:00"},
  "wednesday": {"start": "09:00", "end": "18:00"},
  "thursday": {"start": "09:00", "end": "18:00"},
  "friday": {"start": "09:00", "end": "18:00"}
}
```

### 2. Onay Süreci

1. Belgeler yüklendikten sonra admin onayı beklenir
2. Admin belgeleri doğrular
3. Onaylandıktan sonra blockchain anlaşması otomatik oluşturulur
4. Marketplace'de görünür hale gelir

---

## 👥 Müşteri Yönetimi

### Müşteri Ekleme

1. **Advisors > Müşteriler > Yeni Müşteri Ekle**
2. Müşteri bilgilerini girin:
   - Ad/Soyad veya Şirket Adı
   - VKN/TCKN
   - MERSIS No (opsiyonel)
   - Şirket (opsiyonel - tenancy.Company ile bağlantı)

### Engagement (İlişki) Oluşturma

Müşteri ile danışmanlık ilişkisi kurmak için:

1. Müşteri detay sayfasından **"Yeni İlişki"** butonuna tıklayın
2. İş kapsamını seçin:
   - e-Defter
   - e-Beyan
   - Her ikisi
3. Durum: **Aktif** olarak işaretleyin
4. Kaydet

### Müşteri Detay Sayfası

Müşteri detay sayfasında görüntülenen bilgiler:
- Temel bilgiler
- Beyannameler
- Danışmanlık oturumları
- Dokümanlar
- Sözleşmeler

---

## 📋 Beyanname Yönetimi

### Beyanname Listesi

1. **Advisors > Beyannameler** menüsüne gidin
2. Tüm aktif müşterilerin beyannameleri listelenir
3. Filtreleme:
   - Durum (draft, submitted, approved)
   - Beyanname tipi (KDV, Muhtasar, BA/BS)

### Yeni Beyanname Oluşturma

1. **Advisors > Beyannameler > Yeni Beyanname** butonuna tıklayın
2. Formu doldurun:
   - Müşteri/Şirket seçin
   - Beyanname tipi (KDV, Muhtasar, BA/BS)
   - Dönem (YYYY-MM formatında, örn: 2025-01)
3. **Kaydet** butonuna tıklayın
4. Beyanname **Taslak** durumunda oluşturulur

### Beyanname Durumları

- **draft** - Taslak
- **submitted** - Gönderildi
- **approved** - Onaylandı
- **rejected** - Reddedildi

---

## 🧾 Fatura Yönetimi

### Fatura Listesi

1. **Advisors > Faturalar** menüsüne gidin
2. Tüm aktif müşterilerin faturaları listelenir
3. İstatistikler:
   - Toplam Bekleyen Tutar
   - Toplam Ödenen Tutar
4. Filtreleme:
   - Durum (draft, sent, paid, cancelled)

### Fatura Detayları

Fatura detay sayfasında:
- Fatura numarası
- Müşteri bilgileri
- Fatura kalemleri
- Toplam tutar
- Durum
- Ödeme bilgileri

---

## 💬 Danışmanlık Oturumları

### Oturum Oluşturma

1. **Advisors > Danışmanlık Oturumları > Yeni Oturum** butonuna tıklayın
2. Formu doldurun:
   - Müşteri seçin
   - Oturum tipi (İlk Görüşme, Rutin, Acil, vb.)
   - Planlanan tarih ve saat
   - Süre (dakika)
   - Gündem
3. **Kaydet** butonuna tıklayın

### Oturum Tipleri

- **initial** - İlk Görüşme
- **regular** - Rutin Danışmanlık
- **urgent** - Acil Danışmanlık
- **review** - İnceleme/Review
- **planning** - Planlama
- **training** - Eğitim

### Oturum Durumları

- **scheduled** - Planlandı
- **in_progress** - Devam Ediyor
- **completed** - Tamamlandı
- **cancelled** - İptal Edildi
- **rescheduled** - Ertelendi

### Oturum Notları

Oturum tamamlandıktan sonra:
1. Oturum detay sayfasına gidin
2. **Görüşme Notları** alanına notlarınızı yazın
3. **Aksiyonlar** alanına yapılacakları ekleyin (JSON formatında)
4. **Takip Gerekli** işaretleyin ve takip tarihi belirleyin
5. **Kaydet**

---

## 🛒 Marketplace

### Marketplace Profili

Marketplace'de görünmek için:

1. **ConsultantProfile** oluşturun (yukarıda anlatıldı)
2. Belgeleri yükleyin
3. Admin onayını bekleyin
4. Onaylandıktan sonra marketplace'de görünürsünüz

### Hizmet Paketleri Oluşturma

1. **Marketplace > Hizmetlerim > Yeni Hizmet** butonuna tıklayın
2. Formu doldurun:
   - Hizmet başlığı
   - Kategori (Vergi Danışmanlığı, Muhasebe, vb.)
   - Açıklama
   - Fiyatlandırma tipi (Saatlik, Sabit, Aylık, Proje)
   - Fiyat
   - Süre (dakika) veya Tahmini teslim (gün)
   - Dahil olanlar (JSON listesi)
3. **Kaydet** ve **Yayınla**

### Randevu Yönetimi

Müşteriler marketplace üzerinden randevu alabilir:

1. Müşteri marketplace'de mali müşaviri seçer
2. Müsait saatleri görüntüler
3. Randevu oluşturur
4. Mali müşavir onaylar veya reddeder
5. Onaylandıktan sonra otomatik toplantı oluşturulur

### Ödeme Yönetimi

- Müşteri ödeme yapar
- Platform komisyonu kesilir (%15 varsayılan)
- Kalan tutar mali müşavire ödenir
- Aylık dönemler halinde ödeme yapılır

---

## 📊 Raporlama

### Rapor Oluşturma

1. **Advisors > Raporlar > Yeni Rapor** butonuna tıklayın
2. Formu doldurun:
   - Müşteri seçin
   - Rapor tipi (Vergi Analizi, Mali İnceleme, vb.)
   - Başlık
   - Yönetici Özeti
   - Detaylı İçerik
   - Bulgular (JSON listesi)
   - Öneriler (JSON listesi)
   - Dönem (başlangıç ve bitiş tarihleri)
3. **Kaydet** ve **Onayla**

### Rapor Tipleri

- **tax_analysis** - Vergi Analizi
- **financial_review** - Mali İnceleme
- **compliance_check** - Uyumluluk Kontrolü
- **business_valuation** - İşletme Değerleme
- **budget_planning** - Bütçe Planlama
- **audit_report** - Denetim Raporu
- **monthly_summary** - Aylık Özet
- **custom** - Özel Rapor

### Rapor Teslimi

1. Rapor hazırlandıktan sonra **Onayla** butonuna tıklayın
2. PDF veya Excel olarak indirebilirsiniz
3. Müşteriye e-posta ile gönderebilirsiniz
4. **Teslim Et** butonuna tıklayarak müşteriye iletin

---

## ❓ Sık Sorulan Sorular

### Marketplace'de görünmüyorum

**Çözüm:**
1. ConsultantProfile oluşturdunuz mu?
2. Belgeler yüklendi mi?
3. Admin onayı verildi mi?
4. `approval_status='approved'` mi?
5. `accepts_new_clients=True` mi?

### Randevu oluşturulamıyor

**Çözüm:**
1. Müsaitlik takvimi oluşturuldu mu?
2. `availability_status='available'` mi?
3. Çalışma saatleri doğru mu?
4. `instant_booking=True` ise onay gerekmez

### Ödeme alınamıyor

**Çözüm:**
1. Randevu tamamlandı mı? (`status='completed'`)
2. Ödeme durumu kontrol edin (`payment_status='paid'`)
3. Payout oluşturuldu mu?
4. Banka bilgileri doğru mu?

### Blockchain anlaşması oluşturulamadı

**Çözüm:**
1. Blockchain servisi aktif mi?
2. Belgeler doğrulandı mı?
3. Admin onayı verildi mi?
4. Hata loglarını kontrol edin

---

## 🔗 İlgili Dokümanlar

- [Mali Müşavirlik Modülü Analizi](MALI_MUSAVIR_MODUL_ANALIZ.md)
- [Admin Panel Kullanım Kılavuzu](ADMIN_PANEL_KULLANIM_KILAVUZU.md)
- [Marketplace README](../advisors/MARKETPLACE_README.md)

---

**Son Güncelleme:** 2025-01-XX  
**Versiyon:** 1.0

