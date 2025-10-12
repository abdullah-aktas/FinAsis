# FinAsis – Yatırımcı Sunumu Konuşma Notları (8–10 dk)

Slide 1 – Özet (0:30)
- Tek cümle: FinAsis, KOBİ ve ileri bireysel/küçük ekip yatırımcılar için finansal verileri (banka, e‑fatura/UBL‑TR, POS, e‑ticaret, aracı kurum, kripto) tekleştirip görünürlük, öngörü ve otomasyon sağlayan çoklu‑tenant SaaS’tır.
- Bugün (durum): Erken aşama; pilot/pipeline toplam ≈15 hesap. PayTR ödeme akışı sandbox’ta; rapor ekranları canlı. Hedef: sermaye verimli büyüme ve seed‑ready metrikler.

Slide 2 – Problem (0:45)
- Dağınık veri + manuel mutabakat → geciken kararlar, nakit akışında sürprizler.
- Yerel uyumluluk (EDOC/UBL‑TR, GİB akışları) ve audit hazırlığı iş yükü.
- Aksiyon üretmeyen “salt rapor” yaklaşımı; operasyon otomasyonu yok.

Slide 3 – Çözüm / Ürün (1:15)
- Modüller: Accounting & Finance raporları [Mevcut], AI Assistant (risk skoru, tahmin, öneri API’leri) [Mevcut/PoC], Rule Engine [Yol haritası 3–6 Ay], Education (FinEd), Games (FinGame), Blockchain tabanlı doğrulanabilir kayıt [Opsiyonel/PoC].
- Muhasebe Motoru: JSON `PostingRule` → denklikli `Voucher` üretimi (auto‑book önizleme) ile operasyonel otomasyon.
- EDOC/UBL‑TR: Şema doğrulama ve e‑belge akışları opsiyonel konfigürasyonla etkin.
- Demo akışı (runbook): kayıt → plan seçimi → ödeme (PayTR sandbox) → raporlar → AI/auto‑book önizleme.

Slide 4 – Pazar & ICP (0:45)
- ICP: 1–100 çalışan KOBİ’ler, ajanslar, e‑ticaret girişimleri, ileri bireysel/küçük ekip yatırımcılar.
- Alım tetikleyicileri: çok hesap/çok kanal, artan işlem hacmi, denetim gereksinimi, rapor karmaşıklığı.

Slide 5 – Fiyatlandırma & İş Modeli (0:45)
- Aylık paketler: Core $29 • Growth $59 • Scale $129.
- Add‑on: API/Webhook +$39, Gelişmiş Rapor +$19. Seat upsell/attach ile ARPA artışı. Yıllık ödeme indirimi ~%15.

Slide 6 – Metrikler: Bugün ve Hedefler (1:00)
- Bugün: ≈15 pilot/pipeline; rapor ekranları ve EDOC seçenekleri canlı/sandbox; demo akışı hazır.
- Hedefler (model): 6–12–18–24. ayda 45 → 95 → 190 → 300 aktif müşteri. ARR (run‑rate): Y1 $30K → Y3 $142K → Y5 $344K. ARPA: $44 → $68 → $86. NRR: %90 → %110+. Payback (Y3): ~7.9 ay. LTV/CAC (Y3): ~3.6x.

Slide 7 – Rekabet & Ayrışma (0:45)
- ERP modülleri vs: biz hafif kurulum + zengin entegrasyon + AI/Rule Engine ile aksiyon ve otomasyon sağlıyoruz.
- Tek‑özellikli araçlar vs: çok kaynaktan tek panele getirip rule engine/öneri ile değeri büyütüyoruz.
- Genel BI vs: sadece görselleştirme değil, muhasebe motoru + AI ile öneri/otomasyon katmanıyız.
- Ayrışan unsurlar: EDOC/UBL‑TR yerelleştirme, HMAC/IP doğrulama, audit log, blockchain opsiyonu, i18n.

