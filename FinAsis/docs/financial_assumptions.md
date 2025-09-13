# FinAsis – Finansal Yönetim Platformu

Bu doküman 5 yıllık gelir modeli oluşturulmadan önce kullanılacak baz finansal varsayımları içerir. Varsayımlar; Melek / Pre-Seed yatırımcı sunumu için şeffaf, izahı yapılabilir ve duyarlılık analizine uygun şekilde yapılandırılmıştır.

## 1. Ürün Konumlandırması (Scope)
FinAsis: KOBİ ve ileri bireysel / küçük ekip yatırımcıların finansal verilerini (banka, fatura, POS, e-ticaret, aracı kurum, kripto) tekleştiren; nakit akışı öngörüsü, gider analizi, anomali tespiti ve kural bazlı uyarılar sunan çoklu-tenant SaaS finansal yönetim platformu.

Odak: Finansal görünürlük + öngörü + otomasyon. (Genel şirket yönetimi modülleri bu modelde yer almıyor.)

## 2. Fiyatlandırma Katmanları (USD baz – lokal pazara göre TL çevrimi ayrıca yapılabilir)
| Paket | İçerik (Özet) | Aylık Liste Fiyatı | Dahil Kullanıcı | Ek Kullanıcı Paketi |
|-------|---------------|--------------------|-----------------|---------------------|
| Core  | Entegrasyon (sınırlı), dashboard, temel rapor | $29 | 3 | 10 ek kullanıcı +$12/mo |
| Growth| Core + nakit forecast + anomaly + kural motoru (limitli) | $59 | 8 | 10 ek kullanıcı +$18/mo |
| Scale | Growth + gelişmiş anomaly, sınırsız kural, gelişmiş veri dışa aktarma, SLA | $129 | 15 | 10 ek kullanıcı +$25/mo |
| Add-on: API/Webhook | Genişletilmiş rate limit & event push | +$39 | – | – |
| Add-on: Gelişmiş Rapor & Audit Export | Denetim hazır PDF/XBRL seti | +$19 | – | – |

Not: Yıllık peşin ödeme indirimi varsayımı: -%15 (modelde ARPA etkisi yıllık ödemelerin Y2 sonrası %20 penetrasyonuyla dengelenir).

## 3. Müşteri Büyüme ve Churn Varsayımları
Başlangıç aktif logolu müşteri (Ay 1 sonu): 15

| Yıl | Ortalama Aylık Yeni Logo Büyümesi (ay/ay %) | Aylık Logo Churn % | Gerekçe |
|-----|---------------------------------------------|--------------------|---------|
| Y1  | %18 (erken momentum + küçük taban)          | %5.0 | MVP / onboarding sürtünmesi yüksek |
| Y2  | %10                                         | %4.0 | Ürün olgunlaşması, destek iyileşmesi |
| Y3  | %7                                          | %3.5 | Daha iyi segmentasyon / eğitim |
| Y4  | %6                                          | %3.0 | Enterprise-vari özellikler, sticker value artışı |
| Y5  | %5                                          | %2.5 | Kurumsal kontrat + yıllık ödeme artışı |

Logo churn aylık bazda; yıllık elde tutma ~ (1 - aylık_churn)^12 formülüyle türetilecek.

## 4. Paket Miks Evrimi
| Zaman | Core | Growth | Scale | Not |
|-------|------|--------|-------|-----|
| Başlangıç (Ay1) | %70 | %25 | %5 | Basit görünürlük ihtiyacı baskın |
| Y1 Sonu | %58 | %32 | %10 | Forecast + anomaly kabulü |
| Y2 Sonu | %50 | %36 | %14 | Kural motoru değeri kanıt |
| Y3 Sonu | %44 | %38 | %18 | Üst paket upsell süreçleşmiş |
| Y4 Sonu | %42 | %38 | %20 | Scale kararlılığı |
| Y5 Sonu | %40 | %40 | %20 | Dengeli karışım |

## 5. Add-on (Attach Rate) Varsayımları
| Add-on | Y1 | Y2 | Y3 | Y4 | Y5 | Not |
|--------|----|----|----|----|----|-----|
| API/Webhook | %5 | %9 | %14 | %18 | %22 | Daha büyük & otomasyon odaklı müşteriler |
| Gelişmiş Rapor | %6 | %11 | %16 | %20 | %25 | Denetim / yatırımcı raporlama talepleri |

Attach rate = ilgili yılda toplam logolu müşterilerin yüzdesi.

## 6. ARPA (Aylık Ortalama Paket Geliri) Türetimi
Formül (baz): Sum(Paket Fiyatı * Miks) * (1 - ortalama indirim) + Add-on katkısı + Kullanıcı paketi upsell etkisi.

Varsayılan ek kullanıcı upsell etkisi (paket başına ortalama):
| Yıl | Core | Growth | Scale |
|-----|------|--------|-------|
| Y1  | +%4  | +%7    | +%10  |
| Y3+ | +%6  | +%10   | +%14  |
(Y2 geçiş yılı lineer interpolasyon.)

Model Sonucu (tahmini; kesinleşmez):
| Yıl | Ortalama ARPA (USD/ay) | Not |
|-----|-------------------------|-----|
| Y1  | $44 | Küçük taban, düşük attach |
| Y2  | $56 | Paket miks kayması + add-on artışı |
| Y3  | $68 | Scale payı & API uptake |
| Y4  | $78 | Rapor + kullanıcı upsell |
| Y5  | $86 | Attach doygunluğa yaklaşır |

## 7. Gelir Bileşenleri Ayrımı (MRR Köprüsü Mantığı)
MRR_t = MRR_(t-1) + Yeni Logo MRR + Expansion (upsell + add-on) - Contraction (downsell / paket düşüşü) - Churned MRR.

