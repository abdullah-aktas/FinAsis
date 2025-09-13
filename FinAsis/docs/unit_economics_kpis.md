# FinAsis – Birim Ekonomi & KPI Çerçevesi

Bu doküman yatırımcı sunumu ve iç yönetim için kritik metriklerin tanımları, formülleri, örnek hesapları, veri toplama yaklaşımı ve tetiklenen aksiyon kurallarını içerir. Temel amaç: Büyüme *ve* sermaye verimliliğini aynı anda optimize edebilecek ölçüm sistemini netleştirmek.

## 1. KPI Taksonomisi
| Kategori | Çekirdek KPI'lar | Yardımcı / Türetilmiş |
|----------|------------------|-----------------------|
| Büyüme | Yeni Logo MRR, Net MRR Growth | Expansion MRR, Contraction MRR |
| Müşteri Sağlığı | Aktivasyon Oranı, Health Score | Feature Adoption Rate, Rule Engine Usage |
| Monetizasyon | ARPA, NRR, Gross Retention | Add-on Attach Rate, Paket Mix Index |
| Kârlılık | Brüt Marj, LTV, CAC Payback | LTV/CAC, Capital Efficiency |
| Satış Verim | Magic Number, Pipeline Coverage | Win Rate %, Sales Cycle (gün) |
| Ürün Kullanımı | Aktif Oturum / Şirket, Entegrasyon Sayısı | Oturum başına event, Insight Tıklama Oranı |
| Operasyon | Deployment / Hafta, Hata Oranı | MTTR, Support Ticket / Müşteri |
| Risk / Uyum | Audit Log Coverage, PII Access Events | Exception Rate |

## 2. CAC (Customer Acquisition Cost)
Formül (Blended Basit): (Satış + Pazarlama Giderleri) / Yeni Ücretli Müşteri Adedi.

Varyantlar:
- Paid CAC: Yalnızca ücretli kampanya giderleri / Paid kaynaklı yeni müşteri.
- Fully Loaded CAC: (Satış + Pazarlama + Orantılı Ürün Destek + Araç Lisans payı) / Yeni müşteri.
- CAC Cohort Trend: Ay bazında 3M hareketli ortalama.

Örnek (Y2 Baz Varsayım):
- Aylık Satış + Pazarlama = $55K, Yeni müşteri = 50 → Blended CAC ≈ $1,100 (erken dönemde yüksek). Pipeline olgunlaştıkça Paid payı azalır.

## 3. LTV (Lifetime Value)
Basit Formül: LTV = ARPA * Brüt Marj * (1 / Aylık Logo Churn).
İyileştirilmiş (NRR Dahil) Yaklaşım: LTV ≈ (ARPA * Brüt Marj * (1 + Expansion Faktörü)) * Ortalama Ömür.
İskontolu Nakit (DCF) Yaklaşımı: LTV = Σ (Aylık Net Contribution_t / (1 + r)^t ). (r = aylık iskonto, örn. %1.2 ≈ yıllık %15).

Örnek (Y3): ARPA $68, Marj %78, Churn %3.5 → Ömür ≈ 28.6 ay → Basit LTV ≈ 68 * 0.78 * 28.6 ≈ $1,520.

## 4. Payback Süresi
Formül (Brüt Katkı Esaslı): Payback (ay) = CAC / (ARPA * Brüt Marj).
Genişletilmiş: CAC / (ARPA * Brüt Marj - Aylık Expansion Destek Maliyeti).
Örnek (Y3): 420 / (68 * 0.78) ≈ 7.9 ay.

## 5. Net Revenue Retention (NRR)
NRR = (Başlangıç MRR Cohort + Expansion - Contraction - Churned) / Başlangıç MRR Cohort.
Örnek (Ay Cohort): Başlangıç $10,000; Expansion $1,800; Contraction $300; Churned $700 → NRR = (10,000 + 1,800 - 300 - 700) / 10,000 = 108%.

## 6. Gross Revenue Retention (GRR)
GRR = (Başlangıç MRR - Contraction - Churned) / Başlangıç MRR (Expansion hariç). Örn: (10,000 - 300 - 700)/10,000 = %90.

