# Print 4 · Uyumluluk Otomasyonu Planı

Sprint 4 Paket 2 kapsamında MASAK & KVKK süreçlerinin otomasyonu ile blockchain audit entegrasyon testleri için yol haritası aşağıdadır.

---

## 1. MASAK & KVKK Checklist Otomasyonu

### 1.1 Checklist İçeriği
- **MASAK (AML) Kontrolleri**
  - Müşteri tanıma (KYC) belgeleri tam mı?
  - Şüpheli işlem raporları günlük olarak kontrol edildi mi?
  - Risk skorlaması çalışıyor mu? (örn. belirlenen eşik)
  - Loglar ve saklama süresi (en az 10 yıl) politikası uygulanıyor mu?
  - MASAK rehberine uygun rapor formatı (PDF/Excel).
- **KVKK Kontrolleri**
  - Aydınlatma metni ve kullanıcı onay logları mevcut mu?
  - Veri işleme envanteri güncel mi?
  - Silinmesi gereken kişisel veriler (retention) işlenmiş mi?
  - İlgili kişi başvuruları (access/delete) SLA içinde cevaplanmış mı?
  - KVKK raporu (özet + detay) CI artefact’ı olarak saklanmalı.

### 1.2 Otomasyon Yaklaşımı

| Adım | Açıklama |
| --- | --- |
| 1 | Checklist maddelerini YAML/JSON olarak tanımla (`compliance/checklists/masak.yml`) |
| 2 | Django management command veya pytest plugin: `python manage.py compliance_check --profile masak` |
| 3 | CI pipeline: Haftalık (örn. Pazar gecesi) ve manual trigger; çıktı markdown + HTML rapor |
| 4 | Raporu S3/artefact olarak sakla, Slack kanalına özet gönder |

Checklist formatı örneği:

```yaml
- id: masak-kyc-001
  title: "KYC belgeleri eksiksiz"
  query: "accounts.CustomerDocument.objects.filter(status='missing').count() == 0"
  severity: high
  remediation: "Müşteri belgelerini tamamlayın"
- id: kvkk-retention-010
  title: "Retention politikası uygulanıyor"
  command: "python scripts/check_retention.py"
  severity: medium
```

CI job örneği:

```
  compliance:
    runs-on: ubuntu-latest
    schedule: weekly
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python manage.py compliance_check --profile masak --output build/masak_report.md
      - run: python manage.py compliance_check --profile kvkk --output build/kvkk_report.md
      - uses: actions/upload-artifact@v3
        with:
          name: masak-kvkk-reports
          path: build/
      - name: Slack notify
        run: ./scripts/notify_slack.sh build/summary.json
```

### 1.3 Rapor Çıktıları
- Markdown + HTML raporu:
  - Her madde için PASS/FAIL, gerekirse açıklama.
  - Hangi kayıtların düzeltme gerektirdiği (örn. eksik KYC müşterileri).
  - Son çalışma tarihi, pipeline id.
- Slack mesajı:

```
✅ MASAK checklist: 12/12 PASS
⚠️ KVKK checklist: 9/11 PASS
- kvkk-retention-010 (medium) → 3 kayıt limit dışı
```

---

## 2. Blockchain Audit Entegrasyon Testleri

### 2.1 Test Senaryoları
1. **Hash Doğrulama**
   - Muhasebe kaydı → hash oluştur → blockchain’e yaz.
   - API’den hash’i çek ve database’deki ile karşılaştır.
   - Beklenen: hash eşleşir, timestamp tutarlı.
2. **Senkronizasyon Testi**
   - Belirli zaman aralığında (örn. 24 saat) gönderilen kayıtlar zincire işlenmiş mi?
   - Eksik kayıt varsa uyarı.
3. **Rapor Üretimi**
   - Audit raporu (`audit/reports/blockchain_audit.py`) PDF/HTML olarak oluştur.
   - Rapor hash’lerini rapor un içine göm (audit trail).
4. **Hata Senaryosu**
   - Blockchain API down → retry mekanizması devreye giriyor mu?
   - Yanlış hash gönderimi → audit log’da alert.

### 2.2 Test Otomasyonu
- Pytest mark: `@pytest.mark.blockchain_audit`.
- Test fixture: mock blockchain (örn. Ganache, Hyperledger test net) veya sandbox endpoint.
- CI job: nightly veya manuel.
- Rapor çıktısı:
  - `build/blockchain_audit_report.json`
  - Slack özet: pass/fail, hatalı kayıtlar listesi.

### 2.3 Raporlama ve Dokümantasyon
- `docs/reports/compliance/` altında otomatik olarak raporların toplanması.
- Yetkili kullanıcılara e-posta ile rapor linki (Ops ve Compliance).
- Blockchain raporu için hash imzası (örn. rapor SHA256 → S3 metadata).

---

## 3. Yol Haritası

| Hafta | Görev |
| --- | --- |
| Hafta 1 | Checklist YAML formatı, MASAK maddeleri pilotu; blockchain test senaryoları listesi |
| Hafta 2 | `manage.py compliance_check` komutu, KVKK maddeleri, rapor template’leri |
| Hafta 3 | CI/CD entegrasyonu, Slack/Email bildirimleri, blockchain test otomasyonu |
| Hafta 4 | Dokümantasyon, rapor arşivi, compliance ekibi ile walkthrough |

---

**Hazırlayan:** GPT-5 Codex  

