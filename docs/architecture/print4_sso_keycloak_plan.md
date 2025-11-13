# Print 4 · Keycloak / OIDC Entegrasyon Planı

Bu doküman Sprint 4 kapsamında planlanan SSO entegrasyonunun teknik detaylarını ve rollout adımlarını içerir.

---

## 1. Mimari Genel Bakış

```
Kullanıcı → FinAsis (OIDC client) → Keycloak (IdP) → FinAsis
```

1. Kullanıcı `accounts:login` isteğinde Keycloak’a yönlendirilir.
2. Keycloak kimlik doğrulamasını (MFA dahil) gerçekleştirir.
3. OIDC callback ile FinAsis’e `code` gönderilir, token exchange yapılır.
4. Kullanıcı profili (`/userinfo`) çekilir, roller eşleştirilir, session oluşturulur.

---

## 2. Konfigürasyon Dosyaları

### 2.1 `config/oidc.py`
- SSO için ortam değişkenleri:
  - `OIDC_ENABLED`
  - `KEYCLOAK_URL`
  - `KEYCLOAK_REALM`
  - `KEYCLOAK_CLIENT_ID`
  - `KEYCLOAK_CLIENT_SECRET`
- `KEYCLOAK_AUTHORITY` (`{url}/realms/{realm}`) hesaplanır.

### 2.2 `config/settings/base.py`
- `mozilla_django_oidc` uygulaması OIDC aktif ise `INSTALLED_APPS` ve `AUTHENTICATION_BACKENDS` listelerine eklenir.
- OIDC endpoint’leri (`AUTH`, `TOKEN`, `USERINFO`, `JWKS`) Keycloak authority’den türetilir.
- `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` OIDC ile uyumlu şekilde güncellenir.
- OIDC aktifleştirildiğinde `/accounts/otp/` yolları exempt edilerek MFA kontrolü devam eder.

### 2.3 `config/urls.py`
- OIDC aktifse `mozilla_django_oidc.urls` altında callback ve logout endpoint’leri otomatik eklenir (`/oidc/` prefix’i).

---

## 3. Roller ve Eşleştirme

| Keycloak Group | Django Rol / Permission | Not |
| --- | --- | --- |
| `finasis-admin` | `is_staff`, `permissions:admin` | Django admin erişimi |
| `finasis-professional` | Professional paket yetkileri | billing plan eşlemesi |
| `finasis-enterprise` | Enterprise paket yetkileri | multi-tenant + SLA |
| `finasis-developer` | Developer portal `manage_keys` | API key yönetimi |

- Nightly sync job veya login anında roller güncellenebilir (`mozilla_django_oidc.auth.OIDCAuthenticationBackend` override).
- Ek hook: `OIDC_RP_USERINFO_FN` ile kullanıcı profili eşleme fonksiyonu yazılacak.

---

## 4. Güvenlik Notları

- `KEYCLOAK_CLIENT_SECRET` sadece prod ortamında set edilecek; localde SSO devre dışı kalır.
- HTTPS zorunlu (`KEYCLOAK_URL` TLS).
- `OIDC_USE_NONCE = True` ve state kontrolü CSRF riskini azaltır.
- Session + JWT expiry:
  - Access token: 15 dk
  - Refresh token: 12 saat
  - Session idle timeout: 30 dk (yerel middleware ile)
- Logout: `oidc_logout` → Keycloak `end_session_endpoint` kullanılarak global oturum kapatılacak.

---

## 5. Rollout Planı

| Hafta | Görev |
| --- | --- |
| Hafta 1 | Keycloak realm, client ve group yapılandırması; dev ortamında test |
| Hafta 2 | Django tarafında OIDC userinfo eşlemesi, rol sync fonksiyonu |
| Hafta 3 | QA/staging testleri, fallback login stratejisi (acil durumda lokal auth) |
| Hafta 4 | Production rollout, Keycloak MFA policy, kullanıcı iletişimi |

Fallback plan: `OIDC_ENABLED=false` durumunda mevcut Django login akışı (MFA ile) devreye girer.

---

## 6. Env Örnekleri

```
OIDC_ENABLED=true
KEYCLOAK_URL=https://sso.finasis.com
KEYCLOAK_REALM=finasis-prod
KEYCLOAK_CLIENT_ID=finasis-web
KEYCLOAK_CLIENT_SECRET=********
```

`OIDC_ENABLED` false olduğunda yukarıdaki ayarlar yok sayılır ve uygulama mevcut kullanıcı yönetimi ile çalışır.

---

**Hazırlayan:** GPT-5 Codex  

