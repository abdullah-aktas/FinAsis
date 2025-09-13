# FinAsis – 5 Yıllık Gelir Modeli (Baz Senaryo)

Bu doküman `financial_assumptions.md` içindeki varsayımlara dayanarak 60 aylık (özetlenmiş yıllık) müşteri ve gelir projeksiyonunu sunar. Amaç: Melek / Pre-Seed yatırım sunumunda ARR ölçeklenme potansiyelini, brüt kâr gelişimini ve temel büyüme dinamiklerini açık göstermek.

## 1. Kullanılan Ana Varsayımlar (Özet Referans)
- Başlangıç müşteri: 15 (Ay1 sonu)
- Aylık net yeni logo büyümesi ve churn (yıla göre sabit):
  - Y1: Growth %18 – Churn %5 → Net çarpan 1.13
  - Y2: %10 – %4 → 1.06
  - Y3: %7 – %3.5 → 1.035
  - Y4: %6 – %3 → 1.03
  - Y5: %5 – %2.5 → 1.025
- Yıllık ARPA: Y1 $44, Y2 $56, Y3 $68, Y4 $78, Y5 $86
- Brüt marj: %70, %74, %78, %81, %83
- NRR hedefleri: %90, %103, %110, %113, %116 (yaklaşık mid-point)

Not: Aylık modelde her yıl için tek bir “net logo çarpanı” (1 + growth - churn) varsayılarak geometrik artış hesaplandı.

## 2. Müşteri Projeksiyonu (Yıl Sonu & Ortalama)
| Yıl | Yıl Başı Müşteri | Yıl Sonu Müşteri | Ortalama (≈ (Baş+Son)/2) | Yıllık Net Yeni (Son - Baş) |
|-----|------------------|------------------|---------------------------|----------------------------|
| Y1  | 15   | 57   | 36   | 42 |
| Y2  | 57   | 115  | 86   | 58 |
| Y3  | 115  | 174  | 145  | 59 |
| Y4  | 174  | 248  | 211  | 74 |
| Y5  | 248  | 333  | 291  | 85 |

Açıklama: Müşteri sayısı yıl içi aylık geometrik büyümeden türetilmiştir: C_end = C_start * (net_faktör)^{12} (Y1 ilk yıl için 11 efektif dönem kabul edilmiştir çünkü başlangıç değeri ay1 sonunu temsil eder).

## 3. MRR ve ARR (Run-Rate Yaklaşımı)
Run-rate ARR = (Yıl sonu müşteri * Yıl ARPA) * 12

| Yıl | Yıl Sonu Müşteri | ARPA ($/ay) | Yıl Sonu MRR ($) | Run-Rate ARR ($) |
|-----|------------------|------------|------------------|------------------|
| Y1  | 57  | 44 | 2,508  | 30,096 |
| Y2  | 115 | 56 | 6,440  | 77,280 |
| Y3  | 174 | 68 | 11,832 | 141,984 |
| Y4  | 248 | 78 | 19,344 | 232,128 |
| Y5  | 333 | 86 | 28,638 | 343,656 |

Toplam ARR CAGR (Y1 → Y5): ≈ 90% (basit CAGR hesap: (343,656 / 30,096)^(1/4) - 1 ≈ 0.90).

## 4. Brüt Kâr Projeksiyonu
| Yıl | Run-Rate ARR ($) | Brüt Marj | Brüt Kâr ARR ($) |
|-----|------------------|-----------|------------------|
| Y1  | 30,096  | 70% | 21,067 |
| Y2  | 77,280  | 74% | 57,187 |
| Y3  | 141,984 | 78% | 110,748 |
| Y4  | 232,128 | 81% | 187,024 |
| Y5  | 343,656 | 83% | 285,235 |

## 5. MRR Büyüme Köprüsü (Konseptüel Ayrım)
Yıllık MRR artışı; Yeni Logo, Expansion, Churn (kaybolan) ve Contraction (paket düşüşü) bileşenleriyle açıklanır. Aşağıdaki tablo yüzdeler `financial_assumptions.md` içindeki dağılımların konsept adaptasyonudur ve yıl sonu MRR artışının kompozisyonel anlatımı içindir (muhasebe eşleştirme değil, yatırımcı iletişim çerçevesi):

