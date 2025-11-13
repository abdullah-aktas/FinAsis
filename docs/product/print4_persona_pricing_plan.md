# Print 4 · Persona Bazlı Ürün Paketleri

Bu doküman FinAsis ürün paketlerini üç ana persona (Freemium, Professional, Enterprise) ve ilgili modüllerle eşleştirir. Amaç fiyatlandırmayı netleştirmek, onboarding ve upsell akışlarını kolaylaştırmaktır.

---

## 1. Persona Tanımları

| Persona | Hedef Kullanıcı | İhtiyaç | Not |
| --- | --- | --- | --- |
| **Freemium** | KOBİ giriş seviyesi, öğrenciler, start-up CFO’ları | Temel muhasebe, sınırlı raporlama, öğrenme içerikleri | Ücretsiz fakat kullanıcı/işlem limitli |
| **Professional** | Büyüyen KOBİ, mali müşavir, danışman | Gelişmiş rapor, uyumluluk araçları, AI destekli modüller | En popüler paket; aylık/ yıllık abonelik |
| **Enterprise** | Kurumsal finans ekipleri, holding CFO, çoklu şirket | Çoklu tenant, entegrasyon, blockchain audit, SLA | Özel fiyatlandırma, sözleşmeli |
| **Academy (Add-on)** | MEB / Edu kurumları, üniversiteler | FinAsis Academy, LMS, öğretmen/öğrenci içerikleri | Freemium + modüler ücretlendirme |

---

## 2. Modül & Rol Eşlemesi

### 2.1 Modul Envanteri

- **Finans & Muhasebe**: Genel muhasebe, e-fatura, ERP entegrasyonu, finansal KPI.
- **Uyumluluk & Audit**: MASAK/KVKK checklist, audit raporları, blockchain kanıtı.
- **Eğitim & Gamification**: LMS, öğretmen/öğrenci dashboard, oyun modülleri.
- **AI & Danışmanlık**: AI assistant, otomatik fiş önerisi, danışman modu.
- **Developer & Entegrasyon**: API key yönetimi, webhook, sandbox.

### 2.2 Paket Başına Modül Durumu

| Modül | Freemium | Professional | Enterprise | Academy Add-on |
| --- | --- | --- | --- | --- |
| Temel muhasebe & rapor | ✓ (ayda 100 belge) | ✓ (ayda 5.000 belge) | ✓ (sınırsız) | — |
| e-Fatura / e-Arşiv | — | ✓ | ✓ | — |
| Gelişmiş finans raporları (KPI, nakit akış) | — | ✓ | ✓ | — |
| Uyumluluk checklist & rapor | — | ✓ | ✓ (otomasyon + CI/CD) | — |
| Bölgesel vergi motoru | — | ✓ (TR/EU) | ✓ (TR/EU/US/APAC) | — |
| Blockchain audit | — | Add-on | ✓ |
| AI Assistant (voucher, rapor önerisi) | 50 sorgu/ay (öğrenme modu) | 500 sorgu/ay + rol script kütüphanesi | Sınırsız, özel model | 200 sorgu/ay sınıf bazlı |
| Prompt & Play görev motoru | Öğrenci görev paketi | CFO/Mali müşavir skriptleri | Kurumsal uyarlama | Öğretmen ders senaryoları |
| LMS / Gamification | ✓ (öğrenci) | ✓ (öğrenci+öğretmen) | ✓ (kurumsal) | ✓ (tam erişim) |
| Developer portal & API | Önizleme (read-only) | ✓ (1 key · 100 req/dk) | ✓ (sınırsız key · özel SLA) | Sandbox API (öğrenci) |
| Çoklu şirket/tenant | — | — | ✓ | Kurum/şube temelli |
| SLA / Dedicated success | — | Öncelikli (48s) | 4 saat, 7/24 | Eğitim danışmanı |

### 2.3 Rol Bazlı Yetkiler