Slide 7.1 – Somut Senaryolar (0:45)
- Senaryo 1 – Ajans (10 kişilik): Banka + e‑fatura + e‑ticaret bağlandı. Kural: “15 günden eski ve ödenmemiş faturalar → Slack uyarı + otomatik hatırlatma”. Sonuç: alacak tahsilat süresi kısalır, nakit akışı sürprizleri azalır. EDOC doğrulama ile e‑belge hataları erken yakalanır.
- Senaryo 2 – E‑ticaret KOBİ’si: POS + banka + pazaryeri bağlandı. AI: haftalık satış tahmini + stok/tedarik öneri uyarısı. Rule Engine: “iade oranı > %x → fiyat/ürün kontrol listesi”. Sonuç: fire ve stok maliyeti düşer, NRR’yi destekleyen kural kullanımı artar.

Slide 8 – GTM (0:45)
- Kanallar: içerik & SEO, partner/entegrasyon ekosistemi, kurucu‑led satış, topluluk/webinar; sınırlı ve disiplinli paid.
- Funnel hedefleri: Visit→Lead %3.5; Lead→Trial %40; Trial→Aktivasyon %55 (Y1) → %63 (Y3); Aktivasyon→Ücretli %60+.

Slide 9 – Teknoloji & Güvenlik (0:45)
- Backend: Django; çoklu dil/i18n; event/audit loglama.
- ML API’leri: risk skoru, finansal tahmin (Prophet), öneri; JWT/Session korumalı; Swagger/Redoc dokümantasyon.
- Güvenlik: HMAC/IP doğrulamalı callback, erişim kontrolleri; blockchain tabanlı doğrulanabilir kayıt opsiyonu.

Slide 10 – Yol Haritası (1:15)
- 0–3 Ay: 5→8 entegrasyon, anomaly MVP; 20 aktif pilot; Aktivasyon ≥ %45.
- 3–6 Ay: Rule Engine v1, forecast iyileştirme; 40–45 müşteri; churn ≤ %5.2.
- 6–9 Ay: Add‑on API beta, rapor export; 70 müşteri; ilk >$5K MRR; NRR (3M) ≥ %95.
- 9–12 Ay: Anomaly precision > %85, şablon galerisi; 90–100 müşteri; ARPA $50+.
- 12–18 Ay: API GA, advanced forecasting; 150→200 müşteri; NRR ≥ %102; LTV/CAC >3.2x.
- 18–24 Ay: Segment fiyat optimizasyonu; 230→300 müşteri; Payback < 9 ay; NRR ≥ %108.

Slide 11 – Finansal Özet (0:45)
- Müşteri yıl sonu: 57 → 115 → 174 → 248 → 333 (Y1→Y5). ARR (run‑rate): 30K → 77K → 142K → 232K → 344K.
- Brüt kâr (ARR baz): 21K → 57K → 111K → 187K → 285K. CAGR ~%90.
- Duyarlılık: ARPA ±$5 → Y5 ARR ~±%9; churn ±0.5 puan → ~±%6–7.
- Görseller: Deck’teki ARR ve NRR mermaid grafiklerini göster (11.1 bölümü) — trendi vurgula, sayılar modelden.

Slide 12 – Ekip (0:30)
- Çekirdek: Kurucu (Tech/Product). Metric‑gated işe alım: Backend, Full‑stack, Data/ML, Growth, SDR, CSM, PM, QA, Compliance (fractional).

Slide 13 – Yatırım & Kullanımı (0:45)
- Talep: Pre‑Seed $400K (alternatif $600K). Dağılım (400K): Ürün&Müh. %38, Veri&ML %10, GTM %25, Güvenlik %8, G&A %9, Rezerv %10. Runway ~8–10 ay (gelir katkısıyla uzar).

Slide 14 – Risk & Mitigasyon (0:30)
- Aktivasyon düşük → setup wizard & içerik revizyon; CSM playbook.
- Churn yüksek → health score + rule usage artırımı; segment bazlı paketler.
- CAC yükselişi → paid rotasyonu, organik/partner ağırlığı; kanal ROI takip.
- Güvenlik olayı → temel CIS kontrolleri + pen test; log & SIEM.

Slide 15 – Kapanış & CTA (0:30)
- Misyon: KOBİ’ler için görünürlük, öngörü ve otomasyonun erişilebilir hale getirilmesi.
- CTA: Demo & teknik inceleme; 18–24 ayda seed‑ready metrik paketine giden yolda birlikte ilerleyelim.

Notlar
- Demo: `docs/demo_senaryosu.md`
- Metrik tanımları: `docs/unit_economics_kpis.md`
- Finansal model: `docs/5_year_revenue_model.md` + `docs/financial_assumptions.md`
