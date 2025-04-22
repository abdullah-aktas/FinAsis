# FinAsis API Dokümantasyonu

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

FinAsis API, tüm modüllerin işlevselliğine programatik olarak erişim sağlayan RESTful bir API'dir.

## 🔑 Kimlik Doğrulama

### API Anahtarı
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.finasis.com/v1/endpoint
```

### OAuth 2.0
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" https://api.finasis.com/v1/endpoint
```

## 📊 Endpoint'ler

### Fatura Yönetimi

#### Fatura Oluşturma
```http
POST /v1/invoices
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "customer_id": 1,
    "items": [
        {
            "name": "Ürün 1",
            "quantity": 2,
            "price": 100
        }
    ]
}
```

#### Fatura Listeleme
```http
GET /v1/invoices?status=pending&start_date=2025-01-01&end_date=2025-12-31
Authorization: Bearer YOUR_API_KEY
```

### CRM

#### Müşteri Oluşturma
```http
POST /v1/customers
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "name": "Ahmet Yılmaz",
    "email": "ahmet@example.com",
    "phone": "+905551234567"
}
```

#### Müşteri Listeleme
```http
GET /v1/customers?segment=premium&status=active
Authorization: Bearer YOUR_API_KEY
```

### Muhasebe

#### İşlem Kaydı
```http
POST /v1/transactions
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "date": "2025-04-22",
    "description": "Satış geliri",
    "entries": [
        {
            "account": "100",
            "debit": 1000
        },
        {
            "account": "400",
            "credit": 1000
        }
    ]
}
```

### Stok Yönetimi

#### Ürün Oluşturma
```http
POST /v1/products
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "name": "Laptop",
    "code": "LT001",
    "category": "Elektronik",
    "min_stock": 5
}
```

#### Stok Hareketi
```http
POST /v1/stock-movements
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "product_id": 1,
    "type": "in",
    "quantity": 10,
    "warehouse": "Merkez Depo"
}
```

### E-Belge Sistemi

#### E-Fatura Oluşturma
```http
POST /v1/e-invoices
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "customer_id": 1,
    "items": [
        {
            "name": "Ürün 1",
            "quantity": 2,
            "price": 100
        }
    ]
}
```

### Analitik

#### Dashboard Oluşturma
```http
POST /v1/dashboards
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
    "name": "Finansal Özet",
    "widgets": [
        {
            "type": "line_chart",
            "title": "Aylık Gelir",
            "data_source": "revenue_monthly"
        }
    ]
}
```

## 🔍 Hata Kodları

| Kod | Açıklama |
|-----|----------|
| 400 | Geçersiz istek |
| 401 | Yetkisiz erişim |
| 403 | Erişim engellendi |
| 404 | Kaynak bulunamadı |
| 429 | Çok fazla istek |
| 500 | Sunucu hatası |

## 📈 Rate Limiting

- Standart plan: 100 istek/dakika
- Pro plan: 1000 istek/dakika
- Enterprise plan: 10000 istek/dakika

## 🔒 Güvenlik

- Tüm istekler HTTPS üzerinden yapılmalıdır
- API anahtarları güvenli bir şekilde saklanmalıdır
- Rate limiting kurallarına uyulmalıdır
- IP kısıtlamaları dikkate alınmalıdır

## 📚 Örnek Kodlar

### Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.finasis.com/v1/invoices",
    headers=headers,
    json={
        "customer_id": 1,
        "items": [{"name": "Ürün 1", "quantity": 2, "price": 100}]
    }
)
```

### JavaScript
```javascript
const response = await fetch('https://api.finasis.com/v1/invoices', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        customer_id: 1,
        items: [{name: 'Ürün 1', quantity: 2, price: 100}]
    })
});
```

## 📞 Destek

- API Desteği: api-support@finasis.com
- Dokümantasyon: docs.finasis.com/api
- GitHub: github.com/finasis/api-examples

## Öneri Sistemi API'leri

### 1. Öneri Oluşturma

```http
POST /api/recommendations/generate/
```

**İstek Gövdesi:**
```json
{
    "context": {
        "portfolio_value": 100000,
        "risk_level": "medium",
        "investment_goals": ["retirement", "growth"]
    }
}
```

**Başarılı Yanıt:**
```json
{
    "recommendations": [
        {
            "title": "Portföy Optimizasyonu",
            "recommendations": [
                "Hisse senetleri ağırlığını %60'a çıkarın",
                "Tahvil pozisyonunu %30'a düşürün"
            ],
            "category": "portfolio",
            "priority": "high",
            "action_required": true
        }
    ],
    "market_analysis": {
        "trends": {
            "short_term": "Yükseliş trendi",
            "medium_term": "Dengeli",
            "long_term": "Pozitif"
        },
        "risk_indicators": {
            "volatility": "medium",
            "market_sentiment": "positive"
        }
    }
}
```

### 2. Bildirim Sistemi

```http
POST /api/notifications/create/
```

**İstek Gövdesi:**
```json
{
    "insight_id": "123",
    "notification_type": "recommendation",
    "priority": "high"
}
```

### 3. Performans Metrikleri

```http
GET /api/metrics/
```

**Başarılı Yanıt:**
```json
{
    "response_time": {
        "average": 1.2,
        "p95": 2.5,
        "p99": 3.8
    },
    "recommendation_quality": {
        "accuracy": 0.85,
        "relevance": 0.92,
        "actionability": 0.78
    },
    "user_engagement": {
        "daily_active_users": 1500,
        "recommendation_acceptance_rate": 0.65
    }
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

## Rate Limiting

- Maksimum istek sayısı: 60/dakika
- Maksimum içerik boyutu: 1MB
- İstek zaman aşımı: 30 saniye

## Güvenlik

- Tüm API istekleri HTTPS üzerinden yapılmalıdır
- Her istek için geçerli bir API anahtarı gereklidir
- İstek imzası doğrulaması yapılır 