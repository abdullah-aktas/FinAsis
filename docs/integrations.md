# FinAsis Entegrasyon Sistemi Dokümantasyonu

## İçindekiler
1. [Genel Bakış](#genel-bakış)
2. [Entegrasyon Tipleri](#entegrasyon-tipleri)
3. [Kurulum](#kurulum)
4. [API Referansı](#api-referansı)
5. [Webhook Yapılandırması](#webhook-yapılandırması)
6. [Hata Yönetimi](#hata-yönetimi)
7. [Güvenlik](#güvenlik)
8. [Sık Sorulan Sorular](#sık-sorulan-sorular)

## Genel Bakış

FinAsis Entegrasyon Sistemi, e-ticaret platformları, ödeme sistemleri ve ERP sistemleri ile entegrasyon sağlayan kapsamlı bir çözümdür. Sistem, aşağıdaki temel özellikleri sunar:

- E-ticaret platformları ile ürün ve sipariş senkronizasyonu
- Ödeme sistemleri entegrasyonu
- ERP sistemleri ile muhasebe entegrasyonu
- Webhook desteği
- Otomatik senkronizasyon
- Detaylı loglama ve raporlama

## Entegrasyon Tipleri

### E-Ticaret Entegrasyonları

#### Hepsiburada
- Ürün senkronizasyonu
- Sipariş yönetimi
- Stok takibi
- Webhook desteği

#### Shopify
- Ürün senkronizasyonu
- Sipariş yönetimi
- Müşteri verileri
- Webhook desteği

### Ödeme Sistemleri

#### İyzico
- 3D Secure ödeme
- Taksitli ödeme
- İade işlemleri
- Webhook desteği

### ERP Sistemleri

#### Luca
- e-Fatura entegrasyonu
- Fiş oluşturma
- Cari hesap senkronizasyonu
- Ürün senkronizasyonu

## Kurulum

1. Gerekli paketlerin yüklenmesi:
```bash
pip install -r requirements.txt
```

2. Veritabanı migrasyonlarının yapılması:
```bash
python manage.py migrate
```

3. Entegrasyon ayarlarının yapılandırılması:
- Django admin panelinden veya API üzerinden entegrasyon ayarlarını yapılandırın
- Her entegrasyon için gerekli API anahtarlarını ve erişim bilgilerini girin

4. Celery worker ve beat servislerinin başlatılması:
```bash
celery -A finasis worker -l info
celery -A finasis beat -l info
```

## API Referansı

### Entegrasyon Yönetimi

#### Konfigürasyon Kaydetme
```http
POST /api/integrations/{integration_type}/config
Content-Type: application/json

{
    "is_active": true,
    "api_key": "your_api_key",
    "access_token": "your_access_token"
}
```

#### Senkronizasyon Başlatma
```http
POST /api/integrations/{integration_id}/sync
```

#### Log Görüntüleme
```http
GET /api/integrations/{integration_id}/logs
```

### Webhook Endpointleri

#### Hepsiburada Webhook
```http
POST /api/integrations/webhook/hepsiburada
```

#### Shopify Webhook
```http
POST /api/integrations/webhook/shopify
```

#### İyzico Webhook
```http
POST /api/integrations/webhook/iyzico
```

## Webhook Yapılandırması

### Hepsiburada Webhook
1. Hepsiburada mağaza panelinden webhook URL'sini yapılandırın:
```
https://your-domain.com/api/integrations/webhook/hepsiburada
```

2. Desteklenen olaylar:
- ORDER_STATUS_CHANGED
- PRODUCT_UPDATED

### Shopify Webhook
1. Shopify admin panelinden webhook URL'sini yapılandırın:
```
https://your-domain.com/api/integrations/webhook/shopify
```

2. Desteklenen olaylar:
- orders/create
- products/update

### İyzico Webhook
1. İyzico panelinden webhook URL'sini yapılandırın:
```
https://your-domain.com/api/integrations/webhook/iyzico
```

2. Desteklenen olaylar:
- payment.success
- payment.failed

## Hata Yönetimi

### Hata Kodları
- 400: Geçersiz istek
- 401: Kimlik doğrulama hatası
- 403: Yetkisiz erişim
- 404: Kaynak bulunamadı
- 500: Sunucu hatası

### Hata Logları
- Tüm hatalar `SyncLog` ve `WebhookLog` tablolarında saklanır
- Loglar 30 gün boyunca tutulur
- Kritik hatalar e-posta ile bildirilir

## Güvenlik

### API Anahtarları
- API anahtarları güvenli bir şekilde şifrelenerek saklanır
- Anahtarlar düzenli olarak rotasyona tabi tutulur
- Erişim logları tutulur

### Webhook Güvenliği
- Webhook istekleri imza doğrulaması ile kontrol edilir
- IP kısıtlaması uygulanır
- Rate limiting aktif

## Sık Sorulan Sorular

### Senkronizasyon sıklığı nasıl ayarlanır?
Her entegrasyon için senkronizasyon sıklığı ayrı ayrı ayarlanabilir. Varsayılan değerler:
- Hepsiburada: 15 dakika
- Shopify: 5 dakika
- ERP sistemleri: 30 dakika

### Webhook'lar nasıl test edilir?
Her entegrasyon için test webhook'ları gönderilebilir. Test butonları entegrasyon yönetim panelinde bulunur.

### Hata durumunda ne yapılmalı?
1. Log kayıtlarını kontrol edin
2. Entegrasyon durumunu kontrol edin
3. Gerekirse entegrasyonu yeniden başlatın
4. Sorun devam ederse destek ekibiyle iletişime geçin 