## 7. ARPA Köprüsü (Decomposition)
ARPA_t = Fiyat * Paket Mix Katsayısı * (1 - Ortalama İndirim) + Add-on Gelir / Müşteri + Ek Kullanıcı Upsell.

Örnek Y3 Köprüsü (varsayımsal):
- Y2 ARPA: $56
- Mix Etkisi: +$5 (Scale payı artışı)
- Add-on Uptake: +$3
- Ek Kullanıcı: +$2
- İndirim Disiplini / Yıllık Ödeme Net Etkisi: +$2
= Yeni ARPA ≈ $68.

## 8. Magic Number (Satış Verimi)
Magic Number = (Çeyrek MRR Artışı * 4) / Önceki Çeyrek Satış & Pazarlama Gideri.
Örn: Q Artışı $8K MRR, Önceki S&M $70K → (8K*4)/70K = 0.46 (Henüz verimli değil). Hedef: >0.7 Y2 sonu, >1.0 Y3.

## 9. Capital Efficiency
Formül: Capital Efficiency = ARR / (Kümülatif Harcanan Sermaye). Erken aşamada <1 normal; Series A öncesi 1–1.5 iyi sinyal.

## 10. Health Score (Öneri Modeli)
Ağırlıklı Bileşenler (0–100 puan):
| Boyut | Ağırlık | Alt Metrik | Tanım |
|-------|---------|-----------|-------|
| Entegrasyon Derinliği | 20 | Aktif entegrasyon sayısı normalize | ≥4 entegrasyon tam puan |
| Kullanım Frekansı | 20 | Haftalık aktif gün | ≥4 gün tam |
| Özellik Çeşitliliği | 10 | Kullanılan modül sayısı | ≥3 modül |
| Kural / Otomasyon | 15 | Çalışan kural / hafta | ≥5 |
| Öngörü Değeri | 10 | Forecast view / ay | ≥4 |
| Destek Sinyali | 10 | Negatif ticket oranı | Düşük oran yüksek puan |
| Finansal Sağlık | 10 | Ödeme gecikmesi / risk | Düşük gecikme |
| Expansion Potansiyeli | 5 | Kullanıcı doygunluk oranı | ≥80% kapasite |
Skor <50  churn risk uyarısı, 50–70 izleme, >70 sağlıklı.

## 11. Rule Engine Usage Rate
Formül: Aktif Kurallı Şirket Sayısı / Toplam Aktif Şirket.
Derinlik: Ortalama aktif kural adedi / Şirket.
Hedefler: Y1 Sonu ≥30%, Y2 ≥55%, Y3 ≥70%. Bu oran NRR ile güçlü korelasyon beklenir.

## 12. Aktivasyon Tanımı
“Aktif” saymak için:
1. ≥2 veri entegrasyonu bağlandı.
2. İlk dashboard ziyareti tamamlandı.
3. En az 1 kural veya anomaly insight görüntülendi.
Bu üç adımı ≤14 gün içinde tamamlayanların Aktivasyon Oranı = (Aktive Edilenler / Trial Başlangıcı).

## 13. Dashboard Mimari Önerisi
Paneller:
- Executive: ARR, NRR, Yeni Logo MRR, Expansion MRR, Payback, Magic Number.
- Growth: Funnel (Visit→Lead→Trial→Aktivasyon→Ücretli), CAC kırılımı.
- Customer Health: Health Score dağılımı, Kural kullanım ısı haritası.
- Product: Entegrasyon adoption, özellik tıklama cohort.
- Finance: Brüt Marj trend, COGS bileşen yüzdeleri.
- Risk & Uyum: PII access anomalileri, audit log kapsam oranı.

## 14. Alarm / Tetik Seviyeleri (Örnek Otomasyon Kuralları)
| KPI | Eşik | Aksiyon |
|-----|------|---------|
| NRR (3M hareketli) | < %95 | Churn kök neden analizi, top 10 riskli hesap review |
| Logo Churn (aylık) | > %6 | Sağlık skor <50 olan hesaplara CSM outreach |
| Aktivasyon Oranı | < %50 | Onboarding e-postaları A/B, içerik revizyon |
| Magic Number | <0.4 (Y2) | Paid spend dondur, organik optimizasyon |
| Payback | >12 ay (Y3) | Fiyatlandırma / upsell bundle denemesi |
| Rule Engine Usage | < %25 (Y1 Q4) | Kural şablon galerisi lansmanı |

