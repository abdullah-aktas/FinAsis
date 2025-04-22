# FinAsis Stok Yönetimi Modülü

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

FinAsis Stok Yönetimi modülü, işletmelerin stok hareketlerini takip etmek, stok seviyelerini yönetmek ve stok optimizasyonu yapmak için tasarlanmış kapsamlı bir çözümdür.

## 🎯 Özellikler

- Stok takibi ve kontrolü
- Depo yönetimi
- Ürün kategorizasyonu
- Barkod entegrasyonu
- Stok hareket raporları
- Minimum stok uyarıları
- Toplu stok girişi
- Stok sayımı

## 🔧 Kurulum

### Gereksinimler
- Python 3.9+
- Django 4.0+
- PostgreSQL 13+
- Redis 6.0+

### Kurulum Adımları
1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements/stock_requirements.txt
```

2. Veritabanı migrasyonlarını çalıştırın:
```bash
python manage.py migrate stock
```

3. Stok servisini başlatın:
```bash
python manage.py run_stock_service
```

## 🛠️ Yapılandırma

### Temel Ayarlar
```python
STOCK_CONFIG = {
    "default_warehouse": "Merkez Depo",
    "auto_stock_alert": True,
    "min_stock_level": 10,
    "barcode_prefix": "STK",
    "default_unit": "adet"
}
```

### Barkod Ayarları
```python
BARCODE_CONFIG = {
    "enabled": True,
    "type": "code128",
    "width": 2,
    "height": 100,
    "format": "PNG"
}
```

## 📊 Kullanım

### Ürün Yönetimi
```python
from finasis.stock import StockManager

manager = StockManager()
product = manager.create_product(
    name="Laptop",
    code="LT001",
    category="Elektronik",
    unit="adet",
    min_stock=5
)
```

### Stok Hareketi
```python
movement = manager.create_movement(
    product_id=1,
    type="in",
    quantity=10,
    warehouse="Merkez Depo",
    reference="Sipariş #123"
)
```

### Stok Sayımı
```python
inventory = manager.create_inventory(
    warehouse="Merkez Depo",
    products=[
        {"product_id": 1, "counted": 50},
        {"product_id": 2, "counted": 100}
    ]
)
```

## 🔍 Örnek Kullanımlar

### Toplu Stok Girişi
```python
manager.bulk_stock_in(
    warehouse="Merkez Depo",
    items=[
        {"product_id": 1, "quantity": 100},
        {"product_id": 2, "quantity": 200}
    ]
)
```

### Stok Transferi
```python
transfer = manager.transfer_stock(
    product_id=1,
    from_warehouse="Merkez Depo",
    to_warehouse="Şube Depo",
    quantity=50
)
```

## 🧪 Test

### Test Ortamı
```bash
python manage.py test stock.tests
```

### Test Kapsamı
- Ürün yönetimi
- Stok hareketleri
- Depo yönetimi
- Barkod sistemi
- API testleri

## 📈 Performans

### Ölçümler
- Stok hareketi süresi: < 1 saniye
- Rapor oluşturma süresi: < 3 saniye
- API yanıt süresi: < 500ms
- Toplu işlem kapasitesi: 1000+ kayıt/saat

### Optimizasyon
- Veritabanı indeksleme
- Önbellekleme
- Asenkron işlemler
- Veri sıkıştırma

## 🔒 Güvenlik

### Veri Güvenliği
- Veri şifreleme
- Erişim kontrolü
- Denetim kayıtları
- Veri yedekleme

### API Güvenliği
- API anahtarı doğrulama
- Rate limiting
- IP kısıtlamaları
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
- E-posta: stock-support@finasis.com
- Slack: #stock-support
- GitHub Issues

### SLA
- Yanıt süresi: 24 saat
- Çözüm süresi: 72 saat
- Uptime: %99.9 