| Rol | Freemium | Professional | Enterprise | Academy |
| --- | --- | --- | --- | --- |
| CFO / Finans yöneticisi | Dashboard + rapor (kısıtlı) | Tüm finans modülleri | Çoklu tenant, holding KPI | Eğitim paketleri üzerinden mentorluk |
| Muhasebeci / Mali müşavir | — | Muhasebe + uyumluluk | Audit + blockchain + global vergi | Eğitim modüllerinde canlı vaka |
| Öğretmen / Danışman | LMS öğretmen modu (kısıtlı) | LMS tam erişim + danışman raporları | Multi-organization eğitim & raporlama | Ana paket, görev motoru & ders scriptleri |
| Öğrenci / Stajyer | Öğrenme içerikleri | Profesyonel sandbox & oyun görevleri | Enterprise eğitim portalı | Sertifikalı kariyer rotaları |
| Geliştirici | — | API key (1 key) | SSO + sınırsız key + webhook test | Öğrenci API sandbox |
| Partner / ISV | — | — | Marketplace + gelir paylaşımı | Partner eğitim içerikleri |

---

## 3. Fiyatlandırma & Limitler

| Paket | Türkiye (TRY) | Avrupa (EUR) | ABD (USD) | Kullanıcı Limit | İşlem Limit | AI Kontenjan | Destek |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Freemium** | ₺0 | €0 | $0 | 3 kullanıcı | Aylık 100 belge | 50 sorgu | Topluluk + e-posta |
| **Professional** | ₺3.999 | €199 | $219 | 25 kullanıcı | Aylık 7.500 belge | 500 sorgu (ek paket: +250) | Öncelikli SLA (48s) |
| **Enterprise** | Teklif bazlı | Teklif bazlı | Teklif bazlı | Sınırsız | Sınırsız | Sınırsız / özel model | Dedicated CSM, 4 saat SLA |
| **Academy (kurum başına)** | ₺1.250 | €69 | $79 | 200 öğrenci + 20 eğitmen | Görev motoru sınırsız | 200 sorgu/sınıf | Eğitim danışmanı, aylık canlı oturum |

Notlar:
- Professional için yıllık abonelik 2 ay indirimli (TRY/EUR/USD fiyat × 10).
- Enterprise fiyatlandırması şirket büyüklüğü, entegrasyon sayısı ve SLA’ye göre teklif bazlı.
- Öğrenci/öğretmen kurumları için Freemium türevi “Education” planı (Freemium alt varyantı) oluşturulabilir.
- Döviz bazlı fiyatlar her çeyrek `regional_pricing.yml` üzerinden güncellenecek; vergi (KDV/VAT/Sales Tax) plan bazlı faturalamaya otomatik yansıyacak.

---

## 4. Upsell / Funnel Akışları

1. **Freemium → Professional**
   - Limit aşımı uyarıları (AI işlem, belge sayısı).
   - Uyumluluk modülü promosyonu (rapor otomasyonu).
   - Developer portal teaser (API key / entegrasyon örnekleri).
2. **Professional → Enterprise**
   - Çoklu şirket, audit + blockchain raporu ihtiyacı.
   - SLA gereksinimi (denetim, yatırımcı raporu).
   - Entegrasyon katmanı: ERP/CRM bağlamak için OIDC/SSO.

---

## 5. Uygulama Adımları

| Adım | Detay |
| --- | --- |
| 1 | Pricing sayfası (`templates/pricing.html`) yeni paket tablosuyla güncellenecek. |
| 2 | `billing` modülünde plan kodları (`FREEMIUM`, `PROFESSIONAL`, `ENTERPRISE`) ve limitler (config) eklenecek. |
| 3 | Onboarding wizard: persona soruları → plan önerisi. |
| 4 | Developer portal API limitleri `rate_limit_plan` ve bölgesel kota (TR/EU/US) ile eşleştirilecek. |
| 5 | CRM/marketing otomasyonuna paket bilgileri girilecek (HubSpot/Intercom). |
| 6 | Academy add-on için FinAsis Academy portalı (öğrenci/öğretmen akışı) canlıya alınacak. |

---

## 6. Açık Sorular

- Education planı Freemium’un varyantı mı yoksa ayrı paket mi?
- Enterprise için blockchain ve vergi motoru zorunlu mu yoksa add-on mu?
- Profesyonel paketteki AI limitleri artabilecek (optional add-on) mi?
- Academy paketindeki sertifikaların akreditasyon süreci nasıl yönetilecek?

---

**Hazırlayan:** GPT-5 Codex  

