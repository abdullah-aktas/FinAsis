# FinAsis API Dokümantasyonu

## Genel Bilgiler

- Base URL: `https://api.finasis.com/v1`
- Tüm istekler JSON formatında yapılmalıdır
- Kimlik doğrulama için JWT token kullanılmaktadır

## Kimlik Doğrulama

### Token Alma

```http
POST /auth/token/
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

### Token Yenileme

```http
POST /auth/token/refresh/
Content-Type: application/json

{
    "refresh": "string"
}
```

## Muhasebe API'leri

### Faturalar

#### Fatura Listesi

```http
GET /accounting/invoices/
Authorization: Bearer {token}
```

#### Fatura Detayı

```http
GET /accounting/invoices/{id}/
Authorization: Bearer {token}
```

## CRM API'leri

### Müşteriler

#### Müşteri Listesi

```http
GET /crm/customers/
Authorization: Bearer {token}
```

#### Müşteri Detayı

```http
GET /crm/customers/{id}/
Authorization: Bearer {token}
```

## Hata Kodları

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

- Her IP için dakikada 100 istek
- Her kullanıcı için dakikada 1000 istek 