# FinAsis API Dokümantasyonu

## Genel Bilgiler

- **Base URL**: `http://localhost:8000/api/v1`
- **Format**: JSON
- **Kimlik Doğrulama**: JWT Token

## Kimlik Doğrulama

### Token Alma
```http
POST /auth/token/
Content-Type: application/json

{
    "username": "kullanici",
    "password": "sifre"
}
```

### Token Yenileme
```http
POST /auth/token/refresh/
Content-Type: application/json

{
    "refresh": "refresh_token"
}
```

## Müşteri Yönetimi

### Müşteri Listesi
```http
GET /customers/
Authorization: Bearer {token}
```

### Müşteri Detayı
```http
GET /customers/{id}/
Authorization: Bearer {token}
```

### Müşteri Oluşturma
```http
POST /customers/
Authorization: Bearer {token}
Content-Type: application/json

{
    "company_name": "Şirket Adı",
    "tax_number": "1234567890",
    "industry": "Bilgi Teknolojileri",
    "annual_revenue": 1000000,
    "credit_score": 750
}
```

## Fırsat Yönetimi

### Fırsat Listesi
```http
GET /opportunities/
Authorization: Bearer {token}
```

### Fırsat Oluşturma
```http
POST /opportunities/
Authorization: Bearer {token}
Content-Type: application/json

{
    "title": "Yeni Proje",
    "description": "Proje açıklaması",
    "amount": 50000,
    "probability": 75,
    "stage": "proposal",
    "customer": 1
}
```

## Aktivite Yönetimi

### Aktivite Listesi
```http
GET /activities/
Authorization: Bearer {token}
```

### Aktivite Oluşturma
```http
POST /activities/
Authorization: Bearer {token}
Content-Type: application/json

{
    "subject": "Toplantı",
    "description": "Müşteri toplantısı",
    "due_date": "2024-04-25T14:00:00Z",
    "type": "meeting",
    "customer": 1
}
```

## Raporlama

### Performans Raporu
```http
GET /reports/performance/
Authorization: Bearer {token}
```

### Finansal Rapor
```http
GET /reports/financial/
Authorization: Bearer {token}
```

## Hata Kodları

- 400: Geçersiz İstek
- 401: Yetkisiz Erişim
- 403: Yasaklı
- 404: Bulunamadı
- 500: Sunucu Hatası

## Rate Limiting

- Maksimum istek: 100/dakika
- Limit aşımı: 429 Too Many Requests

## Versiyonlama

- API versiyonu URL'de belirtilir: `/api/v1/`
- Yeni versiyonlar geriye dönük uyumludur 