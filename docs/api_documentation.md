# FinAsis API Dokümantasyonu

FinAsis, CRM ve finans yönetim modülleri için kapsamlı bir REST API sağlar. Bu API, üçüncü taraf uygulamaların FinAsis ile entegre olmasına olanak tanır.

## Temel URL

```
https://api.finasis.com/api/v1/
```

## Kimlik Doğrulama

API, JWT (JSON Web Token) tabanlı kimlik doğrulama kullanır. 

### Token Alma

```
POST /auth/token/
```

**İstek Gövdesi:**

```json
{
  "username": "kullanici_adi",
  "password": "parola"
}
```

**Başarılı Yanıt:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Token Kullanımı

Tüm API isteklerinde, alınan token'ı `Authorization` başlığında şu şekilde kullanın:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## CRM API Endpoint'leri

### Müşteriler

#### Müşteri Listesi

```
GET /crm/customers/
```

**Parametreler:**

- `page`: Sayfa numarası (varsayılan: 1)
- `page_size`: Sayfa boyutu (varsayılan: 10)
- `search`: Arama metni (ad, vergi numarası ve e-posta üzerinde arama yapar)

**Örnek Yanıt:**

```json
{
  "count": 42,
  "next": "https://api.finasis.com/api/v1/crm/customers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Acme Ltd. Şti.",
      "email": "info@acme.com",
      "phone": "+902121234567",
      "tax_number": "1234567890",
      "tax_office": "İstanbul",
      "created_at": "2025-01-15T10:30:45Z"
    },
    // Diğer müşteriler...
  ]
}
```

#### Müşteri Detayı

```
GET /crm/customers/{id}/
```

**Örnek Yanıt:**

```json
{
  "id": 1,
  "name": "Acme Ltd. Şti.",
  "email": "info@acme.com",
  "phone": "+902121234567",
  "tax_number": "1234567890",
  "tax_office": "İstanbul",
  "address": "Levent Mah. 123 Sk. No:4, Beşiktaş/İstanbul",
  "created_at": "2025-01-15T10:30:45Z",
  "updated_at": "2025-03-20T14:22:15Z",
  "contacts": [
    {
      "id": 1,
      "name": "Mehmet Yılmaz",
      "position": "Genel Müdür",
      "email": "mehmet@acme.com",
      "phone": "+905551234567"
    }
  ],
  "opportunities": [
    {
      "id": 2,
      "name": "2025 Yazılım Hizmeti",
      "value": 25000.00,
      "status": "open"
    }
  ]
}
```

#### Yeni Müşteri Oluşturma

```
POST /crm/customers/
```

**İstek Gövdesi:**

```json
{
  "name": "Yeni Müşteri Ltd. Şti.",
  "email": "info@yenimüşteri.com",
  "phone": "+902129876543",
  "tax_number": "9876543210",
  "tax_office": "Ankara",
  "address": "Çankaya Mah. 456 Sk. No:7, Çankaya/Ankara"
}
```

### Fırsatlar

#### Fırsat Listesi

```
GET /crm/opportunities/
```

#### Fırsat Detayı

```
GET /crm/opportunities/{id}/
```

#### Yeni Fırsat Oluşturma

```
POST /crm/opportunities/
```

### Aktiviteler

#### Aktivite Listesi

```
GET /crm/activities/
```

#### Aktivite Detayı

```
GET /crm/activities/{id}/
```

#### Yeni Aktivite Oluşturma

```
POST /crm/activities/
```

## Finans API Endpoint'leri

### Satışlar

#### Satış Listesi

```
GET /finance/sales/
```

#### Satış Detayı

```
GET /finance/sales/{id}/
```

#### Yeni Satış Oluşturma

```
POST /finance/sales/
```

## Hata Kodları

- `400 Bad Request`: İstek geçersiz veya eksik parametrelerle gönderildi
- `401 Unauthorized`: Kimlik doğrulama başarısız
- `403 Forbidden`: İşlem için yetki yok
- `404 Not Found`: İstenen kaynak bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## Rate Limiting

API, dakika başına 100 istek ile sınırlıdır. Sınır aşılırsa, 429 Too Many Requests yanıtı alınır.

## Webhook'lar

Webhook'lar aracılığıyla FinAsis'deki olaylara abone olabilirsiniz. Webhook ayarları için yönetici panelini kullanın.

Desteklenen Olaylar:
- `customer.created`: Yeni müşteri oluşturuldu
- `opportunity.updated`: Fırsat güncellendi
- `sale.confirmed`: Satış onaylandı 