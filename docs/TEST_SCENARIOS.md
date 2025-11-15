# FinAsis Test Kullanıcıları & Senaryoları

Bu doküman `python manage.py setup_test_environment` komutu ile oluşturulan demo verisini nasıl kullanabileceğinizi anlatır. Tüm kullanıcıların parolası varsayılan olarak `FinAsis!2025` şeklindedir.

## Test Kullanıcıları

| Kullanıcı Adı | Rol / Yetkinlik | Bağlı Şirket | Öne Çıkan Yetkiler |
| --- | --- | --- | --- |
| `demo_superadmin` | Süper yönetici | FinAsis Demo Holding | Tüm sistem ayarları, kullanıcı yönetimi, feature flag idaresi |
| `demo_owner` | Şirket sahibi (KOBİ) | FinAsis Demo Holding | Muhasebe ve finans genel yetkileri, AI Asistan konfigürasyonu |
| `demo_finance_manager` | Finans yöneticisi | Anadolu Üretim Sanayi | Nakit akışı, banka entegrasyonları, raporlar |
| `demo_accountant` | Muhasebeci | Anadolu Üretim Sanayi | Fatura, gider, defter, beyannameler |
| `demo_advisor` | Finansal danışman | FinAsis Demo Holding | Analitik rapor okuma, AI önerilerini inceleme |
| `demo_auditor` | Denetçi | FinAsis Demo Holding | Salt okuma, audit trail ve compliance raporları |
| `demo_teacher` | Eğitimci | EduFin Akademi | Eğitim içerikleri, öğrenci yönetimi |
| `demo_student` | Öğrenci | EduFin Akademi | Eğitim portalı, oyunlaştırma içerikleri |
| `demo_employee` | KOBİ çalışanı | Anadolu Üretim Sanayi | Görev yönetimi, temel raporlar |
| `demo_ai_specialist` | AI analisti | FinAsis Demo Holding | AI Asistan, risk analizi, OCR servisleri |

> **Not:** Kullanıcı ve şirketler yeniden oluşturulabilir. Komut var olan kayıtları günceller ve parolayı tekrar `FinAsis!2025` yapar.

## Feature Flag Durumu

Komut aşağıdaki feature flag’leri tüm kullanıcılara açar; admin panelinden (`/management/feature-flags/`) yönetilebilir:

- `help_center`: Yardım merkezi ve rehber içeriklerinin tamamı
- `guided_tours`: Adım adım arayüz turları
- `documentation_portal`: Dokümantasyon giriş noktaları
- `ai_assistant_full_suite`: AI Asistan, risk analizi ve OCR fonksiyonları

## Senaryo Akışları

### 1. Yönetim & Yetki Seti (demo_superadmin)
1. `/management/dashboard/` ekranında şirket özetini inceleyin.
2. `Feature Flag` sayfasından `help_center` anahtarının aktif olduğunu doğrulayın.
3. Kullanıcı yönetimi modülünden `demo_employee` kaydı için rol eşlemesini görüntüleyin.

### 2. Muhasebe & Finans (demo_finance_manager veya demo_accountant)
1. `/accounting/invoices/` sayfasında otomatik oluşturulan demo faturalarını listeleyin.
2. `/accounting/invoices/<id>/` ekranından faturayı görüntüleyin; `PDF`/`Excel` aksiyonlarını test edin.
3. `/finance/cashflow/` dashboard’unda nakit akışı grafiğini ve gelir-gider dağılımını inceleyin.
4. `/finance/banking/` sayfasında örnek banka hesaplarını eklemeyi deneyin (gerekirse sahte IBAN ile).

### 3. Denetim & Uyumluluk (demo_auditor)
1. `/audit/logs/` sayfasında AI Asistan ve fatura işlemlerini içeren log kayıtlarını filtreleyin.
2. `/security/compliance/` raporunda KVKK / ISO 27001 kontrollerini gözden geçirin.

### 4. AI Asistan & Raporlama (demo_ai_specialist veya demo_owner)
1. `/ai-assistant/console/` ekranında “Bu ayki tahmini nakit açığı nedir?” gibi sorular sorun.
2. AI özetleri içerisindeki `Öneriler` sekmesinden aksiyon maddelerini kaydedin.
3. `/ai-assistant/ocr/` bölümünde örnek PDF veya görüntü yükleyerek metin çıkarımını test edin.

### 5. Yardım Merkezi & Dökümantasyon (herhangi bir kullanıcı)
1. Sağ alt köşedeki yardım butonundan “Kılavuzlu Turlar”ı başlatın.
2. `/help/` sayfasında modül bazlı dökümantasyonları inceleyin.
3. Arama kutusuna “fatura” yazarak yardım makalelerini filtreleyin.

### 6. Eğitim & Oyunlaştırma (demo_teacher & demo_student)
1. `demo_teacher` hesabıyla `/education/manage/` ekranında yeni ders planı oluşturun.
2. `demo_student` hesabıyla `/education/courses/` bölümünde ilerlemeyi güncelleyin.
3. `/games/trade-sim/` modülünde piyasa simülasyonunu başlatın.

### 7. Çalışan Portalı (demo_employee)
1. `/core-ui/tasks/` sayfasından görev listesine erişin.
2. `/core-ui/announcements/` modülündeki şirket içi duyuruları kontrol edin.

## Hızlı Komutlar

```bash
# Demo verisini oluştur / güncelle
python manage.py setup_test_environment

# Rol atamalarını yeniden senkronize et
python manage.py auto_assign_roles --assign --force

# Yardım içeriğini yeniden yükle (istenirse)
python manage.py collectstatic --dry-run --noinput
```

Sorular için `destek@finasis.com` adresine ulaşabilirsiniz. İyi testler! 🎯

