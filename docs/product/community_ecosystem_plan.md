# Topluluk ve Ekosistem Planı

Bu doküman FinAsis Academy, geliştirici topluluğu ve partner entegrasyon marketi için hedefleri ve mimari yaklaşımı özetler.

---

## 1. FinAsis Academy

1. **Hedef Kitle:** Öğretmen, öğrenci, kurumsal öğrenme ekipleri.
2. **Modüller:**
   - Ders kütüphanesi ve rol bazlı prompt scriptleri (`ai_assistant/prompts/role_prompts.yml`).
   - Görev motoru entegrasyonu (ders → oyun → değerlendirme akışı).
   - Sertifikalı kariyer rotaları (FinTech Analist, Muhasebe Uzmanı, Oyunlaştırılmış Finans Koçu).
3. **Operasyon:**
   - Aylık canlı oturumlar (academy add-on kapsamında).
   - Eğitmen paneli: katılım ve görev tamamlanma raporları.

---

## 2. Developer Community

1. **Developer Hub:** `/resources/developer-hub/`
   - API kütüphanesi, örnek kod repository bağlantıları.
   - Webhook test konsolu ve Postman collection paylaşımları.
2. **Topluluk Etkinlikleri:**
   - Aylık webinar, quarterly hackathon (Academy ile entegre).
   - Forum / Discord kanalına yönlendirme.
3. **Ecosystem Metrics:**
   - Aktif API anahtarı, günlük çağrı, sandbox hata oranı.
   - Feature request takip: GitHub Discussions + roadmap.

---

## 3. Partner Marketplace

1. **Partner Tipleri:** ERP/CRM entegratörleri, vergi danışmanlık firmaları, e-dönüşüm sağlayıcıları.
2. **Onboarding Adımları:**
   - Partner başvuru formu + sözleşme.
   - API sandbox erişimi, test senaryosu doğrulaması.
   - Marketplace listing (logo, açıklama, fiyat).
3. **Gelir Modeli:**
   - SaaS gelir paylaşımı %15-25.
   - Co-selling komisyonu ve ortak kampanyalar.
4. **Teknik Gereksinimler:**
   - OAuth/Keycloak entegrasyonu (SSO).
   - Webhook olayları (invoice.created, payment.succeeded, audit.alert).

---

## 4. Yol Haritası

| Sprint | Hedef |
| --- | --- |
| Sprint 4 | Academy içerik altyapısı + görev motoru, developer hub sayfası |
| Sprint 5 | Partner marketplace MVP, entegrasyon başvuru süreci |
| Sprint 6 | Topluluk portalı, metrik panosu, co-selling raporları |

---

**Hazırlayan:** GPT-5 Codex  

