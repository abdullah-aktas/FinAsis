# Print 3 · Developer Portal MVP Tasarımı

Bu doküman Sprint 3 kapsamındaki **Paket 2 (Developer Portal MVP)** için hedef kapsamı, veri modelini ve teknik yaklaşımı özetler.

## 1. Amaç ve Kullanıcılar

| Persona | İhtiyaç | Portal Özelliği |
| --- | --- | --- |
| **Üçüncü parti geliştirici / entegratör** | API anahtarı oluşturma, dokümantasyon ve test | API key yönetimi, Swagger/Redoc erişimi, webhook test konsolu |
| **FinAsis iç ekipleri (destek, çözüm ortakları)** | Müşteri anahtarlarını yönetme, kullanım takibi | Admin görüşü, quota takibi, kullanım logları |
| **DevOps / Platform ekibi** | Rate limit ve güvenlik kontrolleri, alerting | API key metadata, çağrı loglarının tutulması |

## 2. Portal Kapsamı

1. **Kimlik & Yetki**  
   - Giriş yapmış kullanıcı (FinAsis hesabı). Tenant bilgisi (şirket) ile ilişkilendirilecek.  
   - `permissions` RBAC + yeni `developer_portal.manage_keys` izni.  
2. **API Key Yönetimi**  
   - Ana ekran: mevcut anahtarlar (ad, oluşturma tarihi, son kullanım, kota).  
   - İşlemler: anahtar oluştur, anahtar döndür (rotate), anahtar iptal (soft delete).  
   - Her anahtar için usage özetleri (son 24 saat, 7 gün).  
3. **Dokümantasyon**  
   - Embed edilebilir Swagger (`/accounting/api/docs/`), Redoc.  
   - Dil bazlı örnek kod snippet’leri (Python, JS, Go).  
   - Quickstart rehberleri (OAuth/Keycloak entegrasyonu vs).  
4. **Webhook Test Konsolu**  
   - Kullanıcıdan callback URL + event seçimi.  
   - Örnek payload üretimi + HMAC imzalama.  
   - Sonuç logunun portala gösterilmesi ve audit tablosuna kaydı.  
5. **Analitik ve Uyumluluk**  
   - Her anahtar için kullanım log tablosu (timestamp, endpoint, response code).  
   - Rate limit aşımı, hatalı çağrılar için işaretleme.  
   - Anahtar başına metadata (plan/quota) → rate limit layer ile eşleştirme.

## 3. Mimari Bileşenler

```
developer_portal (yeni Django app)
├── models.py (DeveloperAPIKey, APIKeyUsageLog, WebhookTestLog)
├── services/
│   ├── key_manager.py (create/rotate/revoke, hashing)
│   ├── usage_service.py (istatistikler, quota kontrolü)
│   └── webhook_tester.py (payload üretimi, imzalama, async gönderim)
├── selectors.py (listeleme ve rapor sorguları)
├── forms.py (anahtar oluşturma, rotate)
├── views.py / api.py (HTML + REST endpoint’leri)
├── urls.py (portal rotaları)
├── templates/developer_portal/
│   ├── dashboard.html
│   ├── key_list.html
│   ├── webhook_console.html
│   └── docs.html (swagger/redoc embed)
└── static/ (UI bileşenleri, kütüphane linkleri)
```

- **Model ilişkileri**  
  - `DeveloperAPIKey`: `owner` (User), `organization` (Company/Tenant), `name`, `prefix`, `hashed_key`, `status`, `rate_limit_plan`, `created_at`, `last_used_at`, `expires_at`.  
  - `APIKeyUsageLog`: `api_key`, `path`, `method`, `response_code`, `duration_ms`, `timestamp`.  
  - `WebhookTestLog`: `initiator`, `target_url`, `event_type`, `payload`, `response_status`, `response_body`, `created_at`.
- **Anahtar saklama**: Tam anahtar yalnızca oluşturma anında gösterilir. Veritabanında `hashed_key` (örn. SHA256 + salt). Prefix (örn. `FAK-1234-`) hızlı lookup için tutulur.
- **Authentication**: API çağrılarında custom DRF authentication class (`X-Finasis-Key` header). Key lookup → owner/plan bilgisi → throttle.
- **Authorization**: Portal UI için `permissions` app’i üzerinden `developer_portal.manage_keys` yetkisi. Admin paneline `DeveloperAPIKey` modeli eklenir.

## 4. Veri Modeli Detayı