| Yıl | Yeni Logo Payı | Expansion Payı | Churn Etkisi | Contraction | Net Pay (≈) | Özet Mesaj |
|-----|----------------|----------------|-------------|-------------|------------|------------|
| Y1  | Yüksek (~55%)  | Düşük (~8%)    | -35%        | -2%         | ~26%       | Yeni müşteri ağırlıklı erken ivme |
| Y2  | Orta (40%)     | Artan (15%)    | -27%        | -2%         | ~26%       | Expansion ivmesi churn’ü dengelemeye başlar |
| Y3  | 32%            | 22%            | -24%        | -2%         | ~28%       | Expansion > churn kalıcı |
| Y4  | 28%            | 25%            | -20%        | -3%         | ~30%       | Üst paket + add-on istikrar |
| Y5  | 24%            | 28%            | -18%        | -3%         | ~31%       | Expansion ana büyüme motoru |

Not: Bu yüzdeler yıllık MRR büyümesinin parçalanmış iletişimidir; kesin muhasebe kalemleri için detaylı aylık kohort tablosu gereklidir.

## 6. NRR (Net Revenue Retention) Hedef İzlemesi
| Yıl | NRR Hedef | Yorum |
|-----|-----------|-------|
| Y1  | %90  | Ürün adaptasyon & churn baskısı |
| Y2  | %103 | Expansion churn’ü nötrlüyor |
| Y3  | %110 | Add-on ve üst paket oturması |
| Y4  | %113 | Metrik iyileştirme yavaşlıyor |
| Y5  | %116 | Olgun expansion döngüsü |

## 7. LTV / CAC Gelişimi (Yüksek Seviye)
Basit LTV ≈ ARPA * Brüt Marj * (1 / aylık_churn). Örnek Y3:
- ARPA $68, Brüt Marj %78, Churn %3.5 → Ömür ~28.6 ay → LTV ≈ $1,520.
- Varsayılan CAC $420 → LTV/CAC ≈ 3.6x.

Hedef: Y5’te ARPA $86, Brüt Marj %83, Churn %2.5 → Ömür 40 ay → LTV ≈ 86 * 0.83 * 40 ≈ $2,853. CAC $380 varsayımıyla LTV/CAC ≈ 7.5x (üst düzey sermaye verim sinyali).

## 8. Görsel / Grafik Önerileri (Deck İçin)
- Çizgi: Yıl sonu müşteri büyümesi.
- Alan: ARR kümülatif + brüt kâr overlay.
- Waterfall: Y3 MRR köprüsü (Başlangıç MRR → Yeni Logo → Expansion → Churn → Contraction → Yıl Sonu MRR).
- Gauge: NRR gelişimi (Y1-5). 

## 9. Duyarlılık Özet (Gelir Üzerinde En Yüksek Etkili 3 Parametre)
1. Aylık churn ±1 puan → Y5 ARR ~%6–8 sapma.
2. ARPA gelişim eğrisi her yıl -$5 → Y5 ARR ~-%9–10.
3. Expansion payı Y3’te hedefin 5 puan altında → NRR < %107 → Y5 LTV/CAC <6x.

## 10. Basit Aylık Simülasyon Formülü (Pseudo-Python)
```python
customers = [15]
year_params = [
    {'growth':0.18,'churn':0.05,'arpa':44},
    {'growth':0.10,'churn':0.04,'arpa':56},
    {'growth':0.07,'churn':0.035,'arpa':68},
    {'growth':0.06,'churn':0.03,'arpa':78},
    {'growth':0.05,'churn':0.025,'arpa':86},
]
mrrs = []
for y,p in enumerate(year_params, start=1):
    net = 1 + p['growth'] - p['churn']
    months = 12 if y>1 else 11  # ilk yıl başlangıç ayı ay1 sonu kabul edildi
    for m in range(months):
        c_prev = customers[-1]
        c_new = c_prev * net
        customers.append(c_new)
        mrrs.append(c_new * p['arpa'])
```

## 11. Interpretasyon & Yatırımcı Mesajı
- ARR büyümesi erken dönemde yeni logo odaklı → Y2’den itibaren expansion hızlanır; dayanıklı büyüme.
- Y3’te NRR >%108 eşiğinin yakalanması; sermaye verimli ölçek sinyali.
- Brüt marj iyileşmesi kademeli; altyapı optimizasyonu anlatısı desteklenebilir.
- Payback <9 ay (Y3) + LTV/CAC >3.5x = sürdürülebilir GTM genişleme gerekçesi.

## 12. Sonraki Adım
`cost_hiring_plan.md` dokümanında: Personel planı, maaş bantları, OPEX kırılımı, runway analizi ve kullanım (Use of Funds) türetilecektir.

---
Revizyon isteğin varsa (ör: başlangıç müşteri >20 olsun, churn farklı vb.) belirt; yeniden hesaplayabilirim.
