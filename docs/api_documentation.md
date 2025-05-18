# FinAsis API Dokümantasyonu

## İçindekiler

1. [Giriş](#giriş)
2. [Kimlik Doğrulama](#kimlik-doğrulama)
3. [API Endpoint'leri](#api-endpointleri)
4. [Hata Kodları](#hata-kodları)
5. [Örnek Kullanımlar](#örnek-kullanımlar)
6. [Rate Limiting](#rate-limiting)
7. [Güvenlik](#güvenlik)

## Giriş

FinAsis API'si, sistemin işlevselliğine programatik olarak erişim sağlar. RESTful mimarisi kullanılarak geliştirilmiştir ve JSON formatında veri alışverişi yapar.

### Temel Bilgiler

- **Base URL**: `https://api.finasis.com/v1`
- **Format**: JSON
- **Karakter Seti**: UTF-8
- **SSL**: Tüm istekler HTTPS üzerinden yapılmalıdır

## Kimlik Doğrulama

### API Anahtarı

API'ye erişim için bir API anahtarı gereklidir. Anahtar, yönetim panelinden oluşturulabilir.

```http
Authorization: Bearer {api_key}
```

### JWT Token

Bazı endpoint'ler için JWT token kullanılır:

```http
Authorization: Bearer {jwt_token}
```

## API Endpoint'leri

### Kullanıcı İşlemleri

#### Kullanıcı Girişi

```http
POST /auth/login
```

**Request Body:**
```json
{
    "email": "kullanici@example.com",
    "password": "sifre123"
}
```

**Response:**
```json
{
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "email": "kullanici@example.com",
        "name": "Kullanıcı Adı"
    }
}
```

#### Kullanıcı Bilgileri

```http
GET /users/{user_id}
```

**Response:**
```json
{
    "id": 1,
    "email": "kullanici@example.com",
    "name": "Kullanıcı Adı",
    "company": "Şirket Adı",
    "role": "admin"
}
```

### Finansal İşlemler

#### Fatura Oluşturma

```http
POST /invoices
```

**Request Body:**
```json
{
    "customer_id": 123,
    "items": [
        {
            "description": "Ürün Açıklaması",
            "quantity": 2,
            "unit_price": 100.00,
            "tax_rate": 18
        }
    ],
    "due_date": "2024-12-31"
}
```

**Response:**
```json
{
    "id": 456,
    "invoice_number": "INV-2024-001",
    "total_amount": 236.00,
    "status": "pending"
}
```

#### Ödeme İşlemi

```http
POST /payments
```

**Request Body:**
```json
{
    "invoice_id": 456,
    "amount": 236.00,
    "payment_method": "credit_card",
    "payment_date": "2024-01-15"
}
```

**Response:**
```json
{
    "id": 789,
    "status": "completed",
    "transaction_id": "TRX-2024-001"
}
```

### Müşteri İşlemleri

#### Müşteri Listesi

```http
GET /customers
```

**Query Parameters:**
- `page`: Sayfa numarası
- `limit`: Sayfa başına kayıt sayısı
- `search`: Arama terimi

**Response:**
```json
{
    "data": [
        {
            "id": 123,
            "name": "Müşteri Adı",
            "email": "musteri@example.com",
            "phone": "5551234567"
        }
    ],
    "total": 100,
    "page": 1,
    "limit": 10
}
```

#### Müşteri Detayları

```http
GET /customers/{customer_id}
```

**Response:**
```json
{
    "id": 123,
    "name": "Müşteri Adı",
    "email": "musteri@example.com",
    "phone": "5551234567",
    "address": "Adres Bilgisi",
    "tax_number": "1234567890"
}
```

## Hata Kodları

| Kod | Açıklama |
|-----|----------|
| 400 | Geçersiz istek |
| 401 | Yetkisiz erişim |
| 403 | Erişim engellendi |
| 404 | Kaynak bulunamadı |
| 429 | Çok fazla istek |
| 500 | Sunucu hatası |

### Hata Örneği

```json
{
    "error": {
        "code": 400,
        "message": "Geçersiz istek parametreleri",
        "details": {
            "field": "email",
            "message": "Geçerli bir e-posta adresi giriniz"
        }
    }
}
```

## Örnek Kullanımlar

### Python Örneği

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "https://api.finasis.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Fatura oluşturma
def create_invoice(customer_id, items):
    url = f"{BASE_URL}/invoices"
    data = {
        "customer_id": customer_id,
        "items": items
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Müşteri listesi
def get_customers(page=1, limit=10):
    url = f"{BASE_URL}/customers"
    params = {
        "page": page,
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

### JavaScript Örneği

```javascript
const API_KEY = 'your_api_key';
const BASE_URL = 'https://api.finasis.com/v1';

const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
};

// Fatura oluşturma
async function createInvoice(customerId, items) {
    const response = await fetch(`${BASE_URL}/invoices`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
            customer_id: customerId,
            items
        })
    });
    return await response.json();
}

// Müşteri listesi
async function getCustomers(page = 1, limit = 10) {
    const response = await fetch(`${BASE_URL}/customers?page=${page}&limit=${limit}`, {
        headers
    });
    return await response.json();
}
```

## Rate Limiting

API kullanımı için rate limiting uygulanmaktadır:

- Standart plan: 100 istek/dakika
- Pro plan: 1000 istek/dakika
- Enterprise plan: 10000 istek/dakika

Rate limit aşıldığında 429 hata kodu döner.

## Güvenlik

### Önerilen Güvenlik Önlemleri

1. API anahtarını güvenli bir şekilde saklayın
2. HTTPS kullanın
3. İstekleri imzalayın
4. Rate limiting uygulayın
5. Hata mesajlarını loglayın

### Güvenlik Başlıkları

```http
X-API-Key: {api_key}
X-Request-ID: {unique_id}
X-Timestamp: {timestamp}
X-Signature: {signature}
```

### İstek İmzalama

1. İstek parametrelerini sıralayın
2. Parametreleri birleştirin
3. API anahtarı ile HMAC-SHA256 imzalayın
4. İmzayı X-Signature başlığına ekleyin 