Varsayılan oranlar (MRR yüzdesi olarak):
| Yıl | Yeni Logo | Expansion | Contraction | Churned |
|-----|-----------|----------|-------------|---------|
| Y1  | %55 | %8  | %2  | %35 |
| Y2  | %40 | %15 | %2  | %27 |
| Y3  | %32 | %22 | %2  | %24 |
| Y4  | %28 | %25 | %3  | %20 |
| Y5  | %24 | %28 | %3  | %18 |

Expansion > Churn’e geçtiği nokta ≈ Y2 sonu → Net Revenue Retention > 100%.

## 8. Net Revenue Retention (NRR) Eğrisi (Hedef)
| Yıl | NRR Hedef |
|-----|-----------|
| Y1  | %88–92 |
| Y2  | %100–105 |
| Y3  | %108–112 |
| Y4  | %112–115 |
| Y5  | %115–118 |

## 9. Brüt Marj Varsayımları
Brüt Marj = (Gelir - COGS) / Gelir.
COGS bileşenleri: Hosting (bulut), entegrasyon API çağrı maliyetleri, veri depolama, temel destek (L1), loglama / izleme SaaS maliyetleri.

| Yıl | Brüt Marj | Not |
|-----|-----------|-----|
| Y1  | %70 | Düşük ölçek, verimsiz kaynak kullanımı |
| Y2  | %74 | Çoklu tenant optimizasyonu |
| Y3  | %78 | Ölçek ekonomisi + rezerve instance |
| Y4  | %81 | API maliyet pazarlığı |
| Y5  | %83 | Otomasyon & veri yaşam döngüsü yönetimi |

## 10. Müşteri Edinimi (Funnel Varsayımları)
| Aşama | Oran (Y1) | İyileşme Trend |
|-------|-----------|----------------|
| Web Ziyaret → Lead | %3.5 | Y3: %4.2 (içerik & SEO) |
| Lead → Trial Signup | %40 | Y3: %45 |
| Trial → Aktivasyon (≥2 entegrasyon) | %55 | Y3: %63 |
| Aktivasyon → Ücretli Dönüşüm | %60 | Y3: %65 |

Örnek Y1 baş: 10,000 aylık ziyaret → 350 lead → 140 trial → 77 aktivasyon → 46 ücretli.

## 11. CAC Bileşenleri (Başlangıç ~450$)
| Kanal | Pay | Not |
|-------|-----|-----|
| İçerik & SEO | %20 | Zaman gecikmeli etkili |
| Performans Reklam | %25 | Erken hız için |
| Partner / Ajans | %15 | Rev pay / komisyon |
| Topluluk / Organik | %10 | Düşük maliyet |
| Kurucu-led Direkt | %20 | İlk satış, ilişki |
| Webinar / Event | %10 | Pipeline hızlandırıcı |

Verimlilik ile Y5 blended CAC ≈ 380$ hedef.

## 12. LTV Varsayım Mantığı
Basit: LTV = ARPA * Brüt Marj * Ortalama Müşteri Ömrü (ay). Ortalama ömür ≈ 1 / aylık_churn.
Ör: Y3: ARPA $68, Brüt Marj %78, Churn %3.5 → Ömür ~28.6 ay → LTV ≈ 68 * 0.78 * 28.6 ≈ $1,520.
Y3’te CAC ~420$ varsayılırsa LTV/CAC ≈ 3.6x (hedef >3 iyi seviye).

## 13. Payback Süresi
Payback (ay) ≈ CAC / (ARPA * Brüt Marj).
Y1: 450 / (44 * 0.70) ≈ 14.6 ay (erken.
Y2: 430 / (56 * 0.74) ≈ 10.4 ay.
Y3: 420 / (68 * 0.78) ≈ 7.9 ay.
Hedef: Y3 sonrası <9 ay sürdürülebilir ölçek.

## 14. Duyarlılık (Kritik Parametreler)
- Aylık Logo Churn ±1 puan → Y5 ARR’de ≈ %6–8 etki.
- Expansion oranı -5 puan → NRR Y5’te %110 altına düşebilir.
- CAC +$50 kalırsa payback ~+0.8–1.1 ay uzar.
- ARPA büyümesi her yıl 5$ düşük gerçekleşirse Y5 ARR’de ~-%9–10 etki.

## 15. İzlenecek İlk 10 KPI
1. Yeni Logo MRR
2. Expansion MRR (Add-on + paket upgrade)
3. Churned MRR
4. Net MRR Growth Rate
5. NRR (kohort bazlı)
6. ARPA / ARPU
7. Aylık Logo Churn
8. Aktivasyon Oranı (≥2 entegrasyon)
9. CAC Payback (yuvarlanan 3 aylık)
10. Brüt Marj

## 16. Veri Kaynakları & Varsayım Notları
- Fiyat yapısı: Benzer erken aşama finans visibility SaaS benchmark karışımı.
- Churn ve NRR: SMB finansal araç benchmark + moderate ürün stickiness.
- CAC: Erken dönemde kurucu-led satış + düşük ölçekli paid acquisition kombosu.
- Brüt marj: Çoklu-tenant + hafif compute yoğunluklu ML tahmini.

## 17. Sonraki Adım
Bu varsayımlar onaylanmış kabul edilerek bir sonraki doküman: `5_year_revenue_model.md` → Yıllık / kümülatif müşteri, MRR, ARR, brüt kâr, NRR gelişimi.

---
Revizyon için: Değiştirilmesini istediğin metrik varsa (ör: başlangıç müşteri, churn, fiyat) belirt; modele yansıtayım.
