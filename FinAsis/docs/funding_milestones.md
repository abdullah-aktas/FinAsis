# FinAsis – Fon Kullanımı & 18–24 Ay Kilometre Taşları

Bu doküman pre-seed / melek yatırımı (baz: $400K, alternatif geniş: $600K) için fon dağılımı, 24 aylık stratejik kilometre taşları, metrik hedefleri ve sermaye disiplin prensiplerini içerir.

## 1. Raise Senaryosu
| Senaryo | Tutar (Net) | Amaç | Runway (Hedef) |
|---------|-------------|------|----------------|
| Base | $400K | MVP derinleştirme + aktivasyon + erken GTM çok kanallı temel | ~10 ay efektif + erken gelir uzatması |
| Extended | $600K | Ek ML / Veri, daha agresif GTM, uyumluluk hızlandırma | ~14–15 ay efektif |

Varsayım: Gelir katkısı Y1 sınırlı; Y2 başında ARR ivmesi burn’u kısmi dengeler.

## 2. Use of Funds (Allocation)
| Kalem | Base % | Base $ | Extended % | Extended $ | Not |
|------|--------|--------|------------|------------|-----|
| Ürün & Mühendislik | 38% | 152K | 36% | 216K | Entegrasyon & kural motoru |
| Veri & ML | 10% | 40K | 12% | 72K | Forecast & anomaly iyileştirme |
| GTM (Pazarlama + Satış) | 25% | 100K | 27% | 162K | İçerik + partner + erken paid |
| Güvenlik & Uyumluluk | 8% | 32K | 7% | 42K | Audit readiness |
| Operasyon / G&A | 9% | 36K | 8% | 48K | Finans, hukuk, araçlar |
| Rezerv / Buffer | 10% | 40K | 10% | 60K | 6 ay sonra re-forecast |

## 3. 24 Aylık Kilometre Taşları (Özet)
| Dönem | Ürün / Teknoloji | Müşteri & Pazar | Operasyon & Risk | Finansal Hedef |
|-------|------------------|-----------------|------------------|-----------------|
| 0–3 Ay | Core entegrasyon 5→8; temel anomaly MVP | 20 aktif müşteri pilot pipeline | Audit log tam kapsama | Aktivasyon ≥ %45 |
| 3–6 Ay | Rule engine v1, forecast iyileştirme | 40–45 aktif müşteri | Health score v1 | Aylık churn ≤ %5.2 |
| 6–9 Ay | Add-on API beta, rapor export | 70 aktif müşteri, ilk >$5K MRR eşiği | Support playbook | NRR (3M) ≥ %95 |
| 9–12 Ay | Anomaly precision > %85, rule template gallery | 90–100 aktif müşteri | Security review (external) | ARPA $50+ | 
| 12–15 Ay | API GA + billing, advanced forecasting | 150 aktif müşteri | CSM motion ölçek | NRR ≥ %102 |
| 15–18 Ay | Upsell paket bundle, usage-based limitler | 190–200 müşteri | Basic SOC kontrol seti | LTV/CAC >3.2x |
| 18–21 Ay | Segment bazlı fiyat optimizasyon | 230–240 müşteri | Data lifecycle policy | Payback <9 ay |
| 21–24 Ay | Predictive action önerileri (beta) | 300 müşteri yaklaşımı | Enterprise pilot 1–2 | NRR ≥ %108 |

## 4. Metrik Milestone Tablosu
| Metrik | Şu An (Vars.) | 6. Ay | 12. Ay | 18. Ay | 24. Ay |
|--------|---------------|-------|--------|--------|--------|
| Aktif Müşteri | 15 | 45 | 95 | 190 | 300 |
| ARR (Run-rate) | $0.03M | $0.06M | $0.09M | $0.18M | $0.32–0.34M |
| Aktivasyon Oranı | %0 (başlangıç) | %55 | %60 | %62 | %65 |
| Logo Churn (aylık) | %5 | %4.8 | %4.2 | %3.5 | %3.0 |
| NRR (3M) | – | %92 | %100 | %105 | %108+ |
| ARPA ($/ay) | 44 | 47 | 52 | 60 | 70+ |
| Rule Usage (Şirket %) | %10 | %30 | %50 | %62 | %70 |
| Payback (ay) | 14.6 | 12 | 10 | 8.5 | 7.5 |
| LTV/CAC | ~2.5x | 2.8x | 3.2x | 3.6x | 4.5x |

