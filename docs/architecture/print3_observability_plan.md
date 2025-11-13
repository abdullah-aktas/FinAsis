# Print 3 · Observability ve Alerting Planı

Sprint 3 kapsamındaki **Paket 4** için loglama, metrik ve alerting stratejisini özetler. Amaç, uygulamanın davranışını görünür kılmak ve kritik olaylara hızlı tepki vermeyi sağlamak.

---

## 1. Hedefler

1. Hataların merkezi bir yerde toplanması (Sentry).
2. Performans ve iş metriklerinin izlenmesi (Prometheus + Grafana).
3. Logların aranabilir ve saklanabilir olması (ELK/OpenSearch).
4. Kritiklik seviyesine göre otomatik uyarılar (Slack/Teams, e-posta).

---

## 2. Sentry Entegrasyonu

| Adım | Detay |
| --- | --- |
| DSN yapılandırması | `SENTRY_DSN` environment variable. Prod/staging farklı DSN. |
| Django entegrasyonu | `sentry-sdk` paketi, `sentry_sdk.init()`; `before_send` ile PII maskesi. (`config/settings/base.py` içinde uygulandı.) |
| Performance tracing | Sentry için `traces_sample_rate` (örn. 0.2). Celery/Channels entegrasyonu opsiyonel. |
| Release tag | CI pipeline içinde `sentry-cli releases set-commits`. |
| Alerting | Sentry içinde Issue alert: `level=error`, Slack kanalı ve e-posta listesi. |

Kod örneği (`config/settings/base.py`):

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if ENV("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=ENV("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(ENV("SENTRY_TRACES", 0.1)),
        environment=ENV("DEPLOY_ENV", "local"),
        send_default_pii=False,
    )
```

---

## 3. Prometheus & Grafana

### 3.1 Prometheus Exporter
- Paket: `django-prometheus`.
- `INSTALLED_APPS` ve middleware eklendi; `/metrics` endpoint’i hazır (`config/urls.py`).
- Kullanılacak metrikler:
  - Django request latency (`django_http_request_latency_seconds`).
  - Celery job süreleri (opsiyonel).
  - Custom business metrics (ör. `finasis_api_calls_total`, `finasis_api_call_latency_seconds` – developer portal middleware’inde ölçülüyor).

### 3.2 Grafana Dashboard
- Hazır paneller: Django, PostgreSQL, Redis.
- Özel panel: `DeveloperAPIKey` kullanım oranı, hata sayıları.
- Dashboard as code: `grafana/provisioning/dashboards/developer_portal.json`.

### 3.3 Alert Rules
- Prometheus alertmanager:
  - `HTTP 5xx rate > 5%` 5 dakika boyunca.
  - `Celery task failures > 10` / saat.
  - `Database connections > 80%`.
- Alertmanager → Slack/Teams webhook.

---

## 4. Log Yönetimi

| Katman | Araç | Plan |
| --- | --- | --- |
| Uygulama logları | Python logging, JSON format | `LOGGING` config → JSON renderer, request id eklenir (`DJANGO_ENABLE_JSON_LOGS=True`). |
| Log shipper | Filebeat / Fluent Bit | Docker host’tan logları toplayıp Elastic’e gönderme. |
| Depolama | ELK (Elasticsearch + Kibana) veya OpenSearch | Index lifecycle policy (örn. 30 gün). |
| İndeksleme | `log-type: django`, `env: prod`, `request_id`, `user_id`. |
| Arama | Kibana saved search’ler, Sentry ile link (issue → log query). |

Blueprint:

```
app logs (JSON) --> fluent bit --> OpenSearch
                          ↘
                           Prometheus (metrics exporter)
```

Ek olarak, `common.logging` modülünde request correlation ID middleware’inin eklendiği kontrol edilecek. Yoksa `common.middleware.RequestContextLoggingMiddleware` genişletilip `X-Request-ID` header’ı üretip loglara yazacak.

---

## 5. Alerting Kanalları

| Olay | Kanal | Not |
| --- | --- | --- |
| CI failure / coverage düşüşü | Slack `#eng-ci` | GitHub Actions Slack app |
| Sentry error (prod) | Slack `#alerts-prod`, e-posta on-call | Sentry alert rule |
| Prometheus yüksek hata oranı | Pager/Slack | Alertmanager |
| Log pattern (security event) | SIEM / e-posta | OpenSearch alert |

---

## 6. Uygulama Adımları

1. **Hafta 4 başı** – Sentry SDK kurulumu, DSN konfigürasyonu, test ortamında doğrulama.
2. **Hafta 4 ortası** – `django-prometheus` entegrasyonu ve `/metrics` endpoint’i; Prometheus + Grafana docker-compose ile dev/test.
3. **Hafta 4 sonu** – Fluent Bit/OpenSearch pipeline, log formatı güncellenmesi, alert kurallarının dokümantasyonu.
4. **Sonraki sprintler** – Production deploy, dashboard iyileştirmesi, business metric eklemeleri.

---

**Hazırlayan:** GPT-5 Codex  

