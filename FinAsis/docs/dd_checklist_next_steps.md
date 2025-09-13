# FinAsis – Due Diligence (DD) Checklist & Sonraki Adımlar

Bu doküman melek / pre-seed yatırımcıların hızlı inceleme (light DD) ve potansiyel seed öncesi derin inceleme (expanded DD) süreçlerinde talep edebileceği belge & veri setlerini, mevcut durum / boşlukları ve aksiyon planını içerir.

## 1. Data Room Önerilen Klasör Yapısı
```
data_room/
  01_corporate/
    cap_table.xlsx
    founders_agreements.pdf
    incorporation_docs.pdf
    option_pool_plan.pdf
  02_financials/
    historical_expenses.xlsx
    revenue_projection_model.xlsx
    assumptions_summary.pdf
    bank_statements/ (son 6 ay)
  03_product_tech/
    architecture_overview.pdf
    security_model.pdf
    api_endpoints.md
    data_model_diagram.png
    backlog_sample.xlsx
  04_metrics/
    kpi_dashboard_export.csv
    cohort_nrr_example.csv
    activation_funnel.csv
  05_customers/
    pilot_list.xlsx
    customer_pipeline.xlsx
    logo_references_plan.md
  06_legal_compliance/
    privacy_policy.pdf
    terms_of_service.pdf
    data_processing_addendum_template.pdf
    kvkk_statement.pdf
  07_security/
    risk_register.xlsx
    vulnerability_scan_report.pdf
    access_control_matrix.xlsx
  08_hr_people/
    org_chart.pdf
    hiring_plan.pdf
  09_marketing_sales/
    gtm_strategy.pdf
    pricing_pack.pdf
  10_misc/
    press_mentions.pdf
    advisor_bios.pdf
```

## 2. Kurumsal (Corporate) Checklist
| Öğe | Durum | Aksiyon | Öncelik |
|-----|-------|---------|---------|
| Kuruluş belgeleri | Var (TR) | İngilizce özet hazırlama | P1 |
| Cap Table güncel | Kısmi | Excel formatı + opsiyon hedefi | P0 |
| Ortaklar sözleşmesi | Var | Revizyon tarihini ekle | P2 |
| Opsiyon havuzu planı | Yok | %10 taslak plan | P0 |

## 3. Finansal Checklist
| Öğe | Durum | Aksiyon | Öncelik |
|-----|-------|---------|---------|
| Tarihsel giderler (aylık) | Kısmi | Kategorize (COGS vs OPEX) | P0 |
| Banka ekstreleri | Var | Tek PDF paketi | P2 |
| Gelir projeksiyonu | Var (md) | XLSX formatına aktar | P1 |
| Vergi yükümlülükleri | İncelenmedi | Muhasebe danışman notu | P1 |
| Runway analizi | Var | Bridge senaryo ekle | P2 |

## 4. Ürün & Teknoloji
| Öğe | Durum | Aksiyon | Öncelik |
|-----|-------|---------|---------|
| Mimari diyagram | Kısmi | Güncel diyagram (PNG) | P0 |
| Kod lisans uyumu | Belirsiz | Açık kaynak kütüphane taraması | P1 |
| API dokümantasyonu | Kısmi | Postman / OpenAPI spec | P0 |
| Ölçeklenebilirlik notu | Yok | Kapasite planı kısa not | P2 |
| SLA / Uptime hedefleri | Yok | Y1 hedef dokümanı | P2 |

## 5. Güvenlik & Uyum
| Öğe | Durum | Aksiyon | Öncelik |
|-----|-------|---------|---------|
| Risk kaydı | Yok | risk_register.xlsx oluştur | P0 |
| Erişim matrisi | Yok | access_control_matrix.xlsx | P0 |
| Şifreleme politikası | Yok | Kısa policy (at-rest, in-transit) | P1 |
| Log & izleme kapsamı | Kısmi | Enstrümantasyon listesi | P1 |
| Zafiyet taraması | Yok | Açık kaynak SCA + basit scan raporu | P1 |
| KVKK / GDPR temel çerçeve | Kısmi | Veri sınıflandırma tablosu | P1 |

## 6. Müşteri & GTM
| Öğe | Durum | Aksiyon | Öncelik |
|-----|-------|---------|---------|
| Pilot müşteri listesi | Kısmi | Segment / aşama kolonları | P0 |
| Referans programı | Yok | 3 referans şablonu | P2 |
| Fiyatlandırma dokümanı | Var | Versiyon control ekle | P2 |
| Kanal performans raporu | Yok | Lead source tablo | P1 |

