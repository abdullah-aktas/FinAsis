# Print 3 · CI/CD ve Güvenlik Otomasyonu Planı

Bu doküman Sprint 3 kapsamındaki **Paket 3 (CI/CD & Gözlemlenebilirlik)** için uygulanacak adımları özetler. Hedef; kod kalitesi, güvenlik ve pipeline şeffaflığını artırmak, sonuçları ekibin görebileceği şekilde raporlamaktır.

---

## 1. CI Pipeline Tasarımı

### 1.1 Hedefler
- Her PR ve ana branch için otomatik lint/test/coverage çalıştırmak.
- Coverage raporlarını artefact olarak saklamak ve (varsa) badge üretmek.
- Pull request statüsünü düşüren kırmızı build’leri engellemek.

### 1.2 Pipeline Adımları (GitHub Actions örnek)

```
name: CI
on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Cache pip
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      - name: Install deps
        run: pip install -r requirements.txt

  lint:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint (Ruff + Black)
        run: |
          pip install ruff black
          ruff check .
          black --check .

  test:
    needs: [setup, lint]
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: finasis
          POSTGRES_USER: finasis
          POSTGRES_PASSWORD: finasis
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    env:
      DJANGO_SETTINGS_MODULE: config.settings
      DATABASE_URL: postgres://finasis:finasis@localhost:5432/finasis
    steps:
      - uses: actions/checkout@v4
      - name: Run tests + coverage
        run: |
          pip install coverage pytest pytest-django
          coverage run -m pytest
          coverage xml
          coverage html
      - name: Upload coverage artefact
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: htmlcov/
```

> **Not:** Yerel geliştiriciler için `make lint` / `make test` komutları eklenecek; pipeline aynı komutları çağırır. Postgres servisi opsiyonel, SQLite ile de testler çalıştırılabilir.

### 1.3 Coverage Badge
- `coverage-badge` paketi veya `codecov` entegrasyonu değerlendirilecek.
- Ana branch’de coverage %80 hedefi, altına düşünce pipeline uyarısı.

---

## 2. Güvenlik ve Dependency Tarama

| Araç | Kapsam | Pipeline Adımı |
| --- | --- | --- |
| **Bandit** | Python kodunda güvenlik açıkları | `bandit -r . -ll` |
| **Safety / pip-audit** | Python dependency CVE taraması | `pip install pip-audit` + `pip-audit` |
| **Dependabot/Snyk** | Repo bağımlılık güncellemeleri ve CVE uyarıları | GitHub dependabot.yml veya Snyk CLI |
| **Trivy (opsiyonel)** | Docker image taraması (deploy pipeline) | `trivy fs --exit-code 1 .` |

Önerilen pipeline adımı (`security` job):

```
security:
  needs: setup
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: |
        pip install bandit pip-audit
        bandit -r . -ll
        pip-audit --ignore-vuln GHSA-xxxx  # gerekirse suppression dosyası
```

Dependabot konfigürasyonu (örnek `/.github/dependabot.yml`):

```
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

---

## 3. Bildirim ve Raporlama

### 3.1 Bildirimler
- Slack veya Microsoft Teams webhook’u ile pipeline sonucu özetleri:
  - Build success/failure.
  - Coverage yüzdesi.
  - Security taramasında bulunan kritik açıklar.
- GitHub Action örneği:

```
      - name: Notify Slack
        if: always()
        uses: slackapi/slack-github-action@v1.24.0
        with:
          payload: |
            {
              "text": "CI sonucu: ${{ job.status }} - Coverage: ${{ steps.coverage.outputs.percent }}%"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 3.2 Artefact & Raporlama
- Coverage HTML raporu artefact olarak saklanacak (7 gün).
- Security taraması raporu (JSON) upload edilecek.
- `docs/reports/ci-summary.md` dosyası otomatik güncellenebilir (opsiyonel).

---

## 4. Uygulama Planı

1. **Hafta 3 başı** – CI pipeline YAML dosyası hazırlanır, lint/test/coverage/artefact akışı eklenir.  
2. **Hafta 3 ortası** – Bandit + pip-audit job’ları eklenir, Dependabot konfigürasyonu repo’ya dahil edilir.  
3. **Hafta 3 sonu** – Slack/Teams entegrasyonu ve raporlama, pipeline sonuçlarının gözden geçirilmesi.  
4. **Sonraki sprint** – Trivy ve container güvenliği, pipeline policy enforcement (örn. branch protection).

---

**Hazırlayan:** GPT-5 Codex  

