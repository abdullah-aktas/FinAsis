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