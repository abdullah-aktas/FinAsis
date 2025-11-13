# Globalleşme Hazırlık Planı

Bu belge FinAsis platformunun çoklu dil, bölgesel fiyatlandırma, vergi uyumluluğu ve yerel regülasyon süreçlerine hazırlanması için Sprint 4-5 arasında uygulanacak adımları özetler.

---

## 1. Dil ve Yerelleştirme

1. **Dil Desteği Genişletme**
   - Dil listesi: Türkçe (varsayılan), İngilizce, Almanca, İspanyolca, Arapça.
   - `LANGUAGES` ayarı genişletildi; `locale/<lang>/LC_MESSAGES` dizinleri oluşturulacak.
   - Crowdin/Transifex entegrasyonu ile UI çevirileri version control’e bağlanacak.

2. **İçerik Ayrıştırma**
   - Statik sayfalar ve e-posta şablonları `django-parler`/`django-modeltranslation` ile çoklu dil desteğine hazırlanacak.
   - Eğitim içerikleri (Academy) için `content_locale` alanı eklenecek; ders planları YAML üzerinde dil etiketi taşıyacak.

3. **Tarih / Para Biçimi**
   - `babel` kütüphanesi ile tarih, sayı, para formatı locale bazlı biçimlendirilecek.
   - Kullanıcı profiline `preferred_locale` alanı eklenerek dashboard otomatik çevrilecek.

---

## 2. Bölgesel Fiyatlandırma ve Vergi Motoru

| Bölge | Para Birimi | Temel Vergi | Not |
| --- | --- | --- | --- |
| Türkiye | TRY | KDV %18 | e-Fatura zorunluluğu |
| Avrupa Birliği | EUR | KDV ülke bazlı | OSS raporlama |
| Amerika | USD | Sales Tax eyalet bazlı | Avalara benzeri servis entegrasyonu |
| APAC (pilot) | SGD | GST %8 | Oyuncu modülü için limitli erişim |

1. **Konfigürasyon**
   - `REGIONAL_PRICING` sözlüğü ile varsayılan fiyat + vergi oranı tanımlandı (bkz. `config/settings/base.py`).
   - `FINASIS_SUPPORTED_REGIONS` env değişkeni ile canlı ortamda etkin bölgeler kontrol edilecek.

2. **Faturalama**
   - `billing` uygulamasına bölge/birim alanları eklenir, Stripe / Iyzico / Paddle gibi gateway’ler için para birimi otomasyonu.
   - Vergi hesaplaması için `tax_engine` servisi (`VAT`, `Sales Tax`, `GST`) oluşturulacak; check adjudication audit log’a yazılacak.

3. **UX**
   - Pricing sayfasında TRY/EUR/USD fiyatlar sergilendi.
   - Kur çevirisi haftalık olarak `regional_pricing.yml` dosyasından güncellenecek (CI pipeline trigger).

---

## 3. Regülasyon Checklist’leri

Yeni checklist dosyaları:

| Dosya | Kapsam | Örnek Kontroller |
| --- | --- | --- |
| `compliance/checklists/eu_gdpr.yml` | GDPR veri koruma | DPO ataması, `DATA_ENCRYPTION_KEY` ayarı, silme süresi |
| `compliance/checklists/us_finreg.yml` | FinCEN/AML | OFAC kontrolü, KYC kayıt süresi |

`manage.py compliance_check --profile eu_gdpr` komutu ile bölge bazlı denetim yapılabilir.

---

## 4. Operasyonel Hazırlık

1. **Destek Kanalları**
   - Çok dilli bilgi bankası; Zendesk/Intercom makale seti dil bazlı çoğaltılacak.
   - SLA’ler bölge bazlı (TR/EU: 48s, US/APAC: 24s).

2. **Veri Yerelleştirme**
   - EU müşterileri için Frankfurt / Amsterdam veri merkezi (GCP).
   - ABD için Virginia (multi-region) ve veri aktarım logu.

3. **Raporlama**
   - BI katmanında bölgesel gelir, churn, uyumluluk raporu.
   - OKR: Yeni bölgede 90 gün içinde NPS ≥ 8, churn ≤ %3.

---

## 5. Yol Haritası

| Sprint | Teslim | Not |
| --- | --- | --- |
| Sprint 4 | Dil/para ayarlarının altyapısı, checklist’lerin entegrasyonu | Çeviri dosyaları placeholder |
| Sprint 5 | Fiyatlandırma motoru, vergi hesaplayıcı, bölgesel planlar | Stripe / yerel ödeme sağlayıcı POC |
| Sprint 6 | GCP bölge dağıtımı, destek ve operasyon süreçleri | SLA & runbook’lar, monitoring (Prometheus) |

---

**Hazırlayan:** GPT-5 Codex  

