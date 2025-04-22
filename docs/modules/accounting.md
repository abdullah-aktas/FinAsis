# FinAsis Muhasebe Modülü

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

FinAsis Muhasebe modülü, işletmelerin finansal işlemlerini yönetmek, raporlamak ve analiz etmek için tasarlanmış kapsamlı bir çözümdür.

## 🎯 Özellikler

- Gelir/Gider takibi
- Nakit akışı yönetimi
- Bütçe planlama
- Finansal raporlama
- Vergi hesaplamaları
- Banka entegrasyonu
- Çoklu para birimi desteği
- Otomatik muhasebe kayıtları

## 🔧 Kurulum

### Gereksinimler
- Python 3.9+
- Django 4.0+
- PostgreSQL 13+
- Redis 6.0+

### Kurulum Adımları
1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements/accounting_requirements.txt
```

2. Veritabanı migrasyonlarını çalıştırın:
```bash
python manage.py migrate accounting
```

3. Muhasebe servisini başlatın:
```bash
python manage.py run_accounting_service
```

## 🛠️ Yapılandırma

### Temel Ayarlar
```python
ACCOUNTING_CONFIG = {
    "default_currency": "TRY",
    "fiscal_year_start": "01-01",
    "tax_rate": 0.18,
    "auto_reconciliation": True,
    "default_chart_of_accounts": "standard"
}
```

### Banka Entegrasyonu
```python
BANK_INTEGRATION = {
    "enabled": True,
    "providers": ["isbank", "akbank", "garanti"],
    "auto_sync": True,
    "sync_interval": "daily"
}
```

## 📊 Kullanım

### Hesap Yönetimi
```python
from finasis.accounting import AccountingManager

manager = AccountingManager()
account = manager.create_account(
    name="Kasa",
    code="100",
    type="asset",
    currency="TRY"
)
```

### İşlem Kaydı
```python
transaction = manager.create_transaction(
    date="2025-04-22",
    description="Satış geliri",
    entries=[
        {"account": "100", "debit": 1000},
        {"account": "400", "credit": 1000}
    ]
)
```

### Raporlama
```python
report = manager.generate_report(
    type="balance_sheet",
    start_date="2025-01-01",
    end_date="2025-03-31",
    currency="TRY"
)
```

## 🔍 Örnek Kullanımlar

### Bütçe Planlama
```python
budget = manager.create_budget(
    year=2025,
    items=[
        {"category": "gelir", "amount": 1000000},
        {"category": "gider", "amount": 800000}
    ]
)
```

### Banka Mutabakatı
```python
reconciliation = manager.reconcile_account(
    account_id=1,
    start_date="2025-04-01",
    end_date="2025-04-30"
)
```

## 🧪 Test

### Test Ortamı
```bash
python manage.py test accounting.tests
```

### Test Kapsamı
- Hesap yönetimi
- İşlem kayıtları
- Raporlama
- Banka entegrasyonu
- API testleri

## 📈 Performans

### Ölçümler
- İşlem kayıt süresi: < 1 saniye
- Rapor oluşturma süresi: < 5 saniye
- API yanıt süresi: < 500ms
- Veri arama süresi: < 1 saniye

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
- E-posta: accounting-support@finasis.com
- Slack: #accounting-support
- GitHub Issues

### SLA
- Yanıt süresi: 24 saat
- Çözüm süresi: 72 saat
- Uptime: %99.9 