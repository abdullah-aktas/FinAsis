# FinAsis E-Belge Sistemi Modülü

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

FinAsis E-Belge Sistemi, işletmelerin elektronik belge yönetimini merkezi bir platformda gerçekleştirmesini sağlayan, GİB (Gelir İdaresi Başkanlığı) standartlarına uygun bir çözümdür.

## 🎯 Özellikler

- E-Fatura ve E-Arşiv entegrasyonu
- E-İrsaliye yönetimi
- E-SMM (Serbest Meslek Makbuzu)
- E-Müstahsil Makbuzu
- E-Bilet
- E-Performans
- E-Mutabakat
- E-İade

## 🔧 Kurulum

### Gereksinimler
- Python 3.9+
- Django 4.0+
- PostgreSQL 13+
- Redis 6.0+

### Kurulum Adımları
1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements/edocument_requirements.txt
```

2. Veritabanı migrasyonlarını çalıştırın:
```bash
python manage.py migrate edocument
```

3. E-Belge servisini başlatın:
```bash
python manage.py run_edocument_service
```

## 🛠️ Yapılandırma

### Temel Ayarlar
```python
EDOCUMENT_CONFIG = {
    "gib_username": "your_username",
    "gib_password": "your_password",
    "test_mode": False,
    "default_document_type": "efatura",
    "auto_send": True
}
```

### Sertifika Ayarları
```python
CERTIFICATE_CONFIG = {
    "path": "/path/to/certificate.p12",
    "password": "cert_password",
    "type": "pkcs12",
    "validity_check": True
}
```

## 📊 Kullanım

### E-Fatura Oluşturma
```python
from finasis.edocument import EDocumentManager

manager = EDocumentManager()
invoice = manager.create_einvoice(
    customer_id=1,
    items=[
        {"name": "Ürün 1", "quantity": 2, "price": 100},
        {"name": "Ürün 2", "quantity": 1, "price": 200}
    ]
)
```

### E-İrsaliye Oluşturma
```python
dispatch = manager.create_dispatch(
    customer_id=1,
    items=[
        {"name": "Ürün 1", "quantity": 2},
        {"name": "Ürün 2", "quantity": 1}
    ],
    vehicle_info={
        "plate": "34ABC123",
        "driver": "Ahmet Yılmaz"
    }
)
```

### E-Belge Gönderme
```python
result = manager.send_document(
    document_id=1,
    document_type="efatura",
    recipient_type="individual"
)
```

## 🔍 Örnek Kullanımlar

### Toplu E-Fatura Gönderimi
```python
manager.send_bulk_einvoices(
    customer_ids=[1, 2, 3],
    period="monthly",
    template_id=1
)
```

### E-Belge Arşivleme
```python
archive = manager.archive_document(
    document_id=1,
    document_type="efatura",
    retention_period=10
)
```

## 🧪 Test

### Test Ortamı
```bash
python manage.py test edocument.tests
```

### Test Kapsamı
- E-Fatura oluşturma
- E-İrsaliye oluşturma
- GİB entegrasyonu
- Sertifika yönetimi
- API testleri

## 📈 Performans

### Ölçümler
- Belge oluşturma süresi: < 2 saniye
- Gönderim süresi: < 5 saniye
- API yanıt süresi: < 500ms
- Toplu işlem kapasitesi: 500+ belge/saat

### Optimizasyon
- Asenkron işlemler
- Önbellekleme
- Veritabanı indeksleme
- Batch işlemler

## 🔒 Güvenlik

### Veri Güvenliği
- Veri şifreleme
- Erişim kontrolü
- Denetim kayıtları
- Veri yedekleme

### Sertifika Güvenliği
- Sertifika doğrulama
- Sertifika yenileme
- Anahtar yönetimi
- SSL/TLS

## 📚 Dokümantasyon

### API Dokümantasyonu
- [API Referansı](api.md)
- [Örnek Kodlar](examples.md)
- [Hata Kodları](errors.md)

### Kullanıcı Kılavuzu
- [Başlangıç Kılavuzu](getting_started.md)
- [Gelişmiş Özellikler](advanced_features.md)
- [SSS](faq.md)

## 🤝 Katkıda Bulunma

### Geliştirme Kuralları
1. PEP 8 standartlarına uyun
2. Birim testleri yazın
3. Dokümantasyonu güncelleyin
4. Pull request açın

### Kod İnceleme Süreci
1. Kod incelemesi
2. Test sonuçları
3. Performans değerlendirmesi
4. Onay ve birleştirme

## 📞 Destek

### İletişim
- E-posta: edocument-support@finasis.com
- Slack: #edocument-support
- GitHub Issues

### SLA
- Yanıt süresi: 24 saat
- Çözüm süresi: 72 saat
- Uptime: %99.9 