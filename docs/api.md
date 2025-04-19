# FinAsis API Dokümantasyonu

Bu dokümantasyon, FinAsis uygulamasının API'lerini detaylı olarak açıklamaktadır.

## Kimlik Doğrulama

Tüm API istekleri JWT (JSON Web Token) tabanlı kimlik doğrulama gerektirir.

### Token Alma

```
POST /api/token/
```

**İstek**

```json
{
    "username": "kullanici",
    "password": "sifre123"
}
```

**Yanıt**

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Token Yenileme

```
POST /api/token/refresh/
```

**İstek**

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Yanıt**

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Fatura API'leri

### Fatura Listesi 

```
GET /api/invoices/
```

**Yetki** 

`invoice.view_invoice` yetkisi gerektirir.

**Sorgu Parametreleri**

- `start_date`: Başlangıç tarihi (YYYY-MM-DD formatında)
- `end_date`: Bitiş tarihi (YYYY-MM-DD formatında)
- `status`: Fatura durumu (DRAFT, APPROVED, PAID, CANCELED)
- `customer`: Müşteri ID'si

**Yanıt**

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "invoice_number": "INV-2023-001",
            "issue_date": "2023-05-15",
            "due_date": "2023-06-15",
            "total_amount": "1180.00",
            "status": "APPROVED",
            "customer": {
                "id": 1,
                "name": "Test Müşteri"
            },
            "created_at": "2023-05-15T10:30:00Z",
            "updated_at": "2023-05-15T10:30:00Z"
        },
        {
            "id": 2,
            "invoice_number": "INV-2023-002",
            "issue_date": "2023-05-16",
            "due_date": "2023-06-16",
            "total_amount": "2360.00",
            "status": "DRAFT",
            "customer": {
                "id": 1,
                "name": "Test Müşteri"
            },
            "created_at": "2023-05-16T09:45:00Z",
            "updated_at": "2023-05-16T09:45:00Z"
        }
    ]
}
```

### Fatura Detayı

```
GET /api/invoices/{id}/
```

**Yetki** 

`invoice.view_invoice` yetkisi gerektirir.

**Yanıt**

```json
{
    "id": 1,
    "invoice_number": "INV-2023-001",
    "issue_date": "2023-05-15",
    "due_date": "2023-06-15",
    "total_amount": "1180.00",
    "status": "APPROVED",
    "customer": {
        "id": 1,
        "name": "Test Müşteri",
        "tax_id": "1234567890",
        "address": "Test Adres"
    },
    "items": [
        {
            "id": 1,
            "description": "Test Ürün",
            "quantity": 2,
            "unit_price": "500.00",
            "tax_rate": "18.00",
            "line_total": "1000.00",
            "tax_amount": "180.00"
        }
    ],
    "created_at": "2023-05-15T10:30:00Z",
    "updated_at": "2023-05-15T10:30:00Z"
}
```

### Fatura Oluşturma

```
POST /api/invoices/
```

**Yetki** 

`invoice.add_invoice` yetkisi gerektirir.

**İstek**

```json
{
    "invoice_number": "INV-2023-003",
    "issue_date": "2023-05-17",
    "due_date": "2023-06-17",
    "customer": 1,
    "status": "DRAFT",
    "items": [
        {
            "description": "Test Ürün 1",
            "quantity": 2,
            "unit_price": "1000.00",
            "tax_rate": "18.00"
        }
    ]
}
```

**Yanıt**

```json
{
    "id": 3,
    "invoice_number": "INV-2023-003",
    "issue_date": "2023-05-17",
    "due_date": "2023-06-17",
    "total_amount": "2360.00",
    "status": "DRAFT",
    "customer": {
        "id": 1,
        "name": "Test Müşteri"
    },
    "items": [
        {
            "id": 3,
            "description": "Test Ürün 1",
            "quantity": 2,
            "unit_price": "1000.00",
            "tax_rate": "18.00",
            "line_total": "2000.00",
            "tax_amount": "360.00"
        }
    ],
    "created_at": "2023-05-17T11:15:00Z",
    "updated_at": "2023-05-17T11:15:00Z"
}
```

### Fatura Güncelleme

```
PATCH /api/invoices/{id}/
```

**Yetki** 

`invoice.change_invoice` yetkisi gerektirir.

**İstek**

```json
{
    "status": "APPROVED"
}
```

**Yanıt**

```json
{
    "id": 3,
    "invoice_number": "INV-2023-003",
    "issue_date": "2023-05-17",
    "due_date": "2023-06-17",
    "total_amount": "2360.00",
    "status": "APPROVED",
    "customer": {
        "id": 1,
        "name": "Test Müşteri"
    },
    "created_at": "2023-05-17T11:15:00Z",
    "updated_at": "2023-05-17T11:20:00Z"
}
```

## Banka Entegrasyonu API'leri

### Banka Hesapları Listesi

```
GET /api/bank-accounts/
```

**Yetki** 

`bank_integration.view_bankaccount` yetkisi gerektirir.

**Yanıt**

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Test Hesabı",
            "account_number": "TR123456789012345678901234",
            "currency": "TRY",
            "created_at": "2023-05-01T09:00:00Z",
            "updated_at": "2023-05-01T09:00:00Z"
        }
    ]
}
```

