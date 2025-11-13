# Print 3 · Domain Analizi ve Refactor Planı

Bu doküman Sprint 3’ün “Teknik Mimari ve DevOps” fazındaki **Paket 1** çıktılarını içerir. Odak noktaları:

1. Django uygulamalarının bounded context perspektifiyle haritalanması ve bağımlılıklar.
2. Paylaşılan kodların envanteri ve servis/util katmanlarına taşınması için backlog.
3. API versiyonlama, hız limiti ve kimlik doğrulama strateji önerileri.

---

## 1. Bounded Context Haritası

| Domain Katmanı | Uygulamalar | Sorumluluklar | Ana Bağımlılıklar |
| --- | --- | --- | --- |
| **Çekirdek Platform** | `accounts`, `permissions`, `common`, `core_ui`, `security`, `tenancy`, `management` | Kullanıcı, rol/RBAC, çoklu tenant, ortak middleware ve temalar | `common` (context processors, middleware), `permissions` (rol yetkileri), `security` (audit) |
| **Finans & Muhasebe** | `accounting`, `finance`, `finance.accounting`, `billing`, `audit`, `kobi_analysis`, `integrator_gib`, `integrator_mock`, `edoc`, `virtual_company` | Muhasebe kayıtları, finansal raporlar, e-belge, entegrasyonlar | Platform katmanı + `ai_assistant` (denetim), `blockchain` (kanıt) |
| **Uyumluluk & Blockchain** | `blockchain`, `audit`, `security` | Zincir kanıt, risk analizleri, denetim loglaması | Finans bağlamı (veri kaynağı), `common.logging`, `ai_assistant` |
| **AI & Danışmanlık** | `ai_assistant`, `advisors` | AI destekli muhasebe, danışman senaryoları | `accounts`, `accounting`, `finance`, `common` |
| **Eğitim & Oyunlaştırma** | `education`, `education.teacher_dashboard`, `games`, `games.*` | LMS, senaryolu oyunlar, gamification | `accounts` (persona), `common` (UI), bazen `finance` (oyun verisi) |
| **Kurumsal & Destek** | `corporate`, `core_ui`, `common.views_help`, `templates/resources*` | Pazarlama, yardım, kaynak merkezi | `common.context_processors`, `core_ui` theme |

### Bağımlılık Diyagramı (özet)

```
            +---------------------+
            |   core_ui / common  |
            +----------+----------+
                       |
             +---------v---------+
             |  accounts         |<---------------+
             +----+--------------+                |
                  |                               |
          +-------v-------+         +-------------v--------------+
          |  permissions  |         |        security            |
          +-------+-------+         +-------------+--------------+
                  |                               |
      +-----------v--------------+        +-------v-----+
      |       tenancy            |        | management  |
      +-----------+--------------+        +-------------+
                  |
   +--------------v-------------------------------+
   |          finance & accounting                |
   | (accounting/billing/finance/audit/edoc/...)  |
   +---------+------------------+-----------------+
             |                  |
   +---------v------+   +-------v-------+
   | blockchain     |   | ai_assistant  |
   +---------+------+   +-------+-------+
             |                  |
     +-------v------+    +------v------+
     |  audit       |    | advisors    |
     +--------------+    +-------------+
```

> **Not:** Dijagram, import/servis çağrıları ve ForeignKey ilişkilerinin hızlı taramasına dayanır (örn: `settings.AUTH_USER_MODEL`, `common.middleware`, `permissions.role_utils`). Veri kökenlerini kayıt altına almak için her app’in README veya kodunda kısa notlar eklenecek.

---

## 2. Paylaşılan Kod Envanteri

| Kategori | Mevcut Konum | Kullanım Alanı | Taşıma Önerisi |
| --- | --- | --- | --- |
| **Context Processors** | `common/context_processors.py`, `core_ui/context_processors.py` | Tüm şablonlar | `common/services/context.py` altında ayrı modüller; test edilip belgelenecek |
| **RBAC & Rol Araçları** | `permissions/`, `common/role_utils.py`, `common/admin_role_assignment.py` | Admin, API, middleware | Tek bir `permissions.services` paketi; admin/API reuse için interface tanımı |
| **Caching & Rate Limit Decorators** | `common/cache_decorators.py`, `common/throttling.py` | API ve view katmanı | `common.services.caching` adında yeni namespace; throttle config DRF ayarına taşınacak |
| **Billing/Subscription Servisleri** | `billing/services.py`, `accounts/services`, `billing/context_processors.py` | Hesap panelleri | `billing.domain` (iş kuralları) + `billing.integrations` (3rd party) ayrıştırılmalı |
| **Finans Hesaplama Util’leri** | `finance/services`, `finance.accounting` alt servisler, `accounting/services` | KPI, rapor, hesaplamalar | `finance.domain` altında “calculator” paketleri, ortak `finance.shared` |
| **Webhook & Notification Helpers** | `common/tasks.py`, `ai_assistant/services`, `audit/utils` | Bildirim, webhook tetikleme | `common.integrations.webhooks` modülü, audit kayıtlarını da kullanacak |
| **PDF/UBL/UBLTR** | `edoc/`, `accounting/views_extra` | e-Fatura / e-Defter | `edoc.shared` → `edoc.domain` ve `edoc.adapters` katmanları; accounting tarafı sadece servis API’sini çağıracak |

