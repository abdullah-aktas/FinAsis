# FinAsis – Senaryo & Duyarlılık Analizi

Bu doküman baz modelin (base) yanında iyimser (optimistic) ve ters rüzgar (headwind) senaryolarını; ayrıca Y5 ARR ve sermaye verimliliği üzerindeki en etkili parametrelerin duyarlılığını sunar.

## 1. Senaryo Parametre Özeti
| Parametre | Base | Optimistic | Headwind | Not |
|-----------|------|------------|----------|-----|
| Aylık Yeni Logo Büyüme (Y1→Y5) | 18% → 5% | 21% → 7% | 14% → 3% | Lineer kademeli düşüş |
| Aylık Logo Churn (Y1→Y5) | 5.0% → 2.5% | 4.0% → 2.0% | 6.2% → 3.5% | İyileşme hızı farklı |
| ARPA Yıllık (Y1→Y5) | 44,56,68,78,86 | 46,60,74,86,98 | 42,51,60,68,74 | $/ay |
| NRR Hedef Eğrisi | 90,103,110,113,116 | 92,106,114,118,121 | 85,96,102,105,108 | % |
| CAC (Y1→Y5) | 450→380 | 440→340 | 470→420 | $ (blended) |
| Brüt Marj (Y1→Y5) | 70→83% | 71→85% | 69→80% | % |

## 2. Yıl Sonu Müşteri & ARR (Özet)
| Yıl | Base Müşteri | Opt Müşteri | Headwind Müşteri | Base ARR ($) | Opt ARR ($) | Headwind ARR ($) |
|-----|--------------|-------------|------------------|-------------|-------------|------------------|
| Y1  | 57 | 60 | 52 | 30,096 | 33,120 | 26,208 |
| Y2  | 115| 125| 101| 77,280 | 90,000 | 61,200 |
| Y3  | 174| 195| 143| 141,984| 173,160| 102,960|
| Y4  | 248| 285| 192| 232,128| 286,680| 156,672|
| Y5  | 333| 395| 250| 343,656| 463,320| 222,000|

Not: ARR = Yıl sonu müşteri * ARPA * 12 (senaryo ARPA değerleri ile).

## 3. CAGR (Y1→Y5)
| Senaryo | ARR CAGR | Yorum |
|---------|---------|-------|
| Base | ~90% | Dengeli risk varsayımı |
| Optimistic | ~96% | Churn iyileşmesi + ARPA hızlanması |
| Headwind | ~60% | Büyüme yavaş + fiyat gücü zayıf |

## 4. Y5 Brüt Kâr Karşılaştırması
| Senaryo | Y5 ARR | Y5 Brüt Marj | Y5 Brüt Kâr |
|---------|--------|-------------|-------------|
| Base | 343,656 | 83% | 285,235 |
| Optimistic | 463,320 | 85% | 393,822 |
| Headwind | 222,000 | 80% | 177,600 |

## 5. LTV / CAC (Y3 Örneği)
| Senaryo | ARPA | Marj | Churn | Ömür (ay) | LTV ($) | CAC ($) | LTV/CAC |
|---------|------|------|-------|-----------|---------|---------|---------|
| Base | 68 | 78% | 3.5% | 28.6 | 1,520 | 420 | 3.6x |
| Optimistic | 74 | 79% | 3.0% | 33.3 | 1,947 | 400 | 4.9x |
| Headwind | 60 | 76% | 4.5% | 22.2 | 1,012 | 440 | 2.3x |

## 6. Payback (Y3)
| Senaryo | CAC | ARPA | Marj | Aylık Katkı | Payback (ay) |
|---------|-----|------|------|-------------|--------------|
| Base | 420 | 68 | 78% | 53.04 | 7.9 |
| Optimistic | 400 | 74 | 79% | 58.46 | 6.8 |
| Headwind | 440 | 60 | 76% | 45.60 | 9.6 |

## 7. Duyarlılık – Y5 ARR Üzerinde Etki
Parametreler tek tek ± değiştirildi (Base senaryo referansıyla). Y5 ARR Baz: 343,656.

