# FinAsis API Dokümantasyonu

## İçindekiler
- [Genel Bilgiler](#genel-bilgiler)
- [Kimlik Doğrulama](#kimlik-doğrulama)
- [İşlemler API](#işlemler-api)
- [Bütçeler API](#bütçeler-api)
- [Kategoriler API](#kategoriler-api)
- [Kullanıcı API](#kullanıcı-api)
- [Senkronizasyon API](#senkronizasyon-api)
- [Hata Kodları](#hata-kodları)

## Genel Bilgiler

### API Endpoint
```
https://api.finasis.com/v1
```

### İstek Formatı
Tüm API istekleri JSON formatında gönderilmelidir.

### Yanıt Formatı
Tüm API yanıtları aşağıdaki formatta döner:

```json
{
  "success": true,
  "data": { ... },
  "message": "İşlem başarılı",
  "timestamp": "2023-06-15T14:30:00Z"
}
```

### Hata Yanıtı
Hata durumunda yanıt formatı:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Hata mesajı",
    "details": { ... }
  },
  "timestamp": "2023-06-15T14:30:00Z"
}
```

## Kimlik Doğrulama

### Giriş Yapma
```
POST /auth/login
```

**İstek Gövdesi:**
```json
{
  "email": "kullanici@ornek.com",
  "password": "sifre123"
}
```

**Başarılı Yanıt:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user123",
      "email": "kullanici@ornek.com",
      "name": "Kullanıcı Adı"
    }
  },
  "message": "Giriş başarılı",
  "timestamp": "2023-06-15T14:30:00Z"
}
```

### Token Yenileme
```
POST /auth/refresh
```

**İstek Gövdesi:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## İşlemler API

### İşlem Listesi
```
GET /transactions
```

**Sorgu Parametreleri:**
- `page`: Sayfa numarası (varsayılan: 1)
- `limit`: Sayfa başına öğe sayısı (varsayılan: 20)
- `start_date`: Başlangıç tarihi (YYYY-MM-DD)
- `end_date`: Bitiş tarihi (YYYY-MM-DD)
- `category`: Kategori ID
- `type`: İşlem tipi (income, expense)

**Başarılı Yanıt:**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "trans123",
        "type": "expense",
        "amount": 150.50,
        "description": "Market alışverişi",
        "category": "category123",
        "date": "2023-06-15",
        "created_at": "2023-06-15T14:30:00Z",
        "updated_at": "2023-06-15T14:30:00Z"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "limit": 20,
      "pages": 5
    }
  },
  "message": "İşlemler başarıyla getirildi",
  "timestamp": "2023-06-15T14:30:00Z"
}
```

### İşlem Detayı
```
GET /transactions/{id}
```

**Başarılı Yanıt:**
```json
{
  "success": true,
  "data": {
    "id": "trans123",
    "type": "expense",
    "amount": 150.50,
    "description": "Market alışverişi",
    "category": "category123",
    "date": "2023-06-15",
    "created_at": "2023-06-15T14:30:00Z",
    "updated_at": "2023-06-15T14:30:00Z",
    "metadata": {
      "receipt_url": "https://storage.finasis.com/receipts/trans123.jpg",
      "tags": ["market", "gıda"]
    }
  },
  "message": "İşlem detayı başarıyla getirildi",
  "timestamp": "2023-06-15T14:30:00Z"
}
```

### İşlem Oluşturma
```
POST /transactions
```

**İstek Gövdesi:**
```json
{
  "type": "expense",
  "amount": 150.50,
  "description": "Market alışverişi",
  "category": "category123",
  "date": "2023-06-15",
  "metadata": {
    "receipt_url": "https://storage.finasis.com/receipts/trans123.jpg",
    "tags": ["market", "gıda"]
  }
}
```

### İşlem Güncelleme
```
PUT /transactions/{id}
```

**İstek Gövdesi:**
```json
{
  "amount": 175.25,
  "description": "Haftalık market alışverişi",
  "category": "category123",
  "metadata": {
    "tags": ["market", "gıda", "haftalık"]
  }
}
```

### İşlem Silme
```
DELETE /transactions/{id}
```

## Bütçeler API

### Bütçe Listesi
```
GET /budgets
```

**Sorgu Parametreleri:**
- `year`: Yıl
- `month`: Ay (1-12)

**Başarılı Yanıt:**
```json
{
  "success": true,
  "data": {
    "budgets": [
      {
        "id": "budget123",
        "month": "06",
        "year": 2023,
        "amount": 5000.00,
        "spent": 3250.75,
        "created_at": "2023-06-01T00:00:00Z",
        "updated_at": "2023-06-15T14:30:00Z"
      }
    ]
  },
  "message": "Bütçeler başarıyla getirildi",
  "timestamp": "2023-06-15T14:30:00Z"
}
```

### Bütçe Oluşturma
```
POST /budgets
```

**İstek Gövdesi:**
```json
{
  "month": "06",
  "year": 2023,
  "amount": 5000.00
}
```

### Bütçe Güncelleme
```
PUT /budgets/{id}
```

**İstek Gövdesi:**
```json
{
  "amount": 5500.00
}
```

## Kategoriler API

### Kategori Listesi
```
GET /categories
```

**Başarılı Yanıt:**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": "category123",
        "name": "Market",
        "type": "expense",
        "color": "#FF5733",
        "icon": "shopping-cart"
      }
    ]
  },
  "message": "Kategoriler başarıyla getirildi",
  "timestamp": "2023-06-15T14:30:00Z"
}
```

### Kategori Oluşturma
```
POST /categories
```

**İstek Gövdesi:**
```json
{
  "name": "Market",
  "type": "expense",
  "color": "#FF5733",
  "icon": "shopping-cart"
}
```

## Kullanıcı API

### Kullanıcı Profili
```
GET /users/profile
```

**Başarılı Yanıt:**
```json
{
  "success": true,
  "data": {
    "id": "user123",
    "email": "kullanici@ornek.com",
    "name": "Kullanıcı Adı",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-06-15T14:30:00Z",
    "preferences": {
      "currency": "TRY",
      "language": "tr",
      "theme": "light"
    }
  },
  "message": "Kullanıcı profili başarıyla getirildi",
  "timestamp": "2023-06-15T14:30:00Z"
}
```

### Kullanıcı Tercihlerini Güncelleme
```
PUT /users/preferences
```

**İstek Gövdesi:**
```json
{
  "currency": "USD",
  "language": "en",
  "theme": "dark"
}
```

## Senkronizasyon API

### Senkronizasyon Durumu
```
GET /sync/status
```

**Başarılı Yanıt:**
```json
{
  "success": true,
  "data": {
    "last_sync": "2023-06-15T14:30:00Z",
    "pending_items": {
      "transactions": 5,
      "budgets": 1,
      "categories": 0
    }
  },
  "message": "Senkronizasyon durumu başarıyla getirildi",
  "timestamp": "2023-06-15T14:30:00Z"
}
```

### Senkronizasyon Başlatma
```
POST /sync/start
```

**İstek Gövdesi:**
```json
{
  "items": ["transactions", "budgets", "categories"]
}
```

## Hata Kodları

| Kod | Açıklama |
|-----|----------|
| `AUTH_REQUIRED` | Kimlik doğrulama gerekli |
| `INVALID_CREDENTIALS` | Geçersiz kimlik bilgileri |
| `TOKEN_EXPIRED` | Token süresi dolmuş |
| `INVALID_TOKEN` | Geçersiz token |
| `RESOURCE_NOT_FOUND` | Kaynak bulunamadı |
| `VALIDATION_ERROR` | Doğrulama hatası |
| `SERVER_ERROR` | Sunucu hatası |
| `RATE_LIMIT_EXCEEDED` | İstek limiti aşıldı | 