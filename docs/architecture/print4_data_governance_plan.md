# Print 4 · Veri Yönetişimi ve Güvenlik Planı

Sprint 4 Paket 3 kapsamındaki şifreleme, veri maskesi, retention politikaları ve log/backup planı aşağıda yer almaktadır.

---

## 1. Şifreleme Stratejisi

### 1.1 At-rest Şifreleme
- **Veritabanı**: PostgreSQL Transparent Data Encryption (TDE) veya disk seviyesinde LUKS/BitLocker. Managed DB (CloudSQL, RDS) tercih ediliyorsa KMS entegrasyonu.
- **Dosya depolama (S3/MinIO)**: `server-side encryption` (SSE-S3 veya SSE-KMS). KMS CMK anahtarı per-bucket.
- **Secrets**: `.env` yerine Vault/AWS Secrets Manager; deploy pipeline environment injection.

### 1.2 Uygulama Seviyesi Şifreleme
- Kritik alanlar (TC kimlik, IBAN, kredi kartı vb.) `Fernet` veya `cryptography` ile şifrelenmiş sahalarda saklanmalı.
- `common/services/crypto.py` altında `encrypt(value, key_id)` / `decrypt(value, key_id)` servisleri; key rotation için key_id meta bilgisi.
- Anahtar yönetimi: Vault transit API veya KMS data key (Envelope encryption).

### 1.3 In-transit Şifreleme
- TLS 1.2+ zorunlu; HSTS header (Strict-Transport-Security).
- İç servisler (Redis, Postgres, Celery broker) TLS ile bağlanmalı.
- Mutual TLS: admin/API entegrasyonları için (opsiyonel).

---

## 2. Veri Maskesi / Anonimleştirme

| Veri Tipi | Maskelenme | Not |
| --- | --- | --- |
| Kimlik No | `12345678901` → `***-***-8901` | Görünümler & loglar |
| IBAN | `TR12 3456 7890 1234 5678 9012 34` → `TR** **** **** **** 9012 34` | API response filtreleri |
| E-posta | `ad.soyad@example.com` → `a***@example.com` | Kullanıcı listeleri |
| Telefon | `+90 555 123 45 67` → `+90 *** *** 45 67` | |

### 2.1 Uygulama
- Serializer/Presenter katmanında `mask_*` yardımcıları (`common/presenters/maskers.py`).
- Mask alanları config: `settings.DATA_MASKING_RULES`.
- Loglama: `LOGGING` filtrelerine mask fonksiyonu eklenmeli.
- Anonimleştirme için rapor ekstreleri (CSV/PDF) örnekleri → `reports.anonymize()` fonksiyonu.

---

## 3. Retention Politikaları

| Veri | Retention | İşlem |
| --- | --- | --- |
| Finansal kayıt | 10 yıl (MASAK/KVKK) | `retention_finance` job, arşiv & imzalı saklama |
| Kullanıcı aktiviteleri | 2 yıl | Log index lifecycle → sıcak/soğuk depolama |
| Kişisel veri (PII) | Kullanıcı talebi + SLA (30 gün) | `manage.py retention_execute --profile kvkk` |
| Audit log | 5 yıl | S3 Glacier + hash ile saklama |

### 3.1 Retention Executor
- `retention_profiles/kvkk.yml`:

```yaml
- model: accounts.PersonalDataRequest
  action: delete
  after_days: 30
- model: audit.SecurityAuditLog
  action: archive
  after_days: 1825
  target: s3://finasis-audit-archive/
```

- Komut: `python manage.py retention_execute --profile kvkk`.
- Arşivlenen veriler şifreli olarak saklanır (S3 SSE-KMS).
- İşlem loglanır ve rapor üretilir.

---

## 4. Log & Backup Planı

### 4.1 Log Yönetimi
- Uygulama logları JSON formatında → Fluent Bit → OpenSearch (bkz. Sprint 3 planı).
- Log sınıfları:
  - `app`: business loglar
  - `audit`: güvenlik/audit
  - `access`: HTTP access (NGINX)
- PII maskesi log filter’ı (`common.logging.SensitiveDataFilter`).
- Log retention: 30 gün sıcak, 90 gün soğuk, 1 yıl arşiv (ILM policy).
- Log integrity: hash chain (örn. günlük log dosyası SHA256 → S3 metadata). Denetim için blockchain (opsiyonel).

### 4.2 Backup Stratejisi
- **Veritabanı**: Günlük tam backup, saatlik incremental (WAL). 30 gün saklama, haftalık dış lokasyon.
- **Dosya depolama**: Lifecycle (S3 versioning + Glacier). Encryption by default.
- **Restore Test**: 3 ayda bir DR testi; staging ortamına restore ve sanity check.
- **Runbook**: `docs/operations/backup_restore.md` güncellenecek; erişim yetkisi sadece ops ekibinde.

---

## 5. Raporlama ve İzleme

| Rapor | İçerik | Sıklık |
| --- | --- | --- |
| Şifreleme durum raporu | Hangi alanlar/servisler şifreli | 6 ay |
| Masking doğrulama | Masked fields list, API snapshot | Aylık |
| Retention raporu | Çalışan job’lar, arşivlenen kayıtlar | Haftalık |
| Backup raporu | Başarılı/başarısız backup, restore test sonucu | Haftalık |

Slack bildirimleri: `#security`, `#ops`. Otomatik olarak CI job’ları ile entegre edilir (`make report:data-governance`).

---

## 6. Uygulama Adımları

| Hafta | Görevler |
| --- | --- |
| Hafta 1 | Masking helper’ları, encrypt/decrypt servis tasarımı, retention profil şablonu |
| Hafta 2 | Vault/KMS entegrasyonu PoC, log mask filter, retention executor implementasyonu |
| Hafta 3 | Backup runbook güncellemesi, restore testi, rapor otomasyonu |
| Hafta 4 | Güvenlik ve uyumluluk ekibi review, rollout planı |

---

**Hazırlayan:** GPT-5 Codex  