---

## 3. Refactor Backlog

| # | Başlık | Kapsam | Hedef | Notlar | Öncelik |
| --- | --- | --- | --- | --- | --- |
| R1 | RBAC servislerinin tekilleştirilmesi | `permissions`, `common.role_utils`, admin görünümü | `permissions/services/rbac_service.py` | API & admin ortak kullanım; unit test gerekli | Yüksek |
| R2 | Context processors modülerleştirme | `common/context_processors`, `core_ui/context_processors` | `common/services/context/` | Django settings üzerinden injection; test doubles | Orta |
| R3 | Finans hesaplama util’lerinin domain-service ayrımı | `finance/services/*`, `finance.accounting` | `finance/domain/` + `finance/shared/metrics.py` | KPI hesapları pure functions, DB erişimi selectors’da | Yüksek |
| R4 | Billing & Subscription servis ayrımı | `billing/services.py`, `accounts/api_panel` | `billing/domain/subscription.py`, `billing/integrations/*.py` | Stripe/iyzico entegrasyonu için adaptör pattern | Orta |
| R5 | Webhook helper consolidation | `common/tasks`, `ai_assistant/services/webhook_*` | `common/integrations/webhooks.py` | Tek noktadan imzalama ve gönderim; retry & audit log | Orta |
| R6 | e-Doc adaptör katmanı | `edoc/*`, `accounting/views_extra/edefter` | `edoc/domain` + `edoc/adapters/gib.py` | Accounting sadece servis arabirimini çağıracak | Düşük |
| R7 | Games & Education ortak persona servisleri | `education/services`, `games/*` | `education/services/persona.py` | Persona bazlı dashboard verilerini paylaştırmak | Düşük |

> Her backlog maddesi için ayrı ticket + tahmini efor eklenecek. R1, R3 ve R5 öncelikli olarak Sprint 3 içinde başlanması önerilir.

---

## 4. API Stratejisi (Versiyonlama, Rate Limit, OAuth/Keycloak)

### 4.1 Versiyonlama
- **Kısa vadede:** Mevcut DRF route’larını `api/v1/` namespace altında toplamak (URLconf alias). Legacy yollar için 3-6 aylık deprecation uyarısı.
- **Uzun vadede:** `v2` için schema-first yaklaşım (OpenAPI contract repo). Breaking change süreçlerini semver mantığıyla (major/minor/patch) yönetmek.

### 4.2 Rate Limiting
- **DRF throttling**: Kullanıcı + API key bazlı custom throttle class (`common.throttling.APIKeyThrottle`).
- **Edge katmanı**: NGINX/Traefik rate limit (örn. 100 req/min default, geliştirilmiş planlar için artış).
- **Developer portal entegrasyonu**: Her API key için quota meta bilgisi; limit aşımlarını webhook + e-posta ile bildirmek.

### 4.3 OAuth / Keycloak
- **POC kapsamı:**  
  1. Keycloak Realms & Client configuration (realm: `finasis-platform`).  
  2. Django tarafında `mozilla-django-oidc` veya `python-keycloak` ile token doğrulama.  
  3. Roller için Keycloak `groups` → `permissions.Role` eşlemesi, nightly sync job.
- **Dağıtım:** Keycloak’ı Docker ile dev/stage için ayağa kaldırıp `accounts` login akışına opsiyonel SSO düğmesi eklemek.  
- **Fallback:** Mevcut Django auth çalışmaya devam eder; Keycloak entegre olduğunda admin kullanıcı rolleri Keycloak master’da tutulur.

---

## 5. Sonraki Adımlar

1. **Diyagram paylaşımı**: Miro/Draw.io dosyası hazırlanacak, Confluence linki eklenerek paylaşıma açılacak.
2. **Backlog ticket’ları**: R1–R7 maddeleri için Jira/Linear ticket’ları açılacak; R1 + R3 Sprint 3’e, R4+R5 Sprint 4’e öneriliyor.
3. **API stratejisi doğrulaması**: Altyapı ekibiyle rate limit ve Keycloak POC zamanlaması netleştirilecek.
4. **Developer Portal MVP** (Paket 2) için gereksinimler bu dokümanı referans alacak; API key quota ve loglama modülleri R1/R5 sonrası kullanılacak.

---

**Hazırlayan:** GPT-5 Codex  

