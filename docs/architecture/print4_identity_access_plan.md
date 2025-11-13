# Print 4 · Kimlik ve Erişim Sertleştirme Planı

Sprint 4 Paket 1 kapsamındaki MFA/SSO, RBAC/ABAC ve oturum + audit log gereksinimleri aşağıda detaylandırılmıştır.

---

## 1. Mevcut Durum Özeti

| Alan | Mevcut | Boşluk |
| --- | --- | --- |
| Kimlik doğrulama | Django `ModelBackend`, opsiyonel JWT | MFA/SSO yok, tek faktör |
| RBAC | `permissions` app, role-based (gruplar) | İnce taneli yetkiler için ABAC eksik |
| Oturum yönetimi | Django session, öntanımlı timeout | Device/IP sınırlaması, eş zamanlı oturum kısıtı yok |
| Audit log | `common.logging`, manuel kayıtlar | Tüm kritik aksiyonlar yakalanmıyor, merkezi rapor yok |

---

## 2. MFA / SSO Stratejisi

### 2.1 MFA
- **Kısa vadeli çözüm:** TOTP tabanlı MFA (Google Authenticator, Authy). Paket önerisi: `django-otp`, `django-two-factor-auth`.
  - Kullanıcı ayarlarında MFA kurulum sihirbazı.
  - Admin/uyumluluk rollerinde MFA zorunlu.
  - Recovery codes + backup method (SMS/e-posta opsiyonel).
- **Entegrasyon:** Login view sonrası challenge, API token oluştururken ikinci faktör zorunlu (developer portal anahtarlarını döndürme vb.).

### 2.2 SSO
- IdP tercihi: Keycloak (geçen sprint POC). Alternatif: Azure AD / Okta.
- **Akış:** OIDC Authorization Code Flow.
- **Plan:**
  1. Keycloak realm: `finasis-prod`, client: `finasis-web`.
  2. Django: `mozilla-django-oidc` veya `django-allauth` OIDC.
  3. Gruplar: Keycloak `groups` → Django `permissions.Role` eşlemesi (sync job).
  4. MFA enforcement: Keycloak policy (MFA enabled, admin role).
  5. Fall-back: Yerel kullanıcı girişi sadece acil durum (feature flag).

### 2.3 Yapılacaklar
1. `SENTRY_DSN` benzeri `KEYCLOAK_*` ayarlarını `.env` dosyasına eklemek.
2. MFA migration planı: kritik kullanıcılar → tüm kullanıcılar (3 aşama).
3. MFA compliance raporu (kimin MFA aktif, son doğrulama tarihi).

---

## 3. RBAC / ABAC İyileştirmesi

### 3.1 RBAC İncelemesi
- `permissions` app’de mevcut roller: admin, staff, viewer (örnek). Modul bazlı yetkiler için gruplar.
- Audit: Hangi view set’leri `IsAuthenticated` dışında kontrol ediliyor? (örn. DRF view’lerde `permission_classes`).
- Eksikler:
  - Developer portal `manage_keys` izni eklendi fakat UI’da role assignment sihirbazı yok.
  - `accounts` modülünde kullanıcı rol değişiklikleri loglanmıyor.

### 3.2 ABAC (Attribute Based)
- Gereksinimler:
  - Tenant/Company bazlı erişim: user.company == object.company.
  - Persona/rol + feature flag: CFO’lar için belirli raporlar, öğrenciler için sınırlı dashboard.
- Öneri:
  - `common.middleware_rbac` genişletilerek request context’e attribute policy eklemek.
  - `permissions/services/policy_engine.py`: basit DSL (örn. `{"attr": "company_id", "op": "equals", "source": "request.user.company_id"}`).
  - Policy declaration YAML/JSON, admin UI ile düzenleme.

### 3.3 Yapılacaklar
1. RBAC envanter dokümanı: roller, izinler, hangi view/controller.
2. ABAC policy motoru taslağı ve pilot uygulama (developer portal API key detail → sadece key.owner).
3. Role assignment UI: `permissions` admin sayfasında bulk assign + import/export.

---

## 4. Oturum Yönetimi & Audit Log

### 4.1 Oturum Politikaları
- Session timeout: 30 dakika inaktif, maksimum 12 saat aktif (configurable).
- Persistent session flag (remember me) – yalnızca MFA etkin kullanıcılar için.
- Eş zamanlı oturum limiti: varsayılan 3 cihaz; limit aşıldığında eski oturumlar kapanır.
- Device fingerprinting: user-agent + IP hash, kullanıcıya bildirim (yeni cihaz login).
- API token/OAuth refresh token revocation list (Redis cache).

### 4.2 Audit Log Gereksinimleri
- Loglanacak olaylar:
  - Login success/failure, MFA challenge, SSO login.
  - Permission/role değişiklikleri.
  - API key oluşturma/döndürme/silme (developer portal).
  - Hassas veri görüntüleme/indirme (rapor export, e-fatura, blockchain kanıt).
- Standart format:

```
{
  "timestamp": "...",
  "actor_id": "...",
  "actor_email": "...",
  "action": "api_key.rotate",
  "resource": "DeveloperAPIKey:uuid",
  "ip": "...",
  "user_agent": "...",
  "metadata": {...},
  "success": true
}
```

- Depolama: `developer_portal_developerportalauditlog` genişletilecek; genel amaçlı `security_audit_log` tablosu veya ELK indeksine gönderim. Retention: min. 1 yıl.

### 4.3 Yapılacaklar
1. Session middleware konfigürasyonu (`SESSION_COOKIE_AGE`, `SESSION_EXPIRE_AT_BROWSER_CLOSE`, custom session backend?).
2. Concurrency kontrolü: `django-axes` veya custom middleware.
3. Audit log servis katmanı (`common/services/audit_logger.py`) → Sentry breadcrumb + ELK.
4. Security team için rapor: haftalık login başarısızlıkları, role değişiklikleri, kritik aksiyonlar.

---

## 5. Yol Haritası

| Hafta | Görevler |
| --- | --- |
| Hafta 1 | MFA modülü PoC, RBAC envanter çıkarma, audit log gereksinimleri |
| Hafta 2 | Keycloak/OIDC entegrasyon planı, ABAC prototipi, session policy tasarımı |
| Hafta 3 | Audit log servis implementasyonu, eş zamanlı oturum kontrolü, MFA rollout planı |
| Hafta 4 | Testler, dokümantasyon, ekip eğitimi ve rollout onayı |

---

**Hazırlayan:** GPT-5 Codex  