## 7. KPI & Analitik
| Öğe | Durum | Aksiyon | Öncelik |
|-----|-------|---------|---------|
| Aktivasyon funnel | Kısmi | CSV export otomasyonu | P1 |
| NRR kohort tablosu | Yok | Script & aylık export | P0 |
| ARPA decomposition | Var | Grafik (waterfall) PDF | P2 |
| Magic Number hesaplaması | Yok | Template formül ekle | P2 |

## 8. İnsan Kaynakları
| Öğe | Durum | Aksiyon | Öncelik |
|-----|-------|---------|---------|
| Organizasyon şeması | Yok | Basit draw.io export | P1 |
| İşe alım planı | Var | Revizyon tarih damgası | P2 |
| ESOP politikasının taslağı | Yok | Opsiyon plan taslak | P0 |
| Çalışan gizlilik sözleşmesi | Kısmi | Standart NDA şablonu | P1 |

## 9. ESG / Etik (Opsiyonel Erken Hazırlık)
| Öğe | Durum | Aksiyon | Öncelik |
|-----|-------|---------|---------|
| Veri etik beyanı | Yok | Kısa açıklama (ML kullanım alanı) | P2 |
| Çeşitlilik metrikleri | Yok | Şeffaflık notu | P3 |

## 10. Yatırımcı Sık Sorular (Hazırlık)
| Tema | Örnek Soru | Kısa Yanıt Şablonu |
|------|-----------|--------------------|
| Pazar | “Neden şimdi?” | Regülasyon + veri parçalanması trendi |
| Rekabet | “X sizden farklı ne yapıyor?” | Dikey vs yatay / otomasyon derinliği |
| Fiyatlandırma | “İndirim politikanız?” | Yıllık -%15, hacim tekil görüşme |
| Ürün | “En zayıf modülünüz?” | Raporlama (şu an) – roadmap ile güçlenecek |
| Güvenlik | “SOC2 durumunuz?” | Hazırlık aşaması, kontrol checklist var |
| Büyüme | “Seed’de ARR hedefiniz?” | ≥$300K run-rate & NRR >%108 |
| Risk | “Tek en büyük riskiniz?” | Entegrasyon hızının aktivasyon etkisi |

## 11. Aksiyon Planı (Önceliklendirilmiş)
| P0 (0–30g) | P1 (30–60g) | P2 (60–90g) |
|------------|------------|-------------|
| Cap table finalize | API spec | ARPA waterfall grafik |
| Opsiyon havuzu taslak | Risk kaydı & erişim matrisi | Referans program şablon |
| NRR kohort script | Banka ekstre paket | SLA dokümanı |
| Pilot liste revizyon | Entegrasyon diyagramı | Magic Number template |
| ESOP taslak | Şifreleme policy | Organize advisor bios |

## 12. T Zaman Çizelgesi (Pitch Öncesi)
| Zaman | Aksiyon |
|-------|---------|
| T-30 | P0 aksiyonlarının %70 tamam, data room çekirdek hazır |
| T-14 | KPI export güncel, risk kaydı ilk versiyon |
| T-7  | Demo senaryosu prova, Q&A dokümanı finalize |
| T-2  | Data room integrite kontrolü |
| T-0  | Pitch + erişim linkleri paylaşımı |

## 13. Risk Açıklama Formatı (Önerilen)
| Başlık | Kategori | Olasılık (L/M/H) | Etki (L/M/H) | Mitigasyon | Durum |
|--------|----------|------------------|-------------|-----------|-------|
| Entegrasyon Gecikmeleri | Ürün | M | H | Önceliklendirme matrisi, adapter kütüphanesi | Açık |
| Churn Düşürülememesi | Büyüme | M | H | Health score + CSM playbook | Açık |
| Güvenlik Olayı | Güvenlik | L | H | Temel kontroller + izleme | Açık |

## 14. Sonraki Adım
Data room dosyalarının fiziksel oluşturulması ve eksik P0 kalemlerinin tamamlanması. Gerektiğinde her tablo için checklist → issue tracker entegrasyonu yapılabilir.

---
Eklemek istediğin farklı bir kategori veya soru listesi varsa belirt; yoksa bu plan seti tamamlandı olarak işaretlenecek.
