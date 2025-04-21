# FinAsis API Dokümantasyonu

Bu belge, FinAsis API'sinin kullanımı hakkında detaylı bilgiler içerir.

## İçindekiler

1. [Giriş](#giriş)
2. [Kimlik Doğrulama](#kimlik-doğrulama)
3. [Kullanıcı API](#kullanıcı-api)
4. [Finans API](#finans-api)
5. [Muhasebe API](#muhasebe-api)
6. [CRM API](#crm-api)
7. [Hata Kodları](#hata-kodları)
8. [Sınırlama Politikası](#sınırlama-politikası)
9. [SSS](#sss)

## Giriş

FinAsis API, RESTful mimarisi üzerine kurulmuştur ve JSON formatında veri alışverişi yapar. API, FinAsis sistemindeki verilere programatik erişim sağlar.

### Temel URL

```
https://api.finasis.com.tr/v1/
```

### İstek Formatı

Tüm API istekleri HTTPS protokolü üzerinden yapılmalıdır. GET istekleri URL parametrelerini kullanır, POST, PUT ve DELETE istekleri JSON formatında gövde içerir.

### Yanıt Formatı

Tüm API yanıtları JSON formatındadır.

```json
{
  "status": "success",
  "data": { ... },
  "message": "İşlem başarılı"
}
```

```json
{
  "status": "error",
  "error": {
    "code": "invalid_input",
    "message": "Geçersiz giriş değerleri"
  }
}
```

## Kimlik Doğrulama

FinAsis API, JWT (JSON Web Token) tabanlı kimlik doğrulama kullanır.

### Token Alma

```
POST /auth/token/
```

#### İstek Gövdesi

```json
{
  "email": "kullanici@ornek.com",
  "password": "sifre123"
}
```

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### Token Yenileme

```
POST /auth/token/refresh/
```

#### İstek Gövdesi

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### API İsteklerinde Kimlik Doğrulama

Tüm API istekleri için Authorization başlığında token belirtilmelidir:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Kullanıcı API

### Kullanıcı Profili Alma

```
GET /users/profile/
```

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "email": "kullanici@ornek.com",
    "first_name": "Ad",
    "last_name": "Soyad",
    "phone_number": "+905551234567",
    "profile": {
      "bio": "Hakkımda bilgisi",
      "birth_date": "1990-01-01",
      "company_name": "Örnek Şirket",
      "job_title": "Yazılım Geliştirici"
    }
  }
}
```

### Kullanıcı Profili Güncelleme

```
PUT /users/profile/
```

#### İstek Gövdesi

```json
{
  "first_name": "Yeni Ad",
  "last_name": "Yeni Soyad",
  "phone_number": "+905559876543",
  "profile": {
    "bio": "Güncellenmiş hakkımda bilgisi",
    "company_name": "Yeni Şirket",
    "job_title": "Kıdemli Yazılım Geliştirici"
  }
}
```

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "email": "kullanici@ornek.com",
    "first_name": "Yeni Ad",
    "last_name": "Yeni Soyad",
    "phone_number": "+905559876543",
    "profile": {
      "bio": "Güncellenmiş hakkımda bilgisi",
      "birth_date": "1990-01-01",
      "company_name": "Yeni Şirket",
      "job_title": "Kıdemli Yazılım Geliştirici"
    }
  },
  "message": "Profil başarıyla güncellendi"
}
```

## Finans API

### Fatura Listesi

```
GET /finance/invoices/
```

#### Sorgu Parametreleri

| Parametre | Açıklama | Örnek |
|-----------|----------|-------|
| page | Sayfa numarası | 1 |
| page_size | Sayfa başına sonuç sayısı | 10 |
| type | Fatura türü (sale/purchase) | sale |
| status | Fatura durumu (draft/issued/paid/cancelled) | paid |
| start_date | Başlangıç tarihi | 2023-01-01 |
| end_date | Bitiş tarihi | 2023-12-31 |

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "count": 25,
    "next": "https://api.finasis.com.tr/v1/finance/invoices/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "number": "INV-2023-001",
        "type": "sale",
        "customer": {
          "id": 5,
          "name": "Örnek Müşteri Ltd. Şti."
        },
        "issue_date": "2023-03-15",
        "due_date": "2023-04-15",
        "total_amount": 1250.00,
        "paid_amount": 1250.00,
        "status": "paid",
        "currency": "TRY"
      },
      // ... diğer faturalar
    ]
  }
}
```

### Fatura Detayı

```
GET /finance/invoices/{id}/
```

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "number": "INV-2023-001",
    "type": "sale",
    "customer": {
      "id": 5,
      "name": "Örnek Müşteri Ltd. Şti.",
      "tax_number": "1234567890",
      "address": "Örnek Mah. Test Cad. No:123 Kadıköy/İstanbul"
    },
    "issue_date": "2023-03-15",
    "due_date": "2023-04-15",
    "items": [
      {
        "id": 1,
        "description": "Web Tasarım Hizmeti",
        "quantity": 1,
        "unit_price": 1000.00,
        "tax_rate": 18,
        "tax_amount": 180.00,
        "total": 1180.00
      },
      {
        "id": 2,
        "description": "Domain Kayıt",
        "quantity": 1,
        "unit_price": 70.00,
        "tax_rate": 0,
        "tax_amount": 0.00,
        "total": 70.00
      }
    ],
    "subtotal": 1070.00,
    "tax_total": 180.00,
    "total_amount": 1250.00,
    "paid_amount": 1250.00,
    "remaining_amount": 0.00,
    "status": "paid",
    "currency": "TRY",
    "notes": "30 gün içinde ödeme yapılmalıdır.",
    "payments": [
      {
        "id": 1,
        "date": "2023-04-10",
        "amount": 1250.00,
        "method": "bank_transfer",
        "reference": "TRF123456"
      }
    ]
  }
}
```

### Yeni Fatura Oluşturma

```
POST /finance/invoices/
```

#### İstek Gövdesi

```json
{
  "type": "sale",
  "customer_id": 5,
  "issue_date": "2023-05-20",
  "due_date": "2023-06-20",
  "items": [
    {
      "description": "SEO Hizmeti",
      "quantity": 1,
      "unit_price": 500.00,
      "tax_rate": 18
    },
    {
      "description": "İçerik Yazımı",
      "quantity": 10,
      "unit_price": 50.00,
      "tax_rate": 18
    }
  ],
  "currency": "TRY",
  "notes": "30 gün içinde ödeme yapılmalıdır."
}
```

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "id": 2,
    "number": "INV-2023-002",
    // ... fatura detayları
  },
  "message": "Fatura başarıyla oluşturuldu"
}
```

## Muhasebe API

### Hesap Planı Listeleme

```
GET /accounting/accounts/
```

#### Sorgu Parametreleri

| Parametre | Açıklama | Örnek |
|-----------|----------|-------|
| type | Hesap tipi (asset/liability/equity/income/expense) | income |
| parent_id | Üst hesap ID'si | 3 |
| search | Arama kelimesi | banka |

#### Yanıt

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "code": "100",
      "name": "Kasa",
      "type": "asset",
      "balance": 5000.00,
      "is_bank_account": false,
      "parent": null,
      "children": [
        {
          "id": 2,
          "code": "100.01",
          "name": "TL Kasa",
          "type": "asset",
          "balance": 3000.00,
          "is_bank_account": false,
          "parent": 1,
          "children": []
        },
        {
          "id": 3,
          "code": "100.02",
          "name": "USD Kasa",
          "type": "asset",
          "balance": 2000.00,
          "is_bank_account": false,
          "parent": 1,
          "children": []
        }
      ]
    }
    // ... diğer hesaplar
  ]
}
```

### Muhasebe Fişi Oluşturma

```
POST /accounting/entries/
```

#### İstek Gövdesi

```json
{
  "date": "2023-05-25",
  "type": "journal",
  "description": "Kira ödemesi",
  "reference": "ÖRN-123",
  "items": [
    {
      "account_id": 15,
      "description": "Mayıs ayı kira ödemesi",
      "debit": 1500.00,
      "credit": 0.00
    },
    {
      "account_id": 5,
      "description": "Mayıs ayı kira ödemesi",
      "debit": 0.00,
      "credit": 1500.00
    }
  ]
}
```

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "id": 5,
    "number": "MUH-2023-005",
    "date": "2023-05-25",
    "type": "journal",
    "description": "Kira ödemesi",
    "reference": "ÖRN-123",
    "items": [
      {
        "id": 9,
        "account": {
          "id": 15,
          "code": "770",
          "name": "Genel Yönetim Giderleri"
        },
        "description": "Mayıs ayı kira ödemesi",
        "debit": 1500.00,
        "credit": 0.00
      },
      {
        "id": 10,
        "account": {
          "id": 5,
          "code": "102",
          "name": "Bankalar"
        },
        "description": "Mayıs ayı kira ödemesi",
        "debit": 0.00,
        "credit": 1500.00
      }
    ],
    "total_debit": 1500.00,
    "total_credit": 1500.00,
    "status": "posted"
  },
  "message": "Muhasebe fişi başarıyla oluşturuldu"
}
```

## CRM API

### Müşteri Listesi

```
GET /crm/customers/
```

#### Sorgu Parametreleri

| Parametre | Açıklama | Örnek |
|-----------|----------|-------|
| page | Sayfa numarası | 1 |
| page_size | Sayfa başına sonuç sayısı | 10 |
| search | Arama kelimesi | örnek |
| type | Müşteri tipi (individual/corporate) | corporate |

#### Yanıt

```json
{
  "status": "success",
  "data": {
    "count": 15,
    "next": "https://api.finasis.com.tr/v1/crm/customers/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Örnek Müşteri Ltd. Şti.",
        "type": "corporate",
        "tax_number": "1234567890",
        "contact_person": "Ahmet Örnek",
        "email": "ahmet@ornek.com",
        "phone": "+905551234567",
        "address": "Örnek Mah. Test Cad. No:123 Kadıköy/İstanbul",
        "created_at": "2023-01-15T10:30:45Z"
      },
      // ... diğer müşteriler
    ]
  }
}
```

## Hata Kodları

| Kod | Açıklama |
|-----|----------|
| invalid_credentials | Geçersiz kimlik bilgileri |
| token_expired | Token süresi doldu |
| invalid_token | Geçersiz token |
| permission_denied | Yetki reddedildi |
| not_found | Kaynak bulunamadı |
| invalid_input | Geçersiz giriş değerleri |
| validation_error | Doğrulama hatası |
| server_error | Sunucu hatası |

## Sınırlama Politikası

API istekleri aşağıdaki şekilde sınırlandırılmıştır:

- Anonim kullanıcılar: Saatte 20 istek
- Kimliği doğrulanmış kullanıcılar: Günde 1000 istek
- Token alımı: Dakikada 5 istek
- Token yenileme: Saatte 20 istek

Sınırlamaya ulaşıldığında, API şu yanıtı döndürür:

```json
{
  "status": "error",
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Çok fazla istek yapıldı, lütfen daha sonra tekrar deneyin"
  }
}
```

## SSS

### API erişim anahtarını nasıl alabilirim?

FinAsis hesabınızda oturum açtıktan sonra, Ayarlar > API Erişimi bölümünden API anahtarınızı oluşturabilirsiniz.

### API'den dönen timestamp formatı nedir?

Tüm tarih ve zaman değerleri ISO 8601 formatında döner: `YYYY-MM-DDTHH:MM:SSZ`

### API hata kodunu nasıl yorumlamalıyım?

Hata kodları, sorunun kaynağını belirlemenize yardımcı olur. Örneğin, "invalid_input" hatası, gönderdiğiniz verilerin geçersiz olduğunu gösterir.

---

## Destek

API kullanımı hakkında sorularınız için lütfen api-support@finasis.com.tr adresine e-posta gönderin.

© 2023 FinAsis Yazılım A.Ş. Tüm hakları saklıdır. 