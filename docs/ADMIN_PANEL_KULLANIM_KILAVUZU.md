# FinAsis Admin Panel Kullanım Kılavuzu

## 📋 İçindekiler

1. [Giriş](#giriş)
2. [Genel Kullanım](#genel-kullanım)
3. [Modül Bazlı Kılavuzlar](#modül-bazlı-kılavuzlar)
4. [Sık Kullanılan İşlemler](#sık-kullanılan-işlemler)
5. [İpuçları ve Püf Noktaları](#ipuçları-ve-püf-noktaları)

---

## 🚀 Giriş

### Admin Paneline Erişim

1. Tarayıcınızda şu adresi açın: `https://finasis.com.tr/admin/`
2. Kullanıcı adı ve şifrenizi girin
3. **Önemli:** Admin paneline erişim için `is_staff=True` veya `is_superuser=True` yetkisine sahip olmanız gerekir

### İlk Giriş

- İlk girişte sistem sizi admin ana sayfasına yönlendirir
- Sol menüde tüm modüller listelenir
- Her modül altında ilgili modeller görünür

---

## 📚 Genel Kullanım

### Temel İşlemler

#### 1. Liste Görünümü (List View)
- Her model için liste sayfası mevcuttur
- **Arama:** Üst kısımdaki arama kutusunu kullanın
- **Filtreleme:** Sağ taraftaki filtrelerle sonuçları daraltın
- **Sıralama:** Sütun başlıklarına tıklayarak sıralayın

#### 2. Yeni Kayıt Ekleme
- Liste sayfasında sağ üstteki **"+ Ekle"** butonuna tıklayın
- Formu doldurun
- **Kaydet** butonuna tıklayın

#### 3. Kayıt Düzenleme
- Liste sayfasında düzenlemek istediğiniz kaydın üzerine tıklayın
- Formu güncelleyin
- **Kaydet** butonuna tıklayın

#### 4. Kayıt Silme
- Kayıt detay sayfasında **Sil** butonuna tıklayın
- Onaylayın
- **⚠️ Dikkat:** Silme işlemi geri alınamaz!

---

## 🎯 Modül Bazlı Kılavuzlar

### 1. Accounts (Hesap Yönetimi)

#### CustomUser (Kullanıcılar)
**Kullanım Amacı:** Sistem kullanıcılarını yönetmek

**Önemli Alanlar:**
- `username`: Kullanıcı adı (benzersiz, zorunlu)
- `email`: E-posta adresi (benzersiz, zorunlu)
- `is_staff`: Admin paneline erişim yetkisi
- `is_superuser`: Tüm yetkilere sahip kullanıcı
- `is_active`: Kullanıcı aktif mi?
- `company`: Kullanıcının bağlı olduğu şirket
- `user_type`: Kullanıcı tipi (KOBİ Sahibi, Muhasebeci, vb.)

**Sık Kullanılan İşlemler:**
- Yeni kullanıcı oluşturma
- Kullanıcı yetkilerini düzenleme
- Kullanıcıyı pasifleştirme/aktifleştirme
- Şifre sıfırlama (kullanıcı kendisi yapabilir)

**İpuçları:**
- `is_staff=True` olmadan admin paneline giriş yapılamaz
- `is_superuser=True` olan kullanıcılar tüm yetkilere sahiptir
- Kullanıcı silmek yerine `is_active=False` yapmak daha güvenlidir

#### UserRole (Kullanıcı Rolleri)
**Kullanım Amacı:** Sistem rolleri tanımlamak ve yönetmek

**Önemli Alanlar:**
- `name`: Rol adı (örn: "Muhasebeci", "Finans Yöneticisi")
- `hierarchy_level`: Hiyerarşi seviyesi (0=En yüksek)
- `permissions`: Rol yetkileri
- `is_active`: Rol aktif mi?

**Kullanım Senaryosu:**
1. Yeni rol oluşturun
2. Hiyerarşi seviyesini belirleyin
3. Yetkileri tanımlayın
4. Kullanıcılara atayın

#### UserProfile (Kullanıcı Profilleri)
**Kullanım Amacı:** Kullanıcı ek bilgilerini yönetmek

**Önemli Alanlar:**
- `user`: İlişkili kullanıcı
- `phone`: Telefon numarası
- `city`: Şehir
- `country`: Ülke
- `language`: Dil tercihi
- `timezone`: Saat dilimi

---

### 2. Accounting (Muhasebe)

#### Company (Şirketler)
**Kullanım Amacı:** Şirket bilgilerini yönetmek

**Önemli Alanlar:**
- `name`: Şirket adı
- `tax_number`: Vergi numarası (benzersiz)
- `trade_name`: Ticari unvan
- `sector`: Sektör
- `address`: Adres
- `phone`: Telefon
- `email`: E-posta

**Sık Kullanılan İşlemler:**
- Yeni şirket ekleme
- Şirket bilgilerini güncelleme
- Şirket silme (dikkatli olun!)

**İpuçları:**
- Vergi numarası benzersiz olmalıdır
- Şirket silindiğinde ilişkili tüm veriler etkilenir

#### Invoice (Faturalar)
**Kullanım Amacı:** Faturaları yönetmek

**Önemli Alanlar:**
- `invoice_number`: Fatura numarası
- `invoice_date`: Fatura tarihi
- `customer`: Müşteri
- `total_amount`: Toplam tutar
- `status`: Durum (Taslak, Gönderildi, Ödendi, vb.)

**Sık Kullanılan İşlemler:**
- Yeni fatura oluşturma
- Fatura durumunu güncelleme
- Fatura yazdırma

#### Customer (Müşteriler)
**Kullanım Amacı:** Müşteri bilgilerini yönetmek

**Önemli Alanlar:**
- `name`: Müşteri adı
- `tax_number`: Vergi numarası
- `email`: E-posta
- `phone`: Telefon
- `address`: Adres

---

### 3. Finance (Finans)

#### Transaction (İşlemler)
**Kullanım Amacı:** Finansal işlemleri yönetmek

**Önemli Alanlar:**
- `account`: Hesap
- `amount`: Tutar
- `transaction_type`: İşlem tipi (Gelir, Gider, Transfer)
- `date`: İşlem tarihi
- `description`: Açıklama

**Filtreleme:**
- Tarih aralığına göre filtreleme
- İşlem tipine göre filtreleme
- Hesaba göre filtreleme

#### Account (Hesaplar)
**Kullanım Amacı:** Finansal hesapları yönetmek

**Önemli Alanlar:**
- `name`: Hesap adı
- `account_type`: Hesap tipi (Nakit, Banka, Kredi, vb.)
- `balance`: Bakiye (otomatik hesaplanır)
- `currency`: Para birimi
- `is_active`: Aktif mi?

**İpuçları:**
- Bakiye otomatik hesaplanır, manuel değiştirmeyin
- Pasif hesaplar işlemlerde görünmez

#### Budget (Bütçeler)
**Kullanım Amacı:** Bütçe planlaması yapmak

**Önemli Alanlar:**
- `name`: Bütçe adı
- `amount`: Bütçe tutarı
- `period`: Dönem (Aylık, Yıllık)
- `start_date`: Başlangıç tarihi
- `end_date`: Bitiş tarihi
- `spent_amount`: Harcanan tutar (otomatik)

**Kullanım Senaryosu:**
1. Yeni bütçe oluşturun
2. Dönem ve tutarı belirleyin
3. Sistem otomatik olarak harcamaları takip eder

---

### 4. Games (Oyunlar)

#### Tournament (Turnuvalar) - TradeSim
**Kullanım Amacı:** TradeSim turnuvalarını yönetmek

**Önemli Alanlar:**
- `name`: Turnuva adı
- `description`: Açıklama
- `start_time`: Başlangıç zamanı
- `end_time`: Bitiş zamanı
- `prize_pool`: Ödül havuzu (JSON formatında)
- `is_active`: Aktif mi?

**Ödül Havuzu JSON Formatı:**
```json
{
  "coins": 50000,
  "badge": "champion_january_2025",
  "xp": 10000,
  "title": "Ocak Şampiyonu"
}
```

**Kullanım Senaryosu:**
1. Yeni turnuva oluşturun
2. Başlangıç ve bitiş tarihlerini belirleyin
3. Ödül havuzunu JSON formatında girin
4. `is_active=True` yaparak turnuvayı aktifleştirin

#### Character (Karakterler) - TradeSim
**Kullanım Amacı:** Oyun karakterlerini yönetmek

**Önemli Alanlar:**
- `user`: Kullanıcı
- `name`: Karakter adı
- `city`: Başlangıç şehri
- `score`: Skor
- `level`: Seviye
- `skills`: Beceriler (JSON)

**İpuçları:**
- Her kullanıcı için otomatik karakter oluşturulur
- Karakter silmek kullanıcıyı etkilemez

---

### 5. AI Assistant (AI Asistan)

#### AIModel (AI Modelleri)
**Kullanım Amacı:** AI modellerini yönetmek

**Önemli Alanlar:**
- `name`: Model adı
- `model_type`: Model tipi (financial, chat, prediction)
- `version`: Versiyon
- `accuracy`: Doğruluk oranı
- `is_active`: Aktif mi?
- `parameters`: Model parametreleri (JSON)

**İpuçları:**
- Sadece aktif modeller kullanılır
- Parametreler JSON formatında saklanır

---

## 🔧 Sık Kullanılan İşlemler

### Kullanıcı Oluşturma

1. **Accounts > Custom Users** menüsüne gidin
2. **"+ Custom User Ekle"** butonuna tıklayın
3. Zorunlu alanları doldurun:
   - Username
   - Email
   - Password (veya kullanıcıya şifre sıfırlama linki gönderin)
4. Yetkileri belirleyin:
   - `is_staff=True` → Admin paneline erişim
   - `is_superuser=True` → Tüm yetkiler
5. **Kaydet** butonuna tıklayın

### Şirket Oluşturma

1. **Accounting > Companies** menüsüne gidin
2. **"+ Company Ekle"** butonuna tıklayın
3. Şirket bilgilerini girin:
   - Name (Şirket adı)
   - Tax Number (Vergi numarası - benzersiz olmalı)
   - Trade Name (Ticari unvan)
   - Sector (Sektör)
4. İletişim bilgilerini girin
5. **Kaydet** butonuna tıklayın

### Turnuva Oluşturma

1. **TradeSim > TradeSim Turnuvaları** menüsüne gidin
2. **"+ TradeSim Turnuvası Ekle"** butonuna tıklayın
3. Turnuva bilgilerini girin:
   - Name: "Ocak 2025 Büyük Turnuva"
   - Description: Açıklama
   - Start time: Başlangıç tarihi/saati
   - End time: Bitiş tarihi/saati
   - Prize pool (JSON):
     ```json
     {
       "coins": 50000,
       "badge": "champion_january_2025",
       "xp": 10000
     }
     ```
   - Is active: ✓ (işaretli)
4. **Kaydet** butonuna tıklayın

---

## 💡 İpuçları ve Püf Noktaları

### 1. Arama ve Filtreleme
- **Arama:** Üst kısımdaki arama kutusu birden fazla alanda arama yapar
- **Filtreleme:** Sağ taraftaki filtrelerle sonuçları daraltın
- **Tarih Filtreleme:** `date_hierarchy` olan modellerde üst kısımda tarih navigasyonu vardır

### 2. Toplu İşlemler
- Liste sayfasında birden fazla kayıt seçebilirsiniz
- Seçili kayıtlar için toplu işlemler yapabilirsiniz (silme, güncelleme, vb.)

### 3. Readonly Fields (Salt Okunur Alanlar)
- Bazı alanlar otomatik hesaplanır ve düzenlenemez
- Bu alanlar `readonly_fields` olarak işaretlenmiştir

### 4. Fieldsets (Alan Grupları)
- Formlar mantıksal gruplara ayrılmıştır
- `collapse` sınıfı olan gruplar varsayılan olarak kapalıdır

### 5. Foreign Key İlişkileri
- Foreign key alanlarında arama yapabilirsiniz
- "+" butonu ile yeni kayıt oluşturabilirsiniz

### 6. Many-to-Many İlişkileri
- `filter_horizontal` kullanılan alanlarda çift liste görünür
- Sol listeden sağa sürükleyerek seçim yapabilirsiniz

### 7. JSON Alanları
- JSON alanları için geçerli JSON formatı kullanın
- Hata durumunda JSON validator kullanın

### 8. Güvenlik
- **⚠️ Silme İşlemleri:** Silme işlemi geri alınamaz, dikkatli olun!
- **Yetkiler:** Kullanıcı yetkilerini dikkatli yönetin
- **Audit Logs:** Tüm değişiklikler loglanır

---

## 📞 Yardım ve Destek

### Sorun Giderme

**Admin paneline giriş yapamıyorum:**
- `is_staff=True` olduğundan emin olun
- Şifrenizi kontrol edin
- Şifre sıfırlama linki kullanın

**Bir modeli göremiyorum:**
- Model admin.py'de kayıtlı mı kontrol edin
- Yetkiniz var mı kontrol edin

**Form hatası alıyorum:**
- Zorunlu alanları doldurduğunuzdan emin olun
- Veri formatlarını kontrol edin (tarih, sayı, JSON, vb.)

### Ek Kaynaklar

- **Dokümantasyon:** `/docs/` klasöründe detaylı dokümantasyon
- **API Dokümantasyonu:** `/api/docs/` adresinde API dokümantasyonu
- **Yardım Merkezi:** `/help/` adresinde yardım içerikleri

---

## 🔄 Güncelleme Notları

**Son Güncelleme:** 2025-01-XX
**Versiyon:** 1.0

### Yapılan İyileştirmeler

1. ✅ Finance modülü admin konfigürasyonları geliştirildi
2. ✅ Accounts modülü admin konfigürasyonları geliştirildi
3. ✅ Tournament admin'e katılımcı sayısı eklendi
4. ✅ Tüm modellere fieldsets eklendi
5. ✅ Arama ve filtreleme iyileştirildi

---

**Not:** Bu kılavuz sürekli güncellenmektedir. Yeni özellikler ve değişiklikler için düzenli olarak kontrol edin.

