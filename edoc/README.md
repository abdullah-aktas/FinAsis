# FinAsis e-Doc Paketi (e-Fatura, e-Arşiv, e-İrsaliye, e-Defter)

Bu dizin, e‑belge (UBL‑TR) ve e‑Defter süreçlerini yöneten modülleri içerir. Geliştiricilere yönelik bu## Yönetim komutu ile kullanım

### Manuel paketleme: `package_edefter`

- XML + Berat üretimi (boyut bilgisi):

```powershell
python manage.py package_edefter --year 2025 --month 9
```

- ZIP üretimi (opsiyonel imza/TS ve dosyaya yazma):

```powershell
python manage.py package_edefter --year 2025 --month 9 --zip
python manage.py package_edefter --year 2025 --month 9 --zip --signed --out D:\temp\edefter_202509.zip
```

### Aylık otomasyon: `generate_monthly_edefter`

Tüm aktif şirketler için aylık e-Defter üretir, EDefter modeline kaydeder ve opsiyonel olarak GİB'e gönderir:

```powershell
# Manuel çalıştırma (mevcut ay/yıl):
python manage.py generate_monthly_edefter

# Belirli dönem için:
python manage.py generate_monthly_edefter --year 2025 --month 9

# GİB'e de gönder:
python manage.py generate_monthly_edefter --year 2025 --month 9 --send

# Tek şirket için:
python manage.py generate_monthly_edefter --year 2025 --month 9 --company 5

# Mevcut kayıtları güncelle:
python manage.py generate_monthly_edefter --year 2025 --month 9 --force
```

**Windows Task Scheduler ile otomasyonu:**

1. Task Scheduler açın (`taskschd.msc`)
2. "Create Basic Task" → İsim: "FinAsis Aylık e-Defter"
3. Trigger: Monthly, ayın ilk günü saat 03:00
4. Action: Start a program
   - Program: `D:\FinAsis\.venv\Scripts\python.exe`
   - Arguments: `manage.py generate_monthly_edefter --send`
   - Start in: `D:\FinAsis`
5. Alternatif: Batch dosyası kullanın (`edefter_monthly.bat`):

```batch
@echo off
cd /d D:\FinAsis
call .venv\Scripts\activate.bat
python manage.py generate_monthly_edefter --send
if errorlevel 1 (
  echo Hata: %date% %time% >> D:\FinAsis\edefter_errors.log
)
```yi, modülleri, ayarları, kullanım örneklerini ve test akışını özetler.

## İçerik
- Mimari ve Modüller
- Kurulum ve Ön Gereksinimler
- Ayarlar (settings) ve Çevresel Değişkenler
- UBL‑TR: Fatura ve İrsaliye (XML üretimi ve şema doğrulama)
- GİB İstemcisi (stub) ve yeniden deneme politikası
- e‑Defter (Yevmiye/Kebir üretimi), Berat ve Paketleme
- İmzalama/Zaman Damgası (stub sağlayıcılar)
- İmzalama/Zaman Damgası (dummy + HSM/TSA iskeletleri)
- Yönetim komutu ile kullanım
- Testler ve Geliştirme Akışı
- Yol Haritası

---

## Mimari ve Modüller

```
edoc/
  ubltr/         # UBL‑TR 2.x XML üretimi ve şema doğrulama yardımcıları
  gib/           # GİB ile entegrasyon (stub: gönder/poll)
  edefter/       # e‑Defter (Yevmiye/Kebir üretimi), Berat ve paketleme
  signing/       # İmzalama ve zaman damgası sağlayıcı protokolleri + dummy
  shared/        # Ortak ayarlar, hata tipleri, logging yardımcıları
  schemas/       # (Opsiyonel) Şema dosyaları için klasör
```

- `ubltr/invoice.py`, `ubltr/dispatch.py`: Minimal XML üreticiler (UBL‑TR Invoice ve DespatchAdvice)
- `ubltr/schema.py`: XSD keşfi ve doğrulama (opsiyonel, yoksa “graceful skip”)
- `gib/client.py`: Gönderim/polling stub (idempotent, retry/backoff ile uyumlu plan)
- `edefter/generator.py`: Yevmiye/Kebir üretimi (Decimal güvenli, basit XML)
- `edefter/berat.py`: Berat XML, hash zinciri (minimal yaklaşım)
- `edefter/packaging.py`: Dosya adlandırma ve ZIP paketleme
- `signing/providers.py`: `Signer`/`TimestampProvider` protokolleri ve `Dummy*` sağlayıcılar
  - Ek: `HSMSigner` (iskelet) ve `HttpTSAProvider` (HTTP tabanlı TSA iskeleti)

> Not: Üretim ortamlarında dummy imza/TS yerine HSM/TSP entegrasyonları eklenmelidir.

---

## Kurulum ve Ön Gereksinimler

