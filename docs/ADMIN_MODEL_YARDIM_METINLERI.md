# Admin Panel Model Yardım Metinleri

Bu doküman, admin panelindeki her model için alan açıklamalarını içerir.

## 📋 Kullanım

Admin panelinde her alanın yanında **"?"** işareti göründüğünde, üzerine gelerek yardım metnini görebilirsiniz.

---

## Accounts (Hesap Yönetimi)

### CustomUser (Kullanıcılar)

| Alan | Açıklama |
|------|----------|
| `username` | Kullanıcı adı. Benzersiz olmalıdır. Sadece harf, rakam ve @/./+/-/_ karakterleri kullanılabilir. |
| `email` | E-posta adresi. Benzersiz olmalıdır. Şifre sıfırlama ve bildirimler için kullanılır. |
| `is_staff` | Admin paneline erişim yetkisi. True ise kullanıcı admin paneline giriş yapabilir. |
| `is_superuser` | Tüm yetkilere sahip kullanıcı. True ise kullanıcı tüm işlemleri yapabilir. |
| `is_active` | Kullanıcı aktif mi? False yapılırsa kullanıcı giriş yapamaz. |
| `company` | Kullanıcının bağlı olduğu şirket. Şirket bilgilerine erişim için gereklidir. |
| `user_type` | Kullanıcı tipi. KOBİ Sahibi, Muhasebeci, Finans Yöneticisi vb. |

### UserRole (Kullanıcı Rolleri)

| Alan | Açıklama |
|------|----------|
| `name` | Rol adı. Örn: "Muhasebeci", "Finans Yöneticisi" |
| `hierarchy_level` | Hiyerarşi seviyesi. 0 = En yüksek yetki. Sayı arttıkça yetki azalır. |
| `permissions` | Rol yetkileri. Bu role sahip kullanıcılar bu yetkilere sahip olur. |
| `is_active` | Rol aktif mi? Pasif roller kullanıcılara atanamaz. |

### Achievement (Başarımlar)

| Alan | Açıklama |
|------|----------|
| `name` | Başarım adı. Kullanıcılara gösterilecek isim. |
| `code` | Başarım kodu. Sistem içinde kullanılacak benzersiz kod. |
| `category` | Başarım kategorisi. Oyun, Eğitim, Finans vb. |
| `points` | Başarım puanı. Kullanıcı bu başarımı kazandığında alacağı puan. |
| `is_active` | Başarım aktif mi? Pasif başarımlar kullanıcılara gösterilmez. |

---

## Accounting (Muhasebe)

### Company (Şirketler)

| Alan | Açıklama |
|------|----------|
| `name` | Şirket adı. Resmi şirket adı. |
| `tax_number` | Vergi numarası. Benzersiz olmalıdır. GİB sisteminde kullanılır. |
| `trade_name` | Ticari unvan. Ticaret sicilinde kayıtlı unvan. |
| `sector` | Sektör. Şirketin faaliyet gösterdiği sektör. |
| `address` | Şirket adresi. Fatura ve resmi belgelerde kullanılır. |

### Invoice (Faturalar)

| Alan | Açıklama |
|------|----------|
| `invoice_number` | Fatura numarası. Benzersiz olmalıdır. E-Fatura sisteminde kullanılır. |
| `invoice_date` | Fatura tarihi. Faturanın düzenlendiği tarih. |
| `customer` | Müşteri. Faturayı alan müşteri. |
| `total_amount` | Toplam tutar. KDV dahil toplam tutar. |
| `status` | Fatura durumu. Taslak, Gönderildi, Ödendi, İptal. |

---

## Finance (Finans)

### Transaction (İşlemler)

| Alan | Açıklama |
|------|----------|
| `account` | İşlemin yapıldığı hesap. Nakit, Banka, Kredi vb. |
| `amount` | İşlem tutarı. Pozitif değer. |
| `transaction_type` | İşlem tipi. Gelir, Gider, Transfer. |
| `date` | İşlem tarihi. İşlemin gerçekleştiği tarih. |
| `description` | İşlem açıklaması. İşlemin detaylı açıklaması. |

### Account (Hesaplar)

