# FinAsis – Maliyet ve İşe Alım Planı (Baz Senaryo)

Bu doküman 24 aylık detay + 60 aylık özet perspektifte personel, COGS, OPEX, işe alım tetikleyicileri, burn & runway ve yatırım kullanım (Use of Funds) dağılımını sunar. Tüm rakamlar USD bazlıdır (lokalizasyon için döviz kuru parametreli yapılabilir).

## 1. Stratejik Yaklaşım
Öncelik sırası: (1) Ürün/entegrasyon derinliği → (2) Aktivasyon & retention → (3) Ölçeklenebilir GTM → (4) Regülasyon & denetim hazırlığı. Headcount artışı MRR ve ürün kullanım sinyallerine bağlı tetiklenir; “takvim tabanlı” değil “metrik tabanlı” yaklaşım.

## 2. Headcount Yol Haritası (Quarter Bazlı – FTE)
| Fonksiyon | Mevcut (M0) | Q1 | Q2 | Q3 | Q4 | Y2 Q1 | Y2 Q2 | Y2 Q3 | Y2 Q4 | Y3 (Ortalama) | Y4 | Y5 |
|-----------|------------|----|----|----|----|-------|-------|-------|-------|---------------|----|----|
| Founder (Tech/Product) | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Backend Engineer | 0 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 |
| Full-stack / Frontend | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 2 |
| Data / ML | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 2 |
| Product Manager | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Growth / Demand Gen | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 2 |
| SDR / Inside Sales | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 2 | 2 | 3 | 3 | 3 |
| Customer Success (CSM) | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 2 | 2 | 3 | 3 |
| Support L1 (part-time→FTE) | 0 | 0.3 | 0.5 | 0.5 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Finance / Admin | 0 | 0 | 0 | 0.5 | 0.5 | 0.5 | 0.5 | 1 | 1 | 1 | 1 | 1 |
| Compliance / Security (fractional) | 0 | 0 | 0 | 0.2 | 0.2 | 0.2 | 0.5 | 0.5 | 0.5 | 0.5 | 1 | 1 |
| QA (otomasyon ağırlıklı) | 0 | 0 | 0 | 0 | 0.5 | 0.5 | 0.5 | 1 | 1 | 1 | 1 | 1 |
| TOPLAM (≈) | 1 | 1.3 | 3.5 | 6.2 | 8.2 | 9.2 | 10.5 | 12 | 15 | 19 | 21 | 22 |

Not: Y3+ özet yıllık ortalama FTE verilmiştir; detaylı aylık plan gerekirse ayrı tab sayfasında modellenir.

## 3. Maaş Bantları (Yıllık, USD, Baz)
| Rol | Bant (Min-Ort-Max) | Model Kullanımı (Ort) |
|-----|-------------------|-----------------------|
| Backend Engineer | 48K – 55K – 62K | 55K |
| Full-stack / Frontend | 42K – 48K – 56K | 48K |
| Data / ML | 52K – 58K – 68K | 58K |
| Product Manager | 45K – 50K – 60K | 50K |
| Growth / Demand Gen | 40K – 45K – 55K | 45K |
| SDR | 28K – 32K – 38K | 32K |
| Customer Success | 30K – 34K – 40K | 34K |
| Support L1 | 16K – 20K – 25K | 20K |
| Finance / Admin | 24K – 28K – 34K | 28K |
| Compliance / Security (fractional) | (effective) 40K FTE baz | 40K * fraction |
| QA | 36K – 42K – 50K | 42K |

Yan hak & işveren yükü katsayısı varsayımı: %18 (salary * 1.18 = tam maliyet).

## 4. Personel Maliyet Projeksiyonu (Örnek Y1–Y2)
Basitleştirilmiş çarpan: Ortalama FTE * Ortalama Karma Maaş (48K) * 1.18.
- Y1 Ortalama FTE ≈ 4.8 → Yıllık personel gideri ≈ 4.8 * 48K * 1.18 ≈ $272K
- Y2 Ortalama FTE ≈ 11.7 → ≈ 11.7 * 50K (karma artışı) * 1.18 ≈ $691K

Not: Detaylı fonksiyonel kırılım tam modelde aylık bazda hesaplanabilir.

## 5. COGS Bileşenleri (Y1 → Y5 Yüzde Aralığı)
| Kalem | Y1 | Y5 | Açıklama |
|-------|----|----|----------|
| Hosting (Compute + DB) | %22 | %15 | Verim + rezerve instance |
| Entegrasyon API ücretleri | %18 | %20 | Kullanım hacmiyle artış, unit cost’da azalma |
| Veri Depolama & Yedek | %10 | %9 | Ölçek + sıkıştırma politikaları |
| Observability / Log / Monitoring | %8 | %6 | Konsolidasyon / self-hosting seçenekleri |
| L1 Destek Personeli (COGS payı) | %15 | %14 | Otomasyon arttıkça düşüş sınırlı |
| Üçüncü Parti Güvenlik / Compliance Araçları | %12 | %10 | Yüksek başlangıç – sabitlenme |
| Diğer (CDN, e-posta, vs.) | %15 | %13 | Oran azalır |

COGS toplamı gelir yüzdesi olarak Y1 ≈ %30 hedef (Brüt Marj %70) → Y5 ≈ %17 (Brüt Marj %83).

