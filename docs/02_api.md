# API Dokümantasyonu

Bu dokümantasyon, FinAsis projesinin API endpoint'lerini ve kullanımını detaylandırmaktadır.

## İçindekiler

1. [Genel Bilgiler](#genel-bilgiler)
2. [Kimlik Doğrulama](#kimlik-doğrulama)
3. [Endpoint'ler](#endpointler)
4. [Hata Kodları](#hata-kodları)
5. [Örnek İstekler](#örnek-istekler)
6. [Rate Limiting](#rate-limiting)
7. [Webhook'lar](#webhooklar)

## Genel Bilgiler

### Base URL

```
Geliştirme: http://localhost:8000/api/v1
Üretim: https://api.finasis.com/v1
```

### İstek Formatı

Tüm API istekleri JSON formatında yapılmalıdır:

```http
Content-Type: application/json
```

### Yanıt Formatı

Tüm API yanıtları aşağıdaki formatta döner:

```json
{
    "status": "success",
    "data": {
        // Yanıt verileri
    },
    "message": "İşlem başarılı"
}
```

## Kimlik Doğrulama

### JWT Token

API istekleri için JWT token kullanılmaktadır. Token'ı almak için:

```http
POST /auth/token/
Content-Type: application/json

{
    "username": "kullanici_adi",
    "password": "sifre"
}
```

### Token Kullanımı

Token'ı isteklerde kullanmak için:

```http
Authorization: Bearer <token>
```

## Endpoint'ler

### Kullanıcı İşlemleri

#### Kullanıcı Kaydı

```http
POST /users/register/
Content-Type: application/json

{
    "username": "yeni_kullanici",
    "email": "kullanici@ornek.com",
    "password": "guclu_sifre",
    "first_name": "Ad",
    "last_name": "Soyad"
}
```

#### Kullanıcı Profili

```http
GET /users/profile/
Authorization: Bearer <token>
```

### Finans İşlemleri

#### Nakit Akışı

```http
GET /finance/cash-flow/
Authorization: Bearer <token>

# Filtreleme parametreleri
?start_date=2024-01-01
&end_date=2024-12-31
&type=income
```

#### Bütçe Yönetimi

```http
POST /finance/budget/
Authorization: Bearer <token>
Content-Type: application/json

{
    "category": "gelir",
    "amount": 10000.00,
    "period": "2024-01",
    "description": "Ocak ayı bütçesi"
}
```

### Muhasebe İşlemleri

#### Hesap Planı

```http
GET /accounting/accounts/
Authorization: Bearer <token>
```

#### Fatura İşlemleri

```http
POST /accounting/invoices/
Authorization: Bearer <token>
Content-Type: application/json

{
    "invoice_number": "FT2024001",
    "date": "2024-01-15",
    "due_date": "2024-02-15",
    "amount": 1500.00,
    "currency": "TRY",
    "items": [
        {
            "description": "Ürün A",
            "quantity": 2,
            "unit_price": 750.00
        }
    ]
}
```

### E-Belge İşlemleri

#### E-Fatura

```http
POST /e-documents/e-invoice/
Authorization: Bearer <token>
Content-Type: application/json

{
    "invoice_type": "SATIS",
    "invoice_number": "EF2024001",
    "date": "2024-01-15",
    "total_amount": 1500.00,
    "currency": "TRY",
    "items": [
        {
            "name": "Ürün A",
            "quantity": 2,
            "unit_price": 750.00,
            "vat_rate": 18
        }
    ]
}
```

#### E-İrsaliye

```http
POST /e-documents/e-dispatch/
Authorization: Bearer <token>
Content-Type: application/json

{
    "dispatch_type": "SATIS",
    "dispatch_number": "EIR2024001",
    "date": "2024-01-15",
    "items": [
        {
            "name": "Ürün A",
            "quantity": 2,
            "unit": "ADET"
        }
    ]
}
```

### Raporlama

#### Finansal Raporlar

```http
GET /reports/financial/
Authorization: Bearer <token>

# Filtreleme parametreleri
?report_type=balance_sheet
&start_date=2024-01-01
&end_date=2024-12-31
&format=pdf
```

#### Analitik Raporlar

```http
GET /reports/analytics/
Authorization: Bearer <token>

# Filtreleme parametreleri
?metric=cash_flow
&period=monthly
&start_date=2024-01-01
&end_date=2024-12-31
```

## Hata Kodları

| Kod  | Açıklama                    |
|------|----------------------------|
| 400  | Geçersiz İstek            |
| 401  | Yetkisiz Erişim           |
| 403  | Erişim Reddedildi          |
| 404  | Bulunamadı                 |
| 429  | Çok Fazla İstek            |
| 500  | Sunucu Hatası              |

## Örnek İstekler

### Python

```python
import requests

# Token alma
response = requests.post(
    'http://localhost:8000/api/v1/auth/token/',
    json={
        'username': 'kullanici',
        'password': 'sifre'
    }
)
token = response.json()['access']

# Nakit akışı sorgulama
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:8000/api/v1/finance/cash-flow/',
    headers=headers,
    params={
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }
)
print(response.json())
```

### JavaScript

```javascript
// Token alma
fetch('http://localhost:8000/api/v1/auth/token/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'kullanici',
        password: 'sifre'
    })
})
.then(response => response.json())
.then(data => {
    const token = data.access;
    
    // Nakit akışı sorgulama
    return fetch('http://localhost:8000/api/v1/finance/cash-flow/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
})
.then(response => response.json())
.then(data => console.log(data));
```

## Rate Limiting

API istekleri için rate limiting uygulanmaktadır:

- Anonim istekler: 100 istek/saat
- Kimlik doğrulamalı istekler: 1000 istek/saat
- Premium kullanıcılar: 5000 istek/saat

Rate limit aşıldığında 429 HTTP kodu döner.

## Webhook'lar

### Webhook Kaydı

```http
POST /webhooks/
Authorization: Bearer <token>
Content-Type: application/json

{
    "url": "https://example.com/webhook",
    "events": ["invoice.created", "payment.received"],
    "secret": "webhook_gizli_anahtar"
}
```

### Webhook İstekleri

Webhook istekleri aşağıdaki formatta gönderilir:

```json
{
    "event": "invoice.created",
    "data": {
        "invoice_id": "123",
        "invoice_number": "FT2024001",
        "amount": 1500.00
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Webhook Güvenliği

Webhook istekleri imzalanır ve doğrulanabilir:

```http
X-Webhook-Signature: t=1234567890,v1=abc123...
``` 