| Alan | Açıklama |
|------|----------|
| `name` | Hesap adı. Örn: "Ana Kasa", "İş Bankası TL Hesabı" |
| `account_type` | Hesap tipi. Nakit, Banka, Kredi, Yatırım vb. |
| `balance` | Hesap bakiyesi. Otomatik hesaplanır, manuel değiştirmeyin. |
| `currency` | Para birimi. TRY, USD, EUR vb. |
| `is_active` | Hesap aktif mi? Pasif hesaplar işlemlerde görünmez. |

### Budget (Bütçeler)

| Alan | Açıklama |
|------|----------|
| `name` | Bütçe adı. Örn: "2025 Pazarlama Bütçesi" |
| `amount` | Bütçe tutarı. Toplam bütçe miktarı. |
| `period` | Bütçe dönemi. Aylık, Yıllık, Özel. |
| `start_date` | Bütçe başlangıç tarihi. |
| `end_date` | Bütçe bitiş tarihi. |
| `spent_amount` | Harcanan tutar. Otomatik hesaplanır. |

---

## Games - TradeSim

### Tournament (Turnuvalar)

| Alan | Açıklama |
|------|----------|
| `name` | Turnuva adı. Kullanıcılara gösterilecek isim. |
| `description` | Turnuva açıklaması. Kurallar ve ödüller hakkında bilgi. |
| `start_time` | Turnuva başlangıç zamanı. Tarih ve saat. |
| `end_time` | Turnuva bitiş zamanı. Tarih ve saat. |
| `prize_pool` | Ödül havuzu. JSON formatında. Örn: `{"coins": 50000, "badge": "champion"}` |
| `is_active` | Turnuva aktif mi? Pasif turnuvalar görünmez. |

**Prize Pool JSON Örneği:**
```json
{
  "coins": 50000,
  "badge": "champion_january_2025",
  "xp": 10000,
  "title": "Ocak Şampiyonu"
}
```

### Character (Karakterler)

| Alan | Açıklama |
|------|----------|
| `user` | Karakterin sahibi olan kullanıcı. |
| `name` | Karakter adı. Oyunda görünecek isim. |
| `city` | Karakterin bulunduğu şehir. Başlangıç şehri. |
| `score` | Karakter skoru. Ticaret işlemlerinden kazanılan puan. |
| `level` | Karakter seviyesi. XP biriktikçe artar. |
| `skills` | Karakter becerileri. JSON formatında. Örn: `{"ticaret": 5, "pazarlık": 3}` |

### City (Şehirler)

| Alan | Açıklama |
|------|----------|
| `name` | Şehir adı. Örn: "İstanbul", "Ankara" |
| `market_size` | Pazar büyüklüğü. Şehrin ticaret potansiyeli. |
| `sectors` | Şehir sektörleri. JSON formatında. Örn: `["gıda", "tekstil", "teknoloji"]` |
| `neighbors` | Komşu şehirler. Ticaret rotaları için. |

### Product (Ürünler)

| Alan | Açıklama |
|------|----------|
| `name` | Ürün adı. Örn: "Buğday", "Pamuk" |
| `category` | Ürün kategorisi. tarım, gıda, tekstil vb. |
| `base_price` | Temel fiyat. Ürünün standart fiyatı. |
| `unit` | Birim. kg, adet, litre vb. |

---

## AI Assistant

### AIModel (AI Modelleri)

| Alan | Açıklama |
|------|----------|
| `name` | Model adı. Örn: "RiskScoringModel", "ChatAssistantModel" |
| `model_type` | Model tipi. financial, chat, prediction. |
| `version` | Model versiyonu. Örn: "v1.0", "20250115" |
| `accuracy` | Model doğruluk oranı. 0.0 - 1.0 arası. |
| `is_active` | Model aktif mi? Sadece aktif modeller kullanılır. |
| `parameters` | Model parametreleri. JSON formatında. |

---

## 📝 Notlar

- **JSON Alanları:** JSON formatında veri girerken geçerli JSON syntax kullanın
- **Benzersiz Alanlar:** Vergi numarası, e-posta gibi alanlar benzersiz olmalıdır
- **Otomatik Hesaplanan Alanlar:** Bakiye, harcanan tutar gibi alanlar otomatik hesaplanır, manuel değiştirmeyin
- **Tarih Alanları:** Tarih formatı: YYYY-MM-DD veya YYYY-MM-DD HH:MM:SS

---

**Son Güncelleme:** 2025-01-XX

