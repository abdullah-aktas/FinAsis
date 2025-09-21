# Blockchain Modülü (FinAsis)

Bu modül; muhasebe ve finans kayıtlarının bütünlüğünü, değişmezliğini ve izlenebilirliğini sağlamak için yerel, hafif bir kanıtlama (proof) altyapısı sunar. Kayıtlar SHA-256 ile özetlenir, `ChainRecord` içine yazılır ve UI/API üzerinden doğrulanabilir.

## Amaç
- Muhasebe ve finans verilerinin (Fatura, E‑Defter, Fiş, Ödeme, Gider, Banka Hareketi) bütünlüğünü kanıtlamak
- Kayıtların sonradan değişmediğini göstermek (hash ile doğrulama)
- Gerektiğinde dış zaman damgası/gerçek zincire "ankraj" yapılabilecek genişletilebilir bir yapı sunmak

## Özellikler
- Kayıt Hash’i: Her kritik kayıt için deterministik payload → SHA‑256 → `hash_hex`
- Otomatik Hashleme: Django sinyalleri ile kayıtlar kaydedildiğinde `ChainRecord` oluşur
- Doğrulama API’si: `POST /blockchain/api/verify/` ile bir referans+payload doğrulanır
- Web UI: Liste/oluştur sayfaları ve ana sayfada doğrulama formu

## Model
- `ChainRecord`
  - `reference: CharField(255)` — İşlemsel referans (örn: `invoice:123`)
  - `hash_hex: CharField(64)` — SHA‑256 sonuç değeri (hex)
  - `payload_preview: TextField` — Hash alınan verinin ön izlemesi (ilk 500 karakter)
  - `status: CharField(20)` — `pending`, `anchored`, `verified` vb.
  - `created_at: DateTimeField` — Oluşturulma zamanı

## Sinyaller (Otomatik Hashlenen Kayıtlar)
Aşağıdaki kayıtlar `post_save` ile hashlenir ve `ChainRecord` oluşturulur:
- Fatura (`Invoice`)
- e‑Defter (`EDefter`)
- Fiş (`Voucher`) ve satırlarının özeti
- Ödeme (`Payment`)
- Gider (`Expense`)
- Banka Hareketi (`BankTransaction`)

Duruma göre `status` alanı `anchored` (örn. `Voucher.state == posted`) ya da `pending` olarak set edilir.

## Servisler (helpers)
`FinAsis.apps.blockchain.services`:
- `compute_sha256_hex(payload: str) -> str`
- `ensure_record(reference: str, payload: str, status: str = 'pending') -> ChainRecord`
- `payload_for_*` fonksiyonları: `invoice`, `voucher(+lines)`, `payment`, `expense`, `banktxn`, `edefter`

Örnek kullanım (Python):
```python
from FinAsis.apps.blockchain.services import ensure_record, compute_sha256_hex

payload = "INVOICE|12345|2024-07-01|1000.00|customer:9"
ensure_record(reference="invoice:123", payload=payload, status="anchored")
```

## URL’ler ve Ekranlar
- `/blockchain/` — Ana sayfa (hash doğrulama formu)
- `/blockchain/records/` — Kayıt listesi
- `/blockchain/records/create/` — Kayıt oluşturma formu
- `/blockchain/api/verify/` — Doğrulama API (POST)

### Doğrulama API (POST)
Form‐Data:
- `reference`: Örn. `invoice:123`
- `payload`: Hash’lenecek düz metin (sistemde kayıt oluşturulurken kullanılanla aynı olmalı)

Dönüş:
```json
{
  "reference": "invoice:123",
  "hash_hex": "…",
  "verified": true
}
```

## Kurulum ve Çalıştırma
PowerShell (Windows):
```powershell
cd finasis-src
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations blockchain
python manage.py migrate
python manage.py runserver
```

## Güvenlik ve Genişletme
- Hash alma yerel olarak gerçekleşir; veri dış servislere gönderilmez
- `status=anchored` için IPFS/Time‑Stamp/gerçek zincire adaptör eklenebilir
- Admin tarafında ilgili kaydın `ChainRecord` referansını gösteren hızlı linkler eklenebilir

## Sorun Giderme
- Doğrulama başarısızsa payload’ın birebir aynı üretildiğini doğrulayın
- Sinyaller çalışmıyorsa `FinAsis.apps.blockchain.apps.BlockchainConfig.ready()` içinde `signals` importunun yüklendiğini kontrol edin