### Hesap Bakiyesi Sorgulama

```
GET /api/bank-accounts/{id}/balance/
```

**Yetki** 

`bank_integration.view_bankaccount` yetkisi gerektirir.

**Yanıt**

```json
{
    "balance": 5000,
    "currency": "TRY",
    "last_updated": "2023-05-17T12:30:00Z"
}
```

### Para Transferi

```
POST /api/bank-transfer/
```

**Yetki** 

`bank_integration.add_banktransaction` yetkisi gerektirir.

**İstek**

```json
{
    "from_account": 1,
    "to_account": "TR987654321098765432109876",
    "amount": "1000.00",
    "description": "Test Transfer"
}
```

**Yanıt**

```json
{
    "status": "success",
    "transaction_id": "12345",
    "from_account": 1,
    "to_account": "TR987654321098765432109876",
    "amount": "1000.00",
    "description": "Test Transfer",
    "timestamp": "2023-05-17T12:45:00Z"
}
```

## E-Fatura API'leri

### E-Fatura Listesi

```
GET /api/einvoices/
```

**Yetki** 

`efatura.view_einvoice` yetkisi gerektirir.

**Yanıt**

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "invoice_number": "INV-2023-001",
            "issue_date": "2023-05-15",
            "due_date": "2023-05-15",
            "total_amount": "1000.00",
            "tax_amount": "180.00",
            "customer_name": "Test Müşteri",
            "customer_tax_id": "1234567890",
            "document_id": "12345678-1234-1234-1234-123456789012",
            "status": "delivered",
            "created_at": "2023-05-15T10:30:00Z",
            "updated_at": "2023-05-15T10:30:00Z"
        }
    ]
}
```

### E-Fatura Gönderme

```
POST /api/einvoices/{id}/send/
```

**Yetki** 

`efatura.change_einvoice` yetkisi gerektirir.

**Yanıt**

```json
{
    "status": "success",
    "document_id": "12345678-1234-1234-1234-123456789012"
}
```

### E-Fatura Durumu Sorgulama

```
GET /api/einvoices/{id}/status/
```

**Yetki** 

`efatura.view_einvoice` yetkisi gerektirir.

**Yanıt**

```json
{
    "status": "delivered",
    "timestamp": "2023-06-15T14:30:00Z"
}
```

## Hata Kodları

| Kod | Açıklama |
|-----|----------|
| 400 | Bad Request - İstek parametreleri hatalı |
| 401 | Unauthorized - Kimlik doğrulama başarısız |
| 403 | Forbidden - Yetkisiz erişim |
| 404 | Not Found - Kaynak bulunamadı |
| 500 | Internal Server Error - Sunucu hatası | 