```python
class DeveloperAPIKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey('accounting.Company', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    prefix = models.CharField(max_length=12, db_index=True)
    hashed_key = models.CharField(max_length=128)
    rate_limit_plan = models.CharField(max_length=32, default='standard')
    allowed_ips = ArrayField(models.GenericIPAddressField(), blank=True, default=list)
    status = models.CharField(max_length=16, choices=APIKeyStatus.choices, default=APIKeyStatus.ACTIVE)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

> **Not:** `allowed_ips` için PostgreSQL ArrayField varsayımı; SQLite’de geliştirme için JSON alanı düşünülebilir. Prod ortamda Postgres şart.

## 5. UI Akışları

1. **Portal Ana Sayfa (`/developers/`)**
   - Kartlar: “API Anahtarları”, “Dokümantasyon”, “Webhook Test”, “Kod Kütüphanesi”.
   - Son çağrılar tablosu (loglardan).
2. **API Anahtarları**
   - Liste, filtreleme (aktif/pasif, plan).
   - “Anahtar Oluştur” modal: ad, plan seçimi, IP kısıtı, son kullanım. Key string tek seferlik gösterilir.
   - “Rotate” işlemi: eski key revoked → yeni key.
   - “Disable/Delete”: soft delete (status=revoked). Audit log.
3. **Dokümantasyon**
   - Swagger iframe (`/accounting/api/docs/?token=...` optional).  
   - Redoc sekmesi.  
   - Kod snippet kartları (statik Markdown → HTML, `common/views_docs` reuse).
4. **Webhook Test Konsolu**
   - Form: event seçimi, hedef URL, header ekleri, manuel payload override.  
   - Gönderim sonrası yanıtın UI’da gösterilmesi (status, body, süre).  
   - Log listesi (kendi test geçmişi + admin için global).

## 6. API Key Üretimi & Güvenlik

| Adım | Açıklama |
| --- | --- |
| 1 | Kullanıcı formu doldurur, seçenekler: anahtar adı, plan, IP whitelist, bitiş tarihi. |
| 2 | `key_manager.generate()` → `prefix` + `secrets.token_urlsafe`. |
| 3 | Hash (`hashlib.sha256`) + salt, DB’ye kaydet. Tam key user’a tek seferlik gösterilir. |
| 4 | Audit log (owner, action). |
| 5 | DRF authentication: request header’daki prefix’e göre key lookup; status/expiry doğrula; usage log yaz. |
| 6 | Rate limit: `plan` bazlı throttle (örn. `standard=100 req/min`, `pro=1000 req/min`). |
| 7 | Alerting: limit aşımı, başarısız girişim, IP kısıtı ihlali logging (Sentry + metrics). |

## 7. Webhook Test Konsolu

```
POST /developers/webhook-test/
Payload {
  "event": "invoice.created",
  "target_url": "https://example.com/webhook",
  "signature_secret": "...",
  "custom_headers": {...},
  "sample_payload": {...}  # optional override
}
```

- `webhook_tester` servisi payload’ı hazırlayıp imzalar (HMAC).  
- Async gönderim (Celery veya background job) → response kaydı `WebhookTestLog`.  
- Portal UI’da sonuç ve hata mesajı (timeout, TLS, HTTP error).  
- Retry seçeneği.

## 8. Entegrasyon Noktaları

| Sistem | Entegrasyon | Not |
| --- | --- | --- |
| DRF Authentication | `developer_portal.authentication.APIKeyAuthentication` | `DEFAULT_AUTHENTICATION_CLASSES` içine eklenecek |
| Rate limit / quota | `developer_portal.throttling.DeveloperAPIKeyRateThrottle` | Plan bazlı dinamik throttle |
| Audit & Logging | `common.logging` + yeni `DeveloperPortalAuditLog` | Admin incelemesi için |
| CI/CD | Migration + unit test + integration test | Pipeline’larda yeni test suite |
| Observability | Prometheus counter (`finasis_api_calls_total`) | Plan ve status etiketi |

## 9. Backlog / İş Paketleri

1. **Uygulama Şablonu & Modeller**
   - `developer_portal` app oluşturma, migration.  
   - Admin ekranları + RBAC permission.
2. **Servisler & Authentication**
   - `key_manager`, `usage_service`, `APIKeyAuthentication`.  
   - Usage log middleware (DRF + Django).
3. **Portal UI**
   - Ana sayfa, key list, create modal.  
   - Swagger/Redoc embed sayfası.  
   - Kod snippet kartları (Markdown → HTML).
4. **Webhook Test Konsolu**
   - Form, servis, log listesi.  
   - Arka plan task (Celery/async).
5. **Dokümantasyon & Test**
   - README/guide.  
  - Unit/integration testler, APIKey usage testleri.  
   - CI pipeline güncellemesi.

---  

**Hazırlayan:** GPT-5 Codex  