## 15. Veri Toplama & Enstrümantasyon
Olay (event) Sözlüğü Örnekleri:
- integration_connected {type, time_to_connect}
- rule_created {rule_type}
- rule_fired {severity, outcome}
- forecast_viewed {horizon_days}
- insight_clicked {category}
- dashboard_visit {section}
- subscription_plan_changed {from, to}
- seat_added {count}
- addon_enabled {addon_type}

Teknik Öneri: Olay kuyruğu → stream processor (ör. Kafka / Redis Stream) → OLAP (DuckDB / ClickHouse) → Metabase / Superset dashboard.

## 16. Kohort İzleme (Örnek Template)
| Cohort (Başlangıç Ayı) | Başlangıç MRR | Ay1 | Ay2 | Ay3 | Ay6 | Ay12 | NRR (%) | Not |
|------------------------|---------------|-----|-----|-----|-----|------|--------|-----|
| 2025-01 | 5,000 | 5,200 | 5,350 | 5,400 | 5,650 | 5,900 | 118 | Sağlam expansion |
| 2025-02 | 4,200 | 4,150 | 4,050 | 4,000 | 3,950 | 3,800 | 90 | Churn riski |

## 17. Örnek Pseudo-Kod – NRR Hesabı
```python
def monthly_nrr(start_mrr, expansion, contraction, churned):
    return (start_mrr + expansion - contraction - churned) / start_mrr

cohort = {'start':10000,'expansion':1800,'contraction':300,'churned':700}
nrr = monthly_nrr(**cohort)  # 1.08 → %108
```

## 18. KPI Öncelik Matrisine Göre Odak (Y1–Y2)
| Dönem | Primer | Sekonder | Neden |
|-------|--------|----------|-------|
| Y1 H1 | Aktivasyon | ARPA Stabilizasyon | Ürün değer doğrulaması |
| Y1 H2 | Churn Azaltma | Rule Usage | Retention tabanı |
| Y2 H1 | Expansion | CAC Verim | NRR > %100 eşiği |
| Y2 H2 | Capital Efficiency | Magic Number | Seri A hazırlığı |

## 19. Capital Efficiency Sinyali (Örnek)
Y5 hedef: ARR $344K, kümülatif harcama $1.2M → 0.29 (erken). Seri A sonrası hedef 1.0+ için hızlandırılmış ARR büyümesi gerekir (fiyat optimizasyonu + enterprise add-on).

## 20. Uygulanacak Kısa Aksiyon Backlog (Metrik Toplama)
| Öncelik | Aksiyon | Çıktı |
|---------|--------|-------|
| P0 | Event şeması YAML taslağı | Tutarlı isimlendirme |
| P0 | Olay yayın middleware (Django signal hook) | Entegre logging |
| P1 | Basit ETL → DuckDB batch | Günlük güncelleme |
| P1 | Health Score cron job | Risk listesi |
| P2 | NRR kohort tablosu script | Aylık rapor |
| P2 | KPI alert rules (celery) | Otomatik uyarı |

## 21. Yatırımcı Sunumunda Kullanılacak KPI Slide Önerisi
1. NRR Trend (çizgi) + Referans Benchmark.
2. ARPA Köprüsü (Waterfall).
3. Payback & LTV/CAC dönüm noktaları (milestone tracker).
4. Aktivasyon → Rule Usage korelasyonu (scatter).
5. Health Score dağılımı (violin / box). 

## 22. Sonraki Adımlar
1. Senaryo & Duyarlılık Analizi (optimistic / base / headwind parametre tabloları).
2. Fon Kullanımı & Kilometre Taşları (18–24 ay plan).
3. DD Checklist (Data Room gereksinimleri).

---
Revizyon veya eklemek istediğin başka bir KPI var mı? Belirtirsen güncellerim; yoksa senaryo & duyarlılık analizine geçeceğim.