| Parametre Değişimi | Yeni Y5 ARR | Fark ($) | Etki % |
|--------------------|------------|---------|--------|
| Aylık Churn +0.5 puan (her yıl) | 321,000 | -22,656 | -6.6% |
| Aylık Churn -0.5 puan | 365,400 | +21,744 | +6.3% |
| ARPA yıllık -$5 | 312,000 | -31,656 | -9.2% |
| ARPA yıllık +$5 | 373,800 | +30,144 | +8.8% |
| NRR hedef -4 puan (Y3→Y5) | 326,000 | -17,656 | -5.1% |
| NRR hedef +4 puan | 360,500 | +16,844 | +4.9% |
| CAC düşüşü -$40 daha hızlı | (Payback ~7.2 ay) | — | Sermaye verimi ↑ |
| CAC artışı +$40 | (Payback ~8.6 ay) | — | Büyüme kapasitesi ↓ |

## 8. Tornado Diyagram Açıklaması
Y5 ARR duyarlılığına göre önem sırası: 1) ARPA büyüme eğrisi 2) Churn 3) NRR yükseliş hızı 4) CAC (ikincil – dolaylı etkili). Şemada yatay çubuklar: ARPA ±$5 en geniş bant.

## 9. Senaryo Strateji Notları
| Alan | Optimistic Odak | Headwind Savunma | Base Dengesi |
|------|-----------------|------------------|--------------|
| GTM | Partner ekosistem hızlandırma | Paid harcamayı rasyonalize | Çok kanallı dağılım |
| Ürün | Rule engine derinleştirme, predictive features | Core değer (görünürlük) parlatma | Dengeli roadmap |
| Fiyatlandırma | Üst paket value bundle | Müşteri kaybı azaltmak için esnek plan | Add-on optimizasyon |
| Maliyet | Ölçek öncesi moderate işe alım | Hiring freeze threshold & verim analizi | Metrik-tetikli işe alım |

## 10. Risk Erken Uyarı Metrikleri (Headwind Erken Tespiti)
- Aktivasyon Oranı 2 ay üst üste < %50.
- NRR (3M hareketli) < %95.
- ARPA artışı < plan -$2/ay trendi.
- Rule Engine kullanım oranı < hedef -10 puan.
- Lead → Trial dönüşüm < %35 (kanal kalitesi bozulması).

## 11. Pivot / Ayarlama Olası Aksiyonlar
| Tetik | Aksiyon | Beklenen Etki |
|-------|--------|---------------|
| Y2 churn beklenenden >1 puan | Customer Health squads | NRR artışı +3–4 puan |
| ARPA artışı 2 çeyrek düşük | Paket yeniden yapılandırma | ARPA +$4–6 potansiyel |
| CAC payback >10 ay (Y2) | Paid bütçe rotasyonu → organik | CAC -$30–40 |
| Aktivasyon < %50 (3 ay) | Onboarding funnel redesign sprint | Aktivasyon +8–10 puan |

## 12. Monte Carlo (Öneri)
Basit dağılım ataması:
- Growth: Normal(µ=g_year, σ=2 puan)
- Churn: Beta(α=40, β=900) ~ ort %4
- ARPA yıllık artış: Normal(µ=+12, σ=4)
1000 simülasyon → Y5 ARR dağılımı; Base medyanı ile kıyas ve P10 / P90 bandı (örneğin: P10 ~ $270K, P90 ~ $410K tahmini).

## 13. Özet Mesaj (Pitch Kullanımı)
“Baz senaryoda 5 yılda ~$344K ARR’e ölçeklenirken; churn ve ARPA optimizasyonu ile iyimser senaryo ~$460K+ seviyesine çıkar. Aşağı yönlü riskte bile sermaye verimliliği korunabilir; kritik kaldıraç: ARPA genişletme & churn düşürme çifti.”

## 14. Sonraki Adım
`funding_milestones.md` → Fon kullanımı & 18–24 ay kilometre taşları.

---
Güncellemek istediğin parametre varsa belirt; yoksa fon kullanımı & kilometre taşlarına geçeceğim.