## 5. Sermaye Disiplini İlkeleri
1. Metric-Gated Hiring (her yeni FTE için MRR veya kullanım tetikleyici).
2. Expansion > Churn sağlanmadan agresif paid scale yok.
3. Buffer fonlar sadece: (a) güvenlik olayı, (b) churn spike, (c) GTM kanal pivot.
4. 6. ay Re-Forecast: Growth / Churn / ARPA vs plan.

## 6. Re-Forecast & Pivot Tetikleri
| Tetik | Eşik | Aksiyon |
|-------|------|---------|
| NRR < %95 (üst üste 2 ay) | Retention kırılması | CSM + onboarding sprint |
| Churn > plan +1 puan (3 ay) | Ürün değer boşluğu | Health score model detaylandır |
| ARPA artış sapması > -$3 (2 çeyrek) | Fiyat optimizasyon | Paket yeniden fiyatlama test |
| CAC payback >12 ay (Q4) | Kanal verimsiz | Paid downscale + organik yatırımı |
| Aktivasyon < %50 (3 ay) | Değer gecikmesi | Setup wizard revizyon |

## 7. Extended Raise Kullanım Farkı ($600K)
- Ek ML headcount 6. ay yerine 3. ay.
- Partner entegrasyon fonu (küçük bütçe) → kanal hızlandırma.
- Güvenlik / pen test yıllık yerine 2x.
- İç veri ambarı + event stream otomasyon erken.

## 8. Kritik Patika (Critical Path)
1. Entegrasyon sayısı & veri kalitesi → Aktivasyon.
2. Aktivasyon → Rule usage (NRR kaldıraç).
3. Rule usage + Add-on uptake → ARPA artışı.
4. ARPA + düşük churn → LTV/CAC & Payback iyileşmesi.
5. Sağlam birim ekonomi → Bir sonraki tur (Seed) için veri hikâyesi.

## 9. Seed Öncesi Hedef Paket (Investor Ready)
| Alan | Hedef |
|------|-------|
| ARR Run-rate | ≥ $300K |
| NRR | ≥ %108 |
| Churn (logo) | ≤ %3.5 |
| Payback | ≤ 8 ay |
| LTV/CAC | ≥ 4x |
| Aktivasyon | ≥ %60 |
| Rule Usage Penetrasyonu | ≥ %65 |

## 10. İletişim & Raporlama Ritmi
- Aylık Update: MRR köprüsü, churn nedenleri, aktivasyon funnel.
- Çeyreklik: NRR kohort, ARPA köprüsü, ürün roadmap ilerleme.
- Seed Prep (Ay 18–24): Data room denetimi, güvenlik raporu, müşteri referans paketleri.

## 11. Pitch Deck Slayt Önerisi (Bu Bölüm İçin)
1. “Use of Funds” (stacked bar + yüzdeler).
2. 24 Ay Milestone Timeline (roadmap şeridi).
3. Metrik Milestones Tablosu (highlight üç çekirdek KPI: NRR, Payback, ARR).
4. Critical Path Diyagramı (ok akışı: Entegrasyon → Aktivasyon → Rule Usage → ARPA → Birim Ekonomi → Seed).
5. Risk & Mitigasyon mini matris.

## 12. Özet Mesaj
“Fon, hızlı fakat disiplinli bir şekilde finansal görünürlük & otomasyon modülümüzü product-market fit sinyaline taşımak; NRR’ı %100+ eşiğine getirmek ve 18–24. ayda sermaye verimli büyüme kanıtıyla Seed turuna girmek için kullanılacaktır.”

## 13. Sonraki Adım
`dd_checklist_next_steps.md` → Data Room & due diligence gereksinimleri listesi.

---
Revizyon isteğin varsa belirt; aksi halde due diligence checklist aşamasına geçeceğim.