## 6. OPEX (Personel Hariç) Dağılımı (Yıllık % Gelir / Yatırım Kullanımı Perspektifi)
| Kalem | Y1 (Gelir Düşük Olduğu İçin ARR% anlamsız) | Y2 | Y3 | Not |
|-------|--------------------------------------------|----|----|-----|
| Pazarlama (Paid + İçerik) | $90K | 35% | 28% | CAC optimizasyonu ile oran düşüşü |
| Satış Araçları & CRM | $12K | 6% | 5% | Kullanıcı başı lisans |
| SaaS / Üretkenlik Araçları | $18K | 9% | 7% | Birleşik paketleme |
| Hukuk & Muhasebe & Danışmanlık | $15K | 5% | 4% | Due diligence hazırlığı |
| Ofis / Remote Ops (donanım, coworking) | $20K | 6% | 5% | Remote-first |
| Güvenlik & Uyumluluk (pen test, audit hazırlık) | $25K | 8% | 6% | SOC hazırlığı |
| Diğer (travel, etkinlik, eğitim) | $10K | 5% | 4% | Konferans hedefli |

## 7. Aylık Burn & Runway (Örnek Raise Senaryosu)
Varsayılan Raise: $400K (net kasaya giriş). Başlangıç aylık burn Y1-Q1 ≈ $35K → Q4’te ≈ $55K.
Basit ortalama Y1 aylık burn ≈ $45K → Runway ≈ 400K / 45K ≈ 8.9 ay (gelir öncesi). Ancak artan MRR (Y1 sonu ~2.5K MRR) etkisi düşüktür. Y2 başına devreden nakit ≈ $10–20K varsayımı; Y2’de burn artmadan önce ikinci dilim / bridge veya daha yüksek ilk raise (> $550K) opsiyonu düşünülebilir.

Alternatif: $600K raise → Ortalama burn (Y1+Y2 erken) ≈ $52K → 11–12 ay runway + pivot buffer.

## 8. Use of Funds (400K Örneği)
| Kalem | Pay | Tutar |
|-------|-----|-------|
| Ürün & Mühendislik | %38 | $152K |
| Veri & ML | %10 | $40K |
| GTM (Pazarlama + Satış) | %25 | $100K |
| Güvenlik & Uyumluluk | %8 | $32K |
| Operasyon / G&A | %9 | $36K |
| Rezerv / Koşullu (buffer) | %10 | $40K |

## 9. İşe Alım Tetikleyicileri (Metric-Gated)
| Rol | Tetikleyici (Metric) | Eşik | Gerekçe |
|-----|----------------------|------|---------|
| 2. Backend | MRR ≥ $8K ve entegrasyon backlog > 4 sprint | ~Ay 9–10 | Feature hızını koru |
| Data/ML | Entegrasyon verisi > 50 aktif müşteri & anomaly precision < %85 | Ay 9–12 | Model doğruluk artırımı |
| Growth | Aktivasyon oranı < hedef (%55) & organik lead payı < %25 | Ay 6 | Dönüşüm optimizasyonu |
| SDR | Kurucu satış kapasitesi > haftalık 8 demo | Ay 7–9 | Pipeline ölçekleme |
| CSM | Aktif müşteri > 70 & churn riski sinyali artışı | Y2 Q1 | Retention koruması |
| QA | Release frekansı > haftada 2 & prod bug oranı > %3 | Ay 10–12 | Kalite teminatı |
| Security/Compliance | Pilot enterprise / audit talebi | Event-driven | Güven artırma |

## 10. Verimlilik Göstergeleri
| KPI | Y1 Hedef | Y2 Hedef | Not |
|-----|---------|---------|-----|
| Mühendislik Çıktısı (deploy / hafta) | 6 | 10 | Otomasyon pipeline |
| Lead → Trial Dönüşüm | %40 | %45 | İçerik & nurture |
| Trial Aktivasyon | %55 | %63 | Onboarding iyileştirme |
| Churn (logo, aylık) | %5 | %4 | CSM & kullanım analitiği |
| Expansion Oranı (MRR payı) | %8 | %15 | Add-on monetizasyon |
| NRR | %90 | %103 | Ürün değer derinliği |
| CAC Payback (ay) | 14.5 | 10.5 | Kanallar miks optimizasyonu |

## 11. Risk & Mitigasyon
| Risk | Etki | Mitigasyon |
|------|------|------------|
| Burn beklenenden yüksek | Runway kısalır | Metric-gated işe alım, ops harcama dondurma |
| Entegrasyon geliştirme gecikmesi | Aktivasyon düşer | Entegrasyon öncelik matrisi, SDK/adapter kütüphanesi |
| Churn yüksek kalır | NRR < %100 | Early warning health score, CSM playbook |
| GTM maliyet şişmesi | CAC artar | Kanal ROI dashboard + test budget tavanı |
| Güvenlik olayı | Reputasyon kaybı | Temel CIS kontrolleri + log & SIEM |

## 12. Lokasyon / Kur Hassasiyeti
Eğer TL bazlı maaş çalışılacaksa parametre: USDTRY = 34 varsayımı. Kur oynaklığı için:
- FX Buffer (%): 3–5 puan ek bütçe.
- Yıllık revizyon: Y2’de maaşlara %15–20 enflasyon farkı.

## 13. Model Genişletme Önerileri
- Aylık bazlı ayrıntı: Google Sheet / Notebook entegrasyonu ile otomatik senaryo tuşu.
- Senaryo parametre setleri: (Optimistic / Base / Headwind) → Growth, Churn, ARPA.
- Monte Carlo (opsiyonel): Churn dağılımı (Beta), Growth (Normal veya Lognormal) ile ARR outcome bandı.

## 14. Sonraki Adım
`unit_economics_kpis.md` dosyasında: CAC, LTV, NRR, Payback, ARPA köprüleri, kohort mantığı ve izleme panosu KPI tanımları.

---
Revize etmek istediğin maaş, raise tutarı veya işe alım zamanlaması varsa belirt; güncelleyebilirim.
