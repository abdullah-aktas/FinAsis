# Finance Uygulaması

Bu modül, FinAsis platformunda banka, e-fatura, çek/senet, muhasebe ve finansal raporlama işlemlerini yönetir.

## Klasör Yapısı
- `models/` ve `models.py`: Veri modelleri
- `views/`: Fonksiyonel view dosyaları
- `services/`: Servis ve yardımcı fonksiyonlar
- `serializers/`: API için serializerlar
- `templates/finance/`: Web arayüzü şablonları
- `static/finance/`: Statik dosyalar
- `api/`: API endpointleri ve urls
- `urls/`: Web ve API için ayrı URL dosyaları
- `tests/`: Birim testler

## Geliştirme Notları
- Kodlar modüler ve fonksiyonel olarak ayrılmıştır.
- API ve web endpointleri ayrıdır.
- Testler `tests/` klasöründe yer alır.

## Katkı
Kodunuzu göndermeden önce testlerinizi çalıştırın ve PEP8'e uygun kod yazmaya özen gösterin. 

## Amortisman ve Dönem Sonu Özellikleri (Yeni)

Eklenen bileşenler:

* `TrialBalanceSnapshot` modeli: Dönem kapanışında mizan bakiyelerini JSON olarak cache'ler.
* Celery task `finance.compute_monthly_depreciation`: Aylık amortismanı hesaplar, yevmiye fişi üretir ve dengedeyse otomatik post eder.
* Yönetim Komutları:
	* `python manage.py month_close --company-id <ID> [--date YYYY-MM-DD] [--skip-depreciation]`
	* `python manage.py year_close --company-id <ID> [--period-id <PID>]`

İş Akışı:
1. Ay sonu: `month_close` -> amortisman tetiklenir (async), snapshot alınır.
2. Yıl sonu: `year_close` -> son snapshot + mali dönem kapanışı (`is_closed=True`).
3. Kapalı döneme fiş değişikliği engellenir.

Testler:
* `test_trial_balance_snapshot_basic`: Snapshot üretimi ve toplamların doğruluğu.
* `test_closed_period_block`: Kapalı döneme fiş kaydı blokesi.

Gelecek İyileştirmeler:
* Amortisman gider hesabı yapılandırması
* Yıl sonu gelir/gider aktarım fişi otomasyonu
* Snapshot tutarlılığı için ek mutabakat raporları