- Python 3.11+ (projede mevcut sanal ortamı kullanın)
- Django ve proje bağımlılıkları (repo kökündeki `requirements.txt`/`pyproject.toml`)
- (Opsiyonel) `lxml` yüklü değilse, `xml.etree.ElementTree` fallback çalışır fakat özellikler sınırlanır.

> Windows PowerShell üzerinde geliştirme yapıyorsanız, sanal ortamı aktif edip testleri `pytest` ile çalıştırabilirsiniz.

---

## Ayarlar ve Çevresel Değişkenler

- `EDOC_SCHEMAS_DIR`: Şema dosyalarının bulunduğu klasör (UBL doğrulaması için opsiyonel)
- `EDEFTER_HTTP_RETRIES` (int, default 3): GİB HTTP çağrıları için retry sayısı
- `EDEFTER_HTTP_BACKOFF` (float, default 0.5): Retry backoff katsayısı
- `EDEFTER_HTTP_TIMEOUT` (float, default 15): HTTP zaman aşımı (saniye)
- `EDEFTER_INCLUDE_SIGNED` (bool, default False): ZIP’e imzalı/TS çıktıları ekle
- `EDEFTER_SIGNER` / `EDEFTER_TSP`: `Signer` ve `TimestampProvider` örnekleri ile override edilebilir.

Django ayarlarında örnek:

```python
# settings.py
EDEFTER_HTTP_RETRIES = 3
EDEFTER_HTTP_BACKOFF = 0.5
EDEFTER_HTTP_TIMEOUT = 15
EDEFTER_INCLUDE_SIGNED = False
# Gelişmiş: üretimde gerçek sağlayıcılar verilebilir
# EDEFTER_SIGNER = MyHSMSigner(...)
# EDEFTER_TSP = MyTSAProvider(...)
```

Kabuğa örnek:

```powershell
$env:EDOC_SCHEMAS_DIR = "D:\\FinAsis\\schemas\\ubltr23"
```

---

## UBL‑TR: Fatura ve İrsaliye

XML üretimi:

```python
from FinAsis.src.edoc.ubltr.invoice import Invoice
xml_bytes = Invoice(...).to_xml_bytes()
```

Şema doğrulama (varsa):

```python
from FinAsis.src.edoc.ubltr.schema import validate_invoice_xml
validate_invoice_xml(xml_bytes)  # Şema bulunamazsa sessizce geçer
```

İrsaliye (DespatchAdvice) için `ubltr/dispatch.py` ve `validate_dispatch_xml` benzer şekilde çalışır.

---

## GİB İstemcisi (Stub)

`edoc/gib/client.py` minimal bir gönderim/poll akışı örneği içerir ve artık adaptör mantığıyla çalışır.

- `EDOC_GIB_MODE=stub` (varsayılan): Yerel stub (`.edoc_state` altında idempotent)
- `EDOC_GIB_MODE=http`: `edoc/gib/adapters.py` içindeki `HttpGibAdapter` ile `EdocSettings.endpoints` üzerinden HTTP çağrıları

Prod entegrasyon için `EdocSettings.endpoints` yapılandırılmalı ve `HttpGibAdapter` genişletilmelidir.

---

## GİB Sandbox Toplu Test (50 Fatura) ve Retry/Idempotency

Bu repoda sandbox/mock ortamına toplu gönderim ve başarı oranı ölçümü için bir yönetim komutu bulunur:

```powershell
# HTTP modunda mock endpoint (Django) ile duman testi
$env:EDOC_GIB_MODE = "http"
$env:EDOC_GIB_BASE_URL = "http://127.0.0.1:8000/gib-mock"  # veya gerçek sandbox URL’niz
python manage.py gib_sandbox_batch_test --count 50
```

Notlar:
- Idempotency: HTTP adapter, `Idempotency-Key` başlığı gönderir. Stub/Mock tarafında aynı anahtar tekrarlarında yeni kayıt oluşturulmaz.
- Retry: `GibClient.send_with_retry(...)` üstel backoff ile `EDOC_RETRY_MAX`, `EDOC_RETRY_BACKOFF`, `EDOC_RETRY_MAX_BACKOFF` ayarlarını kullanır.
- Başarı ölçütü: 50 gönderim içinde kabul edilen adet / 50 >= %99 değilse komut `1` koduyla döner.

Ortam değişkenleri (öncelik sırasıyla):
- `EDOC_GIB_BASE_URL`: HTTP modunda temel URL (örn. mock/sandbox)
- `GIB_TEST_BASE_URL`: Eski değişken adı; yoksa `EDOC_GIB_BASE_URL` kullanılır

---

## e‑Arşiv PDF Üretimi

Basit bir e‑Arşiv fatura özeti PDF’i üretmek için `reportlab` tabanlı yardımcı fonksiyon mevcuttur:

```python
from decimal import Decimal
from edoc.ubltr.invoice import Invoice, Party, Line
from edoc.pdf import generate_invoice_pdf

inv = Invoice(
  id="PDF-TEST-1",
  issue_date=__import__("datetime").date.today(),
  supplier=Party(name="Satıcı A.Ş.", tax_id="1111111111"),
  customer=Party(name="Alıcı Ltd.", tax_id="2222222222"),
  lines=[Line(description="Ürün", quantity=Decimal("2"), unit_price=Decimal("50"))],
  notes=["Teşekkürler"],
)
pdf_bytes = generate_invoice_pdf(inv)
```

> Bu çıktı test/demonstrasyon amaçlı minimal bir görselleştirmedir; üretimde kurumsal şablonlarla genişletilebilir.

---

## e‑Defter: Yevmiye/Kebir, Berat ve Paketleme

Yevmiye/Kebir üretimi:

```python
from FinAsis.src.edoc.edefter.generator import JournalEntryDTO, JournalLine, build_yevmiye, build_kebir
entries = [
  JournalEntryDTO(
    date_=date(2025, 9, 1),
    number="1",
    lines=[JournalLine("100", debit=Decimal("100.00")), JournalLine("600", credit=Decimal("100.00"))],
  )
]
yxml = build_yevmiye(entries)
kxml = build_kebir(entries)
```

Berat üretimi (minimal):

```python
from FinAsis.src.edoc.edefter.berat import build_berat_xml
last_hash = hashlib.sha256(yxml).hexdigest()
berat = build_berat_xml("2025-09", "1234567890", last_hash)
```

ZIP paketleme:

```python
from FinAsis.src.edoc.edefter.packaging import build_output_name, package_zip
files = {build_output_name("1234567890", 2025, 9, "yevmiye"): yxml,
         build_output_name("1234567890", 2025, 9, "kebir"): kxml,
         build_output_name("1234567890", 2025, 9, "berat"): berat}
zip_bytes = package_zip(files)
```

> Projedeki `src/apps/accounting/services/edefter_service.py`, GL fişlerinden DTO’ları otomatik toplayıp Yevmiye/Kebir/Berat üretir ve ZIP’ler.

---

## İmzalama ve Zaman Damgası

`edoc/signing/providers.py`:
- `Signer` / `TimestampProvider` protokolleri
- `DummySigner` ve `DummyTimestampProvider` (geliştirme/test amaçlı)
- `HSMSigner` iskeleti: HSM/akıllı kart entegrasyonuna hazır parametrelerle
- `HttpTSAProvider` iskeleti: Basit HTTP TSA uçları için

ZIP’e imzalı (`.sig`) ve zaman damgalı (`.ts`) varyant eklemek için servis fonksiyonu:

```python
from src.apps.accounting.services.edefter_service import package_edefter_zip
zip_bytes = package_edefter_zip(company, 2025, 9, include_signed=True)
```

---

## Yönetim Komutu ile Kullanım

Komut: `package_edefter`

- XML + Berat üretimi (boyut bilgisi):

```powershell
python manage.py package_edefter --year 2025 --month 9
```

- ZIP üretimi (opsiyonel imza/TS ve dosyaya yazma):

```powershell
python manage.py package_edefter --year 2025 --month 9 --zip
python manage.py package_edefter --year 2025 --month 9 --zip --signed --out D:\temp\edefter_202509.zip
```

---

## Testler ve Geliştirme Akışı

- Pytest ile çalıştırın:

```powershell
pytest -q
```

- Örnek testler:
  - `tests/edoc/test_invoice_basic.py`: UBL‑TR fatura üretimi/validasyonu
  - `tests/edoc/test_berat.py`: Hash zinciri ve minimal berat XML
  - `tests/edoc/test_edefter_generator.py`: Yevmiye toplamları ve Kebir bakiyeleri
  - `tests/edoc/test_gib_retry_idempotency.py`: GİB stub idempotency/poll

Geliştirme ipuçları:
- Şema doğrulaması opsiyoneldir; XSD dizini yoksa testler atlanır.
- `Decimal` kullanın; para alanlarında kayan noktalı tiplerden kaçının.
- Büyük dosyalar için ZIP işlemleri diske yazmadan `BytesIO` ile bellek içi yapılır.

---

## Yol Haritası

- [ ] UBL‑TR kapsayıcılığını artırma (Invoice sahaları, Allowance/Charges vb.)
- [ ] DespatchAdvice (e‑İrsaliye) alanlarının genişletilmesi ve testler
- [ ] e‑Defter için mevzuata tam uyumlu XML şemaları ve validasyon
- [ ] HSM tabanlı imzalama ve TSP entegrasyonu (HSMSigner/HttpTSAProvider somutlama)
- [ ] GİB test/sandbox gerçek uçlarına adaptör (HttpGibAdapter genişletme)
- [ ] CI aşamalarında şema doğrulama/kalite kapıları

> Bu doküman geliştirici odaklıdır. Üretim ortamında mevzuat ve güvenlik gereklilikleri doğrultusunda ek doğrulama, imza, zaman damgası ve arşiv süreçleri uygulanmalıdır.
